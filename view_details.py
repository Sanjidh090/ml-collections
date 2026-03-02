!pip install pandas pyyaml pillow moviepy
import os

# Try to import optional modules
try:
    import pandas as pd
except ImportError:
    pd = None
try:
    import yaml
except ImportError:
    yaml = None
try:
    from PIL import Image
except ImportError:
    Image = None
try:
    import moviepy.editor as mp
except ImportError:
    mp = None

def preview_file(path, max_lines=5):
    """Returns a preview string for the file at the given path."""
    ext = os.path.splitext(path)[1].lower()
    preview = ""
    if ext == ".csv":
        if pd:
            try:
                df = pd.read_csv(path)
                preview += f"\n[CSV] Columns: {list(df.columns)}"
                preview += f"\n[CSV] First rows:\n{df.head(max_lines).to_string(index=False)}"
            except Exception as e:
                preview += f"\n[CSV Read Error]: {e}"
        else:
            preview += "\n[pandas not installed, cannot preview CSV]"
    elif ext in [".yaml", ".yml"]:
        try:
            with open(path, "r") as f:
                lines = [next(f) for _ in range(max_lines)]
            preview += "\n[YAML] First lines:\n" + "".join(lines)
        except Exception as e:
            preview += f"\n[YAML Read Error]: {e}"
    elif ext in [".mp4", ".avi", ".mov", ".mkv"]:
        if mp:
            try:
                clip = mp.VideoFileClip(path)
                preview += f"\n[VIDEO] Duration: {clip.duration}s, Resolution: {clip.size}, FPS: {clip.fps}"
                preview += f"\n[VIDEO] Format: {ext.upper()}"
            except Exception as e:
                preview += f"\n[Video Read Error]: {e}"
        else:
            preview += "\n[moviepy not installed, cannot preview video]"
    elif ext in [".jpg", ".jpeg", ".png", ".bmp", ".gif"]:
        if Image:
            try:
                with Image.open(path) as img:
                    preview += f"\n[IMG] Size: {img.size}, Mode: {img.mode}, Format: {img.format}"
            except Exception as e:
                preview += f"\n[Image Read Error]: {e}"
        else:
            preview += "\n[Pillow not installed, cannot preview images]"
    elif ext in [".txt", ".md", ".log", ".py", ".json"]:
        try:
            with open(path, "r") as f:
                lines = [next(f) for _ in range(max_lines)]
            preview += "\n[TEXT] First lines:\n" + "".join(lines)
        except Exception as e:
            preview += f"\n[Text Read Error]: {e}"
    else:
        try:
            size = os.path.getsize(path)
            preview += f"\n[OTHER] Size: {size} bytes"
        except:
            preview += "\n[Unknown file type]"
    return preview

def print_tree(start_path, prefix="", max_items=3, max_lines=5):
    """Recursively prints directory structure in ASCII format and file previews."""
    try:
        items = sorted(os.listdir(start_path))
    except FileNotFoundError:
        print(f"Error: Path '{start_path}' not found.")
        return
    except PermissionError:
        print(f"Error: Permission denied for '{start_path}'.")
        return

    show_items = items[:max_items]
    more_items = len(items) > max_items

    for index, item in enumerate(show_items):
        path = os.path.join(start_path, item)
        last_item = (index == len(show_items) - 1) and not more_items
        connector = "└── " if last_item else "├── "
        print(prefix + connector + item)
        if os.path.isdir(path):
            extension = "    " if last_item else "│   "
            print_tree(path, prefix + extension, max_items=max_items, max_lines=max_lines)
        else:
            preview = preview_file(path, max_lines=max_lines)
            preview_lines = preview.splitlines()
            for line in preview_lines:
                print(prefix + ("    " if last_item else "│   ") + line)
    if more_items:
        connector = "└── " if True else "├── "
        print(prefix + connector + ",.......")

# Example usage:
if __name__ == "__main__":
    dataset_path = "/kaggle/input/competitions/accident"  # Change to your dataset folder
    print(f"Dataset structure for: {dataset_path}")
    print_tree(dataset_path)
