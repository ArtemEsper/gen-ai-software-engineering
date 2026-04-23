# MemPalace Memory Index

Maps every saved memory blob to its short_id.
Updated automatically by `02-mine-homework.sh`, `03-mine-course.sh`, and `04-backfill.sh`.

To recover a blob:
```bash
# Local blob (L- prefix)
cat course-memory/vault/<hash>.json

# MemPalace cloud blob
npx mempalace recover <short_id>
```

To search:
```bash
bash course-memory/scripts/05-search.sh "<query>"
```

---

| short_id | scope | title | saved_at |
|---|---|---|---|
| `L-68d9c73a` | `hw1_repo` | hw1_repo: src/main.py | 2026-04-23T20:41:30Z |
| `L-cdef989f` | `hw1_repo` | hw1_repo: src/dspy_generate_homework.py | 2026-04-23T20:41:32Z |
| `L-3db0afa8` | `hw1_repo` | hw1_repo: requirements.txt | 2026-04-23T20:41:34Z |
| `L-0ce8ff37` | `hw1_repo` | hw1_repo: README.md | 2026-04-23T20:41:35Z |
| `L-1a4eefdc` | `hw1_repo` | hw1_repo: HOWTORUN.md | 2026-04-23T20:41:37Z |
| `L-c636b04d` | `hw1_repo` | hw1_repo: TASKS.md | 2026-04-23T20:41:38Z |
| `L-3dab017d` | `hw1_repo` | hw1_repo: demo/sample-requests.sh | 2026-04-23T20:41:40Z |
| `L-5773d910` | `hw1_repo` | hw1_repo: demo/sample-requests.http | 2026-04-23T20:41:41Z |
| `L-3129691f` | `hw1_repo` | hw1_repo: demo/sample-data.json | 2026-04-23T20:41:43Z |
| `L-3b265660` | `hw1_repo` | hw1_repo: demo/run.sh | 2026-04-23T20:41:44Z |
| `L-f8314607` | `hw1_convos` | hw1_convos: session-chunk-01-of-03 (7bced355...jsonl) | 2026-04-23T20:41:49Z |
| `L-e8052ce6` | `hw1_convos` | hw1_convos: session-chunk-02-of-03 (7bced355...jsonl) | 2026-04-23T20:41:50Z |
| `L-622394b2` | `hw1_convos` | hw1_convos: session-chunk-03-of-03 (7bced355...jsonl) | 2026-04-23T20:41:52Z |
