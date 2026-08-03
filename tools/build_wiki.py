#!/usr/bin/env python3
"""Build /wiki/ — one generated map of the whole programme.

The site has a canonical page that argues, a journal that records, and a
repository that holds the sources. What it did not have is a place to look
something up: what `β` is, whether L2 still stands, which experiments are void,
what claim 7 was and what killed it. A reader who arrives knowing one term had
to read an essay to place it.

**Generated, never written.** Every row here is read out of the file that owns
it — `lexicon.md` for the terms and symbols, `theory/laws.md` for the laws and
their status lines, `RETRACTIONS.md` for the withdrawals, `theory/open-problems.md`
for the problems, and the `experiments/` directory for run status, which is
inferred from which files exist rather than from anything anybody typed twice.

That is the whole design constraint. A hand-maintained index of a repository
that retracts its own claims would be wrong within a week, and it would be
wrong in the specific way this repository is about: confidently, in a document
that looks maintained. `check_links.py` and `check_retracted.py` cover the
generated output like any other page.

    python3 tools/build_wiki.py            # write docs/wiki/index.html
    python3 tools/build_wiki.py --check    # fail if it is stale
"""

from __future__ import annotations

import argparse
import html
import json
import os
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "docs" / "wiki" / "index.html"
GH = "https://github.com/vyakymenko/noophorics/blob/main/"


def read(rel: str) -> str:
    return (ROOT / rel).read_text(encoding="utf-8")


def md_inline(text: str) -> str:
    """The small subset that appears in these sources. Escapes first."""
    text = html.escape(text)
    text = re.sub(r"~~(.+?)~~", r"<s>\1</s>", text)
    text = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"`([^`]+)`", r'<code>\1</code>', text)
    text = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r"\1", text)   # link text only
    return text


def symbols():
    """The symbol table in lexicon.md, which is already the canonical list."""
    out = []
    for m in re.finditer(r"^\| `([^`]+)` \| ([^|]+) \| ([^|]+) \|$",
                         read("lexicon.md"), re.M):
        out.append((m.group(1).strip(), m.group(2).strip(), m.group(3).strip()))
    return out


def terms():
    """Glossary entries: a bold head at the start of a PARAGRAPH, then an em dash.

    Anchoring on the start of a *line* instead swallowed an entry. The efficiency
    entry wraps onto a line beginning `**valid only where ...**`, an emphasis
    inside a definition rather than a new head, and the pattern took it as one --
    consuming the real `net value (V_λ)` entry that followed. The count said 29
    where the file has 30, which is exactly how much warning a silent
    under-extraction gives you.
    """
    src = read("lexicon.md")
    out = []
    for block in re.split(r"\n\s*\n", src):
        block = block.strip()
        m = re.match(r"^\*\*(.+?)\*\*\s+—\s+(.+)$", block, re.S)
        if m:
            out.append((m.group(1).strip(), " ".join(m.group(2).split())))
    return out


def laws():
    src = read("theory/laws.md")
    out = []
    for m in re.finditer(r"^## (L\d)\s*—\s*(.+?)$", src, re.M):
        start = m.end()
        nxt = src.find("\n## ", start)
        block = src[start: nxt if nxt > 0 else len(src)]
        st = re.search(r"^\*\*Status:\*\*\s*(.+?)$", block, re.M)
        killer = re.search(r"^\*\*Refuted if:\*\*\s*(.+?)(?=\n\n)", block, re.M | re.S)
        title = re.sub(r"\s*<a id=\"[^\"]*\"></a>\s*", " ", m.group(2))
        title = re.sub(r"\s*\*\(.*?\)\*\s*$", "", title).strip()
        out.append({
            "id": m.group(1),
            "title": title,
            "status": " ".join(st.group(1).split()) if st else "—",
            "refuted_if": " ".join(killer.group(1).split()) if killer else "",
            "struck": "~~" in block[:400],
        })
    return out


