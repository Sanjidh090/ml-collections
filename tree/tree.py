import os
from collections import Counter

def tree(path, prefix="", limit=5, root=True):
    items = sorted(os.listdir(path))
    dirs = [x for x in items if os.path.isdir(os.path.join(path, x))]
    files = [x for x in items if os.path.isfile(os.path.join(path, x))]

    if root:
        types = Counter(os.path.splitext(f)[1].lower().lstrip(".") or "other" for f in files)
        info = [f"{len(dirs)} folders"] + [f"{n} {ext}" for ext, n in types.items()]
        print(f"{os.path.basename(os.path.normpath(path))}/ {{{', '.join(info)}}}")

    shown = (dirs + files)[:limit]

    for i, name in enumerate(shown):
        full = os.path.join(path, name)
        more = len(dirs + files) > limit
        last = i == len(shown)-1 and not more
        branch = "└── " if last else "├── "

        if os.path.isdir(full):
            sub = os.listdir(full)
            sub_dirs = [x for x in sub if os.path.isdir(os.path.join(full, x))]
            sub_files = [x for x in sub if os.path.isfile(os.path.join(full, x))]
            types = Counter(os.path.splitext(f)[1].lower().lstrip(".") or "other"
                            for f in sub_files)

            info = [f"{len(sub_dirs)} folders"] + \
                   [f"{n} {ext}" for ext, n in types.items()]

            print(prefix + branch + f"{name}/ {{{', '.join(info)}}}")

            tree(
                full,
                prefix + ("    " if last else "│   "),
                limit,
                root=False
            )
        else:
            print(prefix + branch + name)

    if len(dirs + files) > limit:
        print(prefix + f"└── ... ({len(dirs + files)-limit} more items)")


# Path
tree("/kaggle/working/", limit=5)
