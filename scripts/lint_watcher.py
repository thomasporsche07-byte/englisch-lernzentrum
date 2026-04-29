#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Auto-Linter fuer das Englisch-Lernzentrum (Phase 2)
====================================================

Aufgabe
-------
- Watcht die Ordner `grammatik/` und `uebergreifend/`.
- Prueft jede HTML-Datei beim Speichern (und beim Start einmal komplett)
  gegen die Konventionen aus CLAUDE.md.
- Schreibt Verstoesse a) in die Konsole (rotes "FEHLER")
  und b) in `lint_status.json` im Projekt-Root (fuer UI-Integration).

Aufruf
------
    python scripts/lint_watcher.py             # Watcher-Modus (laeuft permanent)
    python scripts/lint_watcher.py --once      # nur Vollscan, dann beenden
    python scripts/lint_watcher.py --file PATH # nur eine Datei pruefen
    python scripts/lint_watcher.py --json-only # kein Konsolen-Output, nur JSON
    python scripts/lint_watcher.py --no-color  # ohne ANSI-Farben

Abhaengigkeiten
---------------
- Python 3.8+ (ueberall vorhanden, auf Windows ueber `py`-Launcher).
- OPTIONAL: `watchdog` fuer effizientes File-Watching.
    pip install watchdog
  Wenn nicht installiert, faellt der Watcher automatisch auf Polling zurueck
  (mtime-Vergleich alle 2 Sekunden) - funktional gleichwertig, nur etwas
  hoeherer CPU-Verbrauch.
- OPTIONAL: `node` (Node.js) fuer Inline-JS-Syntaxpruefung via `node --check`.
  Ohne node wird die JS-Pruefung uebersprungen (nicht kritisch).
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import tempfile
import time
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Iterable

# ---------------------------------------------------------------------------
# Konfiguration
# ---------------------------------------------------------------------------

# Projekt-Root = Elternverzeichnis von scripts/
PROJECT_ROOT = Path(__file__).resolve().parent.parent
WATCH_DIRS   = [PROJECT_ROOT / "grammatik", PROJECT_ROOT / "uebergreifend"]
STATUS_FILE  = PROJECT_ROOT / "lint_status.json"

# Verbotene Fachbegriffe in sichtbarem Text (CLAUDE.md, Abschnitt "Sprache / Stil")
# Werden case-insensitive geprueft, aber nur ausserhalb von <script>, <style>
# und HTML-Kommentaren - Code-Variablen mit "infinitive" sind also erlaubt.
FORBIDDEN_TERMS = [
    "Infinitiv",
    "partiell",
    "nominal",
    "Auxiliarverb",
    "Kopula",
    "elliptisch",
    "Modalverb-Periphrase",
]

# Pflicht-Includes im <head>
REQUIRED_CSS = [
    '../shared/style.css',
    '../shared/quiz.css',
    '../shared/tutor.css',
]

# Pflicht-Includes am <body>-Ende (Reihenfolge wird zusaetzlich geprueft)
REQUIRED_JS = [
    '../shared/scorecards.js',
    '../shared/quiz.js',
    '../shared/tutor.js',
]

# Pflicht-Aufrufe (Substring-Suche)
REQUIRED_CALLS = [
    'HRQuiz.init(',
    'HRShared.initDarkMode',
    'HRShared.initTTS',
    'HRShared.initResetAllButton',
]

# Pflicht-Felder in window.TUTOR_CONFIG
TUTOR_CONFIG_FIELDS = [
    'topic',
    'grade',
    'unit',
    'rules',
    'welcomeMessage',
    'quickChips',
    'typicalErrors',
]

# Generische LS-Keys, die (allein) auf fehlenden Datei-Prefix hindeuten.
GENERIC_LS_KEYS = {
    'progress', 'dark', 'darkmode', 'dark_mode', 'states', 'open',
    'openacc', 'config', 'settings', 'tts', 'theme', 'data', 'state',
}

# Dateinamen-Endungen, die wir pruefen
LINT_EXT = {'.html', '.htm'}

