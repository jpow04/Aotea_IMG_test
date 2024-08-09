"""
Script converts Retrolens imagery with csv data into raster Geotiff for Georeferencing. Expect the output raster to
be incorrectly scaled, referenced, and rotated. Examine raw image and apply rotation angle variable to estimate rotation
correction. Cropping raw image before raster conversion is advised. Crop image command is commented out but functions,
however each image requires a different crop so automating cropping isn't exact.
"""
import os
import pandas as pd
import rasterio
from rasterio.transform import from_origin, Affine
from pyproj import Transformer
from PIL import Image
import numpy as np

def convert_coordinates(lat, lon):
    transformer = Transformer.from_crs("EPSG:4326", "EPSG:2193", always_xy=True)
    easting, northing = transformer.transform(lon, lat)
    return easting, northing

def process_images(input_dir, output_dir, rotation_correction):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    for filename in os.listdir(input_dir):
        if filename.endswith(".jpg"):
            image_path = os.path.join(input_dir, filename)
            csv_filename = filename.replace("Crown_", "").replace(".jpg", ".csv")
            csv_path = os.path.join(input_dir, csv_filename)

            if os.path.exists(csv_path):
                try:
                    # Read the CSV file
                    metadata = pd.read_csv(csv_path, header=0)
                    lat = float(metadata.at[0, 'Photo_Centre_Lat'])
                    lon = float(metadata.at[0, 'Photo_Centre_Long'])
                    altitude = float(metadata.at[0, 'Altitude'])
                    scale = float(metadata.at[0, 'Scale'])
                    date = str(metadata.at[0, 'Date'])
                    image_name = str(metadata.at[0, 'Name'])

                    # Convert coordinates from EPSG:4326 to EPSG:2193
                    easting, northing = convert_coordinates(lat, lon)

                    # Open the image
                    img = Image.open(image_path)

                    # Crop the image
                    '''width, height = img.size
                    left = 162
                    right = width - 320
                    top = 130
                    bottom = height - 232
                    img = img.crop((left, top, right, bottom))'''

                    # Rotate the image
                    # img = img.rotate(-90, expand=True)

                    # Convert to numpy array for dimension info
                    img_array = np.array(img)
                    width, height = img.size

                    # Calculate the new transform
                    transform = from_origin(easting, northing, altitude / scale, altitude / scale)

                    # Apply rotation correction
                    rotation_correction_rad = np.deg2rad(rotation_correction)
                    # new_transform = transform * Affine.rotation(rotation_correction_rad, (0, 0))  # corner as rotation point
                    new_transform = transform * Affine.rotation(rotation_correction_rad, (width / 2, height / 2))  # center as rotation point

                    # Define the metadata
                    meta = {
                        'driver': 'GTiff',
                        'height': img_array.shape[0],
                        'width': img_array.shape[1],
                        'count': 3,  # Assuming RGB image
                        'dtype': img_array.dtype,
                        'crs': 'EPSG:2193',
                        'transform': new_transform
                    }

                    output_filename = f"{image_name}_{date}.tif"
                    output_path = os.path.join(output_dir, output_filename)

                    # Save as GeoTIFF
                    with rasterio.open(output_path, 'w', **meta) as dst:
                        for i in range(1, 4):  # Write 3 channels (RGB)
                            dst.write(img_array[:, :, i - 1], i)
                        # Add metadata
                        for key, value in metadata.iloc[0].items():
                            if pd.notnull(metadata.at[0, key]):
                                dst.update_tags(**{key: str(metadata.at[0, key])})

                    print(f"Processed {filename} to {output_filename}")

                except Exception as e:
                    print(f"Failed to process {filename}: {e}")


input_directory = r'C:\Users\powelj\Documents\Aotea_test_files\Retrolens\Inputs\1969'
output_directory = r'C:\Users\powelj\Documents\Aotea_test_files\Retrolens\Outputs'
rotation_angle = 5156.5 * 2
# 90 degrees rotation_angle = 5156.5


process_images(input_directory, output_directory, rotation_angle)
