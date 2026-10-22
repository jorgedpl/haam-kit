#!/usr/bin/env python3
"""Check the translations of HAAM's docs for people (template/i18n/<language>/…, README.<language>.md).

A translation must keep everything a tool or an agent reads exactly as it is: fenced code blocks, inline code
(commands, labels, statuses, settings, paths), link targets and the headings' structure. Prose is translated.

    python3 tests/i18n_check.py            # every language
    python3 tests/i18n_check.py es fr      # some
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TEMPLATE = ROOT / "template"
LANGUAGES = ["es", "fr", "de", "it", "nl", "pt"]
# The docs people read. Agent instructions (AGENTS.md, CLAUDE.md, skills, reviewer prompts) stay in English.
TRANSLATED = [
    "docs/process/LIFECYCLE.md", "docs/process/GATES.md", "docs/process/TRACKER.md",
    "docs/process/PRODUCT-MANAGER.md",
    "docs/setup/HAAM-ADOPTION-GUIDE.md", "docs/setup/DECISIONS.md", "docs/setup/GITHUB-SETUP.md",
    "docs/setup/LINEAR-SETUP.md", "docs/setup/AGENTS-SETUP.md",
    "docs/ONBOARDING.md",
    "docs/templates/adr.md", "docs/templates/assessment.md", "docs/templates/bug.md", "docs/templates/epic.md",
    "docs/templates/feature-spec.md", "docs/templates/idea.md", "docs/templates/uat-plan.md",
    "docs/product/PRODUCT.md", "docs/product/ARCHITECTURE.md",
    "docs/epics/README.md", "docs/changes/README.md", "docs/decisions/0001-adopt-haam.md",
    ".github/pull_request_template.md",
]

# Text the skills or workflows look for, so it stays in English in every language.
LITERALS = {
    "docs/templates/uat-plan.md": ["**Fully verified by the agent:** no"],
    ".github/pull_request_template.md": ["Refs #"],
}

FENCE = re.compile(r"^[ \t]*```.*?^[ \t]*```", re.M | re.S)
INLINE = re.compile(r"(?<!`)`([^`\n]+)`(?!`)")
LINK = re.compile(r"\]\(([^)\s]+)\)")
HEADING = re.compile(r"^(#{1,6}) ", re.M)


def parts(text):
    fences = FENCE.findall(text)
    rest = FENCE.sub("", text)
    return fences, set(INLINE.findall(rest)), set(LINK.findall(rest)), [len(h) for h in HEADING.findall(rest)]


LANG_BAR = re.compile(r"^README(\.[a-z]{2})?\.md$")


def readme_links(links, lang):
    """A README links to the same docs in its language where they exist, and its language bar to the others."""
    out = set()
    for url in links:
        if LANG_BAR.match(url):
            continue
        prefix = f"template/i18n/{lang}/"
        if url.startswith(prefix):
            url = "template/" + url[len(prefix):]
        out.add(url)
    return out


def check(src_text, tr_text, readme_lang=None):
    """Problems with one translation, as short lines."""
    out = []
    s_f, s_i, s_l, s_h = parts(src_text)
    t_f, t_i, t_l, t_h = parts(tr_text)
    if readme_lang:
        s_l, t_l = readme_links(s_l, readme_lang), readme_links(t_l, readme_lang)
        if "README.md" not in LINK.findall(tr_text):
            out.append("the language bar has no link back to README.md (English)")
    if s_f != t_f:
        out.append(f"code blocks differ: {len(s_f)} in English, {len(t_f)} here, or one was changed")
    for code in sorted(s_i - t_i):
        out.append(f"inline code missing or changed: `{code}`")
    for url in sorted(s_l - t_l):
        out.append(f"link target missing or changed: {url}")
    if s_h != t_h:
        out.append(f"headings differ: {len(s_h)} in English, {len(t_h)} here (or their levels)")
    return out


def pairs(lang):
    yield ROOT / "README.md", ROOT / f"README.{lang}.md"
    for rel in TRANSLATED:
        yield TEMPLATE / rel, TEMPLATE / "i18n" / lang / rel


def main(langs):
    bad = 0
    for lang in langs:
        extra = [p for p in (TEMPLATE / "i18n" / lang).rglob("*") if p.is_file() and p.name != "GLOSSARY.md"
                 and p.relative_to(TEMPLATE / "i18n" / lang).as_posix() not in TRANSLATED]
        for p in extra:
            print(f"{lang}: {p.relative_to(ROOT)}: not a file the kit translates")
            bad += 1
        for src, tr in pairs(lang):
            if not tr.exists():
                print(f"{lang}: missing {tr.relative_to(ROOT)}")
                bad += 1
                continue
            readme = lang if src.name == "README.md" and src.parent == ROOT else None
            rel = tr.relative_to(TEMPLATE / "i18n" / lang).as_posix() if readme is None else ""
            for lit in LITERALS.get(rel, []):
                if lit not in tr.read_text():
                    print(f"{lang}: {tr.relative_to(ROOT)}: must keep this text in English: {lit}")
                    bad += 1
            for problem in check(src.read_text(), tr.read_text(), readme):
                print(f"{lang}: {tr.relative_to(ROOT)}: {problem}")
                bad += 1
    print("OK" if not bad else f"{bad} problem(s)")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:] or LANGUAGES))
