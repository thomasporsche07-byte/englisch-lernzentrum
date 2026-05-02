# Setup: Azure Static Web Apps + Microsoft Entra ID

Schritt-für-Schritt-Anleitung, um das Englisch-Lernzentrum hinter eine Schul-Login-Wand zu stellen.

**Ziel:** Nur User mit @realschule-xy.de Office-365-Konto kommen rein. Kosten: 0 € im Free-Tier.

**Aufwand:** ca. 1,5–2 Stunden, einmalig. Schul-IT eventuell nötig für Azure-Subscription und Entra-App-Registrierung.

---

## Voraussetzungen

- [ ] **Office 365 / Microsoft 365 Tenant** der Schule (habt ihr)
- [ ] **GitHub-Account** mit deinem englisch-lernzentrum-Repo (oder neu anlegen)
- [ ] **Azure-Subscription** — entweder Schul-Azure-Subscription, oder kostenloses Azure-Konto (200 $ Startguthaben für 30 Tage, danach Free-Tier-Dienste)
- [ ] **Admin-Rechte in Microsoft Entra ID** — falls du selbst keine hast, ist das die Schul-IT bzw. Microsoft-365-Admin

---

## Phase 1 — GitHub-Repo vorbereiten

### 1.1 Repo erstellen (falls noch nicht vorhanden)

1. github.com → New repository
2. Name z.B. `englisch-lernzentrum`
3. Private oder Public — beides geht (Auth läuft separat)
4. Erstellen

### 1.2 Lokale Dateien hochladen

Im englisch-lernzentrum-Ordner:

```bash
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/DEIN-USERNAME/englisch-lernzentrum.git
git push -u origin main
```

(Falls du noch nie mit Git gearbeitet hast: GitHub Desktop oder VSCode-Git-Integration tun's auch.)

### 1.3 `.gitignore` ergänzen

Im Repo-Root eine Datei `.gitignore`:

```
*.bak*
*.bak_*
_test_*.txt
_bashtest.txt
.DS_Store
Thumbs.db
```

---

## Phase 2 — Azure Static Web App erstellen

### 2.1 Azure-Subscription besorgen

Zwei Wege:

**A) Schul-Subscription:** Schul-IT fragen, ob es schon eine Azure-Subscription gibt. Oft mit Microsoft 365 Education gekoppelt.

**B) Eigenes Konto:** azure.microsoft.com/free → mit Schul-Microsoft-Account anmelden → Free Account erstellen. Kreditkarte für Identitätsprüfung nötig (wird nicht belastet, solange du im Free-Tier bleibst).

### 2.2 Static Web App im Portal erstellen

1. portal.azure.com → oben in Suchleiste „Static Web Apps" → „Create"
2. **Subscription:** deine Subscription auswählen
3. **Resource Group:** „Create new" → Name z.B. `rg-englisch-lernzentrum`
4. **Name:** z.B. `englisch-lernzentrum`
5. **Plan type:** **Free**
6. **Region for Azure Functions API:** West Europe (oder Frankreich Central)
7. **Source:** **GitHub**
8. Auf „Sign in with GitHub" klicken → autorisieren
9. **Organization:** dein GitHub-User
10. **Repository:** `englisch-lernzentrum`
11. **Branch:** `main`
12. **Build Presets:** **Custom**
    - **App location:** `/`
    - **Api location:** (leer lassen)
    - **Output location:** (leer lassen)
13. „Review + create" → „Create"

Azure legt jetzt automatisch:
- Eine Static Web App an
- Eine `.github/workflows/azure-static-web-apps-XYZ.yml` in deinem Repo (für automatisches Deployment bei jedem Push)
- Beim ersten Push wird deployed

### 2.3 Erste URL prüfen

Nach 1–2 Minuten zeigt das Azure-Portal eine URL wie:
`https://nice-tree-12345.6.azurestaticapps.net`

Aufrufen → die Seite sollte ungeschützt erscheinen. Wenn ja: Hosting läuft. Jetzt kommt die Auth.

---

## Phase 3 — Microsoft Entra ID App-Registrierung

### 3.1 App registrieren

1. portal.azure.com → Suche „Microsoft Entra ID" → öffnen
2. Linkes Menü: **App registrations** → **New registration**
3. **Name:** `englisch-lernzentrum-auth`
4. **Supported account types:** **Accounts in this organizational directory only** (= nur User aus deinem Schul-Tenant)
5. **Redirect URI:**
   - Plattform: **Web**
   - URL: `https://NICE-TREE-12345.6.azurestaticapps.net/.auth/login/aad/callback` (deine echte Static-Web-App-URL eintragen, behalte das Suffix `/.auth/login/aad/callback`)
