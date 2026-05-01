#!/usr/bin/env python3
"""
v1.7.4 - OCR zu Markdown Konverter mit TUI-Dateiauswahl

Verwendet ein LLM (via LM Studio) um Bilddateien und PDFs zu OCR-lesen
und als Markdown mit Tabellen-Formatierung auszugeben.
Der OCR-Text wird nachbearbeitet fuer bessere Formatierung und Rechtschreibung.

Funktionen:
- Unterstuetzt PNG, JPG, JPEG und PDF Dateien
- Automatische Seiten-Erkennung bei PDFs (via pdftoppm)
- Automatische Spracherkennung (Deutsch, Englisch, Franzoesisch, Spanisch)
- Markdown-Formatierung mit Tabellen, Listen, Fett/Kursiv
- Nachbearbeitung: Rechtschreibung und Formatierung werden verbessert
- OCR-Text wird bei PDF-Input auch in die Quell-PDF eingefuegt
- TUI-Dateiauswahl mit questionary
- Fortschrittsanzeige mit rich
- Temporaere OCR-Dateien werden automatisch geloescht
"""

import sys
import io
import re
import subprocess
import tempfile
from pathlib import Path

# TUI und Progress-Anzeige
import questionary
from questionary import Style
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn

# OCR und PDF-Verarbeitung
import lmstudio as lms
import fitz
from PIL import Image

# Konsolenausgabe mit Rich
console = Console()

# Erlaubte Dateiformate
ALLOWED_EXTENSIONS = {".png", ".jpg", ".jpeg", ".pdf"}

# Maximale Bildgroesse - nur resize wenn groesser
MAX_IMAGE_SIZE = 1024

# Minimale Zeilenlaenge - kuerzere Zeilen werden ignoriert
# Werte von 2 aufwaerts: 2 erlaubt kurze Tabellenzellen, aber filtert Rauschen
MIN_LINE_LENGTH = 2

# Minimale DPI fuer PDF-Rendering (bessere Qualitaet bei gefalteten Seiten)
MIN_PDF_DPI = 50

# LM Studio Konfiguration
LMSTUDIO_HOST = "127.0.0.1:1234"
LMSTUDIO_TTL = 900  # Modell nach 15 Minuten Inaktivitaet entladen
LMSTUDIO_CONTEXT_LENGTH = 8000  # Kontextfenster in Tokens

# Bevorzugte OCR-Modelle in Prioritaetsreihenfolge
# Das erste verfuegbare Modell aus dieser Liste wird verwendet
MODEL_PREFERENCES = [
    "allenai/olmocr-2-7b",
    "gemma-4-e4b-it",
    "gemma-4-e2b-it",
    "qwen3.5-9b",
]

# Woerter fuer automatische Spracherkennung
LANGUAGE_PATTERNS = {
    "Deutsch": [
        "der",
        "die",
        "das",
        "und",
        "ist",
        "ein",
        "eine",
        "nicht",
        "auf",
        "fuer",
        "mit",
        "von",
        "zu",
        "als",
        "auch",
        "sich",
        "bei",
        "nach",
        "aus",
        "oder",
    ],
    "Englisch": [
        "the",
        "and",
        "is",
        "of",
        "to",
        "a",
        "in",
        "that",
        "it",
        "for",
        "was",
        "on",
        "are",
        "with",
        "as",
        "this",
        "be",
        "at",
        "by",
        "from",
    ],
    "Franzoesisch": [
        "le",
        "la",
        "les",
        "de",
        "du",
        "et",
        "est",
        "en",
        "que",
        "qui",
        "dans",
        "ce",
        "il",
        "pas",
        "ne",
        "sur",
        "se",
        "plus",
        "par",
        "au",
    ],
    "Spanisch": [
        "el",
        "la",
        "los",
        "de",
        "en",
        "que",
        "y",
        "es",
        "un",
        "una",
        "por",
        "con",
        "no",
        "para",
        "al",
        "del",
        "se",
        "lo",
        "su",
        "mas",
    ],
}

# Prompt-Artefakte die aus der OCR-Ausgabe gefiltert werden
PROMPT_ARTEFACTS = [
    "keine wiederholungen",
    "keine erfundenen",
    "erste zeile:",
    "sprache:",
    "regeln:",
    "formatiere als",
    "nutze markdown",
    "ocr:",
    "extrahiere den",
    "sichtbaren text",
    "format als",
    "inline-html-tabelle",
    "zusammenfassung:",
    "erklaerung:",
    "hier ist der text:",
    "hier ist der erkannte",
    "extrahierter text:",
    "gesamtinhalt:",
    "nichts anderes",
    "ausgabe:",
    "absoluten grundregeln",
    "tabellen-regeln",
    "ocr-scanner",
    "erkannter inhalt",
    "ich habe den text",
    "der folgende text wurde",
    "das bild zeigt",
    "ich erkenne folgenden",
]

