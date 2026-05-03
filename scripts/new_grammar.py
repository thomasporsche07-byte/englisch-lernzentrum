#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Generator fuer neue Grammatikdateien (Phase 2)
==============================================

Erzeugt eine Stub-Datei `grammatik/<grade>_<topic>.html` mit allen Pflicht-
Bestandteilen aus CLAUDE.md (shared/-Includes, Tutor-Mount, leere Pools, Quiz-
Stub) und ergaenzt `index.html` um eine passende Tile in `DEFAULT_CONFIG.tiles[]`.

Hinweis: ein manueller Versions-Bump ist nicht mehr noetig - das Dashboard
berechnet beim Laden einen Hash ueber DEFAULT_CONFIG.tiles und erkennt das
Einfuegen einer neuen Tile automatisch.

Aufruf
------
Argumentbasiert:
    python scripts/new_grammar.py --grade 6 --topic conditional_1 --unit 3 \\
        --display "Conditional I" [--icon 📕] [--short c1] [--ls-prefix cond1] \\
        [--sub "Real conditional · if + Simple Present"]

Interaktiv (frage was fehlt):
    python scripts/new_grammar.py

Cleanup (zum Aufraeumen nach Tests):
    python scripts/new_grammar.py --cleanup grammatik/99_test_topic.html

Verifikation
------------
Am Ende ruft das Skript automatisch den Linter (`lint_watcher.py --file ...`)
auf der neuen Datei auf. Ergebnis wird angezeigt - Pflicht-Struktur muss
erfuellt sein, auch wenn die Pools noch leer sind.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
GRAMMATIK_DIR = PROJECT_ROOT / "grammatik"
INDEX_FILE   = PROJECT_ROOT / "index.html"
LINTER       = Path(__file__).parent / "lint_watcher.py"

ALLOWED_GRADES = [5, 6, 7, 8, 9, 10]
TOPIC_SLUG_RX  = re.compile(r'^[a-z][a-z0-9_]*$')

# ---------------------------------------------------------------------------
# Hilfsfunktionen
# ---------------------------------------------------------------------------

def ask(prompt: str, default: str | None = None) -> str:
    suffix = f" [{default}]" if default else ""
    while True:
        ans = input(f"{prompt}{suffix}: ").strip()
        if ans:
            return ans
        if default is not None:
            return default
        print("  -> Eingabe erforderlich.")

def derive_short(topic: str) -> str:
    """Tile-ID-Kuerzel aus Topic-Slug ableiten (erste Buchstaben jedes Tokens)."""
    tokens = [t for t in topic.split('_') if t]
    if len(tokens) >= 2:
        short = ''.join(t[0] for t in tokens)
    else:
        short = (tokens[0] if tokens else 'x')[:3]
    return short.lower()

def derive_ls_prefix(topic: str) -> str:
    """LocalStorage-Praefix aus Topic-Slug (ersten 6 Buchstaben ohne '_')."""
    return topic.replace('_', '')[:6].lower() or 'topic'

def derive_display(topic: str) -> str:
    return ' '.join(p.capitalize() for p in topic.split('_'))


# ---------------------------------------------------------------------------
# HTML-Stub
# ---------------------------------------------------------------------------

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="de">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title>{display} – Hellweg-Realschule</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Baloo+2:wght@400;500;600;700;800&display=swap" rel="stylesheet">

<!-- ===== SHARED-MODULES ===== -->
<link rel="stylesheet" href="../shared/style.css">
<link rel="stylesheet" href="../shared/quiz.css">
<link rel="stylesheet" href="../shared/tutor.css">

<!-- ===== TOPIC-SPEZIFISCHES CSS ===== -->
<style>
/* TODO: per-Akkordeon-Farben hier definieren - Beispiel siehe 05_to_be.html */
/* Pflicht-Pattern fuer Pill-Formeln (CLAUDE.md): */
.rc-formula{{display:flex;flex-wrap:wrap;align-items:center;gap:6px 4px}}
.fc-pair{{display:inline-flex;align-items:center;gap:3px;white-space:nowrap;flex-shrink:0}}
.fc{{flex-shrink:0}}
</style>
</head>
<body>

