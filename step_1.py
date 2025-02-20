# Joshua Jackson
# Senior Design Spring '25: Multiscale Crater Analysis and Detection (MCAD)
# February 13, 2025
# This file is simply notes I've taken from trial and error

####################################################################
################ STEP 1 - Create PNG to JSON Mapping ###############
####################################################################
# import os
# from collections import defaultdict
#
# # Define the path where extracted files are stored
# data_folder = "/Users/joshuajackson/Downloads/mcad_moon_data"
#
# # Dictionary to store PNG -> JSON mapping
# png_to_json_mapping = defaultdict(str)
#
# # Scan the folder and create the mapping
# for root, _, files in os.walk(data_folder):
#     json_files = {file.replace(".json", ""): file for file in files if file.endswith(".json")}
#
#     for file in files:
#         if file.endswith(".png"):
#             base_name = file.replace(".png", "")
#             if base_name in json_files:
#                 png_to_json_mapping[file] = json_files[base_name]
#
# # Print mapping for verification
# for png, json_file in png_to_json_mapping.items():
#     print(f"PNG: {png} -> JSON: {json_file}")
#
# print(f"\nTotal mappings created: {len(png_to_json_mapping)}")
#####################################
# import os
# from collections import defaultdict
#
# data_folder = "/Users/joshuajackson/Downloads/mcad_moon_data"
# png_to_json_mapping = defaultdict(str)
#
# # Debugging: Print scanned files
# print("Scanning:", data_folder)
#
# for root, _, files in os.walk(data_folder):
#     print(f"\nChecking folder: {root}")
#     json_files = {file.replace(".json", ""): file for file in files if file.lower().endswith(".json")}
#
#     for file in files:
#         if file.lower().endswith(".png"):
#             base_name = file.replace(".png", "")
#             if base_name in json_files:
#                 png_to_json_mapping[file] = json_files[base_name]
#
# # Debugging: Print mappings
# if not png_to_json_mapping:
#     print("\nNo PNG-JSON mappings found!")
# else:
#     for png, json_file in png_to_json_mapping.items():
#         print(f"PNG: {png} -> JSON: {json_file}")
#
# print(f"\nTotal mappings created: {len(png_to_json_mapping)}")
################################
import os
from collections import defaultdict

# Define the path where extracted files are stored
data_folder = "/Users/joshuajackson/Downloads/mcad_moon_data"

# Dictionary to store PNG -> JSON mapping
png_to_json_mapping = defaultdict(str)

# Iterate through all folders
for root, _, files in os.walk(data_folder):
    json_files = {file.replace(".json", ""): file for file in files if file.lower().endswith(".json")}

    for file in files:
        if file.lower().endswith(".png"):
            base_name = file.replace(".png", "")
            if base_name in json_files:
                # Use full path to ensure uniqueness
                png_to_json_mapping[os.path.join(root, file)] = os.path.join(root, json_files[base_name])

# Debugging: Print first 20 mappings
print("\nFirst 20 mappings:")
for i, (png, json_file) in enumerate(png_to_json_mapping.items()):
    if i < 20:
        print(f"PNG: {png} -> JSON: {json_file}")

print(f"\nTotal mappings created: {len(png_to_json_mapping)}")


