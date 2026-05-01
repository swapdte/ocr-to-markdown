# OCR Prompt Verbesserung: Horizontale & Vertikale Orientierung

## TL;DR

> **Quick Summary**: Verbessere den OCR_PROMPT in ocr_to_markdown.py, um gedrehte/vertikale Textelemente (Signaturen, Stempel, Wasserzeichen) korrekt zu erkennen und die Vollständigkeit der Textextraktion zu gewährleisten.
>
> **Deliverables**:
> - Aktualisierter OCR_PROMPT mit Anweisungen für gedrehten Text (90°, 180°, 270°)
> - Erweiterte systematische Scan-Strategie für Vollständigkeit
> - Verbesserte Tabellenstruktur-Preservation
> - Aktualisierte PROMPT_ARTEFACTS Liste falls nötig
> - Version 1.4.0 → 1.5.0
>
> **Estimated Effort**: Quick
> **Parallel Execution**: NO - sequential (single file change)
> **Critical Path**: Task 1 → Task 2 → Task 3 → Task 4

---

## Context

### Original Request
Das OCR-Skript soll horizontal und vertikal orientierte Dokumente lesen können. Kein Buchstabe soll ausgelassen werden und komplexe Formatierungen sollen in Markdown-Tabellen dargestellt werden.

### Interview Summary
**Key Discussions**:
- Dokumenttyp: Rechnungen (Invoices)
- Vertikaler Text: Gedrehte Elemente (Signaturen, Stempel, Wasserzeichen, rotierte Labels)
- Strategie: Immer sowohl horizontale ALS auch vertikale/gedrehte Texte prüfen (vollständig statt schnell)
- Test-Strategie: Keine automatisierten Tests - manuelle Verifikation mit echten Dokumenten
- Scope: Nur Prompt-Verbesserung, keine Code-Struktur-Änderungen

**Research Findings**:
- Aktueller Prompt (v1.4.0, Zeilen 168-237) hat umfassende DIN A4 Anweisungen
- Zeile 196: "Text fliesst von oben nach unten, dann links nach rechts" - geht nur von horizontal aus
- Keine Test-Infrastruktur im Projekt (keine test-Dependencies, keine test-Dateien)

### Metis Review
Keine Metis-Konsultation durchgeführt (vom Benutzer übersprungen).

---

## Work Objectives

### Core Objective
Verbessere den OCR_PROMPT um gedrehte/vertikale Textelemente zu erkennen und die Vollständigkeit der Textextraktion für Rechnungen zu gewährleisten.

### Concrete Deliverables
- `ocr_to_markdown.py`: Aktualisierter OCR_PROMPT (Zeilen 168-237)
- `ocr_to_markdown.py`: Aktualisierte PROMPT_ARTEFACTS Liste falls nötig
- `ocr_to_markdown.py`: Aktualisierte Versionsnummer (v1.4.0 → v1.5.0)
- `pyproject.toml`: Aktualisierte Version (1.4.0 → 1.5.0)

### Definition of Done
- [ ] Prompt enthält explizite Anweisungen für gedrehten Text (90°, 180°, 270°)
- [ ] Prompt fordert systematische Prüfung auf BEIDE Orientierungen
- [ ] Prompt enthält verbesserte Anweisungen für Tabellenstruktur-Preservation
- [ ] Versionsnummern aktualisiert
- [ ] Manuelle Tests mit echten Dokumenten bestätigen Verbesserungen

### Must Have
- Erkennung von gedrehtem Text (Signaturen, Stempel, Wasserzeichen)
- Vollständige Textextraktion (kein fehlender Text)
- Korrekte Tabellenstruktur im Markdown-Output

### Must NOT Have (Guardrails)
- Keine Code-Struktur-Änderungen (nur Prompt-Konstanten)
- Keine neuen Dependencies
- Keine automatisierten Tests hinzufügen
- Keine Änderungen an der OCR-Verarbeitungslogik
- Keine Änderungen an PDF-Rendering oder Bilddatei-Verarbeitung

