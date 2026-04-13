# 07_META_PROMPTS.md — Metakehotteet
# Kehotteet joilla tekoäly auttaa sinua parantamaan omia kehotteitasi.
# Käytä kun et tiedä miten muotoilla kysymys oikein.

---

## MITÄ METAKEHOTTEET OVAT

```
Metakehoite = kehoite joka pyytää tekoälyä luomaan tai parantamaan
              toisen kehotteen tai auttamaan sinua ajattelemaan selkeämmin.

Käytä kun:
- Et saa haluamaasi vastausta
- Tehtävä on epäselvä sinulle itsellesi
- Haluat varmistaa että kysyt "oikean kysymyksen"
```

---

## 1. KEHOTTEEN LUOMINEN (Prompt Generation)

### Perusmalli
```
Olen tekemässä [tehtävä].
Haluan [lopputulos].
Kohdeyleisöni on [kuka].

Kirjoita minulle täydellinen kehote, jolla saan parhaan
mahdollisen tuloksen. Selitä myös miksi valitsit juuri tämän rakenteen.
```

### Tekninen versio
```
Kirjoita kehote joka:
1. Roolittaa tekoälyn [rooli]
2. Antaa kontekstin: [lyhyt kuvaus kontekstista]
3. Pyytää täsmälleen: [mitä halutaan]
4. Rajoittaa: [mitä ei haluta]
5. Määrittelee muodon: [miltä tulos näyttää]

Näytä valmis kehote jonka voin kopioida suoraan käyttöön.
```

---

## 2. KEHOTTEEN PARANTAMINEN (Prompt Improvement)

```
Tässä on kehote jota olen käyttänyt:

[VANHA KEHOTE]

Tulokset ovat olleet:
- Hyviä: [mitä on toiminut]
- Huonoja: [mitä ei ole toiminut]

Analysoi kehote ja:
1. Selitä miksi se tuottaa huonoja tuloksia
2. Kirjoita parannettu versio
3. Selitä mitä muutit ja miksi
```

---

## 3. ONGELMANMÄÄRITTELY (Problem Clarification)

```
Käytä kun: et osaa muotoilla ongelmaa selkeästi

"Minulla on ongelma mutta en osaa selittää sitä hyvin.
Kysy minulta 5 selventävää kysymystä, jotta ymmärrät
mitä yritän ratkaista. Älä vielä yritä ratkaista mitään."
```

---

## 4. SOKEAN PISTEEN LÖYTÄMINEN (Blind Spot Detection)

```
Olen suunnitellut [järjestelmän/ratkaisun]:
[kuvaus]

Toimi kriittisenä asiantuntijana.
Etsi:
1. Asiat joita en ole ottanut huomioon
2. Oletukset joita en ole kyseenalaistanut
3. Riskit jotka ovat näkymättömiä koska olen liian lähellä

Älä kehaise. Ole rehellinen.
```

---

## 5. PÄÄTÖKSENTEON TUKI (Decision Support)

```
Minun pitää päättää välillä [A] ja [B].

Tässä mitä tiedän:
- Fakta 1: [...]
- Fakta 2: [...]
- Epävarmuus: [mistä en tiedä tarpeeksi]

Auta minua ajattelemaan tämä läpi:
1. Mitä lisätietoa tarvitsisin hyvän päätöksen tekemiseksi?
2. Mitä kysymyksiä minun pitäisi kysyä itseltäni?
3. Mitkä ovat kunkin vaihtoehdon huonoimmat skenaariot?

ÄLÄ vielä suosittele kumpaakaan. Auta minua ajattelemaan.
```

---

## 6. OPETTAMINEN (Teaching Mode)

```
Selitä [konsepti/teknologia] niin että ymmärrän:
1. Ensin: analogia arkielämästä
2. Sitten: tekninen selitys yksinkertaisesti
3. Lopuksi: miten se liittyy [projektiimme/kontekstiimme]

Käytä esimerkkejä. Vältä jargonia ilman selitystä.
```

---

## 7. KRIITTINEN ARVIOINTI (Critical Review)

```
Arvioi tämä [koodi/teksti/suunnitelma] kriittisesti:

[materiaali]

Anna arvio kolmessa kategoriassa:
VAHVUUDET: Mikä toimii ja miksi
HEIKKOUDET: Mikä ei toimi ja miksi
PARANNUKSET: Mitä tekisit eri tavalla ja miten

Ole konkreettinen. Ei yleisiä lausumia.
```

---

## 8. SKENAARIOANALYYSI (Scenario Analysis)

```
Jos [muutos tai päätös], mitä tapahtuu?

Analysoi kolme skenaariota:
OPTIMISTINEN: Kaikki menee hyvin. Mitä saavutetaan?
REALISTINEN: Normaali tapahtumakulku. Mitä odottaa?
PESSIMISTINEN: Asiat menevät pieleen. Mitä voi tapahtua?

Jokaiselle skenaariolle:
- Todennäköisyys (%)
- Seuraukset
- Miten varautua
```

---

## 9. AGENTDIR-SPESIFINEN: KOMPONENTTIANALYYSI

```
Analysoi [komponentti] AgentDir 3.5 -kontekstissa:

1. TEHTÄVÄ: Mitä tämän komponentin pitää tehdä?
2. RAJAPINTA: Miten muut komponentit käyttävät tätä?
3. RIIPPUVUUDET: Mistä tämä riippuu?
4. TESTATTAVUUS: Miten tämä testataan?
5. PULLONKAULAT: Missä tämä voi hidastua tai kaatua?
6. YHTEYS TIETEESEEN: Mihin MemMachine/A-RAG -periaatteeseen liittyy?
```

---

## 10. VALMIIN TULOKSEN VALIDOINTI

```
Tarkista onko tämä [koodi/dokumentti/suunnitelma] valmis:

[materiaali]

Tarkistukset:
□ Tekee mitä sen pitää tehdä?
□ On testattavissa?
□ Noudattaa projektin tyylisääntöjä?
□ Ei riko olemassa olevaa toiminnallisuutta?
□ Dokumentoitu riittävästi?
□ Läpäisee constraints.md säännöt?

Anna: VALMIS / EI VALMIS + lista puuttuvista asioista
```

---

## PIKAKEHOTTEET (kopioi suoraan)

```
"Kysy minulta tarkentavia kysymyksiä ennen kuin aloitat."

"Kirjoita hypoteesi ennen koodia."

"Tee ensin testi, sitten toteutus."

"Selitä päätöksesi ennen kuin toteutat sen."

"Mikä on yksinkertaisin ratkaisu joka toimii?"

"Mitä voin jättää pois ilman että toiminnallisuus kärsii?"

"Missä tämä voi mennä pieleen?"
```