# ANSI-Farben
class C:
    RED    = '\033[91m'
    GREEN  = '\033[92m'
    YELLOW = '\033[93m'
    BLUE   = '\033[94m'
    GREY   = '\033[90m'
    BOLD   = '\033[1m'
    RESET  = '\033[0m'

USE_COLOR = True
def c(text: str, color: str) -> str:
    return f"{color}{text}{C.RESET}" if USE_COLOR else text


# ---------------------------------------------------------------------------
# Datenmodell
# ---------------------------------------------------------------------------

@dataclass
class Issue:
    """Ein einzelner Lint-Verstoss."""
    rule:    str   # Regel-ID, z.B. "forbidden-term"
    message: str   # Mensch-lesbarer Text
    line:    int = 0  # 1-basiert, 0 = unbekannt

@dataclass
class FileReport:
    """Lint-Bericht fuer eine einzelne Datei."""
    file:   str
    issues: list[Issue] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return len(self.issues) == 0


# ---------------------------------------------------------------------------
# HTML/JS-Helper
# ---------------------------------------------------------------------------

_RE_COMMENT = re.compile(r'<!--.*?-->', re.DOTALL)
_RE_STYLE   = re.compile(r'<style\b[^>]*>.*?</style>', re.DOTALL | re.IGNORECASE)
_RE_SCRIPT  = re.compile(r'<script\b[^>]*>.*?</script>', re.DOTALL | re.IGNORECASE)
_RE_TAG     = re.compile(r'<[^>]+>', re.DOTALL)

def strip_for_visible_text(html: str) -> str:
    """
    Liefert den sichtbaren Text - ohne Kommentare, <style>, <script>.
    Tags selbst werden zu Leerzeichen, damit Wortgrenzen erhalten bleiben.
    """
    s = _RE_COMMENT.sub(' ', html)
    s = _RE_STYLE.sub(' ', s)
    s = _RE_SCRIPT.sub(' ', s)
    # Attribute koennen weiterhin "sichtbaren" Text enthalten (placeholder, title, alt).
    # Das ist fuer den Forbidden-Term-Check ok - dort lieber zu viel als zu wenig.
    return s

def extract_inline_scripts(html: str) -> list[tuple[int, str]]:
    """
    Liefert (start_line, code) fuer alle <script>...</script>-Bloecke
    OHNE `src=`-Attribut. Fuer JS-Syntaxcheck.
    """
    out: list[tuple[int, str]] = []
    for m in re.finditer(
        r'<script\b([^>]*)>(.*?)</script>', html, re.DOTALL | re.IGNORECASE
    ):
        attrs = m.group(1)
        if re.search(r'\bsrc\s*=', attrs, re.IGNORECASE):
            continue
        body = m.group(2)
        if not body.strip():
            continue
        # Zeilennummer-Berechnung
        line = html.count('\n', 0, m.start(2)) + 1
        out.append((line, body))
    return out

def line_of_offset(text: str, offset: int) -> int:
    return text.count('\n', 0, offset) + 1


# ---------------------------------------------------------------------------
# Einzelregel-Checker
# ---------------------------------------------------------------------------

def check_required_includes(html: str, issues: list[Issue]) -> None:
    """Pflicht-CSS- und JS-Includes pruefen.

    CSS muss im <head> liegen, JS darf je nach Datei in <head> ODER am <body>-Ende
    stehen (Phase 1b-Refactor hat scorecards.js + quiz.js teilweise in den <head>
    verschoben). Wir suchen daher im gesamten Dokument, melden aber Reihenfolge-
    Verletzungen.
    """
    head_match = re.search(r'<head\b[^>]*>(.*?)</head>', html, re.DOTALL | re.IGNORECASE)
    head = head_match.group(1) if head_match else ''
    for css in REQUIRED_CSS:
        if css not in head:
            issues.append(Issue(
                rule="missing-shared-css",
                message=f'Pflicht-CSS-Include fehlt im <head>: <link href="{css}">',
            ))

    js_positions: list[int] = []
    for js in REQUIRED_JS:
        idx = html.find(js)
        if idx == -1:
            issues.append(Issue(
                rule="missing-shared-js",
                message=f'Pflicht-JS-Include fehlt: <script src="{js}">',
            ))
        js_positions.append(idx)

    # Reihenfolge: scorecards.js -> quiz.js -> tutor.js
    if all(p >= 0 for p in js_positions):
        if not (js_positions[0] < js_positions[1] < js_positions[2]):
            issues.append(Issue(
                rule="shared-js-order",
                message='Falsche <script>-Reihenfolge - Pflicht: '
                        'scorecards.js, quiz.js, tutor.js (in dieser Reihenfolge).',
            ))

