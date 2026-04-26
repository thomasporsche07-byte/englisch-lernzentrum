# Englisch-Lernzentrum – Projekt-Spec für Claude

Verbindliche Spec für jede neue Grammatikdatei. Vor Arbeitsbeginn lesen.

## Vorab: Referenzdatei lesen

Vor jeder neuen Grammatikdatei eine bestehende öffnen und Konventionen 1:1 spiegeln. Nichts neu erfinden.

Aktuelle Referenzen:
- `grammatik/06_will_future.html` — Vollausstattung inkl. WWM-Quiz
- `grammatik/08_past_perfect.html` — Vollausstattung inkl. WWM-Quiz
- `grammatik/05_simple_present.html` — Einfachere Variante

## Standardstruktur Grammatikdatei

Jede neue Datei in `grammatik/<NN>_<thema>.html` enthält in dieser Reihenfolge:

### 1. Regelkarten (`section.rules-combined`)

- 3–6 Karten je nach Themenumfang
- Klassen `c-green`, `c-red`, `c-blue`, `c-indigo`, `c-amber`, `c-teal` für Farb-Varianten
- Pro Karte: Label, Formel-Box (`.fc`-Tags), Regel-Text, Beispiele mit Highlights
- Gleiche CSS-Variablen wie Referenzdatei
- Grid: 3 Spalten Desktop, 2 Spalten ab 900px, 1 Spalte ab 600px

#### ⚠️ Pflicht: Pill-Formeln müssen auf 375 px sauber wrappen

Pill-Formel-Zeilen mit `<span class="fc">…</span>` und `<span class="fc-plus">OP</span>` MÜSSEN auf einer Smartphone-Breite von 375 px (oder schmaler) ohne Layout-Bruch umbrechen — keine alleinstehenden `+` am Zeilenende, keine alleinstehenden Pills am Zeilenanfang.

**Verbindliches CSS-Pattern** (in jede Datei aufnehmen):

```css
.rc-formula{display:flex;flex-wrap:wrap;align-items:center;gap:6px 4px}
.fc-pair{display:inline-flex;align-items:center;gap:3px;white-space:nowrap;flex-shrink:0}
.fc{…;flex-shrink:0}
```

**Verbindliches HTML-Pattern**: Jeder Operator `+` / `→` / `=` / `·` / `/` wird ZUSAMMEN mit der direkt folgenden Pill in eine `.fc-pair` gepackt. So bricht das Operator-Pill-Paar nie auseinander.

```html
<!-- ❌ Falsch -->
<span class="fc fc-subj">Subjekt</span><span class="fc-plus">+</span><span class="fc fc-verb">Verb</span>

<!-- ✅ Richtig -->
<span class="fc fc-subj">Subjekt</span><span class="fc-pair"><span class="fc-plus">+</span><span class="fc fc-verb">Verb</span></span>
```

