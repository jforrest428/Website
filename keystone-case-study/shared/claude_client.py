"""
Thin wrapper around the Anthropic Python SDK.

Features:
- Loads API key from .env automatically
- Disk-based response cache keyed by SHA-256 of (model + system + messages)
- Exponential-backoff retry on rate-limit / transient errors
- Rich-formatted logging for screen-recorded demos
"""

import hashlib
import json
import os
import sys
from pathlib import Path
from typing import Any

import anthropic
from dotenv import load_dotenv
from rich.console import Console
from rich.markup import escape
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

# Load .env from the keystone-case-study root (two levels up from this file)
_ENV_PATH = Path(__file__).parent.parent / ".env"
load_dotenv(_ENV_PATH)

console = Console(stderr=True)

_CACHE_DIR = Path(__file__).parent.parent / ".cache"
_CACHE_DIR.mkdir(exist_ok=True)

_DEFAULT_MODEL = "claude-sonnet-4-6"


def _cache_key(model: str, system: str, messages: list[dict]) -> str:
    payload = json.dumps({"model": model, "system": system, "messages": messages}, sort_keys=True)
    return hashlib.sha256(payload.encode()).hexdigest()


def _load_cache(key: str) -> str | None:
    path = _CACHE_DIR / f"{key}.json"
    if path.exists():
        return json.loads(path.read_text())["content"]
    return None


def _save_cache(key: str, content: str) -> None:
    path = _CACHE_DIR / f"{key}.json"
    path.write_text(json.dumps({"content": content}))


@retry(
    retry=retry_if_exception_type((anthropic.RateLimitError, anthropic.APIStatusError)),
    wait=wait_exponential(multiplier=1, min=2, max=30),
    stop=stop_after_attempt(4),
    reraise=True,
)
def _call_api(
    client: anthropic.Anthropic,
    model: str,
    system: str,
    messages: list[dict],
    max_tokens: int,
    temperature: float,
) -> str:
    response = client.messages.create(
        model=model,
        system=system,
        messages=messages,
        max_tokens=max_tokens,
        temperature=temperature,
    )
    return response.content[0].text


def complete(
    system: str,
    messages: list[dict],
    *,
    model: str = _DEFAULT_MODEL,
    max_tokens: int = 1024,
    temperature: float = 0.3,
    cache: bool = True,
    label: str = "",
) -> str:
    """
    Call Claude and return the response text.

    Args:
        system: System prompt string.
        messages: List of {"role": "user"/"assistant", "content": "..."} dicts.
        model: Model ID (default: claude-sonnet-4-6).
        max_tokens: Max output tokens.
        temperature: Sampling temperature.
        cache: Whether to use disk cache (default True).
        label: Short label shown in the progress log.

    Returns:
        The model's text response.
    """
    key = _cache_key(model, system, messages)

    if cache:
        cached = _load_cache(key)
        if cached is not None:
            console.print(f"  [dim]↩ cache hit[/dim] {escape(label)}")
            return cached

    display = label or (messages[-1]["content"][:60] + "…" if messages else "")
    console.print(f"  [cyan]→ Claude[/cyan] {escape(display)}")

    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        console.print("[red]ERROR: ANTHROPIC_API_KEY not set in .env[/red]")
        sys.exit(1)

    client = anthropic.Anthropic(api_key=api_key)
    content = _call_api(client, model, system, messages, max_tokens, temperature)

    if cache:
        _save_cache(key, content)

    return content


def complete_with_tools(
    system: str,
    messages: list[dict],
    tools: list[dict],
    tool_handler: "ToolHandler",
    *,
    model: str = _DEFAULT_MODEL,
    max_tokens: int = 2048,
    temperature: float = 0.3,
    label: str = "",
) -> tuple[str, list[dict]]:
    """
    Agentic loop: call Claude with tools, execute tool calls, loop until text response.

    Args:
        system: System prompt.
        messages: Conversation so far.
        tools: List of Anthropic tool dicts.
        tool_handler: Object with a handle(tool_name, tool_input) -> Any method.
        label: Progress label.

    Returns:
        (final_text_response, updated_messages_list)
    """
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        console.print("[red]ERROR: ANTHROPIC_API_KEY not set in .env[/red]")
        sys.exit(1)

    client = anthropic.Anthropic(api_key=api_key)
    working_messages = list(messages)

    while True:
        console.print(f"  [cyan]→ Claude[/cyan] {escape(label or 'tool loop')}")
        response = client.messages.create(
            model=model,
            system=system,
            messages=working_messages,
            tools=tools,
            max_tokens=max_tokens,
            temperature=temperature,
        )

        # Collect text and tool-use blocks
        text_parts: list[str] = []
        tool_calls: list[Any] = []
        for block in response.content:
            if block.type == "text":
                text_parts.append(block.text)
            elif block.type == "tool_use":
                tool_calls.append(block)

        # Append assistant message
        working_messages.append({"role": "assistant", "content": response.content})

        if response.stop_reason == "end_turn" or not tool_calls:
            return " ".join(text_parts), working_messages

        # Execute tools and append results
        tool_results = []
        for tc in tool_calls:
            console.print(f"    [yellow]⚙ tool:[/yellow] {tc.name}({json.dumps(tc.input)[:80]})")
            result = tool_handler.handle(tc.name, tc.input)
            tool_results.append({
                "type": "tool_result",
                "tool_use_id": tc.id,
                "content": json.dumps(result),
            })

        working_messages.append({"role": "user", "content": tool_results})


class ToolHandler:
    """Base class — subclass and implement handle()."""

    def handle(self, tool_name: str, tool_input: dict) -> Any:
        raise NotImplementedError(f"No handler for tool: {tool_name}")
