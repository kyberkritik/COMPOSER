from __future__ import annotations

import json
import re
import struct
from pathlib import Path
from xml.sax.saxutils import escape

OUT = Path(__file__).resolve().parent
TEMPO = 66
DIVISIONS = 8
TITLE = "The Mushroom at the End of the World"
SUBTITLE = "A baroque elegy for classical guitar and cello"


def midi(note: str) -> int:
    match = re.fullmatch(r"([A-G])([b#]?)(-?\d)", note)
    if not match:
        raise ValueError(note)
    step, accidental, octave = match.groups()
    semitones = {"C": 0, "D": 2, "E": 4, "F": 5, "G": 7, "A": 9, "B": 11}
    value = semitones[step] + (1 if accidental == "#" else -1 if accidental == "b" else 0)
    return (int(octave) + 1) * 12 + value


def melody(*items):
    return [{"beat": beat, "duration": duration, "midi": midi(note)} for beat, duration, note in items]


def line(*items):
    """A free voice (cello) given as (beat, duration, note) triples."""
    return [{"beat": beat, "duration": duration, "midi": midi(note)} for beat, duration, note in items]


# The germinal motif is G-Ab-C-B-G: it rises like a fruiting body, then folds
# back into the soil. The rest of the melody grows by inversion, sequence, and
# chromatic alteration rather than quoting Bach's melody.
MELODY = [
    melody((0, 1.5, "G4"), (1.5, .5, "Ab4"), (2, 1, "C5"), (3, .5, "B4"), (3.5, .5, "G4")),
    melody((0, 1, "G4"), (1, .5, "F4"), (1.5, .5, "Eb4"), (2, 1, "D4"), (3, 1, "G4")),
    melody((0, 1.5, "Ab4"), (1.5, .5, "G4"), (2, 1, "F4"), (3, .5, "Eb4"), (3.5, .5, "D4")),
    melody((0, 2, "G4"), (2, .5, "F#4"), (2.5, .5, "G4"), (3, 1, "D4")),
    melody((0, 1, "C5"), (1, .5, "Bb4"), (1.5, .5, "Ab4"), (2, 1, "G4"), (3, 1, "F4")),
    melody((0, .5, "Eb4"), (.5, .5, "F4"), (1, 1, "G4"), (2, 1, "C5"), (3, .5, "B4"), (3.5, .5, "C5")),
    melody((0, 1, "D5"), (1, .5, "C5"), (1.5, .5, "Bb4"), (2, .5, "Ab4"), (2.5, .5, "G4"), (3, .5, "F#4"), (3.5, .5, "G4")),
    melody((0, 2.5, "G4"), (2.5, .25, "Ab4"), (2.75, .25, "G4"), (3, .5, "F#4"), (3.5, .5, "G4")),
    melody((0, 1.5, "C5"), (1.5, .5, "B4"), (2, 1, "G4"), (3, .5, "Ab4"), (3.5, .5, "F4")),
    melody((0, 1, "Bb4"), (1, .5, "Ab4"), (1.5, .5, "G4"), (2, 1, "F4"), (3, 1, "D4")),
    melody((0, 1, "Eb4"), (1, .5, "G4"), (1.5, .5, "Ab4"), (2, 1, "C5"), (3, .5, "Bb4"), (3.5, .5, "Ab4")),
    melody((0, 1.5, "G4"), (1.5, .5, "F#4"), (2, 1, "G4"), (3, .5, "D5"), (3.5, .5, "C5")),
    melody((0, 1, "Bb4"), (1, .5, "G4"), (1.5, .5, "Ab4"), (2, 1, "Bb4"), (3, 1, "Eb5")),
    melody((0, 1, "D5"), (1, .5, "C5"), (1.5, .5, "Bb4"), (2, 1, "A4"), (3, 1, "F4")),
    melody((0, .5, "G4"), (.5, .5, "Ab4"), (1, 1, "G4"), (2, .5, "Eb4"), (2.5, .5, "F4"), (3, 1, "D4")),
    melody((0, 1, "D4"), (1, 2, "G4"), (3, .5, "F#4"), (3.5, .5, "G4")),
    melody((0, 1, "C5"), (1, .5, "Eb5"), (1.5, .5, "D5"), (2, 1, "C5"), (3, 1, "Ab4")),
    melody((0, .5, "G4"), (.5, .5, "Ab4"), (1, 1, "C5"), (2, 1, "B4"), (3, 1, "G4")),
    melody((0, 1, "Ab4"), (1, .5, "C5"), (1.5, .5, "Bb4"), (2, .5, "Ab4"), (2.5, .5, "G4"), (3, 1, "F4")),
    melody((0, 1, "D5"), (1, .5, "C5"), (1.5, .5, "Bb4"), (2, 1, "G4"), (3, .5, "F#4"), (3.5, .5, "G4")),
    melody((0, 1.5, "Eb5"), (1.5, .5, "D5"), (2, 1, "C5"), (3, .5, "Bb4"), (3.5, .5, "G4")),
    melody((0, .5, "Ab4"), (.5, .5, "Bb4"), (1, 1, "C5"), (2, 1, "F4"), (3, 1, "Ab4")),
    melody((0, 1, "G4"), (1, .5, "F4"), (1.5, .5, "Eb4"), (2, .5, "D4"), (2.5, .5, "F#4"), (3, 1, "G4")),
    melody((0, 4, "C5")),
]

