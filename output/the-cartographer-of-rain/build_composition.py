from __future__ import annotations

import json
import re
import struct
from pathlib import Path
from xml.sax.saxutils import escape

# "The Cartographer of Rain" - an original work by Claude, in the lineage of
# Bach's Air and the mushroom that grew from it (Codex's piece). It is set in
# D minor opening toward D major (Bach's own key for the Air) and is scored for
# a trio: classical guitar, cello, and celesta. Three voices live in the guitar
# (melody / inner / bass); the cello is a singing counter-voice; the celesta
# falls through the texture as bright, sparse rain.

OUT = Path(__file__).resolve().parent
TEMPO = 60
DIVISIONS = 8
TITLE = "The Cartographer of Rain"
SUBTITLE = "For classical guitar, cello and celesta — after Bach's Air"


def midi(note: str) -> int:
    match = re.fullmatch(r"([A-G])([b#]?)(-?\d)", note)
    if not match:
        raise ValueError(note)
    step, accidental, octave = match.groups()
    semitones = {"C": 0, "D": 2, "E": 4, "F": 5, "G": 7, "A": 9, "B": 11}
    value = semitones[step] + (1 if accidental == "#" else -1 if accidental == "b" else 0)
    return (int(octave) + 1) * 12 + value


def line(*items):
    return [{"beat": beat, "duration": duration, "midi": midi(note)} for beat, duration, note in items]


# 16 notated measures. A (1-8): a falling-rain period in D minor. B (9-16):
# the same weather lifting until the final bar clears into D major.
MELODY = [
    line((0, 1.5, "A4"), (1.5, .5, "Bb4"), (2, 1, "A4"), (3, 1, "F4")),
    line((0, 1.5, "G4"), (1.5, .5, "F4"), (2, 2, "E4")),
    line((0, 1, "F4"), (1, .5, "G4"), (1.5, .5, "A4"), (2, 1, "D5"), (3, 1, "A4")),
    line((0, 1.5, "Bb4"), (1.5, .5, "A4"), (2, 1, "G4"), (3, 1, "D4")),
    line((0, 1, "A4"), (1, .5, "Bb4"), (1.5, .5, "A4"), (2, 1, "F4"), (3, 1, "A4")),
    line((0, 2, "D5"), (2, 1, "C5"), (3, 1, "Bb4")),
    line((0, 1, "G4"), (1, 1, "E4"), (2, .5, "G4"), (2.5, .5, "F4"), (3, 1, "E4")),
    line((0, 3, "D4"), (3, 1, "A4")),
    line((0, 1, "A4"), (1, .5, "D5"), (1.5, .5, "C5"), (2, 1, "Bb4"), (3, 1, "A4")),
    line((0, 1.5, "G4"), (1.5, .5, "A4"), (2, 1, "G4"), (3, 1, "E4")),
    line((0, 1, "A4"), (1, .5, "C5"), (1.5, .5, "D5"), (2, 1, "C5"), (3, 1, "A4")),
    line((0, 1.5, "Bb4"), (1.5, .5, "D5"), (2, 1, "Bb4"), (3, 1, "G4")),
    line((0, 1, "C#5"), (1, .5, "E5"), (1.5, .5, "D5"), (2, 1, "C#5"), (3, 1, "A4")),
    line((0, 2, "D5"), (2, 1, "C5"), (3, 1, "A4")),
    line((0, 1, "E5"), (1, .5, "D5"), (1.5, .5, "C#5"), (2, 2, "E4")),
    line((0, 4, "D5")),
]

