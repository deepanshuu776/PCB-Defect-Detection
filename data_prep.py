import os
import shutil
import random
from PIL import Image

# Configuration
dataset_path = "PCBData"  # Folder containing group000xx folders
output_path = "datasets/DeepPCB_YOLO"
classes = ["open", "short", "mousebite", "spur", "copper", "pin-hole"]

def convert_to_yolo_format(bbox, img_width, img_height):
    # DeepPCB format: x1, y1, x2, y2 (min/max)
    # YOLO format: x_center, y_center, width, height (normalized 0-1)
    x1, y1, x2, y2 = bbox
    
    dw = 1. / img_width
    dh = 1. / img_height
    
    w = x2 - x1
    h = y2 - y1
    x = x1 + (w / 2.0)
    y = y1 + (h / 2.0)
    
    x = x * dw
    w = w * dw
    y = y * dh
    h = h * dh
    return (x, y, w, h)

def prepare_data():
    # Create directories
    for split in ['train', 'val']:
        os.makedirs(f"{output_path}/images/{split}", exist_ok=True)
        os.makedirs(f"{output_path}/labels/{split}", exist_ok=True)

    all_pairs = []
    
    # Walk through dataset groups
    if not os.path.exists(dataset_path):
        print(f"Error: '{dataset_path}' folder not found. Please extract the dataset here.")
        return

    for root, dirs, files in os.walk(dataset_path):
        for file in files:
            if file.endswith("_test.jpg"):
                image_path = os.path.join(root, file)
                # Annotation file has same name but .txt extension and no _test suffix usually, 
                # OR it matches the ID. In DeepPCB, 00041000_test.jpg -> 00041000.txt
                base_id = file.split('_')[0]
                anno_path = os.path.join(root, base_id + ".txt")
                
                if os.path.exists(anno_path):
                    all_pairs.append((image_path, anno_path))

    random.shuffle(all_pairs)
    split_idx = int(len(all_pairs) * 0.8)
    train_set = all_pairs[:split_idx]
    val_set = all_pairs[split_idx:]

    print(f"Found {len(all_pairs)} images. Training: {len(train_set)}, Validation: {len(val_set)}")

    def process_set(dataset, split_name):
        for img_path, anno_path in dataset:
            # Copy Image
            filename = os.path.basename(img_path)
            shutil.copy(img_path, f"{output_path}/images/{split_name}/{filename}")
            
            # Process Labels
            img = Image.open(img_path)
            w, h = img.size
            
            yolo_lines = []
            with open(anno_path, 'r') as f:
                lines = f.readlines()
                for line in lines:
                    # DeepPCB format: x1 y1 x2 y2 type
                    parts = list(map(int, line.strip().split()))
                    if len(parts) == 5:
                        x1, y1, x2, y2, cls_id = parts
                        # Map class 1-6 to 0-5
                        cls_idx = cls_id - 1 
                        if 0 <= cls_idx < len(classes):
                            bbox = convert_to_yolo_format((x1, y1, x2, y2), w, h)
                            yolo_lines.append(f"{cls_idx} {bbox[0]:.6f} {bbox[1]:.6f} {bbox[2]:.6f} {bbox[3]:.6f}")
            
            # Save Label File
            label_name = filename.replace(".jpg", ".txt")
            with open(f"{output_path}/labels/{split_name}/{label_name}", 'w') as f:
                f.write("\n".join(yolo_lines))

    process_set(train_set, 'train')
    process_set(val_set, 'val')
    
    # Create dataset.yaml for YOLO
    yaml_content = f"""
path: {os.path.abspath(output_path)}
train: images/train
val: images/val

nc: {len(classes)}
names: {classes}
    """
    with open("dataset.yaml", "w") as f:
        f.write(yaml_content)
    
    print("Data preparation complete! 'dataset.yaml' created.")

if __name__ == "__main__":
    prepare_data()