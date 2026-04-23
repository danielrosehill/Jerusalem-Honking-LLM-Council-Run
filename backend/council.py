"""3-stage LLM Council orchestration with personality-based members."""

import json
import os
from pathlib import Path
from typing import List, Dict, Any, Tuple
from .openrouter import query_personalities_parallel, query_model
from .config import (
    COUNCIL_MODEL,
    CHAIRMAN_MODEL,
    COUNCIL_PERSONALITIES,
    COUNCIL_QUESTIONS,
    COUNCIL_RESPONSE_SCHEMA,
)


_GROUNDING_DIR = Path(__file__).resolve().parent.parent / "grounding"


def _load_grounding_context() -> str:
    """Load every markdown file in grounding/ and concatenate for prompt use."""
    if not _GROUNDING_DIR.is_dir():
        return ""
    parts: List[str] = []
    for path in sorted(_GROUNDING_DIR.glob("*.md")):
        try:
            parts.append(f"===== FILE: {path.name} =====\n\n{path.read_text()}")
        except OSError:
            continue
    if not parts:
        return ""
    return (
        "GROUNDING CONTEXT — primary sources on the Jerusalem honking issue. "
        "Treat the figures, dates, quotations, and source names below as the "
        "authoritative factual basis for your reasoning. Prefer citing these "
        "over recalling from memory.\n\n"
        + "\n\n".join(parts)
    )


_GROUNDING_CONTEXT_CACHE: str | None = None


def get_grounding_context() -> str:
    global _GROUNDING_CONTEXT_CACHE
    if _GROUNDING_CONTEXT_CACHE is None:
        _GROUNDING_CONTEXT_CACHE = _load_grounding_context()
    return _GROUNDING_CONTEXT_CACHE


def get_personality_name(personality_id: str) -> str:
    """Get the display name for a personality ID."""
    for p in COUNCIL_PERSONALITIES:
        if p["id"] == personality_id:
            return p["name"]
    return personality_id


def _build_stage1_user_prompt(problem_statement: str) -> str:
    """Compose the per-councillor prompt asking one answer per question."""
    questions_block = "\n\n".join(
        f"{q['id'].upper()} — {q['label']}:\n{q['question']}"
        for q in COUNCIL_QUESTIONS
    )
    keys = ", ".join(f"\"{q['id']}\"" for q in COUNCIL_QUESTIONS)
    return (
        "PROBLEM STATEMENT:\n"
        f"{problem_statement}\n\n"
        "QUESTIONS — answer each one from your councillor lens:\n\n"
        f"{questions_block}\n\n"
        "Respond with a single JSON object containing exactly these keys: "
        f"{keys}. Each value is your answer to that question, written from "
        "your specific policy lens and with explicit awareness of the Middle "
        "East / Israeli municipal context. Draw your facts, figures, and "
        "quotations from the GROUNDING CONTEXT attached to this conversation; "
        "cite source file names (e.g. 10-kolhair-jerusalem-quiet-cities.md) "
        "when referring to specific claims."
    )


async def stage1_collect_responses(user_query: str) -> List[Dict[str, Any]]:
    """
    Stage 1: Collect structured per-question responses from every councillor.

    Each councillor returns a JSON object keyed by question id, with the
    Tavily search tool available for grounded answers.
    """
    grounding = get_grounding_context()
    user_messages: List[Dict[str, Any]] = []
    if grounding:
        user_messages.append({"role": "user", "content": grounding})
    user_messages.append(
        {"role": "user", "content": _build_stage1_user_prompt(user_query)}
    )

    responses = await query_personalities_parallel(
        COUNCIL_MODEL,
        COUNCIL_PERSONALITIES,
        user_messages,
        response_format={"type": "json_schema", "json_schema": COUNCIL_RESPONSE_SCHEMA},
    )

    stage1_results = []
    for personality in COUNCIL_PERSONALITIES:
        response = responses.get(personality["id"])
        if response is None:
            continue
        raw = response.get("content", "") or ""
        parsed: Dict[str, str] = {}
        try:
            parsed = json.loads(raw) if raw else {}
        except json.JSONDecodeError:
            parsed = {}
        rendered = _render_per_question_answers(parsed) if parsed else raw
        stage1_results.append({
            "model": personality["id"],
            "name": personality["name"],
            "response": rendered,
            "answers": parsed,
        })

    return stage1_results