def check_required_calls(html: str, issues: list[Issue]) -> None:
    """Verlangte Funktionsaufrufe in Inline-Skripten."""
    inline_js = '\n'.join(code for _, code in extract_inline_scripts(html))
    for call in REQUIRED_CALLS:
        if call not in inline_js:
            issues.append(Issue(
                rule="missing-required-call",
                message=f'Pflicht-Aufruf fehlt: {call}…',
            ))

def check_tutor_mount(html: str, issues: list[Issue]) -> None:
    if 'id="tutor-mount"' not in html and "id='tutor-mount'" not in html:
        issues.append(Issue(
            rule="missing-tutor-mount",
            message='Pflicht-Markup fehlt: <div id="tutor-mount"></div>',
        ))

def check_tutor_config(html: str, issues: list[Issue]) -> None:
    """window.TUTOR_CONFIG existiert und enthaelt Pflicht-Felder."""
    inline_js = '\n'.join(code for _, code in extract_inline_scripts(html))
    if 'window.TUTOR_CONFIG' not in inline_js:
        issues.append(Issue(
            rule="missing-tutor-config",
            message='window.TUTOR_CONFIG ist nicht definiert.',
        ))
        return
    # Block grob extrahieren: ab "window.TUTOR_CONFIG" bis zur passenden };
    m = re.search(r'window\.TUTOR_CONFIG\s*=\s*\{', inline_js)
    if not m:
        return
    block = _balanced_object(inline_js, m.end() - 1)
    if not block:
        return
    for fld in TUTOR_CONFIG_FIELDS:
        # Feld als Property (am Zeilenanfang oder nach Komma/Whitespace)
        if not re.search(r'(^|[\s,{])' + re.escape(fld) + r'\s*:', block):
            issues.append(Issue(
                rule="tutor-config-field-missing",
                message=f'window.TUTOR_CONFIG: Pflicht-Feld "{fld}" fehlt.',
            ))

def _balanced_object(text: str, start_brace_idx: int) -> str:
    """Liefert den String von { bis zur passenden } (naiv, ohne JSON-Parser)."""
    if start_brace_idx >= len(text) or text[start_brace_idx] != '{':
        return ''
    depth = 0
    i = start_brace_idx
    in_str = False
    str_ch = ''
    while i < len(text):
        ch = text[i]
        if in_str:
            if ch == '\\':
                i += 2
                continue
            if ch == str_ch:
                in_str = False
        else:
            if ch in ('"', "'", '`'):
                in_str = True
                str_ch = ch
            elif ch == '{':
                depth += 1
            elif ch == '}':
                depth -= 1
                if depth == 0:
                    return text[start_brace_idx:i + 1]
        i += 1
    return ''

def check_forbidden_terms(html: str, issues: list[Issue]) -> None:
    """Verbotene Fachbegriffe in sichtbarem Text."""
    visible = strip_for_visible_text(html)
    # Wir wollen Zeilennummer im ORIGINAL - dafuer den Original-HTML-Text durchsuchen,
    # aber innerhalb von <script>/<style>/Kommentar-Bereichen ueberspringen.
    skip_ranges = _build_skip_ranges(html)
    for term in FORBIDDEN_TERMS:
        # Wortgrenzen (kein "Inhalts-" als Treffer auf "Infinitiv" etc.)
        pattern = re.compile(r'\b' + re.escape(term) + r'\b', re.IGNORECASE)
        for m in pattern.finditer(html):
            if _in_any_range(m.start(), skip_ranges):
                continue
            issues.append(Issue(
                rule="forbidden-term",
                message=f'Verbotener Fachbegriff im sichtbaren Text: "{term}".',
                line=line_of_offset(html, m.start()),
            ))

