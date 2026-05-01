# Plan: OCR-Prompt fuer DIN A4 Briefe/Rechnungen optimieren

## Ziel
Ersetze den bestehenden `OCR_PROMPT` in `ocr_to_markdown.py` durch einen umfassenden Prompt, der speziell auf DIN A4 Dokumente (Briefe, Rechnungen) mit komplexen Formatierungen, Tabellen, Handschrift und QR-Codes optimiert ist.

## Kontext
- Datei: `/home/misaka/code/glm-ocr-skripte/ocr_to_markdown.py`
- Aktueller Prompt: Zeile 160-170 (kurzer generischer Prompt)
- Fallback-Prompt: Zeile 172-173 (bleibt unveraendert)
- Modell: qwen3.5-9b (via LM Studio, lokal)
- Die Prompt-Artefakte-Filterliste (`PROMPT_ARTEFACTS`) muss ggf. erweitert werden falls der neue Prompt neue Artefakt-Muster erzeugt

## Schritte

### 1. OCR_PROMPT ersetzen (Zeile 160-170)
Den gesamten Block `# Prompt fuer OCR mit Markdown-Formatierung und Tabellen` inklusive des `OCR_PROMPT` Strings ersetzen durch:

```python
# Prompt fuer OCR von DIN A4 Dokumenten (Briefe und Rechnungen)
# Deckt komplexe Formatierungen, Tabellen, Handschrift und QR-Codes ab
OCR_PROMPT = """Fuehre eine umfassende OCR-Erkennung eines DIN A4 Dokuments (Brief oder Rechnung) durch.

ZIEL: Extrahiere den gesamten sichtbaren Text inklusive aller Formatierungen und strukturellen Elemente.

WICHTIGE ANWEISUNGEN:

1. ERKENNUNGSKOMPLETT:
   - Lese den gesamten Inhalt des Dokuments aus, keine Bereiche auslassen
   - Erkunde das Bild systematisch von oben nach unten, von links nach rechts
   - Achte auf kleinen Text, Fussnoten, Randnotizen, Seitenzahlen
   - Ignoriere keine Textbereiche, auch wenn sie unregelmaessig platziert sind

2. HANDSCHRIFT:
   - Erkunde auch handschriftliche Notizen, Unterschriften, Randbemerkungen
   - Transkribiere Handschrift so genau wie moeglich, auch wenn unleserlich
   - Markiere Handschrift mit [HANDSCHRIFT:] wenn sie von gedrucktem Text unterscheidbar ist
   - Wenn Handschrift unleserlich ist, schreibe [UNLESERLICHE HANDSCHRIFT:] und beschreibe die visuelle Form

3. QR-CODES UND BARCODES:
   - Identifiziere alle QR-Codes und Barcodes im Bild
   - Fuer QR-Codes: Schreibe [QR-Code: (Position/Beschreibung)] oder wenn moeglich, den decodierten Inhalt
   - Fuer Barcodes: Schreibe [Barcode: (Position/Beschreibung)]
   - Beschreibe die Position z.B. "oben rechts", "unten links", "Mitte des Dokuments"

4. KOMPLEXE FORMATIERUNG:
   - Erhalte die Struktur des Dokuments: Kopfzeile, Adresszeile, Absender, Empfaenger, Datum, Betreff
   - Erkunde Tabellen vollstaendig: alle Spalten, alle Zeilen, inklusive Kopfbereiche
   - Fuer Tabellen mit vielen Spalten: Stelle sicher, dass keine Spalten uebersprungen werden
   - Behandle mehrspaltige Layouts korrekt: Text fliesst von oben nach unten, dann links nach rechts
   - Markiere Aufzaehlungen mit korrektem Aufzaehlungszeichen (- oder 1., 2., a), behalte das Originalzeichen

5. SCHRIFTGROESSEN UND STILE:
   - Ueberschriften (Titel, Betreff) werden mit ## Markdown-Ueberschriften formatiert
   - Fettdruck wird mit **Fett** markiert
   - Kursiv wird mit *Kursiv* markiert
   - Unterstrichen wird mit <u>Unterstrichen</u> markiert
   - Hervorgehobener Text wird markiert, wenn erkennbar

6. TABELLEN:
   - Tabellen werden als saubere Markdown-Tabellen formatiert
   - Jede Tabelle muss korrekt formatiert sein: | Spalte1 | Spalte2 | Spalte3 |
   - Kopfbereich mit |---|---|---| markieren
   - Leerzellen in Tabellen werden als leer gelassen, nicht mit "-" gefuellt
   - Bei verschachtelten Tabellen: Struktur mit korrekter Einrueckung beibehalten

7. ZAHLEN, BETRAEGE, DATEN:
   - Betraege mit Waehrungssymbol und Komma/Dezimalpunkt: 1.234,56 EUR oder 1,234.56 EUR
   - Behalte das exakte Format: Punkt vs Komma, Tausendertrennzeichen
   - Datumsformate behalten: 01.01.2024 oder 01/01/2024
   - Rechnungsnummern, Kundennummern exakt uebernehmen

8. ADRESSFELDER:
   - Absender- und Empfaengeradressen vollstaendig auslesen
   - Bei mehrzeiligen Adressen: Struktur mit korrekten Zeilenumbruechen beibehalten
   - PLZ, Ort, Land nicht zusammenfassen, sondern wie im Original schreiben

9. RANDNOTIZEN UND FUSSZEILEN:
   - Fussnoten, Seitenzahlen, Copyright-Hinweise auslesen
   - Bankverbindungen, Steuer-IDs, Registrierungsnummern erfassen

10. AUSGABEFORMAT:
    - Gib den gesamten Text als sauberes Markdown aus
    - Keine zusaetzlichen Kommentare oder Erklaerungen in der Ausgabe
    - Ignoriere Bildrauschen, Wasserzeichen nur wenn sie Text enthalten

WICHTIGSTE REGEL:
- Lies das Bild mehrere Male: zuerst den globalen Inhalt erfassen, dann Details pruefen
- Wenn unsicher, gib die beste Interpretation anstelle von "Nicht erkannt"
- Bei konkurrierenden Interpretationen: gib die wahrscheinlichste mit [VORSICHT:] markiert aus
- Keine Woerter erfinden, keine Inhalte hinzufuegen."""
```

