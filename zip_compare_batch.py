import os
import zip_compare

def batch_compare(zip_folder, target_folder, chunk_size=1*1024*1024):
    for file_name in os.listdir(zip_folder):
        if file_name.endswith('.zip'):
            zip_path = os.path.join(zip_folder, file_name)
            folder_path = os.path.join(target_folder, os.path.splitext(file_name)[0])
            if os.path.isdir(folder_path):
                print(f"Comparing {zip_path} with {folder_path}")
                if zip_compare.compare_files_in_zip_and_folder(zip_path, folder_path, chunk_size):
                    print(f"The zip file {zip_path} and the folder {folder_path} are identical.")
                else:
                    print(f"The zip file {zip_path} and the folder {folder_path} are not identical.")
            else:
                print(f"Corresponding folder for {zip_path} does not exist in {target_folder}")

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Batch compare zip files and folders.")
    parser.add_argument("zip_folder", help="Path to the folder containing zip files")
    parser.add_argument("target_folder", help="Path to the folder containing corresponding folders")
    parser.add_argument("--chunk-size", type=int, default=1*1024*1024, help="Chunk size in bytes for reading files (default: 1 MB)")

    args = parser.parse_args()

    batch_compare(args.zip_folder, args.target_folder, args.chunk_size)

# python zip_compare_batch.py zip-comparison/ zip-comparison/