def _build_skip_ranges(html: str) -> list[tuple[int, int]]:
    """Bereiche (start, end), die fuer den Sichtbaren-Text-Check ignoriert werden."""
    ranges = []
    for rx in (_RE_COMMENT, _RE_STYLE, _RE_SCRIPT):
        for m in rx.finditer(html):
            ranges.append((m.start(), m.end()))
    return ranges

def _in_any_range(pos: int, ranges: list[tuple[int, int]]) -> bool:
    return any(s <= pos < e for s, e in ranges)

def check_pronoun_table_in_card(html: str, issues: list[Issue]) -> None:
    """
    Pronomen-Listen wie "he/she/it" oder "you/we/they" duerfen NICHT als
    Klartext-Block in Regelkarten stehen - dort sollen sie als pill-Formel
    aufgeteilt sein. Wir suchen nach diesen Mustern innerhalb von rc-card-Bloecken
    (Heuristik - kann False-Positives haben).
    """
    pattern = re.compile(
        r'\b(?:he/she/it|you/we/they|I/we/you/they)\b',
        re.IGNORECASE,
    )
    # Alle rc-card-Bloecke extrahieren (DOTALL, naive Klammerung bis zum naechsten
    # </div>-Block). Wir nehmen lieber eine grobe Region um jede rc-card und pruefen
    # darin, statt strukturell zu parsen.
    for cm in re.finditer(r'<div\s+class\s*=\s*"rc-card[^"]*"', html, re.IGNORECASE):
        start = cm.start()
        # Region bis zum naechsten </section> oder bis +4000 Zeichen
        end = html.find('</section>', start)
        if end == -1 or end - start > 4000:
            end = start + 4000
        region = html[start:end]
        # Innerhalb der Region: <style>/<script>/Kommentare gibt es i.d.R. nicht,
        # aber die Pillen sehen so aus: <span class="fc fc-subj">he</span>.
        # Wir wollen NUR Klartext-Treffer ausserhalb solcher Spans melden.
        # Daher: erst inline-Tags rausnehmen und das Ergebnis nach Pattern absuchen.
        text_only = _RE_TAG.sub(' ', region)
        for m in pattern.finditer(text_only):
            issues.append(Issue(
                rule="pronoun-cluster-in-card",
                message=f'Pronomen-Cluster "{m.group(0)}" als Klartext '
                        f'in einer Regelkarte gefunden - bitte als Pill-Formel auftrennen.',
                line=line_of_offset(html, start),
            ))
            break  # pro rc-card nur ein Hinweis

def check_br_in_rc_formula(html: str, issues: list[Issue]) -> None:
    """<br> innerhalb von <div class="rc-formula"> ist verboten."""
    for m in re.finditer(
        r'<div\s+class\s*=\s*"rc-formula[^"]*"[^>]*>(.*?)</div>',
        html, re.DOTALL | re.IGNORECASE,
    ):
        if re.search(r'<br\b', m.group(1), re.IGNORECASE):
            issues.append(Issue(
                rule="br-in-rc-formula",
                message='<br> innerhalb von <div class="rc-formula"> verboten - '
                        'stattdessen zwei separate <div class="rc-formula">.',
                line=line_of_offset(html, m.start()),
            ))

def check_localstorage_keys(html: str, issues: list[Issue], file_path: Path) -> None:
    """
    LocalStorage-Keys muessen einen dateispezifischen Prefix tragen.

    Wir pruefen NUR direkte `localStorage.{getItem,setItem,removeItem}('KEY', ...)`-
    Aufrufe. Wrapper wie `tbSave('openAcc', ...)` werden nicht geprueft, da der
    Wrapper den Prefix intern selbst setzt (z.B. `localStorage.setItem('tobe_'+key, ...)`).

    Verstoss, wenn der Key entweder
      - ein generisches Wort ist (siehe GENERIC_LS_KEYS), oder
      - keinen Unterstrich hat und nicht mit dem Datei-Stem-Praefix beginnt.
    """
    inline_js = '\n'.join(code for _, code in extract_inline_scripts(html))
    keys_seen: set[str] = set()
    rx = re.compile(
        r'localStorage\.(?:getItem|setItem|removeItem)\(\s*[\'"`]([^\'"`]+)[\'"`]'
    )
    for m in rx.finditer(inline_js):
        key = m.group(1)
        # String-Konkatenation wie 'tobe_'+key ergibt keinen statisch lesbaren Key -
        # solche Faelle erfasst die Regex nicht und das ist okay.
        keys_seen.add(key)

    stem_prefix = file_path.stem.lower().replace('-', '_').split('_', 1)[0][:6]
    for key in keys_seen:
        bare = key.lower()
        if bare in GENERIC_LS_KEYS:
            issues.append(Issue(
                rule="ls-key-generic",
                message=f'LocalStorage-Key "{key}" hat keinen dateispezifischen '
                        f'Prefix - bitte z.B. "{file_path.stem.lower()}_{key}" verwenden.',
            ))
        elif '_' not in key and not bare.startswith(stem_prefix):
            issues.append(Issue(
                rule="ls-key-no-prefix",
                message=f'LocalStorage-Key "{key}" hat keinen Unterstrich - '
                        f'sieht nach fehlendem Prefix aus.',
            ))

