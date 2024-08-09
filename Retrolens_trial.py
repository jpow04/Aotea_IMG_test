import os
import math
import numpy as np
import pandas as pd
import rasterio
import rasterio as rio
from rasterio.transform import from_origin
from rasterio.transform import Affine
from rasterio.warp import calculate_default_transform, reproject, Resampling
from PIL import Image
from osgeo import gdal  # For read and manipulate rasters
from affine import Affine  # For easy manipulation of affine matrix
from skimage import transform as sk_transform
from skimage.transform import rotate

def process_images(input_dir, temp_dir, output_dir):
    gdal.UseExceptions()
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    if not os.path.exists(temp_dir):
        os.makedirs(temp_dir)

    for filename in os.listdir(input_dir):
        if filename.endswith(".jpg"):
            image_path = os.path.join(input_dir, filename)
            csv_filename = filename.replace("Crown_", "").replace(".jpg", ".csv")
            csv_path = os.path.join(input_dir, csv_filename)

            if os.path.exists(csv_path):
                try:
                    # Read the CSV file
                    metadata = pd.read_csv(csv_path, header=0)
                    lat = 0.00 + float(metadata.at[0, 'Photo_Centre_Lat'])
                    lon = -0.00 + float(metadata.at[0, 'Photo_Centre_Long'])
                    scale = 0.1 / float(metadata.at[0, 'Scale'])
                    date = str(metadata.at[0, 'Date'])
                    image_name = str(metadata.at[0, 'Name'])

                    # Open the image
                    img = Image.open(image_path)
                    # Crop the image
                    width, height = img.size
                    left = 160
                    right = width - 310
                    top = 120
                    bottom = height - 225
                    img = img.crop((left, top, right, bottom))

                    # Rotate the image 270 degrees
                    img = img.rotate(-90, expand=True)
                    # img = img.rotate(0, expand=True)
                    img_array = np.array(img)

                    # Calculate the new width and height after rotation
                    new_width, new_height = img.size
                    print(new_height)
                    print(new_width)

                    # Define the transform
                    transform_1 = from_origin(lon, lat, scale, scale)

                    # Define the metadata
                    meta = {
                        'driver': 'GTiff',
                        'height': new_height,
                        'width': new_width,
                        'count': 3,
                        'dtype': img_array.dtype,
                        'crs': 'EPSG:4326',
                        'transform': transform_1
                    }
                    print(height)
                    print(width)
                    temp_filename = f"temp_{image_name}_{date}.tif"
                    temp_path = os.path.join(temp_dir, temp_filename)

                    # Save as GeoTIFF
                    with rasterio.open(temp_path, 'w', **meta) as dst:
                        for i in range(1, 4):
                            dst.write(img_array[:, :, i - 1], i)
                        # Add metadata
                        for key, value in metadata.iloc[0].items():
                            if pd.notnull(metadata.at[0, key]):
                                dst.update_tags(**{key: str(metadata.at[0, key])})

                    print(f"Processed {filename} to {temp_filename}")
                    print(lat)
                    print(lon)

                except Exception as e:

                    print(f"Failed to process {filename}: {e}")
    return(temp_path)

def raster_center(raster):
    """This function return the pixel coordinates of the raster center
    """

    # We get the size (in pixels) of the raster
    # using gdal
    width, height = raster.RasterXSize, raster.RasterYSize
    # print(width, height)
    # We calculate the middle of raster
    xmed = width / 2
    ymed = height / 2
    # print(xmed, ymed)
    return (xmed, ymed)

def rotate_gt(affine_matrix, angle, pivot=None):
    """This function generate a rotated affine matrix
    """

    # The gdal affine matrix format is not the same
    # of the Affine format, so we use a bullit-in function
    # to change it
    # see : https://github.com/sgillies/affine/blob/master/affine/__init__.py#L178
    affine_src = Affine.from_gdal(*affine_matrix)
    # We made the rotation. For this we calculate a rotation matrix,
    # with the rotation method and we combine it with the original affine matrix
    # Be carful, the star operator (*) is surcharged by Affine package. He make
    # a matrix multiplication, not a basic multiplication
    affine_dst = affine_src * affine_src.rotation(angle, pivot)
    # We retrun the rotated matrix in gdal format
    print(affine_dst)
    return affine_dst.to_gdal()


def rotate_raster(in_file, out_dir, angle, shift_x=0, shift_y=0,adj_width=0, adj_height=0):
    """Rotate a raster image and save it to disk.
            in_file: path to input raster file
            out_file: path to output raster file
            angle: angle of rotation in degrees
            shift_x: shift in x direction
            shift_y: shift in y direction
            adj_width: adjust width of output raster
            adj_height: adjust height of output raster"""

    with rio.open(in_file) as src:

        # Get the old transform and crs
        src_transform = src.transform
        crs = src.crs

        # Affine transformations for rotation and translation
        rotate = Affine.rotation(angle)
        trans_x = Affine.translation(shift_x,0)
        trans_y = Affine.translation(0, -shift_y)

        # Combine affine transformations
        dst_transform = src_transform * rotate * trans_x * trans_y

        # Get band data
        band = np.array(src.read(1))

        # Get the new shape
        y,x = band.shape
        dst_height = y + adj_height
        dst_width = x + adj_width

        # set properties for output
        dst_kwargs = src.meta.copy()
        dst_kwargs.update(
            {
                "transform": dst_transform,
                "height": dst_height,
                "width": dst_width,
                "nodata": 0,
            }
        )

        output_filename = f"rotated_raster.tif"
        out_file = os.path.join(out_dir, output_filename)

        # write to disk
        with rio.open(out_file, "w", **dst_kwargs) as dst:
            # reproject to new CRS

            reproject(source=band,
                      destination=rio.band(dst, 1),
                      src_transform=src_transform,
                      src_crs=crs,
                      dst_transform=dst_transform,
                      dst_crs=crs,
                      resampling=Resampling.nearest)


input_directory = r'C:\Users\powelj\Documents\Aotea_test_files\Retrolens\Inputs'
temp_directory = r'C:\Users\powelj\Documents\Aotea_test_files\Retrolens\tmp'
output_directory = r'C:\Users\powelj\Documents\Aotea_test_files\Retrolens\Outputs'
angle = 0
process_images(input_directory, temp_directory, output_directory)
# temp_path = process_images(input_directory, temp_directory, output_directory)
# dataset_src = gdal.Open(temp_path)
# center = raster_center(dataset_src)
# print(center)
# rotate_raster(temp_path, output_directory, angle)
