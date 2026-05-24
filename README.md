# ocr-to-markdown

Python-CLI-Tool zur Konvertierung von Bild- und PDF-Dateien in formatiertes Markdown mittels lokaler OCR (LM Studio).

## Funktionen

- **Image to Markdown**: OCR von PNG, JPG, JPEG Dateien
- **PDF to Markdown**: Mehrseitige PDFs werden automatisch seitenweise verarbeitet
- **PDF-Textebene**: Bei PDF-Input wird der OCR-Text als unsichtbare, durchsuchbare Textebene in die Quell-PDF eingefuegt
- **TUI-Dateiauswahl**: Interaktive Dateiauswahl mit Ordnernavigation
- **Automatische Spracherkennung**: Deutsch, Englisch, Franzoesisch, Spanisch
- **Markdown-Formatierung**: Ueberschriften, Listen, Fettdruck, Kursiv, Tabellen
- **Nachbearbeitung**: Optionale Rechtschreib- und Formatierungskorrektur via `-d` Flag
- **Tabellenkonvertierung**: HTML-Tabellen in .md Dateien zu Markdown-Tabellen umwandeln via `-t` Flag

## Voraussetzungen

- Python >= 3.10
- [uv](https://docs.astral.sh/uv/) als Paketmanager
- [LM Studio](https://lmstudio.ai/) mit geladenen Modellen
- `pdftoppm` (Teil von poppler-utils) fuer PDF-Verarbeitung

### OCR-Modelle (Prioritaetsreihenfolge)

1. `allenai/olmocr-2-7b`
2. `gemma-4-e4b-it`
3. `gemma-4-e2b-it`
4. `qwen3.5-9b` (Fallback)

### Tabellenkonvertierung (-t Flag)

- Erfordert `gemma-4-e4b-it` in LM Studio

## Installation

```bash
# Projekt klonen
git clone https://github.com/swapdte/ocr-to-markdown.git
cd ocr-to-markdown

# Als uv Tool installieren
uv tool install --force .
```

Nach der Installation steht der Befehl `ocr-to-markdown` systemweit zur Verfuegung.

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

## Ausgabe

- **Markdown-Datei**: `{dateiname}-OCR.md` im aktuellen Arbeitsverzeichnis
- **PDF-Update**: Bei PDF-Input wird die Quell-PDF mit einer unsichtbaren Textebene aktualisiert (Render-Modus 3)
- **Tabellenkonvertierung**: Die ausgewaehlte .md Datei wird direkt aktualisiert (HTML-Tabellen werden durch Markdown-Tabellen ersetzt)
