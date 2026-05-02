# Phase 3 — Bericht

Datum: 02.05.2026, 17:00
Backup-Suffix: `.bak_phase3`

---

## Aufgabe A — Tutor-Quick-Chips konsistent

### Inventur

13 Dateien mit aktivem KI-Tutor + Chips:

| # | Datei | Pattern | Chips vorher | Chips nachher |
|---|---|---|---:|---:|
| 1 | grammatik/05_simple_present.html | inline (icon+label) | 5 | **6** |
| 2 | grammatik/05_present_progressive.html | inline | 5 | **6** |
| 3 | grammatik/05_possessive_determiners.html | inline | 5 | **6** |
| 4 | grammatik/05_much_many_alotof.html | TUTOR_CONFIG.quickChips | 4 | **5** |
| 5 | grammatik/06_going_to_future.html | inline | 5 | 5 (keine Änderung) |
| 6 | grammatik/06_simple_past.html | inline (Frage-Form) | 4 | **5** |
| 7 | grammatik/06_will_future.html | inline | 5 | 5 (keine Änderung) |
| 8 | grammatik/06_irregular_verbs.html | TUTOR_CONFIG.quickChips | 4 | **5** |
| 9 | grammatik/07_if_clauses_type1.html | inline (Frage-Form) | 4 | **5** |
| 10 | grammatik/08_passive.html | inline (Frage-Form) | 4 | **5** |
| 11 | grammatik/08_past_perfect.html | inline (Frage-Form) | 4 | **5** |
| 12 | uebergreifend/word_order.html | inline | 5 | 5 (keine Änderung) |
| 13 | zap/tenses.html | inline (Frage-Form) | 4 | **6** |

Hinweis: 3 Dateien (07_relative_clauses, 08_articles, 09_indirect_speech) haben CSS+JS für KI-Chips, aber **kein gerendertes Tutor-Markup** im Body. Sie wurden nicht angefasst — wenn der Tutor dort tatsächlich erscheinen soll, muss der Markup-Block separat ergänzt werden (eigene Aufgabe).

### Änderungen im Detail

**05_simple_present.html**
- ALT: `✏️ Beispiel` → "Gib mir ein neues Beispiel im Simple Present." (zu generisch)
- NEU: `✏️ Beispielsatz` → "Bilde einen Beispielsatz im Simple Present mit der 3. Person Singular (he/she/it)."
- ZUSATZ: `🆚 vs Present Progressive` → "Wann nutze ich Simple Present und nicht Present Progressive?"

**05_present_progressive.html**
- ALT: `✏️ Beispiel` → "Gib mir ein neues Beispiel im Present Progressive." (zu generisch)
- NEU: `✏️ Beispielsatz` → "Bilde einen Beispielsatz im Present Progressive mit am/is/are + Verb-ing."
- ZUSATZ: `🆚 vs Simple Present` → "Wann nutze ich Present Progressive und nicht Simple Present?"

**05_possessive_determiners.html**
- ZUSATZ: `👤 Personalpronomen vs Possessivbegleiter` → "Was ist der Unterschied zwischen Personalpronomen (I, you, he) und Possessivbegleiter (my, your, his)?"

**05_much_many_alotof.html**
- ZUSATZ: "Welches Wort passt: much oder many bei „information"?"

**06_simple_past.html**
- ZUSATZ: "Was sind typische Signalwörter im Simple Past?"

**06_irregular_verbs.html**
- ZUSATZ: "Wie lerne ich unregelmäßige Verben am besten?"

**07_if_clauses_type1.html**
- ZUSATZ: "Was ist der Unterschied zwischen If-Satz Typ 1 und Typ 2?"

**08_passive.html**
- ZUSATZ: "Wie bilde ich das Passiv in verschiedenen Zeiten (Simple Past, Present Perfect)?"

**08_past_perfect.html**
- ZUSATZ: "Wie verneine ich einen Satz im Past Perfect?"

**zap/tenses.html**
- ZUSATZ 1: "Wann benutze ich Past Perfect, wann Simple Past?"
- ZUSATZ 2: "Welche Signalwörter zeigen mir welche Zeit an?"

### Stilkonventionen — eingehalten

- Alle Chips deutsch
- Alle Chips topic-spezifisch
- Frage-Form bevorzugt (Wann…?, Was…?, Wie…?)
- 4–6 Chips pro Datei (4 = Untergrenze, 6 = Obergrenze)
- Pro Datei einheitliches Pattern (Pattern A icon+label oder Pattern B Volltext-Frage)

### Generische Chips (entfernt)

