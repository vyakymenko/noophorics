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
import json
import re
import sys
import subprocess
from typing import List, Tuple

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOCS = os.path.join(ROOT, "docs")
OUT = os.path.join(DOCS, "journal")

SOURCES: List[Tuple[str, str, str]] = [
    # (slug, source path, kind)
    ("founding", "journal/2026-07-28-founding.md", "journal"),
    ("first-live-run-void", "journal/2026-07-28-first-live-run-void.md", "journal"),
    ("e-001-findings", "experiments/E-001-fluency-cost/FINDINGS.md", "findings"),
    ("e-001b-void", "experiments/E-001b-fluency-factorial/VOID.md", "void"),
    ("e-001b-defect", "experiments/E-001b-fluency-factorial/DEFECT-001.md", "defect"),
    ("e-001c-feasibility",
     "experiments/E-001c-fluency-length-controlled/FEASIBILITY.md", "instrument"),
    ("e-002-void", "experiments/E-002-phantom-agreement/VOID.md", "void"),
    ("e-002b-findings",
     "experiments/E-002b-phantom-agreement-ladder/FINDINGS.md", "findings"),
    ("e-002c-findings",
     "experiments/E-002c-calibration-slope/FINDINGS.md", "findings"),
    ("cross-sender-disagreement",
     "journal/2026-07-30-cross-sender-disagreement.md", "observation"),
    ("two-audit-holes", "journal/2026-07-30-two-audit-holes.md", "audit"),
    ("site-four-versions-behind",
     "journal/2026-07-31-the-site-was-four-versions-behind.md", "audit"),
    ("e-004-void", "experiments/E-004-disagreement-detector/VOID.md", "void"),
    ("e-004-interrupted",
     "experiments/E-004-disagreement-detector/INTERRUPTED.md", "instrument"),
    ("e-001c-defect", "experiments/E-001c-fluency-length-controlled/DEFECT-001.md",
     "defect"),
    ("e-001c-calibration",
     "experiments/E-001c-fluency-length-controlled/CALIBRATION-001.md", "instrument"),
    ("e-001c-void", "experiments/E-001c-fluency-length-controlled/VOID.md", "void"),
    ("nine-templates-not-thirty-two-probes",
     "journal/2026-08-18-nine-templates-not-thirty-two-probes.md", "audit"),
    ("headroom-was-one-readers-uncertainty",
     "journal/2026-08-19-the-headroom-was-one-readers-uncertainty.md", "observation"),
    ("e-002c-defect",
     "experiments/E-002c-calibration-slope/DEFECT-001.md", "defect"),
    ("e-006-void", "experiments/E-006-ablation-ladder/VOID.md", "void"),
    ("good-instrument-sitting-unused",
     "journal/2026-08-28-the-good-instrument-was-sitting-unused.md", "observation"),
    ("retractions", "RETRACTIONS.md", "audit"),
    ("prior-art", "theory/prior-art.md", "audit"),
]

# Experiment documents that are deliberately NOT published as journal entries.
# Anything else matching the patterns below and missing from SOURCES is a
# build error, not a silent omission -- E-001c's VOID.md sat unpublished for
# days because SOURCES is hand-maintained and a new experiment produces new
# files nobody remembers to add. The same shape as check_retracted.py's source
# list, found the same way and fixed the same way.
NOT_PUBLISHED = {
    "experiments/E-004-disagreement-detector/BLOCKED-NOTE.md",
    "experiments/E-001b-fluency-factorial/SENSITIVITY-M33.md",
    "experiments/E-001b-fluency-factorial/AMENDMENT-001.md",
    "experiments/E-001c-fluency-length-controlled/AMENDMENT-001.md",
}
PUBLISHABLE = ("VOID.md", "FINDINGS.md", "DEFECT-001.md", "INTERRUPTED.md",
               "CALIBRATION-001.md", "FEASIBILITY.md")


