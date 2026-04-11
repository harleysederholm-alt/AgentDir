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

---

## 📁 Kansiorakenne

```
agentdir/
├── watcher.py           ← Pääohjelma (käynnistä tämä)
├── verify_setup.py      ← Paikallinen tarkistus (Ollama + API)
├── server.py            ← A2A REST API + mDNS (valinnainen)
├── rag_memory.py        ← Semanttinen muisti (ChromaDB)
├── llm_client.py        ← LLM-asiakasohjelma + fallback
├── file_parser.py       ← PDF, CSV, TXT, MD, JSON
├── sandbox_executor.py  ← Turvallinen koodin suoritus
├── swarm_manager.py     ← Lapsi-agenttien hallinta
├── evolution_engine.py  ← Itseparannus + versiointi
├── config.json          ← Konfiguraatio (muokkaa tätä!)
├── manifest.json        ← Julkiset kyvyt (A2A)
├── requirements.txt
├── requirements-dev.txt
├── install.sh
├── install.ps1
├── run.sh
├── run.ps1
├── Dockerfile
├── docker-compose.yml
├── docker-stack.yml
├── LICENSE
├── CONTRIBUTING.md
├── SECURITY.md
│
├── Inbox/               ← PUDOTA TIEDOSTOT TÄNNE
├── Outbox/              ← Valmiit tulokset ilmestyvät tähän
├── memory/              ← RAG-vektori-DB (ei koske käsin)
├── swarm/               ← Lapsi-agentit (luodaan automaattisesti)
├── plugins/             ← Omat laajennukset (.gitkeep)
└── templates/           ← Valmiit roolikonfiguraatiot
    ├── researcher.json
    └── coder.json
```

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

Terveystarkistus osuu `GET http://127.0.0.1:8080/status` (A2A käynnissä `both`-tilassa).

---

## Tuotanto ja internet

- Älä julkaise `server.py`:n porttia suoraan internetiin ilman **TLS:ää**, **reverse proxya** (Caddy, Traefik, nginx) ja **todennusta**. Oletus-CORS (`*`) on tarkoitettu lähiverkon / kehityksen helppouteen.
- Sandbox on parannus, ei täyttä eristystä; katso [SECURITY.md](SECURITY.md) ja tunnetut rajoitukset alla.
- `server.py` lukee `config.json`:in käynnistyksessä: muutokset vaativat prosessin uudelleenkäynnistyksen, ellei tätä myöhemmin laajenneta.

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

---

## 🐛 Tunnetut rajoitukset (rehellisesti)

- **PDF**: Skannatut PDF:t (kuvapohjaiset) eivät toimi – tarvitaan OCR
- **Sandbox-turvallisuus**: Subprocess-eristys riittää useimpiin käyttöihin, mutta ei ole täysin tiivis. Tuotantokäytössä käytä Docker-konttia.
- **Evoluutio**: Vaatii vähintään 10 tehtävää ennen kuin se alkaa toimia
- **mDNS**: Ei toimi kaikkien VPN:ien tai Docker-verkkojen kanssa – käytä silloin suoria IP-osoitteita

---

## 🤝 Osallistu

Katso [CONTRIBUTING.md](CONTRIBUTING.md) (testit, PR-käytäntö, roadmap). Tietoturva-ilmoitukset: [SECURITY.md](SECURITY.md).

1. Fork → luo oma haara
2. Tee muutos + testit (`pytest tests/ -v`)
3. Pull Request – kaikki tervetulleita

Erityisesti tarvitaan:
- OCR-tuki skannautuille PDF:ille
- Tauri-UI (desktop dashboard)
- Lisää template-rooleja

---

## 📄 Lisenssi

MIT – täydellinen teksti: [LICENSE](LICENSE). Käytä vapaasti, myös kaupallisesti.
