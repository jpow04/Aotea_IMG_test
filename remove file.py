import os
import re
import subprocess
from tqdm import tqdm

# Function to remove .kea files after translation to GeoTIFF
def remove_files(input_dir):
    # Check if the directory exists
    if not os.path.exists(input_dir):
        print(f"Directory {input_dir} does not exist.")
        return
    pattern = re.compile(r'SEN2.*png')  # Searches for .kea files in Sentinel format

    # Get all subdirectories in the input directory
    subdirectories = [os.path.join(input_dir, d) for d in os.listdir(input_dir) if os.path.isdir(os.path.join(input_dir, d))]

    # Initialize tqdm progress bar for subdirectories
    with tqdm(total=len(subdirectories), desc="Removing files") as pbar:
        for subdirectory in subdirectories:
            for root, dirs, files in os.walk(subdirectory):
                for file in files:
                    match = pattern.match(file)
                    if match:
                        kea_path = os.path.join(root, file)
                        try:
                            os.remove(kea_path)
                            '''tqdm.write(f"File '{kea_path}' deleted successfully.")'''  # Terminal output

                        except Exception as e:  # Report errors
                            tqdm.write(f"Failed to remove {kea_path}: {e}")

                pbar.update(1)  # Update the progress bar after processing each subdirectory


# Execute script
if __name__ == "__main__":
    # Define directories
    output_directory = r"C:\Users\powelj\Documents\Aotea_test_files\Sentinel\Outputs"
    # Call functions
    remove_files(output_directory)
