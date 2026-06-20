from __future__ import annotations

import json
import math
import struct
from pathlib import Path
from xml.etree import ElementTree as ET
from xml.sax.saxutils import escape

ROOT = Path(__file__).resolve().parents[3]
SOURCE = ROOT / "tmp/pdfs/score/source-bbox.html"
OUT = ROOT / "output/air-on-the-g-string"
OUT.mkdir(parents=True, exist_ok=True)

NS = {"x": "http://www.w3.org/1999/xhtml"}

# Tablature-system geometry in PDF points. Each tuple is
# (six string-line y coordinates, measure boundary x coordinates).
SYSTEMS = {
    3: [
        ([207.7, 215.1, 222.6, 230.0, 237.5, 244.9], [52, 184, 287, 422, 570]),
        ([367.2, 374.7, 382.1, 389.5, 397.0, 404.4], [52, 242, 410, 570]),
        ([525.3, 532.8, 540.2, 547.6, 555.1, 562.5], [52, 242, 410, 570]),
        ([683.3, 690.8, 698.3, 705.8, 713.2, 720.6], [52, 242, 441, 570]),
    ],
    4: [
        ([148.3, 155.8, 163.2, 170.7, 178.1, 185.5], [52, 243, 423, 570]),
        ([326.6, 334.0, 341.5, 348.9, 356.4, 363.8], [52, 243, 423, 570]),
        ([512.5, 519.9, 527.3, 534.8, 542.2, 549.6], [52, 267, 419, 570]),
        ([683.3, 690.7, 698.2, 705.6, 713.0, 720.5], [52, 245, 414, 570]),
    ],
    5: [
        ([148.3, 155.8, 163.2, 170.7, 178.1, 185.5], [52, 249, 417, 570]),
        ([326.6, 334.0, 341.5, 348.9, 356.4, 363.8], [52, 255, 417, 570]),
        ([505.0, 512.5, 519.9, 527.3, 534.8, 542.2], [52, 249, 415, 570]),
        ([683.3, 690.7, 698.2, 705.6, 713.0, 720.5], [52, 247, 480, 570]),
    ],
}

# Rhythmic onsets (quarter-note beats) read from the notation. Grace/trill
# figures use an eighth-of-a-beat subdivision where needed.
ONSETS = [
    [0, 1, 2, 3], [0, 1, 2, 3], [0, 1, 1.5, 2, 2.5, 3, 3.5],
    [0, .125, .25, 1, 1.5, 2, 3.5],
    [0, 1, 1.5, 2, 3, 3.5], [0, .5, 1, 1.5, 2, 2.5, 3, 3.5],
    [0, 1, 1.5, 2, 2.5, 3, 3.5],
    [0, .5, 1, 1.5, 2, 2.5, 3, 3.5], [0, 1, 2, 2.5, 3, 3.5],
    [0, .5, 1, 1.5, 2, 2.5, 3],
    [0, .5, 1, 1.5, 2, 2.5, 3, 3.5], [0, .5, 1, 1.5, 2, 2.5, 3, 3.5],
    [0, 1, 2, 3],
    [0, .5, 1, 1.5, 2, 2.5, 3, 3.5], [0, .5, 1, 2, 2.5, 3, 3.5],
    [0, 1, 2, 2.5, 3, 3.5],
    [0, 1, 2, 2.25, 2.5, 2.75, 3, 3.5], [0, .5, 1, 2, 2.5, 3, 3.5],
    [0, .5, 1, 1.5, 2, 3],
    [0, .5, 1, 1.5, 2, 2.5, 3, 3.5], [0, 1, 2, 3, 3.5],
    [0, 1, 2.5, 3],
    [0, 1, 1.5, 2, 2.5, 3, 3.5], [0, .5, 1, 1.5, 2, 2.5, 3, 3.5],
    [0, 1, 1.5, 2, 2.5, 3.5],
    [0, .5, 1, 1.5, 2, 2.5, 3, 3.5], [0, .5, 1, 1.5, 2, 2.5, 3.5],
    [0, .5, 1, 1.5, 2.5, 3],
    [0, .5, 1, 1.5, 2, 2.5, 3, 3.5], [0, 1, 2, 2.5, 3, 3.5, 3.75],
    [0, .5, 1, 1.5, 2.5, 3, 3.5],
    [0, 1, 2, 2.5, 3, 3.5], [0, 1, 2, 3, 3.5], [0, 1, 2, 3, 3.5],
    [0, 1, 1.5, 1.75, 2, 2.5, 3, 3.5],
    [0, .25, .5, 1, 1.5, 2, 3, 3.125, 3.25, 3.375, 3.5, 3.75],
    [0],
]

OPEN_STRING_MIDI = {1: 64, 2: 59, 3: 55, 4: 50, 5: 45, 6: 40}