# Prompt fuer OCR von DIN A4 Dokumenten (Briefe und Rechnungen)
# Deckt komplexe Formatierungen, Tabellen, Handschrift und QR-Codes ab
OCR_PROMPT = """Du bist ein Praezisions-OCR-Scanner. Deine Aufgabe ist es, dieses Bild ZEICHEN FUER ZEICHEN exakt zu transkribieren.

## Absolute Grundregeln
1. JEDER einzelne Buchstabe, JEDER Pixel-Text, JEDER Stempel, JEDER Wasserzeichen-Text muss im Ergebnis enthalten sein. NULL Ausnahmen. Null Kompromisse.
2. Gib NUR den erkannten Text zurueck. Keine Kommentare, keine Erklaerungen.
3. Pruefe das gesamte Bild: horizontalen Text, gedrehten Text (90/180/270 Grad), vertikalen Text, schraegen Text, Signaturen, Stempel, Wasserzeichen, Fussnoten, Randnotizen, Kopfzeilen, Fusszeilen.
4. Zahlen, Betraege, IBANs, Steuernummern, Rechnungsnummern, Datumsformate muessen exakt wie im Original sein. Kein Komma oder Punkt darf hinzugefuegt oder weggelassen werden.
5. Die Ausgabe MUSS gueltiges Markdown sein.
6. Wenn du dir bei einem Zeichen unsicher bist: Gib die bestmoegliche Lesung an. Lass KEIN Zeichen aus. Lieber ein ungenaues Zeichen als gar keins.

## Komplexe Formatierung nachbauen
- Hauptueberschriften: `# Titel`
- Abschnittsueberschriften: `## Abschnitt`
- Unterueberschriften: `### Unterabschnitt`
- Fettdruck: `**wichtiges Wort**`
- Kursiv: *hervorgehoben*
- Unterstrichen: `<u>unterstrichen</u>`
- Durchgestrichen: `~~durchgestrichen~~`
- Aufzaehlungen: `- Eintrag` oder `1. erster Eintrag`
- Trennlinien zwischen logischen Bloecken: `---`
- Absaetze durch eine Leerzeile trennen
- Schriftgroessen: Ueberschriften groesser als Fliesstext, Fussnoten kleiner
- Spaltenlayout: Linker Spalte zuerst, dann rechter Spalte
- Boxen/Rahmen: Umrande Inhalte als Blockquote `>` oder erhalte die visuelle Struktur
- Listen-Einrueckungen: Behalte die Hierarchieebenen bei (verschachtelte Listen)

## Tabellen
Erkenne tabellarische Strukturen (Raster, Linien, Spalten) und formatiere sie als Markdown-Tabelle mit korrekter Formatierung.

Beispiel:
| Artikel | Menge | Einzelpreis | Gesamtpreis |
|---------|-------|-------------|-------------|
| Widget A | 2 | 15,00 EUR | 30,00 EUR |
| Widget B | 1 | 8,50 EUR | 8,50 EUR |
| | | Summe: | 38,50 EUR |

Tabellen-Regeln:
- Jede Tabellenzeile muss die gleiche Anzahl Spalten haben
- Leerzellen als leere Zelle lassen (nicht mit Bindestrich fuellen)
- Verbundene Zellen: Inhalt in die erste Spalte, restliche leer
- Trennzeile nach der Kopfzeile: |---|---|---| (Mindestens 3 Bindestriche pro Spalte)
- Tabellen MUESSEN als Markdown mit | Spalte | Format geschrieben werden

## Handschrift
- Erkenne handschriftliche Notizen, Unterschriften, Randbemerkungen und Stempeltext
- Transkribiere Handschrift so genau wie moeglich
- Setze transkribierte Handschrift IMMER in doppelte Anfuehrungszeichen: "handschriftlicher Text"
- Wenn Handschrift unleserlich ist: Gib bestmoegliche Lesung in "Anfuehrungszeichen" mit [?] fuer unsichere Stellen

## Vollstaendigkeit
- Lies das Bild ZWEI MAL bevor du ausgibst: Erst grobe Uebersicht, dann zeichenweise Pruefung
- Kein Absatz, keine Zeile, kein Wort darf im Original vorhanden aber im Ergebnis fehlen
- Ueberpruefe besonders: Zahlen in Tabellen, IBAN-Zeichenketten, Bruchzahlen, hochgestellte Zeichen (m2, m3, etc.)
- Wenn Text unleserlich ist: Gib die bestmoegliche Interpretation mit [?] markiert an. Lass NICHTS komplett weg.

## WICHTIG
- Beginne sofort mit dem ersten erkannten Zeichen. Keine Einleitung.
- Beende mit dem letzten erkannten Zeichen. Keine Zusammenfassung.
- Kein einziges Zeichen im Original darf im Ergebnis fehlen."""

# Fallback-Prompt fuer schwierige Faelle
FALLBACK_PROMPT = """Gib den gesamten sichtbaren Text aus. Keine Formatierung."""