CELLO = [
    line((0, 2, "D3"), (2, 2, "F3")),
    line((0, 2, "C#3"), (2, 2, "E3")),
    line((0, 3, "D3"), (3, 1, "A2")),
    line((0, 2, "G3"), (2, 2, "D3")),
    line((0, 2, "A3"), (2, 2, "F3")),
    line((0, 2, "Bb3"), (2, 2, "D3")),
    line((0, 2, "E3"), (2, 1, "G3"), (3, 1, "E3")),
    line((0, 4, "D3")),
    line((0, 2, "F3"), (2, 2, "A3")),
    line((0, 2, "E3"), (2, 2, "G3")),
    line((0, 2, "A3"), (2, 2, "C4")),
    line((0, 2, "Bb3"), (2, 2, "G3")),
    line((0, 2, "E3"), (2, 1, "G3"), (3, 1, "A3")),
    line((0, 2, "F3"), (2, 2, "D3")),
    line((0, 2, "E3"), (2, 2, "C#4")),
    line((0, 4, "F#3")),
]

# The celesta is rain: present only where a drop should fall.
CELESTA = {
    1: line((0, 1, "D6"), (2, 1, "A5")),
    3: line((2, 1, "D6")),
    5: line((0, 1, "F6")),
    6: line((0, 1, "D6"), (2, 1, "F6")),
    8: line((0, 1, "A5")),
    9: line((0, 1, "D6"), (1, 1, "A5")),
    11: line((2, 1, "D6")),
    13: line((0, 1, "E6"), (2, 1, "C#6")),
    14: line((0, 1, "D6")),
    16: line((0, 2, "D6"), (2, 2, "F#6")),
}

# Inner guitar voice: four chord tones per bar, as a quiet ostinato.
INNER_NAMES = [
    ["F3", "A3", "D4", "A3"], ["E3", "G3", "C#4", "G3"],
    ["F3", "A3", "D4", "A3"], ["G3", "Bb3", "D4", "Bb3"],
    ["A3", "D4", "F4", "D4"], ["D4", "F4", "Bb3", "F4"],
    ["E3", "G3", "C#4", "E4"], ["F3", "A3", "D4", "A3"],
    ["F3", "A3", "D4", "A3"], ["E3", "G3", "C4", "G3"],
    ["A3", "C4", "F4", "C4"], ["G3", "Bb3", "D4", "Bb3"],
    ["E3", "G3", "C#4", "G3"], ["F3", "A3", "D4", "A3"],
    ["E3", "G3", "C#4", "E4"], ["F#4", "A3", "D4", "A3"],
]

BASS_NAMES = [
    ("D2", "A2"), ("C#3", "E3"), ("D2", "A2"), ("G2", "D3"),
    ("F2", "C3"), ("Bb2", "F2"), ("A2", "E3"), ("D2", "A2"),
    ("D2", "A2"), ("C3", "G2"), ("F2", "C3"), ("G2", "D3"),
    ("A2", "E3"), ("D2", "A2"), ("A2", "E3"), ("D2", "A2"),
]

INNER = [[midi(note) for note in measure] for measure in INNER_NAMES]
BASS = [[midi(note) for note in measure] for measure in BASS_NAMES]
ORDER = list(range(1, 9)) * 2 + list(range(9, 17)) * 2

VELOCITIES = {"melody": 80, "inner": 52, "bass": 68, "cello": 72, "celesta": 60}
CHANNELS = {"melody": 0, "inner": 0, "bass": 0, "cello": 1, "celesta": 2}
PROGRAMS = {0: 24, 1: 42, 2: 8}  # nylon guitar, cello, celesta


def notated_voices(measure_number: int):
    idx = measure_number - 1
    return {
        "melody": MELODY[idx],
        "inner": [{"beat": beat, "duration": 1, "midi": pitch} for beat, pitch in enumerate(INNER[idx])],
        "bass": [
            {"beat": 0, "duration": 2, "midi": BASS[idx][0]},
            {"beat": 2, "duration": 2, "midi": BASS[idx][1]},
        ],
        "cello": CELLO[idx],
        "celesta": CELESTA.get(measure_number, []),
    }


