# Englisch-Lernzentrum – Projekt-Spec für Claude

Verbindliche Spec für jede neue Grammatikdatei. Vor Arbeitsbeginn lesen.

## ⚠️ AKTIVE MERKER FÜR CLAUDE

> **Quiz-Implementierung:** Das WWM-Quiz wird pro Datei als Inline-IIFE umgesetzt — `(function initQuiz(){…})()` direkt im topic-spezifischen `<script>`-Block. Logik 1:1 aus Referenzdatei (`grammatik/06_will_future.html` oder `grammatik/08_past_perfect.html`) kopieren. Kein zentrales `shared/`-Modul, kein `HRQuiz.init`.

> **Wort-Wrap bei Tile-Aufgaben:** Bei JEDER Aufgabe, bei der mehrere Buchstaben-Tiles oder Underscore-Lücken ein Wort darstellen (Scramble `.scr-built`, Spell-Clue `.spell-clue`, künftige Buchstaben-Pools), gilt: **kein Wort darf mitten umbrechen — Umbruch nur ZWISCHEN Wörtern.** Pflicht-Pattern siehe Abschnitt „Wort-Wrap bei Tiles" unten. Test auf 375 px / 768 px / 1024 px.

> **Matching-Übung (Vokabeldateien) – Farbpalette:** Die Paar-Farben in `MATCH_COLORS` werden **index-basiert** vergeben (`matched.length % MATCH_COLORS.length`). Pflicht: kuratierte **10-Farben-Palette mit gleichmäßiger Hue-Verteilung**, nicht zufällig/hashbasiert. Keine zwei Farben aus demselben Cluster (kein doppeltes Orange/Braun, kein doppeltes Grün, kein doppeltes Teal/Cyan, kein doppeltes Violett/Indigo) — sonst sehen unterschiedliche Paare optisch ähnlich aus und Schüler vermuten falsche Verwandtschaft. Verbindliche Palette (alle Farben dunkel genug für weißen Text):
>
> ```js
> const MATCH_COLORS=['#C62828','#EF6C00','#827717','#2E7D32','#00838F','#1976D2','#1A237E','#6A1B9A','#AD1457','#5D4037'];
> ```
>
> Hue-Reihenfolge: Rot · Orange · Olivgelb · Grün · Teal · Hellblau · Indigo · Violett · Magenta · Braun. Bei `COUNT_MATCH=10` reicht die Palette ohne Wiederholung pro Runde. Referenz-Implementierungen: `vokabeln/lighthouse_1/unit_4.html`, `vokabeln/lighthouse_1/unit_5.html`, `vokabeln/lighthouse_2/unit_5.html`, `vokabeln/lighthouse_4/unit_4.html`.

> **Memory-Akkordeon (Vokabeldateien) – Paar-Farben:** Beim Memory-Spiel wird **bei jedem Treffer** beiden Karten dieselbe Farbe gegeben (CSS-Variable `--match-col`). Verbindliche **12-Farben-Palette** (für 12 Paare = 24 Karten):
>
> ```js
> const MEMORY_COLORS = ['#C62828','#E65100','#827717','#558B2F','#1B5E20','#00838F','#0277BD','#1A237E','#6A1B9A','#AD1457','#5D4037','#455A64'];
> ```
>
> Hue-Reihenfolge: Rot · Tiefrotorange · Olivgelb · Hellgrün · Tiefgrün · Teal · Stahlblau · Indigo · Violett · Magenta · Braun · Schiefergrau. Index-basierte Vergabe (`MEMORY_COLORS[matched % 12]`). Master: `vokabeln/lighthouse_4/unit_4.html`.

