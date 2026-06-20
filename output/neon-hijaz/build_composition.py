from __future__ import annotations

import json
import re
import struct
from pathlib import Path

# NEON HIJAZ - a dark, danceable hit that fuses Italo-disco / Modern Talking
# (octave bassline, offbeat stabs, soaring lead hook, lush pad) with in-your-face
# House (four-on-the-floor kick, claps, pumping hats) and Acid Arab (resonant
# 303 line, darbuka, oud) over the DOUBLE HARMONIC / HIJAZ scale.
#
# Lineage: the "spore" cell of Codex's mushroom (a semitone rise, a leap, a
# semitone fall) is reborn here as the lead hook D-Eb-G-F#-D, now in D Hijaz.

OUT = Path(__file__).resolve().parent
TEMPO = 124
TITLE = "NEON HIJAZ"
SUBTITLE = "Italo-disco x Acid Arab - double harmonic minor - 124 BPM"


def midi(note: str) -> int:
    m = re.fullmatch(r"([A-G])([b#]?)(-?\d)", note)
    step, acc, octv = m.groups()
    semis = {"C": 0, "D": 2, "E": 4, "F": 5, "G": 7, "A": 9, "B": 11}
    val = semis[step] + (1 if acc == "#" else -1 if acc == "b" else 0)
    return (int(octv) + 1) * 12 + val


# D double harmonic / Hijaz: D Eb F# G A Bb C#
PCS = {2, 3, 6, 7, 9, 10, 1}
SCALE = [m for m in range(38, 91) if m % 12 in PCS]


def scale_run(top_midi: int, count: int, descending=True):
    """A scale line of `count` notes starting near top_midi."""
    idx = min(range(len(SCALE)), key=lambda i: abs(SCALE[i] - top_midi))
    seq = []
    step = -1 if descending else 1
    for k in range(count):
        j = idx + step * k
        j = max(0, min(len(SCALE) - 1, j))
        seq.append(SCALE[j])
    return seq


# Four-bar harmonic loop (one chord per bar): Dmaj - Eb - Gm - Amaj.
# Roots for the bass (low), and mid voicings for pad / stab / arp.
CHORDS = [
    {"root": midi("D2"), "pad": [midi(n) for n in ("D3", "F#3", "A3", "D4")],
     "tri": [midi(n) for n in ("D4", "F#4", "A4")], "arp": [midi(n) for n in ("D3", "F#3", "A3", "D4")]},
    {"root": midi("Eb2"), "pad": [midi(n) for n in ("Eb3", "G3", "Bb3", "Eb4")],
     "tri": [midi(n) for n in ("Eb4", "G4", "Bb4")], "arp": [midi(n) for n in ("Eb3", "G3", "Bb3", "Eb4")]},
    {"root": midi("G2"), "pad": [midi(n) for n in ("G3", "Bb3", "D4", "G4")],
     "tri": [midi(n) for n in ("G4", "Bb4", "D5")], "arp": [midi(n) for n in ("G3", "Bb3", "D4", "G4")]},
    {"root": midi("A2"), "pad": [midi(n) for n in ("A3", "C#4", "E4", "A4")],
     "tri": [midi(n) for n in ("A4", "C#5", "E5")], "arp": [midi(n) for n in ("A3", "C#4", "E4", "A4")]},
]

# The Modern-Talking-style hook (4 bars, one list per bar) - born from the
# mushroom's spore motif, transposed into Hijaz.
HOOK = [
    [(0, 1, "D5"), (1, .5, "Eb5"), (1.5, .5, "D5"), (2, 1, "A4"), (3, 1, "F#4")],
    [(0, 1.5, "G4"), (1.5, .5, "Bb4"), (2, 1, "A4"), (3, 1, "G4")],
    [(0, 1, "Bb4"), (1, .5, "A4"), (1.5, .5, "G4"), (2, 1, "D5"), (3, 1, "Bb4")],
    [(0, 1, "C#5"), (1, .5, "D5"), (1.5, .5, "C#5"), (2, 2, "A4")],
]

# Female voice: sings the chorus hook (doubles the lead an octave feel), with
# vowels so the formant synth shapes faux-lyrics.
FEMALE = [
    [(0, 1, "D5", "a"), (1, .5, "Eb5", "a"), (1.5, .5, "D5", "a"), (2, 1, "A4", "o"), (3, 1, "F#4", "o")],
    [(0, 1.5, "G4", "e"), (1.5, .5, "Bb4", "e"), (2, 1, "A4", "a"), (3, 1, "G4", "a")],
    [(0, 1, "Bb4", "i"), (1, .5, "A4", "i"), (1.5, .5, "G4", "e"), (2, 1, "D5", "a"), (3, 1, "Bb4", "a")],
    [(0, 1, "C#5", "o"), (1, .5, "D5", "o"), (1.5, .5, "C#5", "o"), (2, 2, "A4", "a")],
]