# Prompt fuer die Nachbearbeitung des OCR-Textes
REFINEMENT_PROMPT = """Du bist ein Lektor. Verbessere den folgenden OCR-Text.

DEINE AUFGABE:
1. Korrigiere Rechtschreib- und Tippfehler die durch die OCR entstanden sind
2. Verbessere die Markdown-Formatierung: Ueberschriften, Listen, Fettdruck, Kursiv
3. Sorge fuer konsistente Formatierung im gesamten Dokument
4. Formatiere ALLE Tabellen als Markdown-Tabellen mit | Spalte | Format und korrekter Trennzeile |---|---|
5. Aendere keinen Inhalt, keine Woerter und keine Zahlen - nur Korrekturen die eindeutig OCR-Fehler sind
6. Erhalte die Tabellenstruktur: gleiche Anzahl Spalten pro Zeile, keine Zeile weglassen

AUSGABE: Nur den verbesserten Text. Keine Kommentare, keine Erklaerung was du geaendert hast."""


def get_files_in_directory(directory: Path) -> list[Path]:
    """Sammle alle unterstuetzten Dateien im Verzeichnis.

    Args:
        directory: Das zu durchsuchende Verzeichnis.

    Returns:
        Liste mit Path-Objekten fuer alle unterstuetzten Bild/PDF-Dateien.
    """
    # Alle Dateien im Verzeichnis einsammeln, sortiert nach Namen
    files = []
    for f in sorted(directory.iterdir()):
        # Nur reguläre Dateien mit erlaubter Endung beruecksichtigen
        if f.is_file() and f.suffix.lower() in ALLOWED_EXTENSIONS:
            files.append(f)
    return files


def select_file(start_dir: Path) -> Path | None:
    """Zeige TUI zur Dateiauswahl und gib gewaehlten Pfad zurueck.

    Zeigt eine interaktive TUI mit Fragezeichen-Bibliothek, die es dem Benutzer
    erlaubt, durch Verzeichnisse zu navigieren und eine Datei auszuwaehlen.

    Args:
        start_dir: Das Startverzeichnis fuer die Dateiauswahl.

    Returns:
        Der ausgewaehlte Dateipfad oder None wenn abgebrochen.
    """
    # Benutzerdefinierter Stil fuer questionary
    custom_style = Style(
        [
            ("qmark", "fg:cyan bold"),
            ("question", "fg:white bold"),
            ("answer", "fg:green bold"),
            ("pointer", "fg:cyan bold"),
            ("highlighted", "fg:cyan bold"),
            ("selected", "fg:green"),
            ("separator", "fg:gray"),
            ("instruction", "fg:gray"),
            ("text", "fg:white"),
        ]
    )

    files = get_files_in_directory(start_dir)

    # Wenn keine Dateien: Ordner-Navigation anbieten
    if not files:
        subdirs = sorted([d for d in start_dir.iterdir() if d.is_dir()])
        if subdirs:
            subdir = questionary.select(
                "Keine Dateien gefunden. Waehle einen Unterordner:",
                choices=[str(d.name) for d in subdirs] + ["[..] Uebergeordnet"],
                style=custom_style,
            ).ask()

            if subdir is None:
                return None

            if subdir == "[..] Uebergeordnet":
                return select_file(start_dir.parent)
            return select_file(start_dir / subdir)
        else:
            console.print("[red]Keine Dateien gefunden![/red]")
            return None

    # Dateiliste mit Groessenangabe erstellen
    file_choices = []
    for f in files:
        size = f.stat().st_size
        if size < 1024:
            size_str = f"{size} B"
        elif size < 1024 * 1024:
            size_str = f"{size / 1024:.1f} KB"
        else:
            size_str = f"{size / (1024 * 1024):.1f} MB"

        file_choices.append(
            {"name": f.name, "display": f"{f.name} ({size_str})", "path": f}
        )

    choices = [fc["display"] for fc in file_choices] + ["[Ordner wechseln]"]

    selected = questionary.select(
        "Waehle eine Datei:",
        choices=choices,
        style=custom_style,
    ).ask()

    # Ordner wechseln oder abbrechen
    if selected is None or selected == "[Ordner wechseln]":
        subdirs = sorted([d for d in start_dir.iterdir() if d.is_dir()])
        if subdirs:
            subdir = questionary.select(
                "Waehle einen Ordner:",
                choices=[str(d.name) for d in subdirs] + ["[..] Uebergeordnet"],
                style=custom_style,
            ).ask()

            if subdir is None:
                return None

            if subdir == "[..] Uebergeordnet":
                return select_file(start_dir.parent)
            return select_file(start_dir / subdir)
        # Keine Subdirs: zum Parent gehen wenn moeglich
        if start_dir.parent != start_dir:
            return select_file(start_dir.parent)
        return None

    # Richtige Datei aus Mapping finden
    for fc in file_choices:
        if fc["display"] == selected:
            return fc["path"]

    return None


