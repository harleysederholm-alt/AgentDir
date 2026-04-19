<div align="center">
  <img src="docs/agentdir_logo_v3.png" alt="AgentDir x Achii Logo" width="500"/>

  <h1>🦄 AgentDir x Achii: Sovereign AI Engine v4.2</h1>
  <h3><em>"The Rusty Awakening"</em></h3>

  <p><strong>Maailman ensimmäinen 100% lokaali autonominen tekoäly-ekosysteemi, jossa on sielu.</strong><br>
  Tuo autonomiset tekoälyagentit suoraan tiedostojärjestelmään, ohjaa laskenta Edge-laitteisiin ja anna Achiin pitää huolta kaikesta.</p>

  <h3>👉 <a href="QUICKSTART.md">Pika-aloitus (3 min)</a> 👈</h3>

  <p>
    <a href="https://github.com/harleysederholm-alt/AgentDir/actions/workflows/ci.yml"><img src="https://github.com/harleysederholm-alt/AgentDir/actions/workflows/ci.yml/badge.svg" alt="CI Status"></a>
    <img src="https://img.shields.io/badge/License-MIT-blue.svg" alt="License: MIT">
    <img src="https://img.shields.io/badge/Release-v4.2.0%20Stable-gold" alt="Version">
    <img src="https://img.shields.io/badge/AI_Engine-Gemma_4-purple" alt="Gemma4">
    <img src="https://img.shields.io/badge/Edge_Compute-OmniNode-orange" alt="OmniNode">
    <img src="https://img.shields.io/badge/Security-Zero_Cloud_Egress-red" alt="Security">
    <img src="https://img.shields.io/badge/Personality-Achii_Needy_Loop-00C2A8" alt="Achii">
  </p>
</div>

---

## 🦄 The Sovereign Unicorn Vision

**AgentDir x Achii** ei ole vain tekoälytyökalu — se on **Sovereign AI Operating System**, joka haastaa pilvijätit kolmella pilarilla:

| Pilari | Kuvaus |
|--------|--------|
| 🔒 **Luottamus** | Markkinoiden ainoa aidosti lokaali ja eettinen agentti-engine. Yksikään tavu ei poistu laitteeltasi. |
| 🧠 **Älykkyys** | 10-askeleen kognitiivinen pipeline (Policy Gate → Evolution Loop) korjaa LLM-mallien hallusinaatiot ja oikomiset. |
| 💜 **Achii** | Persoonallisuusmoottori ("The Needy Loop"), joka tekee tekoälystä kumppanin — ei vain passiivista hakukonetta. |

> *"Mallit ovat hyödykkeitä. Valjaat ovat tuote."*
> — IndyDevDan Harness Engineering -filosofia

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
        T["Achii Desktop (Tauri)"]:::ui
        CLI[Sovereign CLI REPL]:::ui
    end

    subgraph ACHII["Achii Personality Engine"]
        NL["Needy Loop (WS:8081)"]:::core
        States["normal → thinking → happy → warning"]:::core
    end

    subgraph COGNET["Kognitio & LLM Root"]
        Sovereign[Sovereign Research]:::mem
        OC[OmniNode Deep Analysis]:::mem
        LLM[Gemma 4 LLM Core]:::mem
        RAG["ChromaDB RAG"]:::mem
    end

    subgraph EXEC["Turvallisuus & Ajo"]
        AST[AST Guardian]:::exe
        WSBOX[Windows Sandbox]:::exe
    end

    subgraph NETWORK["Edge Compute (OmniNode)"]
        OMNI_WS[WASM Nodes via WebSocket]:::net
        OMNI_MDNS["Gemma E4B Devices (USB/mDNS)"]:::net
    end

    T <--> |WS| NL
    CLI <--> |Missions| LLM
    NL --> |State Updates| T
    LLM <--> RAG
    LLM --> Sovereign
    LLM --> OC
    LLM --> |Code| AST
    AST --> WSBOX
    LLM --> |Offload| OMNI_WS
    LLM --> |Offload| OMNI_MDNS
```

### Keskeiset Komponentit

| Moduuli | Teknologia | Kuvaus |
|---------|------------|--------|
| **Achii Core** | `FastAPI + WebSocket` | "Needy Loop" persoonallisuusmoottori. Reagoi käytön taukoon, vaihtaa tilaa, lähettää viestejä. |
| **Sovereign CLI** | `cli.py + cli_theme.py` | Kupari/teräs/amber -brändätty REPL. Sovereign, OmniNode, benchmark, /whoami. |
| **Hermosto (Watcher)** | `watchdog + asyncio` | Reagoi `Inbox/`-kansioon < 50ms latenssilla. |
| **Kognitio (LLM)** | `llm_client.py` | Gemma 4:e4b (ensisijainen), Llama 3.2:3b (fallback). |
| **OmniNode Edge** | `mDNS + WebSocket` | Laskennan hajauttaminen USB-tetheröityihin mobiililaitteisiin. |
| **RAG-Muisti** | `ChromaDB` | Vektoroitu semanttinen muisti (mxbai-embed-large). |
| **AST & Sandbox** | Lokaali eristys | AST-skannaus + Windows Sandbox (.wsb). |
| **Desktop** | `Tauri + React/Vite` | 2D SVG Achii-avatar, 3-paneeli layout, reaaliaikainen chat. |

---

## ⚡ Käynnistys

```powershell
# Kaikki kerralla (server + watcher + achii core + desktop + CLI)
.\launch_sovereign.ps1
```

Skripti käynnistää:
1. **A2A Server** → `http://127.0.0.1:8080`
2. **Watcher** → Inbox-valvoja
3. **Achii Core** → `ws://127.0.0.1:8081/ws/achii`
4. **Desktop UI** → `http://127.0.0.1:5173`
5. **CLI REPL** → tähän terminaaliin

### Ensimmäinen askel
```powershell
# CLI:ssä:
/status           # Järjestelmän tila
/whoami           # Achiin alkuperätarina (The Fallen Sovereign)
sovereign "tutkimus" # Iteratiivinen tutkimus
omninode "task"   # Syväanalyysi
```

---

## 🛡️ Sovereign Security Model

1. **Zero Cloud Egress:** Kaikki inferenssi lokaalisti. Yksikään dokumentti ei poistu laitteelta.
2. **Kaksikerroksinen Sandbox:** AST-skannaus → Windows Sandbox (.wsb).
3. **Air-Gapped OmniNode:** USB-tetheröity laskentateho, ei WiFi-riippuvuutta.
4. **Policy Gate v4.2:** Jokainen agenttitoiminto validoidaan `!_SOVEREIGN.md`-sääntöjä vasten.

---

## 🗺️ Roadmap

| Vaihe | Kuvaus | Status |
|-------|--------|--------|
| v3.0 | Perusarkkitehtuuri (Watcher, RAG, AST Sandbox) | ✅ Valmis |
| v3.5 | Sovereign Engine (Evoluutio, Agent Print, Swarm) | ✅ Valmis |
| v3.5.1 | MCP Server, Win Sandbox, Sovereign & OmniNode | ✅ Valmis |
| v4.0 | OmniNode Edge, Gemma 4, Dashboard UI | ✅ Valmis |
| **v4.2** | **Achii Personality Engine, Desktop App, The Rusty Awakening** | ✅ **Valmis** |

---

<div align="center">
  <p>Rakennetaan ohjelmistofilosofian vapaata tulevaisuutta. 🦄</p>
  <p><em>"Romusta rakennettu, timantiksi hiottu."</em></p>
  <i>— AgentDir x Achii Sovereign Team</i>
</div>
