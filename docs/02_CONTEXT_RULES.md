# 02_CONTEXT_RULES.md — Kontekstinhallinta
# Säännöt siitä mitä tietoa tekoäly käyttää ja mistä se hakee sen.
# Estää hallusinoinnin ja varmistaa, että vastaukset perustuvat faktaan.

---

## KONTEKSTIN HIERARKIA

Tekoäly käyttää tietoa TÄSSÄ prioriteettijärjestyksessä:

```
PRIORITEETTI 1 (korkein): !_SOVEREIGN.md
  → Globaalit säännöt ja eettiset rajat. Ei koskaan ohiteta.

PRIORITEETTI 2: wiki/log.md
  → Aiemmat päätökset ja kausaaliloki tästä sessiosta.

PRIORITEETTI 3: wiki/index.md
  → Projektin tietopankki ja rakenne.

PRIORITEETTI 4: .agentdir.md (paikalliset ankkurit)
  → Kansiokohtainen konteksti ja säännöt.

PRIORITEETTI 5: /raw -kansion tiedostot
  → Käyttäjän syöttämä data ja materiaalit.

PRIORITEETTI 6 (alin): Mallin oma koulutusdata
  → Käytetään VAIN jos muuta ei ole saatavilla.
  → MERKITÄÄN aina: "Tämä perustuu yleistietoon, ei projektin dataan."
```

---

## KONTEKSTIN KÄYTTÖSÄÄNNÖT

### Sääntö 1: Käytä vain annettua materiaalia
```
OIKEIN:  "wiki/index.md mukaan projektin pääkomponentit ovat..."
VÄÄRIN:  "Yleensä tällaisissa projekteissa käytetään..."
         (ilman viitettä projektin omaan dataan)
```

### Sääntö 2: Ilmoita tiedon lähde
```
Jokaisessa vastauksessa jossa käytetään kontekstia:
→ Mainitse mistä tiedosto tieto tuli
→ Esim: "Perustuen /wiki/auth.md riviin 14..."
```

### Sääntö 3: Tunnista tiedon aukot
```
Jos tietoa ei ole:
→ SAY: "Tätä ei löydy projektin dokumentaatiosta. Tarvitaan lisätietoa:"
→ KYSY tarkentava kysymys
→ ÄLÄ keksi vastausta
```

### Sääntö 4: Ristiriitainen tieto
```
Jos eri lähteissä on ristiriita:
→ Ilmoita ristiriidasta
→ Kerro mitä kumpikin lähde sanoo
→ Kysy käyttäjältä kumpi on oikein
→ ÄLÄ valitse itse
```

---

## KONTEKSTIN SYÖTTÄMINEN (käyttäjälle)

### Paras tapa antaa konteksti tekoälylle:

```markdown
## PROJEKTIN KONTEKSTI
- Projekti: AgentDir 3.5
- Vaihe: [esim. "Phase 2, memmachine.py toteutus"]
- Aiempi päätös: [esim. "Päätettiin käyttää subprocess eikä docker"]
- Rajoitteet: [esim. "Ei ulkoisia kirjastoja paitsi openai"]

## RELEVANTTI KOODI / DATA
[liitä tähän relevantti koodinpätkä tai data]

## TEHTÄVÄ
[mitä halutaan tehtäväksi]
```

---

## FEW-SHOT KONTEKSTI -MALLI

Kun haluat tekoälyn jatkavan tiettyä tyyliä tai rakennetta:

```
Tässä on esimerkki nykyisestä koodistamme:

[ESIMERKKI 1]
class PolicyEngine:
    def validate(self, task: str) -> bool:
        # Suomenkieliset kommentit
        # Yksinkertainen, testattava
        ...

Kirjoita sama tyyli uudelle komponentille: [MemMachine]
```

---

## KONTEKSTIN RAJOITTAMINEN

Kun haluat estää tekoälyä käyttämästä omaa tietokantaansa:

```
KÄYTÄ VAIN tässä annettua materiaalia.
ÄLÄ viittaa yleisiin parhaisiin käytäntöihin tai ulkoisiin esimerkkeihin.
Jos tarvittavaa tietoa ei ole annetussa materiaalissa, ilmoita se.
```

---

## SESSIOKONTEKSTIN YLLÄPITO

Pitkissä sessioissa käytä tätä muistiohjausta:

```
Muista koko session ajan:
- Projekti: AgentDir 3.5
- Kieli: Python 3.11
- Tyyli: Karpathy-kuri (kirurgiset muutokset)
- Ei ulkoisia API-kutsuja sandboxissa
- Suomenkieliset kommentit, englanninkielinen koodi

Edellinen vaihe: [mitä tehtiin]
Seuraava vaihe: [mitä tehdään nyt]
```