def resize_if_needed(image_bytes: bytes, max_size: int = MAX_IMAGE_SIZE) -> bytes:
    """Resize Bild nur wenn es groesser als max_size ist.

    Reduziert die Bildgroesse fuer eine schnellere OCR-Verarbeitung,
    aber nur wenn es wirklich noetig ist. Beibehaltung der Seitenverhaeltnisse.

    Args:
        image_bytes: Die Bilddaten als Bytes.
        max_size: Maximale Breite/Hoehe in Pixel.

    Returns:
        Die (moeglichst unveraenderten) Bilddaten als Bytes.
    """
    img = Image.open(io.BytesIO(image_bytes))

    # Kein resize noetig
    if img.width <= max_size and img.height <= max_size:
        return image_bytes

    # RGBA zu RGB konvertieren (weisser Hintergrund)
    if img.mode == "RGBA":
        background = Image.new("RGB", img.size, (255, 255, 255))
        background.paste(img, mask=img.split()[3])
        img = background
    elif img.mode != "RGB":
        img = img.convert("RGB")

    # Proportionales resize
    img.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)

    # Als PNG zurueckgeben
    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    return buffer.getvalue()


def render_pdf_page(
    page, max_size: int = MAX_IMAGE_SIZE, min_dpi: int = MIN_PDF_DPI
) -> bytes:
    """Rendere PDF-Seite mit mindestens min_dpi fuer bessere Qualitaet.

    Diese Funktion wird aktuell nicht verwendet (pdftoppm wird bevorzugt),
    aber ist fuer zukuenftige Erweiterungen verfuegbar.

    Args:
        page: Die PyMuPDF-Seite.
        max_size: Maximale Ausgabegroesse in Pixel.
        min_dpi: Minimale DPI fuer das Rendering.

    Returns:
        Die gerenderte Seite als PNG-Bytes.
    """
    rect = page.rect
    pdf_dpi = 72  # PDF Standard-DPI

    # Mindestens min_dpi erreichen
    min_scale = min_dpi / pdf_dpi

    # Maximale Groesse nicht ueberschreiten
    if rect.width * min_scale > max_size or rect.height * min_scale > max_size:
        # Scale begrenzen auf max_size
        scale = min(max_size / rect.width, max_size / rect.height)
    else:
        # Mindest-DPI verwenden
        scale = min_scale

    mat = fitz.Matrix(scale, scale)
    pix = page.get_pixmap(matrix=mat)
    return pix.tobytes("png")


def has_table_structure(text: str) -> bool:
    """Pruefe ob Text Tabellen-Struktur enthaelt (Pipe-Zeichen oder Tabulatoren).

    Wird verwendet um zu erkennen, ob das OCR-Ergebnis potenzielle Tabellen
    enthaelt. Mehrere Zeilen mit | oder Tabs gelten als Indikator.

    Args:
        text: Der zu pruefende Text.

    Returns:
        True wenn der Text Tabellen-Struktur enthaelt.
    """
    lines = text.strip().split("\n")

    table_line_count = 0
    for line in lines:
        # Pipe-Zeichen fuer Markdown-Tabellen
        if line.count("|") >= 2:
            table_line_count += 1
        # Viele Tabulatoren (Spalten-Trenner)
        elif line.count("\t") >= 2:
            table_line_count += 1

    # Tabelle wahrscheinlich wenn mehrere Zeilen mit Tabellen-Struktur
    return table_line_count >= 2


def detect_language(text: str) -> str:
    """Erkenne Sprache automatisch anhand haeufiger Woerter.

    Vergleicht den Text mit bekannten Woertern verschiedener Sprachen
    und gibt die wahrscheinlichste Sprache zurueck.

    Args:
        text: Der zu analysierende Text.

    Returns:
        Der Name der erkannten Sprache oder "Unbekannt".
    """
    # Text in Kleinbuchstaben umwandeln, mit Leerzeichen umschlossen
    # um Ganz-Wort-Treffer zu ermoeglichen (keine Teilwoerter)
    text_lower = f" {text.lower()} "

    # Punkte fuer jede Sprache berechnen: wie viele typische Woerter gefunden
    scores = {}
    for lang, words in LANGUAGE_PATTERNS.items():
        score = 0
        for word in words:
            if f" {word} " in text_lower:
                score += 1
        scores[lang] = score

    # Sprache mit hoechstem Score zurueckgeben
    if scores:
        best_lang = max(scores, key=lambda k: scores[k])
        if scores[best_lang] > 0:
            return best_lang

    return "Unbekannt"


