# glm-ocr-skripte

Python-CLI-Tool zur Konvertierung von Bild- und PDF-Dateien in formatiertes Markdown mittels lokaler OCR (LM Studio).

## Funktionen

- **Image to Markdown**: OCR von PNG, JPG, JPEG Dateien
- **PDF to Markdown**: Mehrseitige PDFs werden automatisch seitenweise verarbeitet
- **PDF-Textebene**: Bei PDF-Input wird der OCR-Text als unsichtbare, durchsuchbare Textebene in die Quell-PDF eingefuegt
- **TUI-Dateiauswahl**: Interaktive Dateiauswahl mit Ordnernavigation
- **Automatische Spracherkennung**: Deutsch, Englisch, Franzoesisch, Spanisch
- **Markdown-Formatierung**: Ueberschriften, Listen, Fettdruck, Kursiv, Tabellen
- **Nachbearbeitung**: Optionale Rechtschreib- und Formatierungskorrektur via `-d` Flag

## Voraussetzungen

- Python >= 3.10
- [uv](https://docs.astral.sh/uv/) als Paketmanager
- [LM Studio](https://lmstudio.ai/) mit einem geladenen Vision-Modell (z.B. `allenai/olmocr-2-7b`, `gemma-4-e4b-it`, `qwen3.5-9b`)
- `pdftoppm` (Teil von poppler-utils) fuer PDF-Verarbeitung

## Installation

```bash
uv tool install --force .
```

## Nutzung

```bash
# Interaktive Dateiauswahl
ocr-to-markdown

# Mit Verzeichnis starten
ocr-to-markdown /pfad/zum/ordner

# Mit Nachbearbeitung (Rechtschreibung + Formatierung)
ocr-to-markdown -d
```

## Bevorzugte OCR-Modelle (Prioritaetsreihenfolge)

1. `allenai/olmocr-2-7b`
2. `gemma-4-e4b-it`
3. `gemma-4-e2b-it`
4. `qwen3.5-9b` (Fallback)

## Ausgabe

- **Markdown-Datei**: `{dateiname}-OCR.md` im aktuellen Arbeitsverzeichnis
- **PDF-Update**: Bei PDF-Input wird die Quell-PDF mit einer unsichtbaren Textebene aktualisiert (Render-Modus 3)
