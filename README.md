# Un film 3D con Claude, senza aprire Blender

Un'animazione 3D di 12 secondi (verticale 1080x1920) fatta **solo con il codice**: un robottino blu salta sui tasti di un editor video, i pannelli si accendono, sale il titolo "FATTO CON CLAUDE". Claude ha scritto i programmi, Blender li esegue da riga di comando senza aprire la sua finestra, la musica e gli effetti sono sintetizzati con numpy, FFmpeg unisce tutto.

Il nostro render: 360 fotogrammi su un processore AMD Ryzen 7 7700 (8 core), **senza scheda video**.

## Come si usa

1. Scarica questo repository (**Code → Download ZIP**, oppure `git clone`).
2. Installa **Blender** (4.5 o più recente, gratuito da blender.org), **Python 3 con numpy**, **Node.js** e **FFmpeg**.
3. Apri la cartella con **Claude Code** (o Codex) e scrivi: **"Fammi il film 3D"**. Parte la skill `film-3d-blender` (in Codex: `AGENTS.md`).

Se vuoi partire da zero, incolla in Claude il prompt di `prompt.txt` in una cartella vuota: è quello che ha generato questi file.

A mano, dalla cartella `progetto/`:

```
npm install && npx playwright install chromium
node shot.mjs                                   # interfaccia e icone -> tex/
blender -b --factory-startup -P scene.py        # costruisce scene.blend
blender -b scene.blend -P render.py -- 1 360    # render dei fotogrammi
python3 sound.py                                # musica ed effetti -> sound.wav
./encode.sh                                     # film.mp4
```

## Cosa c'è dentro

```
prompt.txt          il prompt da incollare in Claude
progetto/
├── ui.html         l'interfaccia dell'editor (diventa texture)
├── icons.html      le icone dei tasti
├── shot.mjs        fotografa interfaccia e icone con Playwright
├── timeline.py     tutti i tempi: animazione e suoni leggono da qui
├── scene.py        la scena 3D con l'API Python di Blender
├── render.py       render di un intervallo di fotogrammi
├── sound.py        base lo-fi a 120 BPM + effetti, sintetizzati
└── encode.sh       unisce fotogrammi e audio con FFmpeg
```

## Consigli

- Prima di tutto renderizza **5 fotogrammi di prova** (`blender -b scene.blend -P render.py -- 20 330 prova 60`) e guardali.
- Per cambiare il ritmo cambia solo `timeline.py`: animazione e suoni si spostano insieme.
- Troppo lento? Abbassa `sc.cycles.samples` in `scene.py`; con una scheda NVIDIA imposta Cycles sulla GPU.
- Il robottino ha il marchio AutoMate: per i tuoi video fai il tuo personaggio ed evita personaggi o interfacce di marchi altrui.

## Sicurezza

Sono file di testo leggibili: niente rete (a parte l'installazione di Playwright), niente dati personali. Gli script scrivono solo dentro `progetto/` (`tex/`, `renders/`, `scene.blend`, `sound.wav`, `film.mp4`).

## Vuoi che lo facciamo noi?

Video, automazioni e agenti AI costruiti sulla tua azienda: **alex@automate-pro.com** · **automate-pro.com**.

Licenza MIT.
