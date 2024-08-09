import rasterio
import glob
import os
import re

# Directory where the 10-meter .jp2 files are stored
input_dir = r"C:\Users\powelj\Documents\Aotea_test_files\Sentinel\RAW\2023\S2B_MSIL1C_20231224T222549_N0510_R029_T60HUE_20231224T232042\S2B_MSIL1C_20231224T222549_N0510_R029_T60HUE_20231224T232042.SAFE\GRANULE\L1C_T60HUE_A035519_20231224T222543\IMG_DATA"
output_dir = r"C:\Users\powelj\Documents\Aotea_test_files\Sentinel\Outputs"
output_file = os.path.join(output_dir, "sentinel_stacked.tif")

# Ensure the output directory exists
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

# Define a pattern to match the 10-meter bands (B02, B03, B04, B08)
pattern = re.compile(r'B0[2348].jp2$')

# Find all .jp2 files in the input directory that match the pattern
jp2_files = [f for f in glob.glob(os.path.join(input_dir, "*.jp2")) if pattern.search(f)]

# Ensure the files are sorted to maintain band order (optional: you can sort based on your requirement)
jp2_files.sort()

# Open the first file to get the metadata
with rasterio.open(jp2_files[0]) as src0:
    meta = src0.meta

# Update metadata to reflect the number of layers
meta.update(count=len(jp2_files), driver='GTiff')

# Read each layer and write it to stack
with rasterio.open(output_file, 'w', **meta) as dst:
    for id, layer in enumerate(jp2_files, start=1):
        with rasterio.open(layer) as src1:
            dst.write_band(id, src1.read(1))

print(f"Stacked GeoTIFF file saved as {output_file}")