def retractions():
    out = []
    for m in re.finditer(r"^\| (\d+) \| (.+?) \| (.+?) \| (.+?) \|$",
                         read("RETRACTIONS.md"), re.M):
        out.append(tuple(g.strip() for g in m.groups()))
    return out


def problems():
    out = []
    for m in re.finditer(r"^## (\d+)\.\s+(.+?)$", read("theory/open-problems.md"), re.M):
        out.append((m.group(1), m.group(2).strip()))
    return out


def experiments():
    """Status inferred from which files exist, never from a typed label."""
    base = ROOT / "experiments"
    out = []
    for d in sorted(p for p in base.iterdir() if p.is_dir()):
        has = {f.name for f in d.iterdir() if f.is_file()}
        if "VOID.md" in has:
            status, cls = "void", "void"
        elif "FINDINGS.md" in has:
            status, cls = "findings", "ok"
        elif "PREREGISTRATION.md" in has:
            status, cls = "registered, not run", "pending"
        else:
            status, cls = "no registration", "pending"
        # A note about a past event must not read as a present one. E-004's
        # blocked arm ran on 2026-08-03 and the note stayed on disk, as it must
        # -- nothing here is deleted -- so the row went on saying "an arm is
        # blocked" about an experiment that had finished collecting. A file's
        # existence is the wrong tense; whether it declares itself closed is
        # the right one.
        def closed(name):
            try:
                return "## Closed" in (d / name).read_text(encoding="utf-8")
            except OSError:
                return False

        notes = []
        if "INTERRUPTED.md" in has:
            notes.append("interrupted, resumed" if closed("INTERRUPTED.md")
                         or "Outcome" in (d / "INTERRUPTED.md").read_text(encoding="utf-8")
                         else "interrupted")
        if "BLOCKED-NOTE.md" in has:
            notes.append("an arm was blocked" if closed("BLOCKED-NOTE.md")
                         else "an arm is blocked")
        if "DEFECT-001.md" in has:
            notes.append("defect recorded")
        results = sorted((d / "results").glob("*.json")) if (d / "results").is_dir() else []
        out.append({"id": d.name, "status": status, "cls": cls,
                    "notes": ", ".join(notes), "results": len(results)})
    return out


