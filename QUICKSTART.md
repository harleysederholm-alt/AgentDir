<div align="center">
  <img src="docs/agentdir_logo_v3.png" alt="AgentDir Logo" width="250"/>
  <h1>⚡ AgentDir: Pika-aloitus</h1>
  <p>Pysäytä koodailu. Aloita johtaminen. <strong>3 minuuttia asennuksesta autonomiaan.</strong></p>
</div>

---

## 1. Asennus (Windows)

AgentDir pyörii täysin lokaalisti sinun koneellasi. Pilveen ei lähde tavun vertaa dataa.

Avaa **PowerShell** ja aja 2 komentoa:

```powershell
git clone https://github.com/harleysederholm-alt/AgentDir.git
cd agentdir
Set-ExecutionPolicy -Scope Process Bypass; .\install.ps1
```
*(Asennin huolehtii riippuvuuksista automaattisesti. Oletamme, että [Ollama](https://ollama.com/) on jo laitteellasi.)*

---

## 2. Käynnistys

Herätä koko ekosysteemi (Käyttöliittymä, Agentit, RAG-muisti ja Turvahiekkalaatikko) yhdellä komennolla:

```powershell
.\launch_sovereign.ps1
```

Eteesi aukeaa **Sovereign CLI** ja selainpohjainen **Dashboard**. Molemmat kuuntelevat sinua 24/7.

---

## 3. Ensimmäinen tehtävä: Päästä Agentti irti!

AgentDir tekee tavallisesta tiedostojärjestelmästäsi älykkään.

1. Etsi kansio `Inbox/` (Luodaan automaattisesti asennuksessa).
2. Luo sinne tekstitiedosto, esim. `laskukone.txt`, johon kirjoitat:
   > *"Tee minulle Python-skripti, joka laskee fibonaccin lukusarjan sataan asti."*
3. **Seuraa taikaa!** 
   - Agentti **herää** alle 50 millisekunnissa tiedoston havaittuaan.
   - Kirjoittaa koodin.
   - **Testaa** sen eristetyssä Windows Sandboxissa (.wsb).
   - Tallentaa valmiin ja testatun koodin `Outbox/` -kansioon!

---

## Tärkeimmät komennot (Sovereign CLI)

Jos haluat puhua agentille suoraan päätteessä, kokeile näitä:

- `> status` : Näyttää verkoston tilan ja RAG-muistin tilanteen.
- `> operaatio "Tutki hakemisto src ja refaktoroi tiedosto main.py"` : Käynnistää laajemman tutkimus- tai koodaustehtävän (Sovereign / OmniNode -työnkululla).
- `> sandbox test fail.py` : Testaa tiedoston turvallisesti eristetyssä ympäristössä.

**Lisää teknistä syvyyttä, arkkitehtuurikuvauksia ja API-dokumentaatiota löydät [kokonaisvaltaisesta README.md-tiedostosta](README.md).**
