#!/usr/bin/env python3
"""Regenerate publications.html from OpenAlex (by ORCID).

Usage:  python3 scripts/build_publications.py
"""
import html
import json
import re
import urllib.request
from collections import defaultdict
from pathlib import Path

ORCID = "0000-0002-8975-1120"
ME = re.compile(r"c[eè]sar\s+ferri|ferri,?\s+c|c\.?\s*ferri", re.I)
ROOT = Path(__file__).resolve().parent.parent
SKIP_TYPES = {"dataset", "other", "peer-review", "erratum", "paratext"}
TYPE_RANK = {"article": 0, "data-paper": 0, "conference-paper": 1, "book-chapter": 2,
             "book": 2, "conference-abstract": 3, "preprint": 4}


def fetch():
    works, cursor = [], "*"
    while cursor:
        url = (f"https://api.openalex.org/works?filter=author.orcid:{ORCID}"
               f"&per-page=200&cursor={cursor}"
               "&select=title,publication_year,type,doi,cited_by_count,primary_location,authorships")
        data = json.load(urllib.request.urlopen(url, timeout=60))
        works += data["results"]
        cursor = data["meta"]["next_cursor"] if data["results"] else None
    return works


def norm(title):
    return re.sub(r"[^a-z0-9]", "", (title or "").lower())[:80]


def dedupe(works):
    best = {}
    for w in works:
        if w["type"] in SKIP_TYPES or not w.get("title"):
            continue
        if w["title"].lower().startswith("code for the paper"):
            continue
        key = norm(w["title"])
        rank = (TYPE_RANK.get(w["type"], 5), -(w["cited_by_count"] or 0))
        if key not in best or rank < best[key][0]:
            best[key] = (rank, w)
    return [w for _, w in best.values()]


def fmt_authors(authorships):
    names = [re.sub(r"^C\W?\s*sar Ferri$", "Cèsar Ferri", a["author"]["display_name"])
             for a in authorships]
    if len(names) > 12:
        names = names[:10] + ["et al."]
    return ", ".join(f"<strong>{html.escape(n)}</strong>" if ME.search(n) else html.escape(n)
                     for n in names)


def render(works):
    by_year = defaultdict(list)
    for w in works:
        by_year[w["publication_year"]].append(w)
    parts = []
    for year in sorted(by_year, reverse=True):
        parts.append(f'<h2 class="year" id="y{year}">{year}</h2>\n<ol class="pubs">')
        for w in sorted(by_year[year], key=lambda w: -(w["cited_by_count"] or 0)):
            venue = ((w.get("primary_location") or {}).get("source") or {}).get("display_name") or ""
            title = html.escape(w["title"])
            link = w.get("doi") or ""
            title_html = f'<a href="{link}">{title}</a>' if link else title
            cites = w["cited_by_count"] or 0
            badge = f' <span class="cites">{cites} cit.</span>' if cites else ""
            kind = "preprint" if w["type"] == "preprint" else ""
            parts.append(
                f'<li><span class="pub-title">{title_html}</span>{badge}<br>'
                f'<span class="pub-authors">{fmt_authors(w["authorships"])}</span><br>'
                f'<span class="pub-venue">{html.escape(venue)}{" · preprint" if kind and venue else kind}</span></li>')
        parts.append("</ol>")
    return "\n".join(parts)


def main():
    works = dedupe(fetch())
    template = (ROOT / "scripts" / "publications.template.html").read_text()
    out = template.replace("{{PUBLICATIONS}}", render(works)).replace("{{COUNT}}", str(len(works)))
    (ROOT / "publications.html").write_text(out)
    print(f"publications.html: {len(works)} entries")


if __name__ == "__main__":
    main()
