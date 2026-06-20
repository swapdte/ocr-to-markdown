# OCR to Markdown

Ein CLI-Tool zur Konvertierung von Bildern und PDFs in Markdown mithilfe lokaler OCR-Modelle über [LM Studio](https://lmstudio.ai/).

## Funktionen

- **Bild-OCR**: PNG, JPG, JPEG Dateien werden direkt OCR-gelesen
- **PDF-OCR**: PDFs werden seitenweise zu PNG konvertiert und OCR-verarbeitet
- **Automatische Modellauswahl**: Wählt das beste verfügbare OCR-Modell aus einer Prioritätsliste
- **Modell-spezifische Konfiguration**: Temperatur, Repeat Penalty, Top-P, Jinja-Templates pro Modell
- **Spracherkennung**: Automatische Erkennung von Deutsch, Englisch, Französisch und Spanisch
- **Markdown-Nachbearbeitung**: Rechtschreibung, Formatierung und Duplikate werden korrigiert
- **HTML-zu-Markdown Tabellenkonvertierung**: Nachträgliche Konvertierung von HTML-Tabellen in Markdown (`-t` Flag)
- **PDF-Texteinbettung**: OCR-Text wird optional in die Quell-PDF eingefügt
- **TUI-Dateiauswahl**: Interaktive Dateiauswahl mit [questionary](https://github.com/tmbo/questionary)
- **Fortschrittsanzeige**: Visuelle Fortschrittsanzeige mit [rich](https://github.com/Textualize/rich)

## Voraussetzungen

- **Python 3.10+**
- **LM Studio** — Lokaler LLM-Server, läuft auf `127.0.0.1:1234`
- **pdftoppm** — PDF-zu-PNG Konvertierung (Teil von [poppler-utils](https://poppler.freedesktop.org/))
- **ImageMagick** — Bildverarbeitung (`magick`-Befehl, für Bild-Resize)

### Empfohlene OCR-Modelle

Lade eines oder mehrere der folgenden Modelle in LM Studio herunter:

| Priorität | Modell | Hinweis |
|-----------|--------|---------|
| 1 | [nanonets-ocr-s](https://huggingface.co/unsloth/Nanonets-OCR-s-GGUF) | Bestes OCR-Ergebnis, benötigt Jinja-Template |
| 2 | [allenai/olmocr-2-7b](https://huggingface.co/allenai/olmocr-2-7b) | Gute Alternative |
| 3 | [gemma-4-e4b-it](https://huggingface.co/unsloth/gemma-4-E4B-it-GGUF) | Allzweck-Modell |
| 4 | [gemma-4-e2b-it](https://huggingface.co/) | Kleineres Allzweck-Modell |
| 5 | [qwen3.5-9b](https://huggingface.co/unsloth/Qwen3.5-9B-GGUF) | Fallback |

Das erste verfügbare Modell aus der Liste wird automatisch ausgewählt.

## Installation

### Mit uv (empfohlen)

```bash
uv tool install .
```

### Mit pip

```bash
pip install .
```

### Entwicklung

```bash
# Virtuelle Umgebung erstellen
python -m venv .venv
source .venv/bin/activate

# Abhängigkeiten installieren
pip install -e .
```

## Verwendung

### Einfacher Aufruf

```bash
ocr-to-markdown
```

Startet die TUI-Dateiauswahl im aktuellen Verzeichnis.

### Mit Startverzeichnis

```bash
ocr-to-markdown /pfad/zum/verzeichnis
```

### Mit Dateipfad

```bash
ocr-to-markdown /pfad/zur/datei.png
```

### HTML-zu-Markdown Tabellenkonvertierung

```bash
ocr-to-markdown -t
```

Konvertiert HTML-Tabellen in einer bestehenden Markdown-Datei zu Markdown-Tabellen.

### Debug-Modus

```bash
ocr-to-markdown -d
```

Aktiviert zusätzliche Debug-Ausgabe.

## Konfiguration

### Modell-Prioritätsliste

Die Prioritätsliste der Modelle wird in `MODEL_PREFERENCES` in `ocr_to_markdown.py` definiert:

```python
MODEL_PREFERENCES = [
    "nanonets-ocr-s",
    "allenai/olmocr-2-7b",
    "gemma-4-e4b-it",
    "gemma-4-e2b-it",
    "qwen3.5-9b",
]
```

### Modell-spezifische Konfiguration

Jedes Modell kann eigene Vorhersage-Parameter haben:

```python
MODEL_CONFIGS = {
    "nanonets-ocr-s": {
        "temperature": 0,
        "repeatPenalty": 1.05,
        "minPSampling": 0,
        "topPSampling": 1,
        "topKSampling": -1,
        "stopStrings": ["<|im_start|>", "<|im_end|>"],
        "promptTemplate": {
            "type": "jinja",
            "stopStrings": ["<|im_start|>", "<|im_end|>"],
            "jinjaPromptTemplate": {
                "template": NANONETS_JINJA_TEMPLATE,
            },
        },
    },
}
```

### LM Studio Verbindung

Standardmäßig verbindet sich das Tool mit LM Studio auf `127.0.0.1:1234`. Die Konfiguration kann in `ocr_to_markdown.py` angepasst werden:

```python
LMSTUDIO_HOST = "127.0.0.1:1234"
LMSTUDIO_CONTEXT_LENGTH = 20000
LMSTUDIO_SEED = 3502
```

## Wie es funktioniert

### Bildverarbeitung

1. Bild wird ggf. verkleinert (max. 1024px)
2. Bild wird als temporäre PNG-Datei gespeichert
3. LM Studio Modell wird geladen (mit Modell-spezifischer Konfiguration)
4. Bild wird über `prepare_image()` an das Modell gesendet
5. OCR-Ergebnis wird nachbearbeitet (Rechtschreibung, Formatierung, Duplikate)
6. Sprache wird automatisch erkannt
7. Ergebnis wird als Markdown gespeichert

### PDF-Verarbeitung

1. PDF wird mit `pdftoppm` zu PNG-Seiten konvertiert
2. Jede Seite wird einzeln OCR-verarbeitet (wie Bildverarbeitung)
3. Ergebnisse werden zusammengeführt
4. OCR-Text wird optional in die Quell-PDF eingefügt

### Jinja-Template für nanonets-ocr-s

Das Modell `nanonets-ocr-s` (basierend auf Qwen2.5-VL) benötigt ein spezielles Jinja-Chat-Template mit Vision-Tokens (`<|vision_start|><|image_pad|><|vision_end|>`), damit Bilder korrekt an das Modell übergeben werden. Dieses Template ist in `NANONETS_JINJA_TEMPLATE` definiert und wird über `MODEL_CONFIGS` automatisch angewendet.

## Abhängigkeiten

| Paket | Zweck |
|-------|-------|
| [lmstudio](https://github.com/lmstudio-ai/lmstudio-python) | LM Studio Python SDK |
| [questionary](https://github.com/tmbo/questionary) | TUI-Dateiauswahl |
| [rich](https://github.com/Textualize/rich) | Fortschrittsanzeige und Konsolenausgabe |
| [pymupdf](https://github.com/pymupdf/PyMuPDF) | PDF-Verarbeitung (Text einbetten) |
| [pillow](https://python-pillow.org/) | Bildverarbeitung (Resize) |

## Lizenz

Dieses Projekt steht unter der [MIT-Lizenz](LICENSE).

## Autoren

- **Marc Kerkmann** — [marc@kerkmann.dev](mailto:marc@kerkmann.dev)
- **opencode** — Co-Autor