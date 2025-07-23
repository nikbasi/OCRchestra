import os
import random
from music21 import stream, note, chord, metadata

OUTPUT_XML_DIR = "data/xml"
os.makedirs(OUTPUT_XML_DIR, exist_ok=True)

def generate_random_score(length=4):
    s = stream.Score()
    p = stream.Part()
    s.insert(0, metadata.Metadata())
    s.metadata.title = "Synthetic Example"
    s.metadata.composer = "OCRchestraBot"

    for _ in range(length):
        duration = 1 #random.choice([0.25, 0.5, 1.0])  # 16th, 8th, quarter notes
        pitch = random.choice(['C4', 'D4', 'E4', 'F4', 'G4', 'A4', 'B4', 'C5'])
        if random.random() < 0.2:
            # n = chord.Chord([pitch, random.choice(['E4', 'G4'])])
            # To keep spacing even, let's simplify to single notes for now
            n = note.Note(pitch)
        else:
            n = note.Note(pitch)
        n.quarterLength = duration
        p.append(n)

    s.append(p)
    return s

if __name__ == "__main__":
    for i in range(20):
        score = generate_random_score()
        filepath = os.path.join(OUTPUT_XML_DIR, f"sample_{i}.musicxml")
        score.write("musicxml", filepath)
        print(f"Generated {filepath}")
