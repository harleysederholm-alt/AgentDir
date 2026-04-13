<div align="center">
  <img src="docs/agentdir_logo_v3.png" alt="AgentDir Sovereign Engine Logo" width="500"/>

  <h1>🧬 AgentDir Sovereign Engine 4.0 (Edge Architecture)</h1>

  <p><strong>Maailmanluokan 100% lokaali asynkroninen tekoäly-ekosysteemi.</strong><br>
  Tuo autonomiset tekoälyagentit suoraan tiedostojärjestelmään ja ohjaa laskenta lennosta kytkettäviin Edge-laitteisiin.</p>

  <h3>👉 <a href="QUICKSTART.md">Pika-aloitus (3 min)</a> 👈</h3>

  <p>
    <a href="https://github.com/harleysederholm-alt/AgentDir/actions/workflows/ci.yml"><img src="https://github.com/harleysederholm-alt/AgentDir/actions/workflows/ci.yml/badge.svg" alt="CI Status"></a>
    <img src="https://img.shields.io/badge/License-MIT-blue.svg" alt="License: MIT">
    <img src="https://img.shields.io/badge/Release-v4.0%20Stable-gold" alt="Version">
    <img src="https://img.shields.io/badge/AI_Engine-Gemma_4-purple" alt="Gemma4">
    <img src="https://img.shields.io/badge/Edge_Compute-E2B%20%2F%20E4B-orange" alt="Edge">
    <img src="https://img.shields.io/badge/Security-Win_Sandbox-red" alt="Sandbox">
  </p>
</div>

---

## 🚀 Vision: AI-Native Distributed Ecosystem

**Jokainen kansio on itsenäinen, oppiva tekoälyagentti – ja jokainen laite on laskentasolmu.**

AgentDir Sovereign Engine 4.0 on täydellinen asynkroninen tekoäly-ohjelmistoarkkitehtuuri. Se muuttaa paikallisen hakemistosi älykkääksi reaktoriksi: Pudota tiedosto `Inbox/`-kansioon → Agentti herää lennosta, tutkii (Hermes), analysoi (OpenClaw), suorittaa koodin turvallisessa hiekkalaatikossa (Win Sandbox) ja palauttaa validoidun raportin. Yksikään tavu ei poistu lokaalista ympäristöstäsi.

### 📱 Uutta v4.0:ssa: Zero-Install OmniNode & Gemma 4 Edge
Sovereign Enginen kenties maagisin ominaisuus on tuki saumattomalle **Gemma 4 Edge (E2B/E4B)** verkotukselle.
- **Zero-Install WebAssembly**: Skannaa pääkoneelta QR-koodi älypuhelimesi selaimessa, ja puhelin muuttuu osaksi päättelyverkkoa (WASM).
- **USB-Tethering & mDNS**: Kytke vanha älypuhelin tai Raspberry Pi USB-kaapelilla kiinni isäntäkoneeseen. Isäntäkone offloadaa raskaat OpenClaw-analyysit välittömästi eristettyyn Edge-laitteen omaan llama.cpp / Gemma 4 E4B -piiriin. Lue lisää: [USB_COMPUTING.md](docs/USB_COMPUTING.md).

---

## 🧠 Sovereign Architecture

```mermaid
graph TD
    classDef ui fill:#1F2937,stroke:#60A5FA,stroke-width:2px,color:#fff
    classDef core fill:#312E81,stroke:#8B5CF6,stroke-width:2px,color:#fff
    classDef mem fill:#064E3B,stroke:#10B981,stroke-width:2px,color:#fff
    classDef exe fill:#7F1D1D,stroke:#EF4444,stroke-width:2px,color:#fff
    classDef net fill:#4C1D95,stroke:#A78BFA,stroke-width:2px,color:#fff

    subgraph UI["Käyttöliittymä & Etähallinta"]
        T[Sovereign Dashboard UI]:::ui
        CLI[Sovereign CLI REPL]:::ui
        Mobile[Mobile WASM Remote]:::ui
    end

    subgraph COGNET["Kognitio & LLM Root"]
        Hermes[Hermes Research]:::mem
        OC[OpenClaw Deep Analysis]:::mem
        LLM[Gemma 4 LLM Core]:::mem
        RAG[(ChromaDB RAG)]:::mem
    end

    subgraph EXEC["Turvallisuus & Ajo"]
        AST[AST Guardian]:::exe
        WSBOX[Windows Sandbox]:::exe
    end

    subgraph NETWORK["Edge Compute (OmniNode)"]
        OMNI_WS[WASM Nodes via WebSocket]:::net
        OMNI_MDNS[Gemma E4B Devices via USB/mDNS]:::net
    end

    %% Yhteydet
    T <--> |REST/WS| LLM
    CLI <--> |Missions| LLM
    Mobile <--> |WS & QR-Pair| LLM
    LLM <--> RAG
    LLM --> Hermes
    LLM --> OC
    LLM --> |Code| AST
    AST --> WSBOX
    LLM --> |Offload Task| OMNI_WS
    LLM --> |Offload Task| OMNI_MDNS
```

