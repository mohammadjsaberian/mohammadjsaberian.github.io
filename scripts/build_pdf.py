"""Generate print-layout PDFs for every rendered resume HTML preview."""

import os
import sys
import tempfile
from pathlib import Path
from typing import List


ROOT = Path(__file__).resolve().parents[1]
HTML_DIRECTORY = ROOT / "output" / "html"
PDF_DIRECTORY = ROOT / "output" / "pdf"
FONTCONFIG_CACHE = Path(tempfile.gettempdir()) / "resume-fontconfig"


def html_previews() -> List[Path]:
    """Return the generated resume previews in a deterministic order."""
    previews = [
        HTML_DIRECTORY / f"resume-{variant}-{language}.html"
        for variant in ("software", "python", "go")
        for language in ("en", "fa")
    ]
    if any(not preview.is_file() for preview in previews):
        raise RuntimeError(
            "Expected six HTML previews in output/html/. Run python3 build.py first."
        )
    return previews


def generate_pdfs(previews: List[Path]) -> None:
    """Render local HTML previews using WeasyPrint's print media support."""
    FONTCONFIG_CACHE.mkdir(parents=True, exist_ok=True)
    os.environ.setdefault("XDG_CACHE_HOME", str(FONTCONFIG_CACHE))

    try:
        from weasyprint import HTML
    except (ImportError, OSError) as error:
        raise RuntimeError(
            "WeasyPrint is not available. Run: pip install -r requirements.txt"
        ) from error

    PDF_DIRECTORY.mkdir(parents=True, exist_ok=True)
    expected_names = {f"{preview.stem}.pdf" for preview in previews}
    for stale_path in PDF_DIRECTORY.glob("resume-*.pdf"):
        if stale_path.name not in expected_names:
            stale_path.unlink()

    for html_path in previews:
        pdf_path = PDF_DIRECTORY / f"{html_path.stem}.pdf"
        try:
            HTML(
                filename=str(html_path),
                base_url=str(html_path.parent),
                media_type="print",
            ).write_pdf(str(pdf_path))
        except Exception as error:
            raise RuntimeError(
                f"Failed to generate {html_path.name}: {error}"
            ) from error

        if not pdf_path.is_file() or pdf_path.stat().st_size == 0:
            raise RuntimeError(f"Failed to generate a non-empty PDF: {pdf_path.name}")
        print(f"✓ output/pdf/{pdf_path.name}")


def main() -> None:
    """Generate a PDF for each existing HTML resume preview."""
    try:
        generate_pdfs(html_previews())
    except RuntimeError as error:
        print(error, file=sys.stderr)
        raise SystemExit(1)


if __name__ == "__main__":
    main()
