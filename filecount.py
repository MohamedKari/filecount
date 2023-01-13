import sys
import pprint
from pathlib import Path
from argparse import ArgumentParser
from typing import Iterable

def count_files(path_to_dir: Path | str):
    path_to_dir = Path(path_to_dir)
    flat: Iterable[Path] = path_to_dir.glob("**/*")
    
    # print(list(str(f) for f in flat))

    direct_child_files: Iterable[Path] = []
    direct_child_directory: Iterable[Path] = []
    counts_per_directory: dict[str, int] = {}
    
    print("Expanding tree...")
    for p in reversed(list(flat)):
        if p.is_file() and p.parent == path_to_dir:
            direct_child_files.append(p)
            continue
        
        if p.is_dir() and p.parent == path_to_dir:
            direct_child_directory.append(p)
            continue

        if p.is_dir():
            continue

        for parent in p.parents:
            k = str(parent)
            if k in counts_per_directory:
                counts_per_directory[k] = counts_per_directory[k] + 1
            else:
                counts_per_directory[k] = 1
    
    print("Aggregating in dict...")
    counts_per_child_dir: dict[str, int] = {
        str(d): counts_per_directory[str(d)] 
                if str(d) in counts_per_directory
                else 0
        for d in direct_child_directory
    }

    print("Printing...")
    counts_per_child_dir = dict(sorted(counts_per_child_dir.items(), key=lambda item: item[1], reverse=True))

    print(f"{path_to_dir}:")
    for d_name, d_count in counts_per_child_dir.items():
        print(f"{d_count: 8}  {d_name}")
    
    f_count = len(direct_child_files)
    f_name = "direct child files"
    print(f"{f_count: 6}  {f_name}")

if __name__ == "__main__":
    count_files(sys.argv[-1])