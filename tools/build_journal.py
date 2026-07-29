#!/usr/bin/env python3
"""Render the lab journal and findings onto the site.

WHY THESE PAGES AND NOT OTHERS
------------------------------
The most credible material this programme has is the record of it being wrong:
the void run, the near miss where a single `raise` was all that stood between
the repository and a fabricated result, the retraction of its own diagnosis.
Until now that lived only in the repository, reachable by knowing a filename.

A page claiming "three of our own claims are refuted" and giving no way to read
them is asking to be taken on trust — from a programme whose whole subject is
that trust and evidence come apart.

Self-contained markdown → HTML, no dependencies, covering exactly the subset
the journal uses. Deliberately small: a general markdown library would be a
larger surface than the documents it renders.

    python3 tools/build_journal.py
"""

from __future__ import annotations

import html
import os
import re
from typing import List, Tuple

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOCS = os.path.join(ROOT, "docs")
OUT = os.path.join(DOCS, "journal")

SOURCES: List[Tuple[str, str, str]] = [
    # (slug, source path, kind)
    ("founding", "journal/2026-07-28-founding.md", "journal"),
    ("first-live-run-void", "journal/2026-07-28-first-live-run-void.md", "journal"),
    ("e-001-findings", "experiments/E-001-fluency-cost/FINDINGS.md", "findings"),
]

REPO = "https://github.com/vyakymenko/noophorics/blob/main/"


# --------------------------------------------------------------------------
# markdown


def _inline(text: str) -> str:
    text = html.escape(text, quote=False)
    # code first, so its contents are not further transformed
    holds: List[str] = []
    def hold(m):
        holds.append('<code>%s</code>' % m.group(1))
        return "\x00%d\x00" % (len(holds) - 1)
    text = re.sub(r"`([^`]+)`", hold, text)
    text = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", _link, text)
    text = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"(?<!\*)\*([^*\n]+)\*(?!\*)", r"<em>\1</em>", text)
    text = re.sub(r"~~([^~]+)~~", r"<s>\1</s>", text)
    return re.sub(r"\x00(\d+)\x00", lambda m: holds[int(m.group(1))], text)


def _link(m) -> str:
    label, href = m.group(1), m.group(2)
    if href.startswith("http"):
        pass
    elif href.startswith("#"):
        pass
    else:  # relative repo path -> point at the repository
        href = REPO + os.path.normpath(
            os.path.join("journal", href)
        ).replace("\\", "/").lstrip("./")
    return '<a href="%s">%s</a>' % (html.escape(href, quote=True), label)


