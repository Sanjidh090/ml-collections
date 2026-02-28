import os
def print_tree(start_path, prefix="", max_items=3):
    """Recursively prints directory structure in ASCII format.
    Shows only the first `max_items` in each directory, then ' ,.......' if more exist."""
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
        # Determine connector
        last_item = (index == len(show_items) - 1) and not more_items
        connector = "└── " if last_item else "├── "
        print(prefix + connector + item)
        if os.path.isdir(path):
            extension = "    " if last_item else "│   "
            print_tree(path, prefix + extension, max_items=max_items)
    if more_items:
        connector = "└── " if True else "├── "  # Always last if exists
        print(prefix + connector + ",.......")

# Example usage:
if __name__ == "__main__":
    dataset_path = "/kaggle/working/"  # Change to your dataset folder
    print(f"Dataset structure for: {dataset_path}")
    print_tree(dataset_path)