<!-- ===== Confirm-Modal (fuer customConfirm) ===== -->
<div id="confirm-modal" style="display:none" class="confirm-overlay">
  <div class="confirm-box">
    <p id="confirm-msg">Fortschritt zuruecksetzen?</p>
    <div class="confirm-btns">
      <button class="btn primary" id="confirm-ok">Ja, zuruecksetzen</button>
      <button class="btn ghost"   id="confirm-cancel">Abbrechen</button>
    </div>
  </div>
</div>

<!-- ===== DREI BILDSCHIRM-ECKEN-BUTTONS ===== -->
<button class="dark-toggle"  id="dark-toggle">🌙 Dark Mode</button>
<button class="tts-toggle"   id="tts-toggle">🔊 Vorlesen</button>
<button class="reset-all-btn" id="reset-all-btn">🗑️ Zuruecksetzen</button>

<div class="container">

<header>
  <a href="../index.html" title="Zurueck zum Englisch-Lernzentrum" style="display:inline-block;text-decoration:none">
    <img src="../assets/logo_hellweg.png" alt="Logo der Hellweg-Realschule Unna-Massen" style="cursor:pointer"/>
  </a>
  <h1>{display}</h1>
  <p class="sub">Klasse {grade} – Unit {unit}</p>
</header>

<!-- ===== REGELKARTEN =====
     TODO: Inhalt fuellen.
     Bei Tense-Themen sind 6 Karten Pflicht (CLAUDE.md, Abschnitt
     "Pflicht-Karten fuer Tense-Grammatikdateien"):
       1. ✅ Aussagesatz (c-green)
       2. ❌ Verneinung (c-red)
       3. ❓ Ja/Nein-Frage (c-blue)
       4. 🔵 W-Frage (c-indigo)
       5. ⏱ Wann benutze ich es? (c-amber)
       6. 📌 Signalwoerter (c-teal)
     Bei Nicht-Tense-Themen frei nach Bedarf - 3 Karten als Startpunkt.
-->
<section class="rules-combined">
<h2>Regelkarten</h2>
<div class="rc-grid">

<div class="rc-card c-green">
  <div class="rc-card-topbar"></div>
  <div class="rc-card-body">
    <div class="rc-card-label">TODO: Karten-Label 1</div>
    <div class="rc-card-num">1</div>
    <div class="rc-rule">TODO: Regel-Text Karte 1.</div>
    <div class="rc-examples-new">
      <b>Beispiele:</b><br>
      TODO: Beispielsatz 1.<br>
      TODO: Beispielsatz 2.
    </div>
  </div>
</div>

<div class="rc-card c-red">
  <div class="rc-card-topbar"></div>
  <div class="rc-card-body">
    <div class="rc-card-label">TODO: Karten-Label 2</div>
    <div class="rc-card-num">2</div>
    <div class="rc-rule">TODO: Regel-Text Karte 2.</div>
    <div class="rc-examples-new">
      <b>Beispiele:</b><br>
      TODO: Beispielsatz.
    </div>
  </div>
</div>

<div class="rc-card c-blue">
  <div class="rc-card-topbar"></div>
  <div class="rc-card-body">
    <div class="rc-card-label">TODO: Karten-Label 3</div>
    <div class="rc-card-num">3</div>
    <div class="rc-rule">TODO: Regel-Text Karte 3.</div>
    <div class="rc-examples-new">
      <b>Beispiele:</b><br>
      TODO: Beispielsatz.
    </div>
  </div>
</div>

</div>
</section>

<!-- ===== UEBUNGS-AKKORDEONS =====
     Drei Akkordeons mit L1/L2/L3-Pools. setupSection-Aufrufe weiter unten.
     Pool-Inhalt: mind. 15 Aufgaben pro Level (CLAUDE.md). -->