def extract_measures():
    tree = ET.parse(SOURCE)
    pages = tree.findall(".//x:page", NS)
    measures = []
    for page_no, page in zip((3, 4, 5), pages):
        words = []
        for word in page.findall(".//x:word", NS):
            text = "".join(word.itertext()).strip()
            y0, y1 = float(word.attrib["yMin"]), float(word.attrib["yMax"])
            height = y1 - y0
            if text.strip("()").isdigit() and 8.5 < height < 9.5:
                words.append((float(word.attrib["xMin"]), (y0 + y1) / 2, text))
        for string_ys, bounds in SYSTEMS[page_no]:
            items = []
            for x, y, text in words:
                string = min(range(6), key=lambda i: abs(y - string_ys[i])) + 1
                if abs(y - string_ys[string - 1]) < 2 and bounds[0] <= x <= bounds[-1]:
                    items.append((x, string, int(text.strip("()"))))
            for left, right in zip(bounds, bounds[1:]):
                candidates = sorted(item for item in items if left <= item[0] < right)
                groups = []
                for x, string, fret in candidates:
                    if not groups or x - groups[-1][0] > 4.8:
                        groups.append([x, []])
                    groups[-1][1].append({"string": string, "fret": fret})
                measures.append(groups)
    if len(measures) != 37:
        raise ValueError(f"Expected 37 measures, found {len(measures)}")
    for number, (groups, onsets) in enumerate(zip(measures, ONSETS), 1):
        if len(groups) != len(onsets):
            raise ValueError(f"Measure {number}: {len(groups)} note groups but {len(onsets)} onsets")
    return measures


def build_score():
    raw = extract_measures()
    measures = []
    for number, (groups, onsets) in enumerate(zip(raw, ONSETS), 1):
        events = []
        for idx, ((_, fingerings), beat) in enumerate(zip(groups, onsets)):
            next_beat = onsets[idx + 1] if idx + 1 < len(onsets) else 4
            notes = []
            for item in fingerings:
                midi = OPEN_STRING_MIDI[item["string"]] + item["fret"]
                notes.append({**item, "midi": midi})
            events.append({
                "beat": beat,
                "duration": max(.125, next_beat - beat),
                "notes": notes,
            })
        measures.append({"number": number, "events": events})
    return measures


def performance_order():
    # First section with alternate endings, then the second repeated section.
    return list(range(1, 13)) + list(range(1, 12)) + [13] + list(range(14, 38)) * 2


def performance_events(measures):
    by_number = {m["number"]: m for m in measures}
    result = []
    for play_index, number in enumerate(performance_order()):
        base = play_index * 4
        for event in by_number[number]["events"]:
            result.append({
                "beat": base + event["beat"],
                "duration": event["duration"],
                "measure": number,
                "notes": sorted(set(n["midi"] for n in event["notes"])),
            })
    return result


def vlq(value):
    out = [value & 0x7F]
    value >>= 7
    while value:
        out.append((value & 0x7F) | 0x80)
        value >>= 7
    return bytes(reversed(out))


