import arcpy
import os

# Define input directories
input_directory_b = r"your classified buildings path"
input_directory_a = r"your grid path"

# Define output directories
output_directory = r"your projected output directory"
output_directory_space = r"your spatial join output directory"

# Get all Shapefile files in the directory
print("Getting Shapefile files in the directory...")
shp_files_b = sorted([os.path.join(input_directory_b, f) for f in os.listdir(input_directory_b) if f.endswith('.shp')])
# shp_files_b = shp_files_b[39:40]
shp_files_a = {os.path.splitext(os.path.basename(f))[0]: os.path.join(input_directory_a, f) for f in os.listdir(input_directory_a) if f.endswith('.shp')}

# Check the number of Shapefile files in the first group
print(f"Found {len(shp_files_b)} Shapefiles in directory B.")

if not shp_files_b:
    print("Warning: No Shapefile files found in input directory B.")
else:
    print("Starting spatial join...")

    # Iterate over the first group and perform spatial join
    for shapefile_b in shp_files_b:
        # Extract the base file name (without extension)
        base_b = os.path.splitext(os.path.basename(shapefile_b))[0]
        print(f"Processing file: {base_b}...")

        # Find the corresponding Shapefile in the second group
        shapefile_a = shp_files_a.get(base_b)

        if shapefile_a:
            output_shapefile = os.path.join(output_directory_space, f"SJ_{base_b}.shp")
            print(f"Found corresponding Shapefile: {os.path.basename(shapefile_a)}, starting spatial join...")

            # Use the spatial join tool for analysis
            arcpy.analysis.SpatialJoin(
                target_features=shapefile_b,
                join_features=shapefile_a,
                out_feature_class=output_shapefile,
                join_operation="JOIN_ONE_TO_MANY",
                join_type="KEEP_ALL",
                match_option="HAVE_THEIR_CENTER_IN"
            )

            print(f"Spatial join completed, results saved to {output_shapefile}")

            # Project the output
            projected_shapefile = os.path.join(output_directory, f"{base_b}.shp")
            spatial_reference = arcpy.SpatialReference(54009)  # World_Mollweide projection
            arcpy.Project_management(output_shapefile, projected_shapefile, spatial_reference)
            print(f"Output Shapefile projected to World_Mollweide (WKID: 54009), results saved to {projected_shapefile}")

            # Add an area field
            arcpy.management.AddField(projected_shapefile, "Area", "DOUBLE")
            print("Area field added.")

            # Calculate area in square meters
            arcpy.management.CalculateGeometryAttributes(
                projected_shapefile,
                [["Area", "AREA_GEODESIC"]],
                area_unit="SQUARE_METERS"  # In square meters
            )
            print("Area calculated and updated in the area field.")

        else:
            print(f"Warning: No associated Shapefile found for {base_b}.")

print("All processing completed.")