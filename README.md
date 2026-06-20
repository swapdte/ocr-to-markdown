# ocr-to-markdown

Python-CLI-Tool zur Konvertierung von Bild- und PDF-Dateien in formatiertes Markdown mittels lokaler OCR (LM Studio).

## Funktionen

- **Image to Markdown**: OCR von PNG, JPG, JPEG Dateien
- **PDF to Markdown**: Mehrseitige PDFs werden automatisch seitenweise verarbeitet
- **PDF-only Modelle**: Bilder werden automatisch zu PDF konvertiert (via ImageMagick)
- **Jinja Chat-Template**: Qwen2.5-VL kompatibles Template mit Bild-Injektion
- **PDF-Textebene**: Bei PDF-Input wird der OCR-Text als unsichtbare, durchsuchbare Textebene in die Quell-PDF eingefügt
- **TUI-Dateiauswahl**: Interaktive Dateiauswahl mit Ordnernavigation
- **Automatische Spracherkennung**: Deutsch, Englisch, Französisch, Spanisch
- **Markdown-Formatierung**: Überschriften, Listen, Fettdruck, Kursiv, Tabellen
- **Nachbearbeitung**: Optionale Rechtschreib- und Formatierungskorrektur via `-d` Flag
- **Tabellenkonvertierung**: HTML-Tabellen in .md Dateien zu Markdown-Tabellen umwandeln via `-t` Flag

## Voraussetzungen

- Python >= 3.10
- [uv](https://docs.astral.sh/uv/) als Paketmanager
- [LM Studio](https://lmstudio.ai/) mit geladenen Modellen
- `pdftoppm` (Teil von poppler-utils) für PDF-Verarbeitung
- `magick` (ImageMagick) für Bild-zu-PDF-Konvertierung bei PDF-only Modellen

### OCR-Modelle (Prioritätsreihenfolge)

1. `nanonets-ocr-s` (PDF-only, Bild-zu-PDF Konvertierung automatisch)
2. `allenai/olmocr-2-7b`
3. `gemma-4-e4b-it`
4. `gemma-4-e2b-it`
5. `qwen3.5-9b` (Fallback)

### Tabellenkonvertierung (-t Flag)

- Erfordert `gemma-4-e4b-it` in LM Studio

## Installation

```bash
# Projekt klonen
git clone https://marckerkmann.de/forgejo/marc/ocr-to-markdown.git
cd ocr-to-markdown

# Als uv Tool installieren
uv tool install --force .
```

Nach der Installation steht der Befehl `ocr-to-markdown` systemweit zur Verfügung.

### Aktualisierung

```bash
cd ocr-to-markdown
git pull
uv tool install --force .
```

### Deinstallation

```bash
uv tool uninstall ocr-to-markdown
```

## Nutzung

```bash
# Interaktive Dateiauswahl
ocr-to-markdown

# Mit Verzeichnis starten
ocr-to-markdown /pfad/zum/ordner

# Mit Nachbearbeitung (Rechtschreibung + Formatierung)
ocr-to-markdown -d

# HTML-Tabellen in .md Datei zu Markdown umwandeln
ocr-to-markdown -t
```

## Konfiguration

### nanonets-ocr-s

Das Modell `nanonets-ocr-s` (basierend auf Qwen2.5-VL-3B-Instruct) ist ein PDF-only Modell. Bilder werden automatisch via ImageMagick `magick` zu PDF konvertiert.

Die Modellkonfiguration wird über die LM Studio Python SDK API übertragen:

| Parameter | Wert |
|-----------|------|
| System Prompt | `You are a precise OCR engine.` |
| Temperature | 0 |
| Repeat Penalty | 1.05 |
| Top-P Sampling | 1 |
| Top-K Sampling | -1 |
| Min-P Sampling | 0 |
| Max Tokens | 1500 |
| Seed | 3502 |
| Stop Strings | `<\|im_start\|>`, `<\|im_end\|>` |

Das Jinja Chat-Template (Qwen2.5-VL ChatML) wird über die API als `promptTemplate` übertragen und enthält Bild-Injektionstoken (`<|vision_start|><|image_pad|><|vision_end|>`) sowie den OCR-Prompt.

### Referenzdateien

- `ocr.preset.json` — LM Studio Preset mit allen Modellparametern
- `jinja-lmstudio` — Jinja Chat-Template für LM Studio
- `template` — Go-Template Variante (Referenz)
- `system` — System-Prompt
- `params` — Modellparameter als JSON

## Ausgabe

- **Markdown-Datei**: `{dateiname}-OCR.md` im aktuellen Arbeitsverzeichnis
- **PDF-Update**: Bei PDF-Input wird die Quell-PDF mit einer unsichtbaren Textebene aktualisiert (Render-Modus 3)
- **Tabellenkonvertierung**: Die ausgewählte .md Datei wird direkt aktualisiert (HTML-Tabellen werden durch Markdown-Tabellen ersetzt)