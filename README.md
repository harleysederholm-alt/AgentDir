# 🧬 AgentDir – Elävä tiedostojärjestelmä

[![CI](https://github.com/YOUR_GITHUB_USER/agentdir/actions/workflows/ci.yml/badge.svg)](https://github.com/YOUR_GITHUB_USER/agentdir/actions/workflows/ci.yml)

**Jokainen kansio on itsenäinen, oppiva tekoälyagentti.**

Pudota tiedosto `Inbox/`-kansioon → agentti herää, lukee sen, käyttää semanttista muistiaan, suorittaa tarvittavan koodin turvallisessa sandboxissa, oppii virheistään ja jättää valmiin tuloksen `Outbox/`-kansioon.

```
100 % lokaali  •  Yksityinen  •  MIT-lisenssi  •  Ei API-kuluja
```

**Git-repon juuri:** tämä hakemisto (`watcher.py` juuressa) on tarkoitettu GitHub-repositorion juureksi. Kun luot repon, korvaa alla olevissa URL- ja badge-linkeissä `YOUR_GITHUB_USER` omalla käyttäjälläsi tai organisaatiollasi.

**Paikallinen Git:** tässä kansiossa voi olla jo `git init` ja ensimmäinen commit (ilman `remote` / pushia). Kun haluat GitHubiin: luo tyhjä repo palvelussa, `git remote add origin …`, `git push -u origin main`.

---

## ✨ Mitä tämä tekee oikeasti

| Ominaisuus | Kuvaus |
|---|---|
| **Watcher** | Reagoi tiedoston ilmestymiseen alle sekunnissa (watchdog + debounce) |
| **RAG-muisti** | Semanttinen haku kaikesta aiemmasta – agentti muistaa aiemmat tehtävänsä |
| **Sandbox** | Generoitu Python-koodi ajetaan eristetyssä prosessissa + turvallisuustarkistus |
| **Itsekorjaus** | Jos koodi kaatuu, agentti lukee virheen ja korjaa itsensä (max 3 yritystä) |
| **Swarm** | Monimutkaiset tehtävät hajautetaan lapsi-agenttikansioihin (*swarm/*-hakemistoon, ei Inbox:iin) |
| **A2A-protokolla** | REST API + mDNS – agentit löytävät toisensa lokaaliverkosta |
| **Evoluutio** | Mittaa onnistumisprosenttia ja pyytää LLM:ltä paremman promptin jos laatu heikkenee |

---

## 🚀 Nopea aloitus

```bash
# 1. Kloonaa (korvaa YOUR_GITHUB_USER)
git clone https://github.com/YOUR_GITHUB_USER/agentdir.git
cd agentdir

# 2. Asenna (luo venv + lataa Ollama-mallit automaattisesti)
chmod +x install.sh && ./install.sh

# 3. Käynnistä
source .venv/bin/activate
python watcher.py

# 4. Testaa – pudota mikä tahansa tiedosto Inboxiin
echo "Analysoi seuraava data ja tee yhteenveto: tekoäly kasvaa 40% vuodessa." > Inbox/testi.txt
# → Tulos ilmestyy Outbox/-kansioon muutamassa sekunnissa
```

**Windows (PowerShell):** `Set-ExecutionPolicy -Scope Process Bypass; .\install.ps1` — aktivoi sitten `.\\.venv\\Scripts\\Activate.ps1` ja `python watcher.py`.

### Vaatimukset
- Python 3.10+
- [Ollama](https://ollama.com) (tai muu OpenAI-yhteensopiva lokaali serveri)
- Mallit (oletus `config.json`): päämalli **`gemma4:e4b`**, embedding **`mxbai-embed-large`**, fallback-embedding **`nomic-embed-text`**. Asenna: `ollama pull gemma4:e4b && ollama pull mxbai-embed-large && ollama pull nomic-embed-text`

### Kun ympäristö on jo asennettu

Jos `.venv`-kansiota ei ole, aja ensin `.\install.ps1` (Windows) tai `./install.sh` (Linux/macOS).

0. (Valinnainen) Tarkista mallit ja API: `python verify_setup.py`

1. Varmista että **Ollama** pyörii (`ollama serve` tai Ollama-sovellus taustalla).
2. Projektikansiossa: aktivoi virtuaaliympäristö ja käynnistä watcher.

```powershell
cd agentdir
.\.venv\Scripts\Activate.ps1
python watcher.py
```

(Linux/macOS: `source .venv/bin/activate` ennen `python watcher.py`.)

**Pikakäynnistys:** `.\run.ps1` (Windows) tai `./run.sh` (Linux/macOS; ensin kerran `chmod +x run.sh`). Skripti käyttää `.venv`-Pythonia suoraan.

**Windows – kaikki kerralla:** `Set-ExecutionPolicy -Scope Process Bypass; .\start-all.ps1` käynnistää tarvittaessa asennuksen, `verify_setup.py`:n, watcherin ja serverin (kaksi konsoli-ikkunaa), avaa selaimen Web-UI:hin (ohita: `-NoBrowser`). Parametrit: `-SkipVerify`, `-SkipOllamaCheck`, `-WatcherOnly`, `-ServerOnly`, `-Force`, `-NoBrowser`.

### Asennus pip-pakettina (valinnainen)

Projektihakemistossa:

```bash
pip install -e .
# Valinnaiset komennot (kun venv aktiivinen ja PATH päivittynyt):
agentdir-watcher
agentdir-server
```

OCR-riippuvuudet erikseen: `pip install -e ".[ocr]"` tai `pip install -r requirements-ocr.txt`.

### Tauri-työpöytä (valinnainen)

Katso [desktop/README.md](desktop/README.md). Käynnistä ensin `python server.py`, sitten `desktop/`-hakemistossa `npm install` ja `npm run tauri dev`.

---

## 📁 Kansiorakenne

```
agentdir/
├── watcher.py           ← Pääohjelma (käynnistä tämä)
├── verify_setup.py      ← Paikallinen tarkistus (Ollama + API)
├── server.py            ← A2A REST API + mDNS + Web-UI (valinnainen)
├── ui_routes.py         ← Dashboard (Jinja2)
├── web/                 ← UI-mallit ja CSS (templates, static)
├── rag_memory.py        ← Semanttinen muisti (ChromaDB)
├── llm_client.py        ← LLM-asiakasohjelma + fallback + async ``process_task``
├── agent_core.py        ← Manifest-rooli, Outbox-polku, Inbox → Workspace/archive
├── evolution_log.py     ← JSONL-loki onnistuneista ajoista (``evolution.log``)
├── file_parser.py       ← PDF, CSV, TXT, MD, JSON
├── sandbox_executor.py  ← Turvallinen koodin suoritus
├── swarm_manager.py     ← Lapsi-agenttien hallinta
├── evolution_engine.py  ← Itseparannus + versiointi
├── config.json          ← Konfiguraatio (muokkaa tätä!)
├── manifest.json        ← Julkiset kyvyt (A2A)
├── requirements.txt
├── requirements-ocr.txt
├── requirements-dev.txt
├── pyproject.toml
├── desktop/             ← Tauri-työpöytä (npm + Rust)
├── install.sh
├── install.ps1
├── run.sh
├── run.ps1
├── start-all.ps1
├── Dockerfile
├── docker-compose.yml
├── docker-compose.secure.yml   ← valinnainen overlay + .env.secure
├── docker-stack.yml
├── LICENSE
├── CONTRIBUTING.md
├── SECURITY.md
│
├── Inbox/               ← PUDOTA TIEDOSTOT TÄNNE
├── Outbox/              ← Valmiit tulokset: ``vastaus_<tehtävä>.md`` (The Spark)
├── Workspace/archive/   ← Käsitellyt Inbox-varaukset (``*.processing.*``) arkistoidaan tänne
├── evolution.log        ← JSONL: timestamp, tehtävän koko, malli, status (onnistuneet ajot)
├── memory/              ← RAG-vektori-DB (ei koske käsin)
├── swarm/               ← Lapsi-agentit (luodaan automaattisesti)
├── plugins/             ← Python-laajennukset (hooks, katso plugins/README.md)
└── templates/           ← Valmiit roolikonfiguraatiot
    ├── researcher.json
    ├── coder.json
    ├── translator.json
    └── support.json
```

### The Spark (hermosto → loki)

- **Vaihe 1:** Uusi Inbox-tiedosto varataan nimellä ``{nimi}.processing.{pääte}``; lokirivi *Uusi tehtävä havaittu: …*.
- **Vaihe 2:** ``LLMClient.process_task(prompt, role)`` kutsuu OpenAI-yhteensopivaa API:a **asynkronisesti** (``httpx``); rooli tulee ``manifest.json``:sta tai ``config.json``:sta.
- **Vaihe 3:** Vastaus tallennetaan ``Outbox/vastaus_<alkuperäinen_tiedostonimi>.md``; onnistuneen käsittelyn jälkeen varaustiedosto siirtyy ``Workspace/archive/`` (ei pelkkää poistoa). Epäonnistuessa ``.processing``-tiedosto jää Inboxiin.
- **Vaihe 4:** Onnistuneista ajoista kirjoitetaan juureen **JSONL**-tiedosto ``evolution.log`` (kentät: ``timestamp``, ``task_size_bytes``, ``model``, ``source_file``, ``outbox_file``, ``status``).

---

## ⚙️ Konfiguraatio

Muokkaa `config.json`:

```json
{
  "name": "MinunAgentti",
  "role": "Talousanalyytikko",
  "llm": {
    "model": "llama3.2:3b",
    "endpoint": "http://localhost:11434/v1/chat/completions"
  }
}
```

**Valmiit roolit** (`templates/`-kansiossa):
- `researcher.json` – Tieteellinen tutkija
- `coder.json` – Python-kehittäjä / data scientist
- `translator.json` – Käännökset ja rekisteri
- `support.json` – Käyttäjätuki / vianetsintä

Käyttö: Kopioi templatesta haluamasi kentät `config.json`:iin.

---

## 🐳 Docker

```bash
# Yksittäinen agentti
docker build -t agentdir .
docker run -v $(pwd):/agentdir -p 8080:8080 agentdir both

# Koko Swarm (useita agenteja eri rooleilla)
docker swarm init
docker stack deploy -c docker-stack.yml agentdir
```

### Docker Compose (nopea demo)

Käynnistää watcherin ja A2A-palvelimen (`both`). Data säilyy Docker-volumessa `agentdir_data`.

```bash
docker compose up --build
```

**Ollama isäntäkoneella (Linux / WSL / Docker Desktop):** kontti käyttää `extra_hosts: host.docker.internal`. Muokkaa kontissa käytettävää `config.json`:ia (esim. kopioi ulos volumesta tai muokkaa ennen ensimmäistä ajoa) niin että:

- `llm.endpoint` → `http://host.docker.internal:11434/v1/chat/completions`
- `embedding.endpoint` → `http://host.docker.internal:11434/api/embed`

macOS ja Windows Docker Desktopissa `host.docker.internal` toimii yleensä suoraan. Linuxilla tarvitaan Compose 2.x `host-gateway` (mukana tässä `docker-compose.yml`:ssä).

**Compose + salaisuudet (esimerkki):** kopioi `.env.secure.example` → `.env.secure`, täytä arvot ja käynnistä:

```bash
docker compose -f docker-compose.yml -f docker-compose.secure.yml up --build
```

**Tuotanto-checklist (Compose + salaisuudet):**

1. `.env.secure` täytetty (`AGENTDIR_UI_SECRET`, `AGENTDIR_API_SECRET`, `AGENTDIR_SESSION_SECRET` — katso [.env.secure.example](.env.secure.example)).
2. Volumen [`config.json`](config.json) (tai bind-mount): `a2a.cors_origins` **ei** saa olla `["*"]` jos API:ta käytetään selaimesta internetin yli; käytä esim. `["https://oma-sovellus.example"]`.
3. Sama `config.json`: tyhjä `a2a.api_token` + asetettu **`AGENTDIR_API_SECRET`** (tai `api_token` vain luotetussa verkossa) → `POST /task` ja `POST /rag/query` vaativat API-avaimen.
4. Ulkoinen TLS ja reverse proxy välittävät liikenteen konttiin; Web-UI:n `Secure`-eväste: aseta **`AGENTDIR_UI_COOKIE_SECURE=1`** tai `ui.cookie_secure: true` kun käyttäjät käyttävät **https://**-osoitetta (muuten istuntoeväste ei tallennu selaimessa).
5. **Tauri-työpöytä:** jos käytät **`AGENTDIR_UI_SECRET`**, varmista että WebViewin URL on sama **origin** kuin AgentDir-palvelin (portti ja `http`/`https` vastaavat [`desktop/README.md`](desktop/README.md) / `tauri.conf.json`), jotta istuntoeväste (`agentdir_session`) säilyy kirjautumisen jälkeen.

`GET /status` on tarkoituksella kevyt terveys-/valmiustarkistus ilman API-avainta (Docker `healthcheck`). Kun **API-token** on käytössä, **`a2a.cors_origins` ei voi olla `*`** — palvelin poistaa CORS-otsikot kunnes lista on eksplisiittinen. Älä lisää `/status`-reittiin salasanasuojausta ilman että päivität healthcheckin vastaamaan.

---

## Tuotanto ja internet

- Älä julkaise `server.py`:n porttia suoraan internetiin ilman **TLS:ää**, **reverse proxya** (Caddy, Traefik, nginx) ja **todennusta**.
- **`a2a.cors_origins`**: lista sallituista `Origin`-arvoista (esim. `["https://app.example.com"]`). Oletus `["*"]` on vain kehitykseen / luotettuun lähiverkkoon **ilman** API-tokenia; jos **`AGENTDIR_API_SECRET`** tai **`a2a.api_token`** on asetettu, `*` ei kelpaa — määritä eksplisiittiset originat. CORS luetaan `config.json`:sta ja päivittyy ilman uudelleenkäynnistystä.
- **`a2a.api_token`** (tyhjä = ei vaadi) tai ympäristömuuttuja **`AGENTDIR_API_SECRET`**: kun asetettu, `POST /task` ja `POST /rag/query` vaativat otsikon `X-AgentDir-Api-Key` tai `Authorization: Bearer <token>`.
- **Web-UI**: ilman `AGENTDIR_UI_SECRET` dashboard päivittää Inbox/Outbox-listoja noin 5 s välein (HTMX). Kun `AGENTDIR_UI_SECRET` on asetettu, selain ohjataan **`/ui/login`**-sivulle; kirjautuminen asettaa istuntoevästeen (`agentdir_session`), jolloin HTMX-osiot toimivat ilman `X-AgentDir-Key`-otsikkoa (vanhentuneessa istunnossa HTMX saa `HX-Redirect` → kirjautuminen). Vaihtoehtoisesti voit edelleen käyttää otsikkoa tai lomakkeen `agentdir_key`-kenttää. Tuotantoon: **`AGENTDIR_SESSION_SECRET`** (vähintään 16 merkkiä) erikseen UI-salasanasta, tai `config.json` → `ui.session_secret` (pitkä merkkijono); ilman niitä istunto allekirjoitetaan kehitystasolla johdetulla avaimella. **HTTPS + `Secure`-eväste:** `AGENTDIR_UI_COOKIE_SECURE=1` tai `ui.cookie_secure: true` (proxy TLS:n takana).
- Sandbox on parannus, ei täyttä eristystä; katso [SECURITY.md](SECURITY.md) ja tunnetut rajoitukset alla.
- `server.py` käyttää `config_manager.py`:n hot-reloadia: useimmat `config.json`-muutokset näkyvät API:ssa ja Web-UI:ssa ilman uudelleenkäynnistystä (noin 3 s viive). **Kuunneltava portti** (`a2a.port`) luetaan käynnistyksessä — portin vaihto vaatii palvelimen uudelleenkäynnistyksen.

### Reverse proxy (lyhyt esimerkki)

**Caddy** (automaattinen TLS, Let's Encrypt):

```txt
agentti.example.com {
  reverse_proxy 127.0.0.1:8080
}
```

**nginx** (TLS terminoituu proxylle):

```nginx
location / {
  proxy_pass http://127.0.0.1:8080;
  proxy_set_header Host $host;
  proxy_set_header X-Real-IP $remote_addr;
  proxy_set_header X-Forwarded-Proto $scheme;
}
```

Jos käytät Web-UI:ta HTTPS:n kautta, aseta AgentDirissa **`AGENTDIR_UI_COOKIE_SECURE=1`** (tai `ui.cookie_secure` vastaavasti), jotta `agentdir_session` saa `Secure`-lipun.

---

## 🌐 A2A-protokolla

```bash
# Käynnistä A2A-serveri
python server.py

# Tarkista tila
curl http://localhost:8080/status

# Etsi muut agentit lokaaliverkosta
curl http://localhost:8080/discover

# Lähetä tehtävä toiselle agentille
curl -X POST http://TOISEN_AGENTIN_IP:8080/task \
  -H "Content-Type: application/json" \
  -d '{"task": "Analysoi tämä data...", "from": "MinunAgentti"}'
```

### Web-UI (selain)

Kun **A2A-palvelin** on käynnissä (`python server.py` tai Docker `both`), avaa selaimessa:

- **http://127.0.0.1:8080/** → uudelleenohjaus dashboardille  
- **http://127.0.0.1:8080/ui/** → Inbox- ja Outbox-listat (automaattipäivitys HTMX:llä ilman UI-salasanaa), RAG-/evoluutiotilanne, linkit **OpenAPI `/docs`** ja **ReDoc**  
- Tiedostonäkymä: klikkaa listan tiedostonimeä (vain `Inbox/` ja `Outbox/`, ei polkupakoja).

**Valinnainen suojaus:** aseta `AGENTDIR_UI_SECRET` (esim. satunnainen merkkijono). Silloin HTML-pyynnöt ohjataan **`/ui/login`**-sivulle (tai voit lähettää otsikon `X-AgentDir-Key`). Lomakkeet (`POST /ui/submit`) hyväksyvät myös kentän `agentdir_key`. Istuntoevästeen allekirjoitukseen käytetään **`AGENTDIR_SESSION_SECRET`** (≥16 merkkiä), tai SHA256-avainta UI-salasanasta, tai valinnaista `config.json` → **`ui.session_secret`**. Ilman UI-salasanaa dashboard on avoin kaikille, joilla on pääsy porttiin — älä jätä näin tuotantoon.

---

## 🐛 Tunnetut rajoitukset (rehellisesti)

- **PDF / OCR**: Skannatut PDF:t vaativat `config.json` → `pdf.ocr_enabled: true` sekä `pip install -r requirements-ocr.txt` (tai `pip install -e ".[ocr]"`) ja järjestelmään **Tesseract** + **Poppler** (Windows: asenna ja lisää `PATH`; katso `requirements-ocr.txt`).
- **Sandbox-turvallisuus**: Subprocess-eristys riittää useimpiin käyttöihin, mutta ei ole täysin tiivis. Tuotantokäytössä käytä Docker-konttia.
- **Evoluutio**: Vaatii vähintään 10 tehtävää ennen kuin se alkaa toimia
- **mDNS**: Ei toimi kaikkien VPN:ien tai Docker-verkkojen kanssa – käytä silloin suoria IP-osoitteita

---

## Projektin laajuus (yhteenveto)

| Osio | Tila |
|------|------|
| Watcher, Inbox/Outbox, tiedostoparseri | Valmis |
| LLM (Ollama), RAG (ChromaDB), sandbox | Valmis |
| Swarm-lapset `swarm/`-kansiossa | Valmis (lapselle kopioidaan `swarm_manager.py` + `manifest.json`) |
| A2A REST (`server.py`), mDNS | Valmis |
| Web-UI `/ui/`, OpenAPI `/docs` | Valmis |
| Docker / Compose, GitHub Actions CI | Valmis |
| `verify_setup.py`, `start-all.ps1`, `install.ps1/.sh` | Valmis |
| OCR skannatuille PDF:ille | Valmis (`pdf.ocr_enabled` + `requirements-ocr.txt`) |
| `server.py` + Web-UI: config hot-reload | Valmis (portti vain käynnistyksessä) |
| Tauri-työpöytä | Valmis (`desktop/`, katso `desktop/README.md`) |
| `pip install -e .` | Valmis (`pyproject.toml`, komennot `agentdir-watcher` / `agentdir-server`) |
| CORS + A2A API-token (`a2a.cors_origins`, `api_token` / `AGENTDIR_API_SECRET`) | Valmis |
| Web-UI HTMX + istuntokirjautuminen `/ui/login` (`AGENTDIR_SESSION_SECRET` / `ui.session_secret`) | Valmis |
| Plugin-hookit (`hooks.py`, `plugins/*.py`) | Valmis |

---

## 🤝 Osallistu

Katso [CONTRIBUTING.md](CONTRIBUTING.md) (testit, PR-käytäntö, roadmap). Tietoturva-ilmoitukset: [SECURITY.md](SECURITY.md).

1. Fork → luo oma haara
2. Tee muutos + testit (`pytest tests/ -v`)
3. Pull Request – kaikki tervetulleita

Erityisesti tarvitaan:
- Lisää template-rooleja; tuotanto-auth (CORS-lista, `api_token` / `AGENTDIR_API_SECRET`, proxy + TLS) on dokumentoitu yllä

---

## 📄 Lisenssi

MIT – täydellinen teksti: [LICENSE](LICENSE). Käytä vapaasti, myös kaupallisesti.
