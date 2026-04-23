# Jerusalem Honking — LLM Council Run

A concrete run of the [LLM-Council-Policy-Ideation](https://github.com/danielrosehill/LLM-Council-Policy-Ideation) template against a specific local-governance challenge in Jerusalem.

Problem statement: _to be defined_ — see `PROBLEM-STATEMENT.md` (drop one in at the repo root when ready).

The council comprises six domain-specialist advisors who examine the problem from distinct policy lenses; a Chairman synthesises the perspectives into a structured Policy Ideation Report.

Based on [karpathy/llm-council](https://github.com/karpathy/llm-council), adapted to use a single LLM with six policy-specialist system prompts rather than multiple model providers.

## How It Works

The user submits a **policy problem statement** (e.g. "Our downtown has lost 30% of retail tenants in three years — what should the city do?"). The council deliberates in three stages and returns a synthesised report.

### Council members

| Lens | Focus |
|--------|---------------|
| Urban Planner | Land use, zoning, transport, public space, density |
| Municipal Fiscal Officer | Budget envelope, revenue mechanisms, capital vs operating cost |
| Community & Equity Advocate | Distributional impact, vulnerable populations, participation |
| Legal & Regulatory Analyst | Statutory authority, pre-emption, procurement, implementing instruments |
| Service Delivery Practitioner | Implementability, staffing, workflows, frontline friction |
| Policy Innovation & Comparative Scholar | Evidence from other municipalities, unconventional instruments |

### Three-stage pipeline

1. **Stage 1 — Councillor Perspectives.** Each councillor examines the problem through their lens and proposes ideas, options, and considerations independently.
2. **Stage 2 — Peer Review.** Each councillor sees the other responses *anonymised* and ranks them for usefulness and rigour.
3. **Stage 3 — Chairman Synthesis.** The Chairman produces a structured **Policy Ideation Report**: restated problem, consolidated catalogue of ideas with attribution, cross-cutting themes, tensions and trade-offs, a shortlist of promising directions, and open questions.

## Digest Outputs

After deliberation, you can generate two digest formats:

- **PDF Report** -- A formatted Typst document with all stages, rankings, and the final Policy Ideation Report
- **Briefing Podcast** -- An LLM-written briefing script converted to audio via Microsoft Edge TTS, summarising the council's ideas for a commuting municipal official

## Setup

### 1. Install Dependencies

Requires [uv](https://docs.astral.sh/uv/) for Python and Node.js for the frontend.

```bash
uv sync
cd frontend && npm install && cd ..
```

### 2. Configure API Key

Create a `.env` file in the project root:

```bash
OPENROUTER_API_KEY=sk-or-v1-...
```

Get your API key at [openrouter.ai](https://openrouter.ai/).

### 3. Configure Model (Optional)

Set the base model and chairman model via environment variables in `.env`:

```bash
COUNCIL_MODEL=anthropic/claude-sonnet-4.5
CHAIRMAN_MODEL=anthropic/claude-sonnet-4.5
```

Or edit `backend/config.py` to customise the council lenses for a more specific policy domain (e.g. add a Public Health Officer lens for health-policy work, or a Climate & Resilience lens for environmental policy).

### 4. Optional: Install Typst and Edge TTS

For PDF report generation:
```bash
# Install Typst (see https://github.com/typst/typst)
cargo install typst-cli
# or via package manager
```

For podcast audio generation:
```bash
pip install edge-tts
```

## Running

```bash
./start.sh
```

Or manually:

```bash
# Terminal 1 - Backend
uv run python -m backend.main

# Terminal 2 - Frontend
cd frontend && npm run dev
```

Open http://localhost:5173 in your browser.

## Tech Stack

- **Backend:** FastAPI, async httpx, OpenRouter API
- **Frontend:** React + Vite, react-markdown
- **PDF Generation:** Typst
- **Audio Generation:** Microsoft Edge TTS (edge-tts)
- **Storage:** JSON files in `data/conversations/`

## Attribution

Based on [karpathy/llm-council](https://github.com/karpathy/llm-council) by Andrej Karpathy.
