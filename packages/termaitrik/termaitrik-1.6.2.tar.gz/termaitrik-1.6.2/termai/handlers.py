"""Common handler classes for consolidating repeated patterns"""

from __future__ import annotations

import json
from typing import Any, Dict, List, Optional, Callable

from rich.console import Console
from rich.status import Status

from .utils import parse_loose_json, format_json_error_response, pretty_json
from .providers import ProviderError, ChatMessage


class BaseCommandHandler:
    """Base class for handling common command patterns"""

    def __init__(self, console: Optional[Console] = None):
        self.console = console or Console()

    def get_ai_response(
        self,
        messages: List[ChatMessage],
        cfg: Dict[str, Any],
        stream: bool = False,
        temperature: float = 0.2,
        status_message: str = "[dim]Asking the AI...[/dim]"
    ) -> str:
        """
        Get AI response with consistent error handling and status display.

        Args:
            messages: List of chat messages
            cfg: Configuration dictionary
            stream: Whether to stream the response
            temperature: Temperature for generation
            status_message: Status message to display

        Returns:
            AI response text
        """
        try:
            from . import providers
            provider = providers.make_provider(cfg)

            if stream:
                from .utils import stream_to_console
                return stream_to_console(
                    provider.chat(messages, cfg["model"], temperature=temperature, stream=True)
                )
            else:
                with Status(status_message, spinner="dots"):
                    return "".join(
                        provider.chat(messages, cfg["model"], temperature=temperature, stream=False)
                    )

        except ProviderError as e:
            self.console.print(f"[red]Provider error:[/red] {e}")
            raise

    def parse_json_response(self, text: str, expected_keys: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Parse JSON response with fallback handling for markdown wrappers.

        Args:
            text: Response text to parse
            expected_keys: Optional list of keys that should be present

        Returns:
            Parsed JSON dictionary or error response
        """
        data = parse_loose_json(text)

        if data is None:
            return format_json_error_response(text, "Could not extract valid JSON from response")

        if expected_keys:
            missing_keys = [key for key in expected_keys if key not in data]
            if missing_keys:
                return {
                    "error": "Missing expected keys in JSON response",
                    "missing_keys": missing_keys,
                    "parsed_data": data,
                    "original_response": text[:500] + "..." if len(text) > 500 else text
                }

        return data

    def handle_json_command(
        self,
        messages: List[ChatMessage],
        cfg: Dict[str, Any],
        expected_keys: Optional[List[str]] = None,
        temperature: float = 0.1
    ) -> Dict[str, Any]:
        """
        Handle a command that expects JSON response.

        Args:
            messages: List of chat messages
            cfg: Configuration dictionary
            expected_keys: Keys that should be present in response
            temperature: Temperature for generation

        Returns:
            Parsed JSON response
        """
        try:
            text = self.get_ai_response(
                messages, cfg, stream=False, temperature=temperature,
                status_message="[dim]Analyzing and generating JSON...[/dim]"
            )

            data = self.parse_json_response(text, expected_keys)

            if "error" in data:
                self.console.print(f"[yellow]Warning:[/yellow] {data['error']}")
                if data.get("parse_error"):
                    self.console.print(f"[dim]Parse error: {data['parse_error']}[/dim]")

            return data

        except ProviderError:
            # Re-raise provider errors
            raise
        except Exception as e:
            return {
                "error": "Unexpected error processing command",
                "exception": str(e),
                "suggestion": "Please check your configuration and try again."
            }

    def print_result(self, result: Dict[str, Any], format_as_json: bool = True) -> None:
        """
        Print command result with appropriate formatting.

        Args:
            result: Result dictionary to print
            format_as_json: Whether to format as JSON
        """
        if "error" in result:
            self.console.print(f"[red]Error:[/red] {result['error']}")
            if result.get("suggestion"):
                self.console.print(f"[dim]💡 {result['suggestion']}[/dim]")
        elif format_as_json:
            self.console.print(pretty_json(result))
        else:
            self.console.print(result)


class ChatHandler(BaseCommandHandler):
    """Handler for chat-based commands"""

    def handle_chat_command(
        self,
        messages: List[ChatMessage],
        cfg: Dict[str, Any],
        stream: bool = True,
        temperature: float = 0.2
    ) -> str:
        """Handle standard chat interaction"""
        return self.get_ai_response(
            messages, cfg, stream=stream, temperature=temperature
        )


class JsonCommandHandler(BaseCommandHandler):
    """Handler for commands requiring JSON responses"""

    def __init__(self, console: Optional[Console] = None):
        super().__init__(console)

    def handle_fix_command(
        self,
        messages: List[ChatMessage],
        cfg: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Handle fix command with JSON response"""
        return self.handle_json_command(
            messages, cfg, expected_keys=["cause"], temperature=0.1
        )

    def handle_explain_command(
        self,
        messages: List[ChatMessage],
        cfg: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Handle explain command with JSON response"""
        return self.handle_json_command(
            messages, cfg, expected_keys=["explanation"], temperature=0.1
        )