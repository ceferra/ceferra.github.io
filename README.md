# ceferra.github.io

Personal academic website of Cèsar Ferri — https://ceferra.github.io

Plain HTML/CSS, no build step. GitHub Pages serves the `main` branch directly.

- `index.html` — home page (bio, research, selected publications, software, contact)
- `publications.html` — **generated**; do not edit by hand
- `news.html` — past news (older than ~1 year); move items here from `index.html`
- `assets/` — stylesheet and images (replace `avatar.svg` with a photo)

## Updating the publication list

```bash
python3 scripts/build_publications.py
```

Pulls all works for ORCID 0000-0002-8975-1120 from OpenAlex, deduplicates
preprint/published versions and rewrites `publications.html` from
`scripts/publications.template.html`.

The script also copies the `<head>` and navigation menu from `index.html` into the other pages,
so after changing the menu just rerun it.
