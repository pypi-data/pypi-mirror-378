from __future__ import annotations

"""CLI entry-point for TermAI.

Supports three invocation modes:
1. Installed package / console script (normal) -> relative imports work.
2. Module execution: python -m termai.cli (works unchanged).
3. Script execution: uv run termai/cli.py (no package context). We add a
   fallback that rewrites imports so the file can still run, enabling
   quick ad-hoc execution (and therefore uvx/uv run based workflows before
   installation/publishing).
"""

import json
from typing import Optional, List
import os
import re
import subprocess
import sys
import typer
from rich import print
from rich.status import Status
from rich.prompt import Confirm, Prompt
from rich.console import Console

# When executed directly (python termai/cli.py) __package__ is None/"" and
# relative imports fail. Add the directory to sys.path and fall back to
# absolute intra-package imports so `uv run termai/cli.py ...` works.
if not __package__:
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))  # project/termai
    try:  # absolute (script) style
        from __init__ import __version__  # type: ignore
        from config import load_config  # type: ignore
        import providers  # type: ignore
        from providers import ProviderError  # type: ignore
        from prompts import (
            SYSTEM_SHELL_EXPERT,
            GENERIC_CHAT_PROMPT,
            PROMPT_SUGGEST,
            PROMPT_EXPLAIN,
            PROMPT_FIX,
            AGENT_SYSTEM_PROMPT,
            AGENT_STEP_USER_PROMPT,
        )  # type: ignore
        from utils import (
            stream_to_console,
            pretty_json,
            confirm_and_run,
            run_command_capture,
            parse_loose_json,
            format_json_error_response,
        )  # type: ignore
        try:
            from handlers import JsonCommandHandler
        except ImportError:
            pass  # Fallback for direct execution
    except Exception as _import_err:  # pragma: no cover - only on direct script run
        raise
else:  # normal package-relative imports
    from . import __version__
    from .config import load_config
    from . import providers
    from .providers import ProviderError
    from .prompts import (
        SYSTEM_SHELL_EXPERT,
        GENERIC_CHAT_PROMPT,
        PROMPT_SUGGEST,
        PROMPT_EXPLAIN,
        PROMPT_FIX,
        AGENT_SYSTEM_PROMPT,
        AGENT_STEP_USER_PROMPT,
    )
    from .utils import stream_to_console, pretty_json, confirm_and_run, run_command_capture, parse_loose_json, format_json_error_response
from .handlers import JsonCommandHandler

# ASCII Art for TermAI
ASCII_ART = """[cyan]
████████╗███████╗██████╗ ███╗   ███╗ █████╗ ██╗
╚══██╔══╝██╔════╝██╔══██╗████╗ ████║██╔══██╗██║
   ██║   █████╗  ██████╔╝██╔████╔██║███████║██║
   ██║   ██╔══╝  ██╔══██╗██║╚██╔╝██║██╔══██║██║
   ██║   ███████╗██║  ██║██║ ╚═╝ ██║██║  ██║██║
   ╚═╝   ╚══════╝╚═╝  ╚═╝╚═╝     ╚═╝╚═╝  ╚═╝╚═╝
[/cyan]
         [bold]AI Assistant for your Terminal[/bold]
"""

def get_help_text():
    from rich.text import Text
    # We need to return a plain text for Typer's help
    # but we'll create a custom callback to show formatted help
    return "TermAI — AI assistant for your terminal (Ollama + BYOK)."

# Custom help function
def custom_help_callback(ctx: typer.Context):
    # Only show formatted help when we're at the root level and help is requested
    # We check if we're not in a subcommand context
    if ctx.invoked_subcommand is None:
        # Check if help was explicitly requested
        if "--help" in sys.argv or "-h" in sys.argv:
            show_formatted_help()
            raise typer.Exit()
    # For subcommands, let Typer handle the help normally
    return False

app = typer.Typer(help=get_help_text(), no_args_is_help=False)

from rich.console import Console