# A second instrument enters: a cello obbligato. In Section I it is the
# subterranean mycelial network - sparse, sustained, mostly below the guitar.
# In Section II it surfaces and fruits, rising into a singing co-protagonist,
# and in the final bar it sustains the major third E, the "altered light".
CELLO = [
    line((0, 2, "C3"), (2, 2, "Eb3")),
    line((0, 2, "D3"), (2, 2, "F3")),
    line((0, 3, "Eb3"), (3, 1, "C3")),
    line((0, 2, "D3"), (2, 1, "B2"), (3, 1, "D3")),
    line((0, 2, "F3"), (2, 2, "Ab3")),
    line((0, 2, "G3"), (2, 2, "E3")),
    line((0, 2, "F3"), (2, 1, "D3"), (3, 1, "F3")),
    line((0, 4, "G3")),
    line((0, 2, "G3"), (2, 2, "C4")),
    line((0, 2, "D4"), (2, 2, "Bb3")),
    line((0, 1.5, "C4"), (1.5, .5, "Bb3"), (2, 2, "Ab3")),
    line((0, 2, "B3"), (2, 1, "D4"), (3, 1, "F4")),
    line((0, 2, "G4"), (2, 2, "Bb3")),
    line((0, 2, "A3"), (2, 2, "D4")),
    line((0, 1.5, "Eb4"), (1.5, .5, "D4"), (2, 2, "C4")),
    line((0, 2, "D4"), (2, 2, "G3")),
    line((0, 2, "C4"), (2, 2, "Eb4")),
    line((0, 3, "G3"), (3, 1, "Ab3")),
    line((0, 2, "Ab3"), (2, 2, "F3")),
    line((0, 2, "D4"), (2, 1, "B3"), (3, 1, "D4")),
    line((0, 2, "Bb3"), (2, 2, "G3")),
    line((0, 2, "Ab3"), (2, 2, "C4")),
    line((0, 2, "D4"), (2, 1, "B3"), (3, 1, "D4")),
    line((0, 4, "E3")),
]

