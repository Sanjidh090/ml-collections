# !pip install pandas pyyaml pillow
# moviepy removed — no audio/display on Kaggle; use ffprobe instead
import os
import subprocess

try:
    import pandas as pd
except ImportError:
    pd = None
try:
    from PIL import Image
except ImportError:
    Image = None


def _video_info_ffprobe(path):
    """Get video metadata via ffprobe (available on Kaggle by default)."""
    try:
        result = subprocess.run(
            ["ffprobe", "-v", "quiet", "-print_format", "json", "-show_streams", path],
            capture_output=True, text=True, timeout=10
        )
        import json
        data = json.loads(result.stdout)
        v = next((s for s in data.get("streams", []) if s["codec_type"] == "video"), None)
        if v:
            return f"\n[VIDEO] Duration: {v.get('duration', '?')}s, Resolution: {v.get('width')}x{v.get('height')}, FPS: {v.get('r_frame_rate', '?')}"
    except Exception as e:
        return f"\n[Video Read Error]: {e}"
    return "\n[VIDEO] No video stream found"

def _df_preview(df, label, total_rows=None):
    """Truncate cell values and format a compact head preview."""
    MAX_COL_WIDTH = 40
    display = df.copy()
    for col in display.columns:
        if display[col].dtype == object:
            display[col] = display[col].astype(str).str[:MAX_COL_WIDTH + 1].apply(
                lambda v: v[:MAX_COL_WIDTH] + "…" if len(v) > MAX_COL_WIDTH else v
            )
    shape = f"{total_rows}x{df.shape[1]}" if total_rows else f"?x{df.shape[1]}"
    return f"\n[{label}] Shape: {shape} | Columns: {list(df.columns)}\n{display.to_string(index=False)}"