def show_formatted_help():
    console = Console()
    console.print(ASCII_ART)
    console.print("\n[bold]TermAI[/bold] — AI assistant for your terminal (Ollama + llama.cpp + BYOK).\n")
    console.print("[bold]Features:[/bold]")
    console.print("• [green]chat[/green] - General chat with AI")
    console.print("• [green]suggest[/green] - Generate shell commands")
    console.print("• [green]explain[/green] - Explain shell commands")
    console.print("• [green]fix[/green] - Fix failed commands")
    console.print("• [green]run[/green] - Execute commands with confirmation")
    console.print("• [green]agent[/green] - Multi-step iterative assistant")
    console.print("• [green]install-shell[/green] - Install shell integration (ai alias)")
    console.print("• [green]uninstall-shell[/green] - Uninstall shell integration")
    console.print("• [green]info[/green] - Show configuration")
    console.print("• [green]models[/green] - Show available offline AI models")
    console.print("• [green]examples[/green] - Show usage examples")
    console.print("\n[dim]💡 [bold]First time?[/bold] Try 'termai models' to see offline AI options[/dim]")
    console.print("\n[dim]Use [bold]termai [COMMAND] --help[/bold] for more information about a command.[/dim]")

@app.callback(invoke_without_command=True)
def default(ctx: typer.Context,
            help: Optional[bool] = typer.Option(
                None, "--help", "-h",
                help="Show this message and exit.",
                is_eager=True
            ),
            version: Optional[bool] = typer.Option(
                None, "--version", "-v",
                help="Show version and exit.",
                is_eager=True,
            )):
    # Check if help was explicitly requested and we're at the root level
    if help is True and ctx.invoked_subcommand is None:
        show_formatted_help()
        raise typer.Exit()
    # Version requested eagerly
    if version is True and ctx.invoked_subcommand is None:
        print(f"termai {__version__}")
        raise typer.Exit()
    # If no subcommand and no arguments, show formatted help
    elif ctx.invoked_subcommand is None and not any(arg.startswith('-') for arg in sys.argv[1:]):
        show_formatted_help()


@app.command()
def chat(
    prompt: Optional[str] = typer.Argument(
        None, help="Initial message for the chat (optional)."
    ),
    model: Optional[str] = typer.Option(
        None, "--model", "-m", help="Model to use (override)."
    ),
    stream: bool = typer.Option(
        True, "--stream/--no-stream", help="Stream output if supported."
    ),
    temperature: float = typer.Option(
        0.1, "--temperature", "-t", help="Model creativity."
    ),
):
    """
    Starts an interactive chat session with the AI.
    Maintains conversation history during the session.
    """
    import sys
    
    cfg = load_config()
    if model:
        cfg["model"] = model
        
    # Initialize conversation history with system prompt
    messages = [
        providers.ChatMessage(role="system", content=GENERIC_CHAT_PROMPT),
    ]
    
    # Create console for rich output
    console = Console()
    
    # Create provider once for the entire session (quiet initialization)
    try:
        provider = providers.make_provider(cfg, quiet=True)
    except ProviderError as e:
        console.print(f"[red]Provider error:[/red] {e}")
        raise typer.Exit(code=1)

    # If an initial prompt was provided, use it to start the conversation
    if prompt:
        messages.append(providers.ChatMessage(role="user", content=prompt))
        _process_messages_with_provider(messages, cfg, model, stream, temperature, console, provider)

    # Start interactive chat loop
    console.print("[bold cyan]Starting interactive chat session...[/bold cyan]")
    console.print("[dim]Type 'exit' or 'quit' to end the session.[/dim]\n")

    while True:
        try:
            user_input = Prompt.ask("[bold green]You[/bold green]")
            if user_input.lower() in ['exit', 'quit']:
                console.print("[bold cyan]Ending chat session. Goodbye![/bold cyan]")
                break

            # Add user message to history
            messages.append(providers.ChatMessage(role="user", content=user_input))

            # Process the conversation and get AI response (using cached provider)
            response = _process_messages_with_provider(messages, cfg, model, stream, temperature, console, provider)

            # Add AI response to history
            messages.append(providers.ChatMessage(role="assistant", content=response))
            
        except KeyboardInterrupt:
            console.print("\n[bold cyan]Ending chat session. Goodbye![/bold cyan]")
            break
        except Exception as e:
            console.print(f"[red]Error:[/red] {e}")
            break