HARMONY_NAMES = [
    ["Eb3", "G3", "C4", "G3"], ["D3", "G3", "F3", "G3"],
    ["C4", "Eb4", "C4", "Eb4"], ["B2", "D3", "F3", "D3"],
    ["Ab3", "C4", "Ab3", "C4"], ["G3", "C4", "G3", "C4"],
    ["F3", "Ab3", "F3", "B3"], ["B2", "D3", "F3", "D3"],
    ["Eb3", "G3", "Eb3", "G3"], ["D3", "F3", "D3", "F3"],
    ["C4", "Eb4", "C4", "Eb4"], ["B2", "D3", "F3", "D3"],
    ["G3", "Bb3", "G3", "Bb3"], ["F3", "A3", "F3", "A3"],
    ["Eb3", "G3", "Eb3", "G3"], ["B2", "D3", "F3", "D3"],
    ["C4", "Eb4", "C4", "Eb4"], ["Eb3", "G3", "Eb3", "G3"],
    ["Ab3", "C4", "Ab3", "C4"], ["B2", "D3", "F3", "D3"],
    ["G3", "Bb3", "G3", "Bb3"], ["C4", "Eb4", "C4", "D4"],
    ["B2", "D3", "F3", "D3"], ["E3", "G3", "E4", "G3"],
]

BASS_NAMES = [
    ("C3", "G2"), ("B2", "G2"), ("Ab2", "Eb3"), ("G2", "D3"),
    ("F2", "C3"), ("E2", "C3"), ("D3", "G2"), ("G2", "D3"),
    ("C3", "G2"), ("Bb2", "F2"), ("Ab2", "Eb3"), ("G2", "D3"),
    ("Eb3", "Bb2"), ("D3", "A2"), ("C3", "G2"), ("G2", "D3"),
    ("Ab2", "Eb3"), ("G2", "C3"), ("F2", "C3"), ("G2", "D3"),
    ("Bb2", "Eb3"), ("Ab2", "F2"), ("G2", "D3"), ("C3", "C3"),
]

HARMONY = [[midi(note) for note in measure] for measure in HARMONY_NAMES]
BASS = [[midi(note) for note in measure] for measure in BASS_NAMES]
ORDER = list(range(1, 9)) * 2 + list(range(9, 25)) * 2

VELOCITIES = {"melody": 82, "inner": 58, "bass": 70, "cello": 74}


def notated_voices(measure_number: int):
    idx = measure_number - 1
    return {
        "melody": MELODY[idx],
        "inner": [{"beat": beat, "duration": 1, "midi": pitch} for beat, pitch in enumerate(HARMONY[idx])],
        "bass": [
            {"beat": 0, "duration": 2, "midi": BASS[idx][0]},
            {"beat": 2, "duration": 2, "midi": BASS[idx][1]},
        ],
        "cello": CELLO[idx],
    }


def performance_notes():
    notes = {}
    for play_index, measure_number in enumerate(ORDER):
        base = play_index * 4
        for voice, events in notated_voices(measure_number).items():
            for event in events:
                # Voice is part of the key so the cello never collides with the
                # guitar: the two instruments must remain independent.
                key = (base + event["beat"], event["midi"], voice)
                candidate = {
                    "beat": key[0], "duration": event["duration"], "midi": event["midi"],
                    "velocity": VELOCITIES[voice], "measure": measure_number, "voice": voice,
                }
                if key not in notes or candidate["duration"] > notes[key]["duration"]:
                    notes[key] = candidate
    return sorted(notes.values(), key=lambda event: (event["beat"], event["voice"], event["midi"]))


def vlq(value: int) -> bytes:
    output = [value & 0x7F]
    value >>= 7
    while value:
        output.append((value & 0x7F) | 0x80)
        value >>= 7
    return bytes(reversed(output))


