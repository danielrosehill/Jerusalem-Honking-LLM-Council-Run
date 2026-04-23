---
name: start-council
description: Launch an LLM-Council-Policy-Ideation run — six policy-lens councillors (Urban Planner, Fiscal Officer, Equity Advocate, Legal Analyst, Service Delivery, Innovation Scholar) examine a local-governance policy problem via a single LLM behind different system prompts. Use when the user says "run the council", "deliberate on this policy problem", "/start-council", or provides a problem statement in the LLM-Council-Policy-Ideation repo. Starts the app and surfaces the Chairman's Policy Ideation Report plus optional PDF/podcast digests.
---

# Start a Council (Policy Ideation)

You are operating inside the `LLM-Council-Policy-Ideation` repo. This variant is tuned for **local-governance policy challenges** — the user supplies a policy problem statement, six domain-specialist councillors examine it, and the Chairman produces a structured Policy Ideation Report.

## Preconditions

1. Repo root must contain `backend/main.py`, `main.py`, and `start.sh`.
2. `OPENROUTER_API_KEY` must be set. No other keys are required for the base run.
3. `uv sync` and `cd frontend && npm install && cd ..` if dependencies are missing.

## Step 1 — Capture the policy problem

Ask the user for a **problem statement** describing the policy challenge. A good statement names:

- The municipality / jurisdiction (or jurisdiction type if anonymised)
- The observable problem (with any numbers or timeframe the user has)
- What prompted the council — a failing programme, a new mandate, a political pressure, a forthcoming decision

If the statement is sprawling, help the user tighten it to a single paragraph. The councillors take the framing literally — a buried assumption will propagate into every lens.

## Step 2 — Start the app

```bash
./start.sh
```

Or manually:

```bash
# Terminal 1
uv run python -m backend.main
# Terminal 2
cd frontend && npm run dev
```

Direct the user to `http://localhost:5173`.

## Step 3 — Surface the output

The UI walks through the three stages:

1. **Councillor perspectives** — six lenses respond independently.
2. **Peer review** — each councillor ranks the others' (anonymised) responses.
3. **Chairman synthesis** — the final **Policy Ideation Report** with restated problem, consolidated idea catalogue, cross-cutting themes, tensions, a shortlist of promising directions, and open questions.

Encourage the user to read **at least the Equity Advocate and the Fiscal Officer in full** before jumping to the synthesis — those two most often hold the load-bearing objections that the Chairman must reconcile.

## Step 4 — Digests

If requested, trigger:

- **PDF report** — Typst-typeset Policy Ideation Report. Suitable to share with a municipal working group.
- **Briefing podcast** — LLM-written script → Microsoft Edge TTS audio. Useful for a commuting official.

## Step 5 — Iterate

Offer to:

- Re-run with a tightened problem statement.
- Swap or add councillor lenses in `backend/config.py` for domain-specific policy work (e.g. Public Health Officer for health policy, Climate & Resilience lens for environmental policy).
- Fork the repo for a parallel topic area.

## Failure modes

- Missing `OPENROUTER_API_KEY` → stop.
- Frontend port collision → use an alternate port.
- A councillor returns empty → retry that slot; report if it fails twice.

## Out of scope

This variant is for *ideation* — surfacing and structuring the space of policy options. It is not a decision tool: the Chairman produces a catalogue with tensions named, not a single recommended option. For decision-making between defined options, use `LLM-Council-Decide`.
