#!/usr/bin/env python3
"""Fail if a cross-reference in this repository points at nothing.

The third of three mechanical checks over the same body of text, and they fail
independently: `check_counts.py` verifies that a stated number matches its
source, `check_retracted.py` that a stated claim matches its source, and this
one that a stated *location* exists at all.

A dead link here is not cosmetic. Most of this repository's claims are load
bearing only because they carry a pointer -- "refuted, see [laws §L4]", "the
gate is defined in [PREREGISTRATION §3]", "reproduce with [beta_sweep.py]".
A pointer that resolves to nothing turns a checkable claim into an assertion,
and it does it silently, because a broken link renders exactly like a working
one until somebody clicks it.

What is checked:

  markdown   [text](target) and [text]: target -- the file must exist, and a
             `#fragment` must match a heading on that page or an explicit
             `<a id="...">` anchor in it
  html       href="..." within docs/ -- resolved against the published route
             layout, so `/journal/foo/` means `docs/journal/foo/index.html`

What is not checked: external `http(s)://` and `mailto:` targets. Reaching the
network would make this check fail for reasons that have nothing to do with the
repository, and a check that goes red when a third-party site is slow gets
disabled, which is worse than not having it.

    python3 tools/check_links.py           # 0 = every internal link resolves
    python3 tools/check_links.py --list    # print what was checked, and skipped

Exit status is what CI reads.
"""

from __future__ import annotations

import argparse
import html
import os
import re
import sys
import unicodedata
from pathlib import Path
from typing import Dict, List, Set, Tuple

ROOT = Path(__file__).resolve().parent.parent

SKIP_DIRS = {".git", ".venv", "node_modules", "__pycache__", "automation"}

# Markdown inline links, reference definitions, and bare autolinks.
MD_INLINE = re.compile(r"\[(?:[^\]]*)\]\(\s*<?([^)\s>]+)>?(?:\s+\"[^\"]*\")?\s*\)")
MD_REFDEF = re.compile(r"^\s*\[[^\]]+\]:\s*<?([^\s>]+)>?", re.M)

HTML_HREF = re.compile(r"""\bhref\s*=\s*["']([^"']+)["']""", re.I)
HTML_ID = re.compile(r"""\bid\s*=\s*["']([^"']+)["']""", re.I)
HTML_NAME = re.compile(r"""<a\b[^>]*\bname\s*=\s*["']([^"']+)["']""", re.I)

MD_HEADING = re.compile(r"^(#{1,6})\s+(.+?)\s*#*\s*$", re.M)
MD_ANCHOR = re.compile(r"""<a\b[^>]*\bid\s*=\s*["']([^"']+)["']""", re.I)

EXTERNAL = re.compile(r"^(?:[a-z][a-z0-9+.-]*:|//)", re.I)


def rel_to_root(p: Path) -> str:
    """Display path, which must never be the reason this check crashes.

    `Path.relative_to` raises when the two paths straddle a symlink -- on macOS
    a resolved temp path is `/private/var/...` while its parent is `/var/...`,
    and the same happens for any checkout reached through a link. A link
    checker that raises a ValueError instead of naming a broken link has turned
    a report into an outage, so this degrades to the absolute path instead.
    """
    try:
        return p.relative_to(ROOT).as_posix()
    except ValueError:
        return os.path.relpath(str(p), str(ROOT))


def slug(text: str) -> str:
    """GitHub's heading-anchor rule, which is what the markdown links assume."""
    text = re.sub(r"<[^>]+>", "", text)
    text = re.sub(r"`([^`]*)`", r"\1", text)
    text = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", text)   # link text only
    text = unicodedata.normalize("NFKD", text).lower()
    text = re.sub(r"[^\w\s-]", "", text)
    return re.sub(r"\s+", "-", text.strip())


def walk(suffix: str) -> List[Path]:
    out = []
    for dirpath, dirnames, filenames in os.walk(ROOT):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for name in filenames:
            if name.endswith(suffix):
                out.append(Path(dirpath) / name)
    return sorted(out)


def md_anchors(path: Path) -> Set[str]:
    text = path.read_text(encoding="utf-8", errors="replace")
    anchors = {slug(m.group(2)) for m in MD_HEADING.finditer(text)}
    anchors |= set(MD_ANCHOR.findall(text))
    return anchors


def html_anchors(path: Path) -> Set[str]:
    text = path.read_text(encoding="utf-8", errors="replace")
    return set(HTML_ID.findall(text)) | set(HTML_NAME.findall(text))


