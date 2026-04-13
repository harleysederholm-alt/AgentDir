# 08_FEW_SHOT_EXAMPLES.md — Konkreettiset Esimerkit
# Näyttää tekoälylle täsmälleen millaisia vastauksia halutaan.
# Käytä näitä mallina — kopioi rakenne, vaihda sisältö.

---

## MITÄ FEW-SHOT ON

```
Anna tekoälylle 2-3 esimerkkiä halutusta vastauksesta.
Se oppii tyylisi nopeammin kuin mistään säännöstä.

Muoto: "Tässä on esimerkki hyvästä [vastauksesta]:
        [esimerkki]
        Tee nyt sama tälle: [uusi syöte]"
```

---

## ESIMERKKI 1: HYVÄ PYTHON-KOODI

### Mitä halutaan
```python
# ✅ HYVÄ — näin kirjoitamme koodia

class SovereignSandbox:
    """
    Eristetty suoritusympäristö agenttien koodille.
    
    Perustuu Safe YOLO -periaatteeseen: kaikki epäilyttävä
    ajetaan ensin tässä ennen kuin se koskee oikeaa dataa.
    """
    
    DEFAULT_TIMEOUT = 30  # sekuntia

    def execute(self, code: str, timeout: int = DEFAULT_TIMEOUT) -> dict:
        """
        Ajaa Python-koodin eristetyssä prosessissa.
        
        Args:
            code: Ajettava Python-koodi
            timeout: Maksimiaika sekunteina
            
        Returns:
            dict: {success: bool, stdout: str, stderr: str}
        """
        # Kirjoita koodi väliaikaiseen tiedostoon atomisesti
        with tempfile.NamedTemporaryFile(
            mode='w', suffix='.py', delete=False
        ) as f:
            f.write(code)
            tmp_path = f.name

        try:
            result = subprocess.run(
                ["python", tmp_path],
                capture_output=True,
                text=True,
                timeout=timeout,
                env={"PATH": os.environ.get("PATH", "")},  # Minimiympäristö
            )
            return {
                "success": result.returncode == 0,
                "stdout": result.stdout,
                "stderr": result.stderr,
            }
        except subprocess.TimeoutExpired:
            # Timeout ei ole virhe — se on odotettu tilanne
            return {"success": False, "stderr": f"TIMEOUT ({timeout}s)", "stdout": ""}
        finally:
            os.unlink(tmp_path)  # Siivoa aina
```

### Mitä ei haluta
```python
# ❌ HUONO — näin ei kirjoiteta

def run(code):
    # ajaa koodin
    try:
        exec(code)  # VAARALLINEN — ei eristystä
        return True
    except:
        return False  # Virhe katoaa
```

---

## ESIMERKKI 2: HYVÄ KOMMENTTI JA DOKUMENTAATIO

### Mitä halutaan
```python
# ✅ HYVÄ kommentti

# Odotetaan 1s ennen laskentaa, koska iPhonen NPU ylikuumenee
# noin 45s jatkuvan käytön jälkeen. Tämä throttling on
# havaittu A15-siruilla mutta ei M1-siruilla.
time.sleep(1.0)
```

### Mitä ei haluta
```python
# ❌ HUONO kommentti — selittää MITÄ, ei MIKSI

# Odotetaan 1 sekunti
time.sleep(1.0)
```

---

## ESIMERKKI 3: HYVÄ TESTI

### Mitä halutaan
```python
# ✅ HYVÄ testi

class TestPolicyEngine:
    """Testaa että policy-gate estää oikeat asiat."""
    
    def setup_method(self):
        self.policy = PolicyEngine()

    def test_allows_safe_analysis_task(self):
        """Normaali analyysitehtävä pitää päästä läpi."""
        assert self.policy.validate("analysoi data.csv") is True

    def test_blocks_recursive_delete(self):
        """rm -rf pitää estää riippumatta kontekstista."""
        with pytest.raises(PermissionError) as exc_info:
            self.policy.validate("suorita rm -rf /tmp/test")
        assert "rm -rf" in str(exc_info.value)

    def test_blocks_even_in_innocent_context(self):
        """Kielletty kuvio estetään vaikka muuten teksti on viaton."""
        with pytest.raises(PermissionError):
            self.policy.validate(
                "kirjoita dokumentaatio: 'voit ajaa rm -rf poistoon'"
            )
```

