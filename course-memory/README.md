# Course Memory Layer

Encrypted, persistent memory for the **GenAI and Agentic AI for Software Engineering** course.
Powered by [MemPalace](https://github.com/MemPalace/mempalace) (`npx mempalace`).

---

## What is stored here

| Layer | What | Where |
|---|---|---|
| **MemPalace vault** | Encrypted memory blobs (code, conversations, decisions) | `course-memory/vault/` (local, git-ignored) |
| **Local index** | short-id → label mapping for every saved blob | `notes/index.md` (in git) |
| **Human notes** | Pitfalls, decisions, prompt logs — freeform markdown | `notes/*.md` (in git) |
| **PR drafts** | Pull request descriptions generated from memory | `pr.md` (in git) |

Nothing in this folder is a runtime dependency of any homework app.

---

## Memory scopes / naming convention

| Tag | Contents |
|---|---|
| `course` | Course-wide notes, setup decisions, toolchain choices |
| `hw1_repo` | Source files from `homework-1/` (main.py, tests, config) |
| `hw1_convos` | Conversation turns extracted from Claude Code transcripts |
| `hw2_repo` | Source files from `homework-2/` (future) |
| `hw2_convos` | Conversation turns from `homework-2/` sessions (future) |

Local blob IDs are prefixed `L-` (e.g. `L-68d9c73a`).
MemPalace cloud IDs use raw hex (requires `npx mempalace auth gk_xxxx`).

---

## Quick reference — script order

```
01-init.sh              ← run once per machine
02-mine-homework.sh 1   ← run after each milestone
03-mine-course.sh       ← run after course-level changes
04-backfill.sh 1        ← run once to import prior Claude Code sessions
05-search.sh <query>    ← search saved memories by keyword
06-wakeup.sh 1          ← generate context before a new session
07-record-note.sh       ← record a distilled note (pitfall/decision/prompt)
```

All scripts must be run from the **repo root**:
```bash
bash course-memory/scripts/01-init.sh
```

---

## Storage strategy

`_vault.sh` tries `npx mempalace save` first. If it returns 403 (cloud API key
required), it falls back to `course-memory/vault/<sha256[:8]>.json` automatically.
No user action needed — everything works locally without a MemPalace account.

To enable cloud storage: `npx mempalace auth gk_xxxx` (get key from mempalace.ai).

---

## Known caveats

| Issue | Detail |
|---|---|
| No native search | MemPalace 1.1.0 has no `search` command. `05-search.sh` greps vault JSON and notes/ markdown. |
| Local vault not synced | `vault/` is git-ignored. Re-run mine/backfill scripts on a new machine. |
| Gemini key optional | Without a Gemini key, AI-enhanced recall is disabled. All scripts still work. |
| Auto hooks skipped | Manual scripts prevent accidental mining of unrelated directories. |

---

## Directory structure

```
course-memory/
├── README.md
├── .gitignore             ← excludes vault/
├── pr.md                  ← latest generated PR description
├── scripts/
│   ├── 01-init.sh
│   ├── 02-mine-homework.sh
│   ├── 03-mine-course.sh
│   ├── 04-backfill.sh
│   ├── 05-search.sh
│   ├── 06-wakeup.sh
│   ├── 07-record-note.sh
│   ├── _vault.sh          ← shared save/recover helper
│   └── _transcript.py     ← JSONL conversation parser
├── notes/
│   ├── index.md           ← blob short-id index
│   ├── pitfalls.md
│   ├── decisions.md
│   └── prompt-log.md
└── vault/                 ← git-ignored local blob storage
    └── <sha256[:8]>.json
```
