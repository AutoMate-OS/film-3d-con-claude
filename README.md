# Il donut di Blender, fatto da Claude senza aprire Blender

Il donut del tutorial che fanno tutti quando iniziano Blender, fatto **solo con il codice**: Claude scrive uno script Python, Blender lo esegue da riga di comando senza aprire la sua finestra, e la scena si costruisce da sola (la ciambella cresce, la glassa cola con le gocce, gli zuccherini cadono uno per uno). Se non ti piace, lo chiedi a parole: con *"glassa al pistacchio, più zuccherini"* Claude ha cambiato 2 righe in 18 secondi.

I nostri numeri (24/10/2026): 200 fotogrammi 1080x1920 con Cycles in 3 minuti e 52 secondi su una NVIDIA RTX PRO 6000; prove veloci con EEVEE su processore senza scheda video, circa 10 secondi a fotogramma.

## Come si usa

1. Scarica questo repository (**Code → Download ZIP**, oppure `git clone`).
2. Installa **Blender** (4.5 o più recente, gratuito da blender.org) e **FFmpeg**.
3. Apri la cartella con **Claude Code** (o Codex) e scrivi: **"Fammi il donut"**. Parte la skill `film-3d-blender` (in Codex: `AGENTS.md`).

Se vuoi partire da zero, incolla in Claude il prompt di `prompt.txt` in una cartella vuota.

A mano, dalla cartella `donut/`:

```
blender -b -P donut.py -- salva scene.blend                                # costruisce la scena
blender -b scene.blend -P prova.py -- 50 eroe:60 eroe:100 eroe:300 macro:300   # prove veloci (EEVEE)
blender -b scene.blend -P shot.py -- costruzione eroe 1 200                  # render (Cycles, GPU se c'è)
ffmpeg -framerate 30 -i renders/costruzione/f_%04d.png -pix_fmt yuv420p donut.mp4
```

Per cambiarlo: in cima a `donut/donut.py` ci sono `GLASSA` (cioccolato, pistacchio, fragola, vaniglia) e `ZUCCHERINI`. Oppure chiedilo a Claude a parole.

## Cosa c'è dentro

```
prompt.txt          il prompt da incollare in Claude
donut/
├── donut.py        la scena: piatto, ciambella, glassa che cola, zuccherini, luci, 3 camere
├── prova.py        fotogrammi di prova veloci con EEVEE (anche in fil di ferro)
└── shot.py         render di una ripresa con Cycles su GPU, ripartibile
progetto/           secondo esempio: il robottino che salta sui tasti di un editor (prompt in progetto/prompt-robottino.txt)
```

## Licenza

MIT. Il tutorial originale del donut è di Blender Guru (blenderguru.com).
