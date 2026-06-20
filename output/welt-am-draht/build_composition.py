from __future__ import annotations

import json
import re
import struct
from pathlib import Path

# WELT AM DRAHT - imagined as Camel (melodic British prog: lyrical lead, Mellotron
# strings, Rhodes) would have written it, with a touch of Joy Division (a high,
# melodic Hooky bass, motorik tom-driven drums, cold reverb, minimalism). Modal
# D minor / Dorian, slow-burning, effective harmony. Title after Fassbinder's
# "Welt am Draht" (World on a Wire) - cold, melancholic, beings on the wires.

OUT = Path(__file__).resolve().parent
TEMPO = 104
TITLE = "Welt am Draht"
SUBTITLE = "Camel x Joy Division - D minor / Dorian - a sketch with voices"


def midi(note: str) -> int:
    m = re.fullmatch(r"([A-G])([b#]?)(-?\d)", note)
    step, acc, octv = m.groups()
    semis = {"C": 0, "D": 2, "E": 4, "F": 5, "G": 7, "A": 9, "B": 11}
    val = semis[step] + (1 if acc == "#" else -1 if acc == "b" else 0)
    return (int(octv) + 1) * 12 + val


def L(*items):
    return [{"beat": b, "duration": d, "midi": midi(n)} for (b, d, n) in items]


def V(*items):  # vocal line with vowels
    return [{"beat": b, "duration": d, "midi": midi(n), "vowel": vw} for (b, d, n, vw) in items]


# ---- harmony (mid voicings for pad / rhodes) ----
def tri(*names):
    return [midi(n) for n in names]


A_TRIAD = [tri("D3", "F3", "A3"), tri("D3", "F3", "A3"), tri("Bb3", "D4", "F4"), tri("C4", "E4", "G4"),
           tri("D3", "F3", "A3"), tri("G3", "Bb3", "D4"), tri("C4", "E4", "G4"), tri("D3", "F3", "A3")]
B_TRIAD = [tri("F3", "A3", "C4"), tri("C4", "E4", "G4"), tri("D3", "F3", "A3"), tri("Bb3", "D4", "F4"),
           tri("F3", "A3", "C4"), tri("C4", "E4", "G4"), tri("G3", "B3", "D4"), tri("A3", "C#4", "E4")]

# ---- the high, melodic bass (Peter Hook flavour) ----
A_BASS = [
    L((0, .5, "D2"), (.5, .5, "A2"), (1, .5, "D3"), (1.5, .5, "A2"), (2, .5, "D2"), (2.5, .5, "F2"), (3, .5, "A2"), (3.5, .5, "F2")),
    L((0, .5, "D2"), (.5, .5, "A2"), (1, .5, "D3"), (1.5, .5, "A2"), (2, .5, "D2"), (2.5, .5, "F2"), (3, .5, "A2"), (3.5, .5, "F2")),
    L((0, .5, "Bb2"), (.5, .5, "F2"), (1, .5, "Bb2"), (1.5, .5, "D3"), (2, .5, "Bb2"), (2.5, .5, "F2"), (3, 1, "D3")),
    L((0, .5, "C3"), (.5, .5, "G2"), (1, .5, "C3"), (1.5, .5, "E3"), (2, .5, "C3"), (2.5, .5, "G2"), (3, 1, "E3")),
    L((0, .5, "D2"), (.5, .5, "A2"), (1, .5, "D3"), (1.5, .5, "A2"), (2, .5, "D2"), (2.5, .5, "F2"), (3, .5, "A2"), (3.5, .5, "F2")),
    L((0, .5, "G2"), (.5, .5, "D3"), (1, .5, "Bb2"), (1.5, .5, "D3"), (2, .5, "G2"), (2.5, .5, "Bb2"), (3, 1, "D3")),
    L((0, .5, "C3"), (.5, .5, "G2"), (1, .5, "C3"), (1.5, .5, "E3"), (2, .5, "C3"), (2.5, .5, "G2"), (3, 1, "E3")),
    L((0, 1, "D2"), (1, 1, "A2"), (2, 2, "D3")),
]
B_BASS = [
    L((0, 1, "F2"), (1, 1, "C3"), (2, 2, "A2")),
    L((0, 1, "C3"), (1, 1, "G2"), (2, 2, "E3")),
    L((0, 1, "D2"), (1, 1, "A2"), (2, 2, "D3")),
    L((0, 1, "Bb2"), (1, 1, "F2"), (2, 2, "D3")),
    L((0, .5, "F2"), (.5, .5, "A2"), (1, 1, "C3"), (2, 2, "A2")),
    L((0, 1, "C3"), (1, 1, "E3"), (2, 2, "G2")),
    L((0, 1, "G2"), (1, 1, "D3"), (2, 2, "B2")),
    L((0, 1, "A2"), (1, 1, "E3"), (2, 2, "C#3")),
]