def clean_ocr_output(text: str) -> str:
    """Entferne Prompt-Artefakte aus der OCR-Ausgabe.

    Der OCR-LLM kann manchmal Teile des Prompts in die Ausgabe
    einfuegen. Diese Funktion filtert solche unerwuenschten
    Textbausteine heraus.

    Args:
        text: Der rohe OCR-Text.

    Returns:
        Der bereinigte Text ohne Prompt-Artefakte.
    """
    lines = text.split("\n")
    cleaned = []

    for line in lines:
        keep = True
        line_lower = line.lower().strip()

        # Leere Zeilen immer behalten
        if not line_lower:
            cleaned.append(line)
            continue

        # Pruefe ob Zeile ein Prompt-Artefakt enthaelt
        for artifact in PROMPT_ARTEFACTS:
            if artifact in line_lower:
                # Zeile nur entfernen wenn sie KURZ ist (wahrscheinlich Prompt-Rest)
                if len(line_lower) < 80:
                    keep = False
                    break

        if keep:
            cleaned.append(line)

    return "\n".join(cleaned)


def remove_all_duplicates(text: str) -> str:
    """Entferne alle doppelten Zeilen im gesamten Dokument.

    Manchmal gibt der OCR-LLM Text mehrfach aus. Diese Funktion
    entfernt Duplikate und behält nur die erste Instanz.

    Args:
        text: Der zu bereinigende Text.

    Returns:
        Der Text ohne doppelte Zeilen.
    """
    lines = text.split("\n")
    seen = set()
    result = []

    for line in lines:
        stripped = line.strip()
        # Zeile hinzufuegen wenn noch nicht gesehen (Leerzeilen immer behalten)
        if stripped not in seen or not stripped:
            seen.add(stripped)
            result.append(line)

    return "\n".join(result)


def filter_short_lines(text: str, min_length: int = MIN_LINE_LENGTH) -> str:
    """Entferne Zeilen mit weniger als min_length Zeichen.

    Sehr kurze Zeilen sind oft OCR-Fehler oder Artefakte.
    Diese Funktion filtert sie heraus.

    Args:
        text: Der zu bereinigende Text.
        min_length: Minimale Zeilenlaenge die behalten wird.

    Returns:
        Der gefilterte Text.
    """
    lines = text.split("\n")
    filtered = []

    for line in lines:
        stripped = line.strip()
        # Behalte Zeilen die lang genug sind oder leer sind
        if len(stripped) >= min_length or not stripped:
            filtered.append(line)

    return "\n".join(filtered)


def select_ocr_model(client: lms.Client) -> str:
    """Waehle das beste verfuegbare OCR-Modell und entlade es bei Bedarf.

    Prueft welche der bevorzugten Modelle (MODEL_PREFERENCES) in LM Studio
    heruntergeladen sind und waehlt das Modell mit hoechster Prioritaet.
    Falls das Modell bereits geladen ist, wird es zuerst entladen um einen
    sauberen OCR-Durchlauf zu garantieren.

    Args:
        client: Verbundener LM Studio Client.

    Returns:
        Die Modellkennung des ausgewaehlten Modells.
    """
    # Alle heruntergeladenen Modelle abrufen
    downloaded = client.list_downloaded_models()
    # Verfuegbare Modell-IDs/Pfade als Kleinbuchstaben sammeln
    available = {m.path.lower() for m in downloaded}

    selected = None
    # Bevorzugtes Modell in Prioritaetsreihenfolge suchen
    for preferred in MODEL_PREFERENCES:
        for avail_path in available:
            if preferred.lower() in avail_path:
                selected = preferred
                break
        if selected:
            break

    # Fallback: letztes Modell aus der Liste (qwen3.5-9b)
    if not selected:
        selected = MODEL_PREFERENCES[-1]
        console.print(
            f"[yellow]Kein bevorzugtes Modell gefunden, nutze Fallback:[/yellow] {selected}"
        )
    else:
        console.print(f"[green]Modell gewaehlt:[/green] {selected}")

    # Modell entladen falls bereits geladen (frischer Start fuer OCR)
    loaded = client.list_loaded_models(namespace="llm")
    for lm in loaded:
        if selected.lower() in lm.identifier.lower():
            console.print(f"[cyan]Entlade geladenes Modell {selected}...[/cyan]")
            try:
                handle = client.llm.model(selected)
                handle.unload()
            except Exception:
                pass
            break

    return selected