def check_tag_balance(html: str, issues: list[Issue]) -> None:
    """Grobe Pruefung auf gleich viele oeffnende wie schliessende Tags."""
    for tag in ('html', 'head', 'body', 'section', 'details'):
        op = len(re.findall(rf'<{tag}\b', html, re.IGNORECASE))
        cl = len(re.findall(rf'</{tag}>', html, re.IGNORECASE))
        if op != cl:
            issues.append(Issue(
                rule="tag-imbalance",
                message=f'Tag-Balance verletzt: <{tag}> oeffnet {op}x, schliesst {cl}x.',
            ))

def check_inline_js_syntax(html: str, issues: list[Issue]) -> None:
    """Jeder Inline-<script> wird via `node --check` syntaktisch geprueft."""
    if not _NODE_AVAILABLE:
        return
    for line, code in extract_inline_scripts(html):
        # Module-Imports / Top-level await koennen `node --check` stoeren -
        # bei Schul-Dateien aber praktisch nie der Fall.
        try:
            with tempfile.NamedTemporaryFile(
                'w', suffix='.js', delete=False, encoding='utf-8'
            ) as tf:
                tf.write(code)
                tmp_path = tf.name
            res = subprocess.run(
                ['node', '--check', tmp_path],
                capture_output=True, text=True, timeout=10,
            )
            if res.returncode != 0:
                err = res.stderr.strip().splitlines()[-1] if res.stderr.strip() else 'Syntax error'
                issues.append(Issue(
                    rule="js-syntax",
                    message=f'Inline-JS-Syntaxfehler: {err}',
                    line=line,
                ))
        except subprocess.TimeoutExpired:
            issues.append(Issue(
                rule="js-syntax",
                message='node --check hat sich aufgehaengt (Timeout 10s).',
                line=line,
            ))
        finally:
            try:
                os.unlink(tmp_path)
            except OSError:
                pass

def _check_node_available() -> bool:
    try:
        subprocess.run(
            ['node', '--version'], capture_output=True, timeout=5,
        )
        return True
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False

_NODE_AVAILABLE = _check_node_available()


# ---------------------------------------------------------------------------
# Haupt-Lint-Funktion
# ---------------------------------------------------------------------------

def lint_file(path: Path) -> FileReport:
    """Wendet alle Regeln auf eine Datei an."""
    try:
        rel = str(path.relative_to(PROJECT_ROOT)).replace('\\', '/')
    except ValueError:
        # Datei liegt nicht unter PROJECT_ROOT (z.B. /tmp/foo.html bei manuellem Test)
        rel = str(path).replace('\\', '/')
    rep = FileReport(file=rel)
    try:
        html = path.read_text(encoding='utf-8')
    except (OSError, UnicodeDecodeError) as e:
        rep.issues.append(Issue(rule="read-error", message=f'Datei konnte nicht gelesen werden: {e}'))
        return rep

    is_grammatik = '/grammatik/' in rel.replace('\\', '/')
    # Strict-Pflichten gelten laut CLAUDE.md fuer JEDE Grammatikdatei.
    # uebergreifend/-Tools (false_friends, schreibtrainer, word_order) haben
    # eigene Logik und sind hiervon ausgenommen - dort pruefen wir nur die
    # universellen Regeln.

    # Universelle Regeln (alle Dateien)
    check_forbidden_terms(html, rep.issues)
    check_br_in_rc_formula(html, rep.issues)
    check_pronoun_table_in_card(html, rep.issues)
    check_tag_balance(html, rep.issues)
    check_inline_js_syntax(html, rep.issues)
    check_localstorage_keys(html, rep.issues, path)

    # Pflichten nur fuer Grammatikdateien
    if is_grammatik:
        check_required_includes(html, rep.issues)
        check_required_calls(html, rep.issues)
        check_tutor_mount(html, rep.issues)
        check_tutor_config(html, rep.issues)

    # Sortierung: erst nach Zeile, dann nach Regel-ID
    rep.issues.sort(key=lambda i: (i.line, i.rule))
    return rep


