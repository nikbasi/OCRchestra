import matplotlib.pyplot as plt
import matplotlib.patches as patches
from PIL import Image
import sys
import os

def draw_yolo_boxes(image_path, label_path):
    # Load image
    image = Image.open(image_path)
    width, height = image.size

    # Create a matplotlib figure
    fig, ax = plt.subplots(1)
    ax.imshow(image)

    # Read label file
    with open(label_path, 'r') as f:
        for line in f:
            parts = line.strip().split()
            if len(parts) != 5:
                continue  # skip malformed lines
            class_id, x_center, y_center, w, h = map(float, parts)

            # Convert from YOLO format to box coordinates
            x = (x_center - w / 2) * width
            y = (y_center - h / 2) * height
            box_w = w * width
            box_h = h * height

            # Draw rectangle
            rect = patches.Rectangle((x, y), box_w, box_h, linewidth=1.5, edgecolor='red', facecolor='none')
            ax.add_patch(rect)
            ax.text(x, y, str(int(class_id)), color='yellow', fontsize=8, backgroundcolor='black')

    plt.axis('off')
    plt.tight_layout()
    plt.show()


if __name__ == '__main__':
    if len(sys.argv) != 3:
        print("Usage: python visualize_boxes.py path/to/image.png path/to/labels.txt")
        sys.exit(1)

    img_path = sys.argv[1]
    label_path = sys.argv[2]

    if not os.path.exists(img_path) or not os.path.exists(label_path):
        print("Image or label file not found.")
        sys.exit(1)

    draw_yolo_boxes(img_path, label_path)

    """
    python visualize_boxes.py data/png/sample_0-1.png data/labels/sample_0-1.txt
    """
