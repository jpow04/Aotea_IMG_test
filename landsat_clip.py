import os
import shutil
import rasterio
import geopandas as gpd
from rasterio.mask import mask


def clip_raster(input_filepath, output_filepath, shapefile):
    # Read the shapefile using geopandas
    shapes = gpd.read_file(shapefile)

    # Convert the shapes to GeoJSON format
    geoms = shapes.geometry.values

    with rasterio.open(input_filepath) as src:
        # Clip the raster using the shapefile
        out_image, out_transform = mask(src, geoms, crop=True)

        # Update the metadata with the new dimensions, transform, and CRS
        out_meta = src.meta.copy()
        out_meta.update({
            "driver": "GTiff",
            "height": out_image.shape[1],
            "width": out_image.shape[2],
            "transform": out_transform,
            "crs": src.crs
        })

        # Write the clipped raster to the output file
        with rasterio.open(output_filepath, "w", **out_meta) as dest:
            dest.write(out_image)

    print(f"Clipped file: {input_filepath} to {output_filepath}")


def batch_clip(input_dir, output_dir, shapefile):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    for root, dirs, files in os.walk(input_dir):
        relative_path = os.path.relpath(root, input_dir)
        output_folder = os.path.join(output_dir, relative_path)

        if not os.path.exists(output_folder):
            os.makedirs(output_folder)

        for file in files:
            if file.endswith('.TIF'):  # Assuming the Landsat files are in GeoTIFF format
                input_filepath = os.path.join(root, file)
                output_filepath = os.path.join(output_folder, file)
                clip_raster(input_filepath, output_filepath, shapefile)
            else:
                # Copy non-raster files as they are
                shutil.copy(os.path.join(root, file), os.path.join(output_folder, file))


if __name__ == "__main__":
    input_directory = r"C:\Users\powelj\Documents\Aotea_test_files\Landsat\tmp"
    output_directory = r"C:\Users\powelj\Documents\Aotea_test_files\Landsat\Inputs"
    shapefile_path = r"C:\Users\powelj\Documents\Aotea_test_files\Landsat\aotea_landsat_aoi"
    batch_clip(input_directory, output_directory, shapefile_path)
