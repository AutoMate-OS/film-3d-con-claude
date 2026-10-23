# Musica e ogni effetto sonoro dell'animazione, sintetizzati da zero con numpy -> sound.wav
# Tempi presi da timeline.py: ogni atterraggio, tasto, pannello e il titolo hanno il loro suono.
import numpy as np, wave, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from timeline import DURATA, HOPS, ENTRATA, PANNELLI, SALTO_FINALE, TITOLO, BPM

SR = 48000
L = np.zeros(int(SR * DURATA))
R = np.zeros_like(L)
rng = np.random.default_rng(7)

def t_(d):
    return np.arange(int(SR * d)) / SR

def env(n, a=0.005, rel=0.2):
    t = np.arange(n) / SR
    return np.minimum(1, t / a) * np.exp(-t / rel)

def mettere(x, t, vol=1.0, pan=0.0):
    i = int(t * SR)
    if i >= len(L):
        return
    x = x[: len(L) - i] * vol
    L[i:i + len(x)] += x * (1 - pan) / 1.4
    R[i:i + len(x)] += x * (1 + pan) / 1.4

def nota(m):  # numero MIDI -> Hz
    return 440 * 2 ** ((m - 69) / 12)

# ---------- strumenti ----------
def kick():
    t = t_(0.35); f = 45 + 90 * np.exp(-t * 30)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * env(len(t), 0.002, 0.12)

def rim():
    t = t_(0.18); n = rng.standard_normal(len(t))
    return (0.5 * n * env(len(t), 0.001, 0.03) + 0.6 * np.sin(2 * np.pi * 820 * t) * env(len(t), 0.001, 0.02))

def hat():
    t = t_(0.06); n = rng.standard_normal(len(t))
    n = np.diff(n, prepend=0)  # passa-alto grezzo
    return 0.25 * n * env(len(t), 0.001, 0.015)

def rhodes(m, d):
    t = t_(d); f = nota(m)
    x = np.sin(2 * np.pi * f * t + 0.8 * np.sin(2 * np.pi * f * 2 * t) * np.exp(-t * 3))
    x *= (1 + 0.15 * np.sin(2 * np.pi * 4.5 * t))  # tremolo
    return x * env(len(t), 0.01, d * 0.6)

def boing(f0=330):  # atterraggio: molla che sale e scende
    t = t_(0.32)
    f = f0 * (1 + 0.9 * np.exp(-t * 18)) * (1 + 0.05 * np.sin(2 * np.pi * 22 * t))
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * env(len(t), 0.003, 0.09)

def glock(m):  # tasto che si accende
    t = t_(0.9); f = nota(m)
    return (np.sin(2 * np.pi * f * t) + 0.4 * np.sin(2 * np.pi * f * 2.76 * t) * np.exp(-t * 9)) * env(len(t), 0.001, 0.35)

def glass_knock(m):  # pannello che si accende
    t = t_(0.5); f = nota(m)
    x = sum(a * np.sin(2 * np.pi * f * k * t) for k, a in ((1, 1), (2.32, 0.5), (4.25, 0.25)))
    return x * env(len(t), 0.001, 0.08) + 0.2 * rng.standard_normal(len(t)) * env(len(t), 0.001, 0.004)

def whoosh(d=0.8):
    t = t_(d); n = rng.standard_normal(len(t))
    k = np.ones(40) / 40
    n = np.convolve(n, k, mode="same")
    return n * np.sin(np.pi * t / d) ** 2 * 3

def colpo_titolo():
    t = t_(2.5)
    sub = np.sin(2 * np.pi * np.cumsum(60 + 40 * np.exp(-t * 8)) / SR) * env(len(t), 0.005, 0.6)
    ding = sum(glock(m)[: len(t)] if len(glock(m)) >= len(t) else np.pad(glock(m), (0, len(t) - len(glock(m)))) for m in (76, 83, 88))
    return 0.9 * sub + 0.5 * ding

# ---------- musica: lo-fi 120 BPM, 6 battute ----------
b = 60 / BPM
accordi = [(53, 57, 60, 64), (52, 55, 59, 62), (50, 53, 57, 60), (48, 52, 55, 59), (53, 57, 60, 64), (55, 59, 62, 65)]
for i, acc in enumerate(accordi):
    for m in acc:
        mettere(rhodes(m, 4 * b), i * 4 * b, 0.09, pan=(m % 3 - 1) * 0.3)
    mettere(rhodes(acc[0] - 12, 4 * b), i * 4 * b, 0.16)
batt = int(DURATA / b)
for k in range(batt):
    t = k * b
    if t < HOPS[0][0] - 0.01 or t > DURATA - 0.6:
        continue  # la batteria entra col primo salto
    if k % 2 == 0:
        mettere(kick(), t, 0.7)
    else:
        mettere(rim(), t, 0.35, pan=0.1)
    mettere(hat(), t, 0.5, pan=-0.3)
    mettere(hat(), t + b * 0.58, 0.35, pan=-0.3)  # ottavo in swing
mettere(0.012 * rng.standard_normal(len(L)), 0, 1.0)  # fruscio del vinile

# ---------- effetti sui tempi dell'animazione ----------
scala = [72, 74, 76, 79, 81, 84]
mettere(boing(260), ENTRATA[1], 0.45)
mettere(glock(scala[0]), ENTRATA[1] + 0.03, 0.25, pan=-0.4)
for i, (t0, t1, n) in enumerate(HOPS):
    mettere(boing(300 + 25 * i), t1, 0.45, pan=-0.4 + 0.2 * i)
    mettere(glock(scala[i + 1]), t1 + 0.03, 0.28, pan=-0.4 + 0.2 * i)
for i, t in enumerate(PANNELLI):
    mettere(glass_knock(88 + 2 * i), t + 0.05, 0.3, pan=-0.6 + 0.4 * i)
mettere(whoosh(0.9), SALTO_FINALE[0] - 0.05, 0.35)
mettere(boing(200), SALTO_FINALE[1], 0.5)
mettere(colpo_titolo(), TITOLO + 0.3, 0.6)
mettere(boing(420), 10.45, 0.3)

# ---------- master ----------
fade = np.ones_like(L)
n = int(SR * 0.8)
fade[-n:] = np.linspace(1, 0, n)
st = np.stack([L, R], 1) * fade[:, None]
st = np.tanh(st * 1.4) / np.tanh(1.4)
st *= 0.89 / np.abs(st).max()
out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sound.wav")
with wave.open(out, "wb") as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((st * 32767).astype(np.int16).tobytes())
print("ok", out, f"{DURATA:.1f} s")