# ---- lyrical lead (Camel) over the B section ----
B_LEAD = [
    L((0, 2, "A4"), (2, 1, "C5"), (3, 1, "A4")),
    L((0, 1.5, "G4"), (1.5, .5, "A4"), (2, 2, "E4")),
    L((0, 1, "F4"), (1, 1, "A4"), (2, 1, "D5"), (3, 1, "A4")),
    L((0, 2, "D5"), (2, 1, "C5"), (3, 1, "A4")),
    L((0, 1, "C5"), (1, 1, "A4"), (2, 2, "F4")),
    L((0, 1, "E4"), (1, 1, "G4"), (2, 2, "C5")),
    L((0, 1, "D5"), (1, .5, "B4"), (1.5, .5, "D5"), (2, 2, "B4")),
    L((0, 2, "C#5"), (2, 2, "A4")),
]

# ---- voices as a human-voice sketch ----
MALE = [  # baritone (Ian Curtis flavour), verse over A section
    V((0, 1, "D3", "o"), (1, 1, "D3", "o"), (2, 1, "F3", "a"), (3, 1, "E3", "e")),
    V((0, 2, "D3", "o"), (2, 1, "A2", "u"), (3, 1, "D3", "o")),
    V((0, 1, "F3", "a"), (1, 1, "D3", "o"), (2, 2, "F3", "e")),
    V((0, 1, "E3", "e"), (1, 1, "G3", "a"), (2, 2, "E3", "o")),
    V((0, 1, "D3", "o"), (1, 1, "F3", "a"), (2, 1, "E3", "e"), (3, 1, "D3", "o")),
    V((0, 1, "D3", "o"), (1, 1, "Bb2", "u"), (2, 2, "D3", "a")),
    V((0, 1, "E3", "e"), (1, 1, "C3", "o"), (2, 2, "G2", "u")),
    V((0, 2, "D3", "o"), (2, 2, "A2", "a")),
]
FEMALE = [  # ethereal high counter, chorus over B section
    V((0, 2, "A4", "a"), (2, 2, "C5", "o")),
    V((0, 2, "G4", "e"), (2, 2, "E4", "a")),
    V((0, 2, "F4", "o"), (2, 2, "A4", "a")),
    V((0, 2, "D5", "a"), (2, 2, "D5", "o")),
    V((0, 2, "C5", "e"), (2, 2, "A4", "a")),
    V((0, 2, "E4", "o"), (2, 2, "G4", "a")),
    V((0, 2, "D5", "a"), (2, 2, "B4", "o")),
    V((0, 4, "A4", "a")),
]

# ---- drums ----
TOM = {"low": midi("A2"), "mid": midi("B2"), "high": midi("D3")}  # 45, 47, 50
TOM_PAT = [(0.5, "low"), (1, "mid"), (1.5, "high"), (2.5, "low"), (3, "mid"), (3.5, "high")]
HAT_BEATS = [i * 0.5 for i in range(8)]

VEL = {"kick": 116, "snare": 110, "tom": 100, "hat": 50, "bass": 102, "rhodes": 70,
       "pad": 56, "lead": 96, "voxM": 104, "voxF": 110}
CHANNELS = {"bass": 0, "rhodes": 1, "pad": 2, "lead": 3, "voxF": 4, "voxM": 5,
            "kick": 9, "snare": 9, "tom": 9, "hat": 9}
PROGRAMS = {0: 34, 1: 4, 2: 49, 3: 81, 4: 54, 5: 53}  # bass, rhodes, strings, saw lead, voices
DRUM_MIDI = {"kick": 36, "snare": 38, "hat": 42}

RHODES_PAT = [0, 1, 2, 3, 2, 1, 0, 1]  # eighths over a triad+octave


def emit(notes, bar, typ, idx, layers):
    base = bar * 4
    triad = (A_TRIAD if typ == "A" else B_TRIAD)[idx]

    def add(voice, beat, dur, pitch, vel=None, **extra):
        n = {"beat": base + beat, "duration": dur, "midi": pitch,
             "velocity": vel if vel is not None else VEL[voice], "voice": voice, "bar": bar}
        n.update(extra)
        notes.append(n)

    def add_line(voice, table):
        for ev in table[idx]:
            extra = {"vowel": ev["vowel"]} if "vowel" in ev else {}
            add(voice, ev["beat"], ev["duration"], ev["midi"], **extra)

    if "kick" in layers:
        for b in (0, 2):
            add("kick", b, .18, DRUM_MIDI["kick"])
        if "kick4" in layers:
            for b in (1, 3):
                add("kick", b, .18, DRUM_MIDI["kick"], 104)
    if "snare" in layers:
        for b in (1, 3):
            add("snare", b, .2, DRUM_MIDI["snare"])
    if "tom" in layers:
        for (b, name) in TOM_PAT:
            add("tom", b, .16, TOM[name], 96)
    if "hat" in layers:
        for b in HAT_BEATS:
            add("hat", b, .06, DRUM_MIDI["hat"], 56 if (b * 2) % 2 == 0 else 44)
    if "bass" in layers:
        add_line("bass", A_BASS if typ == "A" else B_BASS)
    if "pad" in layers:
        for p in triad:
            add("pad", 0, 4, p)
    if "rhodes" in layers:
        seq = [triad[0], triad[1], triad[2], triad[0] + 12]
        for i, ix in enumerate(RHODES_PAT):
            add("rhodes", i * 0.5, .48, seq[ix], 74 if i % 2 == 0 else 62)
    if "lead" in layers and typ == "B":
        add_line("lead", B_LEAD)
    if "voxM" in layers and typ == "A":
        add_line("voxM", MALE)
    if "voxF" in layers and typ == "B":
        add_line("voxF", FEMALE)


