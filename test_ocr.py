#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Diagnose-Skript 2: Testet ob PNG-Bilder (statt PDF) funktionieren.
Konvertiert PDF zu PNG und sendet das Bild an beide Modelle.
"""

import sys
import subprocess
import tempfile
from pathlib import Path
import lmstudio as lms

LMSTUDIO_HOST = "127.0.0.1:1234"
LMSTUDIO_CONTEXT_LENGTH = 20000

def main():
    pdf_path = sys.argv[1] if len(sys.argv) > 1 else "Jabra Sports_Pace_TechnSpecs_lores.pdf"

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

    client = lms.Client(api_host=LMSTUDIO_HOST)

    # Test 1: PNG an nanonets-ocr-s (obwohl es PDF-only ist)
    print(f"\n{'=' * 60}")
    print("TEST 1: PNG an nanonets-ocr-s")
    print("=" * 60)
    try:
        model = client.llm.model("nanonets-ocr-s", ttl=None, config={"contextLength": LMSTUDIO_CONTEXT_LENGTH})
        img_handle = client.prepare_image(src=png_path)
        print(f"  Image handle: {repr(img_handle)}")
        chat = lms.Chat("You are a precise OCR engine.")
        chat.add_user_message("Extract the text from the above document as if you were reading it naturally. Return the all text and tables in markdown format.", images=[img_handle])
        result = model.respond(chat)
        content = result.content
        print(f"  Länge: {len(content)} Zeichen")
        if content:
            print(f"  Erste 500 Zeichen:\n{content[:500]}")
        else:
            print("  (leere Antwort)")
    except Exception as e:
        print(f"  FEHLER: {e}")

    # Test 2: PNG an gemma-4-e4b-it
    print(f"\n{'=' * 60}")
    print("TEST 2: PNG an gemma-4-e4b-it")
    print("=" * 60)
    try:
        model = client.llm.model("gemma-4-e4b-it", ttl=None, config={"contextLength": LMSTUDIO_CONTEXT_LENGTH})
        img_handle = client.prepare_image(src=png_path)
        print(f"  Image handle: {repr(img_handle)}")
        chat = lms.Chat("You are a precise OCR engine.")
        chat.add_user_message("Extract the text from the above document as if you were reading it naturally. Return the all text and tables in markdown format.", images=[img_handle])
        result = model.respond(chat)
        content = result.content
        print(f"  Länge: {len(content)} Zeichen")
        if content:
            print(f"  Erste 500 Zeichen:\n{content[:500]}")
        else:
            print("  (leere Antwort)")
    except Exception as e:
        print(f"  FEHLER: {e}")

    # Test 3: PDF an nanonets-ocr-s (wie im Hauptskript)
    print(f"\n{'=' * 60}")
    print("TEST 3: PDF an nanonets-ocr-s (Original-Methode)")
    print("=" * 60)
    try:
        model = client.llm.model("nanonets-ocr-s", ttl=None, config={"contextLength": LMSTUDIO_CONTEXT_LENGTH})
        pdf_handle = client.prepare_image(src=pdf_path)
        print(f"  PDF handle: {repr(pdf_handle)}")
        chat = lms.Chat("You are a precise OCR engine.")
        chat.add_user_message("Extract the text from the above document as if you were reading it naturally. Return the all text and tables in markdown format.", images=[pdf_handle])
        result = model.respond(chat)
        content = result.content
        print(f"  Länge: {len(content)} Zeichen")
        if content:
            print(f"  Erste 500 Zeichen:\n{content[:500]}")
        else:
            print("  (leere Antwort)")
    except Exception as e:
        print(f"  FEHLER: {e}")

    # Test 4: PNG an nanonets-ocr-s mit Jinja Template
    print(f"\n{'=' * 60}")
    print("TEST 4: PNG an nanonets-ocr-s MIT Jinja Template")
    print("=" * 60)
    try:
        NANONETS_JINJA_TEMPLATE = r"""{%- set image_count = namespace(value=0) -%}
{%- set video_count = namespace(value=0) -%}
{%- set text_count  = namespace(value=0) -%}
{%- for message in messages -%}
	{%- if loop.first and message["role"] != "system" -%}
		{{- "<|im_start|>system\nYou are a precise OCR engine.<|im_end|>\n" -}}
	{%- endif -%}
	{{- "<|im_start|>" -}}
	{{- message["role"] -}}
	{{- "\n" -}}
	{%- if message["content"] is string -%}
		{{- message["content"] -}}
		{{- "<|im_end|>\n" -}}
	{%- else -%}
		{%- set text_count.value = 0 -%}
		{%- for content in message["content"] -%}
			{%- if content["type"] == "image" or "image" in content or "image_url" in content -%}
				{%- set image_count.value = image_count.value + 1 -%}
				{%- if add_vision_id -%}
					{{- "Picture " -}}
					{{- image_count.value -}}
					{{- ": " -}}
				{%- endif -%}
				{{- "<|vision_start|><|image_pad|><|vision_end|>" -}}
			{%- elif content["type"] == "video" or "video" in content -%}
				{%- set video_count.value = video_count.value + 1 -%}
				{%- if add_vision_id -%}
					{{- "Video " -}}
					{{- video_count.value -}}
					{{- ": " -}}
				{%- endif -%}
				{{- "<|vision_start|><|video_pad|><|vision_end|>" -}}
			{%- elif "text" in content -%}
				{{- content["text"]|string -}}
				{%- if content["text"]|length != 0 -%}
					{%- set text_count.value = text_count.value + 1 -%}
				{%- endif -%}
			{%- endif -%}
		{%- endfor -%}
		{%- if text_count.value != 0 -%}
			{{- "\n" -}}
		{%- endif -%}
		{{- "Extract the text from the above document as if you were reading it naturally. Return the all text and tables in markdown format." -}}
		{{- "<|im_end|>\n" -}}
	{%- endif -%}
{%- endfor -%}
{%- if add_generation_prompt -%}
	{{- "<|im_start|>assistant\n" -}}
{%- endif -%}"""
        model = client.llm.model("nanonets-ocr-s", ttl=None, config={"contextLength": LMSTUDIO_CONTEXT_LENGTH})
        img_handle = client.prepare_image(src=png_path)
        chat = lms.Chat("You are a precise OCR engine.")
        chat.add_user_message("Extract the text from the above document as if you were reading it naturally. Return the all text and tables in markdown format.", images=[img_handle])
        config = {
            "temperature": 0,
            "repeatPenalty": 1.05,
            "stopStrings": ["<|im_start|>", "<|im_end|>"],
            "promptTemplate": {
                "type": "jinja",
                "stopStrings": ["<|im_start|>", "<|im_end|>"],
                "jinjaPromptTemplate": {
                    "template": NANONETS_JINJA_TEMPLATE,
                },
            },
        }
        result = model.respond(chat, config=config)
        content = result.content
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