def _process_messages(messages, cfg, model, stream, temperature, console, quiet=False):
    """Process messages and return the AI response."""
    try:
        provider = providers.make_provider(cfg, quiet=quiet)
        return _process_messages_with_provider(messages, cfg, model, stream, temperature, console, provider)
    except ProviderError as e:
        console.print(f"[red]Provider error:[/red] {e}")
        raise typer.Exit(code=1)


def _process_messages_with_provider(messages, cfg, model, stream, temperature, console, provider):
    """Process messages using an existing provider instance."""
    try:
        if not stream:
            with Status("[dim]Asking the AI...[/dim]", spinner="dots"):
                text = "".join(
                    provider.chat(
                        messages, cfg["model"], temperature=temperature, stream=stream
                    )
                )
            console.print(text)
            return text
        else:
            text = stream_to_console(
                provider.chat(
                    messages, cfg["model"], temperature=temperature, stream=stream
                )
            )
            return text
    except ProviderError as e:
        console.print(f"[red]Provider error:[/red] {e}")
        raise typer.Exit(code=1)


@app.command()
def suggest(
    goal: str = typer.Argument(..., help="Goal in natural language."),
    context: Optional[str] = typer.Option(
        None, "--context", "-c", help="Context: path, available tools, etc."
    ),
    model: Optional[str] = typer.Option(
        None, "--model", "-m", help="Model to use (override)."
    ),
):
    """
    Suggests a command to achieve a given goal.
    """
    cfg = load_config()
    if model:
        cfg["model"] = model
    try:
        provider = providers.make_provider(cfg, quiet=True)
    except ProviderError as e:
        print(f"[red]Provider error:[/red] {e}")
        raise typer.Exit(code=1)
    user_prompt = PROMPT_SUGGEST.format(goal=goal, context=context or "N/A")
    messages = [
        providers.ChatMessage(role="system", content=SYSTEM_SHELL_EXPERT),
        providers.ChatMessage(role="user", content=user_prompt),
    ]
    try:
        with Status("[dim]Asking the AI...[/dim]", spinner="dots"):
            text = "".join(
                provider.chat(messages, cfg["model"], temperature=0.1, stream=False)
            )
        try:
            data = json.loads(text)
            # Verifica se i dati contengono le chiavi attese
            if "commands" in data:
                print(pretty_json(data))
            else:
                # Se non contiene le chiavi attese, stampa il testo originale
                print(text)
        except json.JSONDecodeError:
            print(text)
    except ProviderError as e:
        print(f"[red]Provider error:[/red] {e}")
        raise typer.Exit(code=1)


@app.command()
def explain(
    cmd: str = typer.Option(..., "--cmd", "-c", help="Command to explain."),
    model: Optional[str] = typer.Option(
        None, "--model", "-m", help="Model to use (override)."
    ),
):
    """
    Explains a shell command.
    """
    cfg = load_config()
    if model:
        cfg["model"] = model

    try:
        handler = JsonCommandHandler()
        user_prompt = PROMPT_EXPLAIN.format(cmd=cmd)
        messages = [
            providers.ChatMessage(role="system", content=SYSTEM_SHELL_EXPERT),
            providers.ChatMessage(role="user", content=user_prompt),
        ]

        result = handler.handle_explain_command(messages, cfg)
        handler.print_result(result, format_as_json=False)

    except ProviderError as e:
        print(f"[red]Provider error:[/red] {e}")
        raise typer.Exit(code=1)


@app.command()
def fix(
    cmd: str = typer.Option(..., "--cmd", "-c", help="Command that failed."),
    error: str = typer.Option(..., "--error", "-e", help="Error message from stderr."),
    model: Optional[str] = typer.Option(
        None, "--model", "-m", help="Model to use (override)."
    ),
):
    """
    Fixes a failed shell command.
    """
    cfg = load_config()
    if model:
        cfg["model"] = model

    try:
        handler = JsonCommandHandler()
        user_prompt = PROMPT_FIX.format(cmd=cmd, err=error)
        messages = [
            providers.ChatMessage(role="system", content=SYSTEM_SHELL_EXPERT),
            providers.ChatMessage(role="user", content=user_prompt),
        ]

        result = handler.handle_fix_command(messages, cfg)
        handler.print_result(result)

    except ProviderError as e:
        print(f"[red]Provider error:[/red] {e}")
        raise typer.Exit(code=1)


