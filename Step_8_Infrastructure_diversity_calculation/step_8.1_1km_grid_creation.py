import arcpy
import os

# Set input and output paths
input_folder = r"your city boundary shp path"  # Input folder containing SHP files
output_folder = r"your grid output path"  # Output folder to save grids

# Ensure the output folder exists
print("Checking if output directory exists...")
if not os.path.exists(output_folder):
    os.makedirs(output_folder)
    print(f"Output directory {output_folder} created successfully.")
else:
    print(f"Output directory {output_folder} already exists.")

# Get all Shapefile files in the folder
print("Getting all SHP files from the input directory...")
shp_files = [os.path.join(input_folder, f) for f in os.listdir(input_folder) if f.endswith('.shp')]
print(f"Found {len(shp_files)} SHP files.")

# Process each Shapefile
for shp_file in shp_files:
    print(f"\nProcessing file: {shp_file}")

    # Iterate through each feature
    with arcpy.da.SearchCursor(shp_file, ["ID_UC_G0", "SHAPE@"]) as cursor:
        for row in cursor:
            id_uc_g0 = int(row[0])  # Get ID_UC_G0 field
            geometry = row[1]  # Get the feature's geometry

            # Create temporary file path
            temp_shp_file = os.path.join(output_folder, f"temp_{id_uc_g0}.shp")

            # Save the current feature as a temporary Shapefile
            arcpy.CopyFeatures_management(geometry, temp_shp_file)
            print(f"Feature ID_UC_G0: {id_uc_g0} saved to temporary file: {temp_shp_file}")

            # Calculate the feature's extent using the temporary file
            extent = arcpy.Describe(temp_shp_file).extent
            xmin, ymin, xmax, ymax = extent.XMin, extent.YMin, extent.XMax, extent.YMax
            print(f"Feature ID_UC_G0: {id_uc_g0} extent - xmin: {xmin}, ymin: {ymin}, xmax: {xmax}, ymax: {ymax}")

            # Set grid parameters
            cell_size = 1000  # 1 kilometer (units in meters)
            print("Setting grid size to 1 km x 1 km.")

            # Set Y-axis coordinate
            y_axis_coord = f"{xmin} {ymax}"  # Use maximum Y value as Y-axis coordinate

            # Create grid
            print(f"Creating grid for ID_UC_G0: {id_uc_g0}...")
            fishnet_output = os.path.join(output_folder, f"{id_uc_g0}.shp")
            arcpy.management.CreateFishnet(
                fishnet_output,
                f"{xmin} {ymin}",  # Lower-left corner origin
                y_axis_coord,  # Use maximum Y value as Y-axis coordinate
                cell_size,  # Row size
                cell_size,  # Column size
                "",  # Leave row count and column count empty
                "",  # Leave row count and column count empty
                labels="NO_LABELS",  # Do not create labels
                template=temp_shp_file,  # Use projection from temporary shp file
                geometry_type="POLYGON"  # Create polygons
            )

            print(f"Grid successfully created, output file: {fishnet_output}")

            # Delete temporary Shapefile
            if arcpy.Exists(temp_shp_file):
                arcpy.Delete_management(temp_shp_file)
                print(f"Temporary file deleted: {temp_shp_file}")

print("\nAll grid creation tasks completed.")