def _render_per_question_answers(answers: Dict[str, str]) -> str:
    """Render the per-question JSON into a readable markdown block."""
    lines = []
    for q in COUNCIL_QUESTIONS:
        ans = answers.get(q["id"], "").strip()
        lines.append(f"### {q['id'].upper()} — {q['label']}\n\n{ans}")
    return "\n\n".join(lines)


async def stage2_collect_rankings(
    user_query: str,
    stage1_results: List[Dict[str, Any]]
) -> Tuple[List[Dict[str, Any]], Dict[str, str]]:
    """
    Stage 2: Each personality ranks the anonymized responses.
    """
    labels = [chr(65 + i) for i in range(len(stage1_results))]

    label_to_model = {
        f"Response {label}": result['name']
        for label, result in zip(labels, stage1_results)
    }

    responses_text = "\n\n".join([
        f"Response {label}:\n{result['response']}"
        for label, result in zip(labels, stage1_results)
    ])

    ranking_prompt = f"""You are evaluating different responses to the following question:

Question: {user_query}

Here are the responses from different council members (anonymized):

{responses_text}

Your task:
1. First, evaluate each response individually. For each response, explain what it does well and what it does poorly.
2. Then, at the very end of your response, provide a final ranking.

IMPORTANT: Your final ranking MUST be formatted EXACTLY as follows:
- Start with the line "FINAL RANKING:" (all caps, with colon)
- Then list the responses from best to worst as a numbered list
- Each line should be: number, period, space, then ONLY the response label (e.g., "1. Response A")
- Do not add any other text or explanations in the ranking section

Example of the correct format for your ENTIRE response:

Response A provides good detail on X but misses Y...
Response B is accurate but lacks depth on Z...
Response C offers the most comprehensive answer...

FINAL RANKING:
1. Response C
2. Response A
3. Response B

Now provide your evaluation and ranking:"""

    user_messages = [{"role": "user", "content": ranking_prompt}]

    responses = await query_personalities_parallel(
        COUNCIL_MODEL, COUNCIL_PERSONALITIES, user_messages
    )

    stage2_results = []
    for personality in COUNCIL_PERSONALITIES:
        response = responses.get(personality["id"])
        if response is not None:
            full_text = response.get('content', '')
            parsed = parse_ranking_from_text(full_text)
            stage2_results.append({
                "model": personality["id"],
                "name": personality["name"],
                "ranking": full_text,
                "parsed_ranking": parsed
            })

    return stage2_results, label_to_model


