# Projektanweisung: Interaktive Grammatik-HTML-Seiten

**Hellweg-Realschule Unna-Massen – Englisch**
**Stand: 24.04.2026**

---

## 1. Projektziel

Erstellung interaktiver HTML-Lernseiten für den Englischunterricht. Jede Datei behandelt eine Grammatikstruktur und übernimmt vollständig das technische Gerüst, das Design, alle Interaktionsmuster und alle Qualitätsstandards der Masterdatei (`05_simple_present.html`).

**Wichtigster Grundsatz:** Nur der Inhalt ändert sich. Alles andere bleibt gleich.

---

## 2. Dateistruktur und Benennung

### 2.1 Namenskonvention

```
[Jahrgangsstufe]_[thema_kleinbuchstaben].html
```

**Regeln:**

- Ausschließlich **Kleinbuchstaben**
- Trenner ist der **Unterstrich** – keine Leerzeichen, keine Bindestriche, keine Umlaute
- Jahrgangsstufe zweistellig (`05`, `06`, `09`, `10`)

Hintergrund: Die Dateien werden auf GitHub Pages (englisch-lernzentrum) gehostet. URLs mit Leerzeichen, Bindestrichen in Kombination mit Unterstrichen oder Groß-/Kleinschreibungs-Mix führen zu 404-Fehlern. Die strikte Unterstrich-Konvention verhindert das.

### 2.2 Beispiele

| Datei | Status |
|---|---|
| `05_simple_present.html` | ✓ Masterdatei |
| `06_will_future.html` | ✓ vorhanden |
| `08_past_perfect.html` | ✓ vorhanden |
| `word_order.html` | ✓ vorhanden (Meta-Thema, jahrgangsübergreifend) |

**Geplant:**

- `06_going_to_future.html`
- `07_present_progressive.html`
- `08_simple_past.html`

### 2.3 Sonderfall – jahrgangsübergreifende Meta-Themen

Dateien, die keinem festen Jahrgang zugeordnet sind (z. B. `word_order.html`, Schreibtrainer), erhalten **kein Jahrgangspräfix**. Sie liegen im Ordner `uebergreifend/`.

### 2.4 Ordnerstruktur auf dem Hosting (GitHub Pages)

```
/
├── index.html                      (Dashboard)
├── assets/
│   └── logo_hellweg.png            (Schul-Logo, lokal gehostet)
├── grammatik/
│   ├── 05_simple_present.html
│   ├── 06_will_future.html
│   └── 08_past_perfect.html
├── vokabeln/
│   └── lighthouse_<Band>/
│       └── unit_<Nr>.html
├── skills/
│   ├── reading/
│   ├── listening/
│   └── writing/
├── uebergreifend/
│   └── word_order.html
└── zap/
    ├── organisatorisches.html
    ├── operatoren.html
    ├── videos.html
    ├── lernstrategien.html
    ├── hoerverstehen.html
    ├── leseverstehen.html
    ├── wortschatz.html
    └── schreiben.html
```

---

## 3. Was sich zwischen den Dateien ändert

### 3.1 Kopfbereich

