import os
import pathlib
from PIL import Image
from music21 import converter, note, chord, clef

# --- Project Directories ---
# These should match the directories used by your PNG generation script.
XML_DIR = "data/xml"
PNG_DIR = "data/png"
LABEL_DIR = "data/labels"

# --- Bounding Box Calibration ---
# This is the most important section. You only need to set the F5_Y_POSITION.
# 1. Open a generated PNG in an image editor.
# 2. Find a note on the TOP line of the staff (this is F5 in the treble clef).
# 3. Measure the Y-pixel coordinate of the CENTER of that notehead.
F5_Y_POSITION = 351.6      # The Y-pixel coordinate for the note F5.
STAFF_LINE_SPACING = 13.775   # The pixel distance between two lines on a staff.

# Note size and position fine-tuning
NOTEHEAD_WIDTH = 18          # The width of a notehead's bounding box.
NOTEHEAD_HEIGHT = 13         # The height of a notehead's bounding box.
LEFT_MARGIN_PIXELS = 295     # Fine-tuned horizontal start position.
RIGHT_MARGIN_PIXELS = 100    # Approx. right-side padding.

# Map symbols to class IDs for YOLO
CLASS_MAP = {
    "note": 0,
    "clef": 1,
}
# --- End of Configuration ---

# --- AUTOMATIC CALCULATION (Do not change) ---
# The script internally uses C4 as its reference anchor (0-point).
# We calculate its position automatically based on your F5 measurement.
# F5 is 9 diatonic steps above C4 (C,D,E,F,G,A,B,C,D,E,F -> count the letters after C).
# Wait, C-D-E-F-G-A-B-C-D-E-F is 11 steps. Let's use music21's numbers.
# F5 diatonicNoteNum is 38. C4 is 29. The difference is 9. Correct.
C4_Y_POSITION = F5_Y_POSITION + 10 * (STAFF_LINE_SPACING / 2)


def generate_labels():
    """
    Generates YOLO label files by reading existing PNGs and their
    corresponding MusicXML data. Now includes the specific note name in the label file.
    """
    pathlib.Path(LABEL_DIR).mkdir(parents=True, exist_ok=True)

    try:
        png_files = [f for f in os.listdir(PNG_DIR) if f.endswith(".png")]
        if not png_files:
            print(f"⚠️ No .png files found in '{PNG_DIR}'. Please run your PNG generation script first.")
            return
    except FileNotFoundError:
        print(f"❌ ERROR: Image directory not found: '{PNG_DIR}'")
        return

    for png_filename in png_files:
        base_name = os.path.splitext(png_filename)[0]
        png_path = os.path.join(PNG_DIR, png_filename)
        xml_filename = png_filename.replace("-1.png", ".musicxml").replace(".png", ".musicxml")
        xml_path = os.path.join(XML_DIR, xml_filename)
        label_path = os.path.join(LABEL_DIR, f"{base_name}.txt")

        if not os.path.exists(xml_path):
            print(f"  ⚠️ WARNING: Skipping {png_filename}, no matching MusicXML file found.")
            continue

        print(f"▶️ Processing: {png_filename}")

        try:
            with Image.open(png_path) as img:
                img_width, img_height = img.size

            score = converter.parse(xml_path)
            part = score.parts[0]
            yolo_labels = []
            drawable_width = img_width - LEFT_MARGIN_PIXELS - RIGHT_MARGIN_PIXELS
            score_duration = part.highestTime

            for element in part.flatten().notesAndRests:
                x_center = LEFT_MARGIN_PIXELS + (element.offset / score_duration) * drawable_width

                if isinstance(element, note.Note):
                    pitch_name = element.pitch.nameWithOctave
                    # Calculate distance from the C4 anchor
                    offset_from_c4 = (element.pitch.diatonicNoteNum - 29)
                    y_center = C4_Y_POSITION - offset_from_c4 * (STAFF_LINE_SPACING / 2)
                    class_id = CLASS_MAP["note"]
                    box_w, box_h = NOTEHEAD_WIDTH, NOTEHEAD_HEIGHT
                    yolo_labels.append(yolo_format(x_center, y_center, box_w, box_h, img_width, img_height, class_id, pitch_name))

                elif isinstance(element, chord.Chord):
                    for p in element.pitches:
                        pitch_name = p.nameWithOctave
                        offset_from_c4 = (p.diatonicNoteNum - 29)
                        y_center_chord = C4_Y_POSITION - offset_from_c4 * (STAFF_LINE_SPACING / 2)
                        class_id = CLASS_MAP["note"]
                        yolo_labels.append(yolo_format(x_center, y_center_chord, NOTEHEAD_WIDTH, NOTEHEAD_HEIGHT, img_width, img_height, class_id, pitch_name))

            with open(label_path, "w") as f:
                f.write("\n".join(yolo_labels))
            print(f"  ✅ Generated labels: {label_path}")

        except Exception as e:
            print(f"  ❌ ERROR: Failed to generate labels for {png_filename}. Reason: {e}")

    print("-" * 40)
    print("Label generation complete.")

def yolo_format(x_center, y_center, box_w, box_h, img_w, img_h, class_id, note_name=""):
    """
    Converts absolute pixel coordinates to YOLO's format.
    MODIFIED: Now includes the note name as a 6th column for visualization purposes.
    """
    x_norm = x_center / img_w
    y_norm = y_center / img_h
    w_norm = box_w / img_w
    h_norm = box_h / img_h
    return f"{class_id} {x_norm:.6f} {y_norm:.6f} {w_norm:.6f} {h_norm:.6f} {note_name}"

if __name__ == "__main__":
    generate_labels()