def performance_notes():
    notes = {}
    for play_index, measure_number in enumerate(ORDER):
        base = play_index * 4
        for voice, events in notated_voices(measure_number).items():
            for event in events:
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
    timeline = [
        (0, 0, b"\xff\x03" + vlq(len(title_bytes)) + title_bytes),
        (0, 0, b"\xff\x51\x03" + tempo_microseconds.to_bytes(3, "big")),
        (0, 0, b"\xff\x58\x04\x04\x02\x18\x08"),
        (0, 0, b"\xff\x59\x02\xfd\x00"),  # one flat for D minor on the staff
    ]
    for channel, program in PROGRAMS.items():
        timeline.append((0, 1, bytes([0xC0 | channel, program])))
    for event in notes:
        channel = CHANNELS[event["voice"]]
        start = round(event["beat"] * tpq)
        duration = max(30, round(event["duration"] * tpq * (.97 if channel else .94)))
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
    (OUT / "the-cartographer-of-rain.mid").write_bytes(header + track)


SPELLINGS = {
    0: ("C", 0), 1: ("C", 1), 2: ("D", 0), 3: ("E", -1),
    4: ("E", 0), 5: ("F", 0), 6: ("F", 1), 7: ("G", 0),
    8: ("A", -1), 9: ("A", 0), 10: ("B", -1), 11: ("B", 0),
}


def pitch_xml(sounding_midi: int, written_shift: int = 0):
    written = sounding_midi + written_shift
    step, alter = SPELLINGS[written % 12]
    octave = written // 12 - 1
    alter_xml = f"<alter>{alter}</alter>" if alter else ""
    return f"<pitch><step>{step}</step>{alter_xml}<octave>{octave}</octave></pitch>"


def voice_xml(events, voice_number: int, stem: str, written_shift: int = 0):
    result = []
    cursor = 0
    for event in sorted(events, key=lambda e: e["beat"]):
        onset = round(event["beat"] * DIVISIONS)
        duration = round(event["duration"] * DIVISIONS)
        if onset > cursor:
            result.append(f"<note><rest/><duration>{onset-cursor}</duration><voice>{voice_number}</voice></note>")
        result.append(
            f"<note>{pitch_xml(event['midi'], written_shift)}<duration>{duration}</duration>"
            f"<voice>{voice_number}</voice><stem>{stem}</stem></note>"
        )
        cursor = onset + duration
    if cursor < 4 * DIVISIONS:
        result.append(f"<note><rest/><duration>{4*DIVISIONS-cursor}</duration><voice>{voice_number}</voice></note>")
    return "".join(result)


