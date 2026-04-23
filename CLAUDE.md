# CLAUDE.md -- LLM Council: Policy Ideation (Local Governance)

## What This Is

A variant of the LLM Council pattern tuned for **policy ideation on local-governance
challenges**. The user provides a problem statement describing a policy challenge facing a
municipality; six domain-specialist councillors examine it from distinct policy lenses; a
Chairman synthesises the perspectives into a structured Policy Ideation Report.

Single model, six system-prompt-defined policy lenses (not multi-provider).

## Architecture

- `backend/config.py` -- Model config + councillor lens definitions (system prompts)
- `backend/council.py` -- 3-stage orchestration (perspectives, peer review, Chairman synthesis)
- `backend/openrouter.py` -- OpenRouter API client with parallel lens querying
- `backend/digest.py` -- PDF (Typst) and briefing podcast (Edge TTS) generation
- `backend/storage.py` -- JSON file storage for conversations
- `backend/main.py` -- FastAPI endpoints
- `frontend/` -- React + Vite UI with stage tabs and digest panel

## Council lenses

- Urban Planner
- Municipal Fiscal Officer
- Community & Equity Advocate
- Legal & Regulatory Analyst
- Service Delivery Practitioner
- Policy Innovation & Comparative Scholar

Swap or extend these in `backend/config.py::COUNCIL_PERSONALITIES` for
more specific policy domains (e.g. add a Public Health Officer for health policy, a
Climate & Resilience lens for environmental policy).

## Chairman output

The Chairman produces a structured report, not a single "answer":

1. Restated problem
2. Consolidated catalogue of ideas (with lens attribution)
3. Cross-cutting themes
4. Tensions & trade-offs
5. Shortlist of promising directions
6. Open questions & needed evidence

The Chairman prompt is in `backend/council.py::stage3_synthesize_final`.

## Key Design Decisions

- Single model, multiple policy lenses via system prompts
- Stage 2 uses anonymous labels (Response A, B, C) to prevent bias
- Chairman synthesises a *catalogue of ideas* rather than a single recommended option --
  this is ideation, not decision-making
- Backend port 8001, frontend port 5173

## Running

```bash
./start.sh
# or: uv run python -m backend.main & cd frontend && npm run dev
```

Requires `.env` with `OPENROUTER_API_KEY`.