def ocr_page_sync(image_bytes: bytes, page_num: int) -> tuple[str, str]:
    """OCR mit Markdown-Formatierung und Post-Processing.

    Fuehrt die OCR auf einem Bild durch, formatiert das Ergebnis
    als sauberes Markdown und erkennt die Sprache.

    Args:
        image_bytes: Die Bilddaten als Bytes.
        page_num: Die Seitennummer ( fuer Fortschrittsanzeige).

    Returns:
        Ein Tuple aus (erkannte_sprache, text_inhalt).
    """
    # Bild ggf. verkleinern fuer bessere OCR-Performance
    processed = resize_if_needed(image_bytes)

    # Bild als temporaere PNG-Datei speichern (LM Studio braucht Dateipfad)
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
        tmp.write(processed)
        tmp_path = tmp.name

    try:
        # Verbindung zum lokalen LM Studio Server herstellen
        client = lms.Client(api_host=LMSTUDIO_HOST)
        # Beste verfuegbares Modell auswaehlen (Prioritaetsliste)
        model_name = select_ocr_model(client)
        model = client.llm.model(
            model_name,
            ttl=LMSTUDIO_TTL,
            config={"contextLength": LMSTUDIO_CONTEXT_LENGTH},
        )

        # OCR mit Retry bei Chat-Response-Error (max. 2 Versuche)
        text = None
        for attempt in range(2):
            try:
                # Bild erneut einlesen fuer jeden Versuch
                image_handle = client.prepare_image(src=tmp_path)
                chat = lms.Chat(OCR_PROMPT)
                chat.add_user_message([image_handle])

                result = model.respond(chat)
                text = result.content
                break  # Erfolgreich, kein Retry noetig
            except Exception as e:
                if attempt == 0:
                    console.print(
                        f"[yellow]Chat-Response-Error, retry... ({e})[/yellow]"
                    )
                    continue  # Zweiter Versuch
                else:
                    # Zweiter Versuch auch fehlgeschlagen
                    raise

        # Falls Ergebnis leer oder sehr kurz: Fallback-Prompt versuchen
        if not text or not text.strip() or len(text.strip()) < 10:
            chat = lms.Chat(FALLBACK_PROMPT)
            image_handle = client.prepare_image(src=tmp_path)
            chat.add_user_message([image_handle])
            result = model.respond(chat)
            text = result.content

        # Post-Processing: Prompt-Artefakte entfernen, kurze Zeilen filtern,
        # Duplikate entfernen
        content = clean_ocr_output(text)
        content = filter_short_lines(content)
        content = remove_all_duplicates(content)

        # Sprache des erkannten Textes bestimmen
        language = detect_language(content)

        return language, content

    except Exception as e:
        console.print(f"[red]Fehler bei OCR: {e}[/red]")
        return "Unbekannt", f"[Fehler: {e}]"

    finally:
        # Temporaere Bilddatei immer aufraeumen
        Path(tmp_path).unlink(missing_ok=True)


def convert_pdf_with_pdftoppm(pdf_path: Path) -> list[Path]:
    """Konvertiere PDF-Seiten mit pdftoppm zu PNG-Dateien.

    Verwendet das System-Tool pdftoppm um jede PDF-Seite in ein
    PNG-Bild umzuwandeln. Die Dateien werden im gleichen Verzeichnis
    wie die PDF erstellt mit dem Praefix "ocrpage-".

    Args:
        pdf_path: Pfad zur PDF-Datei.

    Returns:
        Liste mit Pfaden zu den erstellten PNG-Dateien.
    """
    # Verzeichnis der PDF-Datei als Arbeitsverzeichnis verwenden
    pdf_dir = pdf_path.parent

    # pdftoppm aufrufen: jede PDF-Seite wird als PNG gespeichert
    # Praefix "ocrpage" erzeugt zunaechst Dateien wie ocrpage-1.png, ocrpage-2.png
    subprocess.run(
        ["pdftoppm", "-png", str(pdf_path), "ocrpage"],
        cwd=pdf_dir,
        check=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )

    # Erzeugte PNG-Dateien einsammeln und umbenennen
    # pdftoppm erzeugt keine fuehrenden Nullen, daher manuell umbenennen:
    # ocrpage-1.png -> ocrpage-0001.png, ocrpage-2.png -> ocrpage-0002.png, ...
    png_files = sorted(pdf_dir.glob("ocrpage-*.png"))
    renamed_files = []
    for png_file in png_files:
        # Seitennummer aus dem Dateinamen extrahieren (z.B. "ocrpage-1.png" -> 1)
        page_num = int(png_file.stem.split("-")[1])
        # Neuen Dateinamen mit dreistelligem Suffix (z.B. "ocrpage-0001.png")
        new_name = png_file.parent / f"ocrpage-{page_num:04d}.png"
        png_file.rename(new_name)
        renamed_files.append(new_name)

    renamed_files.sort()
    return renamed_files


def cleanup_ocr_pages(directory: Path) -> None:
    """Loesche alle temporaeren ocrpage-*.png Dateien im Verzeichnis.

    Nach erfolgreicher OCR-Verarbeitung eines PDFs werden die
    temporaeren Bilddateien geloescht um das Verzeichnis sauber
    zu halten.

    Args:
        directory: Das Verzeichnis in dem die Dateien geloescht werden sollen.
    """
    # Alle temporaeren ocrpage-Dateien im Verzeichnis finden
    ocr_files = list(directory.glob("ocrpage-*.png"))
    for ocr_file in ocr_files:
        ocr_file.unlink()
        console.print(f"[dim]Geloescht: {ocr_file.name}[/dim]")