6. „Register"

Du landest auf der App-Übersichtsseite. Notiere dir:
- **Application (client) ID** — Beispiel: `12345678-1234-1234-1234-123456789012`
- **Directory (tenant) ID** — auch oben sichtbar

### 3.2 Client Secret erstellen

1. Linkes Menü: **Certificates & secrets** → **Client secrets** → **New client secret**
2. Beschreibung: `static-web-app-secret`
3. Expires: **24 months** (oder nach Schul-Policy)
4. „Add"
5. **WICHTIG:** Den `Value` (nicht die ID!) sofort kopieren — wird nur EINMAL angezeigt. Sicher speichern (z.B. in einem Passwort-Manager).

### 3.3 (Optional aber empfohlen) Domain-Restriction

Falls du nur Schüler eines bestimmten E-Mail-Suffixes erlauben willst (z.B. `@hellweg-realschule.de`):

1. Auf der App-Übersicht: **Token configuration** → **Add optional claim**
2. Token type: **ID** → Claim: **upn** auswählen → Add
3. Wird später in der `staticwebapp.config.json` gefiltert.

---

## Phase 4 — Auth in der Static Web App konfigurieren

### 4.1 Configuration-Datei im Repo anlegen

Lege im Repo-Root die Datei `staticwebapp.config.json` an:

```json
{
  "auth": {
    "identityProviders": {
      "azureActiveDirectory": {
        "registration": {
          "openIdIssuer": "https://login.microsoftonline.com/DEINE-TENANT-ID/v2.0",
          "clientIdSettingName": "AAD_CLIENT_ID",
          "clientSecretSettingName": "AAD_CLIENT_SECRET"
        }
      }
    }
  },
  "routes": [
    {
      "route": "/.auth/login/aad",
      "rewrite": "/.auth/login/aad?domain_hint=hellweg-realschule.de"
    },
    {
      "route": "/*",
      "allowedRoles": ["authenticated"]
    }
  ],
  "responseOverrides": {
    "401": {
      "redirect": "/.auth/login/aad",
      "statusCode": 302
    }
  },
  "globalHeaders": {
    "Cache-Control": "no-cache"
  }
}
```

**Anpassen:**
- `DEINE-TENANT-ID` durch echte Directory-ID aus Schritt 3.1 ersetzen
- `hellweg-realschule.de` durch eure echte Schul-Domain (vereinfacht den Login: User landet sofort auf der Schul-Anmeldeseite)

### 4.2 Secrets in Azure hinterlegen

1. Im Azure-Portal zur Static Web App zurück
2. Linkes Menü: **Configuration** → **Application settings**
3. **Add** → Name: `AAD_CLIENT_ID`, Value: die Application-ID aus Schritt 3.1
4. **Add** → Name: `AAD_CLIENT_SECRET`, Value: das Secret aus Schritt 3.2
5. **Save**

### 4.3 Push triggern

```bash
git add staticwebapp.config.json
git commit -m "Add Entra ID auth config"
git push
```

Nach 1–2 Minuten ist deployed.

### 4.4 Test

1. Inkognito-Fenster öffnen
2. URL aufrufen: `https://NICE-TREE-12345.6.azurestaticapps.net`
3. Du wirst auf die Microsoft-Login-Seite umgeleitet
4. Mit Schul-Konto anmelden → kommst rein
5. Mit privatem Outlook-Konto anmelden → ABGELEHNT (richtig so)

Wenn das funktioniert: **Auth läuft.**

---

## Phase 5 — Eigene Domain (optional, aber empfohlen)

Statt `nice-tree-12345.6.azurestaticapps.net` lieber `englisch.hellweg-realschule.de`.

### 5.1 Domain einrichten

1. In Azure-Portal → Static Web App → **Custom domains** → **+ Add**
2. **Custom domain on other DNS:** wenn die Domain-Verwaltung nicht bei Azure liegt
3. Domain eingeben: `englisch.hellweg-realschule.de`
4. Azure zeigt dir DNS-Einträge an, die du in eurer DNS-Verwaltung anlegen lassen musst (Schul-IT, Strato, IONOS o.ä.)
5. Nach DNS-Propagation (10 Min – 24 h): Validate → Done

### 5.2 Redirect-URI in Entra-App ergänzen

1. Zurück zu Microsoft Entra ID → App registrations → deine App
2. **Authentication** → **Add URI**:
   - `https://englisch.hellweg-realschule.de/.auth/login/aad/callback`
3. Save

### 5.3 SSL