def check_sources_complete() -> list:
    """Every publishable document is listed or explicitly excluded.

    Covers `journal/*.md` as well as the experiment tree. It did not, until
    2026-08-18: the guard below was written after E-001c's VOID.md sat
    unpublished for days, and it was pointed only at `experiments/`. A new file
    in `journal/` was therefore dropped in exactly the way the guard exists to
    prevent -- silently, with the build still printing "built 19 entries" and
    exit 0. Found by writing an entry and noticing it never reached the site.

    The lesson the original comment drew was that a hand-maintained list drifts.
    The lesson it missed is that a guard covering one of the two directories the
    list draws from is itself a hand-maintained list.
    """
    listed = {path for _, path, _ in SOURCES}
    missing = []
    jdir = os.path.join(ROOT, "journal")
    if os.path.isdir(jdir):
        for name in sorted(os.listdir(jdir)):
            if not name.endswith(".md"):
                continue
            rel = "journal/%s" % name
            if rel not in listed and rel not in NOT_PUBLISHED:
                missing.append(rel)
    base = os.path.join(ROOT, "experiments")
    for exp in sorted(os.listdir(base)):
        d = os.path.join(base, exp)
        if not os.path.isdir(d):
            continue
        for name in sorted(os.listdir(d)):
            if name not in PUBLISHABLE:
                continue
            rel = "experiments/%s/%s" % (exp, name)
            if rel not in listed and rel not in NOT_PUBLISHED:
                missing.append(rel)
    return missing

