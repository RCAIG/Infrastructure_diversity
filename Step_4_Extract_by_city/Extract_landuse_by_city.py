import arcpy
import os
from multiprocessing import Pool

# Directory Settings
landuse_directory = r"your path of landuse data after re-class"
city_boundary_shp = r"Path to your city boundaries shapefile"
output_directory = r"your output path of landuse data after extracting by city"

# Create output directory
if not os.path.exists(output_directory):
    os.makedirs(output_directory)
    print(f"Created output directory: {output_directory}")

# Get city boundary features
print(f"Reading city boundary shapefile: {city_boundary_shp}")

# GC_CNT_GAD represents the corresponding country name and indexes to the corresponding country folder
city_boundaries = arcpy.da.SearchCursor(city_boundary_shp, ["ID_UC_G0", "GC_CNT_GAD", "SHAPE@"])
city_data = {row[0]: (row[1], row[2]) for row in city_boundaries}

city_ids = list(city_data.keys())
print(f"Found {len(city_ids)} city boundary features.")

# Function: Process landuse for each city
def process_city(city_id):
    print(f"\nProcessing cities: {int(city_id)}")
    gc_cnt_gad, city_geometry = city_data[city_id]

    # Construct the path (file and folder name) of the landuse you want to find
    landuse_shapefile = os.path.join(landuse_directory, f"{gc_cnt_gad}.shp")
    landuse_folder = os.path.join(landuse_directory, gc_cnt_gad)

    # Processing landuse file paths
    if os.path.exists(landuse_shapefile):
        landuse_shps = [landuse_shapefile]
        print(f"  landuse shapefile found: {landuse_shapefile}")
    elif os.path.isdir(landuse_folder):
        landuse_shps = [os.path.join(landuse_folder, file)
                         for file in os.listdir(landuse_folder) if file.endswith('.shp')]
        print(f"  Found landuse folder: {landuse_folder}, will process the following shapefiles: {landuse_shps}")
    else:
        print(f"No corresponding landuse shapefile or folder found, skipping city: {city_id}")
        return

    # Iterate through selected landuse shapefiles
    for landuse_shp in landuse_shps:
        print(f"  - Mask extraction of landuse shapefile: {landuse_shp}")

        # Create the output file name to extract
        output_shp_name = f"{int(city_id)}.shp"
        output_shp_path = os.path.join(output_directory, output_shp_name)

        # Check if a file with the same name already exists and increment the count suffix
        count = 1
        while os.path.exists(output_shp_path):
            output_shp_name = f"{int(city_id)}_{count}.shp"
            output_shp_path = os.path.join(output_directory, output_shp_name)
            count += 1

        # Perform mask extraction
        print(f"    Performing mask extraction to: {output_shp_path}")
        arcpy.analysis.Clip(landuse_shp, city_geometry, output_shp_path)

        # Check if the result is empty, if so delete it
        if arcpy.management.GetCount(output_shp_path)[0] == "0":
            arcpy.management.Delete(output_shp_path)  # Delete empty output shapefiles
            print(f"    Extraction result is empty, files have been deleted: {output_shp_path}")
        else:
            print(f"    Successfully saved file: {output_shp_path}")

# Using multiprocessing to process cities
if __name__ == '__main__':
    with Pool() as pool:
        pool.map(process_city, city_ids)

print("Extraction complete!")