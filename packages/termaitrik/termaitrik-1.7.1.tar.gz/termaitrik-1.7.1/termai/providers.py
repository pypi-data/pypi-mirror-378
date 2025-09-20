from __future__ import annotations

import json
import os
import shutil
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Iterator
from urllib.request import urlretrieve

import requests

# Global provider cache to avoid repeated initialization
_provider_cache: Dict[str, BaseProvider] = {}
_cache_keys: Dict[str, str] = {}

try:
    from llama_cpp import Llama
    LLAMA_CPP_AVAILABLE = True
except ImportError:
    LLAMA_CPP_AVAILABLE = False


@dataclass
class ChatMessage:
    role: str
    content: str


class ProviderError(RuntimeError):
    pass


class BaseProvider:
    name: str

    def chat(self, messages: List[ChatMessage], model: str, temperature: float = 0.2, stream: bool = False) -> Iterator[str]:
        raise NotImplementedError


class OllamaProvider(BaseProvider):
    name = "ollama"

    def __init__(self, host: str = "http://127.0.0.1:11434"):
        # Normalize host so callers may pass:
        #  - http://host:port
        #  - http://host:port/v1
        #  - http://host:port/api
        # We want self.base to be the authority + optional port, without trailing
        # path segments, so we consistently append /api/chat below.
        base = host.rstrip("/")
        if base.endswith("/v1"):
            base = base[: -len("/v1")]
        if base.endswith("/api"):
            base = base[: -len("/api")]
        self.base = base.rstrip("/")

    def chat(self, messages: List[ChatMessage], model: str, temperature: float = 0.2, stream: bool = False) -> Iterator[str]:
        url = f"{self.base}/api/chat"
        payload = {
            "model": model,
            "messages": [m.__dict__ for m in messages],
            "options": {"temperature": temperature},
            "stream": stream,
        }
        if not stream:
            resp = requests.post(url, json=payload, timeout=60)
            if resp.status_code != 200:
                raise ProviderError(f"Ollama error {resp.status_code}: {resp.text}")
            data = resp.json()
            yield data.get("message", {}).get("content", "")
        else:
            # For streaming requests, do not pass 0 as timeout (urllib3 rejects <= 0).
            # None means no timeout (block until response/stream closes).
            with requests.post(url, json=payload, stream=True, timeout=None) as r:
                if r.status_code != 200:
                    raise ProviderError(f"Ollama error {r.status_code}: {r.text}")
                for line in r.iter_lines():
                    if not line:
                        continue
                    try:
                        part = json.loads(line.decode("utf-8"))
                        delta = part.get("message", {}).get("content", "")
                        if delta:
                            yield delta
                    except Exception:
                        continue


class OpenAIProvider(BaseProvider):
    name = "openai"

    def __init__(self, api_key: str, base_url: str = "https://api.openai.com/v1"):
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")

    def chat(self, messages: List[ChatMessage], model: str, temperature: float = 0.2, stream: bool = False) -> Iterator[str]:
        if not self.api_key:
            raise ProviderError("OPENAI_API_KEY is missing")
        url = f"{self.base_url}/chat/completions"
        payload = {
            "model": model,
            "messages": [m.__dict__ for m in messages],
            "temperature": temperature,
            "stream": stream,
        }
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        if not stream:
            resp = requests.post(url, headers=headers, json=payload, timeout=60)
            if resp.status_code != 200:
                raise ProviderError(f"OpenAI error {resp.status_code}: {resp.text}")
            data = resp.json()
            choices = data.get("choices", [])
            if not choices:
                return
            yield choices[0].get("message", {}).get("content", "")
        else:
            # For streaming requests, do not pass 0 as timeout (urllib3 rejects <= 0).
            # None means no timeout (block until response/stream closes).
            with requests.post(url, headers=headers, json=payload, stream=True, timeout=None) as r:
                if r.status_code != 200:
                    raise ProviderError(f"OpenAI error {r.status_code}: {r.text}")
                for line in r.iter_lines():
                    if not line:
                        continue
                    if line.startswith(b"data: "):
                        line = line[6:]
                    if line.strip() == b"[DONE]":
                        break
                    try:
                        part = json.loads(line.decode("utf-8"))
                        delta = part.get("choices", [{}])[0].get("delta", {}).get("content", "")
                        if delta:
                            yield delta
                    except Exception:
                        continue


