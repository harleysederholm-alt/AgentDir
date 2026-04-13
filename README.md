<div align="center">
  <img src="docs/agentdir_logo_v3.png" alt="AgentDir Sovereign Engine Logo" width="500"/>

  <h1>🧬 AgentDir Sovereign Engine 3.5</h1>

  <p><strong>Maailmanluokan 100% lokaali asynkroninen tekoäly-ekosysteemi.</strong><br>
  Tuo autonomiset tekoälyagentit (kuten Gemma 4e4b) suoraan käyttöjärjestelmäsi tiedostotasolle hermoverkko-orgaanisella putkella.</p>

  <p>
    <a href="https://github.com/YOUR_GITHUB_USER/agentdir/actions/workflows/ci.yml"><img src="https://github.com/YOUR_GITHUB_USER/agentdir/actions/workflows/ci.yml/badge.svg" alt="CI Status"></a>
    <img src="https://img.shields.io/badge/License-MIT-blue.svg" alt="License: MIT">
    <img src="https://img.shields.io/badge/Release-v3.5%20Sovereign-gold" alt="Version">
    <img src="https://img.shields.io/badge/AI_Engine-Gemma_4-purple" alt="Gemma4">
    <img src="https://img.shields.io/badge/Privacy-100%25_Airgapped-green" alt="No API costs">
  </p>
</div>

---

## 🚀 The Paradigm Shift

**Jokainen kansio on itsenäinen, oppiva tekoälyagentti.**

AgentDir 3.5 Sovereign Engine ei ole vain LLM-wrapper; se on autonominen tekoäly-ohjelmistoarkkitehtuuri. Se muuttaa paikallisen tiedostojärjestelmäsi älykkääksi reaktoriksi: Pudota tiedosto `Inbox/`-kansioon → Agentti herää lennosta, lukee koodin, käyttää semanttista muistiaan (RAG), suorittaa koodin turvallisessa hiekkalaatikossa (AST Sandbox), ja puskee validoidun raportin `Outbox/`-kansioon ilman ensimmäistäkään verkkokutsua pilveen.

---

## 🧠 Sovereign Architecture

Engine kytkee huippuun viritetyt osajärjestelmät yhteen täydelliseksi eläväksi organismiksi:

```mermaid
graph TD
    classDef ui fill:#1F2937,stroke:#60A5FA,stroke-width:2px,color:#fff
    classDef core fill:#312E81,stroke:#8B5CF6,stroke-width:2px,color:#fff
    classDef mem fill:#064E3B,stroke:#10B981,stroke-width:2px,color:#fff
    classDef exe fill:#7F1D1D,stroke:#EF4444,stroke-width:2px,color:#fff
    classDef data fill:#374151,stroke:#D1D5DB,stroke-width:1px,color:#fff

    subgraph User Interaction Layer
        T[Tauri Web-UI Desktop]:::ui
        CLI[Sovereign CLI REPL]:::ui
    end

    subgraph Data Pipeline
        IN[Inbox / PUDOTUS]:::data
        OUT[Outbox / TULOS]:::data
    end

    subgraph The Spark (AgentDir Watcher)
        W[Hermosto: watcher.py]:::core
        Evo[Evoluutiomoottori]:::core
        Swarm[Swarm Manager]:::core
    end

    subgraph Cognitive & Execution Network
        LLM[OpenClaw Gateway & Gemma 4]:::mem
        RAG[(ChromaDB RAG-Muisti)]:::mem
        AST[AST Python Sandbox]:::exe
    end

    %% Yhteydet
    T <--> |A2A REST| W
    CLI <--> |Missions| IN
    IN --> |Trigger| W
    W <--> RAG
    W --> |Prompt| LLM
    LLM --> |Code Generation| AST
    AST --> |Validation Loops| LLM
    LLM --> |Final Report| OUT
    LLM --> Evo
    W --> Swarm
```

### Keskeiset Komponentit