**Mehrzeilige Formeln** (z. B. „Adjektiv + Nomen / Verb + Adverb"): NICHT `<br>` in `.rc-formula` einfügen — stattdessen zwei separate `<div class="rc-formula">` untereinander.

Test pflicht auf 3 Breiten: ≥1024 px / 768 px / 375 px.

#### ⚠️ Pflicht-Karten für Tense-Grammatikdateien (Zeitformen)

Bei allen Grammatikdateien zu **Zeiten/Tenses** (Simple Present, Will Future, Present Perfect, Past Perfect, Simple Past, Past Continuous, …) sind **genau diese 6 Karten Pflicht** und in dieser Reihenfolge:

| # | Klasse | Label | Inhalt |
|---|---|---|---|
| 1 | `c-green` | ✅ Aussagesatz | Bildung des positiven Satzes |
| 2 | `c-red` | ❌ Verneinung | Negation (don't/doesn't, won't, hasn't …) |
| 3 | `c-blue` | ❓ Ja/Nein-Frage | Frage + Short Answers |
| 4 | `c-indigo` | 🔵 W-Frage | W-Wort + Hilfsverb + Subjekt |
| 5 | `c-amber` | ⏱ Wann benutze ich es? | Verwendungszweck + 2–3 Beispielsätze |
| 6 | `c-teal` | 📌 Signalwörter | typische Signalwörter als `fc-tz`-Chips |

Referenzdatei: `grammatik/08_past_perfect.html` (Karten-Aufbau 1:1 spiegeln, nur Inhalt anpassen).

**Bei Nicht-Tense-Themen** (some/any, Adverbien, Word Order, …) gilt diese Pflicht nicht — Karten frei nach Themen.

### 2. Übungs-Akkordeons mit L1/L2/L3-Pools

- `<details class="accordion" id="acc-<key>">` mit `<summary>` — **kein `open`-Attribut** (alle Akkordeons starten geschlossen)
- Pro Akkordeon: `level-switch`, `progress-wrap`, `section-actions` (Alle prüfen / Zurücksetzen / Neu würfeln), Tasks-Container
- Multi-Level-Sektionen via `setupSection()`, einfache Sektionen via `setupSimpleSection()`
- Pool-Typen pro Aufgabe:
  - `{type:"mc", prompt, options:[…], correct:idx, answer}` — Multiple Choice
  - `{words:[…], answer:[…], label}` — Wörter ordnen (Tap-to-Order Tiles)
  - `{prompt, answer:[…], placeholder?, explanation?}` — Freitext (auch Lücken, Umformung, Fehlerkorrektur)
- L1 = Erkennen (MC + Ordne), L2 = Anwenden (Lücken/Freitext), L3 = Transfer (Umformen/Fehlerkorrektur)
- Mindestens 15 Aufgaben pro L1/L2/L3-Pool, 12 für simple Sektionen
- Realistischer Wortschatz der Zielklasse (Lighthouse-Vokabular)

### 3. WWM-Quiz (Wer-wird-Millionär-Stil)

**Pflichtbestandteil. Implementierung 1:1 aus Referenzdatei kopieren.**

Markup:
```html
<div class="quiz-divider"><span>🏆 Teste dein Wissen</span></div>
<details class="accordion" id="wwm-quiz">
  <summary>🏆 Quiz</summary>
  <div class="content">
    <div class="progress-wrap" id="quiz-progress">
      <div class="progress mixed" role="progressbar" aria-valuemin="0" aria-valuemax="100">
        <div class="progress-fill"></div>
      </div>
      <div class="progress-text">Fortschritt: 0/15 richtig (0%)</div>
    </div>
    <div class="section-actions"><button class="btn gray" id="quiz-reset">Zurücksetzen</button></div>
    <div id="quiz-tasks"></div>
    <div id="quiz-result" class="result-card" style="display:none"></div>
  </div>
</details>
```

JS: `quizPool` (15 Fragen) + `(function initQuiz(){…})()` IIFE komplett aus Referenz übernehmen — keine eigene Variante.

Pflicht-Features (alle aus Referenz übernommen):
- Geldleiter (`wwm-amounts`, Meilensteine bei Index 4/9/14)
- 3 Joker: 50:50 (`fifty`), Telefonjoker (`phone`), Publikumsjoker (`audience`) — Joker dürfen mit ~30 % auch falsch liegen
- Streak-Anzeige bei 3+ richtigen in Folge
- Timer
- Ergebnis-Karte (`showFinal`) mit Emoji, Headline, Score, gewonnenem Betrag, Fehlerliste
- Gerendert erst beim ersten Öffnen des Akkordeons (`toggle`-Listener)

Quizfragen (15 Stück):
- **d=1** (4 Fragen): Grundregel-Erkennung, klare MC
- **d=2** (5 Fragen): Kontextverständnis, mittlere Schwierigkeit
- **d=3** (6 Fragen): Bedeutungsnuance, Fehlerkorrektur, Edge Cases
- Jede Frage: `{prompt, options:[4 Strings], correct:0–3, tip, explanation, d:1–3}`
- 4 Optionen pro Frage (auch wenn weniger pädagogisch nötig — Geldleiter-Layout)
- **Plausible Distraktoren** — typische Schülerfehler einbauen, keine offensichtlich falschen

### 4. Footer

```html
<footer style="text-align:center;color:#b8905a;font-size:12px;margin-top:30px;padding:16px 20px 4px;border-top:1px solid rgba(184,144,90,.25)">
  <div>Version DD.MM.YYYY, HH:MM</div>
  <div style="margin-top:6px">Der Inhalt dieser Datei ist KI-generiert und kann fehlerhaft bzw. lückenhaft sein. © Thomas Porsche</div>
</footer>
```

Datum/Uhrzeit bei jeder Änderung aktualisieren. Format: `DD.MM.YYYY, HH:MM` (24h).

## Dashboard-Integration

Nach Anlage der Datei: Eintrag in `index.html` `DEFAULT_CONFIG.tiles[]`.

- Position: einsortiert nach Sortier-Regeln (siehe unten)
- ID-Schema: `g-<grade>-<short>` (Grammatik-Präfix + Klasse + Kürzel, z.B. `g-06-saf` für some/any/few)
- Pflichtfelder:
  ```js
  {id, title, sub, category:"grammatik", grade, subcat:"", file, icon, status, visible, since?}
  ```
- `status:"new"` mit `since:"YYYY-MM-DD"` setzen (Badge läuft nach 14 Tagen automatisch ab)
- Icon: passend zur Themenfarbe, möglichst Buch-Emoji (📗📘📙📕) für Grammatik
- Index-Footer-Datum ebenfalls aktualisieren

### Sortier-Regeln in `DEFAULT_CONFIG.tiles[]`

Diese Reihenfolge ist verbindlich. Bei jeder neuen Kachel prüfen, dass sie an der richtigen Stelle eingefügt wird.

**Grammatik-Block:**
1. Zuerst nach Klassenstufe aufsteigend (5 → 6 → 7 → 8 → 9 → 10)
2. Innerhalb derselben Klasse: nach Lighthouse-Unit-Nummer aufsteigend (Unit 1 → Unit 2 → … → Unit 6)
3. Mehrere Themen in derselben Unit: nach Erstellungszeitpunkt der Unterseite (älter zuerst)

Beispiel Klasse 6: `g-06-saf` (Unit 4) steht vor `g-06-wf` (Unit 5).

**Vokabeln-Block:**
1. Zuerst nach Klassenstufe aufsteigend (5 → 10)
2. Innerhalb derselben Klasse: nach Unit-Nummer aufsteigend (Unit 1 → Unit 2 → …)
3. Drafts/Platzhalter werden ebenfalls nach Klasse + Unit einsortiert (nicht ans Ende verschoben)

Beispiel Klasse 5: `v-lh1-u01` (Unit 1, draft) steht vor `v-lh1-u4` (Unit 4, ready).

**Andere Kategorien (Skills, Übergreifend, ZAP):** keine spezifische Sortier-Regel, aktuelle Reihenfolge beibehalten.

### ⚠️ Versions-Bump pflicht

Bei JEDER Änderung an `DEFAULT_CONFIG.tiles[]` (neue Kachel, geänderter Titel, anderer Dateiname, neues Icon, neuer Status, entfernte Kachel) MUSS `DEFAULT_CONFIG.version` um 1 erhöht werden.

```js
const DEFAULT_CONFIG = {
  version: 2,   // ← bumpen!
  tiles: [ ... ]
};
```

Hintergrund: Schüler/Eltern speichern die Konfiguration in `localStorage` (`dashboard_config_v3`). Ohne Versions-Bump bleibt die alte Konfig im Browser-Cache, neue Kacheln/Titel/Icons werden NICHT sichtbar.

Bei Versions-Bump läuft `mergeWithDefaults()` automatisch und aktualisiert smart:
- ✓ Default-Felder (`title`, `sub`, `file`, `icon`, `status`, `since`, `subcat`, `grade`, `category`) werden überschrieben
- ✓ Lehrer-Anpassungen bleiben erhalten: Reihenfolge (Drag&Drop), `visible`-Flag, eigene Custom-Kacheln (IDs ohne Standard-Präfix `g-`/`v-`/`s-`/`u-`/`z-`)
- ✓ Neue Default-Tiles werden an passender Position eingefügt
- ✓ Aus DEFAULT_CONFIG entfernte Default-Tiles werden gelöscht (Custom bleibt)

## Konventionen

### Dateinamen
- Schema: `<Klassenstufe>_<thema>.html`
- Präfix = Klassenstufe (5/6/7/8/9/10), **NICHT sequentiell**
- Mehrere Dateien pro Klasse möglich (z.B. `06_will_future.html` + `06_some_any_little_few.html`)
- Thema in snake_case, kein Umlaut

### Terminologie (Schüler-Sicht)
- „past participle" statt „V3"
- „countable / uncountable" als Standardvokabular ab Klasse 6
- „Grundform" statt „Infinitiv"
- Deutsche Erklärtexte, englische Beispielsätze

### Sprache / Stil (Pflicht)
- **Keine Fachbegriffe ohne Schülerverständnis.** Vermeide z. B. „partiell", „nominal", „Auxiliarverb", „Kopula", „elliptisch", „Modalverb-Periphrase".
- Stattdessen schülergerechte Synonyme: „halb" / „teilweise gleich", „Substantiv" / „Hauptwort", „Hilfsverb".
- Im Zweifel: Wäre das ein Wort, das ein 12-Jähriger versteht? Wenn nein → ersetzen.
- Die Regel gilt für alle sichtbaren Texte (Karten, Badges, Tooltips, Erklärungen). Code-Variablennamen dürfen Fachbegriffe enthalten (sind nicht für Schüler).

### Übergreifend-Wortschatzdateien: Schwierigkeit statt Klasse
- Bei **übergreifenden** Wortschatzdateien (Dateien in `uebergreifend/`, die kein klares Lighthouse-Unit-Mapping haben) Standardmäßig **Schwierigkeits-Tagging** statt Klassen-Tagging:
  - Datenmodell: jeder Eintrag bekommt `diff: 1 | 2 | 3` (1 = leicht, 2 = mittel, 3 = schwer).
  - Anzeige: sortiert nach `diff` aufsteigend, innerhalb gleicher Stufe alphabetisch.
  - Sichtbares Signal pro Karte: dezenter Tag mit Punkten + Label („leicht / mittel / schwer"), keine Klassenangabe.
  - Kein Klassen-Filter im UI – Schüler sehen alle Einträge auf einmal.
- Klassengetrenntes Tagging (`grade: 5..10`) bleibt für **klassengebundene** Inhalte (Lighthouse-Units, Klassen-Grammatik) der Standard.
- Bei Bedarf darf `grade` zusätzlich im Datenmodell stehen (interne Reserve), wird aber im UI nicht ausgewertet.
- Referenz-Implementierung: `uebergreifend/false_friends.html` (`diff:`-Feld, `sortByDiffThenAlpha()`, `diffTagHTML()`).

### Dashboard-Titel
- Schema: `Unit X – Thema` (X = Lighthouse-Unit, in der das Thema eingeführt wird)
- Bei thematisch übergreifenden Dateien (mehrere Units betroffen): nur `Thema` ohne Unit-Präfix

### Style-Konventionen
- Designsystem: Terrakotta/Creme (`--hr-blue:#b85c20`, `--bg:#fef9f2`)
- Font: `Baloo 2`
- Dark-Mode: über `body.dark-mode` gesteuert, `localStorage`-Key projektspezifisch (z.B. `samllf_dark_v1`)
- Print-Styles vorhanden (Aufgaben sichtbar, Controls/Solutions ausgeblendet)

### Button-Layout (Pflicht in jeder Grammatik-Datei)

Drei feste Bildschirm-Ecken-Buttons – Position 1:1 aus `05_simple_present.html` übernehmen:

| Button | Position | CSS-Klasse | Zweck |
|---|---|---|---|
| 🌙 Dark Mode | **oben rechts** (`top:14px;right:16px`) | `.dark-toggle` | Dark/Hell umschalten |
| 🔊 Vorlesen | **unten links** (`bottom:46px;left:16px`) | `.tts-toggle` | TTS für LRS-Schüler |
| 🗑️ Zurücksetzen | **unten links** (`bottom:14px;left:16px`) | `.reset-all-btn` | Globaler Fortschritts-Reset |

Reihenfolge im HTML: dark-toggle, tts-toggle, reset-all-btn (DOM-Reihenfolge irrelevant, da fixed positioniert).

**TTS-Modul** (`var TTS={…}`): komplett 1:1 aus `05_simple_present.html` (Zeilen ~2289–2430) übernehmen, inkl. CSS-Klassen `.tts-btn`, `.tts-flag-btn`, `@keyframes tts-pulse`, `body.dark-mode .tts-toggle`. Liest Aufgaben-Prompts (DE/EN automatisch erkannt), Lösungen und gelöste Sätze beim Aktivieren.

⚠️ Mobile-Breakpoint: nur `.dark-toggle` wird `position:static` (Hamburger-Stil). `.tts-toggle` und `.reset-all-btn` bleiben fixed unten (nur Padding/Schriftgröße kleiner).

## Pflicht-Verifikation (vor Abschluss)

Nach jeder Änderung an einer HTML-Datei automatisch prüfen:

1. **HTML-Tag-Balance**: Öffnende = schließende Tags für `html, head, body, div, section, details, summary, style, script, header, footer`
2. **JS-Syntax**: `new Function(scriptBlock)` muss ohne Fehler durchlaufen (oder `node --check` auf extrahierten Block)
3. **Pool-Validierung**:
   - Alle MC-Aufgaben: `options.length >= 2` (Quiz: genau 4), `correct` in Range, `correct`-Index zeigt auf erwartete Antwort
   - Alle Wörter-Ordnen: `words.length > 0`, `answer` vorhanden
   - Alle Freitext: `prompt` und `answer` vorhanden
4. **Quiz-Spezifisch**: `quizPool.length === 15`, Verteilung d=1:4, d=2:5, d=3:6, alle Fragen haben `tip` und `explanation`
5. **Ergebnis-Karte pro Akkordeon**: Jedes Übungs-Akkordeon zeigt nach Abschluss ein Ergebnis. Pattern 1:1 aus `grammatik/05_simple_present.html`:
   - `checkCelebration(container)` → grünes `.celebrate-banner` „🎉 Perfekt!" bei 100 % korrekt
   - „Alle prüfen"-Klick → farbiger `.result-banner` (grün/orange/rot je nach %) + `.error-list` mit allen falsch beantworteten Aufgaben
   - Aufruf erfolgt aus `updateProgress()`-Hook bzw. `checkAllBtn`-Handler
   - CSS-Klassen `.celebrate-banner` (`@keyframes celebrate-pop`), `.result-banner`, `.error-list` müssen vorhanden sein
   - Reset-Buttons müssen alle drei Banner-Typen entfernen
6. **Footer-Datum**: aktuell

## Bekannte Fallstricke

### Quote-Encoding in JS-Strings
Deutsche Anführungszeichen `„…"` brauchen schließendes `"` (U+201C), NICHT `"` (ASCII 34) — sonst terminiert die JS-String-Definition vorzeitig.

Falsch: `"… kein „two milks"."` (ASCII-Quote schließt String)
Richtig: `"… kein „two milks"."` (mit U+201C als schließendem Quote)

### Datei-Größe beim Schreiben
Sehr große Dateien (>92 KB) können beim direkten Write trunkiert werden. Strategie:
- Ersten Teil mit `Write` schreiben
- Rest mit `bash` und `cat >> file << 'EOF'` anhängen
- Am Ende immer Tag-Balance + JS-Syntax verifizieren

### LocalStorage-Keys eindeutig
Dark-Mode-Key pro Datei eindeutig wählen (z.B. `<topic>_dark_v1`), sonst Konflikte zwischen Seiten.


## Shared-Modules-Architektur (ab Phase 1a)

Seit dem Refactor liegen wiederverwendbare Bestandteile zentral unter `shared/`. Eine Grammatikdatei lädt sie nur noch und liefert die topic-spezifischen Daten.

### Was liegt zentral (`shared/`)

| Datei                         | Inhalt                                                                                                    |
|-------------------------------|-----------------------------------------------------------------------------------------------------------|
| `shared/style.css`            | Variablen, Layout, Header, Container, Akkordeon-Basis, Regelkarten, Pill-Formeln (`.fc/.fc-pair/.fc-plus`), Aufgaben (`.task`), MC, Wörter-Ordnen, Buttons, Score-Karten (Banner/Error-List/Celebrate), Drei-Ecken-Buttons (Dark/TTS/Reset), Quiz-Divider, Confirm-Modal-Stil, alle Dark-Mode-Switches. |
| `shared/quiz.css`             | WWM-Quiz-Styles (Geldleiter, Joker-Optionen, Phone-/Audience-Boxen, Quiz-Bühne, Quiz-Result-Karte).        |
| `shared/quiz.js`              | WWM-Quiz-Logik. `window.HRQuiz.init(quizPool, options)` initialisiert das Quiz, wenn `#wwm-quiz`, `#quiz-tasks` und `#quiz-result` im DOM existieren. Erst beim ersten Öffnen des Akkordeons gestartet. |
| `shared/scorecards.js`        | Globale Helfer in `window.HRShared`: `shuffle`, `initProgressBar`, `checkCelebration`, `showResultBanner`, `clearBanners`, `initDarkMode`, `initTTS` (setzt zugleich `window.TTS`), `customConfirm` (auch global), `initResetAllButton`. |
| `shared/tutor.css`            | Stile für KI-Tutor-Akkordeon (`#acc-ki`, Welcome-Karte, Quick-Chips, Chatbubbles, Eingabezeile, Typing-Indicator). |
| `shared/tutor.js`             | KI-Tutor-Logik. Liest `window.TUTOR_CONFIG`, lädt `tutor_base_prompt.txt` per `fetch`, baut System-Prompt, injiziert das Akkordeon in `#tutor-mount` und exportiert `window.kiSend`/`window.kiClear`. |
| `shared/tutor_base_prompt.txt`| Gemeinsamer Lehrer-Prompt (Realschule, Klasse 5–10, Lighthouse/Camden Market, sehr einfache Sprache, keine Fachbegriffe ohne Schülerverständnis, max. 4 Sätze, keine fertigen Lösungen). |

### Was bleibt pro Datei (topic-spezifisch)

- Header (Titel, Klasse/Unit, Logo)
- Regelkarten-Markup (Texte, Beispiele, Pill-Klassen-Wahl)
- Akkordeon-Markup mit den fünf bzw. sechs Übungs-Sektionen + WWM-Quiz
- **Akkordeon-Farbig­machung** für die topic-spezifischen IDs (`#acc-aus`, `#acc-frag`, …) – das CSS hierfür im Inline-`<style>` lassen.
- Pool-Daten (`xL1`, `xL2`, `xL3`, …) und `quizPool`
- Topic-spezifische `setupSection()`/`renderTask()`-Implementierung (kann bei zukünftigen Refactors weiter zentralisiert werden – Phase 1b/2).
- `window.TUTOR_CONFIG` mit topic-spezifischen Texten
- Init-Aufrufe (`HRShared.initDarkMode`, `HRShared.initTTS`, `HRShared.initResetAllButton`, `HRQuiz.init`)
- Datei-spezifische LocalStorage-Keys (z. B. `tobe_*`, `pas_*`)
- Footer

### Pflicht-Pattern für `<head>`-Includes

```html
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Baloo+2:wght@400;500;600;700;800&display=swap" rel="stylesheet">
<link rel="icon" type="image/svg+xml" href="data:image/svg+xml,...">

<link rel="stylesheet" href="../shared/style.css">
<link rel="stylesheet" href="../shared/quiz.css">
<link rel="stylesheet" href="../shared/tutor.css">

<style>
  /* topic-spezifisches CSS — nur Akkordeon-Farben & Task-Hintergründe pro Section-ID */
</style>
```

### Pflicht-Pattern für `<script>`-Reihenfolge (vor `</body>`)

```html
<!-- 1. Shared scripts: definieren window.HRShared und window.HRQuiz -->
<script src="../shared/scorecards.js"></script>
<script src="../shared/quiz.js"></script>

<!-- 2. Inline script: TUTOR_CONFIG + Pool-Daten + setupSection-Definition + Init-Aufrufe -->
<script>
  window.TUTOR_CONFIG = { /* … */ };
  // Pool-Daten
  // Helper- und setupSection-Implementierungen
  // Init: setupSection(...) × 4-6, HRShared.initDarkMode/TTS/ResetAll, HRQuiz.init
</script>

<!-- 3. Tutor zuletzt: konsumiert window.TUTOR_CONFIG -->
<script src="../shared/tutor.js"></script>
```

Die Reihenfolge ist verbindlich:
1. Shared definieren `HRShared`/`HRQuiz` als Globale, bevor das Inline-Script sie aufruft.
2. Das Inline-Script setzt `TUTOR_CONFIG` und führt die Inits aus.
3. `tutor.js` liest `TUTOR_CONFIG` und injiziert das Tutor-Akkordeon in `#tutor-mount`.

### Pflicht-DOM-Elemente in der Topic-Datei

- `<div id="confirm-modal" style="display:none" class="confirm-overlay">…</div>` direkt nach `<body>` – wird von `HRShared.customConfirm` benötigt.
- `<button class="dark-toggle"  id="dark-toggle">🌙 Dark Mode</button>`
- `<button class="tts-toggle"   id="tts-toggle">🔊 Vorlesen</button>`
- `<button class="reset-all-btn" id="reset-all-btn">🗑️ Zurücksetzen</button>`
- `<div id="tutor-mount"></div>` an gewünschter Stelle (Tutor injiziert hier sein Akkordeon).
- `<details id="wwm-quiz">…</details>` mit `#quiz-progress`, `#quiz-tasks`, `#quiz-result`, `#quiz-reset` (siehe Referenzdatei).

### TUTOR_CONFIG-Schema

```js
window.TUTOR_CONFIG = {
  topic:           "to be (am/is/are)",     // Pflicht – wird in Welcome-Karte und Akkordeon-Titel verwendet
  grade:           5,                        // Klassenstufe 5–10
  unit:            1,                        // Lighthouse-Unit
  rules: [                                   // Kurzform der Regelpunkte → erscheinen als Badges
    "I → am", "he/she/it → is", "you/we/they → are"
  ],
  welcomeMessage:  "<strong>👋 …</strong>…", // HTML erlaubt; ersetzt den Default-Begrüßungstext
  quickChips: [                              // 3-5 Beispielfragen als anklickbare Chips
    "Wann nehme ich am, is oder are?",
    "Prüfe diesen Satz: She are happy."
  ],
  typicalErrors: [                           // Wird in den System-Prompt eingebaut, damit der Tutor gezielt darauf eingehen kann
    "„I are\" oder „I is\" statt „I am\""
  ],
  // Optional:
  mountId:         "tutor-mount",            // Default: "tutor-mount"
  endpoint:        "https://…",              // Default: bekannter Worker-URL
  basePromptUrl:   "../shared/tutor_base_prompt.txt"
};
```

### Topic-spezifische LocalStorage-Keys

Jede Datei nutzt einen eindeutigen Präfix (z. B. `tobe_`, `pas_`, `pre_`):

- `<topic>_dark_v1`       – Dark-Mode-Persistenz (übergeben an `HRShared.initDarkMode(btnId, lsKey)`)
- `<topic>_<sec>_states`  – Aufgabenstatus pro Sektion
- `<topic>_openAcc`       – zuletzt offenes Akkordeon
- (Reset-All löscht diese Keys via `HRShared.initResetAllButton(btnId, sectionResetIds, lsKeys)`)

### Refactor-Status

- ✅ `grammatik/05_to_be.html` – migriert in Phase 1a (Pilot)
- ⬜ Restliche Grammatikdateien – Phase 1b: schrittweise migrieren, Master-Pattern aus `05_to_be.html` übernehmen
- ⬜ Phase 2: ggf. `setupSection()`/`renderTask()` ebenfalls in ein gemeinsames `shared/sections.js` ziehen

### Bekannter Fallstrick: OneDrive-Sync-Tail-Truncation

OneDrive überschreibt manchmal nur die ersten N Bytes einer Datei und füllt den Rest mit `\x00`-Bytes auf, statt die Datei korrekt zu truncieren. Nach jedem großen `Write` prüfen:
```bash
python3 -c "
with open(PFAD,'rb') as f: d=f.read()
print('bytes:',len(d),'nulls:',d.count(b'\\x00'))
"
```
Falls Nulls vorhanden: trailing `\x00` strippen und Datei mit korrekter Länge zurückschreiben.
