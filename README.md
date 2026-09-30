# Bilingual Resume Generator

Initial project structure for future English/Persian resume variants:
`resume-software-en`, `resume-software-fa`, `resume-python-en`,
`resume-python-fa`, `resume-go-en`, and `resume-go-fa`.

Future flow: YAML data → variant config → language content → Jinja2 HTML → CSS → PDF.

## Directories

- `data/` — shared structured resume data.
- `content/` — language-specific English and Persian copy.
- `config/` — per-variant selection and configuration.
- `templates/` — Jinja2 page template and reusable partials.
- `styles/` — shared, language-specific, and print CSS.
- `assets/` — future font and icon files.
- `output/` — generated HTML and PDF artifacts.
- `scripts/` — future HTML, PDF, and combined build commands.

`build.py` will later serve as the top-level build entry point.
