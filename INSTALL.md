## Before You Start

You will need:

- A machine running **Ubuntu 22.04** (server edition, minimal install) with internet access
- A public domain name with DNS pointing to the server's IP
- A TAK client: **iTAK** (iOS), **ATAK** (Android), or **WinTAK** (Windows)

**Minimum server specs:** 8 CPU cores · 16 GB RAM · 60 GB disk
**Recommended:** 8 CPU cores · 32 GB RAM · 80 GB SSD

**Services included:**

| Service | Purpose |
|---|---|
| TAK Server | Tactical situational awareness (ATAK/iTAK/WinTAK) |
| Keycloak | Identity and SSO |
| Matrix / Synapse | Encrypted team chat |
| Battlelog | Live video and operations logging |
| MediaMTX | RTMP / RTSP / WebRTC streaming |
| CryptPad | End-to-end encrypted collaborative documents |
| CFSSL | Internal certificate authority |

---

## Step 1 — DNS Records

All of the following must point to your server's public IP before you run the installer. Let's Encrypt will fail if DNS is not resolved.

```
yourdomain.com
kc.yourdomain.com
tak.yourdomain.com
bl.yourdomain.com
mtx.yourdomain.com
matrix.yourdomain.com
synapse.yourdomain.com
cryptpad.yourdomain.com
sandbox.cryptpad.yourdomain.com
rmcryptpad.yourdomain.com
mtls.yourdomain.com
mtls.kc.yourdomain.com
mtls.tak.yourdomain.com
mtls.bl.yourdomain.com
mtls.mtx.yourdomain.com
mtls.matrix.yourdomain.com
mtls.synapse.yourdomain.com
mtls.cryptpad.yourdomain.com
mtls.sandbox.cryptpad.yourdomain.com
mtls.rmcryptpad.yourdomain.com
```

> **Tip:** A Cloudflare wildcard record `*.yourdomain.com → IP` plus `yourdomain.com → IP` covers all of the above.

---

## Step 2 — Open Firewall Ports

The following ports must be reachable from the internet (or at minimum from your team's devices):

| Port | Protocol | Purpose |
|---|---|---|
| 80 | TCP | Let's Encrypt HTTP challenge |
| 443 | TCP | HTTPS — login and mTLS home |
| 4626 | TCP | Product APIs (TAK packages, Battlelog, MediaMTX, CryptPad) |
| 4627 | TCP | ATAK auto-import ephemeral download |
| 8089 | TCP | TAK CoT (client connections) |
| 8443 | TCP | TAK HTTPS API |
| 8446 | TCP | TAK cert-based HTTPS |
| 9443 | TCP | Keycloak HTTPS admin |
| 1936 | TCP | RTMPS |
| 8322 | TCP | RTSPS |
| 8890 | TCP/UDP | SRT |
| 9888 | TCP | HLS |
| 9889 | TCP | WebRTC |
| 9996 | TCP | Playback |

---

## Step 3 — Run the Installer

Clone the repository and run the installer as root:

```bash
git clone https://github.com/ndukve/deploy.git
cd deploy
sudo ./install.sh
```

The installer will prompt for:
- **Domain** — your base domain (e.g. `example.com`)
- **Let's Encrypt email** — contact address for cert expiry notices
- **Let's Encrypt test mode** — use `true` for staging certs while testing, `false` for real certs
- **CA name** — name for the internal certificate authority

All passwords and secrets are generated automatically and saved to `.env`.

> **First boot takes 5–10 minutes.** TAK Server alone starts 5 Java processes. Keycloak initialises its realm on first run. The installer waits for the stack to be healthy before printing the admin code.

---

## Step 4 — First Admin Login

When the installer finishes it prints a one-time admin invite code:

```
First admin code: XXXXXXXXXXXXXXXX
```

1. Open `https://yourdomain.com` in a browser
2. Enter the invite code and choose your admin callsign
3. You are now the first admin

> If you miss the code, regenerate it:
> ```bash
> docker compose exec rmapi rasenmaeher_api addcode
> ```

---

## Step 5 — Add Users

From the Deploy App home page (`https://mtls.yourdomain.com`):

1. **Manage Users → Add Users → Create New Invite**
2. Share the invite link or QR code with your team
3. Users register with a callsign
4. **Approve Users** → select waiting user → approve

Approved users automatically receive a mutual TLS client certificate and access to all integrated services (TAK, Matrix, Battlelog, CryptPad, MediaMTX).

---

## Step 6 — Connect TAK Clients

1. Log in at `https://mtls.yourdomain.com`
2. Select **TAK**
3. Choose your platform: **Android ATAK**, **iOS iTAK**, or **Windows WinTAK**
4. Click **Download Client Package**
5. Import the `.zip` into your TAK client using Import Manager

**iTAK (iOS)**
Settings → Network → Servers → **+** → Upload Server Package → select the `.zip`

**ATAK (Android)**
Hamburger menu → Settings → Network Preferences → TAK Servers → **+** → Import from file → select the `.zip`

**WinTAK (Windows)**
Hamburger menu → **Import Manager** → Import → select the `.zip`

---

## Admin Interfaces

| Interface | URL |
|---|---|
| Deploy App login | `https://yourdomain.com` |
| Deploy App home (mTLS) | `https://mtls.yourdomain.com` |
| Keycloak admin | `https://kc.yourdomain.com:9443/admin/RASENMAEHER/console/` |
| TAK admin | `https://tak.yourdomain.com:8443/` |

---

## Operations

```bash
# View all logs
docker compose logs -f

# View logs for a specific service
docker compose logs -f rmapi
docker compose logs -f takconfig

# Restart a service
docker compose restart rmapi

# Pull latest images and restart
./update.sh

# Status
docker compose ps
```

> **WARNING:** Never run `docker compose down -v` — this deletes all certificates, user data, and the TAK database. Users will need to be re-onboarded from scratch.

---

## Troubleshooting

> **Let's Encrypt fails**
> DNS records are not propagated yet. Wait a few minutes and re-run the installer, or set `MW_LE_TEST=true` in `.env` and restart: `docker compose up -d miniwerk`.

> **TAK clients cannot connect**
> Port 8089 is not open, or the client package was generated before the server was fully healthy. Re-download the client package from the Deploy App UI.

> **Keycloak or rmapi not starting**
> On first boot Keycloak initialises the RASENMAEHER realm which takes 2–3 minutes. Check with `docker compose logs -f keycloak`. If it loops, run `docker compose restart keycloak`.

> **OpenLDAP or keycloak-init fails on first start**
> This is a known race condition. Run `docker compose up -d` again — it picks up where it left off.