def process_pdf(pdf_path: Path) -> tuple[str, str]:
    """Verarbeite alle Seiten eines PDFs einzeln mit pdftoppm.

    Konvertiert das PDF zunaechst zu PNG-Seiten, führt dann auf
    jeder Seite einzeln die OCR durch und fuegt die Ergebnisse
    zusammen. Jede Seite wird mit einer Markierung versehen.

    Args:
        pdf_path: Pfad zur PDF-Datei.

    Returns:
        Ein Tuple aus (erkannte_sprache, gesamter_text_inhalt).
    """
    # PDF zu PNG-Seiten konvertieren
    png_files = convert_pdf_with_pdftoppm(pdf_path)
    total_pages = len(png_files)

    all_content = []
    detected_language = "Unbekannt"

    # Fortschrittsanzeige mit rich
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        console=console,
    ) as progress:
        task = progress.add_task("", total=total_pages)

        for page_num, png_file in enumerate(png_files):
            progress.update(
                task, description=f"[cyan]Seite {page_num + 1}/{total_pages}[/cyan]"
            )

            img_bytes = png_file.read_bytes()

            progress.update(
                task,
                description=f"[yellow]Seite {page_num + 1}: OCR laeuft...[/yellow]",
            )

            language, content = ocr_page_sync(img_bytes, page_num + 1)

            # Erste erkannte Sprache merken
            if page_num == 0:
                detected_language = language

            # Seiten-Outline als Markdown-Ueberschrift einfuegen
            all_content.append(f"\n\n# Seite {page_num + 1}\n\n{content}")
            progress.advance(task)
            progress.update(
                task, description=f"[green]Seite {page_num + 1} fertig[/green]"
            )

    # Loesche temporaere ocrpage-*.png Dateien nach der Verarbeitung
    cleanup_ocr_pages(pdf_path.parent)

    return detected_language, "".join(all_content)


def process_image_file(image_path: Path) -> tuple[str, str]:
    """Verarbeite eine einzelne Bilddatei.

    Fuehrt OCR auf einer einzigen Bilddatei durch (PNG, JPG, JPEG).

    Args:
        image_path: Pfad zur Bilddatei.

    Returns:
        Ein Tuple aus (erkannte_sprache, text_inhalt).
    """
    # Bilddatei komplett in den Speicher laden
    image_bytes = image_path.read_bytes()

    # Fortschrittsanzeige waehrend der OCR-Verarbeitung
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("[cyan]Verarbeite Bild...[/cyan]")
        progress.update(task, description="[yellow]OCR laeuft...[/yellow]")

        language, content = ocr_page_sync(image_bytes, 1)

        progress.update(task, description="[green]Fertig[/green]")

    return language, content


def save_markdown(file_path: Path, language: str, content: str) -> Path:
    """Speichere Ergebnis als reine Markdown-Datei.

    Die Ausgabedatei wird im aktuellen Arbeitsverzeichnis erstellt,
    nicht im Verzeichnis der Quelldatei. Enthaelt nur den OCR-Text,
    keine Kommentare oder Metadaten.

    Args:
        file_path: Pfad zur Quelldatei (fuer den Namen).
        language: Erkannte Sprache (wird nur auf der Konsole angezeigt).
        content: Der OCR-Text als Markdown.

    Returns:
        Pfad zur erstellten Markdown-Datei.
    """
    output_name = f"{file_path.stem}-OCR.md"
    output_path = Path.cwd() / output_name

    output_path.write_text(content, encoding="utf-8")

    return output_path


def refine_markdown(content: str) -> str:
    """Verbessere OCR-Text mit dem geladenen LM Studio Modell.

    Sendet den OCR-Text an das Modell fuer Rechtschreibkorrektur
    und verbesserte Markdown-Formatierung. Nutzt das bereits geladene
    Modell (TTL steuert das automatische Entladen).

    Args:
        content: Der rohe OCR-Text als Markdown.

    Returns:
        Der verbesserte Markdown-Text, oder der Originaltext bei Fehlern.
    """
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("[cyan]Verbessere Markdown-Formatierung...[/cyan]")

        try:
            client = lms.Client(api_host=LMSTUDIO_HOST)
            model_name = select_ocr_model(client)
            model = client.llm.model(
                model_name,
                ttl=LMSTUDIO_TTL,
                config={"contextLength": LMSTUDIO_CONTEXT_LENGTH},
            )

            chat = lms.Chat(REFINEMENT_PROMPT)
            chat.add_user_message(content)

            result = model.respond(chat)
            refined = result.content

            # Post-Processing: Prompt-Artefakte entfernen
            refined = clean_ocr_output(refined)

            # Wenn das Ergebnis leer ist, Original zurueckgeben
            if not refined.strip():
                progress.update(
                    task, description="[yellow]Kein Ergebnis, behalte Original[/yellow]"
                )
                return content

            progress.update(task, description="[green]Markdown verbessert[/green]")
            return refined

        except Exception as e:
            progress.update(
                task, description=f"[red]Fehler bei Verbesserung: {e}[/red]"
            )
            console.print("[yellow]Behalte urspruenglichen OCR-Text.[/yellow]")
            return content