# Male voice: a lower verse melody that answers the female line.
MALE = [
    [(0, 1, "D4", "o"), (1, 1, "A3", "o"), (2, 1, "Bb3", "a"), (3, 1, "A3", "a")],
    [(0, 1, "G3", "e"), (1, 1, "Bb3", "e"), (2, 2, "A3", "a")],
    [(0, 1, "D4", "o"), (1, 1, "Bb3", "o"), (2, 1, "G3", "a"), (3, 1, "A3", "a")],
    [(0, 2, "A3", "e"), (2, 1, "C#4", "e"), (3, 1, "D4", "a")],
]

# Acid 303 pattern: 16 steps, semitone offsets from the bar's acid root.
# None = rest. Flags: accent (loud) and slide (glide from previous note).
ACID = [
    (0, True, False), (None, False, False), (12, False, True), (0, False, False),
    (1, True, False), (None, False, False), (0, False, False), (12, False, True),
    (0, True, False), (None, False, False), (13, False, True), (0, False, False),
    (None, False, False), (0, True, False), (12, False, True), (1, False, False),
]

ARP_IDX = [0, 1, 2, 3, 2, 1, 0, 1, 2, 3, 2, 1, 0, 1, 2, 3]
BASS_PAT = [0, 0, 12, 0, 0, 0, 12, 0]  # eighth-note octave pulse

VEL = {"kick": 120, "clap": 104, "hat": 56, "perc": 92, "bass": 104,
       "acid": 88, "arp": 78, "pad": 60, "stab": 92, "lead": 110, "oud": 96,
       "voxF": 104, "voxM": 100}

# General MIDI mapping for export.
CHANNELS = {"bass": 0, "acid": 1, "arp": 2, "pad": 3, "stab": 4, "lead": 5, "oud": 6,
            "voxF": 7, "voxM": 8, "kick": 9, "clap": 9, "hat": 9, "perc": 9}
PROGRAMS = {0: 38, 1: 111, 2: 80, 3: 90, 4: 62, 5: 81, 6: 104, 7: 54, 8: 53}  # ch1 Shanai, ch7/8 voices
DRUM_MIDI = {"kick": 36, "clap": 39, "hatC": 42, "hatO": 46, "dum": 64, "tek": 62}


def emit_bar(notes, bar, layers, chord, lead_oct=0):
    base = bar * 4

    def add(voice, beat, dur, pitch, vel=None, **extra):
        n = {"beat": base + beat, "duration": dur, "midi": pitch,
             "velocity": vel if vel is not None else VEL[voice], "voice": voice, "bar": bar}
        n.update(extra)
        notes.append(n)

    if "kick" in layers:
        for b in (0, 1, 2, 3):
            add("kick", b, .16, DRUM_MIDI["kick"], 124 if b == 0 else 116)
    if "clap" in layers:
        for b in (1, 3):
            add("clap", b, .2, DRUM_MIDI["clap"])
    if "hat" in layers:
        for b in (0, 1, 2, 3):
            add("hat", b, .07, DRUM_MIDI["hatC"], 44)
        for b in (0.5, 1.5, 2.5, 3.5):
            add("hat", b, .14, DRUM_MIDI["hatO"], 74)  # open hat, house pump
        if "hatdense" in layers:
            for b in (0.25, 0.75, 1.25, 1.75, 2.25, 2.75, 3.25, 3.75):
                add("hat", b, .05, DRUM_MIDI["hatC"], 34)
    if "perc" in layers:
        for b in (0, 2):
            add("perc", b, .18, DRUM_MIDI["dum"], 96)
        for b in (0.5, 1.5, 3, 3.5):
            add("perc", b, .1, DRUM_MIDI["tek"], 72)
    if "bass" in layers:
        for i, off in enumerate(BASS_PAT):
            add("bass", i * 0.5, .45, chord["root"] + off, 108 if i == 0 else 100)
    if "acid" in layers:
        root = chord["root"] + 12
        for i, (off, accent, slide) in enumerate(ACID):
            if off is None:
                continue
            add("acid", i * 0.25, .24, root + off, 120 if accent else 80, slide=slide)
    if "arp" in layers:
        tones = chord["arp"]
        seq = [tones[0], tones[1], tones[2], tones[0] + 12]
        for i, idx in enumerate(ARP_IDX):
            add("arp", i * 0.25, .22, seq[idx], 84 if i % 4 == 0 else 70)
    if "pad" in layers:
        for p in chord["pad"]:
            add("pad", 0, 4, p, 58)
    if "stab" in layers:
        for b in (0.5, 1.5, 2.5, 3.5):
            for p in chord["tri"]:
                add("stab", b, .22, p, 92)
    if "lead" in layers:
        for (b, d, name) in HOOK[bar % 4]:
            add("lead", b, d, midi(name) + lead_oct, 112)