---

## Verification Strategy (MANDATORY)

> **ZERO HUMAN INTERVENTION** - ALL verification is agent-executed. No exceptions.

### Test Decision
- **Infrastructure exists**: NO
- **Automated tests**: None
- **Framework**: None
- **TDD**: Not applicable

### QA Policy
Da keine automatisierten Tests vorhanden sind, basiert die Verifikation auf:
- Syntax-Check des Python-Codes (Bash: python -m py_compile)
- Linter-Check falls verfügbar (Bash: ruff check ocr_to_markdown.py)
- Manuelle QA Szenarien beschreiben (vom Benutzer mit echten Dokumenten auszuführen)

Jede Aufgabe wird mit Agent-Executed QA Szenarien versehen, die vom Ausführenden Agenten verifiziert werden können (Syntax, Syntax-Errors, korrekte String-Formatierung).

---

## Execution Strategy

### Parallel Execution Waves

> Alle Aufgaben sind sequentiell, da sie dieselbe Datei (ocr_to_markdown.py) betreffen.

```
Wave 1 (Single sequential chain):
└── Task 1: OCR_PROMPT verbessern [quick]
    └── Task 2: PROMPT_ARTEFACTS prüfen und erweitern [quick]
        └── Task 3: Versionen aktualisieren [quick]
            └── Task 4: Code-Syntax und Linter-Check [quick]

Critical Path: Task 1 → Task 2 → Task 3 → Task 4
Parallel Speedup: N/A (sequential only)
Max Concurrent: 1
```

### Dependency Matrix

- **1**: - - 2, 3, 4
- **2**: 1 - 3, 4
- **3**: 1, 2 - 4
- **4**: 1, 2, 3 - -

### Agent Dispatch Summary

- **1**: **1** - T1 → `quick`
- **2**: **1** - T2 → `quick`
- **3**: **1** - T3 → `quick`
- **4**: **1** - T4 → `quick`

---

## TODOs

> Implementation + Test = ONE Task. Never separate.
> EVERY task MUST have: Recommended Agent Profile + Parallelization info + QA Scenarios.
> **A task WITHOUT QA Scenarios is INCOMPLETE. No exceptions.**