# ---------------------------------------------------------------------------
# Ausgabe
# ---------------------------------------------------------------------------

def print_report(rep: FileReport) -> None:
    if rep.ok:
        print(c(f'OK   {rep.file}', C.GREEN))
        return
    print(c(f'FAIL {rep.file}  ({len(rep.issues)} Verstoss/Verstoesse)', C.RED + C.BOLD))
    for iss in rep.issues:
        loc = f':{iss.line}' if iss.line else ''
        print(c(f'  -> [{iss.rule}]{loc}  {iss.message}', C.YELLOW))

def write_status(reports: dict[str, FileReport]) -> None:
    """Schreibt lint_status.json mit allen aktuellen Verstoessen."""
    payload = {
        'updated': time.strftime('%Y-%m-%d %H:%M:%S'),
        'project_root': str(PROJECT_ROOT),
        'node_available': _NODE_AVAILABLE,
        'files': [
            {
                'file': r.file,
                'ok': r.ok,
                'issue_count': len(r.issues),
                'issues': [asdict(i) for i in r.issues],
            }
            for r in sorted(reports.values(), key=lambda r: r.file)
        ],
        'summary': {
            'total_files':  len(reports),
            'files_ok':     sum(1 for r in reports.values() if r.ok),
            'files_failed': sum(1 for r in reports.values() if not r.ok),
            'total_issues': sum(len(r.issues) for r in reports.values()),
        },
    }
    STATUS_FILE.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2), encoding='utf-8'
    )


# ---------------------------------------------------------------------------
# Datei-Sammlung + Watch
# ---------------------------------------------------------------------------

def find_lint_files() -> list[Path]:
    out: list[Path] = []
    for d in WATCH_DIRS:
        if not d.is_dir():
            continue
        for p in d.iterdir():
            if p.is_file() and p.suffix.lower() in LINT_EXT and not p.name.endswith('.bak'):
                out.append(p)
    return sorted(out)

def full_scan(json_only: bool = False) -> dict[str, FileReport]:
    files = find_lint_files()
    reports: dict[str, FileReport] = {}
    for f in files:
        rep = lint_file(f)
        reports[str(f)] = rep
        if not json_only:
            print_report(rep)
    write_status(reports)
    if not json_only:
        n_ok   = sum(1 for r in reports.values() if r.ok)
        n_fail = len(reports) - n_ok
        print(c(
            f'\n=== {len(reports)} Dateien geprueft - '
            f'{n_ok} OK, {n_fail} mit Verstoessen ===',
            C.BLUE + C.BOLD,
        ))
        if not _NODE_AVAILABLE:
            print(c(
                'Hinweis: node nicht gefunden - Inline-JS-Syntaxcheck uebersprungen.',
                C.GREY,
            ))
    return reports


# ---------- watchdog-Variante ----------

