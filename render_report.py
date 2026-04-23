"""Render a focused policy digest PDF from an existing council run.

Reads the stage1/stage2/stage3 JSON from data/run-<stamp>/, asks the chairman
model to produce a concentrated synthesis (novel ideas; convergence/divergence;
most useful recommendations; grounding-tagged), and renders the result via
Typst to a PDF.

Usage:
    uv run python render_report.py                # newest run
    uv run python render_report.py run-20260423T150817
"""

import asyncio
import json
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path

from backend.config import CHAIRMAN_MODEL
from backend.council import get_grounding_context
from backend.openrouter import query_model


ROOT = Path(__file__).resolve().parent
RUN_ROOT = ROOT / "data"


def pick_run_dir(argv_arg: str | None) -> Path:
    if argv_arg:
        d = RUN_ROOT / argv_arg if not argv_arg.startswith("/") else Path(argv_arg)
        if not d.is_dir():
            sys.exit(f"run dir not found: {d}")
        return d
    runs = sorted(RUN_ROOT.glob("run-*"))
    if not runs:
        sys.exit("no runs found in data/")
    return runs[-1]


def load_run(run_dir: Path) -> tuple[list, list, dict, dict]:
    s1 = json.loads((run_dir / "stage1.json").read_text())
    s2 = json.loads((run_dir / "stage2.json").read_text())
    s3 = json.loads((run_dir / "stage3.json").read_text())
    meta = json.loads((run_dir / "metadata.json").read_text())
    return s1, s2, s3, meta


async def synthesize_focused_digest(
    problem: str,
    stage1: list,
    stage2: list,
    stage3: dict,
    grounding: str,
) -> str:
    """Ask the chairman model for a concentrated, deliverable-style synthesis."""
    councillor_block = "\n\n---\n\n".join(
        f"## {r['name']}\n\n{r['response']}" for r in stage1
    )
    reviewer_block = "\n\n---\n\n".join(
        f"## {r['name']}\n\n{r['ranking']}" for r in stage2
    )
    chairman_full = stage3.get("response", "")

    user_prompt = f"""You are condensing a full LLM-council deliberation into a focused, deliverable-style policy digest.

The audience is a Jerusalem Municipality working-group member and the Jerusalem Green Fund. They do not need the full 6-section ideation report again — that already exists as the Chairman's long-form output. They need a concentrated document organised around three questions:

1. **What are the genuinely NOVEL ideas** — proposals that are not already in motion per the GROUNDING CONTEXT, and that the campaign or municipality could adopt tomorrow?
2. **Where do the councillors CONVERGE, and where do they DIVERGE** — which recommendations did multiple lenses independently arrive at (high confidence); which are idiosyncratic to one lens; where do lenses actively disagree?
3. **Which recommendations are MOST USEFUL** — ranked by (a) implementability within Israeli municipal authority, (b) differential impact beyond what is already funded, and (c) political and community feasibility in Jerusalem's Jewish/Arab/Haredi mix.

Problem statement (abridged acceptable):
{problem[:4000]}

Councillor per-question answers (Stage 1):
{councillor_block}

Peer reviews (Stage 2):
{reviewer_block}

Chairman's long-form report (Stage 3), available for reference:
{chairman_full[:15000]}

---

Produce a markdown document with exactly these sections, each tight and signal-dense. Do NOT repeat the long Chairman report. Flag every specific claim against the grounding corpus and tag ideas as "already in motion" when they restate a fact from grounding.

# Focused Policy Digest: Jerusalem Unnecessary Honking

## 1. Executive Summary (150 words max)

## 2. The Five Most Useful Recommendations (ranked)
For each: a short title; which councillor lens(es) surfaced it; why it is additive vs. already in motion; the specific actor who must act; estimated effort; a concrete first step.

## 3. Points of Convergence
Recommendations where three or more lenses independently arrived at the same proposal. Briefly note what makes them robust.

## 4. Points of Divergence and Live Tensions
Where lenses actively disagree or where an idea has a structural trade-off. Name the tension; do not resolve it.

## 5. Novel Ideas Worth Prototyping
Ideas that appeared in only one or two lenses but are materially additive to the current Quiet Cities programme. Include lens attribution and a feasibility note.

## 6. What to Drop
Suggestions that are either (a) already in motion per the grounding (flag which grounding file), (b) outside Israeli municipal authority, or (c) politically infeasible in Jerusalem's demographic mix.

## 7. Evidence Gaps
Specific facts the council could not determine from the grounding — what would need a fresh FOI, interview, or dataset.

Write in neutral, policy-register prose. Use bullet lists where tables would be clumsy in plain markdown. Do not invent facts; cite grounding file names when referring to specific claims (e.g. {{10-kolhair-jerusalem-quiet-cities.md}}).
"""

    messages = [
        {"role": "system", "content": (
            "You are the Chairman of a Policy Ideation Council producing a "
            "condensed deliverable for a municipal audience. You privilege "
            "signal over completeness, and you are fact-checked against the "
            "attached GROUNDING CONTEXT."
        )},
    ]
    if grounding:
        messages.append({"role": "user", "content": grounding})
    messages.append({"role": "user", "content": user_prompt})

    resp = await query_model(CHAIRMAN_MODEL, messages, timeout=300.0)
    if not resp:
        sys.exit("chairman synthesis failed")
    return resp.get("content", "") or ""


