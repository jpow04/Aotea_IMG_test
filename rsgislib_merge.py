import os
import glob
import rsgislib
from rsgislib import imageutils


def merge_geotiff_files(input_dir, output_dir, output_filename):
    # Ensure the output directory exists
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Construct the output file path
    output_filepath = os.path.join(output_dir, output_filename)

    # List all GeoTIFF files in the input directory
    tiff_files = glob.glob(os.path.join(input_dir, '*.tif'))

    if not tiff_files:
        print(f"No GeoTIFF files found in {input_dir}")
        return

    # List mosaic parameters
    backgroundVal = -99.0
    skipVal = -99.0
    skipBand = 1
    overlapBehaviour = 0
    gdalformat = 'GTiff'
    datatype = rsgislib.TYPE_32FLOAT

    # Create the mosaic
    imageutils.create_img_mosaic(tiff_files, output_filepath, backgroundVal, skipVal, skipBand, overlapBehaviour, gdalformat, datatype)

    print(f"Merged GeoTIFF files into: {output_filepath}")


if __name__ == "__main__":
    input_directory = r"C:\Users\powelj\Documents\Aotea_test_files\Landsat\dem"
    output_directory = r"C:\Users\powelj\Documents\Aotea_test_files\Landsat"
    output_filename = "rsgis_merged_dem.tif"

    merge_geotiff_files(input_directory, output_directory, output_filename)