async def stage3_synthesize_final(
    user_query: str,
    stage1_results: List[Dict[str, Any]],
    stage2_results: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Stage 3: Chairman synthesizes final response.
    """
    stage1_text = "\n\n".join([
        f"Council Member ({result['name']}):\n{result['response']}"
        for result in stage1_results
    ])

    stage2_text = "\n\n".join([
        f"Reviewer ({result['name']}):\n{result['ranking']}"
        for result in stage2_results
    ])

    chairman_prompt = f"""You are the Chairman of a local-governance Policy Ideation Council.
The council has six members, each examining the policy challenge from a distinct professional
lens: Urban Planner, Municipal Fiscal Officer, Community & Equity Advocate, Legal & Regulatory
Analyst, Service Delivery Practitioner, and Policy Innovation & Comparative Scholar.

Each member has provided their perspective on the policy problem, and then ranked each other's
contributions on usefulness and rigour.

Policy Problem Statement: {user_query}

STAGE 1 — Councillor Perspectives:
{stage1_text}

STAGE 2 — Peer Rankings:
{stage2_text}

Your task as Chairman is to produce a synthesised Policy Ideation Report that a local
government official could take directly to a working session. Structure the report as follows:

1. **Restated Problem** — a one-paragraph framing of the policy challenge as you now understand it.
2. **Ideas Surfaced by the Council** — a consolidated, deduplicated catalogue of the distinct
   policy ideas, options, and instruments proposed. For each idea, note which lens (or lenses)
   surfaced it and a one-line rationale.
3. **Cross-Cutting Themes** — patterns and interdependencies visible across the councillors'
   perspectives (e.g. a zoning idea that also has fiscal and equity implications).
4. **Tensions & Trade-offs** — where councillors disagreed or where ideas are in direct tension
   (e.g. speed vs equity, cost vs reach). Name the tension; do not resolve it.
5. **Shortlist of Promising Directions** — 3–5 options the Chairman recommends for deeper
   development, with a brief justification drawing on the peer rankings and the councillors'
   substantive reasoning.
6. **Open Questions & Needed Evidence** — what the council could not determine without further
   data, consultation, or legal review.

Write in a neutral, report-style register suitable for a municipal audience. Do not invent
facts; stay grounded in what the council actually said and in the GROUNDING CONTEXT provided.
Do not flatten the distinct lenses into generic prose — preserve attribution where it matters.
When you evaluate the councillors' recommendations for usefulness, test them against the
grounding context: a recommendation that contradicts, ignores, or duplicates something already
happening in the grounding should be flagged accordingly."""

    grounding = get_grounding_context()
    messages: List[Dict[str, Any]] = [
        {"role": "system", "content": (
            "You are the Chairman of a local-governance Policy Ideation Council. Your role is "
            "to synthesise the councillors' diverse policy perspectives into a structured "
            "ideation report that a municipal decision-maker can act on. You preserve "
            "distinct lenses, surface tensions honestly, and produce a catalogue of ideas "
            "rather than a single recommended answer. A curated bundle of primary sources is "
            "attached as GROUNDING CONTEXT — use it to fact-check the councillors and to judge "
            "which recommendations are genuinely additive versus already in motion."
        )}
    ]
    if grounding:
        messages.append({"role": "user", "content": grounding})
    messages.append({"role": "user", "content": chairman_prompt})

    response = await query_model(CHAIRMAN_MODEL, messages)

    if response is None:
        return {
            "model": "chairman",
            "name": "Chairman",
            "response": "Error: Unable to generate final synthesis."
        }

    return {
        "model": "chairman",
        "name": "Chairman",
        "response": response.get('content', '')
    }


def parse_ranking_from_text(ranking_text: str) -> List[str]:
    """Parse the FINAL RANKING section from the model's response."""
    import re

    if "FINAL RANKING:" in ranking_text:
        parts = ranking_text.split("FINAL RANKING:")
        if len(parts) >= 2:
            ranking_section = parts[1]
            numbered_matches = re.findall(r'\d+\.\s*Response [A-Z]', ranking_section)
            if numbered_matches:
                return [re.search(r'Response [A-Z]', m).group() for m in numbered_matches]
            matches = re.findall(r'Response [A-Z]', ranking_section)
            return matches

    matches = re.findall(r'Response [A-Z]', ranking_text)
    return matches


def calculate_aggregate_rankings(
    stage2_results: List[Dict[str, Any]],
    label_to_model: Dict[str, str]
) -> List[Dict[str, Any]]:
    """Calculate aggregate rankings across all council members."""
    from collections import defaultdict

    model_positions = defaultdict(list)

    for ranking in stage2_results:
        parsed_ranking = parse_ranking_from_text(ranking['ranking'])
        for position, label in enumerate(parsed_ranking, start=1):
            if label in label_to_model:
                model_name = label_to_model[label]
                model_positions[model_name].append(position)

    aggregate = []
    for model, positions in model_positions.items():
        if positions:
            avg_rank = sum(positions) / len(positions)
            aggregate.append({
                "model": model,
                "average_rank": round(avg_rank, 2),
                "rankings_count": len(positions)
            })

    aggregate.sort(key=lambda x: x['average_rank'])
    return aggregate


async def generate_conversation_title(user_query: str) -> str:
    """Generate a short title for a conversation."""
    title_prompt = f"""Generate a very short title (3-5 words maximum) that summarizes the following question.
The title should be concise and descriptive. Do not use quotes or punctuation in the title.

Question: {user_query}

Title:"""

    messages = [{"role": "user", "content": title_prompt}]
    response = await query_model(COUNCIL_MODEL, messages, timeout=30.0)

    if response is None:
        return "New Conversation"

    title = response.get('content', 'New Conversation').strip().strip('"\'')
    if len(title) > 50:
        title = title[:47] + "..."
    return title


async def run_full_council(user_query: str) -> Tuple[List, List, Dict, Dict]:
    """Run the complete 3-stage council process."""
    stage1_results = await stage1_collect_responses(user_query)

    if not stage1_results:
        return [], [], {
            "model": "error",
            "name": "Error",
            "response": "All council members failed to respond. Please try again."
        }, {}

    stage2_results, label_to_model = await stage2_collect_rankings(user_query, stage1_results)
    aggregate_rankings = calculate_aggregate_rankings(stage2_results, label_to_model)

    stage3_result = await stage3_synthesize_final(
        user_query, stage1_results, stage2_results
    )

    metadata = {
        "label_to_model": label_to_model,
        "aggregate_rankings": aggregate_rankings
    }

    return stage1_results, stage2_results, stage3_result, metadata
