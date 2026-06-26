## Prieš pradedant

Jums reikės:

- Kompiuterio su **Ubuntu 22.04** (serverio leidimas, minimalus diegimas) ir interneto ryšiu
- Viešo domeno vardo su DNS nukreipimu į serverio IP
- TAK kliento programėlės: **iTAK** (iOS), **ATAK** (Android) arba **WinTAK** (Windows)

**Minimalūs serverio reikalavimai:** 8 CPU branduoliai · 16 GB RAM · 60 GB disko vietos
**Rekomenduojama:** 8 CPU branduoliai · 32 GB RAM · 80 GB SSD

**Įtrauktos paslaugos:**

| Paslauga | Paskirtis |
|---|---|
| TAK serveris | Taktinė situacinė sąmonė (ATAK/iTAK/WinTAK) |
| Keycloak | Tapatybė ir SSO |
| Matrix / Synapse | Šifruotas komandos pokalbių kanalas |
| Battlelog | Tiesioginė vaizdo ir operacijų registracija |
| MediaMTX | RTMP / RTSP / WebRTC srautas |
| CryptPad | Galutinio šifravimo bendradarbiavimo dokumentai |
| CFSSL | Vidinė sertifikatų institucija |

---

## 1 žingsnis — DNS įrašai

Visi šie įrašai turi rodyti į jūsų serverio viešą IP prieš paleidžiant diegiklį. Let's Encrypt nepavyks, jei DNS dar neišplatintas.

```
jusudomenas.lt
kc.jusudomenas.lt
tak.jusudomenas.lt
bl.jusudomenas.lt
mtx.jusudomenas.lt
matrix.jusudomenas.lt
synapse.jusudomenas.lt
cryptpad.jusudomenas.lt
sandbox.cryptpad.jusudomenas.lt
rmcryptpad.jusudomenas.lt
mtls.jusudomenas.lt
mtls.kc.jusudomenas.lt
mtls.tak.jusudomenas.lt
mtls.bl.jusudomenas.lt
mtls.mtx.jusudomenas.lt
mtls.matrix.jusudomenas.lt
mtls.synapse.jusudomenas.lt
mtls.cryptpad.jusudomenas.lt
mtls.sandbox.cryptpad.jusudomenas.lt
mtls.rmcryptpad.jusudomenas.lt
```

> **Patarimas:** Cloudflare pakaitos įrašas `*.jusudomenas.lt → IP` ir `jusudomenas.lt → IP` apima viską.

---

## 2 žingsnis — Atidaryti ugniasienės prievadus

Šie prievadai turi būti pasiekiami iš interneto (arba bent jau iš komandos įrenginių):

| Prievadas | Protokolas | Paskirtis |
|---|---|---|
| 80 | TCP | Let's Encrypt HTTP iššūkis |
| 443 | TCP | HTTPS — prisijungimas ir mTLS pagrindinis puslapis |
| 4626 | TCP | Produktų API (TAK paketai, Battlelog, MediaMTX, CryptPad) |
| 4627 | TCP | ATAK automatinio importo laikinas atsisiuntimas |
| 8089 | TCP | TAK CoT (kliento jungtys) |
| 8443 | TCP | TAK HTTPS API |
| 8446 | TCP | TAK sertifikatu grįstas HTTPS |
| 9443 | TCP | Keycloak HTTPS administratoriaus sąsaja |
| 1936 | TCP | RTMPS |
| 8322 | TCP | RTSPS |
| 8890 | TCP/UDP | SRT |
| 9888 | TCP | HLS |
| 9889 | TCP | WebRTC |
| 9996 | TCP | Įrašų atkūrimas |

---

## 3 žingsnis — Paleisti diegiklį

Paleiskite diegiklį kaip root:

```bash
curl -fsSL https://raw.githubusercontent.com/ndukve/deploy/main/install.sh | bash
```

> Skriptas automatiškai klonuoja repozitoriją, jei ji dar nėra. Reikalingos root teisės — skriptas paleis save su `sudo`, jei reikia.

Diegiklis paklaus:
- **Domenas** — jūsų pagrindinis domenas (pvz. `pavyzdys.lt`)
- **Let's Encrypt el. paštas** — kontaktinis adresas sertifikatų galiojimo pranešimams
- **Let's Encrypt testavimo režimas** — `true` testavimui (bandomieji sertifikatai), `false` realiam naudojimui
- **CA pavadinimas** — vidinio sertifikatų centro pavadinimas

Visi slaptažodžiai ir paslapčių raktai generuojami automatiškai ir išsaugomi `.env` faile.