def write_midi(notes):
    tpq = 480
    tempo_microseconds = round(60_000_000 / TEMPO)
    title_bytes = TITLE.encode("utf-8")
    # Channel 0: nylon-string guitar (program 24). Channel 1: cello (program 42).
    timeline = [
        (0, 0, b"\xff\x03" + vlq(len(title_bytes)) + title_bytes),
        (0, 0, b"\xff\x51\x03" + tempo_microseconds.to_bytes(3, "big")),
        (0, 0, b"\xff\x58\x04\x04\x02\x18\x08"),
        (0, 0, b"\xff\x59\x02\xfd\x00"),  # C minor: three flats.
        (0, 1, bytes([0xC0, 24])),            # Nylon-string guitar.
        (0, 1, bytes([0xC1, 42])),            # Cello.
    ]
    for event in notes:
        channel = 1 if event["voice"] == "cello" else 0
        start = round(event["beat"] * tpq)
        duration = max(30, round(event["duration"] * tpq * (.97 if channel == 1 else .94)))
        pitch = event["midi"]
        timeline.append((start, 2, bytes([0x90 | channel, pitch, event["velocity"]])))
        timeline.append((start + duration, 1, bytes([0x80 | channel, pitch, 0])))
    timeline.sort(key=lambda item: (item[0], item[1]))
    body = bytearray()
    previous = 0
    for tick, _, event in timeline:
        body += vlq(tick - previous) + event
        previous = tick
    body += b"\x00\xff\x2f\x00"
    header = b"MThd" + struct.pack(">IHHH", 6, 0, 1, tpq)
    track = b"MTrk" + struct.pack(">I", len(body)) + body
    (OUT / "the-mushroom-at-the-end-of-the-world.mid").write_bytes(header + track)


SPELLINGS = {
    0: ("C", 0), 1: ("D", -1), 2: ("D", 0), 3: ("E", -1),
    4: ("E", 0), 5: ("F", 0), 6: ("F", 1), 7: ("G", 0),
    8: ("A", -1), 9: ("A", 0), 10: ("B", -1), 11: ("B", 0),
}


def pitch_xml(sounding_midi: int, written_shift: int = 12):
    written = sounding_midi + written_shift
    step, alter = SPELLINGS[written % 12]
    octave = written // 12 - 1
    alter_xml = f"<alter>{alter}</alter>" if alter else ""
    return f"<pitch><step>{step}</step>{alter_xml}<octave>{octave}</octave></pitch>"


def voice_xml(events, voice_number: int, stem: str, written_shift: int = 12):
    result = []
    cursor = 0
    for event in events:
        onset = round(event["beat"] * DIVISIONS)
        duration = round(event["duration"] * DIVISIONS)
        if onset > cursor:
            result.append(f"<note><rest/><duration>{onset-cursor}</duration><voice>{voice_number}</voice></note>")
        result.append(
            f"<note>{pitch_xml(event['midi'], written_shift)}<duration>{duration}</duration><voice>{voice_number}</voice>"
            f"<stem>{stem}</stem></note>"
        )
        cursor = onset + duration
    if cursor < 4 * DIVISIONS:
        result.append(f"<note><rest/><duration>{4*DIVISIONS-cursor}</duration><voice>{voice_number}</voice></note>")
    return "".join(result)