def resolve_html(target: str) -> Path | None:
    """A published href -> the file that actually serves it.

    Site-absolute hrefs (`/journal/foo/`) are rooted at docs/, and a directory
    route is served by its index.html. Getting this wrong in the permissive
    direction would make the check pass on links that 404 in production, which
    is the only failure mode that matters for a link checker.
    """
    docs = ROOT / "docs"
    target = target.split("?", 1)[0]
    if target.startswith("/"):
        base = docs / target.lstrip("/")
    else:
        return None
    if target.endswith("/") or not base.suffix:
        return base / "index.html"
    return base


def check_markdown(report: List[Tuple[str, int, str, str]]) -> int:
    anchor_cache: Dict[Path, Set[str]] = {}
    checked = 0
    for path in walk(".md"):
        text = path.read_text(encoding="utf-8", errors="replace")
        rel = rel_to_root(path)
        targets = [(m.group(1), m.start()) for m in MD_INLINE.finditer(text)]
        targets += [(m.group(1), m.start()) for m in MD_REFDEF.finditer(text)]
        for target, pos in targets:
            if EXTERNAL.match(target) or target.startswith("#") and len(target) == 1:
                continue
            line = text.count("\n", 0, pos) + 1
            if target.startswith("#"):
                dest, frag = path, target[1:]
            else:
                file_part, _, frag = target.partition("#")
                dest = (path.parent / file_part).resolve()
                if not dest.exists():
                    report.append((rel, line, target, "no such file"))
                    continue
                if dest.is_dir():
                    checked += 1
                    continue
            checked += 1
            if not frag:
                continue
            if dest.suffix != ".md":
                continue
            if dest not in anchor_cache:
                anchor_cache[dest] = md_anchors(dest)
            if frag not in anchor_cache[dest]:
                report.append((rel, line, target, "no such anchor in "
                               + rel_to_root(dest)))
    return checked


def check_html(report: List[Tuple[str, int, str, str]]) -> int:
    anchor_cache: Dict[Path, Set[str]] = {}
    checked = 0
    for path in sorted((ROOT / "docs").rglob("*.html")):
        text = path.read_text(encoding="utf-8", errors="replace")
        rel = rel_to_root(path)
        for m in HTML_HREF.finditer(text):
            target = html.unescape(m.group(1)).strip()
            if not target or EXTERNAL.match(target):
                continue
            line = text.count("\n", 0, m.start()) + 1
            if target.startswith("#"):
                frag, dest = target[1:], path
            elif target.startswith("/"):
                file_part, _, frag = target.partition("#")
                dest = resolve_html(file_part)
                if dest is None or not dest.exists():
                    report.append((rel, line, target, "no page serves this route"))
                    continue
            else:
                file_part, _, frag = target.partition("#")
                dest = (path.parent / file_part).resolve()
                if not dest.exists():
                    report.append((rel, line, target, "no such file"))
                    continue
            checked += 1
            if not frag:
                continue
            if dest not in anchor_cache:
                anchor_cache[dest] = html_anchors(dest)
            if frag not in anchor_cache[dest]:
                report.append((rel, line, target, "no such anchor in "
                               + rel_to_root(dest)))
    return checked


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--list", action="store_true",
                    help="report totals including what was deliberately skipped")
    args = ap.parse_args()

    report: List[Tuple[str, int, str, str]] = []
    md = check_markdown(report)
    ht = check_html(report)

    if args.list:
        ext = 0
        for path in walk(".md"):
            text = path.read_text(encoding="utf-8", errors="replace")
            ext += sum(1 for m in MD_INLINE.finditer(text)
                       if EXTERNAL.match(m.group(1)))
        for path in sorted((ROOT / "docs").rglob("*.html")):
            text = path.read_text(encoding="utf-8", errors="replace")
            ext += sum(1 for m in HTML_HREF.finditer(text)
                       if EXTERNAL.match(html.unescape(m.group(1)).strip()))
        print("  markdown internal links checked : %d" % md)
        print("  html internal links checked     : %d" % ht)
        print("  external links skipped          : %d (never fetched)" % ext)

    if not report:
        print("check_links: %d internal links resolve (%d markdown, %d html)"
              % (md + ht, md, ht))
        return 0

    print("check_links: %d broken internal link(s)\n" % len(report))
    for rel, line, target, why in report:
        print("  %s:%d" % (rel, line))
        print("    -> %s" % target)
        print("       %s" % why)
        print()
    return 1


if __name__ == "__main__":
    sys.exit(main())