def oud_phrase(notes, bar, kind):
    base = bar * 4

    def add(beat, dur, pitch, vel=VEL["oud"]):
        notes.append({"beat": base + beat, "duration": dur, "midi": pitch,
                      "velocity": vel, "voice": "oud", "bar": bar})

    if kind == "ornament":
        for (b, d, name) in [(0, .5, "D5"), (.5, .5, "Eb5"), (1, .5, "D5"),
                             (2, .75, "A4"), (2.75, .25, "Bb4"), (3, 1, "F#4")]:
            add(b, d, midi(name))
    elif kind == "run_down":
        for i, p in enumerate(scale_run(midi("D6"), 16, descending=True)):
            add(i * 0.25, .24, p, 92 if i % 4 == 0 else 78)
    elif kind == "run_up":
        for i, p in enumerate(scale_run(midi("D4"), 16, descending=False)):
            add(i * 0.25, .24, p, 92 if i % 4 == 0 else 78)
    elif kind == "call":
        for (b, d, name) in [(0, 1, "A4"), (1, .5, "Bb4"), (1.5, .5, "A4"),
                             (2, .5, "G4"), (2.5, .5, "F#4"), (3, 1, "D4")]:
            add(b, d, midi(name))


FULL = {"kick", "clap", "hat", "hatdense", "perc", "bass", "acid", "arp", "pad", "stab", "lead"}


def block(layers, bars):
    return [set(layers) for _ in range(bars)]


def build_plan():
    """A full single across 128 bars (~4:07 at 124 BPM) with vocals."""
    plan = []
    # Intro (0-7)
    plan += block({"pad", "perc", "oud:ornament"}, 2)
    plan += block({"pad", "perc", "hat", "oud:ornament"}, 2)
    plan += block({"pad", "perc", "hat", "kick", "bass"}, 2)
    plan += block({"pad", "perc", "hat", "kick", "bass", "clap", "arp"}, 2)
    # Verse 1 - male vocal (8-23)
    verse = {"kick", "hat", "perc", "bass", "arp", "pad", "voxM"}
    plan += [verse | {"oud:call"} if i % 4 == 3 else set(verse) for i in range(16)]
    # Chorus 1 - female vocal (24-39)
    plan += block(FULL | {"voxF"}, 16)
    # Verse 2 - male vocal (40-47)
    plan += [verse | {"oud:call"} if i % 4 == 3 else set(verse) for i in range(8)]
    # Chorus 2 - female vocal (48-63)
    plan += block(FULL | {"voxF"}, 16)
    # Break - Arabic, instrumental (64-71)
    plan += block({"pad", "perc", "oud:run_down"}, 2)
    plan += block({"pad", "perc", "acid", "oud:run_up"}, 2)
    plan += block({"kick", "hat", "perc", "bass", "acid", "oud:call"}, 2)
    plan += block({"kick", "hat", "hatdense", "clap", "perc", "bass", "acid", "arp"}, 2)
    # Bridge - call & response (72-79): male asks, female answers
    plan += block({"kick", "hat", "perc", "bass", "pad", "voxM"}, 4)
    plan += block({"kick", "hat", "perc", "bass", "pad", "arp", "voxF"}, 4)
    # Chorus 3 - both voices, big (80-95)
    plan += block(FULL | {"voxF", "voxMh"}, 16)
    # Chorus 4 - both voices, lead up an octave (96-111)
    plan += block(FULL | {"voxF", "voxMh"}, 16)
    # Outro (112-127): filter down to the D Hijaz drone
    plan += block({"pad", "bass", "perc", "oud:ornament"}, 4)
    plan += block({"pad", "oud:ornament"}, 4)
    plan += block({"pad"}, 4)
    plan += block({"pad"}, 4)
    return plan


def emit_vocal(notes, bar, table, voice, octave):
    base = bar * 4
    for (b, d, name, vow) in table[bar % 4]:
        notes.append({"beat": base + b, "duration": d, "midi": midi(name) + octave,
                      "velocity": VEL[voice], "voice": voice, "bar": bar, "vowel": vow})


def build_notes():
    plan = build_plan()
    notes = []
    for bar, layers in enumerate(plan):
        chord = CHORDS[bar % 4]
        ouds = [l.split(":", 1)[1] for l in layers if l.startswith("oud:")]
        clean = {l for l in layers if not l.startswith("oud:") and not l.startswith("vox")}
        lead_oct = 12 if 96 <= bar <= 111 else 0
        emit_bar(notes, bar, clean, chord, lead_oct=lead_oct)
        for kind in ouds:
            oud_phrase(notes, bar, kind)
        if "voxF" in layers:
            emit_vocal(notes, bar, FEMALE, "voxF", 0)
        if "voxM" in layers:
            emit_vocal(notes, bar, MALE, "voxM", 0)
        if "voxMh" in layers:  # male sings the hook an octave below the female
            emit_vocal(notes, bar, FEMALE, "voxM", -12)
    notes.sort(key=lambda n: (n["beat"], n["voice"], n["midi"]))
    return notes, len(plan)


