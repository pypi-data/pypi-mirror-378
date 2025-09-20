"""Generate a Greeum daily digest (stdout or webhook)."""

from __future__ import annotations

import json
import os
import subprocess
import sys
from typing import List

import click
import requests

GREEUM_BIN = os.environ.get("GREEUM_CLI_BIN", "greeum")


def _run_cli(args: List[str], capture: bool = False) -> str:
    result = subprocess.run(
        [GREEUM_BIN, *args],
        check=False,
        text=True,
        capture_output=capture,
    )
    if capture:
        return result.stdout
    return ""


def _format_recent(limit: int) -> str:
    output = _run_cli(["recent-memories", "--limit", str(limit), "--json"], capture=True)
    if not output:
        return "(No recent memories)"
    try:
        data = json.loads(output)
    except json.JSONDecodeError:
        return output
    lines = []
    for idx, block in enumerate(data, start=1):
        timestamp = block.get("timestamp", "unknown")
        slot = block.get("slot") or "?"
        context = (block.get("context") or "").replace("\n", " ")
        lines.append(f"{idx}. [{timestamp}] (Slot {slot}) {context}")
    return "\n".join(lines)


def _fetch_stats() -> str:
    cmd = [GREEUM_BIN, "mcp", "serve", "-t", "stdio"]
    env = os.environ.copy()
    env.setdefault("GREEUM_QUIET", "true")
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True, env=env)
    requests_list = [
        {
            "jsonrpc": "2.0",
            "id": "1",
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-10",
                "clientInfo": {"name": "digest-cli", "version": "1.0"},
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

    for req in requests_list:
        proc.stdin.write(json.dumps(req) + "\n")
        proc.stdin.flush()

    stats_text = ""
    try:
        for _ in requests_list:
            line = proc.stdout.readline()
            if not line:
                continue
            data = json.loads(line)
            if data.get("id") == "2":
                for item in data.get("result", {}).get("content", []):
                    if item.get("type") == "text":
                        stats_text = item["text"]
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=1)
        except subprocess.TimeoutExpired:
            proc.kill()
    return stats_text


@click.command()
@click.option("--limit", default=10, show_default=True, help="Number of recent memories to include")
@click.option("--title", default="Greeum Daily Digest", show_default=True)
@click.option("--webhook", envvar="GREEUM_SLACK_WEBHOOK", help="Slack/Discord webhook URL")
def digest(limit: int, title: str, webhook: str | None) -> None:
    """Generate a daily digest; send to webhook if provided."""
    stats = _fetch_stats()
    recent = _format_recent(limit)

    body = f"{title}\n----------------------------\n{stats}\n\nRecent entries (latest {limit}):\n{recent}\n"

    if webhook:
        try:
            response = requests.post(webhook, json={"text": body}, timeout=10)
            if response.status_code >= 400:
                click.echo(f"Webhook error: {response.status_code} {response.text}", err=True)
        except requests.RequestException as exc:
            click.echo(f"Webhook request failed: {exc}", err=True)
            sys.exit(1)
    else:
        click.echo(body)


if __name__ == "__main__":
    digest()