### 2. PROMPT_ARTEFACTS erweitern (Zeile 143-156)
Neue Artefakt-Muster hinzufuegen, die der ausfuehrlichere Prompt erzeugen koennte:

Folgende Eintraege zur bestehenden Liste hinzufuegen:
- `"zusammenfassung:"`
- `"erklaerung:"`
- `"hier ist der text:"`
- `"extrahierter text:"`
- `"gesamtinhalt:"`

### 3. Versionsnummer erhoehen
- `pyproject.toml`: `1.3.0` -> `1.4.0`
- `ocr_to_markdown.py` Docstring (Zeile 3): `v1.3.0` -> `v1.4.0`
- `ocr_to_markdown.py` TUI-Banner (Zeile ~808): `v1.3` -> `v1.4`

### 4. Tool-Upgrade ausfuehren
```bash
cd /home/misaka/code/glm-ocr-skripte && uv tool upgrade glm-ocr-skripte
```

### 5. Verifikation
- `lsp_diagnostics` auf `ocr_to_markdown.py` ausfuehren (nur pre-existing Import-Fehler erwartet)
- Pruefen dass `uv tool upgrade` erfolgreich war (Exit-Code 0, Versionsausgabe `v1.4.0`)

## Randbedingungen
- Der `FALLBACK_PROMPT` (Zeile 172-173) bleibt unveraendert
- Keine neuen Dependencies erforderlich
- Die Funktion `clean_ocr_output` filtert bereits Prompt-Artefakte, daher ist die Erweiterung der Artefakt-Liste wichtig
- Alle Kommentare auf Deutsch (wie im restlichen Code)
- Der Prompt ist absichtlich auf Deutsch geschrieben, da das LLM Deutsch verarbeitet und die Dokumente deutsch sind