def markdown(src: str) -> str:
    out: List[str] = []
    lines = src.split("\n")
    i, n = 0, len(lines)
    while i < n:
        line = lines[i]

        if line.startswith("```"):
            body = []
            i += 1
            while i < n and not lines[i].startswith("```"):
                body.append(html.escape(lines[i]))
                i += 1
            out.append('<pre><code>%s</code></pre>' % "\n".join(body))
            i += 1
            continue

        if re.match(r"^\s*$", line):
            i += 1
            continue

        if re.match(r"^---+\s*$", line):
            out.append("<hr>")
            i += 1
            continue

        m = re.match(r"^(#{1,4}) (.*)$", line)
        if m:
            # The document's own "# Title" is lifted out and rendered as the
            # page h1, so "##" is already the first in-body level and must map
            # to h2. Shifting it down produced an h1 -> h3 jump, the same
            # defect the canonical page's audit caught in its footer.
            level = min(max(len(m.group(1)), 2), 6)
            out.append("<h%d>%s</h%d>" % (level, _inline(m.group(2)), level))
            i += 1
            continue

        if line.startswith("|"):
            rows = []
            while i < n and lines[i].startswith("|"):
                rows.append(lines[i])
                i += 1
            out.append(_table(rows))
            continue

        if line.startswith("> "):
            body = []
            while i < n and lines[i].startswith(">"):
                body.append(lines[i].lstrip(">").strip())
                i += 1
            out.append("<blockquote><p>%s</p></blockquote>" % _inline(" ".join(body)))
            continue

        if re.match(r"^\s*[-*] ", line) or re.match(r"^\s*\d+\. ", line):
            ordered = bool(re.match(r"^\s*\d+\. ", line))
            items: List[str] = []
            while i < n and (re.match(r"^\s*[-*] ", lines[i])
                             or re.match(r"^\s*\d+\. ", lines[i])
                             or (items and lines[i].startswith("  ") and lines[i].strip())):
                if re.match(r"^\s*(?:[-*]|\d+\.) ", lines[i]):
                    items.append(re.sub(r"^\s*(?:[-*]|\d+\.) ", "", lines[i]))
                else:
                    items[-1] += " " + lines[i].strip()
                i += 1
            tag = "ol" if ordered else "ul"
            out.append("<%s>%s</%s>" % (
                tag, "".join("<li>%s</li>" % _inline(x) for x in items), tag))
            continue

        para = [line]
        i += 1
        while i < n and lines[i].strip() and not re.match(
                r"^(#{1,4} |[-*] |\d+\. |> |\||```|---+\s*$)", lines[i]):
            para.append(lines[i])
            i += 1
        out.append("<p>%s</p>" % _inline(" ".join(para)))

    return "\n".join(out)


def _table(rows: List[str]) -> str:
    def cells(r):
        return [c.strip() for c in r.strip().strip("|").split("|")]
    head = cells(rows[0])
    body = [cells(r) for r in rows[2:]] if len(rows) > 2 else []
    thead = "".join("<th>%s</th>" % _inline(c) for c in head)
    tbody = "".join(
        "<tr>%s</tr>" % "".join("<td>%s</td>" % _inline(c) for c in r) for r in body
    )
    return ('<div class="scroll"><table><thead><tr>%s</tr></thead>'
            '<tbody>%s</tbody></table></div>' % (thead, tbody))


# --------------------------------------------------------------------------


def page_shell(title: str, body: str, description: str, canonical: str,
               style: str) -> str:
    return """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>%s — Noophorics</title>
<meta name="description" content="%s">
<meta name="color-scheme" content="light dark">
<link rel="canonical" href="%s">
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<meta property="og:title" content="%s — Noophorics">
<meta property="og:type" content="article">
<meta property="og:url" content="%s">
<meta property="og:image" content="https://noophorics.org/og.png">
%s
<style>
main{max-width:40rem;margin:0 auto;padding:clamp(2rem,6vw,4.5rem) 1.25rem 5rem}
.jn{font-family:ui-monospace,Menlo,monospace;font-size:.82rem;letter-spacing:.08em;
  text-transform:uppercase;color:var(--soft);margin:0 0 .8rem}
main h1{font-size:clamp(1.9rem,1.4rem + 2.2vw,2.7rem);font-weight:400;
  margin:0 0 2rem;line-height:1.15;letter-spacing:-.01em}
main h2{font-size:1.35rem;font-weight:400;margin:2.6rem 0 .9rem;
  padding-bottom:.4rem;border-bottom:1px solid var(--rule)}
main h3{font-size:1.1rem;font-weight:600;margin:2rem 0 .7rem}
main p{margin:0 0 1.25rem}
main ul,main ol{margin:0 0 1.25rem;padding-inline-start:1.3rem;list-style:revert}
main li{margin-bottom:.5rem}
main blockquote{margin:1.6rem 0;padding-inline-start:1.1rem;
  border-inline-start:3px solid var(--accent);color:var(--ink)}
main blockquote p{margin:0}
main pre{background:var(--code-bg,rgba(128,128,128,.1));padding:1rem 1.1rem;
  overflow-x:auto;font-size:.86rem;line-height:1.5;margin:0 0 1.4rem}
main code{font-family:ui-monospace,Menlo,monospace;font-size:.88em}
main table{border-collapse:collapse;width:100%%;font-size:.92rem;margin:0 0 1.4rem}
main th,main td{text-align:start;padding:.5rem .8rem;border-bottom:1px solid var(--rule);
  vertical-align:top}
main th{font-family:ui-monospace,Menlo,monospace;font-size:.78rem;
  letter-spacing:.06em;text-transform:uppercase;color:var(--soft);font-weight:400}
main hr{border:0;border-top:1px solid var(--rule);margin:2.4rem 0}
.back{display:block;margin-top:3.5rem;padding-top:1.4rem;
  border-top:1px solid var(--rule);font-size:.92rem;color:var(--soft)}
</style>
</head>
<body>
<a class="skip" href="#content">Skip to content</a>
<main id="content">
%s
<p class="back"><a href="/journal/">All journal entries</a> · <a href="/">Noophorics</a> · <a href="https://github.com/vyakymenko/noophorics">Repository</a></p>
</main>
</body>
</html>
""" % (title, html.escape(description, quote=True), canonical, title, canonical,
       style, body)


