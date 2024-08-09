import os
import shutil
from tqdm import tqdm

# Function to extract sentinel data (.SAFE files) from RAW directory
def extract_sentinel_data(input_dir, output_dir):
    # Check for and create temp directory
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"Created temp directory {output_dir}")

    # Collect all .SAFE files in subdirectories
    safe_files = []
    for root, dirs, files in os.walk(input_dir):
        for dir_name in dirs:
            if dir_name.endswith('.SAFE'):
                safe_files.append((root, dir_name))

    # Copy .SAFE folders from RAW to temp
    for root, dir_name in tqdm(safe_files, desc="Extracting RAW data"):
        safe_folder_path = os.path.join(root, dir_name)
        dest_folder_path = os.path.join(output_dir, dir_name)
        if not os.path.exists(dest_folder_path):
            shutil.copytree(safe_folder_path, dest_folder_path)
            tqdm.write(f"Copied {safe_folder_path} to {dest_folder_path}")


if __name__ == "__main__":
    raw_directory = "sentinel/RAW"
    temp_directory = "sentinel/tmp"

    extract_sentinel_data(raw_directory, temp_directory)
