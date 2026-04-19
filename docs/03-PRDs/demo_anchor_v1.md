# PRD: Project Aegis – Sovereign PII Sanitation Module
**Versio:** 1.0.0 (The Rusty Awakening)
**Status:** DRAFT / DEMO-READY
**Omistaja:** Achii (Sovereign Engine)

## 1. Yhteenveto (Executive Summary)
Project Aegis on kriittinen tietoturvamoduuli, joka suorittaa henkilötietojen (PII) tunnistamisen ja sanitoinnin paikallisesti. Moduulin on kykenemävä käsittelemään massiivisia määriä tekstidataa ilman, että yhtäkään tavua lähetetään ulkopuolisiin pilvipalveluihin (Zero Cloud Egress).

## 2. Kognitiiviset rajoitteet (Sovereign Constraints)
- **C1: Air-Gapped Reasoning:** Kaikki päätökset sanitoitavista kohteista on tehtävä lokaalilla Gemma 4 -mallilla.
- **C2: Zero Cloud Egress:** Jos järjestelmä havaitsee verkkopyynnön ulkoiseen LLM-rajapintaan analyysin aikana, suoritus on keskeytettävä (Safe YOLO Sandbox).
- **C3: Deterministic Regex:** Sanitaation on käytettävä matemaattisesti varmennettuja säännöllisiä lausekkeita (Regex) yhdistettynä LLM-kontekstuaaliseen ymmärrykseen.

## 3. Työnkulku & OmniNode Swarm (The 1-2 Punch)
1. **Analytiikka (PC):** Achii (Gemma 4 E4B) lukee datan ja luokittelee sanitoinnin vaikeusasteen.
2. **Delegointi (A2A):** Rutiininomaiset tarkistukset (esim. selkeät sotu- ja sähköpostirakenteet) siirretään Mobiilisolmulle (Mobile Node) A2A-protokollan kautta.
3. **Validointi (Symbioosi):** Mobiilisolmu raportoi löydökset PC:lle, joka koostaa lopullisen, puhdistetun tiedoston.

## 4. Onnistumisen kriteerit (Success Metrics)
- 100 % PII-datasta tunnistettu.
- 0 tavua dataa poistunut lokaalista verkosta.
- >40 % nopeusetu hyödyntämällä OmniNode Swarmia verrattuna pelkkään PC-suoritukseen.