Azure stellt automatisch ein kostenloses SSL-Zertifikat aus (Let's Encrypt). Funktioniert binnen Minuten nach Domain-Validierung.

---

## Phase 6 — KI-Tutor-Schutz (zusätzlich)

Da du den KI-Tutor schon über einen Cloudflare Worker zu Google Gemini routest:

### 6.1 Worker um Auth-Check erweitern

Im Worker-Code prüfen, ob der eingehende Request einen gültigen Microsoft-Token im Header `Authorization: Bearer <token>` hat:

```js
async function verifyMSToken(token) {
  // Token gegen Microsoft Entra validieren
  const res = await fetch('https://graph.microsoft.com/v1.0/me', {
    headers: { 'Authorization': `Bearer ${token}` }
  });
  if (!res.ok) return null;
  const user = await res.json();
  // Nur Schul-Domain erlauben
  if (!user.userPrincipalName?.endsWith('@hellweg-realschule.de')) return null;
  return user;
}

export default {
  async fetch(request, env) {
    const auth = request.headers.get('Authorization');
    if (!auth?.startsWith('Bearer ')) {
      return new Response('Unauthorized', { status: 401 });
    }
    const user = await verifyMSToken(auth.substring(7));
    if (!user) return new Response('Forbidden', { status: 403 });

    // Hier: Rate-Limit pro user.id prüfen, dann Gemini-API aufrufen
    // ... existierender Code ...
  }
};
```

### 6.2 Token im Frontend besorgen

Static Web Apps gibt dir den User-Token automatisch unter `/.auth/me`. In deinem KI-Tutor-Code:

```js
async function getMSToken() {
  const res = await fetch('/.auth/me');
  const data = await res.json();
  return data?.clientPrincipal?.idToken;
}

// Bei jedem KI-Tutor-Aufruf:
const token = await getMSToken();
fetch('https://dein-worker.workers.dev', {
  method: 'POST',
  headers: { 'Authorization': `Bearer ${token}`, 'Content-Type': 'application/json' },
  body: JSON.stringify({ prompt: ... })
});
```

### 6.3 Rate-Limit am Worker

Im Worker-Code per Cloudflare KV oder Durable Objects pro User-ID zählen, max. z.B. 50 Aufrufe/Tag.

---

## Wichtige Notes

### Free-Tier-Grenzen Azure Static Web Apps

- 100 GB Bandbreite/Monat
- 250 MB max App-Size
- 2 benutzerdefinierte Domains
- Bei 700 Schülern × 5 MB Page-Load × 10 Aufrufe/Monat = ~35 GB → reicht locker

### Backup

GitHub-Repo IST dein Backup. Lokale Änderungen committen + pushen, sonst verlierst du sie.

### Updates

Jeder `git push` auf `main` deployed automatisch (1–2 Min). Falls was kaputt geht: per `git revert` zurück.

### Schüler-Onboarding

- URL teilen (über Microsoft Teams oder klassische E-Mail)
- Beim ersten Aufruf einmal mit Schul-Konto anmelden
- Browser merkt sich Login (in der Regel)

---

## Troubleshooting

**„AADSTS50020"-Fehler beim Login:**
User hat ein Microsoft-Konto, aber nicht von eurem Tenant. Das ist gewollt — andere Schulen werden ausgesperrt.

**„AADSTS650056"-Fehler:**
Redirect-URI in Entra-App stimmt nicht mit der angerufenen URL überein. Schritt 3.1 / 5.2 prüfen.

**Static Web App zeigt 404 nach Push:**
Build-Workflow in `.github/workflows/` prüfen, ob `output_location` und `app_location` korrekt sind.

**KI-Tutor antwortet nicht trotz Login:**
Token-Header wird vermutlich nicht gesendet. Browser-DevTools → Network → KI-Anfrage → Request Headers prüfen. Workers-Log in Cloudflare-Dashboard checken.

---

## Nächste Schritte nach Setup

1. **Lehrkräfte-Hinweis** im Footer ergänzen: „Geschütztes Lernmaterial der Hellweg-Realschule. Vokabel-Listen orientiert am Lehrwerk Lighthouse (Cornelsen). Ausschließlich für interne Nutzung im Englischunterricht der Hellweg-Realschule."
2. **Tagesbudget-Cap** bei Google Gemini setzen (Google AI Studio → Settings → Quota)
3. **Klasse informieren:** in welchem Browser, mit welchem Konto, was tun bei Login-Problem (Schul-IT-Hotline)

---

*Stand: 28.04.2026. Bei Rückfragen während des Setups einfach durchklingeln.*
