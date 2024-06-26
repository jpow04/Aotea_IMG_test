import os
import subprocess

# Set your input directory
input_directory = r'C:\Users\powelj\Documents\ARCSI_test\Outputs\LS5TM_19950815_latn517lonw0028_r24p203'


def convert_kea_to_geotiff(input_dir):
    # List all files in the directory
    files = os.listdir(input_dir)

    # Filter out .kea files
    kea_files = [file for file in files if file.endswith('.kea')]

    # Convert each .kea file to .tif
    for kea_file in kea_files:
        kea_path = os.path.join(input_dir, kea_file)
        tiff_path = os.path.join(input_dir, kea_file.replace('.kea', '.tif'))

        try:
            # Run gdal_translate command
            subprocess.run(['gdal_translate', '-of', 'GTiff', kea_path, tiff_path], check=True)
            print(f"Successfully converted {kea_file} to {tiff_path}")
        except subprocess.CalledProcessError as e:
            print(f"Failed to convert {kea_file}: {e}")


if __name__ == "__main__":
    convert_kea_to_geotiff(input_directory)
