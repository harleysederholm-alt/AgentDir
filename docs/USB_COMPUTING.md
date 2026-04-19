# Sovereign OmniNode & USB Computing

Tämä opas neuvoo, kuinka kytket modernin mobiililaitteen (kuten Android-puhelimen, tabletin, tai jopa pöytälaatikosta löytyvän vanhan älypuhelimen) kiinni Sovereign Engineen kiinteällä USB-kaapelilla ja ohjaat järjestelmän offloadaamaan raskaat neuroverkkotehtävät täysin langattomien yhteyksien ohi suoraan laitteen E2B/E4B -piireille.

## 1. Konsepti (Gemma 4 Edge -arkkitehtuuri)
Uudet E-sarjan (**Edge**) kielimallit (Gemma 4 E2B ja E4B) on täsmäoptimoitu mobiilisiruille ja vähävirtaisille IoT-laitteille. 
USB-tetheröinnin avulla rakennamme suljetun ja erittäin suojatun (Air-Gapped) miniverkon PC:si ja puhelimen välille. Tämän USB-sillan yli Sovereign Engine lähettää reaaliajassa päättelytehtäviä (`compute_request`) suoraan laitteesi lokaaliin NPU/CPU-verkkoon.

## 2. Valmistelut (Android)
Mikäli haluat ajaa natiivia **Gemma 4 E4B** mallia laitteella Llama.cpp:n avulla ja jakaa sen Sovereign Enginen käyttöön, seuraa näitä ohjeita:

1. **Lataa Termux**: (F-Droidista, koska Play Kaupan versio on vanhentunut).
2. Ota puhelimen asetuksista asetus **USB-liitäntäjaon (USB Tethering)** käyttöön. Tämä luo "näennäisverkkokortin" tietokoneesi ja puhelimesi välille. Tietokoneesi näkee nyt puhelimesi kiinteässä IP:ssä (yleensä `192.168.42.129`).
3. Avaa Termux ja asenna tarvittavat ympäristöt:
   ```bash
   pkg update && pkg upgrade
   pkg install cmake clang wget git
   ```

## 3. Llama.cpp kääntäminen ja Gemma 4:n tuonti
1. Kloonaa C++ -moottori, joka kykenee hyödyntämään puhelimesi ARM-käskykantaa reaaliajassa:
   ```bash
   git clone https://github.com/ggerganov/llama.cpp
   cd llama.cpp
   make -j4
   ```
2. Lataa uunituore Gemma 4 E2B/E4B (GGUF-formaatti):
   ```bash
   wget https://huggingface.co/google/gemma-4-e2b-it-GGUF/resolve/main/gemma-4-e2b-it-q4_k_m.gguf
   ```
3. Käynnistä lokaali tekoäly-palvelin Termuxissa:
   ```bash
   ./server -m gemma-4-e2b-it-q4_k_m.gguf --host 0.0.0.0 --port 8081 -c 2048
   ```

## 4. Yhteydenotto Sovereign Engineen
Kun ylläoleva palvelin on käynnistetty ja USB-liitäntä on aktiivisena, isäntäkoneellasi rullaava **Sovereign Engine OmniNode Manager** havaitsee laitteen automaattisesti tai voit ilmoittaa sen IP-osoitteen.

Tämän jälkeen Sovereign Engine pystyy välittömästi offloadaamaan laskentaa raskaista analytiikkatehtävistään (kuten OmniNode-kaavinnat) suoraan puhelimesi lokaaliin NPU:hun! Laite toimii tehokkaana lisäkiihdyttimenä ilman, että prosessi vaatii internet-yhteyttä.
