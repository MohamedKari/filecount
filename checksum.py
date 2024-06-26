import csv
import hashlib
from pathlib import Path

MAX_NUM_FILES_PER_CSV = 3

def md5_checksum(file_path):
    hash_md5 = hashlib.md5()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()

def process_files(root_dir, output_dir):
    cache = {}
    output_files = list(Path(output_dir).glob('file_hashes_*.csv'))
    
    for output_file in output_files:
        with output_file.open('r') as cache_file:
            reader = csv.reader(cache_file)
            for row in reader:
                path, md5, size = row
                cache[path] = (md5, size)

    output_index = len(output_files)
    output_path = Path(output_dir) / f"file_hashes_{output_index}.csv"
    paths_to_write = []

    file_count = sum(1 for _ in cache)
    
    for file_path in Path(root_dir).glob('**/*'):
        if file_path.is_file():
            abs_path = str(file_path.resolve())
            size = str(file_path.stat().st_size)
            if abs_path in cache and cache[abs_path][1] == size:
                continue
            else:
                md5 = md5_checksum(abs_path)
                cache[abs_path] = (md5, size)
            
            paths_to_write.append([abs_path, md5, size])
            file_count += 1
            
            if file_count >= MAX_NUM_FILES_PER_CSV:
                with output_path.open('a', newline='') as output_file:
                    writer = csv.writer(output_file)
                    writer.writerows(paths_to_write)
                paths_to_write = []
                file_count = 0
                output_index += 1
                output_path = Path(output_dir) / f"file_hashes_{output_index}.csv"

    if paths_to_write:
        with output_path.open('a', newline='') as output_file:
            writer = csv.writer(output_file)
            writer.writerows(paths_to_write)

process_files('/Users/mo/code/filecount/test-dir-0', 'out')
