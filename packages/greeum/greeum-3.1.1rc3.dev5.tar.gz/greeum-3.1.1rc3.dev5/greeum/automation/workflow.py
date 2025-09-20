"""Entry points for the search → work → add workflow."""

from __future__ import annotations

import json
import os
import subprocess
import sys
from typing import List

import click

GREEUM_BIN = os.environ.get("GREEUM_CLI_BIN", "greeum")


def _run_cli(args: List[str]) -> int:
    proc = subprocess.run([GREEUM_BIN, *args], check=False)
    return proc.returncode


@click.group()
def workflow() -> None:
    """Greeum workflow helper."""


@workflow.command()
@click.argument("query")
@click.option("--limit", default=5, show_default=True, help="Number of results to display")
def search(query: str, limit: int) -> None:
    """Search memories before you start working."""
    code = _run_cli(["search", query, "--limit", str(limit)])
    if code != 0:
        sys.exit(code)


@workflow.command()
@click.argument("importance", type=float)
@click.argument("content", nargs=-1)
def add(importance: float, content: List[str]) -> None:
    """Store a summary after the task is complete."""
    if not content:
        click.echo("Provide memory text after the importance score.", err=True)
        sys.exit(1)
    text = " ".join(content)
    code = _run_cli(["add-memory", text, "--importance", str(importance)])
    if code != 0:
        sys.exit(code)


@workflow.command()
@click.option("--limit", default=5, show_default=True, help="Show recent memories")
def recap(limit: int) -> None:
    """Review latest stored memories."""
    code = _run_cli(["recent-memories", "--limit", str(limit)])
    if code != 0:
        sys.exit(code)


@workflow.command()
def stats() -> None:
    """Display system statistics via MCP."""
    cmd = [GREEUM_BIN, "mcp", "serve", "-t", "stdio"]
    env = os.environ.copy()
    env.setdefault("GREEUM_QUIET", "true")
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True, env=env)
    requests = [
        {
            "jsonrpc": "2.0",
            "id": "1",
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-10",
                "clientInfo": {"name": "workflow-cli", "version": "1.0"},
                "capabilities": {},
            },
        },
        {
            "jsonrpc": "2.0",
            "id": "2",
            "method": "tools/call",
            "params": {"name": "get_memory_stats", "arguments": {}},
        },
    ]

    for req in requests:
        proc.stdin.write(json.dumps(req) + "\n")
        proc.stdin.flush()

    try:
        for _ in requests:
            line = proc.stdout.readline()
            if not line:
                continue
            data = json.loads(line)
            if data.get("id") == "2":
                for item in data.get("result", {}).get("content", []):
                    if item.get("type") == "text":
                        click.echo(item["text"])
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=1)
        except subprocess.TimeoutExpired:
            proc.kill()


if __name__ == "__main__":
    workflow()
