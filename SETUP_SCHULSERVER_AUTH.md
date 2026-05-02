# Setup: Schulserver + eigene Domain + Microsoft Entra ID

Schritt-für-Schritt-Anleitung, um das Englisch-Lernzentrum auf dem Schulserver mit eigener Domain und Microsoft-Entra-ID-Login zu betreiben.

**Ziel:** Nur User mit @realschule-xy.de Office-365-Konto kommen rein. Hosting auf eigenem Server, kein GitHub, kein Azure-Hosting.

**Aufwand:** ca. 2–3 Stunden, einmalig. Schul-IT zwingend nötig für Server-Setup und Modul-Installation.

---

## Voraussetzungen

- [ ] **Webspace auf Schulserver** mit Shell-/SSH-Zugang ODER Schul-IT, die Konfigurationsänderungen vornimmt
- [ ] **Apache 2.4 oder neuer** als Webserver (Standard in den meisten Schulservern)
- [ ] **mod_auth_openidc** verfügbar oder installierbar (Apache-Modul für OAuth/OIDC)
- [ ] **Eigene (Sub-)Domain** (z.B. `englisch.realschule-xy.de`) mit Möglichkeit, DNS-Einträge zu setzen
- [ ] **HTTPS-Zertifikat** (Let's Encrypt, kostenlos)
- [ ] **Office 365 / Microsoft 365 Tenant** der Schule
- [ ] **Admin-Rechte in Microsoft Entra ID** (oder jemand bei Schul-IT mit diesen Rechten)

---

## Übersicht der Architektur

```
[Schüler-Browser]
       ↓
       ↓ HTTPS
       ↓
[englisch.realschule-xy.de]  ←  DNS zeigt auf Schulserver
       ↓
[Apache + mod_auth_openidc]  ←  prüft Microsoft-Token
       ↓ (nur wenn authentifiziert)
[/var/www/englisch-lernzentrum/*.html]
       ↓
[Cloudflare Worker für KI-Tutor]  ←  zusätzlicher Token-Check pro Anfrage
       ↓
[Google Gemini API]
```

---

## Phase 1 — Schulserver + Domain einrichten

### 1.1 Webspace anfordern

Schul-IT kontaktieren mit folgender Liste:

- **Verzeichnis:** z.B. `/var/www/englisch-lernzentrum/` oder eigener vhost-Bereich
- **Schreibzugriff:** SSH/SFTP-Zugang für dich
- **Apache-Module:** `mod_auth_openidc` und `mod_ssl` aktiviert
- **Logs:** Zugriff auf `error.log` für Debugging

### 1.2 Subdomain einrichten

Schul-IT bittet, einen DNS-Eintrag anzulegen:

- **Typ:** A-Record (oder CNAME wenn Schulserver hinter Load Balancer)
- **Name:** `englisch`
- **Wert:** IP-Adresse des Schulservers
- **Beispiel:** `englisch.realschule-xy.de` → `192.168.1.100` (oder die echte öffentliche IP)

DNS-Propagation kann bis zu 24 h dauern (meist <30 Min).

### 1.3 HTTPS-Zertifikat (Let's Encrypt)

Falls der Schulserver Certbot kennt:

```bash
sudo certbot --apache -d englisch.realschule-xy.de
```

Das richtet automatisch HTTPS ein und erneuert das Zertifikat alle 90 Tage automatisch.

Falls Schul-IT das macht, dann darauf bestehen — kostenlose SSL ist heute Standard, ohne ist die Microsoft-Anmeldung übrigens nicht möglich (HTTPS-Pflicht).

### 1.4 Dateien hochladen

Per SFTP, SCP oder Schul-IT-Tool den `englisch-lernzentrum/`-Ordnerinhalt nach `/var/www/englisch-lernzentrum/` (oder dein vhost-Pfad) hochladen.

```bash
# Beispiel via rsync
rsync -avz --delete \
  "K:/OneDrive - Hellweg-Realschule/01 - Schule/01 - Englisch/englisch-lernzentrum/" \
  benutzer@schulserver:/var/www/englisch-lernzentrum/
```

(Aus der Git-Bash oder WSL heraus.)

### 1.5 Erster Test (noch ungeschützt!)

Browser: `https://englisch.realschule-xy.de`

Wenn die Seite lädt: Hosting läuft. Jetzt kommt die Auth.

---

## Phase 2 — Microsoft Entra ID App-Registrierung

Identisch zur Azure-Variante — gleiche App kann später erweitert werden.

### 2.1 App registrieren

1. portal.azure.com → Suche „Microsoft Entra ID" → öffnen
2. Linkes Menü: **App registrations** → **New registration**
3. **Name:** `englisch-lernzentrum-auth`
4. **Supported account types:** **Accounts in this organizational directory only** (= nur User aus eurem Schul-Tenant)
5. **Redirect URI:**
   - Plattform: **Web**
   - URL: `https://englisch.realschule-xy.de/oauth2callback`
6. „Register"

Notiere:
- **Application (client) ID** — z.B. `12345678-1234-1234-1234-123456789012`
- **Directory (tenant) ID** — auch oben sichtbar

### 2.2 Client Secret erstellen

1. Linkes Menü: **Certificates & secrets** → **Client secrets** → **New client secret**
2. Beschreibung: `apache-mod-auth-openidc`
3. Expires: **24 months** (Termin im Kalender markieren — danach erneuern!)
4. „Add"
5. **WICHTIG:** Den `Value` (nicht die ID!) sofort kopieren — wird nur EINMAL angezeigt. In Passwort-Manager speichern.

### 2.3 ID-Token-Berechtigung freischalten

1. **Authentication** → unter „Implicit grant and hybrid flows" → ☑ **ID tokens (used for implicit and hybrid flows)**
2. **Save**

---

## Phase 3 — Apache mit mod_auth_openidc konfigurieren

### 3.1 Modul installieren (falls noch nicht da)

```bash
# Debian/Ubuntu
sudo apt install libapache2-mod-auth-openidc
sudo a2enmod auth_openidc
sudo systemctl restart apache2

# CentOS/RHEL
sudo yum install mod_auth_openidc
sudo systemctl restart httpd
```

(Falls Schul-IT das macht, einfach um Installation des Moduls bitten.)

### 3.2 VirtualHost anpassen

In der Apache-Konfiguration (typisch `/etc/apache2/sites-available/englisch.realschule-xy.de.conf`):

```apache
<VirtualHost *:443>
    ServerName englisch.realschule-xy.de
    DocumentRoot /var/www/englisch-lernzentrum

    SSLEngine on
    SSLCertificateFile /etc/letsencrypt/live/englisch.realschule-xy.de/fullchain.pem
    SSLCertificateKeyFile /etc/letsencrypt/live/englisch.realschule-xy.de/privkey.pem

    # === OIDC-Konfiguration ===
    OIDCProviderMetadataURL https://login.microsoftonline.com/DEINE-TENANT-ID/v2.0/.well-known/openid-configuration
    OIDCClientID DEINE-CLIENT-ID
    OIDCClientSecret DEIN-CLIENT-SECRET

    OIDCRedirectURI https://englisch.realschule-xy.de/oauth2callback
    OIDCCryptoPassphrase EIN-LANGES-ZUFAELLIGES-PASSWORT

    OIDCScope "openid email profile"
    OIDCResponseType "code"

    # Cookie & Session
    OIDCCookiePath /
    OIDCSessionInactivityTimeout 28800
    OIDCSessionMaxDuration 28800

    # Domain-Restriction: nur User mit Schul-Mail
    OIDCRemoteUserClaim email

    <Location />
        AuthType openid-connect
        Require valid-user
        # Nur User mit @realschule-xy.de E-Mail
        Require claim email~^[^@]+@realschule-xy\.de$
    </Location>

    # API-Endpoint /.auth/me wie bei Azure: User-Info ausspielen
    <Location /api/me>
        SetHandler oidc-info
        Require valid-user
    </Location>

    ErrorLog ${APACHE_LOG_DIR}/englisch_error.log
    CustomLog ${APACHE_LOG_DIR}/englisch_access.log combined
</VirtualHost>

# HTTP → HTTPS umleiten
<VirtualHost *:80>
    ServerName englisch.realschule-xy.de
    Redirect permanent / https://englisch.realschule-xy.de/
</VirtualHost>
```

**Anpassen:**
- `DEINE-TENANT-ID` aus Schritt 2.1
- `DEINE-CLIENT-ID` aus Schritt 2.1
- `DEIN-CLIENT-SECRET` aus Schritt 2.2
- `EIN-LANGES-ZUFAELLIGES-PASSWORT` zufällig generieren (z.B. `openssl rand -base64 32`) — verschlüsselt die Session-Cookies, Wert beliebig aber geheim halten
- `realschule-xy.de` durch echte Schul-Domain ersetzen

### 3.3 Konfiguration aktivieren

```bash
sudo a2ensite englisch.realschule-xy.de.conf
sudo apache2ctl configtest    # auf Syntax prüfen
sudo systemctl reload apache2
```

### 3.4 Test

1. Inkognito-Browser: `https://englisch.realschule-xy.de`
2. Sollte automatisch auf Microsoft-Login weiterleiten
3. Mit Schul-Konto anmelden
4. Wirst zurückgeleitet, Lernzentrum lädt
5. Test mit privatem Outlook-Konto: ABGELEHNT (richtig)

Wenn Fehler: `tail -f /var/log/apache2/englisch_error.log` zeigt OIDC-Probleme.

---

## Phase 4 — KI-Tutor-Schutz (Cloudflare Worker)

Der Worker muss zusätzlich prüfen, dass Anfragen wirklich von authentifizierten Schul-Schülern kommen — sonst nützt die Apache-Auth nichts (jemand könnte den Worker direkt aufrufen).

### 4.1 User-Token im Frontend besorgen

Apache mit mod_auth_openidc stellt den Token unter `/api/me` bereit (siehe Config oben).

In deinem KI-Tutor-Code (z.B. `shared/tutor.js` oder inline):

```js
async function getUserToken() {
  try {
    const res = await fetch('/api/me', { credentials: 'same-origin' });
    if (!res.ok) return null;
    const data = await res.json();
    // mod_auth_openidc gibt id_token zurück
    return data?.id_token || null;
  } catch (e) {
    return null;
  }
}

// Bei jedem KI-Tutor-Aufruf:
async function callTutor(prompt) {
  const token = await getUserToken();
  if (!token) {
    alert('Bitte neu einloggen.');
    location.reload();
    return;
  }
  const res = await fetch('https://dein-worker.workers.dev/tutor', {
    method: 'POST',
    headers: {
      'Authorization': 'Bearer ' + token,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({ prompt })
  });
  return res.json();
}
```

### 4.2 Worker um Token-Validation erweitern

Im Cloudflare-Worker-Code:

```js
async function verifyMSToken(token, expectedTenantId, expectedDomain) {
  // Token-Header parsen (kein vollständiger JWT-Verifizierungscheck zur Vereinfachung;
  // produktiv: jose-Lib nutzen, gegen Microsoft-Public-Keys prüfen)
  try {
    const payload = JSON.parse(atob(token.split('.')[1]));
    if (payload.tid !== expectedTenantId) return null;
    if (!payload.email?.endsWith('@' + expectedDomain)) return null;
    if (payload.exp < Math.floor(Date.now() / 1000)) return null;
    return payload;
  } catch (e) {
    return null;
  }
}

export default {
  async fetch(request, env) {
    // CORS preflight
    if (request.method === 'OPTIONS') {
      return new Response(null, {
        headers: {
          'Access-Control-Allow-Origin': 'https://englisch.realschule-xy.de',
          'Access-Control-Allow-Methods': 'POST, OPTIONS',
          'Access-Control-Allow-Headers': 'Authorization, Content-Type',
        }
      });
    }

    const auth = request.headers.get('Authorization');
    if (!auth?.startsWith('Bearer ')) {
      return new Response('Unauthorized', { status: 401 });
    }

    const user = await verifyMSToken(
      auth.substring(7),
      env.EXPECTED_TENANT_ID,
      env.EXPECTED_DOMAIN
    );
    if (!user) return new Response('Forbidden', { status: 403 });

    // Optional: Rate-Limit pro user.email via KV
    // ...

    // Anfrage zu Google Gemini durchreichen
    const body = await request.json();
    const geminiRes = await fetch('https://generativelanguage.googleapis.com/...', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        contents: [{ parts: [{ text: body.prompt }] }],
        // Dein Gemini-API-Key aus env.GEMINI_API_KEY
      })
    });

    return new Response(await geminiRes.text(), {
      headers: {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': 'https://englisch.realschule-xy.de'
      }
    });
  }
};
```

### 4.3 Worker-Secrets setzen

Im Cloudflare Dashboard → dein Worker → Settings → Variables:

- `EXPECTED_TENANT_ID` = deine Tenant-ID aus Phase 2
- `EXPECTED_DOMAIN` = `realschule-xy.de`
- `GEMINI_API_KEY` = wie bisher, als Secret

### 4.4 Rate-Limit (empfohlen)

Per Cloudflare KV oder D1 pro User-Email-Hash zählen, max. z.B. 50 Aufrufe/Tag. Bei Überschreitung 429 zurückgeben.

---

## Phase 5 — Deployment-Workflow

### 5.1 Updates hochladen

Bei jeder Änderung im englisch-lernzentrum-Ordner:

```bash
rsync -avz --delete \
  --exclude='*.bak*' \
  --exclude='*.log' \
  --exclude='_test_*' \
  --exclude='.git/' \
  "K:/OneDrive - Hellweg-Realschule/01 - Schule/01 - Englisch/englisch-lernzentrum/" \
  benutzer@schulserver:/var/www/englisch-lernzentrum/
```

Schon fertig — Apache liest die Dateien direkt vom Filesystem.

Alternativ: WinSCP, FileZilla, oder Schul-IT-eigenes Upload-Tool.

### 5.2 Lokale Backups

OneDrive macht das schon — du arbeitest sowieso im OneDrive-Sync-Ordner. Plus die `.bak_*`-Dateien aus den Refactor-Phasen.

Optional: per `git init` lokal ein Mini-Repo für Versionskontrolle anlegen (auch ohne GitHub-Remote sinnvoll für `git diff` und Rollback).

---

## Wichtige Hinweise

### Schul-IT-Abhängigkeiten

Diese Punkte muss die Schul-IT machen — du kannst sie nicht selbst:

1. Apache-Modul `mod_auth_openidc` installieren
2. DNS-Eintrag für die Subdomain
3. Apache-VirtualHost-Konfiguration aktivieren
4. SSL-Zertifikat (Let's Encrypt oder Schul-eigenes)
5. Apache-Reload nach Konfig-Änderungen

Bring der IT die Apache-Config aus Phase 3.2 mit — dann ist der Termin in 30 Minuten erledigt.

### Was du selbst machen kannst

1. Microsoft Entra App-Registrierung (wenn du Office-365-Admin bist; sonst auch IT)
2. Cloudflare-Worker-Code anpassen
3. Dateien per SFTP hochladen
4. Frontend-Code anpassen (KI-Tutor-Auth)

### Backup-Pflicht

Alle Änderungen liegen in deinem OneDrive — gesyncter Backup. Vor größeren Änderungen am Server ein `tar -czf englisch-backup-$(date +%F).tar.gz /var/www/englisch-lernzentrum` machen lassen.

### Token-Refresh

mod_auth_openidc handhabt Session-Cookies und Token-Refresh automatisch. User bleibt 8 Stunden eingeloggt (siehe `OIDCSessionMaxDuration` in der Config).

---

## Troubleshooting

**„AADSTS500113" oder „AADSTS900561"-Fehler:**
Redirect-URI passt nicht. Prüfen, ob in der Entra-App-Registration EXAKT `https://englisch.realschule-xy.de/oauth2callback` steht (Schrägstrich, HTTPS, Großschreibung).

**„No OpenID Connect provider found":**
mod_auth_openidc ist nicht aktiviert. `sudo a2enmod auth_openidc && sudo systemctl restart apache2`.

**Endlose Redirect-Schleife:**
Cookie-Settings — `OIDCCryptoPassphrase` muss gesetzt sein und Cookie-Path muss zur Site passen.

**„HTTP 500" beim Login:**
Apache-Error-Log checken: `sudo tail -50 /var/log/apache2/englisch_error.log`. Häufigste Ursache: falsche Tenant-ID oder Client-Secret.

**KI-Tutor-Anfrage scheitert mit 403:**
Token-Validation im Worker prüft Tenant-ID. Im Browser-DevTools → Network → Request-Header → `Authorization: Bearer ...` decoden auf jwt.io und prüfen, ob `tid` und `email` korrekt sind.

---

## Nächste Schritte

1. **Schul-IT-Termin vereinbaren** mit dieser Anleitung als Vorlage
2. **Microsoft Entra App-Registrierung** (Phase 2) parallel selbst machen, damit IT-Termin nur noch Apache-Config braucht
3. **Cloudflare Worker** vor dem Live-Gang um Token-Validation erweitern
4. **Test-Phase** mit 2–3 Schülern aus deiner Klasse, dann großer Roll-Out
5. **Lehrkräfte-Hinweis im Footer** der Index-Seite ergänzen: „Geschütztes Lernmaterial der Hellweg-Realschule. Vokabel-Listen orientiert am Lehrwerk Lighthouse (Cornelsen). Ausschließlich für interne Nutzung im Englischunterricht."

---

## Falls die Schul-IT mod_auth_openidc NICHT installieren kann

Plan B: **Caddy** als kleiner Auth-Proxy vor Apache:

- Caddy v2 ist Single-Binary, läuft in 2 MB
- Hat eingebauten OIDC-Plugin-Support (caddy-security)
- Kann auf einem anderen Port laufen, leitet authentifizierte Requests an Apache weiter

Wenn das relevant wird: gib Bescheid, dann schreibe ich eine separate Anleitung dafür.

---

*Stand: 28.04.2026. Bei Rückfragen während des Setups einfach durchklingeln.*
