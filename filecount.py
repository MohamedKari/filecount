import sys
import pprint
from pathlib import Path
from argparse import ArgumentParser
from typing import Iterable

def gather_counts_per_directory(root_dir: Path | str) -> dict[Path, int]:
    root_dir = Path(root_dir)
    assert root_dir.is_dir()

    flat: Iterable[Path] = root_dir.glob("**/*")
    counts_per_directory: dict[str, int] = {}
    for p in reversed(list(flat)):
        if p.is_dir():
            continue

        for parent in p.parents:
            k = str(parent)
            if k in counts_per_directory:
                counts_per_directory[k] = counts_per_directory[k] + 1
            else:
                counts_per_directory[k] = 1

    return counts_per_directory

def get_breatkdown_at_directory(breakdown_dir: Path | str):
    breakdown_dir = Path(breakdown_dir)

    direct_children = list(breakdown_dir.glob("*"))
    direct_child_dirs = [child for child in direct_children if child.is_dir()]
    direct_child_files = [child for child in direct_children if child.is_file()]

    counts_per_directory = gather_counts_per_directory(breakdown_dir)

    # aggregate
    counts_per_child_dir: dict[str, int] = {
        str(d): counts_per_directory[str(d)] 
                if str(d) in counts_per_directory
                else 0
        for d in direct_child_dirs
    }
    
    counts_per_child_dir = dict(sorted(counts_per_child_dir.items(), key=lambda item: item[1], reverse=True))

    print(f"{breakdown_dir}:")
    for d_name, d_count in counts_per_child_dir.items():
        print(f"{d_count: 8}  {d_name}")
    
    f_count = len(direct_child_files)
    f_name = "direct child files"
    print(f"{f_count: 6}  {f_name}")


if __name__ == "__main__":
    get_breatkdown_at_directory(" ".join(sys.argv[1:]))