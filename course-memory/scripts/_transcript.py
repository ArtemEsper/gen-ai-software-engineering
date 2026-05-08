#!/usr/bin/env python3
"""
_transcript.py — Extract conversation turns from Claude Code JSONL transcripts.

Outputs a JSON array of memory-ready blobs suitable for `npx mempalace save`.

Usage:
  python3 _transcript.py <jsonl_path> <scope> [max_chars_per_chunk]

Arguments:
  jsonl_path          Path to a .jsonl Claude Code transcript file
  scope               Memory scope tag, e.g. hw1_convos
  max_chars_per_chunk Max characters per blob (default: 5000)
"""

import json
import sys
from pathlib import Path
from datetime import datetime, timezone

DEFAULT_MAX_CHARS = 5000


def get_text(content) -> str:
    if isinstance(content, str):
        return content.strip()
    if isinstance(content, list):
        parts = [b.get("text", "").strip() for b in content
                 if isinstance(b, dict) and b.get("type") == "text"]
        return "\n".join(p for p in parts if p)
    return ""


def load_messages(path: Path) -> list:
    messages = []
    with open(path, encoding="utf-8") as fh:
        for raw in fh:
            raw = raw.strip()
            if not raw:
                continue
            try:
                entry = json.loads(raw)
            except json.JSONDecodeError:
                continue
            if entry.get("type") in ("queue-operation", "tool_result"):
                continue
            if entry.get("type") in ("user", "assistant"):
                text = get_text(entry.get("message", {}).get("content", ""))
                if len(text) < 10:
                    continue
                messages.append({
                    "role": entry["type"],
                    "text": text,
                    "ts": entry.get("timestamp", ""),
                })
    return messages


def chunk_messages(messages: list, max_chars: int) -> list:
    chunks, current, current_len = [], [], 0
    for msg in messages:
        length = len(msg["text"])
        if current and current_len + length > max_chars:
            chunks.append(current)
            current, current_len = [msg], length
        else:
            current.append(msg)
            current_len += length
    if current:
        chunks.append(current)
    return chunks


def format_blob(chunk: list, idx: int, total: int, scope: str, source: str) -> dict:
    lines = []
    for msg in chunk:
        label = "USER" if msg["role"] == "user" else "ASSISTANT"
        text = msg["text"][:1800] + ("\n...[truncated]" if len(msg["text"]) > 1800 else "")
        lines.append(f"[{label}]\n{text}")
    return {
        "title": f"{scope}: session-chunk-{idx+1:02d}-of-{total:02d} ({source})",
        "content": "\n\n---\n\n".join(lines),
        "tags": [scope, "transcript", "backfill"],
        "metadata": {
            "scope": scope,
            "source": source,
            "chunk_index": idx,
            "chunk_total": total,
            "session_start_ts": chunk[0]["ts"] if chunk else "",
            "mined_at": datetime.now(timezone.utc).isoformat(),
        },
    }


def main():
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(1)
    path = Path(sys.argv[1])
    scope = sys.argv[2]
    max_chars = int(sys.argv[3]) if len(sys.argv) > 3 else DEFAULT_MAX_CHARS
    if not path.exists():
        print(f"ERROR: not found: {path}", file=sys.stderr)
        sys.exit(1)
    messages = load_messages(path)
    if not messages:
        print("[]")
        return
    chunks = chunk_messages(messages, max_chars)
    blobs = [format_blob(c, i, len(chunks), scope, path.name) for i, c in enumerate(chunks)]
    print(json.dumps(blobs, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
