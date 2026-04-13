# 06_ITERATION_GUIDE.md — Iterointi ja Parannus
# Miten parannetaan tulosta ilman alusta aloittamista.
# Tekoäly on väsymätön iteroija — käytä tätä hyväksi.

---

## PERUSPERIAATE

```
Älä aloita alusta.
Iteroi nykyistä.

"Hyvä, mutta..." on arvokkaampi kuin "Ei hyvä, tee uudelleen."
```

---

## ITEROINNIN TASOT

### Taso 1: Mikrotason iteraatio (yksittäinen kohta)
```
Käytä kun: yksi asia on epäselvä tai puuttuu

Muoto:
"Hyvä. Kohdassa [X] tee [muutos]:
 - [tarkka muutos]
 - Pidä kaikki muu samana."
```

### Taso 2: Makrotason iteraatio (rakenne tai lähestymistapa)
```
Käytä kun: suunta on oikea mutta toteutus puuttuu

Muoto:
"Lähestymistapa on oikea. Toteutuksessa:
 - Vaihda [A] → [B] koska [syy]
 - Lisää [C] koska [syy]
 - Poista [D] koska [syy]"
```

### Taso 3: Täysi uudelleenkirjoitus (viimeinen keino)
```
Käytä vain kun: perusoletus oli väärä

Muoto:
"Oletus oli väärä. Oikea oletus on [X].
 Kirjoita [komponentti] uudelleen tästä lähtökohdasta:
 [uusi lähtökohta]"
```

---

## KOODIN ITEROINTIKEHOTTEET

### Paranna suorituskykyä
```
Tämä koodi toimii mutta on hidas [tilanteessa X].
Optimoi VAIN [funktio/metodi] niin että:
- Nopeus paranee [tilanteessa X]
- Toiminnallisuus pysyy täsmälleen samana
- Testit läpäistään edelleen
Älä muuta muuta.
```

### Paranna luettavuutta
```
Tämä toimii mutta on vaikea lukea.
Refaktoroi VAIN luettavuutta:
- Paranna muuttujien nimiä
- Lisää selittävät kommentit kriittisiin kohtiin
- Jaa yli 20-rivinen funktio osiin jos selkeyttää
Älä muuta logiikkaa tai rajapintaa.
```

### Lisää virheenkäsittely
```
Tässä koodissa ei käsitellä virheitä.
Lisää virheenkäsittely NÄIHIN kohtiin:
- [tilanne 1]: [mitä pitäisi tapahtua]
- [tilanne 2]: [mitä pitäisi tapahtua]
Käytä [raise / return None / logging.error] johdonmukaisesti.
```

### Lisää tyyppivihjeet
```
Lisää type hints KAIKKIIN funktioihin tässä tiedostossa.
Käytä Python 3.10+ syntaksia (X | Y eikä Union[X, Y]).
Älä muuta logiikkaa.
```

---

## TEKSTIN ITEROINTIKEHOTTEET

### Tee tiiviimmäksi
```
Tämä teksti on [X sanaa]. Tee siitä [Y sanaa].
Pidä:
- [tärkein pointti]
- [tärkein esimerkki]
Poista:
- Toistot
- Yleiset lausahdukset jotka eivät lisää arvoa
```

### Muuta äänensävyä
```
Muuta äänensävy [teknisestä] → [käytännönläheiseksi].
Kohdeyleisö muuttuu: [kehittäjä] → [liiketoimintapäättäjä].
Pidä kaikki faktat samana, muuta vain esitystapa.
```

### Lisää esimerkkejä
```
Tämä selitys on liian abstrakti.
Lisää [2-3] konkreettista esimerkkiä kohtaan [X].
Esimerkkien pitää olla [teknisiä/arkisia/numeroita].
```

---

## PROGRESSIIVINEN TARKENNUS

Käytä kun et osaa määritellä tavoitetta täsmällisesti:

```
VAIHE 1: Pyydä luonnos
"Tee alustava versio [X]. Fokus laajuuteen, ei täydellisyyteen."

VAIHE 2: Arvioi ja tarkenna
"Hyvä alku. Kohdat [A, B, C] ovat oikein.
 Kohdassa [D] tarvitaan [muutos].
 Kohdassa [E] suunta on väärä koska [syy]."

VAIHE 3: Viimeistele
"Hyvä. Tee vielä:
 - [pieni muutos 1]
 - [pieni muutos 2]
 Sitten se on valmis."
```

---

## RINNAKKAISVERTAILU

Kun haluat vertailla kahta lähestymistapaa:

```
Toteuta SAMA [funktionaliteetti] kahdella tavalla:

VERSIO A: [lähestymistapa A]
VERSIO B: [lähestymistapa B]

Kerro molemmista:
- Suorituskyky [tilanteessa X]
- Koodin määrä (rivit)
- Testattavuus
- Ylläpidettävyys

Suosittele yksi ja perustele.
```

---

## ITEROINNIN PYSÄYTTÄMINEN

Käytä kun lopputulos on saavutettu:

```
✅ Tämä on valmis. Tallenna tulos.
Seuraava tehtävä: [...]
```

Tai kun iteraatio ei enää paranna:
```
Tämä on riittävän hyvä tähän tarkoitukseen.
Paremman ratkaisun tekeminen vaatisi [X] eikä se ole
priorisoitua nyt. Jatketaan eteenpäin.
```