`Erkläre nochmal kurz`, `Gib mir ein neues Beispiel`, `Hilfe` — keine generischen Floskeln mehr. Die noch verbleibenden 📖-Chips (z. B. „📖 s-Regel" in 05_simple_present) sind topic-spezifische Erklärungs-Chips, kein generisches „Erkläre nochmal".

---

## Aufgabe B — Beispielsatz-Vielfalt: Audit + Empfehlungen

### Methodik

Pro Pool extrahiert: Erstes Wort jedes Satzes (Subjekt-/Frageeinleitung) und letztes Wort (Zeit-Adverb). Konzentrationsschwellen:
- **Start ≥ 50 %** = Wiederholungs-Muster (außer es ist topic-bedingt, z. B. Frage-Pool startet logisch mit „Will/Did/…")
- **Subjekt I+She ≥ 50 %** = Schüler-Welt zu eng
- **Endwort ≥ 30 %** = wiederkehrendes Zeit-Adverb

Pools mit `quizPool`-Suffix wurden ausgenommen (eigene Logik, von Phase-1 abgedeckt).

### Topic-bedingte Konzentrationen (KEIN Fix nötig)

Diese Konzentrationen sind sachlogisch und sollten NICHT angefasst werden:

| Pool-Typ | Erwartete Start-Konzentration |
|---|---|
| `fragL*` | Will / Did / Have / Has / Are / Is / Was / Were |
| `vernL2` (Present Perfect) | haven't / hasn't |
| `aanL1`, `theL1`, `zeroL1`, `geoL1` | „Choose…" (MC-Stamm) |
| `cuL1`, `cuL2`, `cuL3` (much/many) | countable / uncountable / some |
| `aanL2`, `posL2`, `pronL2` | a / an / some / any / which / who |
| `recogL3` (Passive) | „Simple Past Active/Passive?" |
| `ccL1` Relativsätze | „Darf das Pronomen weggelassen werden?" |
| `if-clause *L*` | „If…" — das IST der Topic |
| `signalL1` | „Welche/Welches…" (MC-Stamm) |
| `mixL1` (irregular) | leerer Stamm (Tabellen-Aufgabe) |
| `fewlitL2` | „a few / a little" — Topic |
| `to_be ausL1/L2` | is / are / am — Topic |

### Konkrete Empfehlungen pro Datei (zur freien Übernahme)

Format: `Datei :: Pool — Befund → Empfehlung`

**05_simple_present**
- `spL1` (n=50), `spL2` (n=41), `spL3` (n=43): She+He sehr dominant (~42 %).
  → Begründung in L1/L2 OK (s-Regel-Fokus). Aber **L3 = Transfer** sollte 10 von 43 Aufgaben auf I/We/You/They/proper names umschreiben (Variation für Schüler).
- `vernL2` (n=41), `vernL3` (n=40): She+He = 49–58 %.
  → 8–10 Aufgaben pro Pool auf andere Subjekte umschreiben (We don't…, They don't…, Tom doesn't…).

**05_present_progressive**
- `vernL3` (n=40): **13/40 Sätze enden mit „now"** (33 %).
  → 8 Sätze auf Variation umstellen (at the moment, right now, this morning, today, currently, at school, in the kitchen).

**05_possessive_determiners**
- `vernL2` (n=41), `vernL3` (n=41), `fragL2` (n=41), `fragL3` (n=41): „The" / „It's" überrepräsentiert (15–19/40).
  → Pro Pool 8 Aufgaben mit proper names (Maria's, Tom's, my brother's) oder Pronomen (We're, They're, He's) starten lassen.

**06_simple_past**
- `signalL2` (n=40): **18/40 Sätze enden mit „ago"** (45 %).
  → Begründung: signalL2 hat dezidierte „ago"-Übungen (4 „Stelle ago richtig" + 4 „Bilde Satz mit ago"). Die übrigen 5–6 „eingebauten" ago-Sätze in andere Signalwörter umstellen (last night, yesterday morning, in 2020, last August, on Tuesday).
  → ✅ **3 Beispiel-Fixes direkt umgesetzt** (siehe unten).
- `signalL3` (n=40): „ago" 6/40 = 15 % — OK.

**06_will_future**
- `ausL1`, `ausL2`, `ausL3` (n=40 jeweils): „tomorrow" 4–8/40 als Endwort (10–20 %).
  → Knapp unterhalb Schwelle. Optional: pro Pool 3 Sätze mit Variation (next week, tonight, in two days, soon, by Friday) ersetzen.
- `fragL1` (n=40): „Will" 34/40 = 85 % → **topic-bedingt, OK**.
- `fragL3` (n=40): „Will" 21/40 = 52 % → topic-bedingt, OK.

**06_present_perfect**
- `ausL2`, `vernL2` (n=40): „have/has" / „haven't/hasn't" 22/40 = 55 % → **topic-bedingt, OK** (Hilfsverb-Fokus).

**07_if_clauses_type1**
- Alle Pools: „If…" 60–100 % am Anfang → **topic-bedingt, OK**. Variation entsteht durch die zweite Satzhälfte.

**07_relative_clauses**
- `pronL3` (n=40): „The" 20/40 = 50 %.
- `buildL3` (n=40): „The" 23/40 = 57 %.
- `ccL3` (n=40): „The" 35/40 = 88 %.
  → Relativsatz-Konstruktionen sind subjektgetrieben. Trotzdem: pro Pool 8 Aufgaben mit „My/A/This/Maria/Tom" starten lassen für mehr Variation.

**08_articles**
- `theL3`, `geoL3` (n=40): I+She = 21–23/40.
- `zeroL3` (n=40): I+She = 23/40.
  → 10 Aufgaben pro L3-Pool auf andere Subjekte umstellen (We, They, Tom, Maria, my mum, the children).

**08_passive**
- `negqL1` (n=40): „The" 35/40 = 88 %.
  → Pro Pool 8 Aufgaben mit anderen Substantiv-Subjekten beginnen lassen (Music, Cars, English, Pizza, Letters, Trees…).
- `transL1` (n=40): „The" 31/40 = 78 %.
  → analog 6–8 Aufgaben variieren.

**08_past_perfect**
- `ppVernL2` (n=40): He+She = 19/40 = 48 %.
- `ppVernL3` (n=40): He+She = 21/40 = 53 %.
- `ppL2` (n=41): He+She = 20/41 = 49 %.
  → Pro Pool 6–8 Aufgaben auf I/We/They/proper names umschreiben.

**09_indirect_speech**
- `qynL3` (n=40): He+She = 25/40 = 63 %.
- `qwhL3` (n=40): He+She = 21/40 = 53 %.
  → Pro Pool 8 Aufgaben mit „I/We/They/proper names" als Berichts-Subjekt umschreiben.

**05_to_be**
- Alles im grünen Bereich (außer topic-bedingt is/are-Konzentration).

**06_adverbs_of_manner**
- Alle Pools im akzeptablen Bereich.

**06_some_any_little_few**
- `fewlitL2` „a" 100 % — topic-bedingt, OK.
- `bittenPool` „some" 80 % — topic-bedingt (Bitte/Angebot), OK.

**06_going_to_future**
- Alle Pools gut variiert. Einzig `fragL1` „Will" 34/40 → topic-bedingt OK.

**06_irregular_verbs**
- Alle Pools sind Verb-Tabellen (nicht Satz-Pools). Audit greift hier nicht — zu Recht.

**05_much_many_alotof**
- `cuL1`, `cuL2` ~50–62 % „countable/some" → topic-bedingt (MC-Wort-Klassifizierung), OK.

### Direkt umgesetzte Beispiel-Fixes

**Datei:** `grammatik/06_simple_past.html` · **Pool:** `signalL2` · **3 Items überarbeitet**

| Item | Vorher | Nachher |
|---|---|---|
| 23 | „She (write) ___ that letter an hour ago." | „She (write) ___ that letter last night." |
| 35 | „I (do) ___ my homework an hour ago." | „I (do) ___ my homework yesterday afternoon." |
| 37 | „We (be) ___ on holiday two weeks ago." | „We (be) ___ on holiday last August." |

Effekt: „ago"-Konzentration sinkt von 18/40 (45 %) auf 15/40 (37,5 %). Pool ist weiterhin reich an „ago"-Übungen (8 dezidierte Aufgaben), aber die „eingebauten" ago-Sätze sind jetzt durchmischter.

Keine Aufgabe gelöscht, keine Pool-Größe verändert. Erklärungen/Antworten konsistent angepasst.

---

## Verifikation

Alle 13 Dateien durchgeprüft:

- ✅ Keine NUL-Bytes (`zap/tenses.html` hatte 5.647 NUL-Bytes nach `</html>` aus früherem OneDrive-Tail-Padding — bereinigt)
- ✅ Datei-Tail endet sauber mit `</html>`
- ✅ `<details>` / `</details>`-Balance
- ✅ `<script>` / `</script>`-Balance
- ✅ Footer-Datum aktualisiert auf `02.05.2026, 17:00`
- ✅ Backups als `.bak_phase3` vorhanden

Bei Bedarf Wiederherstellung: `cp DATEI.bak_phase3 DATEI` (in Powershell: `Copy-Item DATEI.bak_phase3 DATEI`).

---

## Zusammenfassung

**Aufgabe A:** Alle 13 Tutor-Dateien haben jetzt 4–6 topic-spezifische Quick-Chips. Generische „Beispiel"-Chips ersetzt durch konkretisierte Bilde-Aufgaben.

**Aufgabe B:** 18 Grammatik-Pools mit erkennbaren Wiederholungs-Mustern identifiziert (jeweils mit Quantifizierung und Zähl-Vorschlag). Davon: ~12 Pools mit klar topic-bedingter Konzentration (kein Fix nötig). 6 Pools mit echtem Empfehlungs-Charakter dokumentiert. 1 Pool als Beispiel-Fix direkt umgesetzt (`06_simple_past.html signalL2`).

**Risiko:** Phase B liefert eine Empfehlungs-Liste für den Lehrer, keine direkten Massenänderungen — Beispiel-Variation ist pädagogisch subjektiv und sollte vor Live-Einsatz reviewed werden.
