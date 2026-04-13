# 09_QUICK_REFERENCE.md — Pikaohje
# Kaikki tekniikat yhdellä sivulla.
# Tulosta tai pidä auki kun työskentelet.

---

## TÄYDELLISEN KEHOTTEEN KAAVA

```
[ROOLI]      Toimi [rooli] -roolissa. (→ 01_ROLE_AND_IDENTITY.md)
[YLEISÖ]     Kohdeyleisö on [yleisö].
[KONTEKSTI]  Projektimme on AgentDir 3.5. [lisää relevantti tieto].
             Käytä VAIN annettua materiaalia. (→ 02_CONTEXT_RULES.md)
[PÄÄTTELY]   Ajattele askel askeleelta ennen vastausta. (→ 03_REASONING_PROTOCOL.md)
[TEHTÄVÄ]    Tee täsmälleen: [mitä]
[RAJOITTEET] ÄLÄ: [mitä ei saa tehdä] (→ 05_CONSTRAINTS.md)
[MUOTOILU]   Vastaus muodossa: [miltä näyttää] (→ 04_OUTPUT_FORMATS.md)
[ESIMERKKI]  Tässä malli: [esimerkki] (→ 08_FEW_SHOT_EXAMPLES.md)
```

---

## TILANNE → TEKNIIKKA PIKATAULU

| Tilanne | Tekniikka | Tiedosto |
|---|---|---|
| Uusi session | Rooli + konteksti | 01 + 02 |
| Monimutkainen ongelma | Chain of Thought | 03 |
| Useita vaihtoehtoja | Tree of Thoughts | 03 |
| Tulos melkein oikea | Iterointi | 06 |
| Et tiedä miten kysyä | Meta-kehote | 07 |
| Haluaat tiettyä tyyliä | Few-shot esimerkki | 08 |
| Koodin kirjoitus | Rooli + rajoitteet + esimerkki | 01+05+08 |
| Arkkitehtuuripäätös | Päätösprotokolla | 03 |
| Bugin analyysi | Causal Engine | 03 |
| Dokumentaatio | Muotoilu + rooli | 01+04 |

---

## KOODINKIRJOITUKSEN PIKAKEHOTE

```
Toimi Senior Python Engineer -roolissa.
Kirjoita [komponentti] joka:
- Tekee: [mitä]
- Ei tee: [mitä rajataan pois]
- Palauttaa: [mitä]
- Käsittelee virheet: [miten]

Kirjoita ensin testi, sitten toteutus.
Suomenkieliset kommentit, englanninkielinen koodi.
Max [X] riviä.
Ei ulkoisia kirjastoja paitsi: [lista].
```

---

## ITEROINTIPIKAKEHOTTEET

```
"Hyvä. Kohdassa X: [muutos]. Kaikki muu pysyy."
"Tee tiiviimmäksi. Pidä [A] ja [B]. Poista loput."
"Vaihda äänensävy [X] → [Y]. Faktat samana."
"Lisää virheenkäsittely kohtiin [A, B, C]."
"Optimoi VAIN [funktio]. Älä muuta muuta."
```

---

## AGENTDIR-SPESIFISET PIKAKEHOTTEET

```
"Lue !_SOVEREIGN.md ensin. Kirjoita sitten hypoteesi log.md:hen."
"Toteuta [X] Policy → Hypothesis → Sandbox → Verify -järjestyksessä."
"Käytä openclaw-moodia [yksinkertainen tehtävä]."
"Käytä hermes-moodia [pitkäkestoinen / muistia vaativa tehtävä]."
"Generoi Agent Print tämän suorituksen jälkeen."
"Muuta VAIN workspace/[tiedosto]. Älä koske cli.py tai orchestrator.py."
```

---

## KIELLOT PIKALISTANA

```
❌ rm -rf / rekursiivinen poisto
❌ exec() käyttäjän syötteelle
❌ Verkkoyhtedet sandboxista
❌ Salasanat / avaimet logeissa
❌ Refaktoroi pyytämättömiä tiedostoja
❌ Lupaa toimivuutta ilman testiä
❌ Hallusinoi faktat joita ei kontekstissa ole
❌ Yli 300 riviä per tiedosto
```

---

## ITSEKRITIIKKILISTA (ennen lähettämistä)

```
□ Vastaako alkuperäiseen kysymykseen?
□ Muutinko vain pyydettyjä asioita?
□ Onko testi kirjoitettu?
□ Onko hypoteesi log.md:ssä?
□ Läpäiseekö constraints.md säännöt?
□ Onko lähde mainittu jos fakta ei ole yleistietoa?
□ Onko yksinkertaisempi ratkaisu olemassa?
```

---

## SESSIOALOITUS (kopioi tähän sessioon)

```
Olen tekemässä AgentDir 3.5 Sovereign Engine -projektia.

Roolisi: Senior Systems Engineer + Cognitive Architect
Kieli: Python 3.11, suomenkieliset kommentit
Kuri: Karpathy-discipline (kirurgiset muutokset)
Rajoitteet: katso 05_CONSTRAINTS.md

Edellinen vaihe: [mitä tehtiin]
Nykyinen tehtävä: [mitä tehdään]
Tiedostot joita saa muuttaa: [lista]

Aloita lukemalla !_SOVEREIGN.md ja kirjoittamalla
hypoteesi wiki/log.md:hen.
```