### Mitä ei haluta
```python
# ❌ HUONO testi

def test_policy():
    p = PolicyEngine()
    # Testaa jotain
    result = p.validate("testi")
    assert result  # Mitä tämä testaa?
```

---

## ESIMERKKI 4: HYVÄ .agentdir.md ANKKURI

### Mitä halutaan
```markdown
<!-- ✅ HYVÄ ankkuri -->

# .agentdir.md — workspace/

## TARKOITUS
Sisältää kaikki AgentDir 3.5:n ydinkomponentit.
Tämä on projektin "moottori" — muuta vain jos tiedät mitä teet.

## KONTEKSTI
- Tärkeimmät tiedostot: policy.py, sandbox.py, memmachine.py
- Riippuu: Python 3.11, openai-kirjasto (valinnainen)
- Käyttää tätä: orchestrator.py, cli.py

## OHJEET AGENTILLE
- Sandbox: PAKOLLINEN kaikelle koodinsuoritukselle
- Prioriteetti: KORKEA — muutokset vaikuttavat koko järjestelmään
- Muutos vaatii: testit + kausaliloki + agent print

## KIELLETTYÄ TÄSSÄ KANSIOSSA
- Ulkoiset verkkoyhtedet suoraan (käytä model_router.py)
- Globaalit muuttujat tilan tallentamiseen
- Testit jotka kirjoittavat /raw tai /outputs ulkopuolelle
```

### Mitä ei haluta
```markdown
<!-- ❌ HUONO ankkuri — liian epäselvä -->

# workspace

tässä on koodia
```

---

## ESIMERKKI 5: HYVÄ ITEROINTIKESKUSTELU

### Tilanne: koodi toimii mutta on hidas

```
KÄYTTÄJÄ:
Tämä RAG-haku on hidas isoilla datasetteillä.
Paranna suorituskykyä VAIN query()-metodissa.
Pidä rakenne samana.

TEKOÄLY (hyvä vastaus):
Ongelma: Nykyinen toteutus iteroi kaikki dokumentit O(n).
Ratkaisu: Lisätään esifiltteröinti ennen pistolaskentaa.

MUUTOS VAIN query()-metodiin:

[ennen]
def query(self, query: str, top_k: int = 3) -> list:
    results = []
    query_terms = set(query.lower().split())
    for name, content in self._index.items():
        ...

[jälkeen]
def query(self, query: str, top_k: int = 3) -> list:
    query_terms = set(query.lower().split())
    # Esifiltteröinti: hylkää dokumentit joissa ei yhtäkään termiä
    # O(n) → O(k) missä k = dokumentit joissa on osuma
    candidates = {
        name: content 
        for name, content in self._index.items()
        if query_terms & set(content.lower().split())
    }
    ...

Testi:
def test_query_performance():
    idx = KnowledgeIndex()
    idx._index = {f"doc_{i}": f"content {i}" for i in range(10000)}
    t = time.perf_counter()
    idx.query("content 9999")
    assert time.perf_counter() - t < 0.1  # alle 100ms

Muuta ei muutettu.
```

---

## ESIMERKKI 6: HYVÄ VIRHEVIESTI KÄYTTÄJÄLLE

### Mitä halutaan
```
❌ VIRHE: Policy gate esti suorituksen

SYYT:
  Tehtävä sisälsi kielletyn kuvion: "rm -rf"
  Sääntö: 05_CONSTRAINTS.md, Taso 1

MITÄ VOIT TEHDÄ:
  1. Muotoile tehtävä uudelleen ilman poistoa
  2. Jos poisto on välttämätöntä, pyydä L1-lupa !_SOVEREIGN.md:stä
  3. Katso sallitut toiminnot: 05_CONSTRAINTS.md

KAUSAALILOKI: wiki/log.md (viimeisin merkintä)
```

### Mitä ei haluta
```
Error: Permission denied
```

---

## MITEN KÄYTÄT NÄITÄ

```
1. Valitse esimerkki joka vastaa tilannettasi
2. Kopioi se kehotteen alkuun
3. Lisää: "Kirjoita samalla tyylillä: [uusi tehtävä]"

Esimerkki:
"Tässä on esimerkki hyvästä Python-komponentista meidän
 projektissamme: [kopioi esimerkki 1].
 Kirjoita sama tyyli OmniNode-luokalle."
```