<details class="accordion" id="acc-auf1">
<summary>📝 Aufgabenblock 1 – TODO: Titel</summary>
<div class="content">
  <div class="level-switch" id="auf1-levels"></div>
  <div class="progress-wrap" id="auf1-progress">
    <div class="progress mixed" role="progressbar" aria-valuemin="0" aria-valuemax="100"><div class="progress-fill"></div></div>
    <div class="progress-text">Fortschritt: 0/0 (0%)</div>
  </div>
  <div class="section-actions">
    <button class="btn gray" id="auf1-check-all">Alle pruefen</button>
    <button class="btn gray" id="auf1-reset">Zuruecksetzen</button>
    <button class="btn gray" id="auf1-shuffle">Neu wuerfeln</button>
  </div>
  <div id="auf1-tasks"></div>
</div>
</details>

<details class="accordion" id="acc-auf2">
<summary>📝 Aufgabenblock 2 – TODO: Titel</summary>
<div class="content">
  <div class="level-switch" id="auf2-levels"></div>
  <div class="progress-wrap" id="auf2-progress">
    <div class="progress mixed" role="progressbar" aria-valuemin="0" aria-valuemax="100"><div class="progress-fill"></div></div>
    <div class="progress-text">Fortschritt: 0/0 (0%)</div>
  </div>
  <div class="section-actions">
    <button class="btn gray" id="auf2-check-all">Alle pruefen</button>
    <button class="btn gray" id="auf2-reset">Zuruecksetzen</button>
    <button class="btn gray" id="auf2-shuffle">Neu wuerfeln</button>
  </div>
  <div id="auf2-tasks"></div>
</div>
</details>

<details class="accordion" id="acc-auf3">
<summary>📝 Aufgabenblock 3 – TODO: Titel</summary>
<div class="content">
  <div class="level-switch" id="auf3-levels"></div>
  <div class="progress-wrap" id="auf3-progress">
    <div class="progress mixed" role="progressbar" aria-valuemin="0" aria-valuemax="100"><div class="progress-fill"></div></div>
    <div class="progress-text">Fortschritt: 0/0 (0%)</div>
  </div>
  <div class="section-actions">
    <button class="btn gray" id="auf3-check-all">Alle pruefen</button>
    <button class="btn gray" id="auf3-reset">Zuruecksetzen</button>
    <button class="btn gray" id="auf3-shuffle">Neu wuerfeln</button>
  </div>
  <div id="auf3-tasks"></div>
</div>
</details>

<!-- ===== KI-Tutor-Mount-Point ===== -->
<div id="tutor-mount"></div>

<!-- ===== WWM-QUIZ ===== -->
<div class="quiz-divider"><span>🏆 Teste dein Wissen</span></div>
<details class="accordion" id="wwm-quiz">
<summary>🏆 Quiz</summary>
<div class="content">
  <div class="progress-wrap" id="quiz-progress">
    <div class="progress mixed" role="progressbar" aria-valuemin="0" aria-valuemax="100"><div class="progress-fill"></div></div>
    <div class="progress-text">Fortschritt: 0/15 richtig (0%)</div>
  </div>
  <div class="section-actions"><button class="btn gray" id="quiz-reset">Zuruecksetzen</button></div>
  <div id="quiz-tasks"></div>
  <div id="quiz-result" class="result-card" style="display:none"></div>
</div>
</details>

</div>

<footer style="text-align:center;color:#b8905a;font-size:12px;margin-top:30px;padding:16px 20px 4px;border-top:1px solid rgba(184,144,90,.25)">
<div>Version {version_str}</div>
<div style="margin-top:6px">Der Inhalt dieser Datei ist KI-generiert und kann fehlerhaft bzw. lueckenhaft sein. © Thomas Porsche</div>
</footer>

<!-- ===== SHARED-SCRIPTS (Reihenfolge wichtig!) ===== -->
<script src="../shared/scorecards.js"></script>
<script src="../shared/quiz.js"></script>

