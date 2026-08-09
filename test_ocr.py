#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Diagnose-Skript: Testet OCR gegen koboldcpp (OpenAI-kompatible API).
Konvertiert eine PDF-Seite zu PNG und sendet das Bild an das Modell.
"""

import sys
import subprocess
from pathlib import Path

from ocr_to_markdown import chat_completion, select_ocr_model, _model_config, OCR_PROMPT

def main():
    pdf_path = sys.argv[1] if len(sys.argv) > 1 else "Jabra Sports_Pace_TechnSpecs_lores.pdf"
    model_name = sys.argv[2] if len(sys.argv) > 2 else "nanonets-ocr.kcpps"

    # PDF zu PNG konvertieren mit ImageMagick
    print("=" * 60)
    print("PDF ZU PNG KONVERTIEREN")
    print("=" * 60)
    png_path = "/tmp/test_ocr_page.png"
    result = subprocess.run(
        ["magick", "-density", "150", pdf_path + "[0]", png_path],
        capture_output=True, text=True
    )
    if result.returncode != 0:
        print(f"FEHLER bei Konvertierung: {result.stderr}")
        return
    print(f"PNG erstellt: {png_path} ({Path(png_path).stat().st_size} Bytes)")

    image_bytes = Path(png_path).read_bytes()
    config = _model_config(model_name)
    messages = [
        {"role": "system", "content": "You are a precise OCR engine."},
        {"role": "user", "content": OCR_PROMPT},
    ]

    print("\n" + "=" * 60)
    print(f"OCR AN {model_name} (via chat_completion)")
    print("=" * 60)
    try:
        print(f"Verfügbare Modelle: {select_ocr_model()}")
        content = chat_completion(model_name, messages, config=config, image_bytes=image_bytes)
        print(f"  Länge: {len(content)} Zeichen")
        if content:
            print(f"  Erste 500 Zeichen:\n{content[:500]}")
        else:
            print("  (leere Antwort)")
    except Exception as e:
        print(f"  FEHLER: {e}")

    # Aufräumen
    Path(png_path).unlink(missing_ok=True)

    print("\n" + "=" * 60)
    print("DIAGNOSE ABGESCHLOSSEN")
    print("=" * 60)


if __name__ == "__main__":
    main()
