import os
import numpy as np
import rasterio
from rasterio.errors import RasterioIOError
from tqdm import tqdm
import warnings


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


def validate_geotiffs(image_files):
    """
    Validate the GeoTIFFs and log any issues found.
    """
    valid_images = []
    base_profile = None
    log_entries = []

    for image_file in image_files:
        try:
            with rasterio.open(image_file) as src:
                profile = src.profile
                if base_profile is None:
                    base_profile = profile
                else:
                    if profile['transform'] != base_profile['transform']:
                        log_entries.append(f"Alignment issue with {image_file}")
                        continue
                    if profile['crs'] != base_profile['crs']:
                        log_entries.append(f"CRS mismatch with {image_file}")
                        continue
                valid_images.append(image_file)
        except RasterioIOError as e:
            log_entries.append(f"Rasterio error with {image_file}: {e}")
        except Exception as e:
            log_entries.append(f"Unknown error with {image_file}: {e}")

    return valid_images, log_entries


def compute_median_composite(image_files, output_file, log_file):
    """
    Compute the median composite from a list of image files and save to output file.
    """
    # Read metadata of the first image to get the number of bands
    with rasterio.open(image_files[0]) as src0:
        meta = src0.meta
        num_bands = src0.count

    # Read all images and stack into a list of numpy arrays
    stacks = []
    for image_file in image_files:
        try:
            with rasterio.open(image_file) as src:
                bands = []
                for band in range(1, num_bands + 1):
                    band_data = src.read(band).astype(np.float32)
                    band_data[band_data == src.nodata] = np.nan  # Mask out nodata values
                    bands.append(band_data)
                stacks.append(np.stack(bands, axis=0))
        except Exception as e:
            with open(log_file, 'a') as log:
                log.write(f"Error reading {image_file}: {e}\n")

    # Stack into a 4D array (bands, rows, cols, num_images)
    stacks = np.stack(stacks, axis=-1)

    # Compute the median along the fourth axis, ignoring NaNs
    with warnings.catch_warnings():
        warnings.filterwarnings(action='ignore', message='All-NaN slice encountered')
        median_image = np.nanmedian(stacks, axis=-1)

    # Update metadata to reflect the number of layers
    meta.update(count=num_bands, dtype=rasterio.float32)

    # Write the median composite to a new file
    with rasterio.open(output_file, 'w', **meta) as dst:
        for band in range(num_bands):
            dst.write(median_image[band], band + 1)


def create_median_composites(input_dir, composite_dir, file_suffix, log_dir):
    """
    Create median composites for each year in the output directory.
    """
    if not os.path.exists(composite_dir):
        os.makedirs(composite_dir)
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    year_folders = [os.path.join(input_dir, d) for d in os.listdir(input_dir) if
                    os.path.isdir(os.path.join(input_dir, d))]

    for year_folder in tqdm(year_folders, desc="Creating composites"):
        year = os.path.basename(year_folder)
        image_files = get_image_files(year_folder, file_suffix)

        if image_files:
            log_file = os.path.join(log_dir, f"{year}_log.txt")
            valid_images, log_entries = validate_geotiffs(image_files)
            if log_entries:
                with open(log_file, 'w') as log:
                    for entry in log_entries:
                        log.write(entry + "\n")

            if valid_images:
                output_file = os.path.join(composite_dir, f"{year}_median_composite.tif")
                compute_median_composite(valid_images, output_file, log_file)
                # print(f"Created median composite for year {year}: {output_file}")
            else:
                print(f"No valid images found for year {year} after validation. See log file: {log_file}")
        else:
            print(f"No images found for year {year} with suffix {file_suffix}")


# Parameters
output_directory = r"C:\Users\powelj\Documents\Aotea_test_files\Sentinel\Outputs"
composite_directory = r"C:\Users\powelj\Documents\Aotea_test_files\Sentinel\Composites"
log_directory = r"C:\Users\powelj\Documents\Aotea_test_files\Sentinel\Log\composite"
masked_tif = "_mclds_topshad_rad_srefdem_stdsref.tif"

if __name__ == "__main__":
    create_median_composites(output_directory, composite_directory, masked_tif, log_directory)
