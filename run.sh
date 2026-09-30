#!/usr/bin/env bash
set -euo pipefail

project_root="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$project_root"

echo "Building resume HTML..."
python3 build.py

for output_file in \
  resume-software-en.html resume-software-fa.html \
  resume-python-en.html resume-python-fa.html \
  resume-go-en.html resume-go-fa.html; do
  printf '✓ output/html/%s\n' "$output_file"
done

printf '\nGenerating PDFs...\n'
python3 scripts/build_pdf.py

printf '\nDone.\nHTML:\noutput/html/\n\nPDF:\noutput/pdf/\n'
