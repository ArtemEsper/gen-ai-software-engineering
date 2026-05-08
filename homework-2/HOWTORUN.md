
# How to Run

> Refined with GPT-4.1

## Prerequisites

- Python 3.12 or newer

## Setup

```bash
cd homework-2
python -m venv venv
# Activate the virtual environment:
# macOS/Linux:
source venv/bin/activate
# Windows (cmd):
venv\Scripts\activate.bat
# Windows (PowerShell):
venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

> **Note:** Always run commands from the `homework-2/` directory to avoid import errors.

## Start the Server

```bash
uvicorn src.main:app --reload
```

- The server will be available at: http://localhost:8000
- Interactive API docs: http://localhost:8000/docs
- See [API_REFERENCE.md](API_REFERENCE.md) for detailed endpoint info.

Or use the demo script to start the server and run sample requests:

```bash
bash demo/run.sh
```

## Run Tests

```bash
pytest tests/ --cov=src --cov-report=term-missing --cov-report=html
```

- Coverage HTML report: `htmlcov/index.html`

## Run Demo Requests

```bash
bash demo/sample-requests.sh
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| `ModuleNotFoundError: src` | Make sure you are in the `homework-2/` directory before running commands |
| `uvicorn: command not found` | Activate your venv and run `pip install -r requirements.txt` |
| Port 8000 in use | Use `uvicorn src.main:app --port 8001` or another available port |
| Import errors or test failures | Ensure the venv is activated and dependencies are installed |
