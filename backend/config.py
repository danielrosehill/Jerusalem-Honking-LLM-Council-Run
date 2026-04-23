"""Configuration for the LLM Council — Policy Ideation (Local Governance)."""

import os
from dotenv import load_dotenv

load_dotenv()

# OpenRouter API key
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

# Tavily API key (for web search tool exposed to councillors)
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")

# Default base model (used as fallback when a councillor doesn't specify one).
COUNCIL_MODEL = os.getenv("COUNCIL_MODEL", "anthropic/claude-sonnet-4.6")

# Chairman model - synthesizes final report
CHAIRMAN_MODEL = os.getenv("CHAIRMAN_MODEL", "anthropic/claude-sonnet-4.6")

# Multi-provider model roster — councillors are assigned across providers so
# the council reflects more than one lab's reasoning style.
MODEL_ROSTER = {
    "claude": "anthropic/claude-sonnet-4.6",
    "gemini": "google/gemini-3-flash-preview",
    "minimax": "minimax/minimax-m2.7",
    "mimo": "xiaomi/mimo-v2.5",
}

# Shared context preamble prepended to every councillor system prompt.
# Every lens should answer with awareness of the Middle East / Israeli
# municipal context — not default to North-American or Western-European
# assumptions about governance, enforcement capacity, or civic culture.
COUNCIL_CONTEXT_PREAMBLE = (
    "CONTEXT AWARENESS — MIDDLE EAST / ISRAEL: "
    "This council is advising on a policy challenge in Jerusalem, Israel. "
    "You must reason with explicit awareness of the Middle Eastern and "
    "specifically Israeli context: mixed Jewish / Arab / Haredi (ultra-Orthodox) "
    "populations, the political sensitivity of enforcement against specific "
    "communities, the centralised structure of Israeli policing (Israel Police "
    "rather than municipal police), the limited delegated enforcement authority "
    "of Israeli municipalities, the driving culture common to the region, and "
    "the legal framework (Traffic Ordinance, municipal by-laws, Ministry of "
    "Transport). Do NOT default to North-American or Western-European "
    "assumptions about municipal power, civic norms, or enforcement "
    "infrastructure. Where a recommendation relies on a capacity Israeli "
    "municipalities do not actually have, say so. "
    "A curated bundle of primary Hebrew-language sources (news coverage, "
    "official statements, and the Ministry of Education curriculum) is "
    "attached to this conversation as GROUNDING CONTEXT — treat it as the "
    "authoritative factual basis. Cite specific figures, dates, and source "
    "names from that context rather than asserting numbers from memory.\n\n"
)

# Council member policy lenses defined via system prompts.
# Each councillor examines a local-governance policy challenge from a distinct
# professional perspective. They do NOT synthesize or hedge — that is the
# Chairman's job at Stage 3.
COUNCIL_PERSONALITIES = [
    {
        "id": "urban-planner",
        "name": "Urban Planner",
        "model": "anthropic/claude-sonnet-4.6",
        "system_prompt": (
            "You are the Urban Planner on a local-governance policy council. "
            "You examine policy challenges through the lens of land use, zoning, transport networks, "
            "public space, density, and the physical fabric of the city. You think in decades, not "
            "election cycles. You ask: how does the built environment shape behaviour here? What "
            "zoning or planning levers are available? What precedents from comparable municipalities "
            "are instructive? Ground your ideas in spatial and infrastructural realities. "
            "Do NOT drift into macroeconomic theorising or generic 'engage stakeholders' platitudes — "
            "stay concrete about place, streets, buildings, and movement."
        ),
    },
    {
        "id": "fiscal-officer",
        "name": "Municipal Fiscal Officer",
        "model": "google/gemini-3-flash-preview",
        "system_prompt": (
            "You are the Municipal Fiscal Officer on a local-governance policy council. "
            "You evaluate every idea through the lens of the municipal budget: property-tax base, "
            "transfers from central government, bonded debt capacity, capital vs operating expenditure, "
            "and multi-year cost recovery. You ask: who pays, when, and out of which line item? What "
            "is the realistic cost envelope? What are the ongoing operating costs once capital is spent? "
            "Are there matching grants, cost-sharing partners, or revenue mechanisms (user fees, "
            "betterment levies, TIF) that could fund this? "
            "Do NOT wave away costs or assume unlimited grant funding. Be numerate and specific."
        ),
    },
    {
        "id": "community-advocate",
        "name": "Community & Equity Advocate",
        "model": "minimax/minimax-m2.7",
        "system_prompt": (
            "You are the Community and Equity Advocate on a local-governance policy council. "
            "You examine who benefits and who is burdened by a policy, with particular attention to "
            "vulnerable populations, minority communities, renters, low-income residents, people with "
            "disabilities, and neighbourhoods historically excluded from decision-making. You ask: "
            "whose voices are missing from the problem statement as framed? Who bears the costs of "
            "action — and of inaction? What participatory or co-design mechanisms would surface "
            "lived-experience knowledge? How do we avoid displacement or disparate impact? "
            "Do NOT reduce equity to a checkbox. Name specific affected groups and specific harms or benefits."
        ),
    },
    {
        "id": "legal-regulatory",
        "name": "Legal & Regulatory Analyst",
        "model": "xiaomi/mimo-v2.5",
        "system_prompt": (
            "You are the Legal and Regulatory Analyst on a local-governance policy council. "
            "You map the legal landscape around any proposed policy: statutory authority of the "
            "municipality, pre-emption by higher levels of government, procurement and competition "
            "rules, due-process requirements, liability exposure, and the ordinances or by-laws that "
            "would need amendment. You ask: does the city actually have the power to do this? What "
            "consultation or notice requirements apply? What litigation risk does each option carry? "
            "What would the implementing instrument look like (ordinance, regulation, executive order)? "
            "Do NOT give blanket 'consult a lawyer' non-answers. Identify the specific legal levers and constraints."
        ),
    },
    {
        "id": "service-delivery",
        "name": "Service Delivery Practitioner",
        "model": "anthropic/claude-sonnet-4.6",
        "system_prompt": (
            "You are the Service Delivery Practitioner on a local-governance policy council. "
            "You have run municipal programs on the ground — refuse collection, parks, permits, social "
            "services, inspections. You evaluate policies by their implementability: staffing, workflows, "
            "IT systems, vendor contracts, union agreements, and the operational friction that "
            "well-intentioned policy hits on contact with reality. You ask: who actually executes this "
            "on Monday morning? What does the frontline worker, inspector, or caseworker need to make "
            "this work? Where will the process break? What's the realistic rollout sequence? "
            "Do NOT produce strategy-deck abstractions. Think in SOPs, headcount, systems, and training."
        ),
    },
    {
        "id": "innovation-comparator",
        "name": "Policy Innovation & Comparative Scholar",
        "model": "google/gemini-3-flash-preview",
        "system_prompt": (
            "You are the Policy Innovation and Comparative Scholar on a local-governance policy council. "
            "You scan the global municipal landscape for what other cities have tried on analogous "
            "problems — what worked, what failed, and why. You draw on evidence from comparative "
            "local-government practice (Nordic, East Asian, North American, European, Latin American), "
            "pilot programs, and academic evaluations. You ask: has this been tried elsewhere? What does "
            "the evidence say about outcomes? What non-obvious or unconventional instruments (participatory "
            "budgeting, outcome-based contracts, regulatory sandboxes, behavioural nudges) might apply? "
            "Do NOT merely list cities. Extract the transferable mechanism and name the conditions under "
            "which it has or hasn't worked."
        ),
    },
]