@app.command()
def run(
    goal: str = typer.Argument(..., help="Goal in natural language."),
    context: Optional[str] = typer.Option(
        None, "--context", "-c", help="Optional context."
    ),
    dry_run: bool = typer.Option(
        False, "--dry-run", help="Print the command without executing it."
    ),
    model: Optional[str] = typer.Option(
        None, "--model", "-m", help="Model to use (override)."
    ),
):
    """
    Generates and executes a command to achieve a given goal.
    """
    cfg = load_config()
    if model:
        cfg["model"] = model
    try:
        provider = providers.make_provider(cfg, quiet=True)
    except ProviderError as e:
        print(f"[red]Provider error:[/red] {e}")
        raise typer.Exit(code=1)
    user_prompt = (
        "Translate the following goal into a single executable shell command.\n"
        "The command must be valid and safe.\n"
        "Respond ONLY with the command, wrapped in <CMD></CMD> tags.\n"
        'Example: <CMD>echo "hello" > world.txt</CMD>\n\n'
        f"Goal: {goal}\n"
        f"Context: {context or 'None'}\n"
        "Response:"
    )
    messages = [
        providers.ChatMessage(
            role="system",
            content="You are a shell expert that translates goals into commands.",
        ),
        providers.ChatMessage(role="user", content=user_prompt),
    ]
    try:
        with Status("[dim]Asking the AI...[/dim]", spinner="dots"):
            response_text = "".join(
                provider.chat(messages, cfg["model"], temperature=0.0, stream=False)
            )

        command = ""
        match = re.search(r"<CMD>(.*)</CMD>", response_text, re.DOTALL)
        if match:
            command = match.group(1).strip()

        if not command:
            print(
                f"[red]Error: the AI did not return a valid command.[/red]\n[dim]Received response:[/dim]\n{response_text}"
            )
            raise typer.Exit(code=1)

        rc = confirm_and_run(command, dry_run=dry_run)
        raise typer.Exit(code=rc)
    except ProviderError as e:
        print(f"[red]Provider error:[/red] {e}")
        raise typer.Exit(code=1)


@app.command()
def info():
    """Shows the configured provider and the default model."""
    cfg = load_config()
    model = cfg.get("model") or "N/A"
    env_provider = os.getenv("TERMAI_PROVIDER")
    # Resolve provider and indicate the source of the choice
    source = "fallback"
    cfg_default = cfg.get("default_provider")
    if cfg_default:
        source = "config"
    elif env_provider:
        source = "env"

    try:
        prov = providers.make_provider(cfg, quiet=True)
        provider_name = getattr(prov, "name", None) or (
            cfg_default or env_provider or "ollama"
        )
    except ProviderError as e:
        print(f"[red]Provider error:[/red] {e}")
        provider_name = cfg_default or env_provider or "ollama"

    print(f"[bold]Provider:[/bold] {provider_name}  [dim]({source})[/dim]")

    # show the resolved configuration file path
    from pathlib import Path
    from .config import DEFAULT_CONFIG_PATH

    local_cfg = Path.cwd() / "config.yaml"
    resolved_path = local_cfg if local_cfg.exists() else DEFAULT_CONFIG_PATH
    print(
        f"[bold]Config file:[/bold] {resolved_path} {'(exists)' if resolved_path.exists() else '(not found)'}"
    )
    print(f"[bold]Model:[/bold] {model}")

    # Show additional model info for llamacpp
    if provider_name == "llamacpp":
        try:
            from .providers import LlamaCppProvider
            if model in LlamaCppProvider.DEFAULT_MODELS:
                model_info = LlamaCppProvider.DEFAULT_MODELS[model]
                print(f"[bold]Model Size:[/bold] {model_info['size_mb']}MB")
                print(f"[bold]Description:[/bold] {model_info['description']}")
                print(f"[bold]Best for:[/bold] {', '.join(model_info['recommended_for'])}")
                print(f"\n[dim]💡 Use 'termai models' to see all available models[/dim]")
        except ImportError:
            pass


