# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**OASIS** (Office Action Strategy & Intelligence System) — A Python tool that automates responses to Korean Patent Office rejection notices (의견제출통지서). It guides a patent attorney through multi-step analysis of each rejection reason, then generates a formal English comment `.docx` for the client.

All source code lives in `oa-tool/`. Run all commands from that directory.

## Running the Tool

```bash
# CLI
cd oa-tool
python main.py                                          # Interactive case ID prompt
python main.py KR-2024-12345                           # Direct case ID
python main.py KR-2024-12345 --report                  # Regenerate report only

# Web UI (FastAPI)
cd oa-tool
uvicorn web.app:app --reload --port 8000               # http://localhost:8000
# or on Windows: run_web.bat

# Sample management
python sample_manager.py add <file> --type <type>       # prior_art|clarity|unity|other
python sample_manager.py list
python sample_manager.py delete <id>
python sample_manager.py search <keyword>
python sample_manager.py stats
```

## Running Tests

```bash
cd oa-tool
python test_e2e.py                    # End-to-end (all handlers + report, mocked LLM + input)
python test_oa_parser.py              # Parser unit tests
python test_prior_art_handler.py      # Individual handler unit tests
python test_clarity_handler.py
python test_unity_handler.py
python test_default_handler.py
python test_report_generator.py
python test_sample_manager.py
python test_main.py
```

All tests mock LLM calls and `input()` — no API keys needed.

## Building the Executable

```bash
# Windows — produces dist/OASIS/OASIS.exe
cd oa-tool
build.bat
```

`launcher.py` is the PyInstaller entry point. It starts FastAPI in a background thread, then opens the browser automatically. `oasis.spec` controls the build. RAG dependencies (`chromadb`, `sentence-transformers`) are excluded from the build because they require C++ Build Tools; the tool runs in few-shot mode (< 20 samples) without them.

## Setup

```bash
cd oa-tool
cp .env.example .env                  # Then fill in API key
# config.yaml controls active provider/model
```

## Tech Stack

- Python 3.11+, PyYAML, PyMuPDF (`fitz`), python-docx, python-dotenv
- Web: FastAPI + uvicorn (static files served from `web/static/`)
- LLM: `anthropic`, `openai`, `google-generativeai`
- CLI input: `prompt_toolkit` (optional — falls back to `input()` if not installed)
- RAG: `chromadb` + `sentence-transformers` (optional — not in `requirements.txt`; needs C++ Build Tools)

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

The CLI (`main.py`) and the web app (`web/app.py`) share all the above modules. The web app exposes REST endpoints consumed by `web/static/` (plain HTML/JS).

### Rejection Type Handlers

Each type has a distinct analysis pipeline:

| Type | Name | Steps | Key notes |
|------|------|-------|-----------|
| A | Prior Art (`prior_art`) | 5 | Novelty + inventive step unified; Step 4 always uses inventive step standard |
| B | Clarity (`clarity`) | 3 | No citations; spec-internal analysis only |
| C | Unity (`unity`) | 3 | Branches on `has_citations` flag — different Step 1 & 2 logic |
| D | Other (`other`) | variable | Collaborate with user to determine analysis approach |

### LLM Abstraction (`llm_client.py`)

All LLM calls go through `llm_client.py` only. Provider and model are set in `config.yaml`:

```yaml
provider: gemini            # claude | openai | gemini
model: gemini-2.5-flash
api_key_env: GOOGLE_API_KEY
max_tokens: 16000
```

Supported models: Claude (`claude-sonnet-4-6`, `claude-haiku-4-5`), OpenAI (`gpt-4o`, `gpt-4o-mini`), Gemini (`gemini-2.5-flash`, `gemini-2.5-pro`).

### Sample Style Learning

- **< 20 samples**: Few-shot mode — 3 most recently modified samples included in prompt
- **≥ 20 samples**: Auto-switches to RAG mode — chromadb semantic search selects top 3 matches
- Vector DB stored at `samples/vector_db/` (local, no server needed)

### Session Persistence

`cases/{case_id}/session.json` tracks each rejection's `status` (`pending` / `in_progress` / `concluded`) and `current_step`. On restart, `concluded` rejections are skipped; others resume from `current_step`.

## Core Rules

- **Never advance to the next step without explicit user approval** (`"Y"` or `"승인"`)
- When the user inputs text (not `Y`/`승인`), regenerate the current step with their feedback
- Special commands: `"종료"` (save & exit), `"재검토 N"` (reopen rejection N), `"승인취소"` (undo previous step's approval and go back)
- Always cite source (column/paragraph/page) when quoting cited references
- Use terminology from `claims_en.docx` verbatim in all English output
- Save every step result to `cases/{case_id}/rejection_{n}/step_{x}_result.md` before printing to terminal
- API keys via environment variables only (`ANTHROPIC_API_KEY`, `OPENAI_API_KEY`, `GOOGLE_API_KEY`)

## File Layout

```
cases/{case_id}/
├── oa.pdf, spec.pdf, claims_en.docx        ← required inputs
├── citations/D1.pdf, D2.pdf, ...           ← conditional
├── citations/D1_ocr.txt, ...               ← OCR cache (auto-generated for image PDFs)
├── session.json
├── rejection_1/
│   ├── step_1_result.md … step_N_result.md
│   ├── dialogue.json
│   └── conclusion.md
└── final_comment.docx

samples/{prior_art,clarity,unity,other}/   ← .docx or .txt style examples
samples/vector_db/                          ← chromadb store (auto-created, only if RAG deps installed)
prompts/{prior_art,clarity,unity,unity_with_citations,default,report}.txt
```

**PDF OCR**: When a PDF page has no extractable text, `llm_client.ocr_image()` is called. It first tries Windows WinRT OCR via `powershell.exe` (no extra Python bindings needed, works in PyInstaller builds); if that fails or returns empty, it falls back to LLM Vision (Claude/OpenAI/Gemini). The full result is cached as `{stem}_ocr.txt` next to the PDF so subsequent reads skip the call entirely.

## Final Output Format (`final_comment.docx`)

Sections per rejection ground:
- `N.1 Summary of Rejection`
- `N.2 Our Analysis` (with subsections for claimed invention, cited refs, differences — Type A only)
- `N.3 Proposed Response Strategy`
- `Overall Strategy` (final section)

Tone: formal, concise English for client delivery. Generated with `python-docx`.

## Mock Test Case

`KR-TEST-001` covers all 4 rejection types:
- Rejection #1: Prior Art (novelty+inventive step) — Claims 1,3,5 / D1 (US10,123,456), D2 (US9,876,543)
- Rejection #2: Clarity (§42) — Claim 7, ambiguous term "제1 측위 기준값"
- Rejection #3: Unity (`has_citations: true`) — Groups A (claims 1-5) vs B (claims 6-8) / D1

Mock files: `cases/KR-TEST-001/{oa_mock.txt, spec_mock.txt, claims_en_mock.txt, citations/D1_mock.txt, citations/D2_mock.txt}`
