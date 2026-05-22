# Claude Code CLI Analysis for Pipeline Orchestration

**Date**: 2026-05-22
**Binary**: `$CLAUDE_CODE_EXECPATH` (SDK-bundled, not on `$PATH` by default)
**Version**: claude-code 2.1.147 (agent SDK entrypoint)

---

## Key Findings

### Agent execution
| Feature | Supported | Mechanism |
|---------|-----------|-----------|
| `.agent.md` file format | Yes | YAML frontmatter + markdown body |
| `--agent <name>` flag | Yes | Selects a named agent by its `name:` field |
| `--agents <json>` flag | Yes | Inline agent definitions: `{"name": {"description":"...","prompt":"..."}}` |
| Agent auto-discovery | Yes | From plugin dirs and `.claude/agents/` |
| Project-level agents | Partial | Agents in `homework-4/agents/` not auto-discovered; need explicit loading |

### Model selection
| Feature | Supported | Mechanism |
|---------|-----------|-----------|
| `--model <model>` | Yes | Accepts short names (`sonnet`, `opus`) or full IDs (`claude-sonnet-4-6`) |
| Frontmatter `model:` | Yes | Used by agent system; pipeline script parses it |

### Non-interactive execution
| Feature | Supported | Mechanism |
|---------|-----------|-----------|
| `-p` / `--print` | Yes | Print response and exit |
| `--output-format` | Yes | `text`, `json`, `stream-json` |
| `--permission-mode` | Yes | `acceptEdits`, `auto`, `bypassPermissions`, `default`, `dontAsk`, `plan` |
| `--dangerously-skip-permissions` | Yes | Bypasses all permission checks |
| `--allow-dangerously-skip-permissions` | Yes | Makes bypass available without defaulting to it |

### System prompt injection
| Feature | Supported | Mechanism |
|---------|-----------|-----------|
| `--system-prompt <text>` | Yes | Replaces default system prompt |
| `--append-system-prompt <text>` | Yes | Adds to default system prompt |
| `--system-prompt-file` | Likely | Referenced in `--bare` docs; not in main help |
| `--append-system-prompt-file` | Likely | Referenced in `--bare` docs |

### Tool control
| Feature | Supported | Mechanism |
|---------|-----------|-----------|
| `--allowedTools` | Yes | Whitelist: `"Bash(git *) Edit"` etc. |
| `--disallowedTools` | Yes | Blacklist |
| `--tools` | Yes | Limit to specific built-in tools |

---

## Pipeline Strategy: Prompt-injection approach

Since project-level agents aren't auto-discovered from `homework-4/agents/`,
the pipeline uses a **prompt-injection** strategy:

1. Parse `model:` from each `.agent.md` frontmatter
2. Read the `.agent.md` body (after frontmatter) as agent instructions
3. Construct a task-specific prompt for each bug
4. Invoke: `claude -p --model <model> --append-system-prompt "<instructions>" "<task prompt>"`

This keeps all agent definitions in the spec-required `.agent.md` files
while using `--append-system-prompt` to inject them into Claude Code's
default system prompt (preserving built-in tools like Read, Edit, Bash).

### Permission mode
`--dangerously-skip-permissions` is used because the pipeline is
non-interactive and runs on local code only. The Bug Fixer agent needs
Edit and Bash (for pytest); permission prompts would block the pipeline.

### Fallback
If `claude` is unavailable, the pipeline can still be **demonstrated** by
running each agent prompt manually in an interactive Claude Code session.
The script detects this and prints instructions.
