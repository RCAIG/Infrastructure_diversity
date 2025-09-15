import arcpy
import os

# Define input and output directories
input_dir = r'your input path of AOI data'
output_dir = r'your output path of AOI data'

# Ensure output directory exists
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

# Get all shapefiles in the input directory
shp_files = [f for f in os.listdir(input_dir) if f.endswith('.shp')]

# Define reclassification function
def reclassify_poi(fclass):
    if fclass in ["the Residential classes in OSM in Supplementary Table 2 of our paper"]:
        return 'Residential'
    elif fclass in ["the Commercial classes in OSM in Supplementary Table 2 of our paper"]:
        return 'Commercial'
    elif fclass in ["the Education classes in OSM in Supplementary Table 2 of our paper"]:
        return 'Education'
    elif fclass in ["the Medical classes in OSM in Supplementary Table 2 of our paper"]:
        return 'Medical'
    elif fclass in ["the Public classes in OSM in Supplementary Table 2 of our paper"]:
        return 'Public'
    else:
        return 'other'  # Default classification for unmatched cases

# Process each shapefile
for shp_file in shp_files:
    try:
        # Construct full input file path
        input_path = os.path.join(input_dir, shp_file)

        # Construct output file path
        output_filename = f"{os.path.splitext(shp_file)[0]}_reclass.shp"
        output_path = os.path.join(output_dir, output_filename)

        # Copy the shapefile to the output directory
        arcpy.Copy_management(input_path, output_path)

        # Add new field for reclassification
        arcpy.AddField_management(output_path, "aoi_re", "TEXT", field_length=50)

        # Update the new field based on existing data
        with arcpy.da.UpdateCursor(output_path, ["fclass", "aoi_re"]) as cursor:
            for row in cursor:
                row[1] = reclassify_poi(row[0])
                cursor.updateRow(row)

        print(f"Processing completed: {shp_file}")

    except arcpy.ExecuteError:
        print(f"ArcPy error while processing {shp_file}: {arcpy.GetMessages(2)}")
    except Exception as e:
        print(f"Unknown error while processing {shp_file}: {str(e)}")

print("All files processed!")