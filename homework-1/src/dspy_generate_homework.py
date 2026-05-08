import json
import os
import re
from pathlib import Path
from typing import Dict, List

import dspy


ROOT = Path(__file__).parent.parent   # homework-1/
TASKS_FILE = ROOT / "TASKS.md"
OUTPUT_DIR = ROOT                      # write directly into homework-1/


def load_env(env_path: Path) -> None:
    if not env_path.exists():
        return
    for line in env_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip())


def sanitize_code_block(text: str) -> str:
    """
    Remove fenced code wrappers if the model returns them.
    """
    text = text.strip()
    fence_match = re.match(r"^```[a-zA-Z0-9_-]*\n([\s\S]*?)\n```$", text)
    if fence_match:
        return fence_match.group(1).strip() + "\n"
    return text + ("\n" if not text.endswith("\n") else "")


def ensure_parent(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def write_file(relative_path: str, content: str) -> None:
    path = OUTPUT_DIR / relative_path
    ensure_parent(path)
    path.write_text(content, encoding="utf-8")


def extract_json(text: str) -> Dict:
    """
    Best-effort extraction of JSON object from model output.
    """
    text = text.strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    match = re.search(r"\{[\s\S]*\}", text)
    if not match:
        raise ValueError("Could not find JSON object in model output.")
    return json.loads(match.group(0))


def build_file_list(plan: Dict) -> List[str]:
    raw_files = plan.get("files", [])
    files = []
    for item in raw_files:
        if isinstance(item, str):
            files.append(item)
        elif isinstance(item, dict) and "path" in item:
            files.append(item["path"])
    return files


def main() -> None:
    load_env(ROOT / ".env")       # homework-1/.env

    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        raise RuntimeError("ANTHROPIC_API_KEY is missing. Put it in .env or environment.")

    if not TASKS_FILE.exists():
        raise FileNotFoundError(f"Missing {TASKS_FILE}")

    assignment_text = TASKS_FILE.read_text(encoding="utf-8")

    lm = dspy.LM(
        "anthropic/claude-sonnet-4-6",
        api_key=api_key,
        temperature=0.2,
        max_tokens=4000,
    )
    dspy.configure(lm=lm)

    planner = dspy.Predict(
        "assignment_text -> project_plan_json"
    )
    file_builder = dspy.Predict(
        "assignment_text, project_plan_json, target_file -> file_contents"
    )
    reviewer = dspy.Predict(
        "assignment_text, project_plan_json, file_path, file_contents -> review_json"
    )
    repairer = dspy.Predict(
        "assignment_text, project_plan_json, file_path, current_contents, review_json -> improved_file_contents"
    )

    planning_prompt = f"""
You are helping complete a software engineering homework assignment.

Return ONLY valid JSON.
Choose Python and FastAPI.
Choose the smallest correct implementation that satisfies the rubric.

The JSON must have this shape:
{{
  "stack": "Python + FastAPI",
  "extra_feature": "summary",
  "rationale": "...",
  "files": [
    "README.md",
    "HOWTORUN.md",
    ".gitignore",
    "requirements.txt",
    "src/main.py",
    "demo/run.sh",
    "demo/sample-requests.http",
    "demo/sample-data.json"
  ],
  "notes": [
    "...",
    "..."
  ]
}}

Rules:
- Use in-memory storage only.
- Include all required endpoints and validations.
- Implement GET /accounts/{{accountId}}/summary as the chosen extra feature.
- Keep the project minimal but complete.
- Do not include tests unless absolutely necessary.
- Do not include a database.
- Make file list realistic for a homework submission.
- Return JSON only.

Assignment:
{assignment_text}
""".strip()

    plan_result = planner(assignment_text=planning_prompt)
    plan = extract_json(plan_result.project_plan_json)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUTPUT_DIR / "PLAN.json").write_text(json.dumps(plan, indent=2), encoding="utf-8")

    files = build_file_list(plan)
    if not files:
        raise RuntimeError("Planner returned no files.")

    for target_file in files:
        build_prompt = f"""
You are generating exactly one file for a homework project.

Return only the content of the requested file.
Do not wrap in markdown unless the file itself is markdown.
Keep the implementation minimal, clear, and runnable.

Project plan JSON:
{json.dumps(plan, indent=2)}

Requested file:
{target_file}

Hard requirements from assignment:
- POST /transactions
- GET /transactions
- GET /transactions/{{id}}
- GET /accounts/{{accountId}}/balance
- Validation:
  - amount must be positive
  - amount max 2 decimal places
  - account format ACC-XXXXX where X is alphanumeric
  - valid ISO currency codes via a small whitelist like USD, EUR, GBP, JPY
- GET /transactions filtering:
  - accountId
  - type
  - from
  - to
- Extra feature:
  - GET /accounts/{{accountId}}/summary
- Basic error handling and appropriate status codes
- In-memory storage only

Additional guidance:
- For src/main.py, make it self-contained if possible.
- For README.md and HOWTORUN.md, be explicit and beginner-friendly.
- For demo/sample-requests.http, include sample requests for all main endpoints.
- For demo/run.sh, use uvicorn.
- For .gitignore, include Python essentials.
- For requirements.txt, keep dependencies minimal.

Assignment:
{assignment_text}
""".strip()

        built = file_builder(
            assignment_text=assignment_text,
            project_plan_json=json.dumps(plan),
            target_file=build_prompt,
        )
        content = sanitize_code_block(built.file_contents)

        review_prompt = f"""
You are a strict homework reviewer.

Return ONLY valid JSON with this shape:
{{
  "pass": true,
  "issues": [],
  "fixes": []
}}

Check only this file:
{target_file}

Review for:
- correctness relative to assignment
- missing requirements
- misleading instructions
- broken imports or run steps
- missing endpoint coverage if this file should contain endpoints
- missing demo documentation if this file is docs/demo related

Be strict but practical.
If the file is acceptable, set pass=true.

Assignment:
{assignment_text}

Project plan JSON:
{json.dumps(plan, indent=2)}

File content:
{content}
""".strip()

        review = reviewer(
            assignment_text=assignment_text,
            project_plan_json=json.dumps(plan),
            file_path=target_file,
            file_contents=review_prompt,
        )
        review_json = extract_json(review.review_json)

        if not review_json.get("pass", False):
            repair_prompt = f"""
Improve this file based on the review JSON.

Return only the corrected file content.
Do not explain anything.

File path:
{target_file}

Review JSON:
{json.dumps(review_json, indent=2)}

Current content:
{content}

Assignment:
{assignment_text}
""".strip()

            repaired = repairer(
                assignment_text=assignment_text,
                project_plan_json=json.dumps(plan),
                file_path=target_file,
                current_contents=content,
                review_json=repair_prompt,
            )
            content = sanitize_code_block(repaired.improved_file_contents)

        write_file(target_file, content)
        print(f"Generated: {target_file}")

    print(f"\nDone. Files are in: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()