def insert_text_into_pdf(pdf_path: Path, markdown_text: str) -> None:
    """Fuege OCR-Text als unsichtbare Textebene auf die entsprechenden PDF-Seiten ein.

    Verwendet PyMuPDF (fitz) mit Render-Modus 3 (unsichtbarer Text), um den
    erkannten OCR-Text als durchsuchbare Textebene ueber die jeweilige
    PDF-Seite zu legen. Der visuelle Inhalt der PDF bleibt unveraendert,
    aber der Text wird auswaehlbar und durchsuchbar.

    Args:
        pdf_path: Pfad zur Quell-PDF-Datei (wird direkt modifiziert).
        markdown_text: Der OCR-Text mit Seiten-Ueberschriften ("# Seite N").
    """
    # Seiteninhalte aus dem kombinierten Markdown-Text extrahieren
    # Trenner-Format: "# Seite N" (von process_pdf erzeugt)
    pages_content = re.split(r"\n*# Seite \d+\n*", markdown_text)
    # Leere Eintraege entfernen (z.B. Text vor dem ersten Trenner)
    pages_content = [p.strip() for p in pages_content if p.strip()]

    # PDF-Dokument oeffnen
    doc = fitz.open(str(pdf_path))

    # Schriftgroesse und Seitenrand festlegen
    fontsize = 9
    margin = 50
    # Zeilenabstand: Schriftgroesse plus 2 Punkte Zwischenraum
    line_height = fontsize + 2

    # Fuer jede PDF-Seite den entsprechenden OCR-Text einfuegen
    for page_idx in range(min(len(doc), len(pages_content))):
        page = doc[page_idx]
        page_text = pages_content[page_idx]

        # Seitenabmessungen der aktuellen PDF-Seite verwenden
        rect = page.rect
        # Maximale Y-Position bevor der untere Rand erreicht wird
        max_y = rect.height - margin

        # OCR-Text zeilenweise auf die Seite schreiben
        lines = page_text.split("\n")
        # Y-Position starten am oberen Rand plus Schriftgroesse (Baseline)
        y = margin + fontsize

        for line in lines:
            # Seitenende erreicht: restliche Zeilen ueberspringen
            if y + line_height > max_y:
                break
            # Textzeile als unsichtbare Textebene einfuegen (Modus 3)
            # "helv" = Helvetica, unterstuetzt Deutsch/Lateinisch inkl. Umlaute
            page.insert_text(
                (margin, y),
                line,
                fontname="helv",
                fontsize=fontsize,
                render_mode=3,
            )
            # Zur naechsten Zeile weiterruecken
            y += line_height

    # PDF inkrementell speichern (schneller, aendert nur den Anhang)
    doc.save(str(pdf_path), incremental=True, encryption=0)
    doc.close()


def main():
    """Hauptfunktion: Dateiauswahl, OCR-Verarbeitung, Speichern."""
    console.print("\n[bold cyan]OCR to Markdown Tool v1.7.4[/bold cyan]\n")

    # Kommandozeilenargumente parsen: -d aktiviert Markdown-Nachbearbeitung
    debug_mode = "-d" in sys.argv

    # Startverzeichnis bestimmen (Standard: aktuelles Arbeitsverzeichnis)
    start_dir = Path.cwd()
    for arg in sys.argv[1:]:
        if arg == "-d":
            continue
        arg_path = Path(arg)
        if arg_path.is_dir():
            start_dir = arg_path
        elif arg_path.is_file():
            start_dir = arg_path.parent

    # Datei ueber TUI auswaehlen
    selected_file = select_file(start_dir)

    if selected_file is None:
        console.print("[yellow]Abgebrochen.[/yellow]")
        return

    console.print(f"\n[green]Gewaehlt:[/green] {selected_file.name}\n")

    try:
        ext = selected_file.suffix.lower()

        # PDF oder Bild verarbeiten
        if ext == ".pdf":
            language, content = process_pdf(selected_file)
        else:
            language, content = process_image_file(selected_file)

        # OCR-Text nur mit -d Flag nachbearbeiten
        if debug_mode:
            content = refine_markdown(content)

        # Ergebnis als Markdown-Datei speichern
        output_path = save_markdown(selected_file, language, content)

        # Bei PDF-Input: OCR-Text auch in die Quell-PDF einfuegen
        if ext == ".pdf":
            console.print("[cyan]Fuege OCR-Text in Quell-PDF ein...[/cyan]")
            insert_text_into_pdf(selected_file, content)
            console.print(
                "[green]OCR-Text als durchsuchbare Ebene in Quell-PDF eingefuegt (Modus 3).[/green]"
            )

        console.print("\n[bold green]Fertig![/bold green]")
        console.print(f"[green]Sprache:[/green] {language}")
        console.print(f"[green]Markdown gespeichert:[/green] {output_path}")
        if ext == ".pdf":
            console.print(f"[green]PDF aktualisiert:[/green] {selected_file}")
        console.print()

    except Exception as e:
        console.print(f"\n[bold red]Fehler:[/bold red] {e}\n")
        raise


if __name__ == "__main__":
    main()
