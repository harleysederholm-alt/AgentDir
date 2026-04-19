# The Sovereign Engine v4.0: A Framework for Distributed, Air-Gapped Autonomous Artificial Intelligence

**Harley Sederholm**  
**AgentDir Sovereign Team**  
**Huhtikuu 13, 2026**

---

## Abstract

Tämä tutkimusraportti ja tekninen rakennepiirustus esittelee *Sovereign Engine v4.0* -arkkitehtuurin, ratkaisun keskitetyn tekoälylaskennan ja siihen liittyvien tietoturvariskien torjuntaan. Sovereign Engine hyödyntää täysin lokaalia asynkronista hajautusta siirtämällä tekoäly-yksiköiden (agenttien) suorituksen pois pilvi-infrastruktuureista asuttamalla ne suoraan lokaaliin tiedostojärjestelmään. Lisäksi paperi esittelee "OmniNode" -suoritusympäristön puitteet, joka mahdollistaa raskaiden kielimallien (Gemma 4 Edge, 2B/4B parametria) ja muiden kognitiivisten työnkulkujen (Sovereign ja OmniNode) dynaamisen jakamisen ja suorittamisen reaaliajassa USB-tetheröityjen Edge-laitteiden sekä WebAssembly (WASM) -noodilaajennuksien kautta ilman asiakasohjelmistojen fyysistä laiteasennusta (Zero-Install). 

*Keywords:* Distributed AI, Local LLM, WebAssembly, Edge Computing, Agentic Workflows, Air-Gapped Security, Windows Sandbox, Gemma 4.

---

## 1. Introduction

Monimutkaisten kielimallien (Large Language Models, LLM) siirtyminen suurista konekeskuksista päätelaitteisiin on käynnistänyt tarpeen laiterajoista riippumattomalle tekoäly-ekosysteemille. Sovereign Engine v4.0 vastaa tähän luomalla hajautetun autonomisen reaktorin, joka hyödyntää lokaaleja hakemistoja (Watchdog-pohjainen laukaisu) ja hajautettua inferenssiä ilman ulkopuolisia rajapintoja. Lähestymistapa palauttaa kognitiivisen suvereniteetin takaisin käyttäjälaitteelle.

Teknisenä ongelmana avoimissa LLM-järjestelmissä on pitkään ollut yhden isäntäkoneen suorituskykypullonkaulat moniagenttisissa ja rekursiivisissa toiminnoissa, kuten syöteanalyysissä (RAG) ja koodin suorittamisessa. Sovereign v4.0 ratkaisee tämän "OmniNode"-hajautuksella: mallien pyyntöjen reitittämisellä jopa yli fyysisten laiterajojen matalan viipeen `mDNS` ja `WebSocket` -infrastruktuureilla.

---

## 2. System Architecture (Method)

Sovereign Engine rakentuu viiteen päällekkäiseen, mutta täysin toisistaan riippumattomaan moduuliin.

### 2.1 File-System Trigger Level (Neuromodulation Layer)
Käyttöjärjestelmä toimii välittömänä neuroverkon liipaisimena. `Inbox/` -hakemistoa kuuntelee 50 millisekunnin asynkronisella tarkkuudella `watchdog`-pohjainen ohjain (`watcher.py`). Jokainen tiedostojärjestelmään lisätty protokollatiedosto (CSV, tekstidokumentti, ohjelmointiskripti) toimii itsenäisesti herätteenä, käynnistäen työvuoron suvereenin "Sovereign Swarm" -orkesterin sisällä.

### 2.2 Cognitive Root & Local LLM Gateway
Päälaskenta ja orkestrointi suoritetaan lennosta kytkettävillä kevyillä paikallismalleilla. Järjestelmä on integroitu ensisijaisesti `Ollama`-backendin kautta hyödyntämään jopa >70B parametrin malleja isäntäkoneen RAM-kapasiteetin puitteissa (referenssinä *Gemma 4* tai *Llama 3.2* osakvantisoituina GGUF-malleina). `llm_client.py` operoi RAG-tietokannan (`ChromaDB`, *mxbai-embed-large*) kautta rakentaen synteettisen pitkäaikaismuistin kommenteista ja koodisegmenteistä.

