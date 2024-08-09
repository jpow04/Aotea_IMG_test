import os
import subprocess
from tqdm import tqdm

# Function to apply "arcsiextractdata.py" command to zipped files within subfolders within an input directory
def extract_landsat_data(raw_base_dir, temp_dir):

    # Check for and create temp directory
    if not os.path.exists(temp_dir):
        os.makedirs(temp_dir)
        print("Created temp directory {}".format(temp_dir))

    # Run command through all subfolders
    for root, dirs, files in tqdm(os.walk(raw_base_dir), desc="Extracting landsat data"):
        for file in files:
            if file.endswith('.tar'):
                input_dir = root  # Use the directory containing the .tar file
                extract_command = f"arcsiextractdata.py -i {input_dir} -o {temp_dir}"
                subprocess.run(extract_command, shell=True)
                tqdm.write(f"Extracted data from {input_dir} to {temp_dir}")


# Script directories
if __name__ == "__main__":
    raw_base_directory = r"C:\Users\powelj\Documents\Aotea_test_files\Landsat\RAW"
    temp_directory = r"C:\Users\powelj\Documents\Aotea_test_files\Landsat\tmp"
    extract_landsat_data(raw_base_directory, temp_directory)