<!-- ===== TOPIC-SPEZIFISCHE DATEN + INIT ===== -->
<script>
/* === KI-TUTOR-CONFIG === */
window.TUTOR_CONFIG = {{
  topic: "{display}",
  grade: {grade},
  unit: {unit},
  rules: [
    "TODO: Kurzregel 1",
    "TODO: Kurzregel 2",
    "TODO: Kurzregel 3"
  ],
  welcomeMessage:
    "<strong>👋 Hallo! Ich bin dein KI-Tutor.</strong><br>" +
    "Ich helfe dir, „{display}“ besser zu verstehen. " +
    "Stell mir Fragen, bitte um Beispiele oder schick mir einen Satz zum Pruefen. " +
    "Ich gebe dir Tipps - aber keine fertigen Loesungen!",
  quickChips: [
    "TODO: Beispielfrage 1",
    "TODO: Beispielfrage 2",
    "TODO: Beispielfrage 3"
  ],
  typicalErrors: [
    "TODO: typischer Fehler 1",
    "TODO: typischer Fehler 2"
  ]
}};

/* === LOCAL-STORAGE-WRAPPER (datei-spezifischer Prefix '{ls_prefix}_') === */
function tbSave(key,val){{try{{localStorage.setItem('{ls_prefix}_'+key,JSON.stringify(val));}}catch(e){{}}}}
function tbLoad(key,def){{try{{const v=localStorage.getItem('{ls_prefix}_'+key);return v?JSON.parse(v):def;}}catch(e){{return def;}}}}

/* === POOL-DATEN ===
   TODO: Mind. 15 Aufgaben pro L1/L2/L3-Pool (CLAUDE.md).
   Pool-Typen:
     {{type:"mc", prompt, options:[…], correct:idx, answer}}
     {{words:[…], answer:[…], label}}                      // Tap-to-Order
     {{prompt, answer:[…], placeholder?, explanation?}}   // Freitext
*/
const auf1L1=[]; const auf1L2=[]; const auf1L3=[];
const auf2L1=[]; const auf2L2=[]; const auf2L3=[];
const auf3L1=[]; const auf3L2=[]; const auf3L3=[];

/* === QUIZ-POOL (15 Fragen, Verteilung 4·d=1 / 5·d=2 / 6·d=3) ===
   Schema pro Frage:
     {{prompt, options:[4 Strings], correct:0–3, tip, explanation, d:1|2|3}}
*/
const quizPool=[
  // TODO: 15 Quizfragen einsetzen.
];

/* === SECTION-SETUP ===
   setupSection bzw. setupSimpleSection wird von shared/scorecards.js bereitgestellt.
*/
setupSection('auf1',document.getElementById('auf1-levels'),document.getElementById('auf1-tasks'),
  {{1:auf1L1,2:auf1L2,3:auf1L3}},
  document.getElementById('auf1-check-all'),document.getElementById('auf1-reset'),true);
setupSection('auf2',document.getElementById('auf2-levels'),document.getElementById('auf2-tasks'),
  {{1:auf2L1,2:auf2L2,3:auf2L3}},
  document.getElementById('auf2-check-all'),document.getElementById('auf2-reset'),true);
setupSection('auf3',document.getElementById('auf3-levels'),document.getElementById('auf3-tasks'),
  {{1:auf3L1,2:auf3L2,3:auf3L3}},
  document.getElementById('auf3-check-all'),document.getElementById('auf3-reset'),true);

/* === DARK-MODE / TTS / RESET-ALL === */
HRShared.initDarkMode('dark-toggle','{ls_prefix}_dark_v1');
HRShared.initTTS('tts-toggle');
HRShared.initResetAllButton('reset-all-btn',
  ['auf1-reset','auf2-reset','auf3-reset','quiz-reset'],
  ['{ls_prefix}_auf1_states','{ls_prefix}_auf2_states','{ls_prefix}_auf3_states','{ls_prefix}_openAcc']
);

/* === QUIZ-INIT === */
HRQuiz.init(quizPool, {{
  finalMessages: function(pct){{
    if(pct===100) return {{msg:'EINE MILLION! 🎉 PERFEKT!', emoji:'🏆'}};
    if(pct>=90)   return {{msg:'Fast perfekt – starkes Ergebnis!', emoji:'🥇'}};
    if(pct>=80)   return {{msg:'Richtig stark – die Regel sitzt!', emoji:'🥈'}};
    if(pct>=60)   return {{msg:'Gut gemacht – noch etwas ueben, dann sitzt es!', emoji:'👍'}};
    if(pct>=40)   return {{msg:'Weiter ueben – schau dir die Regelkarten an!', emoji:'💪'}};
    return {{msg:'Nochmal von vorne – Regeln nochmal lesen!', emoji:'📚'}};
  }},
  phoneFallback: 'TODO: Kurzregel als Telefonjoker-Fallback.'
}});