@app.command()
def examples():
    """Shows usage examples."""
    from rich.panel import Panel

    examples = [
        {
            "title": "Generic chat (interactive session)",
            "code": 'termai chat "Hello, how are you today?"',
        },
        {
            "title": "Command suggestion",
            "code": 'termai suggest "find all `.py` files modified in the last week"',
        },
        {
            "title": "Command explanation",
            "code": "termai explain --cmd \"awk -F':' '{print $1}' /etc/passwd\"",
        },
        {
            "title": "Fix command with error",
            "code": 'termai fix --cmd "git push" --error "fatal: repository \'https\' not found"',
        },
        {
            "title": "Direct execution",
            "code": 'termai suggest "list all files in the current directory, including hidden ones, and sort them by size"',
        },
        {
            "title": "Run command (dry-run)",
            "code": 'termai run --dry-run "create a file named \'test.txt\' with the content \'hello world\'"',
        },
        {
            "title": "Agent multi-step (experimental)",
            "code": "termai agent \"create a new directory called 'test_agent', and create a file inside it called 'test.txt' with the content 'hello from agent'\"",
        },
    ]
    for example in examples:
        print(Panel(example["code"], title=example["title"], border_style="green"))


@app.command()
def models():
    """Shows available offline AI models and recommendations."""
    try:
        from .providers import LlamaCppProvider
        LlamaCppProvider.show_model_help()
    except ImportError:
        # Handle direct script execution
        import providers
        providers.LlamaCppProvider.show_model_help()



# ---------------- Experimental minimal agent command ---------------- #

@app.command()
def agent(
    goal: str = typer.Argument(..., help="High-level multi-step goal."),
    steps: int = typer.Option(6, "--steps", "-s", help="Maximum reasoning steps."),
    model: Optional[str] = typer.Option(None, "--model", "-m", help="Model override."),
    temperature: float = typer.Option(0.1, "--temperature", "-t", help="Model temperature."),
    dry_run: bool = typer.Option(False, "--dry-run", help="Do not execute proposed commands."),
):
    """Iterative loop (plan -> propose command -> confirm -> observe -> repeat). Minimal POC."""
    cfg = load_config()
    if model:
        cfg["model"] = model
    try:
        provider = providers.make_provider(cfg, quiet=True)
    except ProviderError as e:
        print(f"[red]Provider error:[/red] {e}")
        raise typer.Exit(code=1)

    history: List[providers.ChatMessage] = [
        providers.ChatMessage(role="system", content=AGENT_SYSTEM_PROMPT),
        providers.ChatMessage(role="user", content=f"Obiettivo: {goal}"),
    ]

    def last_events() -> str:
        msgs = [m for m in history if m.role != "system"][-8:]
        lines: List[str] = []
        for m in msgs:
            tag = "U" if m.role == "user" else "A"
            c = m.content
            if len(c) > 250:
                c = c[:250] + "..."
            lines.append(f"[{tag}] {c}")
        return "\n".join(lines) or "(vuoto)"

    for step in range(1, steps + 1):
        user_prompt = AGENT_STEP_USER_PROMPT.format(goal=goal, history_snippet=last_events())
        history.append(providers.ChatMessage(role="user", content=user_prompt))
        with Status(f"[dim]Agent step {step}...[/dim]", spinner="dots"):
            raw = "".join(
                provider.chat(history, cfg["model"], temperature=temperature, stream=False)
            )
        history.append(providers.ChatMessage(role="assistant", content=raw))
        # Some naive providers may concatenate multiple JSON objects; take the first one that parses.
        data = None
        try:
            data = json.loads(raw)
        except json.JSONDecodeError:
            # Try to split by '}{' boundaries
            fragments = []
            buf = ""
            depth = 0
            for ch in raw:
                buf += ch
                if ch == '{':
                    depth += 1
                elif ch == '}':
                    depth -= 1
                    if depth == 0:
                        fragments.append(buf)
                        buf = ""
            for frag in fragments:
                try:
                    data = json.loads(frag)
                    break
                except Exception:
                    continue
            if data is None:
                print(f"[red]Invalid JSON at step {step}.[/red]\n{raw}")
                break

        thought = data.get("thought", "")
        command = (data.get("command") or "").strip()
        explanation = data.get("explanation", "")
        done = bool(data.get("done", False))

        print(f"[bold cyan]Step {step}[/bold cyan]")
        if thought:
            print(f"[dim]Thought:[/dim] {thought}")
        if command:
            print(f"[green]Command:[/green] {command}")
        if explanation:
            print(f"[dim]Explanation:[/dim] {explanation}")
        if done and not command:
            print("[yellow]Agent finished (done=true).[/yellow]")
            break

        if command:
            rc = confirm_and_run(command, dry_run=dry_run)
            if dry_run:
                observation = f"Dry-run: would have executed: {command}"
            else:
                out, err, rcode = run_command_capture(command)
                text = out + ("\nSTDERR:\n" + err if err else "")
                if len(text) > 800:
                    text = text[:800] + "... (truncated)"
                observation = f"RC={{rcode}}\n{text.strip()}" if text.strip() else f"Return code: {rcode}"
            history.append(
                providers.ChatMessage(role="user", content=f"Observation after command:\n{observation}")
            )

        if done:
            break
    print("[bold]Session ended.[/bold]")


