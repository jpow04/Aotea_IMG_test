import os
import numpy as np
import rasterio
from tqdm import tqdm


def get_image_files(year_folder, file_suffix):
    """
    Retrieve all image files with the specified suffix from the given folder.
    """
    image_files = []
    for root, dirs, files in os.walk(year_folder):
        for file in files:
            if file.endswith(file_suffix):
                image_files.append(os.path.join(root, file))
    return image_files


def compute_median_composite(image_files, output_file):
    """
    Compute the median composite from a list of image files and save to output file.
    """
    # Read metadata of the first image to get the number of bands
    with rasterio.open(image_files[0]) as src0:
        meta = src0.meta
        num_bands = src0.count

    # Read all images and stack into a 4D numpy array (bands, rows, cols, num_images)
    stack = []
    '''for image_file in tqdm(image_files, desc="Reading images"):'''
    for image_file in image_files:
        with rasterio.open(image_file) as src:
            bands = []
            for band in range(1, num_bands + 1):
                bands.append(src.read(band))
            stack.append(np.stack(bands, axis=0))

    stack = np.stack(stack, axis=-1)

    # Compute the median along the fourth axis
    median_image = np.median(stack, axis=-1)

    # Update metadata to reflect the number of layers
    meta.update(count=num_bands)

    # Write the median composite to a new file
    with rasterio.open(output_file, 'w', **meta) as dst:
        for band in range(num_bands):
            dst.write(median_image[band], band + 1)


def create_median_composites(output_directory, composite_directory, file_suffix):
    """
    Create median composites for each year in the output directory.
    """
    if not os.path.exists(composite_directory):
        os.makedirs(composite_directory)

    year_folders = [os.path.join(output_directory, d) for d in os.listdir(output_directory) if
                    os.path.isdir(os.path.join(output_directory, d))]

    for year_folder in tqdm(year_folders, desc="Creating composites"):
        year = os.path.basename(year_folder)
        image_files = get_image_files(year_folder, file_suffix)

        if image_files:
            output_file = os.path.join(composite_directory, f"{year}_median_composite.tif")
            compute_median_composite(image_files, output_file)
            '''tqdm.write(f"Created median composite for year {year}: {output_file}")  # Terminal output
        else:
            tqdm.write(f"No images found for year {year} with suffix {file_suffix}")  # Terminal output'''


# Parameters
output_directory = r"C:\Users\powelj\Documents\Aotea_test_files\Sentinel\Outputs"
composite_directory = r"C:\Users\powelj\Documents\Aotea_test_files\Sentinel\Composites"
file_suffix = "_mclds_topshad_rad_srefdem_stdsref.tif"

if __name__ == "__main__":
    create_median_composites(output_directory, composite_directory, file_suffix)
