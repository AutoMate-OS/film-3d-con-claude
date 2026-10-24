# Istruzioni per l'agente (Codex, Claude): fai il donut

Quando l'utente scrive qualcosa come "fammi il donut":

1. Controlla che ci siano `blender` (4.5+) e `ffmpeg`. Se manca qualcosa, dillo e spiega come installarlo; non installare niente senza il suo ok.
2. Lavora solo dentro `donut/`. Non cancellare e non sovrascrivere file fuori da lì.
3. Esegui `blender -b -P donut.py -- salva scene.blend`.
4. Fotogrammi di prova: `blender -b scene.blend -P prova.py -- 50 eroe:60 eroe:100 eroe:300 macro:300`. Guarda le immagini in `prove/` e correggi `donut.py` se qualcosa non sembra un donut vero (glassa dello stesso colore dell'impasto, bordi a gradini, zuccherini che galleggiano). Mostra le prove all'utente.
5. Con l'ok dell'utente: `blender -b scene.blend -P shot.py -- costruzione eroe 1 200` (dì quanto ci metterà: il primo fotogramma ti dà il tempo), poi `ffmpeg -framerate 30 -i renders/costruzione/f_%04d.png -pix_fmt yuv420p donut.mp4`.
6. Se l'utente chiede una modifica a parole ("glassa al pistacchio", "più zuccherini"), cambia solo le righe che servono (di solito `GLASSA` e `ZUCCHERINI` in cima a `donut.py`), mostragli le righe cambiate, poi rifai le prove.

Il secondo esempio (il robottino) è in `progetto/`: se l'utente lo chiede, segui `progetto/prompt-robottino.txt`.
Regole: niente rete; niente personaggi o marchi altrui.
