"""Render the Full Experiment Report.

Reads stage1/2/3 JSON from a run directory and emits a book-style Typst
document including every raw councillor answer, every peer review, the
aggregate ranking, and the Chairman's synthesis — with proper page
breaking between sections.

Usage:
    uv run python render_full_report.py                    # newest run
    uv run python render_full_report.py run-20260423T150817
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

from backend.config import COUNCIL_QUESTIONS, COUNCIL_PERSONALITIES

ROOT = Path(__file__).resolve().parent
RUN_ROOT = ROOT / "data"
GROUNDING_DIR = ROOT / "grounding"
INGEST_DATE = "23 April 2026"


# ---------------------------------------------------------------------------
# Typst escaping
# ---------------------------------------------------------------------------

# Special chars that *can* be escaped in Typst markup — backslash first.
_ESCAPE_MAP = {
    "\\": "\\\\",
    "#": "\\#",
    "$": "\\$",
    "@": "\\@",
    "<": "\\<",
    ">": "\\>",
    "*": "\\*",
    "_": "\\_",
    "[": "\\[",
    "]": "\\]",
    "{": "\\{",
    "}": "\\}",
    "~": "\\~",
    "`": "\\`",
    "=": "\\=",  # only matters at line start; escaping globally is harmless
    "+": "\\+",
    "-": "\\-",
}


def _escape_typst(text: str) -> str:
    """Escape every Typst-special character so we can safely embed raw prose."""
    out = []
    for ch in text:
        out.append(_ESCAPE_MAP.get(ch, ch))
    return "".join(out)


# ---------------------------------------------------------------------------
# Markdown → Typst (only the shapes emitted by the council outputs)
# ---------------------------------------------------------------------------

_BOLD_RE = re.compile(r"\*\*(.+?)\*\*")
_ITAL_RE = re.compile(r"(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)")
_INLINE_CODE_RE = re.compile(r"`([^`]+)`")
_SRC_RE = re.compile(r"\{([0-9a-zA-Z\-]+\.md)\}")


def _inline_markdown_to_typst(line: str) -> str:
    """Convert inline markdown emphasis to Typst, keeping prose escapes safe."""
    parts: list[str] = []
    i = 0
    for m in _INLINE_CODE_RE.finditer(line):
        if m.start() > i:
            parts.append(_transform_inline(line[i:m.start()]))
        code = m.group(1).replace("\"", "\\\"")
        parts.append(f'#raw("{code}")')
        i = m.end()
    if i < len(line):
        parts.append(_transform_inline(line[i:]))
    return "".join(parts)


def _transform_inline(segment: str) -> str:
    """Handle bold, italic, grounding {file.md} callouts and escapes on prose."""
    # Grounding callouts first: convert {file.md} → #src("file.md"). Do this
    # before general escaping so the braces don't get escaped away.
    tokens: list[tuple[str, str]] = []  # (kind, text)
    i = 0
    for m in _SRC_RE.finditer(segment):
        if m.start() > i:
            tokens.append(("prose", segment[i:m.start()]))
        tokens.append(("src", m.group(1)))
        i = m.end()
    if i < len(segment):
        tokens.append(("prose", segment[i:]))

    out: list[str] = []
    for kind, text in tokens:
        if kind == "src":
            safe = text.replace("\"", "\\\"")
            out.append(f'#src("{safe}")')
            continue
        # Bold / italic handled inside prose segments, then escape the rest.
        buf = text

        def _bold_sub(m: re.Match[str]) -> str:
            inner = _escape_typst(m.group(1))
            return f"*{inner}*"

        def _ital_sub(m: re.Match[str]) -> str:
            inner = _escape_typst(m.group(1))
            return f"_{inner}_"

        # Apply bold first (** pairs), then italic (single *). To preserve the
        # emphasis markers while everything else gets escaped, we do the
        # substitutions in passes, emitting already-Typst strings which must
        # NOT be re-escaped.
        segments: list[tuple[str, str]] = [("prose", buf)]

        # Bold pass
        new_segments: list[tuple[str, str]] = []
        for kind2, seg in segments:
            if kind2 != "prose":
                new_segments.append((kind2, seg))
                continue
            idx = 0
            for m in _BOLD_RE.finditer(seg):
                if m.start() > idx:
                    new_segments.append(("prose", seg[idx:m.start()]))
                new_segments.append(("typst", _bold_sub(m)))
                idx = m.end()
            if idx < len(seg):
                new_segments.append(("prose", seg[idx:]))
        segments = new_segments

        # Italic pass
        new_segments = []
        for kind2, seg in segments:
            if kind2 != "prose":
                new_segments.append((kind2, seg))
                continue
            idx = 0
            for m in _ITAL_RE.finditer(seg):
                if m.start() > idx:
                    new_segments.append(("prose", seg[idx:m.start()]))
                new_segments.append(("typst", _ital_sub(m)))
                idx = m.end()
            if idx < len(seg):
                new_segments.append(("prose", seg[idx:]))
        segments = new_segments

        for kind2, seg in segments:
            if kind2 == "typst":
                out.append(seg)
            else:
                out.append(_escape_typst(seg))

    return "".join(out)


_HEADING_RE = re.compile(r"^(#{1,6})\s+(.*)$")
_BULLET_RE = re.compile(r"^\s*[-*]\s+(.*)$")
_ORDERED_RE = re.compile(r"^\s*\d+\.\s+(.*)$")


def plain_paragraphs_to_typst(text: str) -> str:
    """Aggressive, robust fallback renderer.

    Replaces literal ``\\n`` escape sequences with real newlines, splits on
    blank lines into paragraphs, escapes every Typst-special char, and emits
    them as clean Typst prose with no markdown parsing at all. This is the
    safe path for model-emitted JSON strings that may contain awkward
    escape sequences or unbalanced markdown markers.
    """
    # Normalise literal \n\n (two-char escapes) to real newlines.
    normalised = text.replace("\\n", "\n").replace("\\t", "\t")
    # Split into paragraphs on blank lines
    paragraphs = re.split(r"\n\s*\n", normalised)
    out: list[str] = []
    for p in paragraphs:
        p = p.strip()
        if not p:
            continue
        # Handle the grounding {file.md} callouts inside otherwise-plain prose.
        rendered_parts: list[str] = []
        idx = 0
        for m in _SRC_RE.finditer(p):
            if m.start() > idx:
                rendered_parts.append(_escape_typst(p[idx:m.start()]))
            rendered_parts.append(f'#src("{m.group(1)}")')
            idx = m.end()
        if idx < len(p):
            rendered_parts.append(_escape_typst(p[idx:]))
        out.append("".join(rendered_parts))
    return "\n\n".join(out)


def markdown_block_to_typst(md: str) -> str:
    """Convert a full markdown block — paragraphs, headings, bullets — to Typst."""
    lines = md.splitlines()
    out: list[str] = []
    for raw in lines:
        line = raw.rstrip()
        if not line.strip():
            out.append("")
            continue
        m = _HEADING_RE.match(line)
        if m:
            level = len(m.group(1))
            content = _inline_markdown_to_typst(m.group(2))
            # Cap heading levels at 4 so Part-structure remains clean.
            out.append(f"{'=' * min(level + 1, 5)} {content}")
            continue
        m = _BULLET_RE.match(line)
        if m:
            content = _inline_markdown_to_typst(m.group(1))
            out.append(f"- {content}")
            continue
        m = _ORDERED_RE.match(line)
        if m:
            content = _inline_markdown_to_typst(m.group(1))
            out.append(f"+ {content}")
            continue
        # Horizontal rules
        if re.match(r"^[-*_]{3,}\s*$", line):
            out.append("#line(length: 100%, stroke: 0.5pt + luma(200))")
            continue
        out.append(_inline_markdown_to_typst(line))
    return "\n".join(out)


# ---------------------------------------------------------------------------
# Run loading
# ---------------------------------------------------------------------------


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


# ---------------------------------------------------------------------------
# Typst document assembly
# ---------------------------------------------------------------------------


PREAMBLE = r"""#set document(title: "Jerusalem Honking — Full Experiment Report", author: "LLM Council")
#set page(
  paper: "a4",
  margin: (x: 2cm, y: 2.2cm),
  numbering: "1 / 1",
  footer: context [
    #set text(size: 8pt, fill: luma(110))
    Jerusalem Unnecessary Honking · Full Experiment Report · 23 April 2026
    #h(1fr)
    #counter(page).display("1 / 1", both: true)
  ],
)
// Multi-script font fallback — Libertinus Serif covers Latin, Frank Ruehl CLM
// covers Hebrew, DejaVu Serif picks up anything else (incl. punctuation).
#set text(
  font: ("Libertinus Serif", "Frank Ruehl CLM", "IBM Plex Sans Hebrew", "Noto Serif", "DejaVu Serif"),
  size: 10.5pt,
  lang: "en",
)
#set par(justify: true, leading: 0.62em)
#set heading(numbering: none)
#show heading.where(level: 1): it => {
  pagebreak(weak: true)
  v(0.8em)
  text(size: 22pt, weight: 800, fill: rgb("#123a5e"), it.body)
  v(0.2em)
  line(length: 40%, stroke: 1pt + rgb("#123a5e"))
  v(0.8em)
}
#show heading.where(level: 2): set text(size: 15pt, weight: 700, fill: rgb("#123a5e"))
#show heading.where(level: 3): set text(size: 12pt, weight: 700)
#show heading.where(level: 4): set text(size: 11pt, weight: 700, fill: luma(60))
#show heading.where(level: 5): set text(size: 10.5pt, weight: 700, style: "italic")
#show heading: it => { v(0.6em); it; v(0.25em) }