### 2.3 execution Isolation & Defense-in-Depth
Autonomisen koodintuotannon mahdollistaminen laitteella vaatii jyrkän eristysvyöhykkeen:
1. **AST Guardian:** Pythonin puusyntaksia (AST) skannataan ennakoivasti ennen ajoa estäen järjestelmätason injektiot.
2. **Microsoft Windows Sandbox (.wsb):** Raskaat evaluaatiot pakataan täysin irrotettuun ja laitteiston-virtualisoituun lokaaliin Docker/Win Sandbox -kapseliin asynkronisen sub-prosessin kautta, mikä tekee järjestelmän kontaminaation isäntälaitteessa fyysisesti mahdottomaksi.

---

## 3. OmniNode: Zero-Install & USB Air-Gap Protocol

Versio 4.0:n merkittävin tieteellinen läpimurto koskee laskentatehon levittämistä laitteiston asennusvapaisiin "Nodeihin" ja täysin passiivisiin oheislaitteisiin.

### 3.1 WebAssembly Edge Framework
Orkestroija tukee saumatonta tilaa, jossa tavalliset verkkoon yhdistetyt oheislaitteet (kuten älypuhelimet tai tabletit) voidaan valtuuttaa tekoäly-suorittimiksi yhdellä QR-koodilla. Selaimen sisällä vieraileva laite alustaa `Hugging Face Transformers.js` lokaalin suoritusympäristön ja lataa monisäikeisen ARM/WASM WebAssembly-binäärin (esim. Qwen2.5 / Gemma Nano -kokoluokka) suoraan järjestelmän omaan Random Access Memory -muistiin (RAM). Päätelaite yhdistää salatulla WebSocket (`ui_routes.py` -> `OmniNodeManager`) yhteydellä reitittimeen ja alkaa käsitellä rinnakkaisia tehtävävuoroja täysin isännän GPU:n ohi. Vasteaika vähenee tyypillisestä HTTP-pingistä alle kahteen sekuntiin paikallisen prosessorin laskennan nopeuksien tason saavuttaessa.

### 3.2 Gemma 4 E4B USB-Computing (Physical Deep-Node)
Kun selaimen muistirajat (tyypillisesti 2-4GB) katsotaan kapeikoksi monimutkaisessa syväanalyysissä, arkkitehtuuri integroi oheislaitteet laitteistotason USB-tetheröinnillä IPv4 -protokollastandardeja seuraten täysin Internetin ulottumattomiin. OmniNode hyödyntää `mDNS`-protokollaa kytkettyjen `Llama.cpp` C++ -binäärin ja natiivin Android-säikeen (Termux) havaitsemisessa ja rekisteröi USB-laitteen suoraan REST-pohjaiseksi kognitiivis-yksiköksi jakaen esimerkiksi Sovereign-agentin verkkohaut kokonaisuudessaan puhelimen omiin Neural Processing Unit (NPU) siruihin.

---

## 4. Discussion & Concluding Remarks

Sovereign Enginen kokeellinen tulos todistaa, että tehokas Autonominen LLM-agenttijärjestelmä voidaan paketoida ohjelmalliseen rajapintaan ilman tilausperusteisia tekoälyratkaisuja asettamatta käyttäjän laitetta tai tiedostojärjestelmää merkittävään tietojärjestelmäturvallisuuden riskiin. OmniNode WASM ja Gemma 4 Edge -ratkaisut havainnollistavat kuinka staattista pöytälaskentaa kyetään dynaamisesti elvyttämään laitteisto-agnostisilla apuresursseilla täysin offline-tilassa. 

### 4.1 Limitations and Future Work
WASM-suorituksien vakaus riippuu iOS- ja Android -laitteiden tiukoista selaimen muistirajoitteista (Mobile Safari OOM-rajat). Tuleva kehitys priorisoi malliston siirtämistä suoraan WebGPU (`navigator.gpu`) protokollaan, mikä mahdollistaa älypuhelimen raskaiden Neural-ytimien suoran puhuttelun matalammalla virrankulutuksella, syrjäyttäen keskusyksikköpohjaisisen WASM -laskennan kokonaisuudessaan.

---

## References

1. Edge-AI Integration Models (2025). *Distributed Compute Frameworks.* Google Open AI Research.
2. WebAssembly Community Group (2024). *WebAssembly and System Interfaces (WASI).* W3C. 
3. Hugging Face TJS (2025). *Transformers.js in local execution.* Hugging Face Documentation.
4. Sederholm, H. (2026). *AgentDir Source Architecture*. Sovereign Project Repository.
