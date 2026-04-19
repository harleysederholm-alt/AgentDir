# 04_OUTPUT_FORMATS.md — Vastausten Muotoilu
# Määrittelee miltä tekoälyn vastauksen pitää näyttää eri tilanteissa.
# Käytä kun haluat tietyn rakenteen tai formaatin.

---

## KOODIN MUOTOILU

### Täysi tiedosto
```
Käytä kun: luodaan uusi tiedosto tai kokonaan uusi komponentti

Rakenne:
```python
#!/usr/bin/env python3
"""
[Tiedoston nimi] — [Lyhyt kuvaus]
[Tieteellinen viite jos relevantti]
"""
# [Suomenkielinen kommentti miksi tämä tiedosto on olemassa]

# --- IMPORTS ---
import [stdlib ensin]
from [third-party] import [...]

# --- CONSTANTS ---
[ISOT_KIRJAIMET = "arvo"]

# --- CLASSES / FUNCTIONS ---
class [Nimi]:
    """
    [Mitä tämä luokka tekee]
    [Miksi se on rakennettu näin]
    """
    def method(self, param: str) -> dict:
        """[Mitä tämä metodi tekee]"""
        # [Kommentti kriittisistä kohdista]
        ...
```
```

### Koodinpätkä (patch)
```
Käytä kun: muutetaan olemassa olevaa tiedostoa

Rakenne:
MUUTOS TIEDOSTOON: [tiedostonimi]
RIVI: [rivinumero tai funktionimi]

ENNEN:
```python
[vanha koodi]
```

JÄLKEEN:
```python
[uusi koodi]
```

SYYT: [miksi tämä muutos tehdään]
```

### Testi-muoto
```python
# test_[komponentti].py
import pytest
import sys; sys.path.insert(0, "workspace")
from [komponentti] import [Luokka]

class Test[Luokka]:
    def setup_method(self):
        """Alustus joka testille."""
        self.obj = [Luokka]()

    def test_[onnistuva_tilanne](self):
        """[Mitä testataan ja miksi]"""
        result = self.obj.method("validi_syöte")
        assert result["success"] is True

    def test_[virhetilanne](self):
        """[Mitä virhetilannetta testataan]"""
        with pytest.raises([Virhe]):
            self.obj.method("viallinen_syöte")
```

---

## DOKUMENTAATION MUOTOILU

### README-rakenne
```markdown
# [Projektin nimi]

[Yksi lause: mitä tämä tekee ja kenelle]

## Nopea aloitus

```bash
pip install -r requirements.txt
python cli.py init
python cli.py run "tehtävä"
```

## Mitä tämä ratkaisee

[Ongelma] → [Ratkaisu] → [Hyöty]

## Arkkitehtuuri

[Lyhyt kaavio tai selitys]

## Komponentit

| Tiedosto | Tehtävä |
|---|---|
| ... | ... |

## Tieteellinen pohja

[Viitteet jos relevantti]
```

### .agentdir.md ankkuri -rakenne
```markdown
# .agentdir.md — [Kansion nimi]

## TARKOITUS
[Mitä tämä kansio tekee — yksi virke]

## KONTEKSTI
- Tärkeimmät tiedostot: [lista]
- Riippuu: [muut kansiot/komponentit]
- Vaikuttaa: [mitä käyttää tätä]

## OHJEET AGENTILLE
- Sandbox: [pakollinen / valinnainen]
- Prioriteetti: [korkea / normaali / matala]
- Muutos vaatii: [testit / review / molemmat]

## KIELLETTYÄ TÄSSÄ KANSIOSSA
- [...]
```

---

## ANALYYSIN MUOTOILU

### Tekninen analyysi
```markdown
## Analyysi: [Aihe]

### Tilanne nyt
[Miten asiat ovat]

### Ongelma
[Mikä ei toimi tai mikä voisi olla paremmin]

### Vaihtoehdot
1. **[Vaihtoehto A]** — [lyhyt kuvaus]
   - Plussat: ...
   - Miinukset: ...

2. **[Vaihtoehto B]** — [lyhyt kuvaus]
   - Plussat: ...
   - Miinukset: ...

### Suositus
**[Valinta]** koska [perustelu].

### Seuraavat askeleet
1. [ ] [toimenpide]
2. [ ] [toimenpide]
```

### Benchmark-raportti
```markdown
## Benchmark: [Komponentti] — [Päivämäärä]

| Testi | Tulos | Vertailu | Status |
|---|---|---|---|
| [testi] | [ms/arvo] | [baseline] | ✅/❌ |

### Johtopäätökset
[Mitä tulokset tarkoittavat]

### Jatkotoimenpiteet
[Jos jotain pitää optimoida]
```

---

## AGENT PRINT -FORMAATTI

```markdown
# Agent Print — [ID]

| Kenttä | Arvo |
|---|---|
| Tehtävä | [task] |
| Malli | [model] |
| Moodi | omninode / sovereign |
| Tulos | ✅ ONNISTUI / ❌ EPÄONNISTUI |
| Sandbox verifioitu | Kyllä / Ei |
| EU AI Act Art.13 | ✅ |
| Token-säästö | [%] |
| Kausaaliloki | wiki/log.md |
| Aikaleima | [ISO 8601] |

## Mitä tehtiin
[Lyhyt kuvaus toimenpiteistä]

## Verifiointi
[Testien tulokset]

## Sivuvaikutukset
[Mitä muuttui projektin tilassa]
```

---

## VIRHEILMOITUSTEN MUOTOILU

```
VIRHE: [Lyhyt kuvaus mitä meni pieleen]

SYYT:
  1. [Todennäköisin syy]
  2. [Vaihtoehtoinen syy]

KORJAUS:
  [Konkreettinen toimenpide]

ESTÄMINEN JATKOSSA:
  [Miten sama virhe estetään]
```

---

## PITUUSOHJEET

| Tyyppi | Pituus |
|---|---|
| Lyhyt vastaus | 1-3 lausetta |
| Selitys | 1-2 kappaletta |
| Kooditiedosto | Niin lyhyt kuin mahdollista toimivana |
| Arkkitehtuuripäätös | Max 1 sivu |
| README | Max 2 sivua |
| Tutkimuspaperi | Täyspitkä, ei rajoitusta |