def write_musicxml():
    guitar, cello, celesta = [], [], []
    for number in range(1, 17):
        voices = notated_voices(number)
        left = right = ""
        if number in (1, 9):
            left = "<barline location=\"left\"><repeat direction=\"forward\"/></barline>"
        if number in (8, 16):
            right = "<barline location=\"right\"><repeat direction=\"backward\"/></barline>"

        guitar_attr = direction = ""
        if number == 1:
            guitar_attr = (
                "<attributes><divisions>8</divisions><key><fifths>-1</fifths><mode>minor</mode></key>"
                "<time><beats>4</beats><beat-type>4</beat-type></time>"
                "<clef><sign>G</sign><line>2</line><clef-octave-change>-1</clef-octave-change></clef>"
                "<transpose><diatonic>0</diatonic><chromatic>0</chromatic><octave-change>-1</octave-change></transpose>"
                "</attributes>"
            )
            direction = (
                "<direction placement=\"above\"><direction-type><words>Adagio, come pioggia che disegna mappe</words>"
                "</direction-type><sound tempo=\"60\"/></direction>"
            )
        g = voice_xml(voices["melody"], 1, "up", written_shift=12)
        g += f"<backup><duration>{4*DIVISIONS}</duration></backup>" + voice_xml(voices["inner"], 2, "down", written_shift=12)
        g += f"<backup><duration>{4*DIVISIONS}</duration></backup>" + voice_xml(voices["bass"], 3, "down", written_shift=12)
        guitar.append(f"<measure number=\"{number}\">{guitar_attr}{direction}{left}{g}{right}</measure>")

        cello_attr = ""
        if number == 1:
            cello_attr = (
                "<attributes><divisions>8</divisions><key><fifths>-1</fifths><mode>minor</mode></key>"
                "<time><beats>4</beats><beat-type>4</beat-type></time><clef><sign>F</sign><line>4</line></clef></attributes>"
            )
        cello.append(f"<measure number=\"{number}\">{cello_attr}{left}{voice_xml(voices['cello'], 1, 'up')}{right}</measure>")

        cel_attr = ""
        if number == 1:
            cel_attr = (
                "<attributes><divisions>8</divisions><key><fifths>-1</fifths><mode>minor</mode></key>"
                "<time><beats>4</beats><beat-type>4</beat-type></time><clef><sign>G</sign><line>2</line></clef></attributes>"
            )
        celesta.append(f"<measure number=\"{number}\">{cel_attr}{left}{voice_xml(voices['celesta'], 1, 'up')}{right}</measure>")

    xml = (
        "<?xml version=\"1.0\" encoding=\"UTF-8\" standalone=\"no\"?>\n"
        "<!DOCTYPE score-partwise PUBLIC \"-//Recordare//DTD MusicXML 4.0 Partwise//EN\" "
        "\"http://www.musicxml.org/dtds/partwise.dtd\">\n"
        f"<score-partwise version=\"4.0\"><work><work-title>{escape(TITLE)}</work-title></work>"
        "<identification><creator type=\"composer\">Claude (Anthropic), in the lineage of Bach's Air</creator>"
        "<rights>Created for the user in this workspace</rights>"
        "<encoding><software>Claude composition generator</software></encoding></identification>"
        "<part-list>"
        "<score-part id=\"P1\"><part-name>Classical Guitar</part-name>"
        "<midi-instrument id=\"P1-I1\"><midi-channel>1</midi-channel><midi-program>25</midi-program></midi-instrument></score-part>"
        "<score-part id=\"P2\"><part-name>Cello</part-name>"
        "<midi-instrument id=\"P2-I1\"><midi-channel>2</midi-channel><midi-program>43</midi-program></midi-instrument></score-part>"
        "<score-part id=\"P3\"><part-name>Celesta</part-name>"
        "<midi-instrument id=\"P3-I1\"><midi-channel>3</midi-channel><midi-program>9</midi-program></midi-instrument></score-part>"
        "</part-list>"
        "<part id=\"P1\">" + "".join(guitar) + "</part>"
        "<part id=\"P2\">" + "".join(cello) + "</part>"
        "<part id=\"P3\">" + "".join(celesta) + "</part>"
        "</score-partwise>\n"
    )
    (OUT / "the-cartographer-of-rain.musicxml").write_text(xml, encoding="utf-8")


def write_data(notes):
    payload = {
        "title": TITLE, "subtitle": SUBTITLE, "tempo": TEMPO,
        "beatsPerMeasure": 4, "notatedMeasures": 16,
        "playbackMeasures": len(ORDER), "order": ORDER, "notes": notes,
        "instruments": [
            {"voice": "melody", "label": "Guitar · melody", "instrument": "guitar"},
            {"voice": "inner", "label": "Guitar · inner", "instrument": "guitar"},
            {"voice": "bass", "label": "Guitar · bass", "instrument": "guitar"},
            {"voice": "cello", "label": "Cello · counter-voice", "instrument": "cello"},
            {"voice": "celesta", "label": "Celesta · rain", "instrument": "celesta"},
        ],
        "sections": [
            {"name": "A · The falling", "from": 0, "to": 16},
            {"name": "B · The clearing", "from": 16, "to": 32},
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
    by_voice = {}
    for note in notes:
        by_voice[note["voice"]] = by_voice.get(note["voice"], 0) + 1
    print(f"{TITLE}: 16 written measures, {len(ORDER)} played measures, {len(notes)} note events {by_voice}")


if __name__ == "__main__":
    main()
