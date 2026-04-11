# AgentDir – Tauri-työpöytäikkuna

Kevyt **Tauri 2** -kuori, joka avaa paikallisen Web-UI:n (`http://127.0.0.1:8080/ui/`).

## Vaatimukset

- [Rust](https://rustup.rs/) (stable)
- [Node.js](https://nodejs.org/) 18+ (Tauri CLI)
- Käynnissä: `python server.py` (tai `agentdir-server`) samassa koneessa, jotta Web-UI vastaa.

## Asennus ja ajo

```bash
cd desktop
npm install
# Jos `src-tauri/icons/` puuttuu, generoi kuvakkeet lähde-PNG:stä:
# npx @tauri-apps/cli icon icon-src.png
npm run tauri dev
```

Tuotantorakennus (lokaalinen `.exe` / binääri):

```bash
npm run tauri build
```

Portti tai polku poikkeaa oletuksesta → muokkaa `src-tauri/tauri.conf.json` (`build.devUrl` ja `app.windows[0].url`) vastaamaan `config.json`-kohtaa `a2a.port`.

## Huomiot

- Tämä ei korvaa palvelinta: watcher + `server.py` pitää käynnistää erikseen (tai Docker `both`).
- Etä-URL vaatii Tauri ACL:ssä `capabilities/default.json`-kohdan `remote.urls`-sallinnat.