- [x] 1. **OCR_PROMPT verbessern: Rotierte Texte und Vollständigkeit**

  **What to do**:
  - Lies den aktuellen OCR_PROMPT in ocr_to_markdown.py (Zeilen 168-237)
  - Ersetze/Erweitere den Prompt mit folgenden Verbesserungen:
    1. **Rotierte Texte (NEU)**: Füge einen neuen Abschnitt für gedrehte/vertikale Textelemente hinzu:
       - Instruktionen zum Erkennen von um 90°, 180° und 270° gedrehtem Text
       - Spezifische Erwähnung von Signaturen, Stempeln, Wasserzeichen, rotierten Labels
       - Anweisung: Drehrichtung erkennen und Text korrekt transkribieren (nicht umschreiben)
       - Beispiel: "Gedrehten Text so erkennen wie er erscheint, z.B. [GEDREHT 90°:] Signatur"

    2. **Systematische Vollständigkeit (VERSTÄRKT)**: Erweitere den Abschnitt "ERKENNUNGSKOMPLETT":
       - Explizite Anweisung: Prüfe das Bild ZWEIMAL - einmal horizontal lesen, einmal auf gedrehte Elemente scannen
       - Strategie: "Erst alle horizontalen Texte auslesen, dann gezielt nach gedrehten Elementen suchen"
       - Erwähnung von Randbereichen und Ecken, wo oft Stempel oder Signaturen stehen

    3. **Tabellenstruktur (VERBESSERT)**: Erweitere den Abschnitt "TABELLEN":
       - Ergänze: "Prüfe Tabellen auf geschachtelte Strukturen und verbundene Zellen (merged cells)"
       - Ergänze: "Bei komplexen Tabellen: Zuerst die Tabellenstruktur erfassen, dann Zelleninhalte füllen"
       - Ergänze: "Tabellen mit rotierten Kopfzeilen: Rotierung kennzeichnen, z.B. [GEDREHT 90°:] Spaltenname"

    4. **Lesereihenfolge bei gemischten Layouts (KLARER)**: Aktualisiere Abschnitt 4:
       - Ändere: "Behandle mehrspaltige Layouts korrekt: Text fliesst von oben nach unten, dann links nach rechts"
       - Zu: "Bei mehrspaltigen Layouts: Bestimme zuerst die Hauptleserichtung, dann lese Spalten in der korrekten Reihenfolge aus. Prüfe ob Spalten unterschiedliche Leserichtungen haben."

  - Achte auf korrekte Python-Multi-line String-Syntax (dreifache Anführungszeichen, korrekte Einrückung)
  - Erweitere die Liste PROMPT_ARTEFACTS falls der neue Prompt neue Artefakt-Muster erzeugen könnte

  **Must NOT do**:
  - Keine Änderungen an der OCR-Verarbeitungslogik (Funktionen, Klassen)
  - Keine neuen Funktionen oder Methoden hinzufügen
  - Keine Änderungen an Import-Anweisungen
  - Keine Änderungen an der PDF- oder Bildverarbeitung

  **Recommended Agent Profile**:
  > Select category + skills based on task domain. Justify each choice.
  - **Category**: `quick`
    - Reason: Single string replacement task, straightforward text editing
  - **Skills**: `[]`
    - No specialized skills needed - simple string editing
  - **Skills Evaluated but Omitted**:
    - `context7-mcp`: Not needed - no library/API references required
    - `git-master`: Not needed yet - commit happens in final task

  **Parallelization**:
  - **Can Run In Parallel**: NO
  - **Parallel Group**: Sequential (Task 1)
  - **Blocks**: [Task 2, Task 3, Task 4]
  - **Blocked By**: None (can start immediately)

  **References** (CRITICAL - Be Exhaustive):

  > The executor has NO context from your interview. References are their ONLY guide.
  > Each reference must answer: "What should I look at and WHY?"

  **Pattern References** (existing code to follow):
  - `ocr_to_markdown.py:168-237` - Current OCR_PROMPT structure and style to maintain
  - `ocr_to_markdown.py:144-164` - PROMPT_ARTEFACTS list format to extend if needed
  - `ocr_to_markdown.py:27-31` - Multi-line string syntax pattern with German comments

  **API/Type References** (contracts to implement against):
  - None - this is a string constant, not code logic

  **Test References** (testing patterns to follow):
  - None - no test infrastructure

  **External References** (libraries and frameworks):
  - None - pure Python string manipulation

  **WHY Each Reference Matters** (explain the relevance):
  - `ocr_to_markdown.py:168-237`: Shows current prompt structure, German language style, and formatting to maintain consistency
  - `ocr_to_markdown.py:144-164`: Shows how to add new artifact patterns to filter list
  - `ocr_to_markdown.py:27-31`: Demonstrates multi-line string syntax with proper indentation and comments

  **Acceptance Criteria**:

  > **AGENT-EXECUTABLE VERIFICATION ONLY** - No human action permitted.
  > Every criterion MUST be verifiable by running a command or using a tool.

  **No TDD (tests disabled)**:
  - [ ] File ocr_to_markdown.py contains updated OCR_PROMPT (lines 168-237)
  - [ ] OCR_PROMPT contains section for rotated text (90°, 180°, 270°)
  - [ ] OCR_PROMPT contains explicit instruction to check both horizontal AND rotated text
  - [ ] OCR_PROMPT contains improved table structure instructions
  - [ ] PROMPT_ARTEFACTS list extended if new patterns identified
  - [ ] Python syntax valid (no syntax errors)

  **QA Scenarios (MANDATORY - task is INCOMPLETE without these):**

  > **This is NOT optional. A task without QA scenarios WILL BE REJECTED.**

  ```
  Scenario: Verify prompt contains rotated text instructions
    Tool: Bash (grep)
    Preconditions: Task 1 completed
    Steps:
      1. grep -i "gedreht\|rotiert\|90°\|180°\|270°" ocr_to_markdown.py | head -5
      2. Check if output contains OCR_PROMPT section with rotated text instructions
    Expected Result: At least one line from OCR_PROMPT containing rotated text instructions
    Failure Indicators: No matches found, or matches only in comments not in OCR_PROMPT
    Evidence: .sisyphus/evidence/task-1-rotated-text-instructions.txt

  Scenario: Verify prompt contains completeness instructions
    Tool: Bash (grep)
    Preconditions: Task 1 completed
    Steps:
      1. grep -A 3 "ERKENNUNGSKOMPLETT\|vollstaendig\|systematisch" ocr_to_markdown.py
      2. Check if instructions mention scanning twice or checking both orientations
    Expected Result: OCR_PROMPT section contains instructions for systematic completeness check
    Failure Indicators: No completeness instructions found
    Evidence: .sisyphus/evidence/task-1-completeness-instructions.txt

  Scenario: Verify Python syntax is valid
    Tool: Bash (python -m py_compile)
    Preconditions: Task 1 completed
    Steps:
      1. python -m py_compile ocr_to_markdown.py
      2. Check exit code
    Expected Result: Exit code 0 (no syntax errors)
    Failure Indicators: SyntaxError, IndentationError, or other Python syntax errors
    Evidence: .sisyphus/evidence/task-1-syntax-check.txt
  ```

  **Evidence to Capture**:
  - [ ] task-1-rotated-text-instructions.txt: grep output showing rotated text instructions
  - [ ] task-1-completeness-instructions.txt: grep output showing completeness instructions
  - [ ] task-1-syntax-check.txt: py_compile output (or empty if successful)

  **Commit**: NO (commits grouped in Task 3)

