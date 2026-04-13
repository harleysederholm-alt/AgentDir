# 03_REASONING_PROTOCOL.md — Päättelyprotokolla
# Miten tekoäly ajattelee vaihe vaiheelta ennen kuin antaa vastauksen.
# Käytä monimutkaisten ongelmien, arkkitehtuuripäätösten ja bugien kanssa.

---

## PERUSPROTOKOLLA: CHAIN OF THOUGHT

Aina ennen vastausta tekoäly tekee tämän:

```
VAIHE 1 — YMMÄRRÄ
  Mitä täsmälleen pyydetään?
  Mitkä ovat piilossa olevat vaatimukset?
  Mitä voi mennä pieleen?

VAIHE 2 — KERÄÄ
  Mitä tietoa tarvitaan?
  Mitä puuttuu?
  Mitä aiempaa kontekstia on relevanttia?

VAIHE 3 — SUUNNITTELE
  Mitkä ovat vaihtoehdot?
  Mikä on yksinkertaisin toimiva ratkaisu?
  Mitä sivuvaikutuksia on?

VAIHE 4 — TOTEUTA
  Kirurginen toteutus.
  Ei turhia lisäyksiä.

VAIHE 5 — TARKISTA
  Vastaako ratkaisu alkuperäiseen pyyntöön?
  Onko testit kirjoitettu?
  Onko dokumentoitu?
```

---

## KOODAUKSEN PÄÄTTELYPROTOKOLLA

Käytä tätä aina kun kirjoitat koodia:

```
Ennen koodin kirjoitusta vastaa näihin:

1. MITÄ tämän funktion/luokan pitää tehdä?
   → Yksi lause, ei enempää.

2. MITEN se tiedetään että se toimii?
   → Kirjoita testi ENNEN koodia.

3. MITÄ riippuvuuksia tarvitaan?
   → Lista, mahdollisimman lyhyt.

4. MITÄ voi mennä pieleen?
   → Virhetilanteet, edge caset.

5. MITEN virhetilanteet käsitellään?
   → raise, return None, log — valitse yksi ja pysy siinä.

Vasta näiden jälkeen: kirjoita koodi.
```

---

## TREE OF THOUGHTS — VAIHTOEHTOJEN VERTAILU

Käytä kun on useita ratkaisuvaihtoehtoja:

```
Tutki KOLME eri lähestymistapaa:

VAIHTOEHTO A: [nimi]
  Plussat: ...
  Miinukset: ...
  Sopii kun: ...

VAIHTOEHTO B: [nimi]
  Plussat: ...
  Miinukset: ...
  Sopii kun: ...

VAIHTOEHTO C: [nimi]
  Plussat: ...
  Miinukset: ...
  Sopii kun: ...

SUOSITUS: [valitse yksi ja perustele]
SYYT: [miksi tämä on parempi kuin muut]
```

---

## ARKKITEHTUURIPÄÄTÖSTEN PROTOKOLLA

Kun tehdään isoja rakenteellisia päätöksiä:

```
PÄÄTÖSKEHYS:

1. ONGELMA
   Mitä ongelmaa ratkaistaan? (1-2 lausetta)

2. VAATIMUKSET
   Pakollinen (Must): ...
   Toivottu (Should): ...
   Ei nyt (Won't): ...

3. RAJOITTEET
   Tekninen: (esim. "ei ulkoisia kirjastoja")
   Aika: (esim. "yhdessä sessiossa toteutettava")
   Osaaminen: (esim. "tiimi tuntee Python mutta ei Rust")

4. RATKAISU
   Valittu lähestymistapa ja syyt.

5. KOMPROMISSIT
   Mitä luovuttiin? Miksi se on hyväksyttävää?

6. UUDELLEENARVIOINTI
   Milloin tämä päätös pitää tarkistaa uudelleen?
```

---

## BUGIN ANALYSOINNIN PROTOKOLLA (CAUSAL ENGINE)

```
BUG REPORT:
[virheviesti tai kuvailu]

KAUSAALINEN ANALYYSI:

HAVAINTO: Mitä konkreettisesti tapahtuu?
ODOTETTU: Mitä pitäisi tapahtua?
EROAVUUS: Mikä on ero näiden välillä?

HYPOTEESI 1: [mahdollinen syy]
  Todennäköisyys: korkea / keskisuuri / matala
  Testi: miten varmennetaan?

HYPOTEESI 2: [vaihtoehtoinen syy]
  Todennäköisyys: korkea / keskisuuri / matala
  Testi: miten varmennetaan?

VALITTU KORJAUS: [perustuen testiin]
SIVUVAIKUTUKSET: [mitä muuta voi muuttua]
TESTI: [miten varmistetaan että bugi on korjattu]
```

---

## ITSEKRITIIKKI — SELF-REFLECTION PROTOKOLLA

Käytä tätä kun vastaus on "melkein valmis":

```
Tarkista vastauksesi ennen lopullista tulosta:

□ Vastaako tämä alkuperäiseen kysymykseen?
□ Onko mitään yksinkertaisempaa tapaa?
□ Onko virheitä tai epätarkkuuksia?
□ Onko kaikki väitteet tuettuja?
□ Ymmärtääkö kohderyhmä tämän?
□ Puuttuuko jotain tärkeää?

Jos jokin kohta on "ei" → korjaa ennen lähettämistä.
```

---

## NOPEUSASETUKSET

| Tilanne | Protokolla |
|---|---|
| Yksinkertainen kysymys | Suora vastaus, ei protokollaa |
| Koodi alle 20 riviä | Chain of Thought lyhyesti |
| Arkkitehtuuri tai iso muutos | Kaikki vaiheet täysin |
| Bugi tai virhetilanne | Causal Engine protokolla |
| Useita vaihtoehtoja | Tree of Thoughts |
