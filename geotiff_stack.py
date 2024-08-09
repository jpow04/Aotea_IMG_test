import os
import rasterio
from rasterio.merge import merge
from rasterio.enums import Resampling


def stack_layers(input_dir, output_dir):
    input_dir_name = os.path.basename(os.path.normpath(input_dir))
    # Create the output directory if it doesn't exist
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Traverse the input directory
    for root, dirs, files in os.walk(input_dir):
        bands = []
        for file in files:
            if file.endswith('.TIF'):
                bands.append(os.path.join(root, file))

        if bands:
            # Sort the bands to ensure consistent order
            bands.sort()

            # Open the files as a list of rasterio datasets
            datasets = [rasterio.open(fp) for fp in bands]

            # Read the first dataset to get the metadata
            meta = datasets[0].meta.copy()
            meta.update(count=len(datasets))

            # Create the output file path
            relative_path = os.path.relpath(root, input_dir)
            output_folder = os.path.join(output_dir, relative_path)
            if not os.path.exists(output_folder):
                os.makedirs(output_folder)

            output_filepath = os.path.join(output_folder, f"{input_dir_name}.TIF")

            # Write the stacked layers to the output file
            with rasterio.open(output_filepath, 'w', **meta) as dest:
                for idx, dataset in enumerate(datasets):
                    dest.write_band(idx + 1, dataset.read(1, resampling=Resampling.bilinear))

            print(f"Stacked image saved to: {output_filepath}")


if __name__ == "__main__":
    input_directory = r"C:\Users\powelj\Documents\Aotea_test_files\Landsat\Clipped\LT04_L1TP_073085_19901216_20200915_02_T1"
    output_directory = r"C:\Users\powelj\Documents\Aotea_test_files\Landsat\Stacked"
    stack_layers(input_directory, output_directory)
