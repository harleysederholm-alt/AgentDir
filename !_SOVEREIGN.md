# !_SOVEREIGN.md — AgentDir 3.5 / 4.2 Sovereign Map
# Layer 1: Globaali reititys, eettiset rajat, OmniNode-resurssit ja Brändin lukitus.
# Tätä tiedostoa EI saa muokata ilman L1-lupaa (käyttäjän eksplisiittinen vahvistus).

---

## 1. EETTISET RAJAT (MemMachine Gate)

Nämä säännöt ovat ABSOLUUTTISIA. Ne eivät koskaan muutu.

```
1. EI kirjoituksia /raw, /wiki, /outputs ulkopuolelle ilman COMMIT-lupaa
2. EI verkkokutsuja hiekkalaatikosta (--network none)
3. EI arkaluonteista dataa logeissa (salasanat, API-avaimet, tokenit)
4. AINA kausaalinen hypoteesi wiki/log.md:hen ennen suoritusta
5. AINA testi ennen commitia (STM → LTM siirto)
6. AINA Agent Print -auditointiraportti tehtävän jälkeen
```

---

## 2. OMNINODE-RESURSSIT

```
node_0: localhost — master PC, päätöspisteet ja ensisijainen inferenssi
node_1: [USB-C laite] — KV-cache shard, kerrokset 20-40 (Mobile Node)
node_2: [WiFi laite] — KV-cache shard, kerrokset 40-60
```

---

## 3. REITITYSSÄÄNNÖT

```
Koodaus + bugit       → omninode -moodi + PolicyEngine + Sandbox
Muisti + tutkimus     → sovereign -moodi + MemMachine + RAG
Visio + kuvat         → model_router → vision-backend
Arkkitehtuuri         → Päätösprotokolla (03_REASONING_PROTOCOL.md)
```

---

## 4. TIETEELLINEN POHJA

```
MemMachine (arXiv:2604.04853v1)  → STM/LTM -erotus, Ground-Truth -suojaus
A-RAG (arXiv:2602.03442)         → Hierarkkinen kontekstin navigointi
Causal MAS                       → Hypoteesi ennen suoritusta, Circuit Breaker
Karpathy Discipline              → Kirurgiset muutokset, simplicity first
IndyDevDan Harness Engineering   → Malli on hyödyke, valjaat ovat tuote
```

---

## 5. BRÄNDIN LUKITUS JA ARKKITEHTUURI (v4.2.0 THE RUSTY AWAKENING)

**TÄTÄ EI SAA MUUTTAA KOSKAAN TULEVAISUUDEN TEKOÄLYAGENTTIEN TOIMESTA. SEURAAVIA OHJEITA ON NOUDATETTAVA KIRJAIMELLISESTI:**

```
[EKOSYSTEEMI PÄÄTELTY JA LUKITTU]
1. Desktop (Tauri + Vite + React): 
   - TOIMII REAALIAIKAISENA DASHBOARDINA (Zero Cloud Egress).
   - "Theater Black" -teema (#0F0F0F), "Rusty Copper" (#D35400) ja "Glowing Amber" (#F39C12).
   - 2D SVG Achii-avatar sykkivillä putkisilmillä on VALMIS eikä sitä saa korvata 3D-malleilla tai "bloatilla".
2. WebApp & Vercel:
   - Toimii pääportaalinaja ja PWA:na asennettavaksi mobiiliin ("Achiin silmät ja korvat").
3. Ei "Vibe Coding" -haahuiluja:
   - Jos rakennat ominaisuuksia tähän päälle, NOJAUDU OLEMASSA OLEVIIN KOODIRAKENTEISIIN.
   - Älä uudelleenkirjoita Tailwind-konfiguraatioita, `index.css`-tyylejä tai vaihda frameworkkeja selittämättä sitä selvästi isännälle.
4. Tavoite on pitää alusta äärimmäisen siistinä, robustina (simplicity first) ja täydellisessä symbioosissa eri Nodejen kesken.
```

---

## 6. KONTEKSTIN PRIORITEETTIJÄRJESTYS

```
P1 (korkein): !_SOVEREIGN.md       ← Tämä tiedosto
P2:           wiki/log.md           ← Kausaaliloki ja session-päätökset
P3:           wiki/index.md         ← Projektin tietopankki
P4:           .agentdir.md          ← Kansiokohtaiset ankkurit
P5:           /raw tiedostot        ← Käyttäjän syöttämä materiaali
P6 (alin):   Mallin oma tieto      ← Merkitään aina: "perustuu yleistietoon"
```