REPO = "https://github.com/vyakymenko/noophorics/blob/main/"
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Directory a document's relative links resolve against. Set per source before
# rendering: a link written in RETRACTIONS.md at the repo root and the same
# link written in journal/ point at different files.
_LINK_BASE = ["journal"]


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
        base = _LINK_BASE[0]
        href = REPO + os.path.normpath(
            os.path.join(base, href)
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


def structured_data(title: str, description: str, canonical: str, kind: str,
                    source: str) -> str:
    """Schema.org for one journal page, with every value read from the page.

    Thirty-six of thirty-seven pages carried none. The fifteen under journal/
    are the actual research record -- findings, retractions, prior art, voided
    runs -- and to a search engine or a citation tool they were untyped prose.

    AGENTS.md puts JSON-LD *structure* in the presentation lane and its claim
    values in the science lane, so nothing here is authored: the headline is
    the page's own H1, the description its own meta description, and the dates
    come from git rather than from a literal, because a hand-typed dateModified
    is a freshness claim nothing checks.
    """
    kind_to_type = {"findings": "ScholarlyArticle", "audit": "ScholarlyArticle",
                    "instrument": "TechArticle", "defect": "TechArticle",
                    "void": "ScholarlyArticle", "observation": "ScholarlyArticle",
                    "journal": "Article"}
    data = {
        "@context": "https://schema.org",
        "@type": kind_to_type.get(kind, "Article"),
        "@id": canonical + "#article",
        "headline": title,
        "description": description,
        "url": canonical,
        "inLanguage": "en",
        "isPartOf": {"@id": "https://noophorics.org/#website"},
        "license": "https://creativecommons.org/licenses/by/4.0/",
        "author": {"@type": "Person", "name": "Valentyn Yakymenko",
                   "url": "https://github.com/vyakymenko"},
        "publisher": {"@type": "Organization", "name": "Noophorics",
                      "url": "https://noophorics.org/"},
        "isAccessibleForFree": True,
        "creativeWorkStatus": "Published",
    }
    dates = git_dates(source)
    if dates:
        data["datePublished"], data["dateModified"] = dates
    return json.dumps(data, ensure_ascii=False, separators=(",", ":"))


def git_dates(path: str):
    """(first commit, last commit) for a file, as dates. None if git cannot say.

    Reading them from history rather than writing them down is the same
    argument the sitemap makes for lastmod: a literal date is a claim about
    freshness that nothing verifies, and this repository's history is the
    record by policy.
    """
    try:
        out = subprocess.run(
            ["git", "log", "--follow", "--format=%cs", "--", path],
            cwd=REPO_ROOT, capture_output=True, text=True, timeout=20)
    except (OSError, subprocess.SubprocessError):
        return None
    days = [l.strip() for l in out.stdout.splitlines() if l.strip()]
    return (days[-1], days[0]) if days else None


def page_shell(title: str, body: str, description: str, canonical: str,
               style: str, ld: str = "{}") -> str:
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
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:image:alt" content="Noophorics — a dark card reading NOOPHORICS above the line “Understanding is measured by behavioural convergence toward a declared reference”, footed with Φ phantom agreement and the version.">
<meta name="twitter:image" content="https://noophorics.org/og.png">
<script type="application/ld+json">%s</script>
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
<p class="back"><a href="/journal/">All journal entries</a> · <a href="/wiki/">Reference</a> · <a href="/">Noophorics</a> · <a href="https://github.com/vyakymenko/noophorics">Repository</a></p>
</main>
</body>
</html>
""" % (title, html.escape(description, quote=True), canonical, title, canonical,
       ld, style, body)


def extract_style(canonical_html: str) -> str:
    """Reuse the canonical page's variables and base rules verbatim."""
    m = re.search(r"<style>.*?</style>", canonical_html, re.S)
    return m.group(0) if m else "<style></style>"


def first_paragraph(rest: str) -> str:
    """The first real paragraph, joined across its lines.

    Two defects lived in the one-liner this replaces. It took a single *line*,
    so a wrapped paragraph was cut at the wrap; and it skipped any line
    starting with `*`, which excludes a bullet but also excludes a paragraph
    opening in **bold** -- the house style for a findings lede. E-002c opens
    with a bold sentence, so both fired at once and the description began at
    "six gates passed", three words into the second line of the first sentence.
    """
    block, started = [], False
    for line in rest.split("\n"):
        stripped = line.strip()
        if not stripped:
            if started:
                break
            continue
        if stripped.startswith(("#", ">", "|", "`", "---", "===")) or \
                re.match(r"^([-+]|\d+\.|\*)\s", stripped):
            if started:
                break
            continue                        # heading, quote, table, list, rule
        block.append(stripped)
        started = True
    return " ".join(block)


def summarise(first_para: str, rest: str, limit: int = 175) -> str:
    """A description that reads as a sentence, because it is one.

    The old rule was `first_paragraph[:180]`, which cut mid-word and often
    mid-clause: E-002c's search snippet read "six gates passed, all twenty-four
    briefs analysed, all four registered" -- starting lowercase, ending nowhere.
    That string is what a search result shows and what a chat client previews,
    so it is the first sentence of this repository most people ever read.

    Whole sentences are accumulated until adding the next would exceed the
    limit, so the snippet always ends on a full stop. Bold and emphasis markers
    are stripped but the words are never rewritten -- a description that
    paraphrases the page is a second claim to keep in sync.
    """
    text = first_para
    if len(text) < 80:                     # a short opener is a lede, not a summary
        for line in rest.split("\n"):
            line = line.strip()
            if (line and not line.startswith(("#", ">", "-", "*", "|", "`"))
                    and line != first_para):
                text += " " + line
                break
    text = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", text)       # links -> their text
    text = re.sub(r"[*`_]", "", text)
    text = " ".join(text.split())
    # A floor as well as a ceiling. Several entries open with a bold date or a
    # one-clause lede -- "2026-07-31, 19:04 local." -- and stopping at the
    # limit left that as the entire search snippet. Below the floor the next
    # sentence is taken whatever it costs; above it, the limit governs.
    floor = 70
    out = ""
    for piece in re.split(r"(?<=[.!?])\s+", text):
        if out and len(out) >= floor and len(out) + 1 + len(piece) > limit:
            break
        out = (out + " " + piece).strip()
        if len(out) >= limit:
            break
    return out or text[:limit]


def build() -> int:
    missing = check_sources_complete()
    if missing:
        print("refusing to build: publishable documents are not in "
              "SOURCES and not in NOT_PUBLISHED --", file=sys.stderr)
        for m in missing:
            print("  " + m, file=sys.stderr)
        print("  add each to one list or the other; a journal that silently omits "
              "a void is worse than one that fails to build", file=sys.stderr)
        return 2
    with open(os.path.join(DOCS, "index.html"), "r", encoding="utf-8") as fh:
        style = extract_style(fh.read())
    os.makedirs(OUT, exist_ok=True)

    entries = []
    for slug, path, kind in SOURCES:
        with open(os.path.join(ROOT, path), "r", encoding="utf-8") as fh:
            src = fh.read()
        _LINK_BASE[0] = os.path.dirname(path) or "."
        title = re.search(r"^#\s+(.*)$", src, re.M).group(1).strip()
        rest = src[src.index("\n", src.index("# ")) :]
        first_para = first_paragraph(rest)
        summary = summarise(first_para, rest)
        body = ('<p class="jn">%s · %s</p>\n<h1>%s</h1>\n%s'
                % (kind, slug.replace("-", " "), html.escape(title), markdown(rest)))
        out_dir = os.path.join(OUT, slug)
        os.makedirs(out_dir, exist_ok=True)
        url = "https://noophorics.org/journal/%s/" % slug
        with open(os.path.join(out_dir, "index.html"), "w", encoding="utf-8") as fh:
            fh.write(page_shell(title, body, summary, url, style,
                                structured_data(title, summary, url, kind, path)))
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
