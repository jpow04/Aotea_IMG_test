import os
import subprocess
import glob
import tempfile


def merge_tif_files(input_dir, output_dir, output_filename):
    # Ensure the output directory exists
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Construct the output file path
    output_filepath = os.path.join(output_dir, output_filename)

    # List all .tif files in the input directory
    tif_files = glob.glob(os.path.join(input_dir, '*.tif'))

    if not tif_files:
        print(f"No .tif files found in {input_dir}")
        return

    # Create a temporary file to hold the list of .tif files
    with tempfile.NamedTemporaryFile(delete=False, mode='w') as tmpfile:
        tmpfile_name = tmpfile.name
        for tif_file in tif_files:
            tmpfile.write(tif_file + '\n')

    # Prepare the gdal_merge.py command
    cmd = f'gdal_merge -o {output_filepath} --optfile {tmpfile_name}'

    # Execute the command
    subprocess.call(cmd, shell=True)

    # Clean up the temporary file
    os.remove(tmpfile_name)

    print(f"Merged .tif files into: {output_filepath}")


if __name__ == "__main__":
    input_directory = r"C:\Users\powelj\Documents\Aotea_test_files\Landsat\dem"
    output_directory = r"C:\Users\powelj\Documents\Aotea_test_files\Landsat"
    output_filename = "merged_dem.tif"

    merge_tif_files(input_directory, output_directory, output_filename)