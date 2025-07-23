import os
import sys
import pathlib
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from PIL import Image

# --- Project Directories ---
# These must match the directories from your label generation script.
PNG_DIR = "data/png"
LABEL_DIR = "data/labels"
OUTPUT_DIR = "output/visualized_boxes"

# --- Class Mappings ---
# This is now a fallback for labels that don't have a specific name.
CLASS_MAP = {
    0: "note",
    1: "clef",
}
CLASS_COLORS = {
    "note": "red",
    "clef": "blue",
    "rest": "green"
}

def draw_yolo_boxes(image_path, label_path, save_path, show_plot=False):
    """
    Opens an image, reads a YOLO-formatted label file, and draws the
    bounding boxes on the image, saving the result.
    Optionally displays the plot if show_plot is True.
    """
    try:
        image = Image.open(image_path)
        width, height = image.size
        print(f"\nProcessing {os.path.basename(image_path)} | Size: {width}x{height}")
    except FileNotFoundError:
        print(f"❌ ERROR: Image file not found at '{image_path}'")
        return

    fig, ax = plt.subplots(1, figsize=(15, 20))
    ax.imshow(image)

    try:
        with open(label_path, 'r') as f:
            for line in f:
                parts = line.strip().split()
                if len(parts) < 5:
                    continue
                
                # Check if the line includes the extra note name data.
                if len(parts) == 6:
                    class_id, x_center, y_center, w, h, text_label = parts
                else: # Fallback for older 5-column format
                    class_id, x_center, y_center, w, h = parts
                    text_label = CLASS_MAP.get(int(class_id), "Unknown")
                
                # Convert numeric parts
                class_id, x_center, y_center, w, h = map(float, [class_id, x_center, y_center, w, h])
                class_id = int(class_id)

                box_w = w * width
                box_h = h * height
                x = (x_center * width) - (box_w / 2)
                y = (y_center * height) - (box_h / 2)

                # Use the generic class name for color, but specific name for the label
                generic_class_name = CLASS_MAP.get(class_id, "Unknown")
                edge_color = CLASS_COLORS.get(generic_class_name, "yellow")

                rect = patches.Rectangle(
                    (x, y), box_w, box_h, 
                    linewidth=1, 
                    edgecolor=edge_color, 
                    facecolor='none'
                )
                ax.add_patch(rect)

                # Use the specific text_label for the text
                ax.text(
                    x, y - 5, text_label, 
                    color='white', 
                    fontsize=8, 
                    bbox=dict(facecolor=edge_color, alpha=0.5, pad=1)
                )
    except FileNotFoundError:
        print(f"❌ ERROR: Label file not found at '{label_path}'")
        plt.close(fig)
        return

    plt.axis('off')
    plt.tight_layout()
    pathlib.Path(OUTPUT_DIR).mkdir(parents=True, exist_ok=True)
    plt.savefig(save_path, bbox_inches='tight', pad_inches=0)
    print(f"✅ Saved visualized image to: {save_path}")
    
    # --- MODIFICATION ---
    # Conditionally show the plot based on the 'show_plot' flag.
    if show_plot:
        # This will pause the script and show the plot for the first image.
        # Close this window to allow the program to finish.
        plt.show()
    else:
        # For all other images, just close the figure in memory.
        plt.close(fig)


if __name__ == '__main__':
    print("Starting visualization process...")
    
    try:
        label_files = [f for f in os.listdir(LABEL_DIR) if f.endswith(".txt")]
        if not label_files:
            print(f"⚠️ No label files (.txt) found in '{LABEL_DIR}'.")
            sys.exit(0)
    except FileNotFoundError:
        print(f"❌ ERROR: Label directory not found at '{LABEL_DIR}'")
        sys.exit(1)

    # --- MODIFICATION ---
    # Loop through all files, but only show the plot for the first one (i=0).
    for i, label_filename in enumerate(label_files):
        base_name = os.path.splitext(label_filename)[0]

        image_name_v1 = f"{base_name}.png"
        image_name_v2 = f"{base_name.replace('-1', '')}.png"
        
        image_path = os.path.join(PNG_DIR, image_name_v1)
        if not os.path.exists(image_path):
            image_path = os.path.join(PNG_DIR, image_name_v2)

        label_path = os.path.join(LABEL_DIR, label_filename)
        save_path = os.path.join(OUTPUT_DIR, f"{base_name}_boxed.png")
        
        # The 'show_plot' argument is True only when i is 0.
        draw_yolo_boxes(image_path, label_path, save_path, show_plot=(i == 0))

    print("\nVisualization complete for all files. Check the 'output/visualized_boxes' folder.")
