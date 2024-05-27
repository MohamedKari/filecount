from pathlib import Path
import argparse
from typing import Iterable, Optional
import hashlib
import json 

class Breakddown:
    def __init__(self, 
        counts_per_direct_child_dir: dict[Path, int], 
        direct_child_files: list[Path]
    ) -> None:
        self.counts_per_direct_child_dir = counts_per_direct_child_dir
        self.direct_child_files = direct_child_files
    
    def to_stdout(self) -> None:
        print(f"{breakdown_dir}:")
        for d_name, d_count in self.counts_per_direct_child_dir.items():
            print(f"{d_count: 8}  {d_name}")
        
        f_count = len(self.direct_child_files)
        f_name = "direct child files"
        print(f"{f_count: 6}  {f_name}")

    @classmethod
    def compute_at_directory(cls, breakdown_dir: Path | str, counts_per_directory: dict[Path, int]) -> "Breakddown":
        breakdown_dir = Path(breakdown_dir)

        direct_children = list(breakdown_dir.glob("*"))
        direct_child_dirs = [child for child in direct_children if child.is_dir()]
        direct_child_files = [child for child in direct_children if child.is_file()]

        # aggregate
        counts_per_child_dir: dict[str, int] = {
            str(d.absolute()): counts_per_directory[str(d.absolute())] 
                               if str(d.absolute()) in counts_per_directory
                               else 0
            for d in direct_child_dirs
        }
        
        counts_per_child_dir = dict(sorted(counts_per_child_dir.items(), key=lambda item: item[1], reverse=True))

        return Breakddown(
            counts_per_child_dir,
            direct_child_files
        )
        

def gather_counts_per_directory(root_dir: Path | str) -> dict[Path, int]:
    print("Gathering counts per directory...")
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

def str2hash(hashable: str) -> str:
    return hashlib.md5(hashable.encode("utf8")).hexdigest()

def get_potential_cache_path(breakdown_dir: Path) -> Path:
    paths = [breakdown_dir] + list(breakdown_dir.parents)

    for p in paths:
        hash = str2hash(str(p.absolute()))
        potential_hash_file = Path(f"{hash}.json")
        if potential_hash_file.exists():
            print(f"Found cache with hash {hash} for {p}")
            return potential_hash_file
    
    return Path(f"{str2hash(str(breakdown_dir.absolute()))}.json")

if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("--use-cache", action="store_true")
    parser.add_argument("path", type=str, nargs=argparse.REMAINDER)
    args = parser.parse_args()

    breakdown_dir = Path(" ".join(args.path))
    assert breakdown_dir.is_dir()

    if args.use_cache:
        cache_file = get_potential_cache_path(breakdown_dir)
        
        if cache_file.exists():
            print(f"Loading cache at {cache_file}...")
            with cache_file.open("rt", encoding="utf8") as f:
                counts_per_directory = json.load(f,)
                # print(counts_per_directory)
        else:
            counts_per_directory = gather_counts_per_directory(breakdown_dir)
            with cache_file.open("wt", encoding="utf8") as f:
                print(f"writing cache for {breakdown_dir} to {cache_file}")
                json.dump(counts_per_directory, f, indent=1, ensure_ascii=False)
    
    Breakddown.compute_at_directory(breakdown_dir, counts_per_directory).to_stdout()