def vlq(value: int) -> bytes:
    out = [value & 0x7F]
    value >>= 7
    while value:
        out.append((value & 0x7F) | 0x80)
        value >>= 7
    return bytes(reversed(out))


def write_midi(notes):
    tpq = 480
    tempo_us = round(60_000_000 / TEMPO)
    title_bytes = TITLE.encode("utf-8")
    timeline = [
        (0, 0, b"\xff\x03" + vlq(len(title_bytes)) + title_bytes),
        (0, 0, b"\xff\x51\x03" + tempo_us.to_bytes(3, "big")),
        (0, 0, b"\xff\x58\x04\x04\x02\x18\x08"),
    ]
    for ch, prog in PROGRAMS.items():
        timeline.append((0, 1, bytes([0xC0 | ch, prog])))
    for ev in notes:
        ch = CHANNELS[ev["voice"]]
        start = round(ev["beat"] * tpq)
        dur = max(24, round(ev["duration"] * tpq * .9))
        pitch = ev["midi"]
        vel = max(1, min(127, ev["velocity"]))
        timeline.append((start, 2, bytes([0x90 | ch, pitch, vel])))
        timeline.append((start + dur, 1, bytes([0x80 | ch, pitch, 0])))
    timeline.sort(key=lambda x: (x[0], x[1]))
    body = bytearray()
    prev = 0
    for tick, _, data in timeline:
        body += vlq(tick - prev) + data
        prev = tick
    body += b"\x00\xff\x2f\x00"
    header = b"MThd" + struct.pack(">IHHH", 6, 0, 1, tpq)
    track = b"MTrk" + struct.pack(">I", len(body)) + body
    (OUT / "neon-hijaz.mid").write_bytes(header + track)


def write_data(notes, bars):
    payload = {
        "title": TITLE, "subtitle": SUBTITLE, "tempo": TEMPO,
        "beatsPerMeasure": 4, "notatedMeasures": bars, "playbackMeasures": bars,
        "order": list(range(1, bars + 1)), "notes": notes,
        "instruments": [
            {"voice": "kick", "label": "Kick", "color": "#ff5d73"},
            {"voice": "clap", "label": "Clap", "color": "#ff9a3d"},
            {"voice": "hat", "label": "Hats", "color": "#c8c2d8"},
            {"voice": "perc", "label": "Darbuka", "color": "#e0a96d"},
            {"voice": "bass", "label": "Octave bass", "color": "#5be0c0"},
            {"voice": "acid", "label": "Acid reed", "color": "#b4ff3d"},
            {"voice": "arp", "label": "Arp", "color": "#7df0ff"},
            {"voice": "pad", "label": "Pad", "color": "#8f7dff"},
            {"voice": "stab", "label": "Stab", "color": "#ff6fe0"},
            {"voice": "lead", "label": "Lead hook", "color": "#ffe14d"},
            {"voice": "oud", "label": "Oud", "color": "#ff8a5b"},
            {"voice": "voxF", "label": "Voice · female", "color": "#ff7ab0"},
            {"voice": "voxM", "label": "Voice · male", "color": "#6fa8ff"},
        ],
        "sections": [
            {"name": "Intro", "from": 0, "to": 8},
            {"name": "Verse · male", "from": 8, "to": 24},
            {"name": "Chorus · female", "from": 24, "to": 40},
            {"name": "Verse · male", "from": 40, "to": 48},
            {"name": "Chorus · female", "from": 48, "to": 64},
            {"name": "Break · Arabic", "from": 64, "to": 72},
            {"name": "Bridge · duet", "from": 72, "to": 80},
            {"name": "Chorus · duet", "from": 80, "to": 96},
            {"name": "Final Chorus", "from": 96, "to": 112},
            {"name": "Outro", "from": 112, "to": 128},
        ],
    }
    (OUT / "composition.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")
    (OUT / "composition-data.js").write_text(
        "window.COMPOSITION=" + json.dumps(payload, separators=(",", ":")) + ";\n", encoding="utf-8")


def main():
    notes, bars = build_notes()
    write_midi(notes)
    write_data(notes, bars)
    by = {}
    for n in notes:
        by[n["voice"]] = by.get(n["voice"], 0) + 1
    print(f"{TITLE}: {bars} bars, {len(notes)} events {by}")


if __name__ == "__main__":
    main()
