# AgentDir – Tauri-työpöytäikkuna

Kevyt **Tauri 2** -kuori, joka avaa paikallisen Web-UI:n (`http://127.0.0.1:8080/ui/`).

Jos AgentDir on käynnissä **`AGENTDIR_UI_SECRET`**-suojauksella, selain (WebView) ohjautuu **`/ui/login`**-sivulle. Kirjaudu samalla salasanalla kuin ympäristömuuttujassa; onnistuneen kirjautumisen jälkeen **istuntoeväste** (`agentdir_session`) tallennetaan WebViewiin kuten tavallisessa selaimessa, ja HTMX-päivitykset toimivat ilman erillistä otsikkoa. Jos joskus käytät **HTTPS**-osoitetta Taurissa, aseta palvelimelle **`AGENTDIR_UI_COOKIE_SECURE=1`** (tai `config.json` → `ui.cookie_secure: true`), jotta evästeen `Secure`-lippu vastaa skeemaa; pelkkä `http://127.0.0.1` paikallisesti käyttää oletuksena ei-secure-evästettä.

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
