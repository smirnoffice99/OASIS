# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
# CLI
python main.py                            # Interactive case ID prompt
python main.py KR-2024-12345             # Direct case ID
python main.py KR-2024-12345 --report    # Regenerate report only

# Web UI
uvicorn web.app:app --reload --port 8000  # http://localhost:8000
# Windows shortcut: run_web.bat

# Tests (all mock LLM calls and input() — no API key needed)
python test_e2e.py                        # End-to-end: all handlers + report
python test_oa_parser.py                  # Parser unit tests
python test_prior_art_handler.py          # Individual handler tests
python test_clarity_handler.py
python test_unity_handler.py
python test_default_handler.py
python test_report_generator.py
python test_sample_manager.py
python test_main.py

# Sample management
python sample_manager.py add <file> --type <type>   # prior_art|clarity|unity|other
python sample_manager.py list
python sample_manager.py stats

# Build (Windows — produces dist/OASIS/OASIS.exe)
build.bat
```

## Architecture

### Data Flow

```
cases/{case_id}/oa.pdf + spec.pdf + claims_en.docx [+ citations/]
    → oa_parser.py        — extract rejections, classify type, set has_citations
    → session.py          — persist state to session.json
    → handlers/*          — type-specific multi-step analysis with user gates
    → sample_manager.py   — select style examples (few-shot or RAG)
    → report_generator.py — write final_comment.docx
```

CLI (`main.py`) and web (`web/app.py`) share all modules above. The web app exposes REST + SSE endpoints consumed by `web/static/` (plain HTML/JS with no build step).

### Rejection Handlers (`handlers/`)

`BaseHandler` owns the step loop: LLM call → print → await user input → save result. Subclasses implement `STEPS` (int) and `execute_step(step, feedback)`.

| Type | Handler | Steps | Notes |
|------|---------|-------|-------|
| prior_art | `PriorArtHandler` | 6 | Steps 1–3: invention/citation/diff; Steps 4–5: strategy + claim confirmation; Step 6: English comment |
| clarity | `ClarityHandler` | 3 | No citations; spec-internal analysis only |
| unity | `UnityHandler` | 3 | Branches on `has_citations` — different Step 1 & 2 logic |
| other | `DefaultHandler` | variable | User-driven |

Special commands handled in `BaseHandler`: `Y`/`승인` (approve), `종료` (save & exit), `재검토 N` (reopen rejection N), `승인취소` (undo last approval).

### LLM Client (`llm_client.py`)

Single gateway for all LLM calls. Provider/model set in `config.yaml` (currently: `gemini` / `gemini-2.5-flash`). Supports Claude, OpenAI, Gemini. Lazily initialized once with a module-level lock; shared across all web requests.

**OCR path**: image-only PDF pages → try Windows WinRT OCR first (via `winrt-*` Python bindings, no subprocess) → fall back to LLM Vision. WinRT runs on a dedicated daemon `asyncio` loop (`_get_winrt_loop()`) so completion callbacks are always delivered regardless of thread context. Results cached as `{stem}_ocr.txt`.

### Session Persistence (`session.py`)

`cases/{case_id}/session.json` tracks per-rejection `status` (`pending` / `in_progress` / `concluded`) and `current_step`. On restart, `concluded` rejections are skipped; others resume.

### Sample Style Learning (`sample_manager.py`)

- **< 20 samples**: few-shot — 3 most recently modified samples in prompt
- **≥ 20 samples**: RAG — chromadb semantic search (optional deps: `chromadb` + `sentence-transformers`; not in `requirements.txt`; requires C++ Build Tools)

### Web API (`web/app.py`)

`execute` and `report/draft` endpoints stream SSE via `StreamingResponse`. Key groups: Cases CRUD, Parse, Steps (execute/approve/cancel-approval/reopen), Citations OCR, Report (draft/finalize/download), Session.

In PyInstaller builds, `OASIS_DATA_DIR` env var overrides where `cases/` and `samples/` are stored.

## Core Rules

- **Never advance to next step without explicit `Y` / `승인`**
- Non-approval user input → regenerate current step with that feedback
- Always cite source (column/paragraph/page) when quoting references
- Use terminology from `claims_en.docx` verbatim in all English output
- Save every step result to `cases/{case_id}/rejection_{n}/step_{x}_result.md` before printing

## LLM Config (`config.yaml`)

```yaml
provider: gemini            # claude | openai | gemini
model: gemini-2.5-flash
api_key_env: GOOGLE_API_KEY
max_tokens: 16000
```

## Mock Test Case

`KR-TEST-001` — all 4 rejection types, mock files under `cases/KR-TEST-001/`. No real PDFs needed.