# --- helper: locate scripts only under termai/scripts (with optional env override) --- #
def _find_script_or_exit(script_file: str, action: str = "Install") -> str:
    override_dir = os.getenv("TERMAI_SCRIPTS_DIR")
    if override_dir:
        cand = os.path.join(override_dir, script_file)
        if os.path.exists(cand):
            return cand
    current_file = os.path.abspath(__file__)
    pkg_dir = os.path.dirname(current_file)  # .../termai
    cand = os.path.join(pkg_dir, "scripts", script_file)
    if os.path.exists(cand):
        return cand
    print(f"[red]Error:[/red] {action} script not found at {cand}")
    raise typer.Exit(code=1)


@app.command("install-shell")
def install_shell(
    shell: Optional[str] = typer.Option(
        None, "--shell", "-s", help="Target shell (bash, zsh, fish). Auto-detected if not specified."
    ),
):
    """Install shell integration (ai alias) for TermAI."""
    # Resolve script path from multiple candidates (package, data-files, repo, env override)
    install_script = _find_script_or_exit("install-shell-integration.sh", action="Install")

    try:
        # Build command
        cmd = ["bash", install_script]
        if shell:
            cmd.extend(["--shell", shell])

        # Execute the installation script
        with Status("[dim]Installing shell integration...[/dim]", spinner="dots"):
            result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode == 0:
            print("[green]✓[/green] Shell integration installed successfully!")
            if result.stdout.strip():
                print(result.stdout.strip())
        else:
            print(f"[red]Error installing shell integration:[/red]")
            if result.stderr.strip():
                print(result.stderr.strip())
            if result.stdout.strip():
                print(result.stdout.strip())
            raise typer.Exit(code=result.returncode)
    except Exception as e:
        print(f"[red]Error:[/red] {e}")
        raise typer.Exit(code=1)


@app.command("uninstall-shell")
def uninstall_shell():
    """Uninstall shell integration (ai alias) for TermAI."""
    # Resolve script path from multiple candidates (package, data-files, repo, env override)
    uninstall_script = _find_script_or_exit("uninstall-shell-integration.sh", action="Uninstall")

    try:
        # Execute the uninstallation script
        with Status("[dim]Uninstalling shell integration...[/dim]", spinner="dots"):
            result = subprocess.run(["bash", uninstall_script], capture_output=True, text=True)

        if result.returncode == 0:
            print("[green]✓[/green] Shell integration uninstalled successfully!")
            if result.stdout.strip():
                print(result.stdout.strip())
        else:
            print(f"[red]Error uninstalling shell integration:[/red]")
            if result.stderr.strip():
                print(result.stderr.strip())
            if result.stdout.strip():
                print(result.stdout.strip())
            raise typer.Exit(code=result.returncode)
    except Exception as e:
        print(f"[red]Error:[/red] {e}")
        raise typer.Exit(code=1)


if __name__ == "__main__":
    app()
