# Istruzioni per l'agente (Codex, Claude): fai il film 3D

Quando l'utente scrive qualcosa come "fammi il film 3D":

1. Controlla che ci siano `blender` (4.5+), `python3` con `numpy`, `node` e `ffmpeg`. Se manca qualcosa, dillo e spiega come installarlo; non installare niente senza il suo ok.
2. Lavora solo dentro `progetto/`. Non cancellare e non sovrascrivere file fuori da lì.
3. Esegui: `npm install && npx playwright install chromium`, poi `node shot.mjs`, poi `blender -b --factory-startup -P scene.py`.
4. Renderizza 5 fotogrammi di prova: `blender -b scene.blend -P render.py -- 20 330 prova 60`. Guarda le immagini in `renders/prova/` e correggi `scene.py` se qualcosa non va (oggetti fuori posto, testo che spunta, interfaccia illeggibile). Mostra le prove all'utente.
5. Con l'ok dell'utente: `blender -b scene.blend -P render.py -- 1 360` (dì quanto ci metterà: il primo fotogramma ti dà il tempo), poi `python3 sound.py` e `./encode.sh`.
6. Se l'utente vuole cambiare tempi o personaggio: tempi in `timeline.py`, scena in `scene.py`, suoni in `sound.py`.

Regole: niente rete oltre all'installazione di Playwright; niente personaggi o interfacce di marchi altrui.
