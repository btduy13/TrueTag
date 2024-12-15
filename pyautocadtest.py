import math
from pyautocad import Autocad, APoint
import re

def clean_text(text):
    # Remove formatting tags from the text
    cleaned_text = re.sub(r'\{\\fTimes New Roman\|b1\|i0\|c0\|p18;', '', text)
    cleaned_text = cleaned_text.rstrip("}")
    return cleaned_text

def format_platform(platform):
    # Remove the hyphen from the platform name
    return platform.replace("-", "")

def format_riser(riser):
    # Remove "No." and any leading/trailing spaces or periods, then format with leading zero if necessary
    riser = riser.replace("No.", "").replace(".", "").strip()
    return f"R{riser.zfill(2)}"

def format_number(num):
    # Ensure the number is in 2-digit format
    return num.zfill(2)

def create_block(acad, blkname, layer, insertion_point, radius, height, text_style):
    # Create a block with a circle and an attribute definition in AutoCAD using PyAutoCAD
    # Insert a circle
    circle = acad.model.AddCircle(insertion_point, radius)
    circle.Layer = layer

    # Insert text for attribute simulation (since PyAutoCAD does not handle attributes)
    text = acad.model.AddText(blkname, insertion_point, height)
    text.StyleName = text_style
    text.Layer = layer
    # Removed WidthFactor as it is not supported in all contexts

def select_text(prompt):
    acad = Autocad(create_if_not_exists=True)
    # Get a single text or mtext object
    print(prompt)
    selection = acad.get_selection()  # Use PyAutoCAD's selection mechanism
    if selection:
        for obj in selection:
            if obj.ObjectName in ["AcDbText", "AcDbMText"]:
                return obj
    print("No valid text selected.")
    return None

def calculate_distance(point1, point2):
    # Calculate the Euclidean distance between two points
    return math.sqrt((point1[0] - point2[0]) ** 2 + (point1[1] - point2[1]) ** 2 + (point1[2] - point2[2]) ** 2)

def main():
    # Initialize AutoCAD application
    acad = Autocad(create_if_not_exists=True)

    blkname = "EQ_BLOCK"
    clayerb = "-DRN"       # defined block layer
    clayer1 = "-DRNMARK"   # attribute def layer
    styname = "STANDARD"   # text style
    htx = 0.1563           # attribute def height
    radius = 0.04          # radius of the circle
    sclx = 1
    scly = 1
    sclz = 1

    # Select platform and riser text
    platform_text = select_text("Select Platform text:")
    riser_text = select_text("Select Riser No. text:")

    if platform_text and riser_text:
        # Get platform and riser values
        platform_value = format_platform(clean_text(platform_text.TextString))
        riser_value = format_riser(clean_text(riser_text.TextString))

        final_text = ""

        # Select all TEXT and MTEXT objects in the drawing
        texts = [ent for ent in acad.iter_objects(['Text', 'MText'])]

        # Check for specific phrases in the text objects
        for text_obj in texts:
            text_str = text_obj.TextString
            if re.search(r"AT FIXED CONTROLLED POINTS", text_str, re.IGNORECASE):
                final_text = f"{platform_value}-{riser_value}_FCP"
            elif re.search(r"WALL THICKNESS MEASUREMENT", text_str, re.IGNORECASE):
                final_text = f"{platform_value}-{riser_value}_TML"

        # Select all circles in the drawing
        circles = [ent for ent in acad.iter_objects('Circle')]

        # Check if circles are found
        if circles:
            for circle in circles:
                circle_center = circle.Center
                radius = circle.Radius

                for text_obj in texts:
                    text_position = text_obj.InsertionPoint
                    # Calculate the distance manually
                    distance = calculate_distance(circle_center, text_position)
                    
                    if distance <= radius:
                        combined_text = format_number(text_obj.TextString.strip())

                        # Create and insert the block with the formatted name
                        create_block(acad, blkname, clayerb, APoint(*circle_center), radius, htx, styname)

                        # Print confirmation
                        print(f"Block inserted with attribute: {final_text}{combined_text}")

        # Determine save file name based on finalText
        if "_FCP" in final_text:
            save_file_name = f"{platform_value}-IA-FCP.dwg"
        elif "_TML" in final_text:
            save_file_name = f"{platform_value}-IA-WT.dwg"
        else:
            save_file_name = f"{platform_value}-IA-UNKNOWN.dwg"

        # Save the drawing
        save_file_name = acad.prompt(f"Save Drawing As {save_file_name}: ")
        acad.ActiveDocument.SaveAs(save_file_name)

        print("Done.")
    else:
        print("Platform or Riser text was not selected correctly.")

if __name__ == "__main__":
    main()