### Keskeiset Komponentit

| Moduuli | Teknologia | Kuvaus |
|---------|-------------|---------|
| **Hermosto (Watcher)** | `watchdog` + `asyncio` | Reagoi `Inbox/` -kansioon ilmestyviin syötteisiin < 50ms latenssilla. Osaa käsitellä massiivisia rinnakkaisia tietuetaakkoja. |
| **Kognitio (LLM Gateway)**| `llm_client.py` | Ohjaa päälaskennan (Ollama / Gemma 4). Toimii orkestraattorina koko verkolle. |
| **OmniNode Edge** | `WebAssembly / mDNS` | Mahdollistaa laskennan hajauttamisen USB-tetheröityihin mobiililaitteisiin (**Gemma 4 E2B/E4B**) täysin Zero-Install periaatteella. |
| **AST & Win Sandbox** | Lokaali Eristys | Kaksikerroksinen suojaus: AST-skannaus ja Microsoft Windows Sandbox (.wsb) estämään vaaralliset ajot isäntäkäyttöjärjestelmässä täysin irrotetusti. |
| **RAG-Muisti** | `ChromaDB` | Vektoroitu semanttinen lyhyt- ja pitkäkestoinen muisti (Embedding: `mxbai-embed-large`). |
| **Hermes & OpenClaw** | Työnkulut | Vahvasti asynkroniset kognitiotyönkulut tauottomaan iteratiiviseen tutkimukseen ja syväpäättelyyn. |

---

## ⚡ Universal Sovereign Launch (Asennus & Käyttö)

Sovereign Engine hylkää paloitellut scriptit. Kokonaisuus ajetaan ylös yhdellä interaktiivisella komentoketjulla.

**Vaatimukset:**
- Python 3.10+
- [Ollama](https://ollama.com) asennettuna taustalla.

**1. Käynnistä "Matrix" (Kaikki järjestelmät Liveen)**
```powershell
.\launch_sovereign.ps1
```

Skripti laukaisee Watcherin, RAG-kannan, FastAPI-palvelimen (UI ja WebSocketit) sekä Sovereign CLI:n yhdessä synkronoidussa instanssissa.

### Tehtävien Anto
Käyttö on yksinkertaista. Pudota dokumentteja, csv-tiedostoja tai komentoja `Inbox/` kansioon joko ohjelmallisesti, käyttöliittymän upload-painikkeesta, komentoriviltä, tai kauko-ohjaimena toimivalta kännykältä!

---

## 🛡️ Sovereign Security Model

**Täysi lokaali ilmaherruus.** Järjestelmä sijaitsee kokonaan sinun laitteistollasi:
1. **Zero Cloud Egress:** Kaikki inferenssi lokaalisti asennetuilla malleilla. Yksikään koodirivi tai dokumentti ei poistu laitteelta.
2. **Kaksikerroksinen Sandbox:** AST-skannaus estää vaaralliset kutsut → Windows Sandbox (.wsb) varmistaa OS-tason eristyksen suoritukselle.
3. **Air-Gapped OmniNode:** USB-tetheröity lisälaskentateho ei nojaa WiFi-verkkoon, vaan rakentaa tunkeutumattoman oman USB/IP-väylän laitteiden välille.

---

## 🗺️ Roadmap

| Vaihe | Kuvaus | Status |
|-------|--------|--------|
| v3.0 | Perusarkkitehtuuri (Watcher, RAG, AST Sandbox) | ✅ Valmis |
| v3.5 | Sovereign Engine (Evoluutio, Agent Print, Swarm) | ✅ Valmis |
| v3.5.1 | MCP Server, Win Sandbox, Hermes & OpenClaw | ✅ Valmis |
| **v4.0** | **OmniNode Edge (WASM/USB mDNS), Gemma 4 E2B/E4B -arkkitehtuuri, Dashboard UI** | ✅ **Valmis (Stable)** |

---

<div align="center">
  <p>Rakennetaan ohjelmistofilosofian vapaata tulevaisuutta. 🚀</p>
  <i>- AgentDir Sovereign Team</i>
</div>