> **Memory-PAIRS pro Klassenstufe:** Die Anzahl der Memory-Paare wird klassenstufen-abhängig in `const PAIRS = …` gesetzt — kleinere Klassen haben weniger Karten, damit das Spiel kognitiv passend bleibt.
>
> | Klassenstufe | `PAIRS` | Karten gesamt | Empf. Grid (Desktop / Mobile) |
> |---|---|---|---|
> | Klasse 5 | **8** | 16 | 4×4 / 4×4 |
> | Klasse 6 | **10** | 20 | 5×4 / 4×5 |
> | Klasse 7+ | **12** | 24 | 6×4 / 4×6 |
> | Klasse 9+ (optional) | bis **14** | 28 | 7×4 / 4×7 |
>
> **Pflicht-Synchronisation pro Datei** beim Anpassen von `PAIRS`:
> 1. `const PAIRS = N;` im `setupMemory()`-Scope
> 2. Note-String: `<div class="note">Decke N Paare auf: …</div>`
> 3. Counter: `<span id="mem-found">✅ Paare: 0/N</span>`
> 4. CSS-Grid: `.mem-grid{grid-template-columns:repeat(<dcols>,1fr);…}` + Mobile-Media-Query
>
> Die `MEMORY_COLORS`-Palette bleibt bei 12 Farben (Modulo-Index) — überschüssige Farben sind unkritisch. Aktuelle Werte: `lighthouse_1/unit_4.html` = 8 (Klasse 5) · `lighthouse_1/unit_5.html` = 8 (Klasse 5) · `lighthouse_2/unit_5.html` = 10 (Klasse 6) · `lighthouse_4/unit_4.html` = 12 (Klasse 8).
>
> **Karten-Größe (kompakt, Standard):** `.mem-card` mit `aspect-ratio:3/4` + `max-width:110 px` pro Spalte → ~110×147 px Desktop, ~80×107 px Mobile. Pflicht-CSS:
>
> ```css
> .mem-grid{display:grid;grid-template-columns:repeat(<N>,minmax(0,110px));gap:7px;margin:14px auto;justify-content:center}
> @media(max-width:600px){.mem-grid{grid-template-columns:repeat(<M>,minmax(0,1fr));gap:5px;max-width:380px}}
> .mem-card{aspect-ratio:3/4;border-radius:8px;…}
> .mem-face{…border-radius:8px;font-size:14px;padding:4px;line-height:1.15;overflow-wrap:break-word;hyphens:auto;…}
> .mem-back{…font-size:21px}
> ```
>
> 4×4-Grid (16 Karten, Klasse 5): 4×110 + 3×7 = **461 px breit**, 4×147 + 3×7 = **609 px hoch** → passt komplett ohne Scrollen ins Schul-Notebook-Sichtfenster (1366×768).

> **Memory-Abschluss-Animation:** Nach dem letzten Paar (a) bleibt das Win-Badge stehen, (b) wird das Karten-Grid nach 1 s ausgeblendet (`opacity` auf 0, dann `display:none`), (c) erscheint stattdessen eine animierte Zusammenfassung — pro Paar eine Zeile mit EN-Wort | → | DE-Übersetzung in der Akzentfarbe, mit der das Paar im Spiel markiert wurde. Verwendet die bestehenden `.match-summary*`-CSS-Klassen (statt Duplikat-Klassen), markiert per `data-mem="1"` zur Unterscheidung. Gestaffelte `fly-in`-Animation 100 ms pro Zeile. Pflicht-Implementierung in jeder Vokabeldatei: `matchedPairs`-State im Match-Branch füllen, `finish()` zeigt Summary an, `render()` löscht alte Summary + setzt Grid-Style zurück (für Reroll/Topic-Switch).

> **PAGE_TITLE in Vokabeldateien muss EINDEUTIG sein.** Schema: `"Lighthouse <N> · Unit <X> · Vokabeln"` (z. B. `"Lighthouse 4 · Unit 4 · Vokabeln"`). Begründung: localStorage-Keys (`pb_*`, `lt_*`, `album_*`) werden aus `PAGE_TITLE.replace(/[^a-zA-Z0-9]/g,'_')` gebildet — bei doppeltem PAGE_TITLE vermischen sich die Daten verschiedener Dateien. **Pflicht:** Migration-Block einbauen, der beim ersten Laden alte Sammel-Keys (`Unit_4___Vokabeln` o. ä.) auf neue eindeutige Keys (`Lighthouse_4___Unit_4___Vokabeln`) umkopiert. Referenz-Implementierung in jeder Vokabeldatei direkt nach `PAGE_SUB`.