def render() -> str:
    sym, trm = symbols(), terms()
    lw, rt, pb, ex = laws(), retractions(), problems(), experiments()

    def rows(items, fn):
        return "\n".join(fn(i) for i in items)

    ld = json.dumps({
        "@context": "https://schema.org",
        "@type": "DefinedTermSet",
        "@id": "https://noophorics.org/wiki/#termset",
        "name": "Noophorics reference",
        "description": ("Every quantity, law, experiment, withdrawn claim and "
                        "open problem in the programme, generated from the "
                        "files that define them."),
        "url": "https://noophorics.org/wiki/",
        "inLanguage": "en",
        "isPartOf": {"@id": "https://noophorics.org/#website"},
        "license": "https://creativecommons.org/licenses/by/4.0/",
        "hasDefinedTerm": [
            {"@type": "DefinedTerm", "name": s[0], "description": s[1]}
            for s in sym],
    }, ensure_ascii=False, separators=(",", ":"))

    return """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Reference — Noophorics</title>
<meta name="description" content="Every quantity, law, experiment, withdrawn claim and open problem in the programme, on one page, generated from the files that define them.">
<meta name="color-scheme" content="light dark">
<link rel="canonical" href="https://noophorics.org/wiki/">
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<meta property="og:title" content="Reference — Noophorics">
<meta property="og:type" content="website">
<meta property="og:url" content="https://noophorics.org/wiki/">
<meta property="og:description" content="Every quantity, law, experiment, withdrawn claim and open problem, generated from source.">
<meta property="og:image" content="https://noophorics.org/og.png">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:image" content="https://noophorics.org/og.png">
<script type="application/ld+json">%s</script>
<style>
:root{--plate:#e7e8e3;--ink:#12161a;--soft:#5c6369;--rule:#c5c7c0;--acc:#a3291d;
  --serif:"Iowan Old Style",Palatino,Charter,Georgia,serif;
  --mono:ui-monospace,"SF Mono",Menlo,Consolas,monospace;color-scheme:light dark}
@media (prefers-color-scheme:dark){:root{--plate:#0f1317;--ink:#d7d9d4;
  --soft:#8c9299;--rule:#262c32;--acc:#e0705f}}
*{box-sizing:border-box}
body{margin:0;background:var(--plate);color:var(--ink);font-family:var(--serif);
  font-size:17px;line-height:1.6}
main{max-width:56rem;margin:0 auto;padding:clamp(2rem,6vw,4rem) 1.25rem 5rem}
a{color:inherit}
h1{font-size:clamp(1.9rem,1.4rem + 2.2vw,2.7rem);font-weight:400;margin:0 0 .6rem;
  letter-spacing:-.01em}
.sub{color:var(--soft);margin:0 0 2.4rem;max-width:40rem}
h2{font-size:1.3rem;font-weight:400;margin:3rem 0 .4rem;padding-bottom:.4rem;
  border-bottom:1px solid var(--rule)}
h2 .n{font-family:var(--mono);font-size:.75rem;color:var(--soft);
  letter-spacing:.1em;margin-left:.6rem}
.hint{color:var(--soft);font-size:.9rem;margin:.4rem 0 1.2rem}
.wrap{overflow-x:auto}
table{border-collapse:collapse;width:100%%;font-size:.94rem;margin:0 0 1rem}
th,td{text-align:left;padding:.5rem .7rem;border-bottom:1px solid var(--rule);
  vertical-align:top}
th{font-family:var(--mono);font-size:.72rem;letter-spacing:.09em;
  text-transform:uppercase;color:var(--soft);font-weight:400;white-space:nowrap}
code{font-family:var(--mono);font-size:.88em}
.sym{font-family:var(--mono);white-space:nowrap;color:var(--acc)}
.tag{font-family:var(--mono);font-size:.7rem;letter-spacing:.08em;
  text-transform:uppercase;padding:.12rem .45rem;border:1px solid var(--rule);
  border-radius:2px;white-space:nowrap}
.tag.void{color:var(--acc);border-color:var(--acc)}
.tag.ok{color:var(--ink)}
.tag.pending{color:var(--soft)}
dl{margin:0}
dt{font-weight:600;margin:1.1rem 0 .2rem}
dd{margin:0;color:var(--soft)}
s{opacity:.65}
.back{margin-top:3.5rem;font-size:.9rem;color:var(--soft)}
nav.toc{font-family:var(--mono);font-size:.78rem;letter-spacing:.06em;
  text-transform:uppercase;margin:0 0 2.5rem;line-height:2.1}
nav.toc a{margin-right:1.1rem;white-space:nowrap}
</style>
</head>
<body>
<main>
<h1>Reference</h1>
<p class="sub">Every quantity, law, experiment, withdrawn claim and open problem
in the programme. This page is <strong>generated</strong> from the files that
define each of them — nothing here is typed twice, so it cannot drift from the
theory the way a hand-kept index would.</p>

<nav class="toc">
  <a href="#symbols">Symbols</a><a href="#terms">Terms</a><a href="#laws">Laws</a>
  <a href="#experiments">Experiments</a><a href="#withdrawn">Withdrawn</a>
  <a href="#problems">Open problems</a>
</nav>

<h2 id="symbols">Symbols<span class="n">%d</span></h2>
<p class="hint">From the symbol table in <a href="%slexicon.md">lexicon.md</a>.</p>
<div class="wrap"><table>
<thead><tr><th>Symbol</th><th>Reads as</th><th>Defined in</th></tr></thead>
<tbody>
%s
</tbody></table></div>

<h2 id="terms">Terms<span class="n">%d</span></h2>
<p class="hint">Struck text is a withdrawn claim kept in place, never deleted.</p>
<dl>
%s
</dl>

<h2 id="laws">Conjectural laws<span class="n">%d</span></h2>
<p class="hint">A law enters the record only with a refutation condition
attached, and leaves it never. From <a href="%stheory/laws.md">theory/laws.md</a>.</p>
<div class="wrap"><table>
<thead><tr><th></th><th>Law</th><th>Status</th><th>Refuted if</th></tr></thead>
<tbody>
%s
</tbody></table></div>

<h2 id="experiments">Experiments<span class="n">%d</span></h2>
<p class="hint">Status is read from which files exist in each directory — a
<code>VOID.md</code>, a <code>FINDINGS.md</code>, a
<code>PREREGISTRATION.md</code> — not from a label anybody maintains.</p>
<div class="wrap"><table>
<thead><tr><th>Id</th><th>Status</th><th>Results</th><th>Notes</th></tr></thead>
<tbody>
%s
</tbody></table></div>

<h2 id="withdrawn">Withdrawn claims<span class="n">%d</span></h2>
<p class="hint">Ours, with what killed each one. Full index at
<a href="/journal/retractions/">retractions</a>.</p>
<div class="wrap"><table>
<thead><tr><th>#</th><th>Claim</th><th>Killed by</th></tr></thead>
<tbody>
%s
</tbody></table></div>

<h2 id="problems">Open problems<span class="n">%d</span></h2>
<div class="wrap"><table>
<thead><tr><th>#</th><th>Problem</th></tr></thead>
<tbody>
%s
</tbody></table></div>

<p class="back"><a href="/">Noophorics</a> · <a href="/journal/">Lab journal</a> ·
<a href="https://github.com/vyakymenko/noophorics">Repository</a></p>
</main>
</body>
</html>
""" % (
        ld,
        len(sym), GH,
        rows(sym, lambda s: '<tr><td class="sym">%s</td><td>%s</td><td>%s</td></tr>'
             % (html.escape(s[0]), md_inline(s[1]), md_inline(s[2]))),
        len(trm),
        rows(trm, lambda t: "<dt>%s</dt><dd>%s</dd>"
             % (md_inline(t[0]), md_inline(t[1]))),
        len(lw), GH,
        rows(lw, lambda l: '<tr><td class="sym">%s</td><td>%s</td><td>%s</td><td>%s</td></tr>'
             % (l["id"], md_inline(l["title"]), md_inline(l["status"]),
                md_inline(l["refuted_if"]) or "—")),
        len(ex),
        rows(ex, lambda e: '<tr><td class="sym">%s</td><td><span class="tag %s">%s</span></td>'
                           "<td>%s</td><td>%s</td></tr>"
             % (html.escape(e["id"]), e["cls"], html.escape(e["status"]),
                e["results"] or "—", html.escape(e["notes"]) or "—")),
        len(rt),
        # The claim column is struck, not plain. These are withdrawn claims and
        # the site's convention for a withdrawn claim is <s>...</s> everywhere
        # else; printing them unstruck here made check_retracted fire on this
        # page the first time it was generated, which was correct -- a table
        # heading is not a strikethrough, and a reader skimming the column sees
        # the claim before the column header.
        rows(rt, lambda r: "<tr><td>%s</td><td><s>%s</s></td><td>%s</td></tr>"
             % (r[0], md_inline(r[1]), md_inline(r[2]))),
        len(pb),
        rows(pb, lambda p: "<tr><td>%s</td><td>%s</td></tr>"
             % (p[0], md_inline(p[1]))),
    )


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args()
    want = render()
    if args.check:
        if not OUT.exists() or OUT.read_text(encoding="utf-8") != want:
            print("build_wiki: /wiki/ is stale — run tools/build_wiki.py")
            return 1
        print("build_wiki: /wiki/ current")
        return 0
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(want, encoding="utf-8")
    print("  wiki: %d symbols, %d terms, %d laws, %d experiments, %d withdrawn, "
          "%d problems" % (len(symbols()), len(terms()), len(laws()),
                           len(experiments()), len(retractions()), len(problems())))
    return 0


if __name__ == "__main__":
    sys.exit(main())