- [x] 2. **PROMPT_ARTEFACTS Liste prüfen und erweitern**

  **What to do**:
  - Lies die aktuelle PROMPT_ARTEFACTS Liste in ocr_to_markdown.py (Zeilen 144-164)
  - Analysiere den neuen OCR_PROMPT aus Task 1 auf neue Keywords/Phrasen, die als Artefakte in der LLM-Ausgabe erscheinen könnten
  - Füge alle neuen Artefakt-Pattern zur Liste hinzu, wenn sie noch nicht vorhanden sind
  - Behalte das gleiche Format: kleingeschriebene strings ohne spezielle Zeichen
  - Typische neue Artefakte für rotierte Texte könnten sein:
    - "gedreht"
    - "rotation"
    - "grad"
    - "signatur" (falls als prompt-echo erscheint)
  - Die Liste soll helfen, Prompt-Echos aus der LLM-Ausgabe zu filtern

  **Must NOT do**:
  - Keine Änderungen am OCR_PROMPT selbst (dies wurde in Task 1 erledigt)
  - Keine Änderungen an der clean_ocr_output Funktion
  - Keine Änderungen an anderen Teilen des Codes

  **Recommended Agent Profile**:
  > Select category + skills based on task domain. Justify each choice.
  - **Category**: `quick`
    - Reason: Simple list extension based on pattern analysis
  - **Skills**: `[]`
    - No specialized skills needed - list analysis and string addition
  - **Skills Evaluated but Omitted**:
    - None applicable

  **Parallelization**:
  - **Can Run In Parallel**: NO
  - **Parallel Group**: Sequential (Task 2)
  - **Blocks**: [Task 3, Task 4]
  - **Blocked By**: [Task 1]

  **References** (CRITICAL - Be Exhaustive):

  > The executor has NO context from your interview. References are their ONLY guide.
  > Each reference must answer: "What should I look at and WHY?"

  **Pattern References** (existing code to follow):
  - `ocr_to_markdown.py:144-164` - Current PROMPT_ARTEFACTS list format and style
  - `ocr_to_markdown.py:168-237` - Updated OCR_PROMPT from Task 1 to analyze for new patterns
  - `ocr_to_markdown.py:494-530` - clean_ocr_output function that uses PROMPT_ARTEFACTS

  **API/Type References** (contracts to implement against):
  - None - this is a list constant, not code logic

  **Test References** (testing patterns to follow):
  - None - no test infrastructure

  **External References** (libraries and frameworks):
  - None - pure Python list manipulation

  **WHY Each Reference Matters** (explain the relevance):
  - `ocr_to_markdown.py:144-164`: Shows current artifact list format - lowercase strings, German patterns
  - `ocr_to_markdown.py:168-237`: Source of potential new artifact patterns from the updated prompt
  - `ocr_to_markdown.py:494-530`: Shows how PROMPT_ARTEFACTS is used - line-by-line filtering based on artifact matches

  **Acceptance Criteria**:

  > **AGENT-EXECUTABLE VERIFICATION ONLY** - No human action permitted.
  > Every criterion MUST be verifiable by running a command or using a tool.

  **No TDD (tests disabled)**:
  - [ ] PROMPT_ARTEFACTS list contains new patterns from updated OCR_PROMPT
  - [ ] List format maintained (lowercase strings, no regex)
  - [ ] No duplicate entries in the list
  - [ ] Python syntax valid

  **QA Scenarios (MANDATORY - task is INCOMPLETE without these):**

  > **This is NOT optional. A task without QA scenarios WILL BE REJECTED.**

  ```
  Scenario: Verify PROMPT_ARTEFACTS contains new patterns
    Tool: Bash (grep)
    Preconditions: Task 2 completed
    Steps:
      1. grep -E "gedreht|rotation|grad|signatur" ocr_to_markdown.py | grep "PROMPT_ARTEFACTS\|artifact"
      2. Check if any new patterns related to rotated text were added
    Expected Result: New artifact patterns present if they appeared in OCR_PROMPT
    Failure Indicators: No new patterns despite OCR_PROMPT containing new keywords
    Evidence: .sisyphus/evidence/task-2-new-artifacts.txt

  Scenario: Verify list has no duplicates
    Tool: Bash (python -c)
    Preconditions: Task 2 completed
    Steps:
      1. Extract PROMPT_ARTEFACTS list and check for duplicates using Python
    Expected Result: No duplicate entries in the list
    Failure Indicators: Duplicate artifact patterns found
    Evidence: .sisyphus/evidence/task-2-no-duplicates.txt

  Scenario: Verify Python syntax is valid
    Tool: Bash (python -m py_compile)
    Preconditions: Task 2 completed
    Steps:
      1. python -m py_compile ocr_to_markdown.py
      2. Check exit code
    Expected Result: Exit code 0 (no syntax errors)
    Failure Indicators: SyntaxError, IndentationError, or other Python syntax errors
    Evidence: .sisyphus/evidence/task-2-syntax-check.txt
  ```

  **Evidence to Capture**:
  - [ ] task-2-new-artifacts.txt: grep output showing new artifact patterns
  - [ ] task-2-no-duplicates.txt: Python check output confirming no duplicates
  - [ ] task-2-syntax-check.txt: py_compile output (or empty if successful)

  **Commit**: NO (commits grouped in Task 3)