def watch_with_watchdog(reports: dict[str, FileReport], json_only: bool) -> None:
    from watchdog.events import FileSystemEventHandler
    from watchdog.observers import Observer

    class Handler(FileSystemEventHandler):
        def __init__(self):
            self._last: dict[str, float] = {}

        def _on_change(self, path_str: str) -> None:
            p = Path(path_str)
            if p.suffix.lower() not in LINT_EXT or p.name.endswith('.bak'):
                return
            # Debounce - viele Editoren feuern mehrere Events pro Save.
            now = time.time()
            if now - self._last.get(path_str, 0) < 0.4:
                return
            self._last[path_str] = now
            try:
                rep = lint_file(p)
            except Exception as e:                                  # noqa: BLE001
                print(c(f'Lint-Fehler in {p}: {e}', C.RED))
                return
            reports[str(p)] = rep
            if not json_only:
                print_report(rep)
            write_status(reports)

        def on_modified(self, event):  # noqa: D401, N802
            if not event.is_directory:
                self._on_change(event.src_path)

        def on_created(self, event):  # noqa: D401, N802
            if not event.is_directory:
                self._on_change(event.src_path)

    obs = Observer()
    handler = Handler()
    for d in WATCH_DIRS:
        if d.is_dir():
            obs.schedule(handler, str(d), recursive=False)
    obs.start()
    print(c(f'Watcher (watchdog) laeuft - Strg+C zum Beenden.', C.BLUE))
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        pass
    finally:
        obs.stop()
        obs.join()


# ---------- Polling-Variante ----------

def watch_with_polling(reports: dict[str, FileReport], json_only: bool) -> None:
    print(c('Watcher (Polling, kein watchdog installiert) laeuft - Strg+C zum Beenden.', C.BLUE))
    print(c('Tipp: `pip install watchdog` fuer effizientes File-Watching.', C.GREY))
    mtimes: dict[Path, float] = {p: p.stat().st_mtime for p in find_lint_files()}
    try:
        while True:
            time.sleep(2)
            current = {p: p.stat().st_mtime for p in find_lint_files()}
            # Geaenderte oder neue Dateien
            for p, m in current.items():
                if mtimes.get(p) != m:
                    rep = lint_file(p)
                    reports[str(p)] = rep
                    if not json_only:
                        print_report(rep)
                    write_status(reports)
            # Geloeschte Dateien
            for p in list(mtimes.keys()):
                if p not in current:
                    reports.pop(str(p), None)
                    write_status(reports)
            mtimes = current
    except KeyboardInterrupt:
        pass


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> int:
    global USE_COLOR
    parser = argparse.ArgumentParser(description='Auto-Linter fuer das Englisch-Lernzentrum.')
    parser.add_argument('--once', action='store_true',
                        help='Nur Vollscan, danach beenden (kein Watcher).')
    parser.add_argument('--file', type=Path, default=None,
                        help='Nur diese eine Datei pruefen (Pfad relativ oder absolut).')
    parser.add_argument('--json-only', action='store_true',
                        help='Kein Konsolen-Output, nur lint_status.json schreiben.')
    parser.add_argument('--no-color', action='store_true',
                        help='Keine ANSI-Farben (z.B. fuer Windows-CMD ohne Color-Support).')
    args = parser.parse_args()

    if args.no_color or os.environ.get('NO_COLOR'):
        USE_COLOR = False

    if args.file:
        p = args.file if args.file.is_absolute() else (PROJECT_ROOT / args.file)
        if not p.exists():
            print(c(f'Datei nicht gefunden: {p}', C.RED))
            return 2
        rep = lint_file(p)
        if not args.json_only:
            print_report(rep)
        # Status nur fuer diese Datei aktualisieren - vorhandene Daten erhalten.
        existing: dict[str, FileReport] = {}
        if STATUS_FILE.exists():
            try:
                data = json.loads(STATUS_FILE.read_text(encoding='utf-8'))
                for entry in data.get('files', []):
                    existing[str(PROJECT_ROOT / entry['file'])] = FileReport(
                        file=entry['file'],
                        issues=[Issue(**i) for i in entry.get('issues', [])],
                    )
            except (OSError, json.JSONDecodeError):
                pass
        existing[str(p)] = rep
        write_status(existing)
        return 0 if rep.ok else 1

    reports = full_scan(json_only=args.json_only)
    if args.once:
        return 0 if all(r.ok for r in reports.values()) else 1

    try:
        import watchdog  # noqa: F401
        watch_with_watchdog(reports, args.json_only)
    except ImportError:
        watch_with_polling(reports, args.json_only)
    return 0


if __name__ == '__main__':
    sys.exit(main())