def preview_file(path, max_lines=5):
    """Returns a preview string for the file at the given path."""
    ext = os.path.splitext(path)[1].lower()
    preview = ""

    # --- Tabular ---
    if ext == ".csv":
        if pd:
            try:
                total = sum(1 for _ in open(path, encoding="utf-8", errors="replace")) - 1
                df = pd.read_csv(path, nrows=max_lines)
                preview += _df_preview(df, "CSV", total)
            except Exception as e:
                preview += f"\n[CSV Read Error]: {e}"
        else:
            preview += "\n[pandas not installed]"

    elif ext == ".tsv":
        if pd:
            try:
                total = sum(1 for _ in open(path, encoding="utf-8", errors="replace")) - 1
                df = pd.read_csv(path, sep="\t", nrows=max_lines)
                preview += _df_preview(df, "TSV", total)
            except Exception as e:
                preview += f"\n[TSV Read Error]: {e}"
        else:
            preview += "\n[pandas not installed]"

    elif ext == ".parquet":
        if pd:
            try:
                full = pd.read_parquet(path)
                df = full.head(max_lines)
                preview += _df_preview(df, "PARQUET", len(full))
            except Exception as e:
                preview += f"\n[Parquet Read Error]: {e}"
        else:
            preview += "\n[pandas not installed]"

    elif ext in [".feather", ".arrow"]:
        if pd:
            try:
                full = pd.read_feather(path)
                df = full.head(max_lines)
                preview += _df_preview(df, "FEATHER", len(full))
            except Exception as e:
                preview += f"\n[Feather Read Error]: {e}"
        else:
            preview += "\n[pandas not installed]"

    elif ext in [".h5", ".hdf5"]:
        if pd:
            try:
                with pd.HDFStore(path, mode="r") as store:
                    keys = store.keys()
                    preview += f"\n[HDF5] Keys: {keys}"
                    if keys:
                        full = store[keys[0]]
                        df = full.head(max_lines)
                        preview += _df_preview(df, keys[0], len(full))
            except Exception as e:
                preview += f"\n[HDF5 Read Error]: {e}"
        else:
            preview += "\n[pandas not installed]"

    elif ext in [".db", ".sqlite", ".sqlite3"]:
        try:
            import sqlite3
            con = sqlite3.connect(path)
            tables = con.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
            preview += f"\n[SQLITE] Tables: {[t[0] for t in tables]}"
            if tables:
                cols_desc = con.execute(f"SELECT * FROM '{tables[0][0]}' LIMIT 0").description
                cols = [d[0] for d in cols_desc]
                rows = con.execute(f"SELECT * FROM '{tables[0][0]}' LIMIT {max_lines}").fetchall()
                preview += f"\n  [{tables[0][0]}] Columns: {cols}\n"
                preview += "\t".join(cols) + "\n"
                preview += "\n".join(["\t".join(str(v) for v in row) for row in rows])
            con.close()
        except Exception as e:
            preview += f"\n[SQLite Read Error]: {e}"

    elif ext == ".pkl":
        if pd:
            try:
                obj = pd.read_pickle(path)
                if isinstance(obj, pd.DataFrame):
                    preview += _df_preview(obj.head(max_lines), "PKL/DataFrame", len(obj))
                else:
                    preview += f"\n[PKL] Type: {type(obj).__name__} | Value: {str(obj)[:200]}"
            except Exception as e:
                preview += f"\n[Pickle Read Error]: {e}"
        else:
            preview += "\n[pandas not installed]"

    elif ext == ".npy":
        try:
            import numpy as np
            arr = np.load(path, allow_pickle=False)
            preview += f"\n[NPY] Shape: {arr.shape}, dtype: {arr.dtype}\n{arr[:max_lines]}"
        except Exception as e:
            preview += f"\n[NPY Read Error]: {e}"

    elif ext == ".npz":
        try:
            import numpy as np
            npz = np.load(path, allow_pickle=False)
            for key in list(npz.keys())[:3]:
                preview += f"\n[NPZ] '{key}': shape={npz[key].shape}, dtype={npz[key].dtype}"
        except Exception as e:
            preview += f"\n[NPZ Read Error]: {e}"

    # --- Text / Code / Markup --- (skipped, size only)
    elif ext in [
        ".ipynb", ".json", ".jsonl", ".ndjson",
        ".txt", ".md", ".log", ".py",
        ".yaml", ".yml", ".xml", ".html", ".rst"
    ]:
        try:
            size = os.path.getsize(path)
            preview += f"\n[{ext.upper().lstrip('.')}] {size:,} bytes"
        except Exception:
            preview += f"\n[{ext.upper().lstrip('.')}] size unknown"

    # --- Media ---
    elif ext in [".mp4", ".avi", ".mov", ".mkv", ".webm"]:
        preview += _video_info_ffprobe(path)

    elif ext in [".jpg", ".jpeg", ".png", ".bmp", ".gif", ".webp", ".tiff"]:
        if Image:
            try:
                with Image.open(path) as img:
                    preview += f"\n[IMG] Size: {img.size}, Mode: {img.mode}, Format: {img.format}"
            except Exception as e:
                preview += f"\n[Image Read Error]: {e}"
        else:
            preview += "\n[Pillow not installed]"

    elif ext in [".mp3", ".wav", ".flac", ".ogg"]:
        try:
            result = subprocess.run(
                ["ffprobe", "-v", "quiet", "-print_format", "json", "-show_streams", path],
                capture_output=True, text=True, timeout=10
            )
            import json
            data = json.loads(result.stdout)
            a = next((s for s in data.get("streams", []) if s["codec_type"] == "audio"), None)
            if a:
                preview += f"\n[AUDIO] Duration: {a.get('duration', '?')}s, Codec: {a.get('codec_name')}, Sample rate: {a.get('sample_rate')}Hz, Channels: {a.get('channels')}"
        except Exception as e:
            preview += f"\n[Audio Read Error]: {e}"

    # --- Archives ---
    elif ext == ".zip":
        try:
            import zipfile
            with zipfile.ZipFile(path) as z:
                names = z.namelist()
                preview += f"\n[ZIP] {len(names)} files | First {min(max_lines, len(names))}: {names[:max_lines]}"
        except Exception as e:
            preview += f"\n[ZIP Read Error]: {e}"

    elif ext in [".tar", ".gz", ".bz2", ".xz"]:
        try:
            import tarfile
            with tarfile.open(path) as t:
                names = t.getnames()
                preview += f"\n[TAR] {len(names)} files | First {min(max_lines, len(names))}: {names[:max_lines]}"
        except Exception as e:
            preview += f"\n[TAR Read Error]: {e}"

    # --- Fallback ---
    else:
        try:
            size = os.path.getsize(path)
            preview += f"\n[OTHER] Size: {size} bytes"
        except Exception:
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
            child_prefix = prefix + ("    " if last_item else "│   ")
            for line in preview.splitlines():
                print(child_prefix + line)

    if more_items:
        print(prefix + "└── .......")


if __name__ == "__main__":
    dataset_path = "/kaggle/input/"
    print(f"Dataset structure for: {dataset_path}")
    print_tree(dataset_path)
