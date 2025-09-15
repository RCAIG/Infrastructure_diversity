import arcpy
import os
from shutil import rmtree

# Set up workspace
workspace = "Any independent path"
arcpy.env.workspace = workspace

# Set up the directory
input_shp_dir = r"Your POI point feature path"
output_points_dir = r"The path to your building's geometric center point data"

# Ensure that output can be overwritten during geoprocessing
arcpy.env.overwriteOutput = True

# Define the field name for multi-value extraction to the point
field_names = ["res_500", "res_250", "com_500", "com_250", "edu_500", "edu_250", "med_500", "med_250", "pub_500", "pub_250"]

# Get all SHP files in the input directory
shp_files = [f for f in os.listdir(input_shp_dir) if f.endswith('.shp')]

point_files = [f for f in os.listdir(output_points_dir) if f.endswith('.shp')]

print("POI reclassification and building point files have been obtained")

# Loop through each SHP feature file and the corresponding building point file
for i, shp_file in enumerate(shp_files):
    try:
        # Build the complete input file path
        shp_path = os.path.join(input_shp_dir, shp_file)
        point_path = os.path.join(output_points_dir, point_files[i])

        # Get the value of the "poi_re" field in the shapefile
        poi_re_values = ['residential','commercial','education','medical','public']
        # Create a list to store the kernel density grid paths generated for each group
        density_rasters = []
        density_rasters_tem = []
        field_index = 0  # Index used to track field names
        print("Start generating kernel density")

        # Iterate over each "poi_re" value
        for poi_type in poi_re_values:

            # Use the "Select Feature" tool to select the feature corresponding to the current "poi_re" value
            selected_features = os.path.join(workspace, f"{poi_type}_selected.shp")
            a = arcpy.management.SelectLayerByAttribute(shp_path, "NEW_SELECTION", f"bui_big = '{poi_type}'")
            arcpy.management.CopyFeatures(a, selected_features)

            # Get the extent of the shapefile
            desc = arcpy.Describe(point_path)
            extent = desc.extent

            # Create a rectangular feature
            array = arcpy.Array([
                arcpy.Point(extent.XMin, extent.YMin),
                arcpy.Point(extent.XMax, extent.YMin),
                arcpy.Point(extent.XMax, extent.YMax),
                arcpy.Point(extent.XMin, extent.YMax),
                arcpy.Point(extent.XMin, extent.YMin)  # Close the polygon
            ])
            polygon = arcpy.Polygon(array, desc.spatialReference)

            # Buffer the rectangle
            buffer_distance = "5000 Meters"  # Buffer distance, adjustable
            buffered_polygon = os.path.join(workspace, f"{os.path.splitext(shp_file)[0]}_buffered_rect.shp")
            arcpy.analysis.Buffer(polygon, buffered_polygon, buffer_distance)

            # Get the range of the buffered rectangle
            desc_buffered = arcpy.Describe(buffered_polygon)
            buffered_extent = desc_buffered.extent
            arcpy.env.extent = buffered_extent

            # Perform kernel density estimation for 500m  For surface files, add area weight
            output_tif_500 = os.path.join(workspace, f"{poi_type[:3]}_500.tif")
            kernel_density_500 = arcpy.sa.KernelDensity(selected_features, "NONE", 50, 500, "SQUARE_METERS")


            density_rasters.append([kernel_density_500, field_names[field_index]])
            density_rasters_tem.append(kernel_density_500)
            field_index += 1

            print(f"500m kernel density estimation results have been successfully added {output_tif_500}")

            # Perform kernel density estimation for 250m  For surface files, add area weight
            output_tif_250 = os.path.join(workspace, f"{poi_type[:3]}_250.tif")
            kernel_density_250 = arcpy.sa.KernelDensity(selected_features, "NONE", 50, 250, "SQUARE_METERS")


            density_rasters.append([kernel_density_250, field_names[field_index]])
            density_rasters_tem.append(kernel_density_250)
            field_index += 1
            print(f"500m kernel density estimation results have been successfully added {output_tif_250}")
            # Reset the environment scope (optional but recommended)
            arcpy.env.extent = None
            # Delete temporary buffer files
            arcpy.management.Delete(buffered_polygon)
            # Delete temporary shapefile
            arcpy.management.Delete(selected_features)

        # Extract all generated kernel density rasters to multiple values
        print(f"Processing completed: {shp_file}")
        arcpy.sa.ExtractMultiValuesToPoints(point_path, density_rasters, "NONE")
        print(f"Completed multi-value extraction of {shp_file} to points")
        # Delete the data in density_rasters
        for i in density_rasters_tem:
             arcpy.management.Delete(i)
        print(f"All files in {workspace} have been deleted")
        density_rasters = []
        density_rasters_tem = []
        field_index = 0  # Index used to track field names


    except Exception as e:
        print(f"Error processing {shp_file}: {str(e)}")

print("All files processed!")

