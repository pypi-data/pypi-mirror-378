# TermAI — AI assistant for your terminal (Ollama + BYOK)

> Version: 1.6.2

**TermAI** is a terminal AI assistant (CLI + local server) inspired by Warp AI.
It works *offline* with Ollama and supports **BYOK** (Bring Your Own Key) for cloud providers
(OpenAI or compatible endpoints).

## Features

- `termai chat ["initial message"]` — interactive general chat with conversation history (optional streaming)
- `termai suggest "...description..."` — generates **shell commands** with reasoning and risks
- `termai explain --cmd "command"` — explains what a command does
- `termai fix --cmd "command" --error "stderr"` — suggests a fix
- `termai run "...description..."` — suggests a command and asks for confirmation before **executing** it
- `termai agent "...goal..."` — experimental multi‑step iterative assistant (proposes & confirms each command)
- `termai install-shell [--shell SHELL]` — install shell alias
- `termai uninstall-shell` — uninstall shell alias
- Local FastAPI server: `uvicorn termai.server:app --host 127.0.0.1 --port 8765`

## Requirements

- Python 3.10+
- (Optional) **Ollama** at `http://127.0.0.1:11434`
- (Optional) cloud provider key for BYOK (`OPENAI_API_KEY` etc.)

## Installation & Quick Start

Install from PyPI:

```bash
pip install termaitrik
termai --help
```

Or run without installing:

```bash
uvx --from termaitrik termai --help
```

For development (from source):

```bash
pip install -r requirements.txt
pip install -e .
termai --help
```

The shell integration alias (see below) provides resilient fallbacks that work across all install modes.

## Configuration

Create `~/.termai/config.yaml` (see `examples/config.example.yaml`).

Minimal example (Ollama):
```yaml
default_provider: ollama
model: llama3.1:8b
ollama:
  host: http://127.0.0.1:11434
```

BYOK example (OpenAI):
```yaml
default_provider: openai
model: gpt-4o-mini
openai:
  api_key: sk-...
  base_url: https://api.openai.com/v1
```

> Useful environment variables: `TERMAI_PROVIDER`, `TERMAI_MODEL`,
> `OPENAI_API_KEY`, `OPENAI_BASE_URL`, `OLLAMA_HOST`.

## Shell Integration (alias `ai`)

Install a resilient alias that falls back across install modes:

### Option 1: Using TermAI CLI (Recommended)

```bash
termai install-shell
# then reopen your shell (or: source ~/.bashrc | ~/.zshrc | fish config)
ai suggest "create a tar archive of the current folder"
```

Uninstall:
```bash
termai uninstall-shell
```

### Option 2: Using scripts directly

```bash
bash scripts/install-shell-integration.sh
# then reopen your shell (or: source ~/.bashrc | ~/.zshrc | fish config)
ai suggest "create a tar archive of the current folder"
```

Uninstall:
```bash
bash scripts/uninstall-shell-integration.sh
```

### Shell Integration Details

The alias resolution order:
1. Global/venv command `termai`
2. Importable module: `python -m termai.cli`
3. PyPI package via `uvx termai`
4. Local repository via `uvx --from <repo>` (development)

## Local Server API

Start:
```bash
uvicorn termai.server:app --host 127.0.0.1 --port 8765
```

Endpoints:
- `GET /health` → `{ "ok": true }`
- `POST /v1/chat` → body:
  ```json
  {"messages":[{"role":"user","content":"hi"}],"provider":"ollama","model":"llama3.1:8b"}
  ```
  Response: `{ "content": "..." }`

## Safety & Warnings

- Always inspect and confirm suggested commands before executing.
- Redact secrets before sending errors or stack traces to providers.
- Local models (Ollama) keep data on your machine; cloud providers transmit prompts off‑device.

## Changelog Highlights 1.0.0

- Added robust shell integration with multi-fallback launcher.
- Stabilized command set (`chat`, `suggest`, `explain`, `fix`, `run`, plus info/examples helpers).
- Improved provider error handling & streaming.
- Config merging & environment variable expansion.
- Extended test coverage across core flows.

MIT License.

## Experimental Agent Mode

You can try an early iterative "agent" loop that plans and executes several shell commands with your confirmation between steps:

```bash
termai agent "list the latest 5 created files, then show the first"
```

Workflow per step:
1. Model emits JSON: `{ "thought", "command", "explanation", "done" }`.
2. You confirm/modify/abort; if accepted the command runs locally.
3. Stdout/stderr are summarized and appended to the conversation as an observation.
4. Loop continues until `done=true`, command empty, or max steps reached (default 6).

Options (current minimal POC):
```
--steps N          maximum steps (default 6)
--dry-run          never execute commands (records hypothetical observations)
--model / -m       override configured model
--temperature / -t sampling temperature (default 0.1)
```

Roadmap ideas (not yet implemented): whitelist & yolo auto‑approval modes, danger pattern guard, transcript export, richer tool schema. Feedback welcome.