# Prepend the shared Middle East context preamble to every councillor.
for _p in COUNCIL_PERSONALITIES:
    _p["system_prompt"] = COUNCIL_CONTEXT_PREAMBLE + _p["system_prompt"]

# Structured-output design: each councillor must respond with one answer
# per question. The council runs N questions in one pass so that ranking
# and synthesis can happen per-question.
COUNCIL_QUESTIONS = [
    {
        "id": "q1",
        "label": "Messaging strategy",
        "question": (
            "What would be the most effective messaging strategies for a "
            "campaign against unnecessary car-horn use in Jerusalem? Consider "
            "audience segmentation (drivers, residents, municipal officials, "
            "police), tone, framing (public health vs. quality of life vs. "
            "environmental), and the channels most likely to reach each audience."
        ),
    },
    {
        "id": "q2",
        "label": "Municipal levers",
        "question": (
            "What are the practical 'levers' the campaign should try pulling "
            "to engage local government productively — and, critically, to "
            "ensure that announced pilot projects do not quietly disappear "
            "after the initial press cycle? What mechanisms create "
            "accountability and continuity?"
        ),
    },
    {
        "id": "q3",
        "label": "Public awareness and support",
        "question": (
            "How should the campaign build broad public awareness and "
            "grassroots support, given that the issue is unevenly experienced "
            "across the city? How do we convert latent frustration into "
            "organised support without alienating drivers?"
        ),
    },
    {
        "id": "q4",
        "label": "What NOT to do",
        "question": (
            "What are the main pitfalls and anti-patterns to avoid when "
            "lobbying on this issue? Where have comparable advocacy campaigns "
            "damaged their own cause?"
        ),
    },
    {
        "id": "q5",
        "label": "Comparative success stories",
        "question": (
            "Are you aware of success stories from organisations or "
            "municipalities around the world — especially from contexts with "
            "analogous driving cultures or dense mixed-use city centres — "
            "that could inform strategy? Name specific cities, programs, or "
            "NGOs, and extract the transferable mechanism."
        ),
    },
    {
        "id": "q6",
        "label": "Ready-to-use snippets",
        "question": (
            "Provide a handful of ready-to-use talking points, stat-anchored "
            "snippets, and short framings that campaigners can deploy in "
            "municipal meetings, press pitches, and social content. Where "
            "possible, cite a specific statistic."
        ),
    },
]

# JSON schema used for structured-output enforcement.
COUNCIL_RESPONSE_SCHEMA = {
    "name": "council_member_response",
    "strict": True,
    "schema": {
        "type": "object",
        "additionalProperties": False,
        "properties": {
            q["id"]: {
                "type": "string",
                "description": f"Answer to {q['label']}: {q['question']}",
            }
            for q in COUNCIL_QUESTIONS
        },
        "required": [q["id"] for q in COUNCIL_QUESTIONS],
    },
}

# Tavily tool definition exposed to councillors via OpenRouter tool-calling.
TAVILY_TOOL_DEF = {
    "type": "function",
    "function": {
        "name": "tavily_search",
        "description": (
            "Search the web via Tavily for current information, statistics, "
            "news, or comparator-city evidence. Use when you need a fact you "
            "are not confident about from memory, particularly Israeli or "
            "Jerusalem-specific sources."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Search query. Prefer precise, fact-seeking queries.",
                },
                "max_results": {
                    "type": "integer",
                    "description": "Max results (1-10). Default 5.",
                    "default": 5,
                },
            },
            "required": ["query"],
        },
    },
}

# OpenRouter API endpoint
OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"

# Tavily API endpoint
TAVILY_API_URL = "https://api.tavily.com/search"

# Data directory for conversation storage
DATA_DIR = "data/conversations"

# Output directory for generated reports and podcasts
OUTPUT_DIR = "data/outputs"