- `<title>`: Grammatikthema + Schulname
- `<h1>`: Grammatikthema
- `<p class="sub">`: Beschreibt, **wann** die Grammatik verwendet wird – konkrete Verwendungsfälle, keine allgemeine Umschreibung (z. B. *„Regelmäßige Handlungen · Fakten & Feststellungen · Gewohnheiten · Zeitpläne"*)

### 3.2 Regelkarten (`.rules-combined`)

4–6 Regelkarten, jeweils mit:

- Farbcodierung (c-green, c-red, c-blue, c-indigo, c-amber, c-teal)
- Formel als `.rc-formula` mit farbigen `.fc`-Bausteinen
- Kurze Regel als `.rc-rule`
- Beispiele als `.rc-examples-new` mit farblichen Highlighting-Spans

### 3.3 Videos

Zwei YouTube-Links (Erklärvideo + Übungsvideo) zum neuen Thema.

### 3.4 Übungs-Akkordeons (Abschnitte 1–7)

Anzahl und Themen der Akkordeons anpassen. Typische Struktur:

| Akkordeon | Simple Present | Past Perfect |
|---|---|---|
| 1 | Aussagesätze | Aussagesätze (had + V3) |
| 2 | s-Regel | past participle bilden |
| 3 | Verneinungen | Verneinungen (hadn't) |
| 4+5 | Fragen | Fragen (Had…? / W-Fragen) |
| 6 | Short Answers | Short Answers |
| 7 | Signalwörter | Signalwörter (already, before…) |

### 3.5 Aufgaben-Pools

Für jedes Akkordeon drei Pools (L1, L2, L3) mit mind. 25–35 Aufgaben je Pool.

**localStorage-Key anpassen:** Eigenes Präfix pro Datei (siehe Abschnitt 6).

### 3.6 Quiz-Pool

Mind. 25 Aufgaben mit `d:1`, `d:2`, `d:3` (Schwierigkeit). Enthält alle Aufgabentypen.

### 3.7 KI-Tutor System-Prompt

- Klassenstufe und Thema benennen
- Erklärt die relevanten Grammatikregeln (max. 4 Sätze pro Antwort)
- Gibt keine fertigen Lösungen

---

## 4. Was sich NICHT ändert

Folgendes wird 1:1 aus der Vorlage übernommen — kein Umbau, keine Vereinfachung:

### 4.1 Design-System

**Schriftart:** `Baloo 2` (Google Fonts, Gewichte 400–800)

```html
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Baloo+2:wght@400;500;600;700;800&display=swap" rel="stylesheet">
```

```css
font-family: 'Baloo 2', system-ui, -apple-system, sans-serif;
```

**Farbpalette (warm, aufeinander abgestimmt):**

| Variable | Wert | Verwendung |
|---|---|---|
| `--hr-blue` | `#b85c20` | Primärfarbe (Terrakotta/Amber) |
| `--hr-red` | `#b83a22` | Verneinungen, Fehler |
| `--hr-green` | `#3d7a2e` | Aussagesätze, Erfolg |
| Body-Hintergrund | `#fef9f2` | Warmes Creme |
| Body-Text | `#2c1a0e` | Warmes Dunkelbraun |

Kein Kaltblau (`#1565C0` o. ä.) in der gesamten Datei. Alle Farben warm getönt.

**Vollständige CSS-Regeln für Formel-Chips (`.fc`-Klassen)** – Light + Dark Mode:

```css
.fc-subj   /* Subjekt – Amber (warm) */
.fc-verb   /* Verb – Cyan */
.fc-obj    /* Objekt / past participle – Grün */
.fc-do     /* do/does/had – Gelb */
.fc-neg    /* not/never – Rot */
.fc-sig    /* Signalwörter – Lila gestrichelt */
.fc-wh     /* Fragewörter – Orange */
.fc-s      /* s-Endung – Grün */
.fc-tz     /* Zeitangaben / Signalwort-Chips – Sage/Teal */
```

**Pflicht-Keyframes:**

```css
@keyframes fadeUp { from{opacity:0;transform:translateY(8px)} to{opacity:1;transform:translateY(0)} }
@keyframes bounce { 0%,100%{opacity:.35;transform:translateY(0)} 50%{opacity:1;transform:translateY(-4px)} }
```

**Favicon & klickbares Schul-Logo (verbindlich für alle Lerndateien):**

Jede Lerndatei (außer dem Dashboard selbst) hat:

1. **Union-Jack-Favicon** im `<head>` – identische SVG-data-URL wie im Dashboard, damit alle Browser-Tabs einheitlich aussehen:

```html
<link rel="icon" type="image/svg+xml" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 60 40'><clipPath id='c'><path d='M0 0h60v40H0z'/></clipPath><rect width='60' height='40' fill='%23012169'/><g clip-path='url(%23c)'><path d='M0 0l60 40M60 0L0 40' stroke='white' stroke-width='8'/><path d='M0 0l60 40M60 0L0 40' stroke='%23C8102E' stroke-width='4'/><path d='M30 0v40M0 20h60' stroke='white' stroke-width='10'/><path d='M30 0v40M0 20h60' stroke='%23C8102E' stroke-width='6'/></g></svg>">
```

2. **Schul-Logo im `<header>` als klickbarer Link** zurück zur `index.html`. Logo wird **lokal** aus `assets/logo_hellweg.png` geladen – **keine externen URLs** (Datenschutz, Stabilität). Relative Pfade je nach Ordnertiefe:

| Ordner | Pfad zum Logo | Pfad zum Dashboard |
|---|---|---|
| `/grammatik/*.html` | `../assets/logo_hellweg.png` | `../index.html` |
| `/uebergreifend/*.html` | `../assets/logo_hellweg.png` | `../index.html` |
| `/zap/*.html` | `../assets/logo_hellweg.png` | `../index.html` |
| `/vokabeln/lighthouse_X/*.html` | `../../assets/logo_hellweg.png` | `../../index.html` |
| `/index.html` | `assets/logo_hellweg.png` | (n/a) |

```html
<header>
  <a href="../index.html" title="Zurück zum Englisch-Lernzentrum" style="display:inline-block;text-decoration:none">
    <img src="../assets/logo_hellweg.png" alt="Logo der Hellweg-Realschule Unna-Massen" style="cursor:pointer"/>
  </a>
  <h1>...</h1>
</header>
```

### 4.2 Terminologie

- Die 3. Verbform heißt immer und überall **„past participle"** – niemals „Partizip II", „3. Verbform" allein oder **„V3"**
- Erlaubt: „past participle" oder als Klammerergänzung „past participle (3. Verbform)"
- **Verboten:** „V3" als eigenständiger Begriff in sichtbarem Text (Aufgaben, Erklärungen, Regelkarten, Quiz-Prompts, Tooltips)
- `V3` darf ausschließlich als interner JS-Variablenname verwendet werden (z. B. `ppV3pool`, `acc-v3`)
- Kurzformen (Kontraktionen) immer in beiden Varianten als akzeptierte Antworten angeben (z. B. `hadn't` und `had not`)

### 4.3 Aufgabentypen

Drei Typen – alle müssen vorhanden sein:

**Multiple Choice (`type:"mc"`)**

```js
{type:"mc", prompt:"Fragetext", options:["Option A","Option B","Option C"],
 correct:1, explanation:"✅ Erklärung"}
```

- 3 Optionen, gemischt
- Bei falscher Antwort: richtige wird markiert, kein zweiter Versuch

**Wörter ordnen (Tap-to-Order)**

```js
{words:["Wort1","Wort2","Wort3"], answer:"Wort1 Wort2 Wort3.", label:"Ordne"}
// Mehrere akzeptierte Antworten:
{words:["..."], answer:["Variante 1.","Variante 2."], label:"Ordne"}
```

- Shuffle prüft ALLE Antwort-Varianten
- Satzzeichen-Kachel erscheint nach richtiger Antwort
- TTS: deutscher Prompt + englische Wörter (Text-Labels `🔊 DE` / `🔊 EN`, keine Flaggen-Emojis)

**Freitext**

```js
{prompt:"Aufgabenstellung", answer:["Lösung 1.","Lösung 2."],
 explanation:"💡 Grammatikhinweis"}
```

- Mehrere Antwort-Varianten möglich
- Nach 2 Fehlversuchen: partieller Tipp; nach 3 Fehlversuchen: vollständige Lösung

### 4.4 Interaktionsmuster

- Fortschrittsbalken mit animiertem Reset beim Neu würfeln
- Grünes ✓ im Akkordeon-Titel bei 15/15
- 🎉-Banner bei 15/15 (Entfernung NACH `renderLevel()` platzieren, nicht davor)
- Akkordeons schließen sich beim Öffnen eines anderen
- „Zurücksetzen" mit Custom-Modal (kein `window.confirm`)
- Celebrate-Banner verschwindet beim Zurücksetzen
- Erstes Akkordeon öffnet beim Laden standardmäßig

### 4.5 Niveau-Stufen

Alle Sektionen mit Aufgaben-Pools haben 3 Stufen:

- 🟢 Stufe 1: MC + kurze Ordne-Aufgaben (rezeptiv)
- 🟡 Stufe 2: längere Ordne + einfache Freitext
- 🔴 Stufe 3: komplexe Freitext, Umformungen

Labels beschreiben den Aufgabentyp, nicht die Nummer.

### 4.6 Quiz (WWM-Format)

15 Fragen, aufgeteilt nach Schwierigkeit (ca. 5× d:1, 5× d:2, 5× d:3).

**Akkordeon-Überschrift:** immer nur `🏆 Quiz` – kein Datei-Präfix oder Themenname.

**Eine falsche Antwort beendet das Quiz sofort** (echtes WWM-Prinzip):

- Richtige Antwort, Tipp und Erklärung werden angezeigt
- Gewinn fällt auf letzte Sicherheitsstufe zurück (Fragen 5 und 10)

Sicherheitsstufen: Frage 5 = 1.000 €, Frage 10 = 32.000 €

Drei Joker (einmalig pro Spiel):

- **50:50**: immer korrekt
- **📞 Telefonjoker**: gibt Regelhinweis (zuverlässig)
- **👥 Publikum**: 30 % Chance auf falsche Mehrheit

Quiz-Aufgaben benötigen:

```js
{type:"mc", prompt:"...", options:[...], correct:0,
 tip:"Tipp für Joker", explanation:"✅ Erklärung", d:2}
```

### 4.7 TTS (Vorlesefunktion)

- Regelkarten: **kein TTS**
- Ordne-Aufgaben: Deutsche + englische Text-Buttons (`🔊 DE` / `🔊 EN`) am Prompt
- Freitext + MC: `🔊` am Prompt
- Lösungsboxen: `🔊` wenn sichtbar
- `var TTS` (nicht `const`) – Temporal Dead Zone Fix für iOS Safari
- **Keine Flaggen-Emojis** (🇩🇪 / 🇬🇧) – werden auf Windows/Edge oft nicht farbig gerendert

### 4.8 Regeln-FAB & Sonstige Features

- Dark Mode (localStorage)
- **📋 Regeln-FAB:** Position **unten rechts** (`bottom:20px; right:20px`). Erscheint nur, wenn ein Übungs-Akkordeon geöffnet ist. Klick öffnet ein verschiebbares Modal mit der zum Akkordeon passenden Regelkarte
  - Modal verwendet CSS-Klasse `.show` (nicht `.open`) → `modal.classList.add('show')` / `modal.classList.remove('show')`
  - **`ACC_MAP`** muss auf die Akkordeon-IDs der neuen Datei angepasst werden
- Responsive Regelkarten-Grid:

```css
.rc-grid { grid-template-columns: repeat(3,1fr) }
@media(max-width:900px) { .rc-grid { grid-template-columns: repeat(2,1fr) } }
@media(max-width:600px) { .rc-grid { grid-template-columns: 1fr } }
```

### 4.9 Version-Footer (verbindlicher Standard)

**Jede** HTML-Datei im Projekt (Grammatik, Dashboard, Vokabeln, ZAP, Übergreifend, alle zukünftigen) hat einen zweizeiligen Footer am Seitenende:

```html
<footer style="text-align:center;color:#b8905a;font-size:12px;margin-top:30px;padding:16px 20px 4px;border-top:1px solid rgba(184,144,90,.25)">
  <div>Version TT.MM.JJJJ, HH:MM</div>
  <div style="margin-top:6px">Der Inhalt dieser Datei ist KI-generiert und kann fehlerhaft bzw. lückenhaft sein. © Thomas Porsche</div>
</footer>
```

**Regeln:**

- **Zeile 1:** Datum und Uhrzeit in Zeitzone **Europe/Berlin**, Format `TT.MM.JJJJ, HH:MM`. Bei **jeder** Änderung aktualisieren – auch bei Minor-Edits.
- **Zeile 2:** KI-Disclaimer und Copyright – wortgleich in allen Dateien.
- **Kein** Zusatztext wie „Englisch-Lernzentrum · Hellweg-Realschule Unna-Massen" mehr.
- Farbton leicht an die Datei anpassbar (Grammatik: `#b8905a`, Past Perfect: `#c4a882`, Vokabeln: `#a0845c` …) – Struktur und Inhalt bleiben identisch.

---

## 5. Qualitätsstandards für Aufgaben

### 5.1 Inhaltlich

- Level 1: max. 5–6 Wörter pro Ordne-Aufgabe
- Keine mehrdeutigen Wortstellungen
- Keine Vokabeln über A2-Niveau
- Kontextvielfalt: verschiedene Subjekte (I, she, he, they, we, my mum, Tom, our class…)
- Keine Wiederholung desselben Subjekts in mehr als 3 aufeinanderfolgenden Aufgaben
- Ab L2: Aufgaben, in denen **beide Zeitformen im selben Satz** vorkommen (sofern grammatisch sinnvoll für das Thema)

### 5.2 Technisch

- Jede grammatisch korrekte Antwort muss akzeptiert werden (Array)
- Kontraktionen immer beide Varianten angeben (`don't` / `do not`, `hadn't` / `had not` etc.)
- `normalizeAnswer()` übernimmt Apostroph-Normierung automatisch
- Quiz: `answer`-Feld enthält normalisierte Kleinschreibung, `display` den Anzeigetext

### 5.3 Didaktisch

- L1 schult Erkennen (rezeptiv), L3 schult Produzieren (produktiv)
- Signalwörter: L3 enthält immer Verneinung + Signalwort kombiniert
- `analyzeError()` für häufige Schülerfehler der neuen Grammatik erweitern

---

## 6. localStorage-Verwaltung

Jede Datei bekommt einen eigenen Key-Präfix:

| Datei | LS_KEY (aktuell im Einsatz) |
|---|---|
| `05_simple_present.html` | `sp_progress_v3` |
| `06_will_future.html` | `wf_progress_v1` |
| `08_past_perfect.html` | `pastperf_progress_v1` |
| `word_order.html` | `wo_progress_v1` |
| `07_present_progressive.html` (geplant) | `pp_progress_v1` |
| `08_simple_past.html` (geplant) | `past_progress_v1` |

Migration alter Keys:

```js
try{['alter_key_v1'].forEach(k=>{
  if(localStorage.getItem(k))localStorage.removeItem(k);
});}catch(e){}
```

---

## 7. Vorgehensweise beim Erstellen einer neuen Datei

1. Masterdatei (`05_simple_present.html`) als Basis laden
2. Titel, H1, Sub-Beschreibung anpassen (Verwendungsfälle der Grammatik benennen)
3. Regelkarten neu befüllen (Formeln, Regeln, Beispiele)
4. YouTube-Links aktualisieren
5. Akkordeon-Struktur anpassen (Anzahl, Titel, Farben – keine doppelten Farben!)
6. Level-Button-Labels anpassen
7. Alle Aufgaben-Pools neu schreiben (L1/L2/L3 je Sektion, mind. 25–35 Aufgaben)
8. Quiz-Pool neu schreiben (mind. 25 Aufgaben)
9. `LS_KEY` anpassen
10. `normalizeAnswer()` prüfen – ggf. neue Kontraktionen ergänzen
11. `analyzeError()` prüfen – ggf. neue Fehlermuster ergänzen
12. **`ACC_MAP` anpassen:** Akkordeon-IDs und Regelkarten-Indizes auf neue Datei abstimmen
13. **Version-Footer einfügen** (aktuelles Datum/Uhrzeit, Zeitzone Berlin, neuer Zwei-Zeilen-Standard – siehe 4.9)
14. **Favicon + klickbares Logo prüfen** (Union-Jack im `<head>`, Logo im `<header>` als `<a>`-Link zur `index.html` – siehe 4.1)
15. **Dateiname prüfen:** nur Kleinbuchstaben + Unterstriche, keine Leerzeichen, keine Bindestriche
16. Auf iOS testen (Safari + Edge)
17. Im Dashboard (`index.html`) eintragen (Admin-Modus, Kachel hinzufügen) oder im Code der `DEFAULT_CONFIG` ergänzen

---

## 8. iOS-Kompatibilität (kritisch)

- Kein `window.confirm()` → Custom Modal verwenden
- Kein `window.alert()` → Inline-Feedback
- Externe Bilder vermeiden → CSS-only Thumbnails
- `var TTS` statt `const TTS` – Temporal Dead Zone Fix in iOS Safari
- `el.open = true` statt `el.setAttribute('open','')` – zuverlässigere Methode zum Öffnen von `<details>` auf iOS
- Alle Touch-Interaktionen mit `-webkit-tap-highlight-color:transparent` versehen

---

## 9. Referenzdatei und Drift-Kontrolle

`05_simple_present.html` ist die Masterdatei. Bei Unklarheiten gilt deren Implementierung als Standard.

### 9.1 Drift-Kontrolle (verbindlich)

Wenn in `05_simple_present.html` eine Logik- oder Struktur-Änderung erfolgt (Render-Engine, Quiz-Format, TTS-Pattern, Akkordeon-Logik, CSS-Basiskomponenten, Design-System), muss sie innerhalb von 14 Tagen auf alle aktiven Schwesterdateien portiert werden.

**Vor jeder neuen Dateierstellung:**

1. Diff zwischen `05_simple_present.html` und allen bestehenden Schwesterdateien prüfen
2. Festgestellte Drifts dokumentieren (was weicht ab, warum)
3. Neue Datei ausschließlich gegen den aktuellen Stand der Masterdatei erzeugen

**Bekannte Abweichungen (Stand 24.04.2026):**

- `word_order.html`: Übungsblöcke nutzen zusätzlich Tap-to-Order mit 3-Optionen-MC (Word-Order-spezifisch). Kein Jahrgangspräfix.
- `08_past_perfect.html`: Akkordeon 2 ist „past participle bilden" statt einer Regel-Sektion (themenspezifisch).

### 9.2 Projektanweisung aktuell halten

Nach jeder grundsätzlichen Änderung an einer der Dateien prüfen, ob diese Anweisung aktualisiert werden muss. Änderungen, die alle Dateien betreffen, gehören hier dokumentiert.

---

## 10. Dashboard & Verteilung

### 10.1 Zweck

`index.html` im Repository-Root ist das Einstiegs-Dashboard für die Schüler. Es bündelt alle Lerndateien in Kategorien (Grammatik, Vokabeln, Skills, Übergreifend, ZAP) und macht sie über Kachel-Klicks aufrufbar.

### 10.2 Hosting

GitHub Pages, Repository `englisch-lernzentrum`. Schüler-URL:

`https://thomasporsche07-byte.github.io/englisch-lernzentrum/`

Zugang zum Schulnetz: Domain muss ggf. in der Schul-Whitelist freigeschaltet werden.

### 10.3 Admin-Modus

URL + `?admin=1`. Ermöglicht:

- Kacheln hinzufügen, bearbeiten, löschen, sortieren (Drag & Drop)
- Export/Import der Konfiguration als JSON
- Reset auf Werkseinstellungen

Admin-Änderungen werden im localStorage des Admin-Geräts gespeichert – **nicht** automatisch auf dem Server. Für eine dauerhafte Änderung, die alle Schüler sehen, muss der Default in der `DEFAULT_CONFIG` im Script-Block der `index.html` angepasst und die Datei auf GitHub ersetzt werden.

### 10.4 Kategorien & Farben

| Kategorie | Farbe | Hex | Zweck |
|---|---|---|---|
| Grammatik | Terrakotta | `#b85c20` | Grammatikthemen pro Jahrgang |
| Vokabeln | Waldgrün | `#3d7a2e` | Lighthouse-Unit-Vokabeln |
| Skills | Pflaume | `#9b4880` | Reading / Listening / Writing |
| Übergreifend | Senf/Ocker | `#a16207` | Jahrgangsübergreifende Tools |
| ZAP | Weinrot | `#7c2d12` | Zentrale Abschlussprüfung, **nur Klasse 10** |

ZAP-Kategorie hat die Filter-Restriction `gradeRestriction:["10"]` – der Chip erscheint nur bei Jahrgangsfilter „Alle" oder „Klasse 10".

### 10.5 Namenskonvention Vokabeln

```
vokabeln/lighthouse_<Band>/unit_<Nr>.html
```

Beispiel: `vokabeln/lighthouse_2/unit_5.html`. Einstellige Unit-Nummern aktuell festgelegt (einheitlich, auch wenn zweistellige besser sortieren).

### 10.6 Kachel-Titel-Konvention

**Grammatik-Kacheln:** `Unit X – Thema`
X = Lighthouse-Unit, in der die Grammatik laut Lehrbuch eingeführt wird.
Beispiele:

- `Unit 4 – Simple Present` (Klasse 5, Lighthouse 1 Unit 4)
- `Unit 5 – Will Future` (Klasse 6, Lighthouse 2 Unit 5)
- `Unit 4 – Past Perfect` (Klasse 9, Lighthouse 5 Unit 4)

Der Jahrgang erscheint nicht im Titel, sondern als separater Badge auf der Kachel.

**Vokabel-Kacheln:** `Lighthouse X – Unit Y`
Beispiele:

- `Lighthouse 1 – Unit 4`
- `Lighthouse 2 – Unit 5`

**Reihenfolge** wird händisch per Drag & Drop im Admin-Modus festgelegt und anschließend in `DEFAULT_CONFIG` verankert (sonst sehen die Schüler die Reihenfolge nicht).

### 10.7 Update-Workflow (Grammatik-Datei austauschen)

1. Lokal bearbeiten / neue Version erzeugen
2. Auf GitHub in den passenden Ordner navigieren (z. B. `grammatik/`)
3. Datei öffnen → Bleistift (Edit) → Inhalt komplett ersetzen → **Commit changes**
4. 30–90 Sekunden warten (Deploy-Zeit)
5. Live-URL im Inkognito-Fenster testen, damit Cache umgangen wird

---

**Änderungshistorie**

- **24.04.2026:** Namenskonvention auf Unterstriche umgestellt (URL-Kompatibilität GitHub Pages); Footer-Standard auf Zwei-Zeilen-Format mit KI-Disclaimer; Kapitel 10 (Dashboard & Verteilung) neu aufgenommen; TTS-Flaggen-Emojis durch Text-Labels ersetzt dokumentiert; ZAP-Kategorie mit `gradeRestriction` ergänzt.
