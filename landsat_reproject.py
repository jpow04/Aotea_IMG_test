import os
import shutil
import rasterio
from rasterio.warp import calculate_default_transform, reproject, Resampling


def reproject_raster(input_filepath, output_filepath, dst_crs='EPSG:2193'):
    with rasterio.open(input_filepath) as src:
        transform, width, height = calculate_default_transform(
            src.crs, dst_crs, src.width, src.height, *src.bounds)

        kwargs = src.meta.copy()
        kwargs.update({
            'crs': dst_crs,
            'transform': transform,
            'width': width,
            'height': height
        })

        with rasterio.open(output_filepath, 'w', **kwargs) as dst:
            for i in range(1, src.count + 1):
                reproject(
                    source=rasterio.band(src, i),
                    destination=rasterio.band(dst, i),
                    src_transform=src.transform,
                    src_crs=src.crs,
                    dst_transform=transform,
                    dst_crs=dst_crs,
                    resampling=Resampling.bilinear
                )

    print(f"Reprojected file: {input_filepath} to {output_filepath}")


def process_landsat_data(input_dir, output_dir):
    """if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    for root, dirs, files in os.walk(input_dir):
        relative_path = os.path.relpath(root, input_dir)
        output_folder = os.path.join(output_dir, relative_path)

        if not os.path.exists(output_folder):
            os.makedirs(output_folder)"""

    for root, dirs, files in os.walk(input_dir):
        for file in files:
            if file.endswith('.tif'):
                print(file)
                input_filepath = os.path.join(input_dir, file)
                output_filepath = os.path.join(output_dir, file)
                reproject_raster(input_filepath, output_filepath)
        """else:
            shutil.copy(input_filepath, output_filepath)
            print(f"Copied file: {input_filepath} to {output_filepath}")"""


if __name__ == "__main__":
    input_directory = r"C:\Users\powelj\Documents\Aotea_test_files\Retrolens\tmp"
    output_directory = r"C:\Users\powelj\Documents\Aotea_test_files\Retrolens\Outputs"
    # process_landsat_data(input_directory, output_directory)
    process_landsat_data(input_directory, output_directory)
