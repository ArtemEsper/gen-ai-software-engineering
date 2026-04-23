# How to Run — Banking Transactions API

This guide walks you through setting up and running the API from scratch, even if you are new to Python.

---

## Prerequisites

| Requirement | Version | How to check |
|-------------|---------|--------------|
| Python | 3.9 or newer | `python --version` or `python3 --version` |
| pip | bundled with Python | `pip --version` |

If Python is not installed, download it from https://www.python.org/downloads/ and follow the installer instructions for your operating system.

---

## Project Structure

```
homework-1/
├── README.md
├── HOWTORUN.md
├── requirements.txt
├── .gitignore
├── src/
│   └── main.py          ← the entire API lives here
└── demo/
    ├── run.sh           ← convenience start script (macOS / Linux)
    ├── sample-requests.http
    └── sample-data.json
```

---

## Step 1 — Clone or Download the Project

If you received a zip file, extract it and open a terminal inside the `homework-1/` folder.

If you are cloning from Git:

```bash
git clone <repository-url>
cd homework-1
```

---

## Step 2 — Create a Virtual Environment (Recommended)

A virtual environment keeps the project's dependencies isolated from the rest of your system.

**macOS / Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

**Windows (Command Prompt):**
```cmd
python -m venv venv
venv\Scripts\activate
```

**Windows (PowerShell):**
```powershell
python -m venv venv
venv\Scripts\Activate.ps1
```

You should see `(venv)` appear at the beginning of your terminal prompt, which means the virtual environment is active.

---

## Step 3 — Install Dependencies

With the virtual environment active, install the required packages:

```bash
pip install -r requirements.txt
```

This installs:
- **fastapi** — the web framework
- **uvicorn[standard]** — the ASGI server that runs the app

The installation should take less than a minute.

---

## Step 4 — Start the Server

**Option A — Using the demo script (macOS / Linux):**

```bash
chmod +x demo/run.sh
./demo/run.sh
```

**Option B — Running directly (all platforms):**

```bash
uvicorn src.main:app --reload --host 127.0.0.1 --port 3000
```

You should see output similar to:

```
INFO:     Uvicorn running on http://127.0.0.1:3000 (Press CTRL+C to quit)
INFO:     Started reloader process [12345]
INFO:     Started server process [12346]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

The `--reload` flag means the server automatically restarts whenever you save a change to `src/main.py`. Remove it for a production-like run.

---

## Step 5 — Verify the Server is Running

Open your browser and visit:

```
http://localhost:3000
```

You should see:

```json
{"message": "Banking Transactions API is running"}
```

---

## Step 6 — Explore the Interactive API Docs

FastAPI generates interactive documentation automatically. Open either of these URLs in your browser:

| UI | URL |
|----|-----|
| Swagger UI (try requests in the browser) | http://localhost:3000/docs |
| ReDoc (read-only reference) | http://localhost:3000/redoc |

The Swagger UI lets you send real requests directly from the browser without needing any extra tools.

---

## Step 7 — Run the Automated Test Suite

A bash script in `demo/` exercises every endpoint defined in the assignment (Tasks 1–4):

```bash
bash demo/sample-requests.sh
```

Expected output when everything is working:

```
Results: 39 tests  |  39 passed  |  0 failed
```

You can point it at a different host/port if needed:

```bash
bash demo/sample-requests.sh http://127.0.0.1:3001
```

---

## Step 8 — Manual Testing

### Using curl

```bash
# Create a deposit
curl -X POST http://localhost:3000/transactions \
  -H "Content-Type: application/json" \
  -d '{
    "fromAccount": "ACC-00001",
    "toAccount": "ACC-00002",
    "amount": 250.00,
    "currency": "USD",
    "type": "deposit"
  }'

# List all transactions
curl http://localhost:3000/transactions

# Get account balance
curl http://localhost:3000/accounts/ACC-00002/balance

# Get account summary
curl http://localhost:3000/accounts/ACC-00002/summary
```

### Using VS Code REST Client

Install the **REST Client** extension in VS Code, then open `demo/sample-requests.http` and click **Send Request** above any request block.

### Using Postman

Import the requests manually or paste the curl commands into Postman's import dialog.

---

## Stopping the Server

Press `Ctrl + C` in the terminal where the server is running.

---

## Deactivating the Virtual Environment

When you are done, deactivate the virtual environment:

```bash
deactivate
```

---

## Troubleshooting

### `command not found: python3`
Try `python` instead of `python3`. On Windows, `python` is the standard command.

### `ModuleNotFoundError: No module named 'fastapi'`
The virtual environment may not be active. Run `source venv/bin/activate` (macOS/Linux) or `venv\Scripts\activate` (Windows) and then `pip install -r requirements.txt` again.

### `Address already in use` on port 3000
Another process is using port 3000. Either stop that process or start the server on a different port:

```bash
uvicorn src.main:app --reload --host 127.0.0.1 --port 3001
```

Then replace `3000` with `3001` in all your requests.

### `Permission denied` when running `demo/run.sh`
Make the script executable first:

```bash
chmod +x demo/run.sh
```

### Validation errors (HTTP 422)
FastAPI returns a 422 response when the request body does not match the expected schema. Check that:
- `amount` is a positive number with at most 2 decimal places (e.g., `100.50`)
- `fromAccount` and `toAccount` follow the format `ACC-XXXXX` (5 alphanumeric characters after the dash)
- `currency` is a supported ISO 4217 code such as `USD`, `EUR`, `GBP`, or `JPY`
- `type` is one of `deposit`, `withdrawal`, or `transfer`

---

## Quick Reference — All Endpoints

| Method | URL | Description |
|--------|-----|-------------|
| `GET` | `/` | Health check |
| `POST` | `/transactions` | Create a transaction |
| `GET` | `/transactions` | List transactions (supports filters) |
| `GET` | `/transactions/{id}` | Get a single transaction |
| `GET` | `/accounts/{accountId}/balance` | Get account balance |
| `GET` | `/accounts/{accountId}/summary` | Get account summary |

### Query Parameters for `GET /transactions`

| Parameter | Example | Description |
|-----------|---------|-------------|
| `accountId` | `ACC-12345` | Filter by account (from or to) |
| `type` | `transfer` | Filter by transaction type |
| `from` | `2024-01-01` | Start date (inclusive) |
| `to` | `2024-01-31` | End date (inclusive) |
