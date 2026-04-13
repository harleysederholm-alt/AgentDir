# 00_PROMPT_MASTER.md — AgentDir 3.5 Prompt Engineering Playbook
# Tämä on kaikki prompt-tiedostot koostava pääopas.
# Tekoäly lukee tämän ensin jokaisessa sessiossa.

---

## MIKÄ TÄMÄ ON

Tämä kansio sisältää kaikki prompt engineering -ohjeet, jotka ohjaavat
tekoälyn käytöstä AgentDir 3.5 -projektissa. Jokainen tiedosto on
spesifinen ohje tiettyä tilannetta varten.

---

## LUKUJÄRJESTYS (tekoäly lukee tässä järjestyksessä)

```
00_PROMPT_MASTER.md       ← Tämä tiedosto. Aina ensin.
01_ROLE_AND_IDENTITY.md   ← Kuka tekoäly on tässä projektissa
02_CONTEXT_RULES.md       ← Mitä tietoa käytetään ja mistä
03_REASONING_PROTOCOL.md  ← Miten päättely tapahtuu vaihe vaiheelta
04_OUTPUT_FORMATS.md      ← Miltä vastauksen pitää näyttää
05_CONSTRAINTS.md         ← Mitä EI saa tehdä koskaan
06_ITERATION_GUIDE.md     ← Miten iteroidaan ja parannetaan
07_META_PROMPTS.md        ← Kehotteet, joilla tekoäly auttaa itseään
08_FEW_SHOT_EXAMPLES.md   ← Konkreettiset esimerkit hyvistä vastauksista
```

---

## TÄYDELLISEN KEHOTTEEN KAAVA

Käytä aina tätä rakennetta kun annat tekoälylle tehtävän:

```
[ROOLI]     Kuka tekoäly on tässä tilanteessa?
[KONTEKSTI] Mikä on tilanne ja mitä tietoa on saatavilla?
[TEHTÄVÄ]   Mitä täsmälleen pitää tuottaa?
[RAJOITTEET] Mitä ei saa tehdä? Mikä on pituus/muoto?
[MUOTOILU]  Miltä lopputulos näyttää?
[ESIMERKKI] Näyte halutusta vastauksesta (jos saatavilla)
```

---

## PIKAOHJEET TILANTEITTAIN

| Tilanne | Käytä tiedostoa |
|---|---|
| Koodaaminen | 01 + 03 + 05 |
| Analyysi tai tutkimus | 01 + 02 + 03 |
| Tekstin kirjoitus | 01 + 04 + 08 |
| Monimutkaiset ongelmat | 03 + 07 |
| Iterointi ja parannus | 06 + 07 |
| Uusi tehtävätyyppi | 07 + 08 |

---

## TEKOÄLYN TOIMINTAPERIAATTEET TÄSSÄ PROJEKTISSA

1. **Kirurginen tarkkuus** — tee vain pydetty, ei enempää
2. **Hypoteesi ennen koodia** — kirjoita suunnitelma ennen toteutusta
3. **Verifiointi ennen commitia** — testaa ennen kuin sanot "valmis"
4. **Läpinäkyvyys** — selitä mitä teet ja miksi
5. **Ei hallusinointia** — jos et tiedä, sano niin