// Grounding file callout — subtle inline monospace tag.
#let src(name) = box(
  inset: (x: 3pt, y: 0pt),
  outset: (y: 1pt),
  fill: luma(235),
  radius: 2pt,
  text(
    size: 7.8pt,
    font: ("DejaVu Sans Mono", "Fira Mono", "monospace"),
    fill: luma(60),
    name,
  ),
)

// Cover page
#align(center + horizon)[
  #text(size: 11pt, fill: luma(100), weight: 600)[LLM COUNCIL · POLICY IDEATION]
  #v(0.4em)
  #text(size: 26pt, weight: 800)[Jerusalem Unnecessary Honking]
  #v(0.3em)
  #text(size: 16pt, weight: 600, fill: luma(65))[Full Experiment Report]
  #v(1.8em)
  #text(size: 10.5pt, fill: luma(90))[
    Prepared for the Jerusalem Municipality Working Group \
    and the Jerusalem Green Fund \
    Reference date · 23 April 2026
  ]
  #v(3em)
  #text(size: 9.5pt, fill: luma(110))[
    This report includes the raw responses from every council member, \
    the full peer-review stage, aggregate rankings, the Chairman's synthesis, \
    and the complete text of every grounding source.
  ]
]
#pagebreak()
"""


FOOTER_TPL = r"""
#v(1.2em)
#line(length: 100%, stroke: 0.5pt + luma(180))
#v(0.4em)
#text(size: 8.5pt, fill: luma(110))[
  Source run: #raw("{run_id}") · Grounding corpus aggregated 23 April 2026. \
  Inline grey tags such as #src("10-kolhair-jerusalem-quiet-cities.md") reference files in the repo's `grounding/` directory.
]
"""


_META_BULLET_RE = re.compile(r"^\s*-\s+\*\*([^*]+?):\*\*\s*(.*)$")


def parse_grounding_file(path: Path) -> dict:
    """Parse a grounding/*.md file into title, metadata dict, and body markdown."""
    text = path.read_text()
    lines = text.splitlines()

    title = path.stem
    meta: dict[str, str] = {}
    body_lines: list[str] = []

    state = "preamble"  # preamble → metadata → body
    for line in lines:
        if state == "preamble":
            m = re.match(r"^#\s+(.*)$", line)
            if m:
                title = m.group(1).strip()
                state = "metadata"
                continue
            continue
        if state == "metadata":
            bm = _META_BULLET_RE.match(line)
            if bm:
                key = bm.group(1).strip().lower()
                val = bm.group(2).strip()
                meta[key] = val
                continue
            if line.strip().startswith("---"):
                state = "body"
                continue
            # Non-bullet, non-sep line — treat metadata as done, start body.
            if line.strip():
                state = "body"
                body_lines.append(line)
            continue
        body_lines.append(line)

    return {
        "title": title,
        "meta": meta,
        "body": "\n".join(body_lines).strip(),
        "filename": path.name,
    }


def load_grounding_corpus() -> list[dict]:
    if not GROUNDING_DIR.is_dir():
        return []
    files = sorted(GROUNDING_DIR.glob("*.md"))
    # Skip README.md from the appendix — it's an index, not a primary source.
    return [
        parse_grounding_file(p)
        for p in files
        if p.name.lower() != "readme.md"
    ]


def _find_personality(model_id: str) -> dict | None:
    for p in COUNCIL_PERSONALITIES:
        if p["id"] == model_id:
            return p
    return None


def build_typst_document(
    run_dir: Path,
    stage1: list[dict],
    stage2: list[dict],
    stage3: dict,
    metadata: dict,
) -> str:
    parts: list[str] = [PREAMBLE]

    # --- TOC -------------------------------------------------------------
    parts.append(r"""
#align(left)[
  #text(size: 16pt, weight: 700, fill: rgb("#123a5e"))[Contents]
]
#v(0.6em)
#outline(depth: 2, indent: auto)
""")

    # --- Part I: Methodology --------------------------------------------
    parts.append("= Part I · Methodology\n\n")
    parts.append(markdown_block_to_typst(_methodology_markdown(run_dir, metadata)))

    # --- Part II: Chairman's long-form report ---------------------------
    parts.append("\n\n= Part II · Chairman's Synthesis\n\n")
    chairman = stage3.get("response", "") or ""
    parts.append(markdown_block_to_typst(chairman))

    # --- Part III: Raw councillor answers -------------------------------
    parts.append("\n\n= Part III · Raw Councillor Responses\n\n")
    parts.append(markdown_block_to_typst(
        "Each council member was asked the same six questions and returned a "
        "JSON-structured response. This section reproduces every councillor's "
        "raw answer to every question, in order, so the reader can audit the "
        "Chairman's synthesis against source material."
    ))

    for i, entry in enumerate(stage1):
        lens_id = entry.get("model") or ""
        personality = _find_personality(lens_id)
        model_used = personality.get("model") if personality else ""
        name = entry.get("name") or lens_id
        answers = entry.get("answers") or {}

        parts.append(f"\n\n== {_escape_typst(name)}\n\n")
        if model_used:
            parts.append(
                f"#text(size: 9.5pt, fill: luma(100))[Model: #raw(\"{model_used}\")]\n\n"
            )
        if not answers:
            parts.append(
                "#text(fill: rgb(\"#a04040\"))[Note: structured JSON output "
                "parse failed for this councillor; raw response follows.]\n\n"
            )
            parts.append(plain_paragraphs_to_typst(entry.get("response") or ""))
            continue
        for q in COUNCIL_QUESTIONS:
            qid = q["id"]
            ans = (answers.get(qid) or "").strip()
            parts.append(
                f"\n\n=== {qid.upper()} — {_escape_typst(q['label'])}\n\n"
            )
            parts.append(
                f"#text(size: 9.5pt, fill: luma(100), style: \"italic\")["
                f"{_escape_typst(q['question'])}]\n\n"
            )
            if ans:
                parts.append(plain_paragraphs_to_typst(ans))
            else:
                parts.append("_(no answer)_")

    # --- Part IV: Peer reviews ------------------------------------------
    parts.append("\n\n= Part IV · Stage 2 Peer Reviews\n\n")
    parts.append(markdown_block_to_typst(
        "Each council member was shown every Stage 1 response *anonymised* as "
        "Response A, B, C, … and asked to evaluate and rank them. The aggregate "
        "ranking derived from this stage appears in the table below."
    ))

    label_to_model = metadata.get("label_to_model") or {}
    if label_to_model:
        parts.append("\n\n=== Anonymised label → councillor map\n\n")
        parts.append("#table(\n  columns: 2,\n  [*Label*], [*Councillor*],\n")
        for label, who in label_to_model.items():
            parts.append(
                f"  [#raw(\"{label}\")], [{_escape_typst(who)}],\n"
            )
        parts.append(")\n\n")

    aggregate = metadata.get("aggregate_rankings") or []
    if aggregate:
        parts.append("=== Aggregate rankings\n\n")
        parts.append(
            "#table(\n  columns: (auto, 1fr, auto, auto),\n"
            "  [*Rank*], [*Council Member*], [*Avg. position*], [*Votes*],\n"
        )
        for idx, row in enumerate(aggregate, start=1):
            parts.append(
                f"  [{idx}], [{_escape_typst(row.get('model',''))}],"
                f" [{row.get('average_rank','')}], [{row.get('rankings_count','')}],\n"
            )
        parts.append(")\n\n")

    for entry in stage2:
        name = entry.get("name") or entry.get("model") or ""
        ranking_text = entry.get("ranking") or ""
        parts.append(f"\n\n== {_escape_typst(name)} · Peer Review\n\n")
        if ranking_text:
            parts.append(plain_paragraphs_to_typst(ranking_text))

    # --- Part V: Grounding corpus (full texts) --------------------------
    corpus = load_grounding_corpus()
    if corpus:
        parts.append("\n\n= Part V · Grounding Corpus (Full Source Texts)\n\n")
        parts.append(markdown_block_to_typst(
            f"The council was grounded in the following primary-source corpus, "
            f"aggregated on {INGEST_DATE}. The full text of each source — "
            "Hebrew original and English translation where applicable — is "
            "reproduced below together with its original URL and publication "
            "metadata, so that this report is self-contained and independently "
            "auditable."
        ))

        for src in corpus:
            parts.append(f"\n\n== {_escape_typst(src['title'])}\n\n")
            meta = src["meta"]
            # Metadata box: source, URL, author, published, ingest date
            parts.append("#block(\n  fill: luma(243),\n  inset: 10pt,\n  radius: 3pt,\n  width: 100%,\n  [\n")
            parts.append("  #set text(size: 9.5pt)\n")
            for label in ("Source", "Author", "Published", "Issuing Authority", "Scope", "Type", "Unit number", "Format", "Length", "Group slogan (Hebrew)", "Alternative name visible in metadata", "Note"):
                key = label.lower()
                if key in meta:
                    parts.append(
                        f"  *{_escape_typst(label)}:* "
                        f"{_inline_markdown_to_typst(meta[key])} \\\n"
                    )
            url = meta.get("url")
            if url:
                # Typst link() requires a string URL; escape backslashes + quotes.
                url_safe = url.replace("\\", "\\\\").replace("\"", "\\\"")
                parts.append(
                    f"  *URL:* #link(\"{url_safe}\")[#raw(\"{url_safe}\")] \\\n"
                )
            parts.append(f"  *Date of ingest:* {INGEST_DATE}\n")
            parts.append("  ]\n)\n\n")
            # Body
            if src["body"]:
                parts.append(markdown_block_to_typst(src["body"]))

    # --- Footer ----------------------------------------------------------
    parts.append(FOOTER_TPL.format(run_id=run_dir.name))

    return "".join(parts)


def _methodology_markdown(run_dir: Path, metadata: dict) -> str:
    lenses_lines = []
    for p in COUNCIL_PERSONALITIES:
        lenses_lines.append(
            f"- **{p['name']}** — model: `{p.get('model','(default)')}`"
        )
    lenses_block = "\n".join(lenses_lines)
    return f"""
## Summary

This report is the complete experimental record for the 23 April 2026 LLM Council run on the Jerusalem unnecessary car-horn policy challenge. It reproduces the raw output of every council member and every peer review in addition to the Chairman's synthesis, so the reader can independently audit the reasoning chain.

## Orchestration

The council is a three-stage pipeline:

1. **Stage 1 — Councillor Perspectives.** Six specialist policy lenses (system-prompt-defined) each receive the problem statement, the full grounding corpus, and the six council questions. Each returns a JSON-structured response with one answer per question.
2. **Stage 2 — Peer Review.** Every council member sees every other member's Stage 1 response *anonymised* (Response A, B, C, …) and produces a ranked evaluation.
3. **Stage 3 — Chairman Synthesis.** The Chairman (same base model as the Urban Planner in this run) receives the grounding corpus, all Stage 1 responses, and all Stage 2 reviews, and produces a structured policy-ideation report.

## Model roster

The council is deliberately multi-provider to minimise single-lab bias:

{lenses_block}

All model calls are routed through OpenRouter. Structured JSON output is enforced via `response_format: json_schema` at Stage 1.

## Grounding

A curated corpus of 13 primary Hebrew-language sources — news coverage, official municipal and ministry statements, the Ministry of Education curriculum, and campaign artefacts — was aggregated on 23 April 2026 and injected into every councillor's context window at Stage 1 and into the Chairman's context at Stage 3. The corpus is committed to the repository under `grounding/` with an index at `grounding/README.md` and a synthesis overview at `grounding.md`.

## Problem statement

The canonical problem statement for this run — an author-narrated account of the Jerusalem unnecessary-honking issue by Daniel Rosehill, dated 23 April 2026 — is committed to the repository as `problem-statement.md`.

## Council questions

The six questions posed to each councillor are listed verbatim in `council-questions.md`. Councillors were required to return a single JSON object with one answer per question.

## Reproducibility

The exact JSON outputs of Stage 1, Stage 2, and Stage 3 for this run — including the anonymised-label map and aggregate ranking — are committed alongside this PDF in `data/{run_dir.name}/`. A re-run against the same grounding corpus will approximate but not exactly reproduce these outputs due to normal LLM temperature / sampling variance.
"""


def compile_typst(typst_path: Path, pdf_path: Path) -> None:
    result = subprocess.run(
        ["typst", "compile", str(typst_path), str(pdf_path)],
        capture_output=True, text=True, timeout=120,
    )
    if result.returncode != 0:
        sys.stderr.write(result.stderr)
        sys.exit(f"typst compile failed for {typst_path}")


def main() -> None:
    arg = sys.argv[1] if len(sys.argv) > 1 else None
    run_dir = pick_run_dir(arg)
    print(f"[render-full] run dir: {run_dir}")

    stage1, stage2, stage3, metadata = load_run(run_dir)

    typst_doc = build_typst_document(run_dir, stage1, stage2, stage3, metadata)
    typst_path = run_dir / "full-experiment-report.typ"
    pdf_path = run_dir / "full-experiment-report.pdf"

    typst_path.write_text(typst_doc)
    print(f"[render-full] typst: {typst_path} ({len(typst_doc)} chars)")

    compile_typst(typst_path, pdf_path)
    print(f"[render-full] pdf: {pdf_path}")


if __name__ == "__main__":
    main()