> **Master-Datei für Vokabeldateien: `vokabeln/lighthouse_4/unit_4.html`.** Diese hat den vollständigen Feature-Stack (Tranchen A+B+C: Cloze-L4, Tastatur-Shortcuts, Memory mit Farb-Paaren, Leitner-Score, Speech-Recognition, Crossword, System-Dark-Mode, Profil-Button im Header, eindeutiger PAGE_TITLE, Migration-Block). Bei neuen Vokabeldateien diese Vorlage kopieren und nur Inhalte (PAGE_TITLE/PAGE_SUB/TOPICS/VOCAB) ersetzen.

> **Beispielsätze in Vokabel-Datenmodell (`s:"…"`):** Vokabel muss als **unveränderter Wortlaut** in den Placeholder passen. Keine Suffix-Buchstaben (`s`, `es`, `ed`, `ing`, `er`, `est`, `ly`, `'s`, `n't`, `d`) NACH den Underscores anhängen — der Schüler tippt die Vokabel und der gerenderte Satz bleibt mehrdeutig (z. B. „many ________s" sieht aus wie „many spice" statt „many spices"). Stattdessen Beispielsatz so umformulieren, dass die Grundform passt (Singular bei Substantiven, `to`-Infinitiv oder Modalkonstruktion bei Verben). Details siehe Konventions-Abschnitt „Lückentext-Beispielsätze in Vokabeldateien".

<!-- Rekonstruiert nach Refactor-Rollback. Falls dieser Hinweis-Block vor dem Refactor anders formuliert war, hier anpassen. -->

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

#### ⚠️ Pflicht: Wort-Wrap bei Buchstaben-/Lücken-Tiles

Sobald eine Aufgabe ein **Mehrwort-Wort** (z. B. „baking powder", „main course") in mehrere Tiles/Spans zerlegt — sei es Buchstaben-Tiles (Scramble), Underscore-Lücken (Spell-Clue) oder neue ähnliche Pattern — MUSS jedes ganze Wort als untrennbare Einheit gerendert werden. **Umbruch nur ZWISCHEN Wörtern, nie mitten im Wort.**

Falsch (was passierte vor dem Fix):
```
[b][a][k][i][n][g] [p]
[o][w][d][e][r]
```
Richtig:
```
[b][a][k][i][n][g]
[p][o][w][d][e][r]
```

**Verbindliches Pattern (Buchstaben-Tiles in Scramble `.scr-built`):**

CSS:
```css
.scr-built{display:flex;flex-wrap:wrap;align-items:center;justify-content:center;gap:6px 14px;…}
.scr-built .scr-word-group{display:inline-flex;align-items:center;gap:3px;flex-shrink:0;flex-wrap:nowrap;white-space:nowrap}
.scr-built .scr-char{…}
```

JS (Render-Loop): Pro Wort eine `<span class="scr-word-group">` öffnen; bei jedem Leerzeichen (`spacePos`) die aktuelle Gruppe schließen und eine neue starten. NICHT mehr ein Spacer-`<span>` für jedes Leerzeichen einfügen — die Trennung erledigt der Container-Gap.

```js
let li=0;
let wg=document.createElement('span');wg.className='scr-word-group';
for(let pos=0;pos<totalSlots;pos++){
  if(spacePos.has(pos)){
    if(wg.childNodes.length>0)builtEl.appendChild(wg);
    wg=document.createElement('span');wg.className='scr-word-group';
  } else {
    if(li<built.length){
      const s=document.createElement('span');s.className='scr-char';s.textContent=built[li].ch;
      wg.appendChild(s);
    }
    li++;
  }
}
if(wg.childNodes.length>0)builtEl.appendChild(wg);
```

**Verbindliches Pattern (Spell-Clue Text `.spell-clue`):**

CSS:
```css
.spell-clue{display:flex;flex-wrap:wrap;justify-content:center;align-items:center;gap:6px 18px;…}
.spell-clue-word{display:inline-block;white-space:nowrap;flex-shrink:0}
```

JS (`makeClue`): Jedes Wort in einen `.spell-clue-word`-Span wickeln. Innerhalb des Spans dürfen ruhig normale Spaces zwischen den Underscores stehen — `white-space:nowrap` verhindert den Bruch. Trennung zwischen Wörtern via Container-Gap.

```js
function makeClue(answer){
  return answer.split(' ')
    .map(w=>'<span class="spell-clue-word">'+(w[0]+' '+Array(w.length-1).fill('_').join(' '))+'</span>')
    .join(' ');
}
```

**Wort-Tiles** (Aufgabentyp „Ordne die Wörter" mit `.word-tile`/`.wo-chip`): Hier ist jedes Tile bereits ein ganzes Wort — kein In-Wort-Bruch möglich. Nichts zu tun.

Test pflicht auf 375 px mit Mehrwort-Antwort wie „baking powder", „main course".

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
- **Mindestens 40 Aufgaben pro L1/L2/L3-Pool, dem Lernniveau angepasst.** Bei mehrfachem Durchlauf des Schülers sollen neue Aufgaben sichtbar werden. Pool wird pro Durchlauf zufällig durchmischt (`shuffle()` im `setupSection()`-Pattern). Quiz-Pools (15 Fragen) sind davon ausgenommen.
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

JS: `quizPool` (mind. 40 Fragen, Picker zieht 15 pro Runde) + Inline-IIFE `(function initQuiz(){ … })()` mit Geldleiter, 3 Jokern, Streak, Timer, Ergebnis-Karte. 1:1 aus Referenzdatei kopieren. Picker-Aufruf `pickByDifficulty(4,5,6)` (oder analog) ist Pflicht — sonst werden die zusätzlichen Pool-Fragen nie gezogen.

Pflicht-Features:
- Geldleiter (`wwm-amounts`, Meilensteine bei Index 4/9/14)
- 3 Joker: 50:50, Telefonjoker, Publikumsjoker — Joker dürfen mit ~30 % auch falsch liegen
- Streak-Anzeige bei 3+ richtigen in Folge
- Timer
- Ergebnis-Karte (`showFinal`) mit Emoji, Headline, Score, gewonnenem Betrag, Fehlerliste
- Gerendert erst beim ersten Öffnen des Akkordeons (`toggle`-Listener)

Quizfragen (Pool ≥ 40, Picker zieht 15 pro Runde mit Difficulty-Verteilung 4·d=1 / 5·d=2 / 6·d=3):
- Pool-Verhältnis proportional erhalten: ca. **25 % d=1 / 35 % d=2 / 40 % d=3**. Beispiel bei 40 Fragen: 10·d=1 / 14·d=2 / 16·d=3.
- **d=1**: Grundregel-Erkennung, klare MC
- **d=2**: Kontextverständnis, mittlere Schwierigkeit
- **d=3**: Bedeutungsnuance, Fehlerkorrektur, Edge Cases
- Jede Frage: `{prompt, options:[4 Strings], correct:0–3, tip, explanation, d:1–3}`
- 4 Optionen pro Frage (auch wenn weniger pädagogisch nötig — Geldleiter-Layout)
- **Plausible Distraktoren** — typische Schülerfehler einbauen, keine offensichtlich falschen
- Falls eine Datei `pickByDifficulty` nicht aufruft (statisch alle Fragen rendert), Picker ergänzen — sonst wirkt das Pool-Wachstum nicht.

### 4. Footer

```html
<footer style="text-align:center;color:#b8905a;font-size:12px;margin-top:30px;padding:16px 20px 4px;border-top:1px solid rgba(184,144,90,.25)">
  <div>Version DD.MM.YYYY, HH:MM</div>
  <div style="margin-top:6px">Der Inhalt dieser Datei ist KI-generiert und kann fehlerhaft bzw. lückenhaft sein. © Thomas Porsche</div>
</footer>
```

Datum/Uhrzeit bei jeder Änderung aktualisieren. Format: `DD.MM.YYYY, HH:MM` (24h).

## Standardstruktur Vokabeldatei

Pfad: `vokabeln/lighthouse_<N>/unit_<X>.html`. Master: `vokabeln/lighthouse_4/unit_4.html`. Bei neuer Vokabeldatei: Master kopieren, nur PAGE_TITLE / PAGE_SUB / `<title>` / `<h1>` / `<p class="sub">` / TOPICS / VOCAB ersetzen.

### Engine-Features (Pflicht, Reihenfolge wie Master)

| # | Akkordeon | Engine-Funktion | Notizen |
|---|---|---|---|
| 1 | ✏️ Lückentext | `setupGap()` | 4 Stufen: 🟢 MC · 🟡 Wortfeld · 🔴 Freitext (2 Versuche) · 🟣 **Cloze ohne Hilfe** (1 Versuch) |
| 2 | 🔗 Zuordnung | `setupMatch()` | Farbpalette `MATCH_COLORS` (10 Farben) |
| 3 | 🔤 Buchstabensalat | `setupScramble()` | Wort-Wrap-Pattern (siehe oben) |
| 4 | ✍️ Schreibübung | `setupSpelling()` | – |
| 5 | 🎧 Diktat | `setupDictation()` | TTS engl. Aussprache |
| 6 | 🎤 **Aussprache** | `setupSpeech()` | Web Speech API zuverlässig nur in **Chrome (Desktop, Android)** + Edge Desktop. iOS (alle Browser teilen WebKit) liefert oft `aborted` — UA-Hinweis-Banner + Auto-Retry + erklärende Error-Texte sind eingebaut |
| 7 | 🃏 **Memory** | `setupMemory()` | Paar-Anzahl klassenstufen-abhängig (siehe „Memory-PAIRS pro Klassenstufe"), **MEMORY_COLORS-Palette**, animierte Abschluss-Summary (siehe „Memory-Abschluss-Animation") |
| — | section-divider „🎮 Spiele" | – | – |
| 8 | 🏎️ Vokabel-Rennen | `setupRace()` | – |
| 9 | 👾 Vokabel-Invaders | `setupSpaceInvaders()` | – |
| 10 | 🧩 **Kreuzworträtsel** | `setupCrossword()` | Greedy-Solver, 8–10 Wörter |

### Header-Konvention

```html
<header>
  <button class="dark-toggle" id="dark-toggle">🌙 Dark Mode</button>
  <a class="profile-btn-vk" href="../../uebergreifend/lernprofil.html" title="Mein Lernprofil">📊 Profil <span class="streak-pill" id="profile-streak" style="display:none"></span></a>
  <a href="../../index.html" ...><img src="../../assets/logo_hellweg.png" .../></a>
  <h1 id="page-title">Unit X · Vokabeln</h1>
  <p class="sub" id="page-sub">Topic-Beschreibung · Lighthouse N</p>
</header>
```

- `📊 Profil`-Button **fixed top:14px right:160px**, Streak-Pill liest live aus `lp_streak`.
- Dark-Toggle bleibt rechts oben.
- Auf Mobile (≤ 600 px): beide Buttons static, mittig zentriert.

### Leitner-Score (Pool-Bias)

- Helper: `lt_load()`, `lt_save()`, `lt_record(en, ok)`, `lt_pick(arr, n)`.
- `lt_record(en, true)` erhöht Score (clamped −5..+5).
- `lt_pick` zieht **60 % aus den schwächsten 50 %, 40 % random**.
- Score-Range: −5 bis +5 (geclamped).
- localStorage-Key: `lt_<title>` mit Map `{en: score}`.

### Tastatur-Shortcuts (Pflicht)

| Taste | Aktion |
|---|---|
| 1, 2, 3, … | Wählt n-te MC-Option der **obersten sichtbaren** Aufgabe im offenen Akkordeon |
| ↓ / ↑ | Springt zur nächsten/vorherigen `.task` im offenen Akkordeon |
| Enter | (in Inputs) Lösung prüfen |

In Inputs/Textareas werden Zifferntasten ignoriert (sonst kein Tippen möglich).

### System-Dark-Mode (prefers-color-scheme)

```js
// Dark Mode: System-Präferenz als Default, manueller Toggle überschreibt
const stored = localStorage.getItem('darkMode');
const sysDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
const useDark = stored==='1' || (stored===null && sysDark);
```

Bei Live-Änderung der System-Präferenz reagiert die Seite, **solange der User noch keinen manuellen Toggle gesetzt hat**.

### CSS-Pflicht: Body-Höhe & Dark-Mode-Hintergrund

```css
body{min-height:100vh}
html:has(body.dark-mode){background:#111827}
```

Verhindert, dass im Dark Mode der weiße `<html>`-Hintergrund unter kurzem Inhalt durchscheint.

### localStorage-Schlüssel-Schema

| Key-Präfix | Inhalt |
|---|---|
| `pb_<TitleNorm>_<section>` | Aufgaben-Akkordeon-Fortschritt `{c, t}` |
| `lt_<TitleNorm>` | Leitner-Score-Map `{en: score}` |
| `album_<TitleNorm>` | (Legacy, Album entfernt) bestehende Daten bleiben, neue werden nicht mehr geschrieben |
| `mig_title_v1_<TitleNorm>` | Flag: Migration v1 erledigt |
| `lp_streak` | Streak-Counter (datei-übergreifend) |
| `darkMode` | `'1'` / `'0'` (datei-übergreifend) |

`<TitleNorm>` = `PAGE_TITLE.replace(/[^a-zA-Z0-9]/g,'_')`. Pflicht: PAGE_TITLE so wählen, dass `TitleNorm` **eindeutig pro Datei** ist.

### Migrations-Block (Pflicht direkt nach `PAGE_SUB`)

Kopiert beim ersten Laden alte Sammel-Keys auf den neuen eindeutigen Lighthouse-Key. Referenzcode siehe Master `vokabeln/lighthouse_4/unit_4.html` (Funktion `migrateTitleKeysV1`).

## Lernprofil-Datei

- Pfad: `uebergreifend/lernprofil.html`
- Snapshot-only Aggregator über alle `pb_*`/`lt_*`-Keys (Legacy `album_*` werden nur noch beim Reset gelöscht, nicht mehr aggregiert)
- Streak-Counter wird beim Öffnen aktualisiert
- KNOWN_FILES-Map: hardcoded Mapping `<TitleNorm> → {display, path}`. Bei neuer Vokabeldatei dort eintragen.
- Reset-Button löscht alle `pb_/lt_/album_/lp_streak/sect_/boss_*`-Keys.

## ZAP-Operatoren-Datei

- Pfad: `zap/operatoren.html`
- Inhalt 1:1 aus offiziellem **NRW-MSA-Operatorenkatalog** ([Quelle](https://www.standardsicherung.schulministerium.nrw.de/system/files/media/document/file/operatorenliste_msa.pdf))
- 7 Operatoren (describe, summarise/present, point out, explain, compare, comment, discuss) + 4 Textsorten (online article, email/letter, diary entry, continuation of a story)
- Pro Operator: Erläuterung + Beispielaufgabe + ausklappbar: weitere Beispiele · Schreibanfänge & Phrasen · Musterlösung · Übungsaufgabe
- Layout-Konsistenz Aufgabe 3b an 1–3a: weinrote Schrift (`var(--zap)`), Hinweisbox **unter** den Karten

## Dashboard-Integration

Nach Anlage der Datei: Eintrag in `index.html` `DEFAULT_CONFIG.tiles[]`.

- Position: einsortiert nach Sortier-Regeln (siehe unten)
- ID-Schema: `g-<grade>-<short>` (Grammatik-Präfix + Klasse + Kürzel, z. B. `g-06-saf` für some/any/few)
- Pflichtfelder:
  ```js
  {id, title, sub, category:"grammatik", grade, subcat:"", file, icon, status, visible, since?}
  ```
- `status:"new"` mit `since:"YYYY-MM-DD"` setzen (Badge läuft nach 14 Tagen automatisch ab)
- Icon: passend zur Themenfarbe, möglichst Buch-Emoji (📗📘📙📕) für Grammatik
- Index-Footer-Datum ebenfalls aktualisieren
- **`DEFAULT_CONFIG.version` hochzählen** (Integer, +1 bei jeder inhaltlichen Änderung an `tiles[]`). Schüler/Eltern bekommen beim nächsten Reload `mergeWithDefaults()` und damit die neuen Tiles.

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

## Konventionen

### Dateinamen

**Grammatik:**
- Schema: `<Klassenstufe>_<thema>.html`
- Präfix = Klassenstufe (5/6/7/8/9/10), **NICHT sequentiell**
- Mehrere Dateien pro Klasse möglich (z. B. `06_will_future.html` + `06_some_any_little_few.html`)
- Thema in snake_case, kein Umlaut

**Vokabeln:**
- Schema: `vokabeln/lighthouse_<N>/unit_<X>.html`
- `PAGE_TITLE` (in JS) muss eindeutig sein: `"Lighthouse <N> · Unit <X> · Vokabeln"` — sonst localStorage-Kollision

**Übergreifend:**
- Schema: `uebergreifend/<thema>.html`

**ZAP:**
- Schema: `zap/<thema>.html`

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

### Lückentext-Beispielsätze in Vokabeldateien

**Pflicht:** Der Beispielsatz im Vokabel-Datenmodell (`s:"…"`-Feld) muss so formuliert sein, dass die Vokabel als **unveränderter Wortlaut** in den Placeholder eingefügt werden kann. Keine Suffixe (`s`, `es`, `ed`, `ing`, `er`, `est`, `ly`, `'s`, `n't`, `d`) NACH den Placeholder-Underscores anhängen — das ergibt im gerenderten Text mehrdeutige Konstruktionen, die den Schüler verwirren. Beispiel: „many `__________`s" sieht beim Lesen aus wie „many spice" statt „many spices".

**Falsch:**
```js
{en:"spice",   s:"This curry has many __________s.",          h:"…"}  // Plural-s außerhalb
{en:"play",    s:"She __________ed tennis.",                  h:"…"}  // Past-ed außerhalb
{en:"teach",   s:"Mr Brown __________es English.",            h:"…"}  // 3rd-person-es außerhalb
{en:"potato",  s:"We eat __________es a lot.",                h:"…"}  // Plural-es außerhalb
{en:"wave",    s:"She __________d at me.",                    h:"…"}  // Past-d außerhalb
```

**Richtig — Vokabel passt direkt rein:**
```js
{en:"spice",   s:"Pepper is a popular __________.",                  h:"…"}  // Singular
{en:"play",    s:"She wants to __________ tennis.",                  h:"…"}  // Grundform via to-Infinitiv
{en:"teach",   s:"Mr Brown wants to __________ English.",            h:"…"}  // Grundform via to-Infinitiv
{en:"potato",  s:"I want one big __________.",                       h:"…"}  // Singular
{en:"wave",    s:"She wants to __________ at me.",                   h:"…"}  // Grundform via to-Infinitiv
```

**Alternativ — vollständige Wortform als Lemma führen (selten, nur wenn pädagogisch sinnvoll):**
```js
{en:"played",  s:"She __________ tennis yesterday.",          h:"…"}
```

**Konsistenz-Pflicht:** Beim Umformulieren auch das `h:`-Feld (deutsche Übersetzung) anpassen, damit es zum neuen englischen Satz passt. Die Vokabel-Bedeutung (`de:`) und das Stichwort (`k:`) bleiben unverändert.

**Audit-Regex** zum Prüfen einer Datei: `s:"[^"]*_+[a-zA-Z']` — sollte 0 Treffer geben.

### Dashboard-Titel
- Schema: `Unit X – Thema` (X = Lighthouse-Unit, in der das Thema eingeführt wird)
- Bei thematisch übergreifenden Dateien (mehrere Units betroffen): nur `Thema` ohne Unit-Präfix

### Style-Konventionen
- Designsystem: Terrakotta/Creme (`--hr-blue:#b85c20`, `--bg:#fef9f2`)
- Font: `Baloo 2`
- Dark-Mode: über `body.dark-mode` gesteuert, `localStorage`-Key projektspezifisch (z. B. `samllf_dark_v1`)
- Print-Styles vorhanden (Aufgaben sichtbar, Controls/Solutions ausgeblendet)

<!-- Hinweis Rollback: Der ursprüngliche Abschnitt „Button-Layout (Pflicht in jeder Grammatik-Datei)" enthielt eine Tabelle mit drei festen Bildschirm-Ecken-Buttons (🌙 Dark Mode oben rechts, 🔊 Vorlesen, 🧹 Alles zurücksetzen). Da die zugehörige .bak von CLAUDE.md fehlt UND die im Repo verfügbare Quelle (CLAUDE.md auf Festplatte) mitten im Satz abbrach, ist die genaue Tabelle hier NICHT rekonstruiert. Wer die exakte Position/Beschriftung braucht, soll als Source of Truth `grammatik/05_simple_present.html` (jetzt zurückgespielt) lesen — dort steht der echte Markup. -->
