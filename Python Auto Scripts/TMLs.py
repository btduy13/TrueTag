from pyautocad import Autocad, APoint
import math

acad = Autocad(create_if_not_exists=True)

def clean_text(text):
    """Remove the formatting tags from the text."""
    cleaned_text = text.replace("{\\fTimes New Roman|b1|i0|c0|p18;", "").replace("}", "")
    return cleaned_text

def format_platform(platform):
    """Remove the hyphen from the platform name."""
    platform = platform.replace("-", "")
    return platform

def format_riser(riser):
    """Remove 'No.', periods, and format riser number with leading zero if needed."""
    riser = riser.replace("No.", "").replace(".", "").strip()
    riser = "R" + (riser.zfill(2) if len(riser) < 2 else riser)
    return riser

def format_number(num):
    """Ensure the number is in 2-digit format."""
    return num.zfill(2)

def create_block(acad, blkname, clayerb, clayer1, insertion_point, radius, htx, wdy, styname, final_text, combined_text):
    """Create a block with a circle and an attribute definition."""
    # Create a circle at insertion point
    circle = acad.model.AddCircle(APoint(insertion_point), radius)
    circle.Layer = clayerb
    
    # Create a text attribute
    acad.model.AddText(final_text + combined_text, APoint(insertion_point), htx).Layer = clayer1

def save_drawing_as(save_filename):
    """Save the current drawing as the provided filename."""
    acad.doc.SaveAs(save_filename)

def select_text(prompt_message):
    """Helper function to select a text object and return its text value."""
    try:
        selection = acad.prompt(prompt_message)
        if selection:
            return selection.TextString
        else:
            print(f"No valid object selected for: {prompt_message}")
            return None
    except AttributeError:
        print(f"Selected object is not valid: {prompt_message}")
        return None

def main():
    blkname = "EQ_BLOCK"
    clayerb = "-DRN"
    clayer1 = "-DRNMARK"
    styname = "STANDARD"
    htx = 0.1563
    wdy = 0.8
    radius = 0.04

    # Select platform and riser text with error handling
    platform_text_str = select_text("Select Platform text: ")
    if platform_text_str is None:
        return  # Exit if platform text selection failed

    riser_text_str = select_text("Select Riser No. text: ")
    if riser_text_str is None:
        return  # Exit if riser text selection failed

    # Clean and format platform and riser values
    platform_value = format_platform(clean_text(platform_text_str))
    riser_value = format_riser(clean_text(riser_text_str))

    final_text = ""

    # Search for specific phrases in the text objects
    for text_obj in acad.iter_objects(['Text', 'MText']):
        text_str = text_obj.TextString.strip().upper()
        if "AT FIXED CONTROLLED POINTS" in text_str:
            final_text = f"{platform_value}-{riser_value}_FCP"
            break
        elif "WALL THICKNESS MEASUREMENT" in text_str:
            final_text = f"{platform_value}-{riser_value}_TML"
            break

    # Select all circles and check if any are found
    circles_found = False
    for circle in acad.iter_objects("Circle"):
        circles_found = True
        circle_center = APoint(circle.Center)
        radius = circle.Radius

        # Check text inside the circle
        combined_text = ""
        for text_obj in acad.iter_objects(['Text', 'MText']):
            text_center = APoint(text_obj.InsertionPoint)
            if math.dist(circle_center, text_center) <= radius:
                combined_text = format_number(text_obj.TextString)
                break
        
        if combined_text:
            print(f"Text inside the circle: {combined_text}")
            print(f"Insertion point: {circle_center}")

            # Create block with attributes
            create_block(acad, blkname, clayerb, clayer1, circle_center, radius, htx, wdy, styname, final_text, combined_text)

            print(f"Block inserted with attribute: {final_text}{combined_text}")

    if not circles_found:
        print("No circles found in the drawing.")

    # Determine save file name based on finalText
    if "_FCP" in final_text:
        save_file_name = f"{platform_value}-IA-FCP.dwg"
    elif "_TML" in final_text:
        save_file_name = f"{platform_value}-IA-WT.dwg"
    else:
        save_file_name = f"{platform_value}-IA-UNKNOWN.dwg"

    # Save the drawing
    save_file_name = acad.prompt(f"Save Drawing As (default: {save_file_name}): ")
    if save_file_name:
        save_drawing_as(save_file_name)

    print("Done.")

# Run the main function
if __name__ == "__main__":
    main()