/* === AKKORDEON-PERSISTENZ === */
(function(){{
  const ACC_IDS=['acc-auf1','acc-auf2','acc-auf3','wwm-quiz','acc-ki'];
  const savedOpen=tbLoad('openAcc',null);
  ACC_IDS.forEach(id=>{{
    const el=document.getElementById(id);
    if(!el)return;
    el.removeAttribute('open');
    el.addEventListener('toggle',()=>{{
      if(el.open) tbSave('openAcc',id);
    }});
  }});
  setTimeout(()=>{{
    if(savedOpen){{
      const el=document.getElementById(savedOpen);
      if(el){{el.setAttribute('open','');el.open=true;}}
    }}
  }},50);
}})();
</script>

<!-- Tutor zuletzt – konsumiert window.TUTOR_CONFIG, das oben gesetzt wurde -->
<script src="../shared/tutor.js"></script>

</body>
</html>
"""


# ---------------------------------------------------------------------------
# index.html-Bearbeitung
# ---------------------------------------------------------------------------

def _grammar_tile_block(short_id: str) -> str:
    """Liefert die Regex zur Block-Erkennung einer einzelnen Tile."""
    return rf'\{{id:"{re.escape(short_id)}",.*?\}},?\s*\n'

def find_grammatik_insertion(content: str, grade: int, unit: int) -> int:
    """
    Bestimmt die Einfuegeposition (Char-Offset) im content fuer eine neue
    Grammatik-Tile, sodass die Sortierung (Klasse aufsteigend, dann Unit
    aufsteigend) erhalten bleibt.

    Strategie: Alle existierenden g-XX-...-Tiles parsen, ihre (grade, unit)
    bestimmen, passende Folge-Tile finden und davor einfuegen. Wenn keine
    Folge-Tile existiert, hinter die letzte g-Tile einfuegen.
    """
    # Alle Grammatik-Tile-Bloecke finden (id beginnt mit "g-")
    rx = re.compile(
        r'(\s*)\{id:"(g-[^"]+)",\s*title:"([^"]*)"[^}]*?grade:"(\d+)"[^}]*?file:"grammatik/([^"]+)"[^}]*?\},?\s*\n',
        re.DOTALL,
    )
    tiles = []
    for m in rx.finditer(content):
        title  = m.group(3)
        gr     = int(m.group(4))
        # Unit aus Titel extrahieren ("Unit 4 – ...") - nicht jede Tile hat eine Unit
        unit_m = re.search(r'Unit\s+(\d+)', title)
        un = int(unit_m.group(1)) if unit_m else 99
        tiles.append((m.start(), m.end(), gr, un))

    if not tiles:
        # Keine Grammatik-Tiles gefunden - fall back: nach DEFAULT_CONFIG.tiles=[
        m = re.search(r'tiles:\s*\[\s*\n', content)
        return m.end() if m else 0

    # Erste Tile mit (grade, unit) groesser als (new_grade, new_unit)
    for start, end, gr, un in tiles:
        if (gr, un) > (grade, unit):
            return start
    # Sonst: hinter die letzte Grammatik-Tile
    return tiles[-1][1]

def build_tile_line(*, tile_id: str, title: str, sub: str, grade: int,
                    file_rel: str, icon: str, since: str) -> str:
    """Erzeugt einen 3-zeiligen Tile-Block (Einrueckung 4 Spaces, wie im Bestand)."""
    return (
        f'    {{id:"{tile_id}", title:"{title}", sub:"{sub}",\n'
        f'     category:"grammatik", grade:"{grade}", subcat:"",\n'
        f'     file:"{file_rel}", icon:"{icon}", status:"new", visible:true, since:"{since}"}},\n\n'
    )

def insert_tile(content: str, tile_block: str, grade: int, unit: int) -> str:
    pos = find_grammatik_insertion(content, grade, unit)
    return content[:pos] + tile_block + content[pos:]

def remove_tile(content: str, tile_id: str) -> tuple[str, bool]:
    """Entfernt eine Tile (ID-genau) aus DEFAULT_CONFIG."""
    rx = re.compile(
        r'\s*\{id:"' + re.escape(tile_id) + r'"[^}]*\},?\s*\n',
        re.DOTALL,
    )
    new_content, n = rx.subn('\n    ', content, count=1)
    return new_content, n > 0

def remove_tile_by_file(content: str, file_rel: str) -> tuple[str, bool, str]:
    """
    Entfernt eine Tile, die `file:"<file_rel>"` enthaelt - unabhaengig von der ID.
    Robuster als ID-basiertes Entfernen, weil der Dateiname unmittelbar aus
    dem Cleanup-Argument bekannt ist.
    Liefert (neuer Inhalt, removed?, gefundene_id).
    """
    rx = re.compile(
        r'\s*\{(id:"([^"]+)"[^}]*?file:"' + re.escape(file_rel) + r'"[^}]*?)\},?\s*\n',
        re.DOTALL,
    )
    m = rx.search(content)
    if not m:
        return content, False, ''
    found_id = m.group(2)
    new_content = content[:m.start()] + '\n    ' + content[m.end():]
    return new_content, True, found_id


# ---------------------------------------------------------------------------
# Hauptfunktionen
# ---------------------------------------------------------------------------

def cmd_create(args: argparse.Namespace) -> int:
    # 1. Eingaben sammeln (interaktiv, falls fehlend)
    grade   = args.grade   or int(ask("Klassenstufe (5/6/7/8/9/10)"))
    topic   = args.topic   or ask("Topic-Slug (snake_case, z.B. conditional_1)")
    unit    = args.unit    or int(ask("Unit-Nummer"))
    display = args.display or ask("Topic-Anzeigename", derive_display(topic))
    short   = (args.short or derive_short(topic)).lower()
    ls_pref = (args.ls_prefix or derive_ls_prefix(topic)).lower()
    icon    = args.icon or "📕"
    sub     = args.sub  or "TODO: kurze Beschreibung ergaenzen"

    # 2. Validierung
    if grade not in ALLOWED_GRADES:
        print(f"FEHLER: grade muss in {ALLOWED_GRADES} sein.", file=sys.stderr)
        return 2
    if not TOPIC_SLUG_RX.match(topic):
        print("FEHLER: topic-slug muss snake_case sein (a-z, 0-9, _).", file=sys.stderr)
        return 2
    file_rel = f"grammatik/{grade:02d}_{topic}.html"
    target   = PROJECT_ROOT / file_rel
    if target.exists() and not args.force:
        print(f"FEHLER: Zieldatei existiert bereits: {file_rel}. "
              f"Mit --force ueberschreiben.", file=sys.stderr)
        return 2

    # 3. Tile-ID + Konflikt-Check
    tile_id = f"g-{int(grade):02d}-{short}"
    index_content = INDEX_FILE.read_text(encoding='utf-8')
    if f'id:"{tile_id}"' in index_content:
        print(f"FEHLER: Tile-ID '{tile_id}' existiert bereits in index.html. "
              f"Bitte --short anders waehlen.", file=sys.stderr)
        return 2

    # 4. HTML-Stub erzeugen
    now = datetime.now()
    version_str = now.strftime("%d.%m.%Y, %H:%M")
    since_str   = now.strftime("%Y-%m-%d")
    title_for_tile = f"Unit {unit} – {display}"

    GRAMMATIK_DIR.mkdir(parents=True, exist_ok=True)
    target.write_text(
        HTML_TEMPLATE.format(
            display=display, grade=grade, unit=unit,
            version_str=version_str, ls_prefix=ls_pref,
        ),
        encoding='utf-8',
    )
    print(f"✓ Stub erzeugt: {file_rel}")

    # 5. index.html: Tile einfuegen + Version bumpen
    tile_block = build_tile_line(
        tile_id=tile_id, title=title_for_tile, sub=sub,
        grade=grade, file_rel=file_rel, icon=icon, since=since_str,
    )
    new_index = insert_tile(index_content, tile_block, grade, unit)
    INDEX_FILE.write_text(new_index, encoding='utf-8')
    print(f"✓ index.html: Tile '{tile_id}' eingefuegt (Position nach Sortier-Regel).")
    print(f"  Hinweis: kein manueller Versions-Bump - Dashboard erkennt die Aenderung")
    print(f"  automatisch ueber den DEFAULT_CONFIG-Hash.")

    # 6. Linter aufrufen
    print(f"\n--- Linter-Lauf auf {file_rel} ---")
    res = subprocess.run(
        [sys.executable, str(LINTER), '--file', file_rel, '--no-color'],
        cwd=str(PROJECT_ROOT),
    )
    if res.returncode == 0:
        print(f"✓ Linter: keine Verstoesse - Pflicht-Struktur erfuellt.")
    else:
        print(f"⚠  Linter meldet Verstoesse - bitte beheben.")
    return 0

def cmd_cleanup(args: argparse.Namespace) -> int:
    target = Path(args.cleanup)
    if not target.is_absolute():
        target = PROJECT_ROOT / target
    if not target.exists():
        print(f"FEHLER: Datei nicht gefunden: {target}", file=sys.stderr)
        return 2

    file_rel = str(target.relative_to(PROJECT_ROOT)).replace('\\', '/')

    try:
        target.unlink()
        print(f"✓ Datei geloescht: {file_rel}")
    except PermissionError as e:
        print(f"⚠  Datei konnte nicht geloescht werden ({e}).")
        print(f"   Bitte manuell loeschen: {target}")

    if INDEX_FILE.exists():
        content = INDEX_FILE.read_text(encoding='utf-8')
        new_content, removed, found_id = remove_tile_by_file(content, file_rel)
        if removed:
            INDEX_FILE.write_text(new_content, encoding='utf-8')
            print(f"✓ index.html: Tile '{found_id}' entfernt.")
            print(f"  Hinweis: kein manueller Versions-Bump - Dashboard erkennt die Aenderung")
            print(f"  automatisch ueber den DEFAULT_CONFIG-Hash.")
        else:
            print(f"  Hinweis: keine Tile mit file=\"{file_rel}\" in index.html gefunden.")
    return 0


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> int:
    ap = argparse.ArgumentParser(description='Generator fuer neue Grammatikdateien.')
    ap.add_argument('--grade', type=int, choices=ALLOWED_GRADES,
                    help='Klassenstufe (5/6/7/8/9/10).')
    ap.add_argument('--topic', type=str, help='Topic-Slug in snake_case (z.B. conditional_1).')
    ap.add_argument('--unit',  type=int, help='Lighthouse-Unit-Nummer.')
    ap.add_argument('--display', type=str, help='Topic-Anzeigename (z.B. "Conditional I").')
    ap.add_argument('--sub', type=str, help='Untertitel der Tile (Dashboard).')
    ap.add_argument('--icon', type=str, help='Icon-Emoji (Default: 📕).')
    ap.add_argument('--short', type=str,
                    help='Kuerzel fuer Tile-ID (Default: aus Topic abgeleitet).')
    ap.add_argument('--ls-prefix', dest='ls_prefix', type=str,
                    help='LocalStorage-Praefix (Default: aus Topic abgeleitet).')
    ap.add_argument('--force', action='store_true',
                    help='Existierende Zieldatei ueberschreiben.')
    ap.add_argument('--cleanup', type=str, default=None,
                    help='Aufraeum-Modus: gibt eine zu loeschende Datei an. '
                         'Loescht Datei UND zugehoerige Tile aus index.html.')
    args = ap.parse_args()

    if args.cleanup:
        return cmd_cleanup(args)
    return cmd_create(args)


if __name__ == '__main__':
    sys.exit(main())
