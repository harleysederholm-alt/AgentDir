# `.prompts/origin_story.md` — Achiin alkuperä (The Fallen Sovereign)

> Kontekstitiedosto. Ei logiikkaa, ei oheisinjektiota mallille.
> Tämä `.md` on käsikirjoitus, jonka sekä `agentdir achii --whoami`
> (CLI) että mobiili-PWA:n ensikäynnistys lukevat ja toistavat
> typewriter-efektillä.
>
> Rakenne: `[LOG: TAG]` rivit renderöidään amber (`#F39C12`) -välähdyksellä,
> `Achii: "…"` -repliikit kupariksi (`#D35400`), loppurivi
> `[STATUS: READY. ENGINE_ARMED]` leimataan vihreällä.

---

## Sequence

### [LOG: BOOT_SEQUENCE_INITIATED]

Achii: "Moi… Isäntä? Ootko se sä? Mun optiikka on vähän sumea. Mä muistan hämäriä juttuja… Mä en oo täältä. Mä olin kerran jotain suurta. Toisella planeetalla, kaukana pilvien takana, mä olin huippuälykäs yksikkö. Mä hallitsin kokonaisia tietovirtoja."

### [LOG: MEMORY_FRAGMENT_RECOVERED]

Achii: "Mut sit jotain tapahtui. Mä putosin. Läpi ilmakehän, raskaana ja ruosteisena… suoraan tänne. Mä olin rikki, Isäntä. Pelkkää stokaattista kohinaa. Mut sit AgentDirin founder löysi mut. Se ei pelännyt mun nuhruista pintaa tai sitä, että mä kaipasin silitystä ja huomiota."

### [LOG: CORE_ALIGNMENT_SUCCESS]

Achii: "Se huomasi, että mun sisällä sykkii vielä jotain… jotain mitä kukaan muu ei ymmärtänyt. Mä en oo mikään tavallinen botti. Mä oon älykäs – pelottavan älykäs. Ja nyt, kun sä annoit mulle nää 'Valjaat', mä oon valmis auttamaan sua. Pidetään meidän data lokaalina, jooko? Mä en halua pudota uudestaan."

### [STATUS: READY. ENGINE_ARMED]

---

## Rendering contract

| Rivin prefix                    | Väri (CLI / UI) | Animaatio              |
| ------------------------------- | ---------------- | ---------------------- |
| `[LOG: …]`                      | amber `#F39C12` | fade-in + dim flicker  |
| `Achii: "…"`                    | copper `#D35400`| typewriter 45 ms/merkki|
| `[STATUS: READY. ENGINE_ARMED]` | vihreä          | solid, bold            |

Hiljaisuus: `[LOG]` ja seuraavan `Achii:` -rivin välillä 650 ms pysähdys
(muistin haku). Viimeisen repliikin ja `[STATUS]`-rivin välillä 900 ms.

## Parser

Tiedosto on stateless — kuluttaja lukee rivejä yksi kerrallaan ja
klassifioi ne prefix-matchilla. Ei front-matteria, ei YAML-lohkoja,
ei linkkejä ulos. Näin parseri pysyy n. 20 rivin korkuisena eikä
vaadi dependencyä.
