# FitBuddy

FitBuddy is a FastAPI fitness assistant that creates seven-day workout plans, concise nutrition tips, and feedback-based plan updates with Google Gemini. It works even without a Gemini key (built-in fallback plan and tips).

## Project structure

```
fitbuddy/
├── app/
│   ├── main.py                  # FastAPI app, static mount, routes for / and /health
│   ├── routes.py                # API endpoints
│   ├── database.py              # SQLite (sqlite3) storage
│   ├── schemas.py               # Pydantic request validation
│   ├── models.py                # Dataclasses
│   ├── config.py                # Environment settings
│   ├── ai_common.py             # Shared Gemini call
│   ├── gemini_generator.py      # Workout plan prompt
│   ├── gemini_flash_generator.py# Nutrition tips prompt (JSON)
│   ├── updated_plan.py          # Feedback-based plan revision
│   ├── static/                  # Static files
│   └── templates/index.html     # Frontend (single page)
├── tests/test_app.py
├── requirements.txt / requirements-dev.txt
├── .env.example  .gitignore  pytest.ini  render.yaml
└── .vscode/                     # VS Code settings + run config
```

## Run locally (Windows PowerShell)

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements-dev.txt
copy .env.example .env      # then edit .env
python -m uvicorn app.main:app --reload
```

macOS / Linux:

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements-dev.txt
cp .env.example .env
python -m uvicorn app.main:app --reload
```

Open http://127.0.0.1:8000 (API docs: http://127.0.0.1:8000/docs).

## Configuration (`.env`)

| Variable | Purpose |
|---|---|
| `GEMINI_API_KEY` | Get one at https://aistudio.google.com/apikey. Leave unset to use fallback content. |
| `FITBUDDY_WORKOUT_MODEL` | Model for workout plans (default `gemini-2.5-pro`) |
| `FITBUDDY_TIP_MODEL` | Model for nutrition tips (default `gemini-2.5-flash`) |
| `ADMIN_TOKEN` | Password for the Admin tab |
| `FITBUDDY_DB_PATH` | Optional custom SQLite file path |

If a model name is invalid or unavailable, the app automatically serves the fallback plan instead of failing.

## Tests

```powershell
python -m pytest -v
```

Tests use a temporary database and never call Gemini.

## Deployment

`render.yaml` configures a Render web service. Add `GEMINI_API_KEY` and `ADMIN_TOKEN` as secret environment variables. Note: Render's free disk is ephemeral, so the SQLite data resets on redeploy.

## Prerequisites and documentation

FastAPI (https://fastapi.tiangolo.com/), Gemini API (https://ai.google.dev/), Python (https://docs.python.org/3/), SQLite (https://www.sqlite.org/docs.html), Uvicorn (https://www.uvicorn.org/).