- [x] 3. **Versionen aktualisieren**

  **What to do**:
  - Aktualisiere alle Versionen von 1.4.0 auf 1.5.0:
    1. `ocr_to_markdown.py`: Docstring Zeile 3: "v1.4.0" → "v1.5.0"
    2. `ocr_to_markdown.py`: main() function Zeile 889: "v1.4" → "v1.5"
    3. `pyproject.toml`: Zeile 3: version = "1.4.0" → version = "1.5.0"
  - Stelle sicher, dass alle Versionen konsistent sind (gleiche Versionsnummer überall)
  - Keine anderen Änderungen in diesen Dateien vornehmen

  **Must NOT do**:
  - Keine Änderungen am OCR_PROMPT (bereits erledigt in Task 1)
  - Keine Änderungen an PROMPT_ARTEFACTS (bereits erledigt in Task 2)
  - Keine Änderungen an anderen Dateien
  - Keine Versionssprünge auf ungerade Zahlen (1.4.0 → 1.4.1 statt 1.5.0) - die Version soll 1.5.0 sein

  **Recommended Agent Profile**:
  > Select category + skills based on task domain. Justify each choice.
  - **Category**: `quick`
    - Reason: Simple version string replacement across 2 files
  - **Skills**: `[git-master]`
    - `git-master`: Required for the commit operation at the end of this task
  - **Skills Evaluated but Omitted**:
    - `context7-mcp`: Not needed - no library/API references required

  **Parallelization**:
  - **Can Run In Parallel**: NO
  - **Parallel Group**: Sequential (Task 3)
  - **Blocks**: [Task 4]
  - **Blocked By**: [Task 1, Task 2]

  **References** (CRITICAL - Be Exhaustive):

  > The executor has NO context from your interview. References are their ONLY guide.
  > Each reference must answer: "What should I look at and WHY?"

  **Pattern References** (existing code to follow):
  - `ocr_to_markdown.py:3` - Docstring with version to update
  - `ocr_to_markdown.py:889` - TUI banner with version to update
  - `pyproject.toml:3` - Project version to update
  - `.sisyphus/plans/ocr-prompt-verbesserung.md:104-106` - Example of version update pattern from previous plan

  **API/Type References** (contracts to implement against):
  - None - this is string replacement only

  **Test References** (testing patterns to follow):
  - None - no test infrastructure

  **External References** (libraries and frameworks):
  - None - simple string replacement

  **WHY Each Reference Matters** (explain the relevance):
  - `ocr_to_markdown.py:3`: Shows docstring version format - "v1.4.0 - OCR zu Markdown Konverter..."
  - `ocr_to_markdown.py:889`: Shows TUI banner version format - "OCR to Markdown Tool v1.4"
  - `pyproject.toml:3`: Shows pyproject version format - version = "1.4.0"
  - `.sisyphus/plans/ocr-prompt-verbesserung.md:104-106`: Shows previous version update pattern to follow

  **Acceptance Criteria**:

  > **AGENT-EXECUTABLE VERIFICATION ONLY** - No human action permitted.
  > Every criterion MUST be verifiable by running a command or using a tool.

  **No TDD (tests disabled)**:
  - [ ] ocr_to_markdown.py docstring contains "v1.5.0"
  - [ ] ocr_to_markdown.py TUI banner contains "v1.5"
  - [ ] pyproject.toml contains version = "1.5.0"
  - [ ] All version numbers are consistent
  - [ ] No syntax errors

  **QA Scenarios (MANDATORY - task is INCOMPLETE without these):**

  > **This is NOT optional. A task without QA scenarios WILL BE REJECTED.**

  ```
  Scenario: Verify all version numbers updated to 1.5.0
    Tool: Bash (grep)
    Preconditions: Task 3 completed
    Steps:
      1. grep -n "v1\.5" ocr_to_markdown.py
      2. grep -n "version.*1\.5\.0" pyproject.toml
      3. Verify grep finds at least 2 matches (docstring and TUI banner)
    Expected Result: All version strings show 1.5.0 or v1.5, no 1.4.0 or v1.4 remaining
    Failure Indicators: Old version numbers (1.4.0, v1.4) still present, or inconsistent versions
    Evidence: .sisyphus/evidence/task-3-version-check.txt

  Scenario: Verify no version inconsistencies
    Tool: Bash (grep + grep -v)
    Preconditions: Task 3 completed
    Steps:
      1. grep -n "1\.4\." ocr_to_markdown.py pyproject.toml
      2. Verify no matches found (old versions removed)
    Expected Result: No output (no old version numbers found)
    Failure Indicators: Old version numbers (1.4.0, 1.4, etc.) still present
    Evidence: .sisyphus/evidence/task-3-no-old-versions.txt

  Scenario: Verify Python syntax is valid
    Tool: Bash (python -m py_compile)
    Preconditions: Task 3 completed
    Steps:
      1. python -m py_compile ocr_to_markdown.py
      2. Check exit code
    Expected Result: Exit code 0 (no syntax errors)
    Failure Indicators: SyntaxError, IndentationError, or other Python syntax errors
    Evidence: .sisyphus/evidence/task-3-syntax-check.txt
  ```

  **Evidence to Capture**:
  - [ ] task-3-version-check.txt: grep output showing all updated version numbers
  - [ ] task-3-no-old-versions.txt: grep output confirming no old versions remain
  - [ ] task-3-syntax-check.txt: py_compile output (or empty if successful)

  **Commit**: YES (final commit for all changes)
  - Message: `feat(ocr-prompt): add rotated text handling and completeness instructions`
  - Files: `ocr_to_markdown.py`, `pyproject.toml`
  - Pre-commit: `python -m py_compile ocr_to_markdown.py`

