import os
import zipfile
import hashlib
import argparse

zip_exclusions = ['__MACOSX', '.DS_Store']
folder_exclusions = ['.DS_Store']

def get_file_checksum(file_path, is_zip=False, chunk_size=1*1024*1024):
    hash_md5 = hashlib.md5()
    if is_zip:
        with file_path as file:
            for chunk in iter(lambda: file.read(chunk_size), b""):
                hash_md5.update(chunk)
    else:
        with open(file_path, "rb") as file:
            for chunk in iter(lambda: file.read(chunk_size), b""):
                hash_md5.update(chunk)
    return hash_md5.hexdigest()

def write_list_to_file(file_list, file_path):
    with open(file_path, 'w') as file:
        for item in file_list:
            file.write(f"{item}\n")

def normalize_zip_path(zip_path, root_folder_name):
    if zip_path.startswith(root_folder_name + '/'):
        return zip_path[len(root_folder_name) + 1:]
    return zip_path

def should_exclude(file_name, exclusions):
    return any(file_name.startswith(exclusion) or file_name.endswith(exclusion) for exclusion in exclusions)

def compare_files_in_zip_and_folder(zip_path, folder_path, chunk_size):
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_file_list = zip_ref.namelist()
        if zip_file_list:
            root_folder_name = zip_file_list[0].split('/')[0]
        else:
            root_folder_name = ''
        
        zip_file_list = sorted([
            normalize_zip_path(name, root_folder_name) 
            for name in zip_ref.namelist() 
            if not name.endswith('/') and not should_exclude(name, zip_exclusions)
        ])

        folder_file_list = []
        for root, _, files in os.walk(folder_path):
            for file in files:
                if not should_exclude(file, folder_exclusions):
                    file_path = os.path.relpath(os.path.join(root, file), folder_path)
                    folder_file_list.append(file_path)
        folder_file_list = sorted(folder_file_list)

        zip_file_list_name = os.path.basename(zip_path) + '_zip_file_list.txt'
        folder_file_list_name = os.path.basename(zip_path) + '_folder_file_list.txt'

        if zip_file_list != folder_file_list:
            write_list_to_file(zip_file_list, zip_file_list_name)
            write_list_to_file(folder_file_list, folder_file_list_name)
            print(f"File names or structure do not match. Check {zip_file_list_name} and {folder_file_list_name} for details.")
            return False

        for file_name in zip_file_list:
            with zip_ref.open(root_folder_name + '/' + file_name) as zip_file:
                folder_file_path = os.path.join(folder_path, file_name)
                if not os.path.exists(folder_file_path):
                    print(f"File {folder_file_path} is missing in the folder.")
                    return False
                
                zip_file_info = zip_ref.getinfo(root_folder_name + '/' + file_name)
                if os.path.getsize(folder_file_path) != zip_file_info.file_size:
                    print(f"File size mismatch for {file_name}.")
                    return False

                zip_file_checksum = get_file_checksum(zip_file, is_zip=True, chunk_size=chunk_size)
                folder_file_checksum = get_file_checksum(folder_file_path, chunk_size=chunk_size)

                if zip_file_checksum != folder_file_checksum:
                    print(f"File content mismatch for {file_name}. Zip file checksum: {zip_file_checksum}, Folder file checksum: {folder_file_checksum}.")
                    return False
                
                # print(f"{folder_file_path} {zip_file_checksum} matches {folder_file_checksum}")
                print(".", end="", flush=True)

    return True

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Compare the contents of a zip file and a folder.")
    parser.add_argument("zip_path", help="Path to the zip file")
    parser.add_argument("folder_path", help="Path to the folder")
    parser.add_argument("--chunk-size", type=int, default=1*1024*1024, help="Chunk size in bytes for reading files (default: 1 MB)")

    args = parser.parse_args()

    if compare_files_in_zip_and_folder(args.zip_path, args.folder_path, args.chunk_size):
        print("The zip file and the folder are identical.")
    else:
        print("The zip file and the folder are not identical.")

# python zip_compare.py zip-comparison/mdfprocessor.zip zip-comparison/mdfprocessor