def block(plan, typ, layers, bars):
    for i in range(bars):
        plan.append((typ, set(layers), i % 8))


def build_plan():
    plan = []
    # Intro (A, 8): wires power up
    block(plan, "A", {"pad", "bass", "tom"}, 4)
    block(plan, "A", {"pad", "bass", "tom", "hat", "kick", "snare"}, 4)
    # Verse 1 (A, 16) - male baritone
    block(plan, "A", {"pad", "bass", "rhodes", "kick", "snare", "hat", "tom", "voxM"}, 16)
    # Chorus 1 (B, 16) - female + lead, lift
    block(plan, "B", {"pad", "bass", "rhodes", "kick", "kick4", "snare", "hat", "lead", "voxF"}, 16)
    # Verse 2 (A, 16) - male
    block(plan, "A", {"pad", "bass", "rhodes", "kick", "snare", "hat", "tom", "voxM"}, 16)
    # Bridge (B, 16) - instrumental Camel lead solo, biggest
    block(plan, "B", {"pad", "bass", "rhodes", "kick", "kick4", "snare", "hat", "tom", "lead"}, 16)
    # Chorus 2 (B, 16) - both voices
    block(plan, "B", {"pad", "bass", "rhodes", "kick", "kick4", "snare", "hat", "lead", "voxF", "voxM"}, 16)
    # Outro (A, 16) - fade to the wires
    block(plan, "A", {"pad", "bass", "rhodes", "kick", "hat"}, 4)
    block(plan, "A", {"pad", "bass", "rhodes"}, 4)
    block(plan, "A", {"pad", "bass"}, 4)
    block(plan, "A", {"pad"}, 4)
    return plan


def build_notes():
    plan = build_plan()
    notes = []
    for bar, (typ, layers, idx) in enumerate(plan):
        emit(notes, bar, typ, idx, layers)
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
        (0, 0, b"\xff\x59\x02\xff\x00"),  # one flat (D minor)
    ]
    for ch, prog in PROGRAMS.items():
        timeline.append((0, 1, bytes([0xC0 | ch, prog])))
    for ev in notes:
        ch = CHANNELS[ev["voice"]]
        start = round(ev["beat"] * tpq)
        dur = max(24, round(ev["duration"] * tpq * .92))
        timeline.append((start, 2, bytes([0x90 | ch, ev["midi"], max(1, min(127, ev["velocity"]))])))
        timeline.append((start + dur, 1, bytes([0x80 | ch, ev["midi"], 0])))
    timeline.sort(key=lambda x: (x[0], x[1]))
    body = bytearray()
    prev = 0
    for tick, _, data in timeline:
        body += vlq(tick - prev) + data
        prev = tick
    body += b"\x00\xff\x2f\x00"
    header = b"MThd" + struct.pack(">IHHH", 6, 0, 1, tpq)
    (OUT / "welt-am-draht.mid").write_bytes(header + b"MTrk" + struct.pack(">I", len(body)) + body)


def write_data(notes, bars):
    payload = {
        "title": TITLE, "subtitle": SUBTITLE, "tempo": TEMPO,
        "beatsPerMeasure": 4, "notatedMeasures": bars, "playbackMeasures": bars,
        "order": list(range(1, bars + 1)), "notes": notes,
        "instruments": [
            {"voice": "kick", "label": "Kick", "color": "#e85d5d"},
            {"voice": "snare", "label": "Snare", "color": "#f0a35a"},
            {"voice": "tom", "label": "Toms", "color": "#d98cff"},
            {"voice": "hat", "label": "Hats", "color": "#bcd0e0"},
            {"voice": "bass", "label": "Bass (Hooky)", "color": "#5fd0ff"},
            {"voice": "rhodes", "label": "Rhodes", "color": "#ffd98a"},
            {"voice": "pad", "label": "Mellotron pad", "color": "#8aa0d8"},
            {"voice": "lead", "label": "Lead", "color": "#ffe07a"},
            {"voice": "voxF", "label": "Voice · female", "color": "#ff8ab0"},
            {"voice": "voxM", "label": "Voice · male", "color": "#7fa8ff"},
        ],
        "sections": [
            {"name": "Intro", "from": 0, "to": 8},
            {"name": "Verse · male", "from": 8, "to": 24},
            {"name": "Chorus · female", "from": 24, "to": 40},
            {"name": "Verse · male", "from": 40, "to": 56},
            {"name": "Bridge · lead", "from": 56, "to": 72},
            {"name": "Chorus · duet", "from": 72, "to": 88},
            {"name": "Outro", "from": 88, "to": 104},
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
    dur = bars * 4 * 60 / TEMPO
    print(f"{TITLE}: {bars} bars, {len(notes)} events, ~{int(dur//60)}:{int(dur%60):02d} {by}")


if __name__ == "__main__":
    main()
