# Unica fonte dei tempi: la leggono scene.py (animazione) e sound.py (musica ed effetti).
FPS = 30
DURATA = 12.0  # secondi -> 360 fotogrammi

# Tasti della barra strumenti: (nome, icona). Il robottino salta su quelli in HOPS.
TASTI = ["Selezione", "Mano", "Testo", "Rettangolo", "Penna", "Bagliore", "Posizione", "Zoom"]

# (partenza, atterraggio, tasto) in secondi
HOPS = [
    (1.00, 1.55, "Testo"),
    (2.05, 2.60, "Rettangolo"),
    (3.10, 3.65, "Penna"),
    (4.15, 4.70, "Bagliore"),
    (5.25, 5.80, "Posizione"),
]
ENTRATA = (0.15, 0.55)      # il robottino cade sul primo tasto ("Mano")
ACCENSIONE = 6.30           # i pannelli dell'editor si accendono uno dopo l'altro
PANNELLI = [6.30, 6.55, 6.80, 7.05]
SALTO_FINALE = (8.10, 8.95) # salto grande sull'anteprima
TITOLO = 9.05               # sale "FATTO CON CLAUDE"
BPM = 120
