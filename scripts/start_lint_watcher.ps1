# PowerShell-Wrapper fuer den Auto-Linter (Phase 2)
# ---------------------------------------------------------------
# Aufgabe: Startet scripts/lint_watcher.py im Hintergrund.
# Aufruf:  manuell per Doppelklick (Rechtsklick -> "Mit PowerShell ausfuehren")
#          oder beim Login automatisch (siehe README, Abschnitt "Auto-Start").
# ---------------------------------------------------------------

$ErrorActionPreference = "Stop"

# Projekt-Root = Elternverzeichnis dieses Skripts
$ScriptDir   = Split-Path -Parent $MyInvocation.MyCommand.Definition
$ProjectRoot = Split-Path -Parent $ScriptDir

# Python-Launcher finden (py -3 ist auf Windows Standard, sonst python.exe)
function Resolve-Python {
    foreach ($cmd in @("py", "python", "python3")) {
        $exe = Get-Command $cmd -ErrorAction SilentlyContinue
        if ($exe) { return $exe.Source }
    }
    throw "Python nicht gefunden. Bitte Python 3.8+ installieren (https://www.python.org/downloads/)."
}

$PythonExe = Resolve-Python
$Linter    = Join-Path $ScriptDir "lint_watcher.py"
$LogFile   = Join-Path $ProjectRoot "lint_watcher.log"

Write-Host "=== Englisch-Lernzentrum - Auto-Linter ==="
Write-Host "Projekt-Root: $ProjectRoot"
Write-Host "Python:       $PythonExe"
Write-Host "Linter:       $Linter"
Write-Host "Log:          $LogFile"
Write-Host ""

# Watchdog optional installieren (effizienter als Polling)
& $PythonExe -c "import watchdog" 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Host "Hinweis: 'watchdog' ist nicht installiert - der Linter laeuft im Polling-Modus."
    Write-Host "Empfohlen (optional): & '$PythonExe' -m pip install watchdog"
    Write-Host ""
}

# Linter starten - Output in Konsole + Log
& $PythonExe $Linter --no-color 2>&1 | Tee-Object -FilePath $LogFile
