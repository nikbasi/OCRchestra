import os
import subprocess

MUSESCORE_EXE = r"C:\Program Files\MuseScore 3\bin\MuseScore3.exe"
XML_DIR = "data/xml"
PNG_DIR = "data/png"
os.makedirs(PNG_DIR, exist_ok=True)

def convert(xml_file, png_file):
    subprocess.run([
        MUSESCORE_EXE,
        "-s",
        "-o", png_file,
        "-r", "200",
        xml_file
    ], check=True)

if __name__ == "__main__":
    for fname in os.listdir(XML_DIR):
        if fname.endswith(".musicxml"):
            xml_path = os.path.join(XML_DIR, fname)
            png_path = os.path.join(PNG_DIR, fname.replace(".musicxml", ".png"))
            print(f"Converting {xml_path} -> {png_path}")
            convert(xml_path, png_path)
