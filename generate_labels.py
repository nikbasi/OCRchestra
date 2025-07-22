import os
from music21 import converter, note, chord
from PIL import Image

XML_DIR = "data/xml"
PNG_DIR = "data/png"
LABELS_DIR = "data/labels"
os.makedirs(LABELS_DIR, exist_ok=True)

# Image and staff assumptions — tune by inspection
NOTEHEAD_WIDTH = 20
NOTEHEAD_HEIGHT = 20
STAFF_TOP_Y = 100
STAFF_LINE_SPACING = 10  # pixels between lines
STAFF_LINE_COUNT = 5
MEASURE_WIDTH = 150

def pitch_to_y(p):
    step_order = ['C', 'D', 'E', 'F', 'G', 'A', 'B']
    step_index = step_order.index(p.step)
    offset_from_c4 = (p.octave - 4) * 7 + (step_index - 0)
    y = STAFF_TOP_Y + STAFF_LINE_SPACING * (STAFF_LINE_COUNT - offset_from_c4)
    return y

def offset_to_x(offset, measure_number):
    base_x = 100 + (measure_number - 1) * MEASURE_WIDTH
    return base_x + offset * 50

def generate_labels(xml_path, png_path, label_path):
    try:
        score = converter.parse(xml_path)
        s = score.parts[0]
    except Exception as e:
        print(f"Failed to parse {xml_path}: {e}")
        return

    try:
        img = Image.open(png_path)
        w, h = img.size
    except Exception as e:
        print(f"Failed to open image {png_path}: {e}")
        return

    lines = []
    for m in s.getElementsByClass('Measure'):
        mnum = m.measureNumber
        for n in m.notesAndRests:
            targets = []
            if isinstance(n, note.Note):
                targets = [n.pitch]
            elif isinstance(n, chord.Chord):
                targets = n.pitches
            else:
                continue

            for pitch in targets:
                x = offset_to_x(n.offset, mnum)
                y = pitch_to_y(pitch)

                x_norm = x / w
                y_norm = y / h
                w_norm = NOTEHEAD_WIDTH / w
                h_norm = NOTEHEAD_HEIGHT / h

                class_id = 0  # just noteheads for now
                lines.append(f"{class_id} {x_norm:.6f} {y_norm:.6f} {w_norm:.6f} {h_norm:.6f}")

    with open(label_path, "w") as f:
        f.write("\n".join(lines))

if __name__ == "__main__":
    for fname in os.listdir(XML_DIR):
        if fname.endswith(".musicxml"):
            base = os.path.splitext(fname)[0]  # e.g., sample_0
            xml_path = os.path.join(XML_DIR, fname)
            png_path = os.path.join(PNG_DIR, base + "-1.png")
            label_path = os.path.join(LABELS_DIR, base + ".txt")

            print(f"Processing {base}")
            generate_labels(xml_path, png_path, label_path)