> **Pirmasis paleidimas trunka 5–10 minučių.** Vien TAK serveris paleidžia 5 Java procesus. Keycloak pirmojo paleidimo metu inicializuoja savo sritį. Diegiklis laukia, kol sistema taps sveika, ir tik tada atspausdina administratoriaus kodą.

---

## 4 žingsnis — Pirmasis administratoriaus prisijungimas

Baigus diegimą, diegiklis atspausdina vienkartinį administratoriaus pakvietimo kodą:

```
First admin code: XXXXXXXXXXXXXXXX
```

1. Naršyklėje atidarykite `https://jusudomenas.lt`
2. Įveskite pakvietimo kodą ir pasirinkite administratoriaus šaukinį
3. Dabar esate pirmasis administratorius

> Jei praleidote kodą, sugeneruokite iš naujo:
> ```bash
> docker compose exec rmapi rasenmaeher_api addcode
> ```

---

## 5 žingsnis — Pridėti vartotojus

Deploy App pagrindiniame puslapyje (`https://mtls.jusudomenas.lt`):

1. **Manage Users → Add Users → Create New Invite**
2. Pasidalinkite pakvietimo nuoroda arba QR kodu su komanda
3. Vartotojai registruojasi pasirinkdami šaukinį
4. **Approve Users** → pasirinkite laukiantį vartotoją → patvirtinkite

Patvirtinti vartotojai automatiškai gauna abipusio TLS kliento sertifikatą ir prieigą prie visų integruotų paslaugų (TAK, Matrix, Battlelog, CryptPad, MediaMTX).

---

## 6 žingsnis — Prijungti TAK klientus

1. Prisijunkite prie `https://mtls.jusudomenas.lt`
2. Pasirinkite **TAK**
3. Pasirinkite platformą: **Android ATAK**, **iOS iTAK** arba **Windows WinTAK**
4. Spustelėkite **Download Client Package**
5. Importuokite `.zip` į TAK klientą naudodami Import Manager

**iTAK (iOS)**
Settings → Network → Servers → **+** → Upload Server Package → pasirinkite `.zip`

**ATAK (Android)**
Hamburger meniu → Settings → Network Preferences → TAK Servers → **+** → Import from file → pasirinkite `.zip`

**WinTAK (Windows)**
Hamburger meniu → **Import Manager** → Import → pasirinkite `.zip`

---

## Administratoriaus sąsajos

| Sąsaja | URL |
|---|---|
| Deploy App prisijungimas | `https://jusudomenas.lt` |
| Deploy App pagrindinis (mTLS) | `https://mtls.jusudomenas.lt` |
| Keycloak administravimas | `https://kc.jusudomenas.lt:9443/admin/RASENMAEHER/console/` |
| TAK administravimas | `https://tak.jusudomenas.lt:8443/` |

---

## Eksploatacija

```bash
# Peržiūrėti visus žurnalus
docker compose logs -f

# Peržiūrėti konkrečios paslaugos žurnalus
docker compose logs -f rmapi
docker compose logs -f takconfig

# Paleisti paslaugą iš naujo
docker compose restart rmapi

# Atsisiųsti naujausius atvaizdus ir paleisti iš naujo
./update.sh

# Būsena
docker compose ps
```

> **ĮSPĖJIMAS:** Niekada nevykdykite `docker compose down -v` — tai ištrina visus sertifikatus, vartotojų duomenis ir TAK duomenų bazę. Vartotojus reikės registruoti iš naujo.

---

## Dažnos problemos

> **Let's Encrypt nepavyksta**
> DNS įrašai dar neišplatinti. Palaukite kelias minutes ir paleiskite diegiklį iš naujo, arba nustatykite `MW_LE_TEST=true` faile `.env` ir paleiskite: `docker compose up -d miniwerk`.

> **TAK klientai negali prisijungti**
> Prievadas 8089 neuždarytas, arba kliento paketas buvo sugeneruotas prieš serverio visišką pasirengimą. Atsisiųskite kliento paketą iš naujo per Deploy App sąsają.

> **Keycloak arba rmapi nesipalaeidžia**
> Pirmojo paleidimo metu Keycloak inicializuoja RASENMAEHER sritį, tai trunka 2–3 minutes. Patikrinkite: `docker compose logs -f keycloak`. Jei cikliškai kartojasi, paleiskite: `docker compose restart keycloak`.

> **OpenLDAP arba keycloak-init nepavyksta pirmojo paleidimo metu**
> Tai žinoma lenktynių sąlyga. Paleiskite `docker compose up -d` dar kartą — sistema tęsia nuo ten, kur sustojo.
