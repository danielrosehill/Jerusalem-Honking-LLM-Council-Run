"""Translate English policy docs into Hebrew for RTL typesetting.

Uses the configured chairman model (Claude Sonnet 4.6) via OpenRouter.
Chunks the input to stay within output token limits, preserves markdown
structure, and keeps technical terms / grounding-file tags intact.

Usage:
    uv run python translate_to_hebrew.py <path/to/english.md> <path/to/hebrew.md>
"""

from __future__ import annotations

import asyncio
import re
import sys
from pathlib import Path

from backend.config import CHAIRMAN_MODEL
from backend.openrouter import query_model

TRANSLATION_SYSTEM_PROMPT = (
    "You are a professional Hebrew translator specialising in municipal "
    "policy and communications. Translate the user's English markdown into "
    "natural, fluent Hebrew policy register (formal but accessible, as for "
    "a memo to a mayor's office). "
    "Rules: "
    "(1) Preserve all markdown structure exactly — heading levels, bullet "
    "markers, bold/italic, horizontal rules. "
    "(2) Do NOT translate: file-reference tags like {10-kolhair-jerusalem-"
    "quiet-cities.md}, inline code (backticks), URLs, email addresses, or "
    "organisation acronyms (MoEP, NOize, NIS, FOI, PPA, JGF). "
    "(3) Organisation and official-body names should use their standard "
    "Hebrew forms (e.g. Jerusalem Municipality → עיריית ירושלים; Ministry "
    "of Environmental Protection → המשרד להגנת הסביבה; Jerusalem Green "
    "Fund → קרן ירושלים ירוקה; Environmental Quality Committee → הוועדה "
    "לאיכות הסביבה; Israel Police → משטרת ישראל; Ministry of Interior → "
    "משרד הפנים; Privacy Protection Authority → הרשות להגנת הפרטיות; "
    "Knesset Constitution Committee → ועדת חוקה של הכנסת). "
    "(4) Keep numeric figures, currency, and dates in the original form "
    "(e.g. 250 NIS, 23 April 2026). "
    "(5) Direct quotations in Hebrew transliteration (e.g. 'Kan Garim Lo "
    "Tzofrim') should be restored to native Hebrew (כאן גרים לא צופרים). "
    "(6) Output ONLY the translated markdown. No preamble, no commentary, "
    "no wrapping code fence."
)


# --- Chunking ---------------------------------------------------------------

# Split on top-level (H1/H2) headings so each chunk is semantically whole
# and fits inside the output-token budget comfortably.
_SPLIT_RE = re.compile(r"(?m)^(#{1,2}\s+.+)$")


def split_by_major_headings(text: str, max_chars: int = 8000) -> list[str]:
    """Return chunks, each starting on a heading and at most max_chars long."""
    matches = list(_SPLIT_RE.finditer(text))
    if not matches:
        return [text]
    chunks: list[str] = []
    starts = [m.start() for m in matches] + [len(text)]
    # Preamble before first heading (if any)
    if starts[0] > 0:
        chunks.append(text[: starts[0]].rstrip())
    current = ""
    for i in range(len(matches)):
        block = text[starts[i] : starts[i + 1]]
        if current and len(current) + len(block) > max_chars:
            chunks.append(current.rstrip())
            current = block
        else:
            current += block
    if current:
        chunks.append(current.rstrip())
    return [c for c in chunks if c.strip()]


async def translate_chunk(chunk: str) -> str:
    resp = await query_model(
        CHAIRMAN_MODEL,
        messages=[
            {"role": "system", "content": TRANSLATION_SYSTEM_PROMPT},
            {"role": "user", "content": chunk},
        ],
        timeout=300.0,
    )
    if not resp:
        raise RuntimeError("Translation request failed")
    return (resp.get("content") or "").strip()


async def translate_markdown_file(src: Path, dst: Path) -> None:
    text = src.read_text()
    print(f"[translate] {src} → {dst}  ({len(text)} chars)")
    chunks = split_by_major_headings(text)
    print(f"[translate] split into {len(chunks)} chunks")
    translated: list[str] = []
    for i, chunk in enumerate(chunks, 1):
        print(f"[translate]   chunk {i}/{len(chunks)} ({len(chunk)} chars)…")
        t = await translate_chunk(chunk)
        translated.append(t)
    dst.parent.mkdir(parents=True, exist_ok=True)
    dst.write_text("\n\n".join(translated) + "\n")
    print(f"[translate] wrote {dst} ({dst.stat().st_size} bytes)")


async def main() -> None:
    if len(sys.argv) != 3:
        sys.exit("usage: translate_to_hebrew.py <src.md> <dst.he.md>")
    await translate_markdown_file(Path(sys.argv[1]), Path(sys.argv[2]))


if __name__ == "__main__":
    asyncio.run(main())
