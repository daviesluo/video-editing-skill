"""Procedural sound effects and a fallback music bed.

Everything here is synthesised from noise and oscillators, so the series owns
every sample outright: no licence to track, no Content ID claim to dispute.
They are the fallback; generated or recorded takes in pipeline/sfx-lib/
(pipeline/sfxgen.py) sound less synthetic and are used first. Each function
returns float32 mono at RATE.
"""

import numpy as np

RATE = 48000
_rng = np.random.default_rng(20261018)


def _t(dur):
    return np.arange(int(dur * RATE)) / RATE


def _env(n, attack, release, curve=3.0):
    a = int(attack * RATE)
    r = int(release * RATE)
    e = np.ones(n)
    if a:
        e[:a] = np.linspace(0, 1, a) ** 2
    if r:
        e[-r:] *= np.linspace(1, 0, r) ** curve
    return e


def _onepole(x, cutoff):
    """One-pole low-pass; cutoff may be an array (per-sample sweep)."""
    cutoff = np.broadcast_to(cutoff, x.shape)
    k = 1 - np.exp(-2 * np.pi * cutoff / RATE)
    y = np.empty_like(x)
    s = 0.0
    for i in range(len(x)):
        s += k[i] * (x[i] - s)
        y[i] = s
    return y


def whoosh(dur=0.55, low=300.0, high=5200.0):
    """Air moving past: band-limited noise swept up then down."""
    n = int(dur * RATE)
    t = np.linspace(0, 1, n)
    sweep = low + (high - low) * np.sin(np.pi * t) ** 1.5
    noise = _rng.standard_normal(n)
    lp = _onepole(noise, sweep)
    hp = lp - _onepole(lp, sweep * 0.25)
    out = hp * _env(n, dur * 0.45, dur * 0.5, 2.0)
    return (out / (np.abs(out).max() + 1e-9) * 0.8).astype(np.float32)


def tick(freq=2400.0, dur=0.05):
    """A soft UI tick for counters and labels."""
    t = _t(dur)
    out = np.sin(2 * np.pi * freq * t) * np.exp(-t * 90)
    out += 0.3 * np.sin(2 * np.pi * freq * 2.01 * t) * np.exp(-t * 140)
    return (out * 0.5).astype(np.float32)


def pop(dur=0.12):
    """A rounded pop for a marker landing."""
    t = _t(dur)
    f = 900 * np.exp(-t * 30) + 220
    out = np.sin(2 * np.pi * np.cumsum(f) / RATE) * np.exp(-t * 38)
    return (out * 0.7).astype(np.float32)


def thud(dur=0.7):
    """A low impact for a big reveal; sits under the voice."""
    t = _t(dur)
    f = 95 * np.exp(-t * 6) + 42
    body = np.sin(2 * np.pi * np.cumsum(f) / RATE) * np.exp(-t * 5.5)
    click = _onepole(_rng.standard_normal(len(t)), 1800) * np.exp(-t * 60) * 0.6
    out = body + click
    return (out / np.abs(out).max() * 0.9).astype(np.float32)


def riser(dur=1.2):
    """Tension into a reveal: filtered noise and a rising tone."""
    n = int(dur * RATE)
    t = np.linspace(0, 1, n)
    noise = _onepole(_rng.standard_normal(n), 400 + 6000 * t**2)
    tone = np.sin(2 * np.pi * np.cumsum(180 + 520 * t**2) / RATE) * 0.25
    out = (noise * 0.6 + tone) * (t**2) * _env(n, 0.0, 0.04)
    return (out / (np.abs(out).max() + 1e-9) * 0.7).astype(np.float32)


def bed(dur, root=55.0, seed=7):
    """A slow, warm pad: a minor-ninth voicing on detuned saws, low-passed,
    with a gentle swell. Meant to sit around -30 LUFS under the voice."""
    rng = np.random.default_rng(seed)
    n = int(dur * RATE)
    t = np.arange(n) / RATE
    # i - VI - III - VII in A minor, four seconds per chord.
    progression = [
        [0, 7, 12, 15, 19, 26],
        [-4, 3, 8, 12, 15, 22],
        [3, 10, 15, 19, 22, 27],
        [-2, 5, 10, 14, 17, 24],
    ]
    seg = 4.0
    out = np.zeros(n)
    for ci in range(int(np.ceil(dur / seg)) + 1):
        start = int(ci * seg * RATE)
        if start >= n:
            break
        length = min(n - start, int((seg + 1.5) * RATE))
        tt = np.arange(length) / RATE
        env = np.minimum(1, tt / 1.2) * np.minimum(1, np.maximum(0, (seg + 1.5 - tt) / 1.5))
        chord = np.zeros(length)
        for semi in progression[ci % len(progression)]:
            f = root * 2 ** (semi / 12)
            for det in (-0.12, 0.0, 0.11):
                ph = rng.uniform(0, 1)
                saw = 2 * ((f * (1 + det / 100) * tt + ph) % 1) - 1
                chord += saw
        out[start:start + length] += chord * env
    out = _onepole(out, 900 + 300 * np.sin(2 * np.pi * t / 11))
    out = _onepole(out, 1400)
    swell = 0.85 + 0.15 * np.sin(2 * np.pi * t / 9)
    out = out * swell * _env(n, 1.5, 2.5, 2.0)
    return (out / (np.abs(out).max() + 1e-9) * 0.5).astype(np.float32)


LIBRARY = {"whoosh": whoosh, "tick": tick, "pop": pop, "thud": thud, "riser": riser}
