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

# Run a single test method
python -m unittest test_prior_art_handler.TestPriorArtHandler.test_step1 -v

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

CLI (`main.py`) and web (`web/app.py`) share all modules above. The web app exposes REST + SSE endpoints consumed by `web/static/` (plain HTML/JS, no build step, uses `marked.min.js` for Markdown rendering).

### Rejection Handlers (`handlers/`)

`BaseHandler` owns the step loop: LLM call → print → await user input → save result. Subclasses implement `STEPS` (int) and `execute_step(step, messages)`.

| Type | Handler | Steps | Notes |
|------|---------|-------|-------|
| prior_art | `PriorArtHandler` | 6 | Steps 1–3: invention/citation/diff; Steps 4–5: strategy + claim confirmation; Step 6: English comment |
| clarity | `ClarityHandler` | 4 | No citations; spec-internal analysis only |
| unity | `UnityHandler` | 4 | Branches on `has_citations` at `execute_step()` call time — different Step 1 & 2 prompt and logic |
| other | `DefaultHandler` | variable | LLM plans dynamic steps; plan saved to `rejection_N/analysis_plan.json` |

Special commands handled in `BaseHandler`: `Y`/`승인` (approve), `종료` (save & exit), `재검토 N` (reopen rejection N), `승인취소` (undo last approval and go back one step — deletes stale `step_N_result.md`).

**`execute_step(step, messages)` contract**:
- Initial call: `messages=[]` → handler constructs full system prompt + user message and calls `llm.chat()`
- Feedback call: `messages=[{user: initial_prompt}, {assistant: prev_result}, {user: feedback}]` → handler calls `llm.chat_messages(messages)` so LLM sees full context

**Guidance marker**: step results may contain `<!-- oasis-guidance -->` lines. These are rendered in the UI but stripped from LLM message history so they never count as LLM output when the user requests regeneration.

### LLM Client (`llm_client.py`)

Single gateway for all LLM calls. Provider/model set in `config.yaml`. Supports Claude, OpenAI, Gemini. Lazily initialized once with a module-level lock; shared across all web requests.

Public methods: `chat()`, `chat_stream()`, `chat_messages()`, `chat_messages_stream()`, `ocr_image()`, `load_prompt()`.

**OCR path**: image-only PDF pages → try Windows WinRT OCR first (via `winrt-*` Python bindings, no subprocess) → fall back to LLM Vision. WinRT runs on a dedicated daemon `asyncio` loop (`_get_winrt_loop()`) — a single long-lived loop in a daemon thread — so completion callbacks are always delivered regardless of the calling thread context. For each page WinRT tries Korean (`ko`) and English (`en-US`) and returns whichever produces the longer text. Results cached as `{stem}_ocr.txt`.

### OA Parser (`oa_parser.py`)

Non-obvious behaviors:
- **Prior Art merging**: consecutive prior_art rejections (e.g., novelty + inventive step) are auto-merged into one `RejectionInfo` with combined claims/citations.
- **Claims extraction priority**: `[심사결과]` summary table > block text (handles "청구항 전항", "제N항 내지 제M항", PDF digit-separation artifacts). Claim ranges with span ≥ 500 are rejected as parser artifacts.
- **Text normalization**: removes spaces inserted by PyMuPDF between Korean syllables (applied repeatedly until stable).
- **Citation ID normalization**: "인용발명 N" / "인용문헌 N" → "DN"; duplicates removed while preserving discovery order.

### Session Persistence (`session.py`)

`cases/{case_id}/session.json` tracks per-rejection `status` (`pending` / `in_progress` / `concluded`) and `current_step`. On restart, `concluded` rejections are skipped; others resume from `current_step`.

`create_session()` **deletes all existing `rejection_N/` folders** before writing a new session — prevents stale step results from a previous parse from polluting the workspace.

### Report Generator (`report_generator.py`)

Two generation modes:
- **Combine** (`generate()` / CLI): uses handler's final step output directly, no extra LLM call per rejection.
- **Structured** (web draft): LLM regenerates per-section (Summary / Analysis / Strategy) with optional feedback.

Web flow: `generate_draft()` → saves `draft_comment.md` + `draft_data.json` → `finalize()` reads those and writes `final_comment.docx` (no LLM calls at finalize time). `draft_data.json` structure: `{"sections": [{rejection_meta, raw_comment, summary, analysis, strategy}, ...], "overall": {...}}`.

### Sample Style Learning (`sample_manager.py`)

- **< 20 samples**: few-shot — 3 most recently modified samples in prompt
- **≥ 20 samples**: RAG — chromadb semantic search (optional deps: `chromadb` + `sentence-transformers`; not in `requirements.txt`; requires C++ Build Tools)

### Web API (`web/app.py`)

SSE streaming: `execute` endpoints send `": keepalive\n\n"` every 15 s. Step execution has a **1800 s** deadline (accommodates OCR + LLM); report draft has a **600 s** deadline. Key endpoint groups: Cases CRUD, Parse, Steps (execute / approve / cancel-approval / reopen), Citations OCR (cancel / resume with partial-progress tracking), Report (draft / finalize / download), Session.

**Citation OCR pipeline** (triggered on upload if image pages detected):
- Upload rejects PDFs with > 100 image pages.
- Phase 1 (main thread): sequential page text extraction / PNG rendering — fitz is not thread-safe so this stays single-threaded.
- Phase 2 (thread pool, 4 workers): parallel `llm.ocr_image()` calls for image-only pages.
- Cancellation: each citation gets a `threading.Event` in `_ocr_cancel_events` (keyed `"case_id/citation_id"`); uploading the same file again cancels any running OCR.
- Resumption: only contiguous successfully-OCR'd pages are preserved in `_ocr_partial.json`; the next run starts from the first failed page.

**Step prompt caching** (web only): `step_N_prompt.md` is saved on first (no-feedback) execution and reused as the fixed initial prompt for all subsequent feedback regenerations. A fresh execution (no prior feedback) deletes any existing prompt cache first.

Notable: `GET /api/cases/{id}/rejections/{rid}/steps/{step}/dialogue` returns the full feedback history for a step.

In PyInstaller builds, `OASIS_DATA_DIR` env var overrides where `cases/` and `samples/` are stored.

### PyInstaller Build (`launcher.py`, `oasis.spec`)

`launcher.py` is the entry point. On startup it detects `sys.frozen`, creates `{exe_dir}/oasis_data/`, copies `prompts/` from the bundle on first run, sets `OASIS_DATA_DIR`, then starts FastAPI in a background thread and opens the browser. `oasis.spec` explicitly lists hidden imports and uses `collect_all('winrt')` for the WinRT OCR package.

## File Layout

```
cases/{case_id}/
├── oa.pdf, spec.pdf, claims_en.docx
├── citations/D1.pdf, ...
├── citations/D1_ocr.txt, ...          ← OCR cache (full result)
├── citations/D1_ocr_partial.json, ... ← partial progress for mid-job resume
├── citations/D1_ocr_progress.txt, ... ← current page counter
├── session.json
├── rejection_N/
│   ├── step_1_result.md … step_N_result.md
│   ├── step_1_prompt.md …             ← web only: initial prompt cache for regeneration
│   ├── analysis_plan.json             ← DefaultHandler only: dynamic step plan
│   ├── dialogue.json
│   └── conclusion.md
├── draft_comment.md, draft_data.json  ← web report draft
└── final_comment.docx

prompts/                               ← one .txt per handler type + report
    prior_art.txt, clarity.txt, unity.txt, unity_with_citations.txt, default.txt, report.txt
```

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
