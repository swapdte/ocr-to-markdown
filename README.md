# OCR to Markdown

Ein CLI-Tool zur Konvertierung von Bildern und PDFs in Markdown mithilfe lokaler OCR-Modelle über [koboldcpp](https://github.com/LostRuins/koboldcpp) (OpenAI-kompatible API).

## Funktionen

- **Bild-OCR**: PNG, JPG, JPEG Dateien werden direkt OCR-gelesen
- **PDF-OCR**: PDFs werden seitenweise zu PNG konvertiert und OCR-verarbeitet
- **Automatische Modellauswahl**: Wählt das beste verfügbare OCR-Modell aus einer Prioritätsliste
- **Modell-spezifische Konfiguration**: Sampler-Parameter (Temperatur, Repeat Penalty, Top-P, Seed) pro Modell
- **Spracherkennung**: Automatische Erkennung von Deutsch, Englisch, Französisch und Spanisch
- **Markdown-Nachbearbeitung**: Rechtschreibung, Formatierung und Duplikate werden korrigiert
- **HTML-zu-Markdown Tabellenkonvertierung**: Nachträgliche Konvertierung von HTML-Tabellen in Markdown (`-t` Flag)
- **PDF-Texteinbettung**: OCR-Text wird optional in die Quell-PDF eingefügt
- **TUI-Dateiauswahl**: Interaktive Dateiauswahl mit [questionary](https://github.com/tmbo/questionary)
- **Fortschrittsanzeige**: Visuelle Fortschrittsanzeige mit [rich](https://github.com/Textualize/rich)

## Voraussetzungen

- **Python 3.10+**
- **koboldcpp** — Lokaler LLM-Server mit OpenAI-kompatibler API auf `http://localhost:5001/v1`. Lädt Modelle automatisch und entlädt sie nach 600 Sekunden Inaktivität
- **pdftoppm** — PDF-zu-PNG Konvertierung (Teil von [poppler-utils](https://poppler.freedesktop.org/))
- **ImageMagick** — Bildverarbeitung (`magick`-Befehl, für Bild-Resize)

### Empfohlene OCR-Modelle

Lade eines oder mehrere der folgenden Modelle in koboldcpp (als Modell-Dateien im koboldcpp-Modellordner):

| Priorität | Modell | Hinweis |
|-----------|--------|---------|
| 1 | [nanonets-ocr-s](https://huggingface.co/unsloth/Nanonets-OCR-s-GGUF) | Bestes OCR-Ergebnis |
| 2 | [allenai/olmocr-2-7b](https://huggingface.co/allenai/olmocr-2-7b) | Gute Alternative |
| 3 | [gemma-4-e4b-it](https://huggingface.co/unsloth/gemma-4-E4B-it-GGUF) | Allzweck-Modell |
| 4 | [gemma-4-e2b-it](https://huggingface.co/unsloth/gemma-4-E2B-it-GGUF) | Kleineres Allzweck-Modell |
| 5 | [qwen3.5-9b](https://huggingface.co/unsloth/Qwen3.5-9B-GGUF) | Fallback |

Das erste verfügbare Modell aus der Liste wird automatisch ausgewählt. Die Auswahl erfolgt über die `/v1/models`-API von koboldcpp — gesendet wird dabei immer die **echte Modell-ID** (Dateiname, z.B. `nanonets-ocr.kcpps`), nicht der Präferenzname. Nur so bleibt das geladene Modell über mehrere Bilder hinweg aktiv, statt bei jedem Request neu geladen zu werden.

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

Jedes Modell kann eigene Sampler-Parameter haben (OpenAI-Namen, werden direkt an die koboldcpp-API übergeben):

```python
MODEL_CONFIGS = {
    "nanonets-ocr-s": {
        "temperature": 0,
        "repetition_penalty": 1.05,
        "min_p": 0,
        "top_p": 1,
        "top_k": -1,  # -1 = deaktiviert
        "seed": KOBOLDCPP_SEED,
        "max_tokens": 4096,
    },
}
```

### koboldcpp Verbindung

Standardmäßig verbindet sich das Tool mit koboldcpp auf `http://localhost:5001/v1` (OpenAI-kompatible API). Die Konfiguration kann in `ocr_to_markdown.py` angepasst werden:

```python
KOBOLDCPP_API_BASE = "http://localhost:5001/v1"
KOBOLDCPP_SEED = 3502
```

koboldcpp lädt Modelle bei Bedarf automatisch und entlädt sie nach 600 Sekunden Inaktivität (Server-Einstellung `--adminunloadtimeout`) — das Tool selbst verwaltet kein Laden/Entladen mehr. Voraussetzung für ein geladen bleibendes Modell: Jeder Request muss die exakte Modell-ID (Dateiname) verwenden — das übernimmt das Tool automatisch.

## Wie es funktioniert

### Bildverarbeitung

1. Bild wird ggf. verkleinert (max. 1024px)
2. Bild wird als base64 `image_url` direkt an die koboldcpp-API gesendet
3. koboldcpp lädt das gewählte Modell automatisch (mit Modell-spezifischer Konfiguration)
4. OCR-Ergebnis wird nachbearbeitet (Rechtschreibung, Formatierung, Duplikate)
5. Sprache wird automatisch erkannt
6. Ergebnis wird als Markdown gespeichert

### PDF-Verarbeitung

1. PDF wird mit `pdftoppm` zu PNG-Seiten konvertiert
2. Jede Seite wird einzeln OCR-verarbeitet (wie Bildverarbeitung)
3. Ergebnisse werden zusammengeführt
4. OCR-Text wird optional in die Quell-PDF eingefügt

## Abhängigkeiten

| Paket | Zweck |
|-------|-------|
| [questionary](https://github.com/tmbo/questionary) | TUI-Dateiauswahl |
| [rich](https://github.com/Textualize/rich) | Fortschrittsanzeige und Konsolenausgabe |
| [pymupdf](https://github.com/pymupdf/PyMuPDF) | PDF-Verarbeitung (Text einbetten) |
| [pillow](https://python-pillow.org/) | Bildverarbeitung (Resize) |

Die Kommunikation mit koboldcpp erfolgt über die OpenAI-kompatible API mit der Python-Standardbibliothek (`urllib`) — keine zusätzliche Abhängigkeit nötig.

## Lizenz

Dieses Projekt steht unter der [MIT-Lizenz](LICENSE).

## Autoren

- **Marc Kerkmann**
- **opencode** — Co-Autor