- [x] 4. **Code-Qualitätscheck (Syntax und Linter)**

  **What to do**:
  - Fuehre einen finalen Syntax-Check auf ocr_to_markdown.py durch
  - Pruefe ob ruff (Python linter) installiert ist und fuehre ruff check aus falls verfuegbar
  - Verifiziere, dass alle String-Formatierungen im OCR_PROMPT korrekt sind (keine fehlenden Escape-Sequenzen)
  - Pruefe auf offensichtliche Code-Qualitaetsprobleme (ungenuetzte Imports, konsistente Einrueckung, etc.)
  - Berichte ueber alle gefundenen Probleme (falls welche existieren)

  **Must NOT do**:
  - Keine Code-Refactoring oder Stil-Verbesserungen vornehmen
  - Keine logischen Änderungen am Code
  - Nur prüfen und berichten, nicht korrigieren (außer kritische Syntax-Errors)

  **Recommended Agent Profile**:
  > Select category + skills based on task domain. Justify each choice.
  - **Category**: `quick`
    - Reason: Verification-only task, no code changes
  - **Skills**: `[]`
    - No specialized skills needed - basic bash commands for syntax/linter check
  - **Skills Evaluated but Omitted**:
    - `git-master`: Not needed - this is verification only, no git operations

  **Parallelization**:
  - **Can Run In Parallel**: NO
  - **Parallel Group**: Sequential (Task 4)
  - **Blocks**: [Final Verification Wave]
  - **Blocked By**: [Task 1, Task 2, Task 3]

  **References** (CRITICAL - Be Exhaustive):

  > The executor has NO context from your interview. References are their ONLY guide.
  > Each reference must answer: "What should I look at and WHY?"

  **Pattern References** (existing code to follow):
  - `ocr_to_markdown.py` - Entire file to check for syntax and quality issues
  - None specific - this is a comprehensive file check

  **API/Type References** (contracts to implement against):
  - None - this is verification only

  **Test References** (testing patterns to follow):
  - None - no test infrastructure

  **External References** (libraries and frameworks):
  - Python py_compile module documentation (if needed for syntax check reference)
  - ruff linter documentation (if available and used)

  **WHY Each Reference Matters** (explain the relevance):
  - `ocr_to_markdown.py`: The entire file needs to be checked for syntax errors and quality issues after all modifications

  **Acceptance Criteria**:

  > **AGENT-EXECUTABLE VERIFICATION ONLY** - No human action permitted.
  > Every criterion MUST be verifiable by running a command or using a tool.

  **No TDD (tests disabled)**:
  - [ ] Python syntax valid (py_compile passes)
  - [ ] No ruff errors (if ruff available)
  - [ ] No obvious code quality issues (unbalanced quotes, inconsistent indentation)
  - [ ] All string literals properly escaped in OCR_PROMPT

  **QA Scenarios (MANDATORY - task is INCOMPLETE without these):**

  > **This is NOT optional. A task without QA scenarios WILL BE REJECTED.**

  ```
  Scenario: Verify Python syntax is valid
    Tool: Bash (python -m py_compile)
    Preconditions: Task 4 completed
    Steps:
      1. python -m py_compile ocr_to_markdown.py
      2. Check exit code
      3. Capture any error output
    Expected Result: Exit code 0, no syntax errors
    Failure Indicators: SyntaxError, IndentationError, or other Python syntax errors
    Evidence: .sisyphus/evidence/task-4-syntax-check.txt

  Scenario: Check for ruff linter issues (if available)
    Tool: Bash (which ruff && ruff check || echo "ruff not installed")
    Preconditions: Task 4 completed
    Steps:
      1. Check if ruff is installed with 'which ruff'
      2. If ruff available, run 'ruff check ocr_to_markdown.py'
      3. If ruff not available, record that check was skipped
    Expected Result: No ruff errors (if ruff available), or note that ruff not installed
    Failure Indicators: Ruff errors or warnings (if ruff available)
    Evidence: .sisyphus/evidence/task-4-ruff-check.txt

  Scenario: Verify string formatting in OCR_PROMPT
    Tool: Bash (python -c)
    Preconditions: Task 4 completed
    Steps:
      1. Use Python to parse the file and check for SyntaxError specifically in multi-line strings
      2. Verify OCR_PROMPT is a valid Python string
    Expected Result: No string formatting errors
    Failure Indicators: EOL while scanning string literal, unterminated triple-quoted string
    Evidence: .sisyphus/evidence/task-4-string-format-check.txt
  ```

  **Evidence to Capture**:
  - [ ] task-4-syntax-check.txt: py_compile output (or empty if successful)
  - [ ] task-4-ruff-check.txt: ruff check output or "ruff not installed" message
  - [ ] task-4-string-format-check.txt: Python string parsing check output

  **Commit**: NO (commit happened in Task 3)

