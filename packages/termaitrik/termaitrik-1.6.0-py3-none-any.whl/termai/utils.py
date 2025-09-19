from __future__ import annotations

import json
import re
import subprocess
from typing import Any, Dict, Iterable, List, Optional, Union

from rich.console import Console
from rich.markdown import Markdown
from rich.prompt import Confirm, Prompt

console = Console()


def stream_to_console(chunks: Iterable[str]) -> str:
    out = []
    for chunk in chunks:
        console.print(chunk, end="")
        out.append(chunk)
    console.print()
    return "".join(out)


def pretty_json(data) -> str:
    return json.dumps(data, indent=2, ensure_ascii=False)


def confirm_and_run(command: str, dry_run: bool = False) -> int:
    """
    Prompts the user to confirm a command before running it.
    """
    while True:
        console.print(Markdown(f"**Suggested command:**\n\n```bash\n{command}\n```"))
        if dry_run:
            console.print("[yellow]Dry-run: command not executed.[/yellow]")
            return 0

        choice = Prompt.ask(
            "What do you want to do?",
            choices=["e", "m", "a"],
            default="e",
            show_choices=True,
        )

        if choice == "e":
            return subprocess.call(command, shell=True)
        elif choice == "m":
            command = Prompt.ask("Modify the command", default=command)
        elif choice == "a":
            console.print("[yellow]Aborted by user.[/yellow]")
            return 0


def run_command_capture(command: str) -> tuple[str, str, int]:
    """Executes a shell command capturing stdout, stderr and return code.

    Minimal helper used by the experimental agent loop.
    """
    proc = subprocess.run(command, shell=True, capture_output=True, text=True)
    return proc.stdout, proc.stderr, proc.returncode


def extract_json_from_text(text: str) -> Optional[Dict[str, Any]]:
    """
    Extract JSON from text that may contain markdown wrappers or other content.

    Args:
        text: Text that may contain JSON

    Returns:
        Parsed JSON dictionary if found, None otherwise
    """
    # Try to find JSON in code blocks first
    json_block_pattern = r'```(?:json)?\s*(\{[\s\S]*?\})\s*```'
    matches = re.findall(json_block_pattern, text, re.IGNORECASE)

    for match in matches:
        try:
            return json.loads(match.strip())
        except json.JSONDecodeError:
            continue

    # Try to find JSON object using brace matching
    json_start = text.find('{')
    if json_start != -1:
        brace_count = 0
        for i in range(json_start, len(text)):
            char = text[i]
            if char == '{':
                brace_count += 1
            elif char == '}':
                brace_count -= 1
                if brace_count == 0:
                    json_str = text[json_start:i+1]
                    try:
                        return json.loads(json_str)
                    except json.JSONDecodeError:
                        break

    # Try to parse the entire text as JSON
    try:
        return json.loads(text.strip())
    except json.JSONDecodeError:
        pass

    return None


def clean_json_response(text: str) -> str:
    """
    Clean text that should be JSON by removing common wrappers and formatting.

    Args:
        text: Raw text response

    Returns:
        Cleaned JSON string
    """
    # Remove markdown code block wrappers
    text = re.sub(r'^```json\s*', '', text, flags=re.MULTILINE)
    text = re.sub(r'\s*```$', '', text, flags=re.MULTILINE)

    # Remove common prefixes/suffixes
    text = text.strip()

    # Remove explanatory text before/after JSON
    json_start = text.find('{')
    json_end = text.rfind('}') + 1

    if json_start != -1 and json_end != -1:
        text = text[json_start:json_end]

    return text


def parse_loose_json(text: str) -> Optional[Dict[str, Any]]:
    """
    Parse JSON that may be wrapped in markdown or have formatting issues.

    Args:
        text: Text containing JSON

    Returns:
        Parsed JSON dictionary or None if parsing fails
    """
    # Clean the text first
    cleaned = clean_json_response(text)

    # Try to parse
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        pass

    # Try extracting JSON from larger text
    return extract_json_from_text(text)


def safe_json_loads(text: str, default: Any = None) -> Any:
    """
    Safely load JSON with fallback to default value.

    Args:
        text: JSON string to parse
        default: Default value if parsing fails

    Returns:
        Parsed JSON object or default
    """
    try:
        return json.loads(text)
    except (json.JSONDecodeError, TypeError):
        return default


def format_json_error_response(original_text: str, parse_error: str) -> Dict[str, Any]:
    """
    Format a response when JSON parsing fails.

    Args:
        original_text: Original text that failed to parse
        parse_error: Error message from parsing attempt

    Returns:
        Formatted error response dictionary
    """
    return {
        "error": "Failed to parse JSON response",
        "parse_error": parse_error,
        "original_response": original_text[:500] + "..." if len(original_text) > 500 else original_text,
        "suggestion": "The AI response was not in valid JSON format. This might indicate a problem with the model or prompt."
    }
