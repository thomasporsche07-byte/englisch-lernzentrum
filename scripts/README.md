# Phase-2-Werkzeuge: Auto-Linter + Generator

Dieser Ordner enthaelt zwei Werkzeuge zur Produktivitaetssteigerung:

| Datei | Zweck |
|---|---|
| `lint_watcher.py` | Watcht `grammatik/` + `uebergreifend/`, prueft jede Datei beim Speichern gegen `CLAUDE.md`-Konventionen. |
| `new_grammar.py` | Generiert eine neue Grammatik-Stub-Datei + Tile in `index.html`. |
| `start_lint_watcher.ps1` | PowerShell-Wrapper, der den Linter startet (manuell oder per Auto-Start). |
| `lint_watcher_task.xml` | Task-Scheduler-Definition fuer Auto-Start beim Login. |

## Voraussetzungen

- **Python 3.8+** muss installiert sein. Auf Windows ueblicherweise per [python.org/downloads](https://www.python.org/downloads/) – beim Setup „Add Python to PATH" aktivieren. Der `py`-Launcher wird automatisch mitinstalliert.
- **node.js** (optional, aber empfohlen): aktiviert die Inline-JS-Syntaxpruefung des Linters. Ohne node arbeitet der Linter weiter, ueberspringt aber den `node --check`-Schritt. Download: [nodejs.org](https://nodejs.org/).
- **watchdog** (optional, aber empfohlen): macht den Linter effizienter. Ohne watchdog laeuft Polling alle 2 s.

  ```powershell
  py -m pip install watchdog
  ```

  Falls `pip` fehlt: `py -m ensurepip --upgrade`.

## Auto-Linter

### Manueller Lauf

```powershell
cd "K:\OneDrive - Hellweg-Realschule\01 - Schule\01 - Englisch\englisch-lernzentrum"
py scripts\lint_watcher.py
```

Standardverhalten: einmal Vollscan (alle Dateien), danach Watcher (laeuft permanent, Strg+C beendet).

Optionen:

| Flag | Wirkung |
|---|---|
| `--once` | Nur Vollscan, dann beenden (gut fuer CI / Pre-Commit). |
| `--file PATH` | Nur eine Datei pruefen. |
| `--json-only` | Kein Konsolen-Output, nur `lint_status.json` schreiben. |
| `--no-color` | Ohne ANSI-Farben (z. B. fuer Windows-CMD ohne ANSI-Support). |

Konsolen-Output:

```text
OK   grammatik/05_to_be.html
FAIL grammatik/06_some_any_little_few.html  (2 Verstoss/Verstoesse)
  -> [br-in-rc-formula]:387  <br> innerhalb von <div class="rc-formula"> verboten - ...
```

JSON-Status (`lint_status.json` im Projekt-Root):

```json
{
  "updated": "2026-04-27 02:55:00",
  "files": [
    {
      "file": "grammatik/05_to_be.html",
      "ok": true,
      "issue_count": 0,
      "issues": []
    }
  ],
  "summary": { "total_files": 15, "files_ok": 14, "files_failed": 1, "total_issues": 1 }
}
```

### Geprueftes Regelwerk

Der Linter implementiert die Konventionen aus `CLAUDE.md`:

| Regel-ID | Anwendbar auf | Erklaerung |
|---|---|---|
| `forbidden-term` | alle | Fachbegriffe wie „Infinitiv", „partiell", „nominal" im sichtbaren Text. |
| `pronoun-cluster-in-card` | alle | Klartext-Pronomen-Cluster („he/she/it") in `rc-card`-Markup statt als Pill-Formel. |
| `br-in-rc-formula` | alle | `<br>` direkt in `<div class="rc-formula">`. |
| `tag-imbalance` | alle | Anzahl `<html>`/`<head>`/`<body>`/`<section>`/`<details>` oeffnend ≠ schliessend. |
| `js-syntax` | alle | Inline-`<script>` ist via `node --check` syntaktisch fehlerhaft. |
| `ls-key-generic` / `ls-key-no-prefix` | alle | LocalStorage-Key ohne dateispezifischen Praefix. |
| `missing-shared-css` / `missing-shared-js` | nur `grammatik/` | Pflicht-Includes (`shared/style.css`, `quiz.css`, `tutor.css`, `scorecards.js`, `quiz.js`, `tutor.js`). |
| `shared-js-order` | nur `grammatik/` | Reihenfolge der Pflicht-Skripte (scorecards → quiz → tutor). |
| `missing-required-call` | nur `grammatik/` | `HRQuiz.init(`, `HRShared.initDarkMode/initTTS/initResetAllButton`. |
| `missing-tutor-mount` | nur `grammatik/` | `<div id="tutor-mount"></div>` fehlt. |
| `missing-tutor-config` / `tutor-config-field-missing` | nur `grammatik/` | `window.TUTOR_CONFIG` mit Pflicht-Feldern. |

### Auto-Start beim Login (Windows)

Der Linter laeuft permanent im Hintergrund. Damit der Lehrer sich nicht manuell darum kuemmern muss, wird er per Aufgabenplanung beim Login gestartet.

**Variante A – Aufgabenplanung-XML importieren** (empfohlen):

```powershell
schtasks /Create /XML "K:\OneDrive - Hellweg-Realschule\01 - Schule\01 - Englisch\englisch-lernzentrum\scripts\lint_watcher_task.xml" /TN "EnglischLernzentrumLinter"
```

Falls die Task bereits existiert: vorher mit `schtasks /Delete /TN EnglischLernzentrumLinter /F` entfernen.

Die Task laeuft als angemeldeter Benutzer (kein Admin), Trigger = Logon. Stop-bei-Akku ist deaktiviert.

**Variante B – Startup-Ordner** (einfach, aber Konsolenfenster ist sichtbar):

1. `Win + R` → `shell:startup` → Enter.
2. Verknuepfung in den geoeffneten Ordner ziehen mit Ziel:

   ```text
   powershell.exe -ExecutionPolicy Bypass -WindowStyle Minimized -File "K:\OneDrive - Hellweg-Realschule\01 - Schule\01 - Englisch\englisch-lernzentrum\scripts\start_lint_watcher.ps1"
   ```

Bei beiden Varianten landet das Linter-Log unter `lint_watcher.log` im Projekt-Root.

### Manueller Test (Verstoss-Verifikation)

So pruefst du, dass der Linter wirklich anspringt:

```powershell
# 1. Fuege in 05_to_be.html irgendwo „Infinitiv" ein und speichere.
#    Konsole sollte zeigen:
#    FAIL grammatik/05_to_be.html  (1 Verstoss/Verstoesse)
#      -> [forbidden-term]:NN  Verbotener Fachbegriff im sichtbaren Text: "Infinitiv".

# 2. Aenderung zuruecknehmen, speichern.
#    Konsole sollte zeigen:
#    OK   grammatik/05_to_be.html
```

## Generator: neue Grammatikdatei

### Aufruf

Argumentbasiert (alles in einem Schritt):

```powershell
py scripts\new_grammar.py --grade 6 --topic conditional_1 --unit 3 `
   --display "Conditional I" `
   --sub "Real conditional · if + Simple Present"
```

Interaktiv (Eingaben werden abgefragt):

```powershell
py scripts\new_grammar.py
```

### Optionen

| Flag | Default | Zweck |
|---|---|---|
| `--grade N` | (Pflicht / Abfrage) | Klassenstufe 5/6/7/8/9/10. |
| `--topic SLUG` | (Pflicht / Abfrage) | snake_case-Slug, z. B. `conditional_1`. |
| `--unit N` | (Pflicht / Abfrage) | Lighthouse-Unit-Nummer. |
| `--display NAME` | aus Topic abgeleitet | Anzeigename (z. B. „Conditional I"). |
| `--sub TEXT` | „TODO: kurze Beschreibung ergaenzen" | Untertitel der Tile (Dashboard). |
| `--icon EMOJI` | `📕` | Icon der Tile. |
| `--short KEY` | aus Topic abgeleitet | Kuerzel fuer Tile-ID (`g-<grade>-<short>`). |
| `--ls-prefix STR` | aus Topic abgeleitet | LocalStorage-Praefix fuer alle Keys. |
| `--force` | – | Existierende Zieldatei ueberschreiben. |
| `--cleanup PATH` | – | Aufraeum-Modus: Datei + Tile entfernen. |

### Was wird erzeugt

1. **HTML-Stub** unter `grammatik/<grade:02>_<topic>.html` – mit:
   - allen drei `shared/`-CSS-Includes,
   - 3 leeren Konzept-Karten (Hinweis auf Pflicht-Karten bei Tense-Themen),
   - 3 leeren Aufgaben-Akkordeons mit korrektem Markup-Skelett,
   - `<div id="tutor-mount"></div>`,
   - `window.TUTOR_CONFIG` mit allen Pflicht-Feldern (TODO-Platzhaltern),
   - LocalStorage-Wrapper (`tbSave`/`tbLoad`) mit dateispezifischem Praefix,
   - `setupSection`-Aufrufen fuer alle drei Akkordeons,
   - leerem `quizPool` plus `HRQuiz.init`-Aufruf,
   - `HRShared.initDarkMode` / `initTTS` / `initResetAllButton`-Aufrufen,
   - Akkordeon-Persistenz,
   - Footer mit aktueller Versions-Zeitangabe.
2. **Tile in `index.html`** – an der richtigen Stelle nach Sortier-Regel (Klasse aufsteigend, dann Unit aufsteigend) eingefuegt.
3. **Versions-Bump** – `DEFAULT_CONFIG.version` wird automatisch um 1 erhoeht.
4. **Linter-Verifikation** – das Skript ruft am Ende `lint_watcher.py --file ...` auf der neuen Datei auf. Pflicht-Struktur muss erfuellt sein.

### Cleanup

Zum Entfernen einer (Test-)Datei:

```powershell
py scripts\new_grammar.py --cleanup grammatik\99_test_topic.html
```

Loescht die Datei und entfernt die zugehoerige Tile aus `index.html` (per Dateiname-Match, ID-unabhaengig). Versions-Bump erfolgt erneut – die Konfiguration ist also versioniert.

## Bekannte Einschraenkungen

- **Pronomen-Tabellen-Check** ist heuristisch und kann False-Positives liefern, wenn ein Aufgabentext zufaellig „he/she/it" enthaelt. Falls noetig, Regel `pronoun-cluster-in-card` mit `# noqa`-Kommentar im Markup ignorieren – aktuell nicht implementiert, kann auf Zuruf nachgereicht werden.
- **JS-Syntax-Check** setzt eine globale `HRQuiz`/`HRShared`-Verfuegbarkeit voraus. `node --check` prueft nur Syntax, nicht Semantik – fehlende Funktionen werden zur Laufzeit, nicht zur Lintzeit erkannt.
- **HTML-Tag-Balance** ist eine grobe Zaehlheuristik. Selbstschliessende Tags (`<br>`, `<img>`) sind ausgenommen. Bei verschachtelten `<details>`-Strukturen kann es zu False-Positives kommen, wenn ein `<details>` durch einen Kommentar geoeffnet, aber im Kommentar nicht geschlossen wird.

## Phase 3 (geplant, separat)

Hash-Versionierung ist die naechste Stufe und wird separat angegangen.