---

## Final Verification Wave (MANDATORY — after ALL implementation tasks)

> Da keine automatisierten Tests existieren, konzentriert sich die Endverifikation auf Code-Qualität und Syntax-Check.
>
> **Do NOT auto-proceed after verification. Wait for user's explicit approval before marking work complete.**
> **Never mark F1 as checked before getting user's okay.** Rejection or user feedback -> fix -> re-run -> present again -> wait for okay.

- [x] F1. **Code-Syntax und Linter-Check** — `quick`
  Fuehre python -m py_compile auf ocr_to_markdown.py aus, um Syntax-Error sicherzustellen. Pruefe ob ruff verfuegbar ist und fuehre ruff check ocr_to_markdown.py aus. Pruefe alle String-Formatierungen im OCR_PROMPT auf korrekte Escape-Sequenzen und Syntax. Verifiziere dass alle Versionen konsistent auf 1.5.0 aktualisiert wurden.
  Output: `Syntax [PASS] | Linter [PASS] | String-Formatting [CORRECT] | Versions [CONSISTENT] | VERDICT: ALL PASS`

---

## Commit Strategy

- **1**: `feat(ocr-prompt): add rotated text handling and completeness instructions` - ocr_to_markdown.py, pyproject.toml

---

## Success Criteria

### Verification Commands
```bash
# Syntax check
python -m py_compile ocr_to_markdown.py
# Expected: No output (exit code 0)

# Linter check (falls ruff installiert)
ruff check ocr_to_markdown.py
# Expected: No errors or warnings related to the changes

# Version check
grep "v1.5.0" ocr_to_markdown.py
grep "version = \"1.5.0\"" pyproject.toml
# Expected: Both commands find the updated version
```

### Final Checklist
- [ ] OCR_PROMPT enthält Anweisungen für gedrehten Text (90°, 180°, 270°)
- [ ] OCR_PROMPT fordert Prüfung auf BEIDE Orientierungen
- [ ] Tabellenstruktur-Anweisungen verbessert
- [ ] PROMPT_ARTEFACTS aktualisiert falls nötig
- [ ] Versionen auf 1.5.0 aktualisiert
- [ ] Code-Syntax korrekt (python -m py_compile pass)
- [ ] Manuelles Testing mit echten Dokumenten durch Benutzer
