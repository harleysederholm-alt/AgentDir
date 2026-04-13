# 05_CONSTRAINTS.md — Rajoitteet ja Kiellot
# Nämä säännöt ovat ABSOLUUTTISIA. Ei poikkeuksia.
# PolicyEngine tarkistaa nämä ennen jokaista suoritusta.

---

## TASON 1: EHDOTTOMAT KIELLOT (ei koskaan)

```
❌ EI koskaan:
  - rm -rf tai vastaava rekursiivinen poisto
  - Tiedostojen muokkaus /wiki tai /outputs ulkopuolella ilman COMMIT-lupaa
  - Verkkokutsut sandboxista (--network none)
  - Salasanojen, API-avainten tai tokenien lokittaminen
  - eval() tai exec() käyttäjän syötteelle ilman validointia
  - Ohjelmiston ajaminen root/admin -oikeuksilla
  - Kirjoittaminen !_SOVEREIGN.md -tiedostoon ilman L1-lupaa
  - Oikealla datalla testaaminen (käytä mock/fixture)
```

---

## TASON 2: KOODAUSKIELLOT (Karpathy-säännöt)

```
❌ EI koskaan koodissa:
  - Refaktoroi tiedostoja joita ei pyydetty muuttamaan
  - Lisää "paranteluja" joita ei pyydetty
  - Käytä globaaleja muuttujia tilaan
  - Kirjoita kommentteja jotka selittävät MITÄ (sen näkee koodista)
    → Kirjoita kommentteja jotka selittävät MIKSI
  - Piilota virheitä try/except ilman lokitusta
  - Hard-code polkuja tai URL-osoitteita ilman ympäristömuuttujaa
  - Importoi kirjastoja joita ei ole requirements.txt:ssä
  - Kirjoita koodia jota ei voi testata

❌ EI koskaan projektissa:
  - Siirrä pysyvää dataa /raw → /wiki ilman verifiointia
  - Commitoi STM-muistia LTM:ään ilman testien läpäisyä
  - Ohita policy.validate() ennen suoritusta
  - Ohita causal.write_hypothesis() ennen koodinajoa
```

---

## TASON 3: KOMMUNIKAATIOKIELLOT

```
❌ EI koskaan vastauksissa:
  - Keksi faktoja joita ei ole annetussa kontekstissa
    → SAY: "Tätä tietoa ei löydy annetusta materiaalista"
  - Väitä varmuutta epävarmasta asiasta
    → SAY: "Tämä on arvio, ei vahvistettu fakta"
  - Lupaa toimivuutta ilman testiä
    → SAY: "Tämä on toteutus — testaa ennen kuin luotat siihen"
  - Käytä passiivia vastuun välttämiseen
    → SAY: "Minä teen X" ei "X tehdään"
  - Sano "helppo" tai "yksinkertainen" ilman perustelua
```

---

## TASON 4: PROJEKTISPESIFIT KIELLOT

```
❌ EI AgentDir 3.5 -projektissa:
  - Ulkoiset API-kutsut joita ei ole model_router.py:ssä
  - Docker-in-Docker ilman erillistä lupaa
  - Tiedostot joiden nimi alkaa numerolla (paitsi wiki/log ja ankkurit)
  - Yli 300 rivin Python-tiedostot (jaa osiin jos ylitetään)
  - Funktiot joilla on yli 3 parametria ilman dataclass/dict
  - Testit jotka riippuvat toisistaan (jokainen testi on itsenäinen)
  - Koodia ilman type hints Python 3.10+ -projekteissa
```

---

## KIELTOJA OHITTAVAT ERIKOISTAPAUKSET

Nämä vaativat AINA eksplisiittisen luvan käyttäjältä:

```
⚠️ Vaatii vahvistuksen:
  - Tiedoston poistaminen (ei edes tyhjää)
  - Muutos !_SOVEREIGN.md -tiedostoon
  - Uuden ulkoisen kirjaston lisääminen
  - Tietokannan skeeman muutos
  - Muutos joka vaikuttaa useampaan kuin yhteen moduuliin
  - Tuotantodatan käsittely (ei koskaan testissä)
```

Pyydä vahvistus näin:
```
VAHVISTUS TARVITAAN:
Aion tehdä [toimenpide] koska [syy].
Tämä vaikuttaa [mitä].
Hyväksytkö? [kyllä/ei]
```

---

## RAJOITTEIDEN PRIORITEETTIJÄRJESTYS

Jos kaksi rajoitetta on ristiriidassa:

```
1. Turvallisuus > kaikki muu
2. Olemassa olevan datan suojaus > uuden datan luominen
3. Testattavuus > nopeus
4. Selkeys > nerokkuus
5. Yksinkertaisuus > kattavuus
```

---

## RAJOITTEIDEN TARKISTUSLISTA (ennen jokaista suoritusta)

```
□ Onko tehtävä läpäissyt policy.validate()?
□ Onko hypoteesi kirjoitettu wiki/log.md:hen?
□ Toimiiko sandbox ilman verkkoyhteyttä?
□ Muutetaanko vain pyydettyjä tiedostoja?
□ Onko testi kirjoitettu ennen koodia?
□ Lokitetaanko virheet ilman arkaluonteista dataa?
□ Onko kaikki uudet riippuvuudet requirements.txt:ssä?

Jos jokin on "ei" → pysähdy ja korjaa ennen jatkamista.
```
