"""Generate the six bilingual resume HTML files from shared structured data."""

import json
import re
from pathlib import Path
from typing import Dict, List, Optional, Union

from jinja2 import Environment, FileSystemLoader, select_autoescape
from markupsafe import Markup, escape


ROOT = Path(__file__).resolve().parent
LANGUAGES = {
    "en": {"direction": "ltr", "name": "Mohammad Javad Saberian", "summary_heading": "Professional Summary", "experience_heading": "Experience", "education_heading": "Education"},
    "fa": {"direction": "rtl", "name": "محمد جواد صابریان", "summary_heading": "خلاصه", "experience_heading": "سوابق کاری", "education_heading": "تحصیلات"},
}
VARIANTS = ("software", "python", "go")
INLINE_PARTS = re.compile(r"(\*\*[^*]+\*\*|\bDanab\b|\bPatriot\b)")


def yaml_value(value: str) -> Union[str, bool]:
    """Read the quoted strings and booleans used by the initial content files."""
    value = value.strip()
    if value in {"true", "false"}:
        return value == "true"
    return value.strip('"')


def load_yaml(path: Path) -> dict:
    """Load the small YAML subset used by the initial summary and variant files."""
    lines = path.read_text(encoding="utf-8").splitlines()
    result: dict = {}
    current_mapping: Optional[dict] = None
    segments: list[dict] = []

    for line in lines:
        if not line or line.lstrip().startswith("#"):
            continue
        indentation = len(line) - len(line.lstrip())
        key, _, raw_value = line.strip().partition(":")
        if indentation == 0:
            if raw_value.strip():
                result[key] = yaml_value(raw_value)
            else:
                current_mapping = {}
                result[key] = current_mapping
        elif line.lstrip().startswith("- text:"):
            segments.append({"text": yaml_value(raw_value)})
            result["shared"] = {"segments": segments}
        elif key == "bold" and segments:
            segments[-1][key] = yaml_value(raw_value)
        elif current_mapping is not None:
            current_mapping[key] = yaml_value(raw_value)

    return result


def load_skills(path: Path, variant: str) -> List[Dict]:
    """Load the shared skill groups in the selected variant's defined order."""
    data = json.loads(path.read_text(encoding="utf-8"))
    return [data["groups"][group_id] for group_id in data["variants"][variant]]


def load_structured(path: Path):
    """JSON is a YAML-compatible subset used by the shared records."""
    return json.loads(path.read_text(encoding="utf-8"))


def render_achievement(value: str, projects: dict) -> Markup:
    """Render limited bold markup and named project links from trusted content."""
    rendered = Markup("")
    for part in INLINE_PARTS.split(value):
        if not part:
            continue
        bold = part.startswith("**") and part.endswith("**")
        content = part[2:-2] if bold else part
        if content in {"Danab", "Patriot"}:
            url = projects[f"{content.lower()}_url"]
            if url:
                inner = Markup('<a class="project-link" href="{url}" target="_blank" rel="noopener noreferrer" dir="ltr">{name}<span class="project-link__icon" aria-hidden="true"> ↗</span></a>').format(url=escape(url), name=escape(content))
            else:
                inner = escape(content)
        else:
            inner = escape(content)
        rendered += Markup("<strong>{}</strong>").format(inner) if bold else inner
    return rendered


def main() -> None:
    """Build one HTML preview for each variant and language."""
    environment = Environment(
        loader=FileSystemLoader(ROOT / "templates"),
        autoescape=select_autoescape(["html", "j2"]),
    )
    environment.filters["render_achievement"] = render_achievement
    template = environment.get_template("resume.html.j2")
    output_directory = ROOT / "output" / "html"
    output_directory.mkdir(parents=True, exist_ok=True)
    profile = load_structured(ROOT / "data" / "profile.yaml")
    projects = load_structured(ROOT / "data" / "projects.yaml")
    education = load_structured(ROOT / "data" / "education.yaml")
    experience = load_structured(ROOT / "data" / "experience.yaml")

    expected_names = {
        f"resume-{variant}-{language}.html"
        for variant in VARIANTS for language in LANGUAGES
    }
    for stale_path in output_directory.glob("resume-*.html"):
        if stale_path.name not in expected_names:
            stale_path.unlink()

    for variant_name in VARIANTS:
        variant_path = ROOT / "config" / f"{variant_name}.yaml"
        variant = load_yaml(variant_path)
        for language, language_settings in LANGUAGES.items():
            summaries = load_yaml(ROOT / "content" / language / "summaries.yaml")
            output_path = output_directory / f"resume-{variant['variant']}-{language}.html"
            output_path.write_text(
                template.render(
                    language=language,
                    direction=language_settings["direction"],
                    name_placeholder=language_settings["name"],
                    resume_title=variant["titles"][language],
                    summary_heading=language_settings["summary_heading"],
                    summary=summaries[variant["summary"]],
                    skills_heading="Skills" if language == "en" else "مهارت‌ها",
                    skills=load_skills(ROOT / "data" / "skills.yaml", variant["variant"]),
                    profile=profile,
                    projects=projects,
                    experience_heading=language_settings["experience_heading"],
                    experience=experience,
                    education_heading=language_settings["education_heading"],
                    education=education,
                ),
                encoding="utf-8",
            )


if __name__ == "__main__":
    main()
