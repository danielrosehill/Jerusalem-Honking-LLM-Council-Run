"""Render a Hebrew markdown document as an RTL PDF via Typst.

Usage:
    uv run python render_hebrew_pdf.py <src.he.md> <dst.pdf> [title]
"""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path


# --- Typst escaping (shared logic with render_full_report.py) ---------------

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
    "=": "\\=",
    "+": "\\+",
    "-": "\\-",
}


def _escape_typst(text: str) -> str:
    return "".join(_ESCAPE_MAP.get(c, c) for c in text)


_BOLD_RE = re.compile(r"\*\*(.+?)\*\*")
_ITAL_RE = re.compile(r"(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)")
_INLINE_CODE_RE = re.compile(r"`([^`]+)`")
_SRC_RE = re.compile(r"\{([0-9a-zA-Z\-]+\.md)\}")


def _inline(line: str) -> str:
    """Bold/italic/inline-code/grounding-tag aware inline converter."""
    # Inline code pass (preserves verbatim)
    parts: list[tuple[str, str]] = []
    idx = 0
    for m in _INLINE_CODE_RE.finditer(line):
        if m.start() > idx:
            parts.append(("prose", line[idx:m.start()]))
        code = m.group(1).replace("\"", "\\\"")
        parts.append(("raw", f'#raw("{code}")'))
        idx = m.end()
    if idx < len(line):
        parts.append(("prose", line[idx:]))

    out: list[str] = []
    for kind, seg in parts:
        if kind == "raw":
            out.append(seg)
            continue
        # Grounding callouts
        sub: list[str] = []
        j = 0
        for m in _SRC_RE.finditer(seg):
            if m.start() > j:
                sub.append(_transform_emphasis(seg[j:m.start()]))
            name = m.group(1)
            sub.append(f'#src("{name}")')
            j = m.end()
        if j < len(seg):
            sub.append(_transform_emphasis(seg[j:]))
        out.append("".join(sub))
    return "".join(out)


def _transform_emphasis(prose: str) -> str:
    """Apply bold then italic, escaping everything else safely."""
    segments: list[tuple[str, str]] = [("prose", prose)]

    def _expand(pat: re.Pattern[str], wrap_l: str, wrap_r: str) -> None:
        nonlocal segments
        new: list[tuple[str, str]] = []
        for kind, s in segments:
            if kind != "prose":
                new.append((kind, s))
                continue
            pos = 0
            for m in pat.finditer(s):
                if m.start() > pos:
                    new.append(("prose", s[pos:m.start()]))
                inner = _escape_typst(m.group(1))
                new.append(("typst", f"{wrap_l}{inner}{wrap_r}"))
                pos = m.end()
            if pos < len(s):
                new.append(("prose", s[pos:]))
        segments = new

    _expand(_BOLD_RE, "*", "*")
    _expand(_ITAL_RE, "_", "_")

    result: list[str] = []
    for kind, s in segments:
        result.append(s if kind == "typst" else _escape_typst(s))
    return "".join(result)


_HEADING_RE = re.compile(r"^(#{1,6})\s+(.*)$")
_BULLET_RE = re.compile(r"^\s*[-*]\s+(.*)$")
_ORDERED_RE = re.compile(r"^\s*\d+\.\s+(.*)$")


def markdown_to_typst_body(md: str) -> str:
    out: list[str] = []
    for line in md.splitlines():
        line = line.rstrip()
        if not line.strip():
            out.append("")
            continue
        m = _HEADING_RE.match(line)
        if m:
            level = len(m.group(1))
            out.append(f"{'=' * min(level + 1, 5)} {_inline(m.group(2))}")
            continue
        m = _BULLET_RE.match(line)
        if m:
            out.append(f"- {_inline(m.group(1))}")
            continue
        m = _ORDERED_RE.match(line)
        if m:
            out.append(f"+ {_inline(m.group(1))}")
            continue
        if re.match(r"^[-*_]{3,}\s*$", line):
            out.append("#line(length: 100%, stroke: 0.5pt + luma(200))")
            continue
        out.append(_inline(line))
    return "\n".join(out)


PREAMBLE_TEMPLATE = r"""#set document(title: "__TITLE__", author: "LLM Council")
#set page(
  paper: "a4",
  margin: (x: 2cm, y: 2.2cm),
  numbering: "1 / 1",
  footer: context [
    #set text(size: 8pt, fill: luma(110), dir: rtl)
    __FOOTER__
    #h(1fr)
    #counter(page).display("1 / 1", both: true)
  ],
)
// Hebrew-first font stack. David CLM / Frank Ruehl CLM render Hebrew well;
// Libertinus Serif picks up the Latin characters (numbers, acronyms).
#set text(
  font: ("Frank Ruehl CLM", "David CLM", "Libertinus Serif", "Noto Serif", "DejaVu Serif"),
  size: 11pt,
  lang: "he",
  dir: rtl,
)
#set par(justify: true, leading: 0.72em)
#show heading.where(level: 1): it => {
  pagebreak(weak: true)
  v(0.8em)
  text(size: 22pt, weight: 800, fill: rgb("#123a5e"), it.body)
  v(0.2em)
  line(length: 40%, stroke: 1pt + rgb("#123a5e"))
  v(0.6em)
}
#show heading.where(level: 2): set text(size: 15pt, weight: 700, fill: rgb("#123a5e"))
#show heading.where(level: 3): set text(size: 12pt, weight: 700)
#show heading.where(level: 4): set text(size: 11pt, weight: 700, fill: luma(60))
#show heading.where(level: 5): set text(size: 10.5pt, weight: 700, style: "italic")
#show heading: it => { v(0.55em); it; v(0.25em) }

#let src(name) = box(
  inset: (x: 3pt, y: 0pt),
  outset: (y: 1pt),
  fill: luma(235),
  radius: 2pt,
  text(
    size: 7.8pt,
    font: ("DejaVu Sans Mono", "Fira Mono", "monospace"),
    fill: luma(60),
    dir: ltr,
    name,
  ),
)

"""


def build_document(md_text: str, title: str, footer: str) -> str:
    preamble = (
        PREAMBLE_TEMPLATE
        .replace("__TITLE__", title.replace("\"", "\\\""))
        .replace("__FOOTER__", _escape_typst(footer))
    )
    body = markdown_to_typst_body(md_text)
    return preamble + body + "\n"


def compile_typst(typ: Path, pdf: Path) -> None:
    r = subprocess.run(
        ["typst", "compile", str(typ), str(pdf)],
        capture_output=True, text=True, timeout=120,
    )
    if r.returncode != 0:
        sys.stderr.write(r.stderr)
        sys.exit(f"typst failed for {typ}")


def main() -> None:
    if len(sys.argv) < 3:
        sys.exit("usage: render_hebrew_pdf.py <src.he.md> <dst.pdf> [title]")
    src = Path(sys.argv[1])
    dst = Path(sys.argv[2])
    title = sys.argv[3] if len(sys.argv) > 3 else "מסמך"
    footer = "מועצת LLM · ירושלים: צפירות מיותרות · 23 באפריל 2026"

    typ = dst.with_suffix(".typ")
    doc = build_document(src.read_text(), title, footer)
    typ.write_text(doc)
    compile_typst(typ, dst)
    print(f"[hebrew-pdf] {dst} ({dst.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