# --- Typst rendering ---------------------------------------------------------

TYPST_PREAMBLE = r"""#set document(title: "Jerusalem Honking — Focused Policy Digest")
#set page(
  paper: "a4",
  margin: (x: 2cm, y: 2.2cm),
  numbering: "1 / 1",
  header: context {
    if counter(page).get().first() > 1 [
      #set text(size: 8pt, fill: luma(110))
      Jerusalem Unnecessary Honking — Focused Policy Digest · 23 April 2026
      #h(1fr)
    ]
  },
)
#set text(font: ("Libertinus Serif", "Linux Libertine", "Nimbus Roman"), size: 10.5pt, lang: "en")
#set par(justify: true, leading: 0.62em)
#show heading.where(level: 1): set text(size: 18pt, weight: 700)
#show heading.where(level: 2): set text(size: 13.5pt, weight: 700, fill: rgb("#123a5e"))
#show heading.where(level: 3): set text(size: 11pt, weight: 700)
#show heading: it => { v(0.3em); it; v(0.15em) }
#show link: set text(fill: rgb("#1a6ab0"))

#align(center)[
  #text(size: 20pt, weight: 800)[Jerusalem Unnecessary Honking]
  #v(0.2em)
  #text(size: 13pt, weight: 600, fill: luma(60))[Focused Policy Digest]
  #v(0.4em)
  #text(size: 9pt, fill: luma(110))[Prepared by the LLM Council · 23 April 2026]
]
#v(1em)
#line(length: 100%, stroke: 0.5pt + luma(180))
#v(0.5em)
"""


_BRACE_RE = re.compile(r"\{([^{}]+\.md)\}")


def markdown_to_typst(md: str) -> str:
    """Small pragmatic Markdown → Typst converter for the digest shape we emit."""
    # Protect {file.md} source callouts so that our brace handling doesn't eat them.
    md = _BRACE_RE.sub(r"#raw(\"\1\")", md)

    lines = md.splitlines()
    out: list[str] = []
    in_list = False

    def esc_inline(s: str) -> str:
        # Typst-escape minimal chars, keep #raw() intact
        # (We already replaced {} for file callouts with #raw().)
        s = s.replace("\\", "\\\\")
        # Bold **x** → *x*, italic *x* unchanged; Typst supports both.
        s = re.sub(r"\*\*(.+?)\*\*", r"*\1*", s)
        s = re.sub(r"`([^`]+)`", r'#raw("\1")', s)
        return s

    for raw in lines:
        line = raw.rstrip()
        if not line.strip():
            if in_list:
                out.append("")
                in_list = False
            else:
                out.append("")
            continue
        m = re.match(r"^(#{1,4})\s+(.*)", line)
        if m:
            hashes = m.group(1)
            text = esc_inline(m.group(2))
            out.append(f"{hashes} {text}")
            in_list = False
            continue
        if re.match(r"^[-*]\s+", line):
            text = esc_inline(re.sub(r"^[-*]\s+", "", line))
            out.append(f"- {text}")
            in_list = True
            continue
        m = re.match(r"^(\d+)\.\s+(.*)", line)
        if m:
            text = esc_inline(m.group(2))
            out.append(f"+ {text}")
            in_list = True
            continue
        out.append(esc_inline(line))
        in_list = False

    return "\n".join(out)


def build_typst_doc(body_md: str, run_dir: Path) -> str:
    body_typst = markdown_to_typst(body_md)
    footer = f"""
#v(1em)
#line(length: 100%, stroke: 0.5pt + luma(180))
#v(0.4em)
#text(size: 8.5pt, fill: luma(110))[
  Source run: #raw("{run_dir.name}") · Chairman model: #raw("{CHAIRMAN_MODEL}") · Grounding corpus aggregated 23 April 2026
]
"""
    return TYPST_PREAMBLE + body_typst + footer


def render_pdf(typst_source: str, out_path: Path) -> None:
    typ_path = out_path.with_suffix(".typ")
    typ_path.write_text(typst_source)
    result = subprocess.run(
        ["typst", "compile", str(typ_path), str(out_path)],
        capture_output=True, text=True, timeout=60,
    )
    if result.returncode != 0:
        sys.exit(f"typst failed:\n{result.stderr}")


async def main() -> None:
    arg = sys.argv[1] if len(sys.argv) > 1 else None
    run_dir = pick_run_dir(arg)
    print(f"[render] run dir: {run_dir}")

    problem = (ROOT / "problem-statement.md").read_text()
    grounding = get_grounding_context()
    stage1, stage2, stage3, _meta = load_run(run_dir)

    print("[render] synthesising focused digest…")
    digest_md = await synthesize_focused_digest(problem, stage1, stage2, stage3, grounding)
    (run_dir / "focused-digest.md").write_text(digest_md)
    print(f"[render] focused digest markdown saved: {len(digest_md)} chars")

    print("[render] rendering Typst → PDF…")
    pdf_path = run_dir / "focused-digest.pdf"
    doc = build_typst_doc(digest_md, run_dir)
    render_pdf(doc, pdf_path)
    print(f"[render] PDF: {pdf_path}")


if __name__ == "__main__":
    asyncio.run(main())
