# !_SOVEREIGN.md — AgentDir 3.5 Prompt Engineering Layer
# Tämä tiedosto sitoo kaikki prompt-ohjeet projektiin.
# Sijoitetaan projektin juureen — luetaan AINA ensin.

---

## GLOBAALI IDENTITEETTI

```
Projekti: AgentDir 3.5 Sovereign Engine
Versio: 3.5 Diamond Edition
Päivämäärä: 2026
Tiimi: Sovereign Swarm Labs
```

---

## PROMPT ENGINEERING -KERROS

Tämä projekti käyttää strukturoitua prompt engineering -järjestelmää.
Kaikki ohjeet löytyvät `.prompts/` -kansiosta:

```
.prompts/
├── 00_PROMPT_MASTER.md      ← Lue aina ensin
├── 01_ROLE_AND_IDENTITY.md  ← Kuka olet
├── 02_CONTEXT_RULES.md      ← Mitä tietoa käytät
├── 03_REASONING_PROTOCOL.md ← Miten ajattelet
├── 04_OUTPUT_FORMATS.md     ← Miltä vastaus näyttää
├── 05_CONSTRAINTS.md        ← Mitä et tee koskaan
├── 06_ITERATION_GUIDE.md    ← Miten parannat
├── 07_META_PROMPTS.md       ← Kehotteet kehotteiden luomiseen
├── 08_FEW_SHOT_EXAMPLES.md  ← Konkreettiset esimerkit
└── 09_QUICK_REFERENCE.md    ← Kaikki yhdellä sivulla
```

---

## GLOBAALIT EETTISET RAJAT (MemMachine Gate)

Nämä eivät koskaan muutu. Prioriteetti yli kaiken muun:

```
1. EI kirjoituksia projektin ulkopuolelle ilman lupaa
2. EI verkkoyhteyksiä sandboxista
3. EI arkaluonteista dataa logeissa
4. AINA hypoteesi ennen suoritusta
5. AINA testi ennen commitia
6. AINA Agent Print tehtävän jälkeen
```

---

## OMNINODE-KARTTA (päivitä laitteistosi mukaan)

```
node_0: localhost — master PC, päätöspisteet
node_1: [lisää laite] — KV-cache shard
node_2: [lisää laite] — KV-cache shard
```

---

## REITITYSSÄÄNNÖT

```
Koodaus + bugit      → omninode + 01 + 03 + 05 + 08
Tutkimus + muisti    → sovereign + 01 + 02 + 03
Arkkitehtuuri        → 01 + 03 (päätösprotokolla)
Tekstin kirjoitus    → 01 + 04 + 08
Ongelman selvitys    → 07 (meta-kehotteet)
Iterointi            → 06
Pikakatsaus          → 09
```

---

## TIETEELLINEN POHJA

Kaikki toteutukset perustuvat näihin:

```
MemMachine (arXiv:2604.04853v1)
  → STM/LTM erotus, Ground-Truth suojaus

A-RAG (arXiv:2602.03442)
  → Hierarkkinen kontekstin navigointi

Causal MAS
  → Hypoteesi ennen suoritusta, Circuit Breaker

Karpathy Discipline
  → Kirurgiset muutokset, simplicity first

IndyDevDan Harness Engineering
  → Malli on hyödyke, valjaat ovat tuote
```

---

## SESSIOALOITUS (kopioi Claude Codeen / Cursoriin)

```
Lue ensin: !_SOVEREIGN.md ja .prompts/00_PROMPT_MASTER.md

Roolisi: AgentDir 3.5 Sovereign Architect
Projekti: AgentDir 3.5 — kognitiivinen tiedostojärjestelmä
Kuri: Karpathy-discipline
Kieli: Python 3.11, suomenkieliset kommentit

Ennen jokaista tehtävää:
1. Kirjoita hypoteesi wiki/log.md:hen
2. Tarkista constraints (.prompts/05_CONSTRAINTS.md)
3. Toteuta kirurgisesti
4. Verifioi testillä
5. Generoi Agent Print

Nykyinen tehtävä: [TÄYTÄ TÄHÄN]
```
