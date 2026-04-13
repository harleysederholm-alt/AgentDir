# !_SOVEREIGN.md — AgentDir 3.5 Sovereign Map
# Layer 1: Globaali reititys, eettiset rajat ja OmniNode-resurssit.
# Tätä tiedostoa EI saa muokata ilman L1-lupaa (käyttäjän eksplisiittinen vahvistus).

---

## EETTISET RAJAT (MemMachine Gate)

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

## OMNINODE-RESURSSIT

```
node_0: localhost — master PC, päätöspisteet ja ensisijainen inferenssi
node_1: [USB-C laite] — KV-cache shard, kerrokset 20-40
node_2: [WiFi laite] — KV-cache shard, kerrokset 40-60
```

---

## REITITYSSÄÄNNÖT

```
Koodaus + bugit       → openclaw -moodi + PolicyEngine + Sandbox
Muisti + tutkimus     → hermes -moodi + MemMachine + RAG
Visio + kuvat         → model_router → vision-backend
Arkkitehtuuri         → Päätösprotokolla (03_REASONING_PROTOCOL.md)
```

---

## TIETEELLINEN POHJA

```
MemMachine (arXiv:2604.04853v1)  → STM/LTM -erotus, Ground-Truth -suojaus
A-RAG (arXiv:2602.03442)         → Hierarkkinen kontekstin navigointi
Causal MAS                       → Hypoteesi ennen suoritusta, Circuit Breaker
Karpathy Discipline              → Kirurgiset muutokset, simplicity first
IndyDevDan Harness Engineering   → Malli on hyödyke, valjaat ovat tuote
```

---

## KONTEKSTIN PRIORITEETTIJÄRJESTYS

```
P1 (korkein): !_SOVEREIGN.md       ← Tämä tiedosto
P2:           wiki/log.md           ← Kausaaliloki ja session-päätökset
P3:           wiki/index.md         ← Projektin tietopankki
P4:           .agentdir.md          ← Kansiokohtaiset ankkurit
P5:           /raw tiedostot        ← Käyttäjän syöttämä materiaali
P6 (alin):   Mallin oma tieto      ← Merkitään aina: "perustuu yleistietoon"
```
