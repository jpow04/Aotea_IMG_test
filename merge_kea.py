import os
import subprocess
import glob
import tempfile


def merge_kea_files(input_dir, output_dir, output_filename):
    # Ensure the output directory exists
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Construct the output file path
    output_filepath = os.path.join(output_dir, output_filename)

    # List all .kea files in the input directory
    kea_files = glob.glob(os.path.join(input_dir, '*.kea'))

    if not kea_files:
        print(f"No .kea files found in {input_dir}")
        return

    # Create a temporary file to hold the list of .kea files
    with tempfile.NamedTemporaryFile(delete=False, mode='w') as tmpfile:
        tmpfile_name = tmpfile.name
        for kea_file in kea_files:
            tmpfile.write(kea_file + '\n')

    # Prepare the gdal_merge.py command
    cmd = f'gdal_merge -o {output_filepath} --optfile {tmpfile_name}'

    # Execute the command
    subprocess.call(cmd, shell=True)

    # Clean up the temporary file
    os.remove(tmpfile_name)

    print(f"Merged .kea files into: {output_filepath}")


if __name__ == "__main__":
    input_directory = r"C:\Users\powelj\Documents\Aotea_test_files\Landsat\dem2"
    output_directory = r"C:\Users\powelj\Documents\Aotea_test_files\Landsat\dem"
    output_filename = "merged_dem.kea"

    merge_kea_files(input_directory, output_directory, output_filename)