def write_midi(events):
    tpq = 480
    timeline = []
    # Tempo 72 BPM, 4/4, C major, nylon-string guitar.
    timeline += [
        (0, 0, b"\xff\x03" + vlq(len("Air on the G String")) + b"Air on the G String"),
        (0, 0, b"\xff\x51\x03" + (833333).to_bytes(3, "big")),
        (0, 0, b"\xff\x58\x04\x04\x02\x18\x08"),
        (0, 0, b"\xff\x59\x02\x00\x00"),
        (0, 1, bytes([0xC0, 24])),
    ]
    for event in events:
        start = round(event["beat"] * tpq)
        duration = max(24, round(event["duration"] * tpq * .88))
        for midi in event["notes"]:
            velocity = min(88, 66 + max(0, midi - 52) // 3)
            timeline.append((start, 2, bytes([0x90, midi, velocity])))
            timeline.append((start + duration, 1, bytes([0x80, midi, 0])))
    timeline.sort(key=lambda item: (item[0], item[1]))
    track = bytearray()
    previous = 0
    for tick, _, data in timeline:
        track += vlq(tick - previous) + data
        previous = tick
    track += b"\x00\xff\x2f\x00"
    header = b"MThd" + struct.pack(">IHHH", 6, 0, 1, tpq)
    chunk = b"MTrk" + struct.pack(">I", len(track)) + track
    (OUT / "air-on-the-g-string.mid").write_bytes(header + chunk)


PITCH_NAMES = {
    0: ("C", 0), 1: ("C", 1), 2: ("D", 0), 3: ("E", -1),
    4: ("E", 0), 5: ("F", 0), 6: ("F", 1), 7: ("G", 0),
    8: ("G", 1), 9: ("A", 0), 10: ("B", -1), 11: ("B", 0),
}


def note_xml(note, duration, chord=False):
    written = note["midi"] + 12
    step, alter = PITCH_NAMES[written % 12]
    octave = written // 12 - 1
    chord_tag = "<chord/>" if chord else ""
    alter_tag = f"<alter>{alter}</alter>" if alter else ""
    return (
        f"<note>{chord_tag}<pitch><step>{step}</step>{alter_tag}<octave>{octave}</octave></pitch>"
        f"<duration>{duration}</duration><voice>1</voice>"
        f"<notations><technical><string>{note['string']}</string><fret>{note['fret']}</fret>"
        f"</technical></notations></note>"
    )


def write_musicxml(measures):
    divisions = 8
    parts = []
    for measure in measures:
        n = measure["number"]
        attrs = ""
        directions = ""
        left_bar = ""
        right_bar = ""
        if n == 1:
            attrs = (
                "<attributes><divisions>8</divisions><key><fifths>0</fifths></key>"
                "<time><beats>4</beats><beat-type>4</beat-type></time>"
                "<clef><sign>G</sign><line>2</line><clef-octave-change>-1</clef-octave-change></clef>"
                "<transpose><diatonic>0</diatonic><chromatic>0</chromatic><octave-change>-1</octave-change></transpose>"
                "</attributes>"
            )
            directions = (
                "<direction placement=\"above\"><direction-type><words>Andante</words></direction-type>"
                "<sound tempo=\"72\"/></direction>"
            )
            left_bar = "<barline location=\"left\"><bar-style>heavy-light</bar-style><repeat direction=\"forward\"/></barline>"
        if n == 12:
            left_bar = "<barline location=\"left\"><ending number=\"1\" type=\"start\"/></barline>"
            right_bar = "<barline location=\"right\"><ending number=\"1\" type=\"stop\"/><repeat direction=\"backward\"/></barline>"
        elif n == 13:
            left_bar = "<barline location=\"left\"><ending number=\"2\" type=\"start\"/></barline>"
            right_bar = "<barline location=\"right\"><ending number=\"2\" type=\"stop\"/></barline>"
        elif n == 14:
            left_bar = "<barline location=\"left\"><bar-style>heavy-light</bar-style><repeat direction=\"forward\"/></barline>"
        elif n == 37:
            right_bar = "<barline location=\"right\"><repeat direction=\"backward\"/></barline>"
        notes = []
        for event in measure["events"]:
            duration = max(1, round(event["duration"] * divisions))
            ordered = sorted(event["notes"], key=lambda note: note["midi"])
            for idx, note in enumerate(ordered):
                notes.append(note_xml(note, duration, chord=idx > 0))
        parts.append(f"<measure number=\"{n}\">{attrs}{directions}{left_bar}{''.join(notes)}{right_bar}</measure>")
    xml = (
        "<?xml version=\"1.0\" encoding=\"UTF-8\" standalone=\"no\"?>\n"
        "<!DOCTYPE score-partwise PUBLIC \"-//Recordare//DTD MusicXML 4.0 Partwise//EN\" "
        "\"http://www.musicxml.org/dtds/partwise.dtd\">\n"
        "<score-partwise version=\"4.0\"><work><work-title>Air on the G String</work-title></work>"
        "<identification><creator type=\"composer\">Johann Sebastian Bach</creator>"
        "<creator type=\"arranger\">Allen W. Mathews</creator>"
        "<encoding><software>Codex transcription</software><encoding-description>Transcribed from the user-provided score; tablature cross-checked against the free high-resolution edition.</encoding-description></encoding>"
        "</identification><part-list><score-part id=\"P1\"><part-name>Classical Guitar</part-name>"
        "<score-instrument id=\"P1-I1\"><instrument-name>Acoustic Guitar (nylon)</instrument-name></score-instrument>"
        "<midi-instrument id=\"P1-I1\"><midi-channel>1</midi-channel><midi-program>25</midi-program></midi-instrument>"
        "</score-part></part-list><part id=\"P1\">" + "".join(parts) + "</part></score-partwise>\n"
    )
    (OUT / "air-on-the-g-string.musicxml").write_text(xml, encoding="utf-8")


def write_data(measures, events):
    payload = {
        "title": "Air on the G String",
        "subtitle": "From Orchestral Suite No. 3 - BWV 1068",
        "composer": "Johann Sebastian Bach",
        "arranger": "Allen W. Mathews",
        "tempo": 72,
        "beatsPerMeasure": 4,
        "notatedMeasures": 37,
        "playbackMeasures": len(performance_order()),
        "order": performance_order(),
        "events": events,
    }
    (OUT / "transcription.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")
    compact = json.dumps(payload, separators=(",", ":"))
    (OUT / "score-data.js").write_text("window.SCORE_DATA=" + compact + ";\n", encoding="utf-8")


def main():
    measures = build_score()
    events = performance_events(measures)
    write_midi(events)
    write_musicxml(measures)
    write_data(measures, events)
    print(f"Generated {len(measures)} notated measures, {len(performance_order())} playback measures, {len(events)} events")


if __name__ == "__main__":
    main()
