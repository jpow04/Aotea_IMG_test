import os
import rasterio
import matplotlib.pyplot as plt
import numpy as np
from glob import glob
from rasterio.enums import Resampling


def create_histogram_line_graph(data, title, output_path, avg_height=None, raw=False):
    plt.figure(figsize=(10, 6))

    all_heights = []
    max_height = 0
    for band in range(1, data.shape[0] + 1):
        band_data = data[band - 1]
        hist, bins = np.histogram(band_data, bins=256, range=(np.min(band_data), np.max(band_data)))
        plt.plot(bins[:-1], hist, label=f'Band {band}')
        all_heights.append(hist)
        if raw:
            max_height = max(max_height, hist.max())

    if avg_height is None:
        # Calculate the average height across all bands if not provided
        all_heights = np.array(all_heights)
        avg_height = np.mean(all_heights)

    plt.title(title)
    plt.xlabel('Pixel Value')
    plt.ylabel('Frequency')

    if raw:
        plt.ylim(0, max_height)
    else:
        plt.ylim(0, avg_height)  # Set y-axis limit to the average height of all bands

    plt.legend(loc='upper right')
    plt.grid(True)
    plt.savefig(output_path)
    plt.close()


def resize_image_to_match_shape(image, target_shape):
    with rasterio.open(image) as src:
        data = src.read(
            out_shape=(
                src.count,
                target_shape[0],
                target_shape[1]
            ),
            resampling=Resampling.bilinear
        )
        return data[0]  # We only need the first band


def generate_histograms(output_dir, surface_reflectance_end, radiance_end, raw_data_dir=None,
                        raw_histogram_output_dir=None):
    for root, dirs, files in os.walk(output_dir):
        if any(file.endswith(surface_reflectance_end) or file.endswith(radiance_end) for file in files):
            sr_files = [f for f in files if f.endswith(surface_reflectance_end)]
            rad_files = [f for f in files if f.endswith(radiance_end)]

            # Create histogram directory within the current image folder
            histogram_dir = os.path.join(root, "histogram")
            if not os.path.exists(histogram_dir):
                os.makedirs(histogram_dir)

            for sr_file in sr_files:
                sr_path = os.path.join(root, sr_file)
                try:
                    with rasterio.open(sr_path) as src:
                        sr_data = src.read()
                        short_name = sr_file[:13]
                        mask_info = []
                        if 'mclds' in sr_file:
                            mask_info.append('cloud masked')
                        if 'topshad' in sr_file:
                            mask_info.append('shadow masked')
                        mask_info_str = " | ".join(mask_info) if mask_info else ""
                        title = f'Surface Reflectance Histogram for {short_name} | {mask_info_str}'
                        output_path = os.path.join(histogram_dir,
                                                   f"{os.path.basename(sr_file).replace('.tif', '')}_sr_hist.png")
                        create_histogram_line_graph(sr_data, title, output_path)
                        print(f"Created Surface Reflectance histogram for {sr_file}")
                except Exception as e:
                    print(f"Error processing {sr_file}: {e}")

            for rad_file in rad_files:
                rad_path = os.path.join(root, rad_file)
                try:
                    with rasterio.open(rad_path) as src:
                        rad_data = src.read()
                        short_name = rad_file[:13]
                        mask_info = []
                        if 'mclds' in rad_file:
                            mask_info.append('cloud masked')
                        if 'topshad' in rad_file:
                            mask_info.append('shadow masked')
                        mask_info_str = " | ".join(mask_info) if mask_info else ""
                        title = f'Radiance Histogram for {short_name} | {mask_info_str}'
                        output_path = os.path.join(histogram_dir,
                                                   f"{os.path.basename(rad_file).replace('.tif', '')}_rad_hist.png")
                        create_histogram_line_graph(rad_data, title, output_path)
                        print(f"Created Radiance histogram for {rad_file}")
                except Exception as e:
                    print(f"Error processing {rad_file}: {e}")

    if raw_data_dir and raw_histogram_output_dir:
        generate_raw_histograms(raw_data_dir, raw_histogram_output_dir)


def generate_raw_histograms(raw_data_dir, raw_histogram_output_dir):
    for root, dirs, files in os.walk(raw_data_dir):
        for dir_name in dirs:
            if dir_name.endswith('.SAFE'):
                safe_dir = os.path.join(root, dir_name)
                jp2_files = glob(os.path.join(safe_dir, 'GRANULE', '*', 'IMG_DATA', '*.jp2'))

                # Filter for bands 1-10
                jp2_files = [f for f in jp2_files if any(band in f for band in [f'B0{i}.jp2' for i in range(1, 11)])]

                if not jp2_files:
                    continue

                raw_data = []
                target_shape = None
                for jp2_file in jp2_files:
                    try:
                        with rasterio.open(jp2_file) as src:
                            if target_shape is None:
                                target_shape = src.shape
                            band_data = resize_image_to_match_shape(jp2_file, target_shape)
                            raw_data.append(band_data)
                    except Exception as e:
                        print(f"Error reading {jp2_file}: {e}")

                if raw_data:
                    raw_data = np.stack(raw_data)
                    title = f'Raw Sentinel-2 Histogram for {dir_name}'
                    output_path = os.path.join(raw_histogram_output_dir, f"{dir_name}_raw_hist.png")
                    max_height = np.max([np.histogram(band_data, bins=256)[0].max() for band_data in raw_data])
                    create_histogram_line_graph(raw_data, title, output_path, avg_height=max_height, raw=True)
                    print(f"Created Raw Sentinel-2 histogram for {dir_name}")


if __name__ == "__main__":
    # Define the output directory and file ends
    output_directory = r"C:\Users\powelj\Documents\Aotea_test_files\Sentinel\Outputs"
    surface_reflectance_end = "_stdsref.tif"
    radiance_end = "_rad.tif"
    raw_sentinel_dir = r"C:\Users\powelj\Documents\Aotea_test_files\Sentinel\RAW"
    raw_histogram_output_dir = r"C:\Users\powelj\Documents\Aotea_test_files\Sentinel\Raw_Histograms"

    # Generate histograms
    generate_histograms(output_directory, surface_reflectance_end, radiance_end, raw_sentinel_dir,
                        raw_histogram_output_dir)