class LlamaCppProvider(BaseProvider):
    name = "llamacpp"

    # Primary recommended model for offline use
    DEFAULT_MODELS = {
        "qwen2.5-1.5b": {
            "url": "https://huggingface.co/bartowski/Qwen2.5-1.5B-Instruct-GGUF/resolve/main/Qwen2.5-1.5B-Instruct-Q4_K_M.gguf",
            "size_mb": 1100,
            "description": "Qwen2.5 1.5B - Modern high-quality model with excellent instruction following",
            "recommended_for": ["all purposes", "coding", "chat", "multilingual", "best quality"]
        }
    }

    # Model-specific chat templates and system prompts
    MODEL_TEMPLATES = {
        "qwen2.5-1.5b": {
            "template": "<|im_start|>system\n{system}<|im_end|>\n<|im_start|>user\n{user}<|im_end|>\n<|im_start|>assistant\n{assistant}",
            "system_prompt": "You are Qwen2.5, a helpful AI assistant created by Alibaba Cloud. You provide accurate, helpful, and harmless responses. Follow instructions carefully and be concise when appropriate.",
            "stop_tokens": ["<|im_end|>", "<|im_start|>"]
        },
        # Fallback template for any other models
        "default": {
            "template": "<|im_start|>system\n{system}<|im_end|>\n<|im_start|>user\n{user}<|im_end|>\n<|im_start|>assistant\n{assistant}",
            "system_prompt": "You are a helpful AI assistant. Provide accurate, helpful, and harmless responses.",
            "stop_tokens": ["<|im_end|>", "<|im_start|>"]
        }
    }

    def __init__(self, model_dir: Optional[str] = None, model_name: str = "qwen2.5-1.5b",
                 n_ctx: int = 2048, n_gpu_layers: int = 1, verbose: bool = False, quiet: bool = False):
        if not LLAMA_CPP_AVAILABLE:
            raise ProviderError(
                "📦 llama-cpp-python is not installed.\n"
                "💡 Please install it with: pip install llama-cpp-python\n"
                "🔧 Or run: pip install -e . (in this directory)"
            )

        self.model_name = model_name
        self.n_ctx = n_ctx
        self.n_gpu_layers = n_gpu_layers
        self.verbose = verbose
        self.quiet = quiet

        # Validate model name
        if model_name not in self.DEFAULT_MODELS:
            available_models = ", ".join(self.DEFAULT_MODELS.keys())
            raise ProviderError(
                f"❌ Unknown model: '{model_name}'\n"
                f"📋 Available models: {available_models}\n"
                f"💡 Use 'termai info' to see model information"
            )

        self.model_dir = Path(model_dir) if model_dir else Path.home() / ".termai" / "models"
        self.model_dir.mkdir(parents=True, exist_ok=True)
        self.model_path = None
        self.llm = None

        # Load model-specific template configuration
        if model_name in self.MODEL_TEMPLATES:
            self.template_config = self.MODEL_TEMPLATES[model_name]
        else:
            # Use the modern default template for any unknown models
            self.template_config = self.MODEL_TEMPLATES["default"]

        if not quiet:
            print(f"🚀 Initializing {self.model_name}...")
        self._load_model(quiet)

    def _load_model(self, quiet: bool = False):
        """Load or download the model"""
        if self.model_name in self.DEFAULT_MODELS:
            model_info = self.DEFAULT_MODELS[self.model_name]
            model_url = model_info["url"]
            model_filename = model_url.split("/")[-1]
            self.model_path = self.model_dir / model_filename

            if not self.model_path.exists():
                size_mb = model_info["size_mb"]
                description = model_info["description"]
                if not quiet:
                    print(f"📥 Downloading {self.model_name} ({size_mb}MB)")
                    print(f"📝 {description}")
                self._download_model(model_url, self.model_path, size_mb, quiet)
        else:
            # Assume it's a local file path
            self.model_path = Path(self.model_name)
            if not self.model_path.exists():
                raise ProviderError(f"Model file not found: {self.model_path}")

        # Show model info
        if not quiet:
            self._show_model_info()

        try:
            # Suppress Metal initialization messages by redirecting stderr temporarily
            import sys
            import io
            original_stderr = sys.stderr
            sys.stderr = io.StringIO()

            try:
                self.llm = Llama(
                    model_path=str(self.model_path),
                    n_ctx=self.n_ctx,
                    n_batch=512,
                    verbose=self.verbose,
                    n_gpu_layers=self.n_gpu_layers
                )
            finally:
                # Restore stderr
                sys.stderr = original_stderr

        except Exception as e:
            raise ProviderError(f"Failed to load model {self.model_path}: {e}")

    def _download_model(self, url: str, destination: Path, size_mb: int, quiet: bool = False):
        """Download model with progress indication"""
        try:
            # Create a temporary file for download
            with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
                def show_progress(block_num, block_size, total_size):
                    if total_size > 0 and not quiet:
                        percent = min(100, (block_num * block_size * 100) // total_size)
                        if block_num % 50 == 0:  # Update more frequently
                            downloaded_mb = (block_num * block_size) // (1024 * 1024)
                            print(f"\r📊 Progress: {percent}% ({downloaded_mb}/{size_mb}MB)", end="", flush=True)

                if not quiet:
                    print(f"🚀 Starting download... (this may take a few minutes)")
                urlretrieve(url, tmp_file.name, reporthook=show_progress)
                if not quiet:
                    print(f"\n✅ Download complete!")  # New line after progress

                # Move to final location
                shutil.move(tmp_file.name, destination)
                if not quiet:
                    print(f"💾 Model saved to: {destination}")
        except Exception as e:
            # Clean up temporary file if it exists
            if 'tmp_file' in locals():
                try:
                    os.unlink(tmp_file.name)
                except:
                    pass
            raise ProviderError(f"Failed to download model: {e}")

    def _show_model_info(self):
        """Show information about the loaded model"""
        if self.model_name in self.DEFAULT_MODELS:
            info = self.DEFAULT_MODELS[self.model_name]
            print(f"🤖 Model: {self.model_name}")
            print(f"📊 Size: {info['size_mb']}MB")
            print(f"📝 {info['description']}")
            print(f"🎯 Recommended for: {', '.join(info['recommended_for'])}")
        else:
            print(f"🤖 Model: {self.model_name} (custom)")

    @classmethod
    def get_available_models(cls):
        """Get list of available models with descriptions"""
        models = []
        for name, info in cls.DEFAULT_MODELS.items():
            models.append({
                "name": name,
                "size_mb": info["size_mb"],
                "description": info["description"],
                "recommended_for": info["recommended_for"]
            })
        return models

    @classmethod
    def get_recommended_model(cls, use_case: str = "general"):
        """Get recommended model based on use case"""
        recommendations = {
            "beginners": "qwen2.5-1.5b",
            "general": "qwen2.5-1.5b",
            "coding": "qwen2.5-1.5b",
            "technical": "qwen2.5-1.5b",
            "quick": "qwen2.5-1.5b",
            "minimal": "qwen2.5-1.5b",
            "quality": "qwen2.5-1.5b",
            "balanced": "qwen2.5-1.5b",
            "multilingual": "qwen2.5-1.5b"
        }
        return recommendations.get(use_case, "qwen2.5-1.5b")

    @classmethod
    def show_model_help(cls):
        """Show help about available models"""
        print("🤖 Available AI Models for Offline Use:")
        print("=" * 50)

        for name, info in cls.DEFAULT_MODELS.items():
            print(f"\n📋 {name.upper()}")
            print(f"   📊 Size: {info['size_mb']}MB")
            print(f"   📝 {info['description']}")
            print(f"   🎯 Best for: {', '.join(info['recommended_for'])}")

        print(f"\n💡 Primary Model: Qwen2.5-1.5B")
        print(f"   🎯 This single model handles all tasks excellently:")
        print(f"   • High-quality responses for coding & technical tasks")
        print(f"   • Great conversational abilities")
        print(f"   • Multilingual support")
        print(f"   • Modern prompt format for reliable results")

        print(f"\n🔧 First time use will automatically download the model (1.1GB).")
        print(f"💾 Models are cached in ~/.termai/models/")
        print(f"⚡ No need to choose - this model does everything well!")

    def _format_messages_for_model(self, messages: List[ChatMessage]) -> str:
        """Format messages according to the model's specific template"""
        template = self.template_config["template"]
        system_prompt = self.template_config["system_prompt"]

        # Extract system message from messages or use default
        system_msg = system_prompt
        user_messages = []
        assistant_messages = []

        for msg in messages:
            if msg.role == "system":
                system_msg = msg.content
            elif msg.role == "user":
                user_messages.append(msg.content)
            elif msg.role == "assistant":
                assistant_messages.append(msg.content)

        # Handle special case for Phi-2 instruction format
        if self.template_config.get("uses_instruction_format"):
            # Phi-2 format: simple instruction-response
            if user_messages:
                return template.format(instruction=user_messages[-1])
            else:
                return template.format(instruction="Hello")

        # For TinyLlama and similar models, use the proper format
        if "tinyllama" in self.model_name:
            if len(user_messages) == 1:
                # Single message
                return f"[INST] <<SYS>>\n{system_msg}\n<</SYS>>\n{user_messages[0]} [/INST]"
            else:
                # Multi-turn conversation - build conversation history
                conversation = f"[INST] <<SYS>>\n{system_msg}\n<</SYS>>\n{user_messages[0]} [/INST] {assistant_messages[0] if assistant_messages else ''}"
                for i in range(1, len(user_messages)):
                    conversation += f"\n[INST] {user_messages[i]} [/INST] {assistant_messages[i] if i < len(assistant_messages) else ''}"
                return conversation

        # For Qwen 1.5 and 2.5 models
        elif "qwen" in self.model_name and ("1.5" in self.model_name or "2.5" in self.model_name):
            # Build conversation using proper Qwen format
            conversation = f"<|im_start|>system\n{system_msg}<|im_end|>\n"

            for i in range(len(user_messages)):
                conversation += f"<|im_start|>user\n{user_messages[i]}<|im_end|>\n"
                if i < len(assistant_messages):
                    conversation += f"<|im_start|>assistant\n{assistant_messages[i]}<|im_end|>\n"

            # Add final assistant prompt for response generation
            conversation += "<|im_start|>assistant\n"
            return conversation

        # For Gemma models
        elif "gemma" in self.model_name:
            conversation = ""

            # Handle system message (if present and not default)
            first_user_prefix = ""
            if system_msg != self.template_config["system_prompt"]:
                first_user_prefix = system_msg + "\n"

            # Build conversation with proper role mapping
            all_messages = []

            # Add system message as first user message if custom
            if system_msg != self.template_config["system_prompt"]:
                all_messages.append(("user", first_user_prefix.strip()))

            # Add conversation history
            for i in range(len(user_messages)):
                all_messages.append(("user", user_messages[i]))
                if i < len(assistant_messages):
                    all_messages.append(("model", assistant_messages[i]))

            # Format according to Gemma template
            for i, (role, content) in enumerate(all_messages):
                # For the first user message, include system prefix if present
                if i == 0 and role == "user" and first_user_prefix:
                    actual_content = first_user_prefix.strip()
                else:
                    actual_content = content

                conversation += f"<start_of_turn>{role}\n{actual_content}<end_of_turn>\n"

            # Add generation prompt
            conversation += "<start_of_turn>model\n"
            return conversation

        else:
            # Fallback to simple template
            user_msg = user_messages[0] if user_messages else "Hello"
            return template.format(system=system_msg, user=user_msg, assistant="")

    def chat(self, messages: List[ChatMessage], model: str, temperature: float = 0.2, stream: bool = False) -> Iterator[str]:
        if not self.llm:
            raise ProviderError("Model not loaded")

        # Format messages according to model-specific template
        prompt = self._format_messages_for_model(messages)

        try:
            # Adjust max tokens and stop tokens based on model
            max_tokens = 256 if self.model_name == "phi2" else 1024  # Increased for better context

            response = self.llm(
                prompt,
                max_tokens=max_tokens,
                temperature=temperature,
                stop=self.template_config["stop_tokens"],
                echo=False
            )

            content = response["choices"][0]["text"].strip()

            # Clean up common artifacts
            content = content.strip()

            # Remove template artifacts that might appear at the beginning or end
            if content.startswith("<</SYS>>"):
                content = content[7:].strip()
            if content.startswith("<<SYS>>"):
                content = content[7:].strip()

            # Remove instruction tags that might be included
            content = content.replace("[INST]", "").replace("[/INST]", "")
            content = content.replace("<<SYS>>", "").replace("<</SYS>>", "")

            # Remove user/assistant artifacts
            lines = content.split('\n')
            cleaned_lines = []
            for line in lines:
                line = line.strip()
                if line and not line.startswith('User:') and not line.startswith('Assistant:') and line not in ["[INST]", "[/INST]"]:
                    cleaned_lines.append(line)

            content = ' '.join(cleaned_lines).strip()

            # Remove extra whitespace
            content = ' '.join(content.split()).strip()

            # Special handling for Gemma - ensure clean model responses
            if "gemma" in self.model_name:
                # Remove any turn markers that might remain
                content = content.replace("<start_of_turn>", "").replace("<end_of_turn>", "")
                content = ' '.join(content.split()).strip()

            yield content

        except Exception as e:
            raise ProviderError(f"Llama.cpp inference error: {e}")


VALID_PROVIDERS = {"ollama", "openai", "llamacpp"}


def _generate_cache_key(cfg: Dict) -> str:
    """Generate a cache key for the provider configuration."""
    import hashlib
    key_data = {
        'provider': cfg.get('default_provider', 'ollama'),
        'model': cfg.get('model', ''),
        'ollama_host': cfg.get('ollama', {}).get('host', ''),
        'openai_key': bool(cfg.get('openai', {}).get('api_key')),
        'openai_url': cfg.get('openai', {}).get('base_url', ''),
        'llamacpp_model': cfg.get('llamacpp', {}).get('model_name', ''),
        'llamacpp_dir': cfg.get('llamacpp', {}).get('model_dir', ''),
        'llamacpp_ctx': cfg.get('llamacpp', {}).get('n_ctx', 4096),
        'llamacpp_gpu': cfg.get('llamacpp', {}).get('n_gpu_layers', 1),
    }
    key_str = json.dumps(key_data, sort_keys=True)
    return hashlib.md5(key_str.encode()).hexdigest()


def make_provider(cfg: Dict, use_cache: bool = True, quiet: bool = False) -> BaseProvider:
    """
    Resolves which provider to use.

    Priority:
      1. TERMAI_PROVIDER environment variable
      2. cfg['default_provider']
      3. fallback -> 'ollama'
    """
    env_provider = os.getenv("TERMAI_PROVIDER")
    provider = (env_provider or cfg.get("default_provider") or "ollama").lower()

    if provider not in VALID_PROVIDERS:
        raise ProviderError(f"Unsupported provider: {provider}")

    # Check cache first
    if use_cache:
        cache_key = _generate_cache_key(cfg)
        if cache_key in _provider_cache:
            return _provider_cache[cache_key]

    # Create new provider instance
    if provider == "ollama":
        provider_instance = OllamaProvider(host=cfg.get("ollama", {}).get("host", "http://127.0.0.1:11434"))

    # llamacpp
    elif provider == "llamacpp":
        llamacpp_cfg = cfg.get("llamacpp", {}) or {}
        model_dir = llamacpp_cfg.get("model_dir")
        model_name = cfg.get("model") or llamacpp_cfg.get("model_name", "qwen2.5-1.5b")
        n_ctx = llamacpp_cfg.get("n_ctx", 4096)
        n_gpu_layers = llamacpp_cfg.get("n_gpu_layers", 1)
        verbose = llamacpp_cfg.get("verbose", False)

        # Pass quiet parameter to suppress initialization messages
        provider_instance = LlamaCppProvider(
            model_dir=model_dir,
            model_name=model_name,
            n_ctx=n_ctx,
            n_gpu_layers=n_gpu_layers,
            verbose=verbose,
            quiet=quiet
        )

    # openai
    else:
        ocfg = cfg.get("openai", {}) or {}
        api_key = ocfg.get("api_key") or os.getenv("OPENAI_API_KEY") or ""
        base_url = ocfg.get("base_url", "https://api.openai.com/v1")
        if not api_key:
            # fail early for clarity
            raise ProviderError("OpenAI provider selected but API key is missing (config.openai.api_key or OPENAI_API_KEY).")
        provider_instance = OpenAIProvider(api_key=api_key, base_url=base_url)

    # Cache the provider instance
    if use_cache:
        cache_key = _generate_cache_key(cfg)
        _provider_cache[cache_key] = provider_instance

    return provider_instance


def clear_provider_cache():
    """Clear the provider cache to force reinitialization."""
    global _provider_cache
    _provider_cache.clear()