def extract_style(canonical_html: str) -> str:
    """Reuse the canonical page's variables and base rules verbatim."""
    m = re.search(r"<style>.*?</style>", canonical_html, re.S)
    return m.group(0) if m else "<style></style>"


def build() -> int:
    with open(os.path.join(DOCS, "index.html"), "r", encoding="utf-8") as fh:
        style = extract_style(fh.read())
    os.makedirs(OUT, exist_ok=True)

    entries = []
    for slug, path, kind in SOURCES:
        with open(os.path.join(ROOT, path), "r", encoding="utf-8") as fh:
            src = fh.read()
        title = re.search(r"^#\s+(.*)$", src, re.M).group(1).strip()
        rest = src[src.index("\n", src.index("# ")) :]
        first_para = next(
            (ln.strip() for ln in rest.split("\n")
             if ln.strip() and not ln.startswith(("#", ">", "-", "*", "|", "`"))),
            "",
        )
        summary = re.sub(r"[*`\[\]]|\(https?://[^)]+\)", "", first_para)[:180]
        body = ('<p class="jn">%s · %s</p>\n<h1>%s</h1>\n%s'
                % (kind, slug.replace("-", " "), html.escape(title), markdown(rest)))
        out_dir = os.path.join(OUT, slug)
        os.makedirs(out_dir, exist_ok=True)
        url = "https://noophorics.org/journal/%s/" % slug
        with open(os.path.join(out_dir, "index.html"), "w", encoding="utf-8") as fh:
            fh.write(page_shell(title, body, summary, url, style))
        entries.append((slug, title, summary, kind, path))

    index_body = (
        '<p class="jn">Lab notebook</p>\n<h1>The record of being wrong</h1>\n'
        "<p>Dated, append-only, and never edited after the fact except for typos. "
        "The entries below are the programme's most load-bearing documents: they "
        "are where it recorded its own failures while they were still fresh.</p>\n"
        "<hr>\n"
    )
    for slug, title, summary, kind, path in entries:
        index_body += (
            '<h2><a href="/journal/%s/">%s</a></h2>\n<p>%s…</p>\n'
            '<p style="font-size:.9rem;color:var(--soft)">'
            '<a href="%s%s">source</a></p>\n'
            % (slug, html.escape(title), html.escape(summary), REPO, path)
        )
    with open(os.path.join(OUT, "index.html"), "w", encoding="utf-8") as fh:
        fh.write(page_shell(
            "Lab journal", index_body,
            "The lab notebook of the noophorics programme: the void run, the near "
            "miss, and the retraction of its own diagnosis.",
            "https://noophorics.org/journal/", style))

    print("built %d entries + index" % len(entries))
    return 0


if __name__ == "__main__":
    raise SystemExit(build())
