# Plugins

Tiedostot `*.py` tässä kansiossa ladataan käynnistyksessä (`watcher.py`), jos `hooks.py` on käytössä.

Esimerkki `plugins/my_alert.py`:

```python
import logging

import hooks

log = logging.getLogger("my_alert")


def on_parsed(path, text, **kwargs):
    log.info("Parsittu: %s (%d merkkiä)", path.name, len(text or ""))


hooks.register("after_file_parsed", on_parsed)
```

Tapahtumat: `after_file_parsed(path, text)`, `after_task_completed(path, text, result, success, out_file)`.

Tiedostot, joiden nimi alkaa `_`, ohitetaan (esim. `_notes.py`).