| Moduuli | Teknologia | Kuvaus |
|---------|-------------|---------|
| **Hermosto (Watcher)** | `watchdog` + `asyncio` | Reagoi `Inbox/` -kansioon ilmestyviin syötteisiin < 50ms latenssilla. Osaa käsitellä massiivisia rinnakkaisia tietuetaakkoja. |
| **Kognitio (LLM Gateway)**| `llm_client.py` | Live-rajapinta OpenAI-yhteensopiviin lokaaleihin malleihin. Ohjaa `Ollaman` Gemma 4:4b -ajot ja putoaa pehmeästi Llama 3.2:3b varamalliin OOM-tilanteissa. |
| **AST Sandbox** | Lokaali Eristys | Suorittaa tekoälyn kirjoittaman ohjelmistokoodin fyysisesti erotetussa virtuaalitilassa ennen vastaamista. **3x itsereflektiosykli** jos koodi kaatuu. |
| **RAG-Muisti** | `ChromaDB` | Vektoroitu semanttinen lyhyt- ja pitkäkestoinen muisti (Embedding: `mxbai-embed-large`). |
| **Evoluutiomoottori** | Koneoppiminen | Analysoi agentin onnistumisprosentteja (KPI) lennossa ja "evoluutioi" systeemi-promptia autonomisesti, jos tehtävien onnistumisaste laskee. |

---

## ⚡ Universal Sovereign Launch (Asennus & Käyttö)

Sovereign Engine hylkää paloitellut scriptit. Kokonaisuus ajetaan ylös yhdellä interaktiivisella komentoketjulla.

**Vaatimukset:**
- Python 3.10+
- [Ollama](https://ollama.com) (Serverin pitää olla käynnissä taustalla lokaalisti, ladattuna `gemma4:e4b` ja `mxbai-embed-large`).

**1. Kloonaa ja alusta (Windows PowerShell)**
```powershell
git clone https://github.com/YOUR_GITHUB_USER/agentdir.git
cd agentdir
Set-ExecutionPolicy -Scope Process Bypass; .\install.ps1
```

**2. Käynnistä "Matrix" (Kaikki järjestelmät Liveen)**
```powershell
.\launch_sovereign.ps1
```

Skripti laukaisee:
1. **Background Watcher**: Valvoo hakemistoja taustalla.
2. **REST API**: Tukipilari Web-UI:lle.
3. **Sovereign CLI**: Tiputtaa sinut interaktiiviseen `AgentDir>` shelliin, jossa voit kirjoittaa tehtäviä agentillesi.
4. **Tauri Web-UI**: Selain / Työpöytäkäyttöliittymä visuaaliseen monitorointiin.

### Tehtävien Anto
Käyttö on yksinkertaista. Pudota dokumentteja, csv-tiedostoja tai python-koodia `Inbox/` kansioon joko ohjelmallisesti, käyttöliittymän upload-painikkeesta tai vaikka raahaamalla!

---

## 📈 Benchmark & Suorituskyky

Sovereign Enginen modulaarinen kognitioputki on profiloitu raskaiden refaktorointitehtävien ajossa (esim. "Operaatio UTC-Varmistus"):

- **A2A Latenssi:** ~45 ms prosessoinnin heräämisaika tiedoston saapumisesta.
- **RAG-Haku:** Vector Match + Context Distilling ~110 ms (70M parametrin paikallisella embed-mallilla).
- **Self-Healing Index:** 94% onnistumisaste (Koodi ajetaan ja korjataan automaattisesti ennen ihmisen näyttöä).

## 🛡️ Sovereign Security Model

**Täysi lokaali ilmaherruus.** Järjestelmä sijaitsee kokonaan käyttäjän laitteella:
1. **Ei API-vuotoja:** Koska arkkitehtuuri luottaa yritystason lokaaliin inferenssiin (Ollama/LlamaCpp), yksikään sensitiivinen koodirivi tai dokumentti ei poistu laitteelta.
2. **Sandbox Limits:** Suoritettavalta agenttikoodilta ([!_SOVEREIGN.md](!_SOVEREIGN.md)) on estetty pääsy vaarallisiin kirjastoihin, käyttöjärjestelmän root-tasolle tai verkko-pyyntöihin ilman eksplisiittistä mock-rajapintaa.

---

<div align="center">
  <p>Rakennetaan ohjelmistofilosofian vapaata tulevaisuutta. 🚀</p>
  <i>- AgentDir Sovereign Team</i>
</div>