def write_musicxml():
    guitar_measures = []
    cello_measures = []
    for number in range(1, 25):
        voices = notated_voices(number)
        attributes = ""
        direction = ""
        left = ""
        right = ""
        if number == 1:
            attributes = (
                "<attributes><divisions>8</divisions><key><fifths>-3</fifths><mode>minor</mode></key>"
                "<time><beats>4</beats><beat-type>4</beat-type></time>"
                "<clef><sign>G</sign><line>2</line><clef-octave-change>-1</clef-octave-change></clef>"
                "<transpose><diatonic>0</diatonic><chromatic>0</chromatic><octave-change>-1</octave-change></transpose>"
                "</attributes>"
            )
            direction = (
                "<direction placement=\"above\"><direction-type><words>Andante, come una rete sotterranea</words>"
                "</direction-type><sound tempo=\"66\"/></direction>"
            )
            left = "<barline location=\"left\"><repeat direction=\"forward\"/></barline>"
        elif number == 9:
            left = "<barline location=\"left\"><repeat direction=\"forward\"/></barline>"
        if number in (8, 24):
            right = "<barline location=\"right\"><repeat direction=\"backward\"/></barline>"
        content = voice_xml(voices["melody"], 1, "up")
        content += f"<backup><duration>{4*DIVISIONS}</duration></backup>"
        content += voice_xml(voices["inner"], 2, "down")
        content += f"<backup><duration>{4*DIVISIONS}</duration></backup>"
        content += voice_xml(voices["bass"], 3, "down")
        guitar_measures.append(f"<measure number=\"{number}\">{attributes}{direction}{left}{content}{right}</measure>")

        # Cello part: bass clef, sounding pitch (no octave transposition).
        cello_attributes = ""
        if number == 1:
            cello_attributes = (
                "<attributes><divisions>8</divisions><key><fifths>-3</fifths><mode>minor</mode></key>"
                "<time><beats>4</beats><beat-type>4</beat-type></time>"
                "<clef><sign>F</sign><line>4</line></clef></attributes>"
            )
        cello_content = voice_xml(voices["cello"], 1, "up", written_shift=0)
        cello_measures.append(f"<measure number=\"{number}\">{cello_attributes}{left}{cello_content}{right}</measure>")

    xml = (
        "<?xml version=\"1.0\" encoding=\"UTF-8\" standalone=\"no\"?>\n"
        "<!DOCTYPE score-partwise PUBLIC \"-//Recordare//DTD MusicXML 4.0 Partwise//EN\" "
        "\"http://www.musicxml.org/dtds/partwise.dtd\">\n"
        f"<score-partwise version=\"4.0\"><work><work-title>{escape(TITLE)}</work-title></work>"
        "<identification><creator type=\"composer\">Original composition generated with Codex; cello obbligato added by Claude</creator>"
        "<rights>Created for the user in this workspace</rights>"
        "<encoding><software>Codex composition generator</software></encoding></identification>"
        "<part-list>"
        "<score-part id=\"P1\"><part-name>Classical Guitar</part-name>"
        "<score-instrument id=\"P1-I1\"><instrument-name>Acoustic Guitar (nylon)</instrument-name></score-instrument>"
        "<midi-instrument id=\"P1-I1\"><midi-channel>1</midi-channel><midi-program>25</midi-program></midi-instrument>"
        "</score-part>"
        "<score-part id=\"P2\"><part-name>Cello</part-name>"
        "<score-instrument id=\"P2-I1\"><instrument-name>Cello</instrument-name></score-instrument>"
        "<midi-instrument id=\"P2-I1\"><midi-channel>2</midi-channel><midi-program>43</midi-program></midi-instrument>"
        "</score-part>"
        "</part-list>"
        "<part id=\"P1\">" + "".join(guitar_measures) + "</part>"
        "<part id=\"P2\">" + "".join(cello_measures) + "</part>"
        "</score-partwise>\n"
    )
    (OUT / "the-mushroom-at-the-end-of-the-world.musicxml").write_text(xml, encoding="utf-8")


def write_data(notes):
    payload = {
        "title": TITLE, "subtitle": SUBTITLE, "tempo": TEMPO,
        "beatsPerMeasure": 4, "notatedMeasures": 24,
        "playbackMeasures": len(ORDER), "order": ORDER, "notes": notes,
        "instruments": [
            {"voice": "melody", "label": "Guitar · melody", "instrument": "guitar"},
            {"voice": "inner", "label": "Guitar · inner", "instrument": "guitar"},
            {"voice": "bass", "label": "Guitar · bass", "instrument": "guitar"},
            {"voice": "cello", "label": "Cello · obbligato", "instrument": "cello"},
        ],
        "sections": [
            {"name": "I · Spores", "from": 0, "to": 16},
            {"name": "II · Ruins / Fruiting", "from": 16, "to": 48},
        ],
    }
    (OUT / "composition.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")
    (OUT / "composition-data.js").write_text(
        "window.COMPOSITION=" + json.dumps(payload, separators=(",", ":")) + ";\n", encoding="utf-8"
    )


def main():
    notes = performance_notes()
    write_midi(notes)
    write_musicxml()
    write_data(notes)
    cello_count = sum(1 for note in notes if note["voice"] == "cello")
    print(f"{TITLE}: 24 written measures, {len(ORDER)} played measures, "
          f"{len(notes)} note events ({cello_count} cello).")


if __name__ == "__main__":
    main()
