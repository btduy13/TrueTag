from pyautocad import Autocad, APoint
import win32com.client
import pythoncom
import tkinter as tk
from tkinter import filedialog
import time

def clean_text(text):
    """
    Remove the formatting tags from the text.
    """
    cleaned_text = text.lstrip('{\\fTimes New Roman|b1|i0|c0|p18;').rstrip('}')
    return cleaned_text.strip()

def format_platform(platform):
    """
    Remove the hyphen from the platform name.
    """
    return platform.replace('-', '')

def format_riser(riser):
    """
    Remove "No." and any leading/trailing spaces or periods, then format with leading zero if necessary.
    """
    riser = riser.replace('No.', '').replace('.', '').strip()
    return f"R{riser.zfill(2)}"

def format_number(num):
    """
    Ensure the number is in 2-digit format.
    """
    num = num.strip()
    return num.zfill(2) if len(num) < 2 else num

def create_block(acad, blkname, clayerb, clayer1, insertion_point, radius, htx, wdy, styname, max_retries=10, delay=0.5):
    """
    Create a block definition with a circle and an attribute.
    Implements a retry mechanism to handle COM errors.
    """
    for attempt in range(max_retries):
        try:
            block = acad.doc.Blocks.Add(APoint(*insertion_point), blkname)
            print(f"Block '{blkname}' created at {insertion_point}.")

            # Add circle to block at origin (relative to block)
            circle = block.AddCircle(APoint(0, 0), radius)
            circle.Layer = clayerb
            print(f"Circle added to block '{blkname}' on layer '{clayerb}'.")

            # Add attribute definition to block
            attr_mode = win32com.client.constants.acAttributeModeNormal  # Editable attribute
            attr = block.AddAttribute(
                Height=htx,
                Mode=attr_mode,
                Prompt="NAME",
                InsertionPoint=APoint(0, 0),
                Tag="EQ_TAG",
                Default="+"
            )
            attr.Layer = clayer1
            attr.WidthFactor = wdy
            attr.StyleName = styname
            print(f"Attribute 'EQ_TAG' added to block '{blkname}' on layer '{clayer1}'.")

            return True  # Success
        except win32com.client.pywintypes.com_error as e:
            if e.hresult == -2147418111:  # RPC_E_CALL_REJECTED
                print(f"Call rejected by callee during block creation. Retrying {attempt + 1}/{max_retries}...")
                time.sleep(delay)
                pythoncom.PumpWaitingMessages()
            else:
                print(f"COMError during block creation: {e}")
                break
    print(f"Failed to create block '{blkname}' after {max_retries} attempts.")
    return False  # Failure

def get_entity(acad, prompt, max_retries=10, delay=0.5):
    """
    Prompt the user to select an entity using SelectionSet.
    Implements a retry mechanism to handle 'Call was rejected by callee' errors.
    """
    for attempt in range(max_retries):
        try:
            acad.doc.Utility.Prompt(prompt + "\n")
            ssname = "GetEntitySelectionSet"
            try:
                selection_set = acad.doc.SelectionSets.Item(ssname)
                selection_set.Clear()
            except:
                selection_set = acad.doc.SelectionSets.Add(ssname)
            selection_set.SelectOnScreen()
            if selection_set.Count > 0:
                entity = selection_set.Item(0)
                selection_set.Delete()
                return entity, None  # pick_point is not used
            else:
                selection_set.Delete()
                print("No entity selected.")
                return None, None
        except win32com.client.pywintypes.com_error as e:
            if e.hresult == -2147418111:  # RPC_E_CALL_REJECTED
                print(f"Call rejected by callee. Retrying {attempt + 1}/{max_retries}...")
                time.sleep(delay)
                pythoncom.PumpWaitingMessages()
            else:
                print(f"COMError encountered: {e}")
                return None, None
    print("Failed to get entity after multiple attempts.")
    return None, None

def ensure_layer_exists(acad, layer_name, max_retries=10, delay=0.5):
    """
    Check if the layer exists; if not, create it.
    Implements a retry mechanism for COM errors.
    """
    layers = acad.doc.Layers
    for attempt in range(max_retries):
        try:
            layer = layers.Item(layer_name)
            print(f"Layer '{layer_name}' exists.")
            return layer
        except:
            try:
                layer = layers.Add(layer_name)
                print(f"Layer '{layer_name}' created.")
                return layer
            except win32com.client.pywintypes.com_error as e:
                if e.hresult == -2147418111:
                    print(f"Layer creation call rejected. Retrying {attempt + 1}/{max_retries}...")
                    time.sleep(delay)
                    pythoncom.PumpWaitingMessages()
                else:
                    print(f"Error creating layer '{layer_name}': {e}")
                    break
    print(f"Failed to ensure layer '{layer_name}' exists.")
    return None

def get_blocks(acad, blkname, max_retries=10, delay=0.5):
    """
    Retrieve the names of the blocks from the Blocks collection with retry.
    Handles AttributeError if a block does not have a 'Name' attribute.
    """
    for attempt in range(max_retries):
        try:
            block_names = []
            for blk in acad.doc.Blocks:
                try:
                    block_names.append(blk.Name)
                except AttributeError:
                    print(f"A block does not have a 'Name' attribute. Skipping.")
            return block_names
        except win32com.client.pywintypes.com_error as e:
            if e.hresult == -2147418111:  # RPC_E_CALL_REJECTED
                print(f"Access to Blocks was rejected. Retrying {attempt + 1}/{max_retries}...")
                time.sleep(delay)
                pythoncom.PumpWaitingMessages()
            else:
                print(f"COMError encountered while accessing Blocks: {e}")
                break
    print("Failed to access Blocks after multiple attempts.")
    return []

def get_bounding_box(text_obj, max_retries=10, delay=0.5):
    """
    Retrieve the bounding box of a text object with retry mechanism.
    """
    for attempt in range(max_retries):
        try:
            min_pt_variant, max_pt_variant = text_obj.GetBoundingBox()
            min_pt = list(min_pt_variant)
            max_pt = list(max_pt_variant)
            text_center = [(min_pt[i] + max_pt[i]) / 2.0 for i in range(3)]
            return text_center
        except win32com.client.pywintypes.com_error as e:
            if e.hresult == -2147418111:
                print(f"GetBoundingBox call rejected. Retrying {attempt + 1}/{max_retries}...")
                time.sleep(delay)
                pythoncom.PumpWaitingMessages()
            else:
                print(f"COMError encountered while getting bounding box: {e}")
                break
    print("Failed to get bounding box after multiple attempts.")
    return None

def TML():
    acad = Autocad(create_if_not_exists=True)
    print("Connected to AutoCAD.")

    blkname = "EQ_BLOCK"
    clayerb = "-DRN"
    clayer1 = "-DRNMARK"
    clayeri = "-DRN"
    styname = "STANDARD"
    htx = 0.1563
    wdy = 0.8
    radius = 0.04
    sclx = scly = sclz = 1

    # Ensure that required layers exist
    layerb = ensure_layer_exists(acad, clayerb)
    layer1 = ensure_layer_exists(acad, clayer1)
    layeri = ensure_layer_exists(acad, clayeri)

    if not all([layerb, layer1, layeri]):
        print("One or more required layers could not be ensured. Exiting.")
        return

    # Set the current layer to clayeri
    for attempt in range(10):
        try:
            acad.doc.ActiveLayer = layeri
            print(f"Active layer set to '{clayeri}'.")
            break
        except win32com.client.pywintypes.com_error as e:
            if e.hresult == -2147418111:
                print(f"Setting ActiveLayer rejected. Retrying {attempt + 1}/10...")
                time.sleep(0.5)
                pythoncom.PumpWaitingMessages()
            else:
                print(f"Error setting ActiveLayer: {e}")
                return
    else:
        print(f"Failed to set ActiveLayer to '{clayeri}' after multiple attempts.")
        return

    # Prompt user to select platform text and riser text
    print("Please select the platform text.")
    platform_text_object, pt = get_entity(acad, "Select Platform text: ")
    if not platform_text_object:
        print("No platform text selected. Exiting.")
        return

    print("Please select the riser number text.")
    riser_text_object, pt = get_entity(acad, "Select Riser No. text: ")
    if not riser_text_object:
        print("No riser number text selected. Exiting.")
        return

    # Ensure the selected objects are TEXT or MTEXT
    valid_object_types = ['AcDbText', 'AcDbMText']
    if platform_text_object.ObjectName not in valid_object_types:
        print("Selected platform object is not TEXT or MTEXT. Exiting.")
        return
    if riser_text_object.ObjectName not in valid_object_types:
        print("Selected riser object is not TEXT or MTEXT. Exiting.")
        return

    platform_text = platform_text_object.TextString
    riser_text = riser_text_object.TextString

    platform_value = format_platform(clean_text(platform_text))
    riser_value = format_riser(clean_text(riser_text))

    print(f"Platform Value: {platform_value}")
    print(f"Riser Value: {riser_value}")

    final_text = ""

    # Collect all TEXT and MTEXT objects
    texts = []
    for obj_type in ['AcDbText', 'AcDbMText']:
        try:
            texts.extend(acad.iter_objects([obj_type]))
        except win32com.client.pywintypes.com_error as e:
            if e.hresult == -2147418111:
                print(f"Access to {obj_type} was rejected. Retrying...")
                time.sleep(0.5)
                pythoncom.PumpWaitingMessages()
            else:
                print(f"Error accessing {obj_type}: {e}")

    # Check for specific phrases
    for text_obj in texts:
        text_str = text_obj.TextString
        text_str_upper = text_str.upper()

        if 'AT FIXED CONTROLLED POINTS' in text_str_upper:
            final_text = f"{platform_value}-{riser_value}_FCP"
            print(f"Found phrase 'AT FIXED CONTROLLED POINTS'. Final Text: {final_text}")
            break  # Exit loop since we found it
        elif 'WALL THICKNESS MEASUREMENT' in text_str_upper and not final_text:
            final_text = f"{platform_value}-{riser_value}_TML"
            print(f"Found phrase 'WALL THICKNESS MEASUREMENT'. Final Text: {final_text}")

    # If final_text is still empty, set a default value
    if not final_text:
        final_text = f"{platform_value}-{riser_value}_UNKNOWN"
        print(f"No specific phrases found. Final Text set to: {final_text}")

    # Select all circles
    circles = []
    try:
        circles = list(acad.iter_objects(['AcDbCircle']))
    except win32com.client.pywintypes.com_error as e:
        if e.hresult == -2147418111:
            print("Access to Circles was rejected. Retrying...")
            time.sleep(0.5)
            pythoncom.PumpWaitingMessages()
            try:
                circles = list(acad.iter_objects(['AcDbCircle']))
            except Exception as e_inner:
                print(f"Error accessing Circles after retry: {e_inner}")
        else:
            print(f"Error accessing Circles: {e}")

    if not circles:
        print("No circles found in the drawing.")
    else:
        print(f"Found {len(circles)} circles.")

    # Iterate through each circle
    for circle in circles:
        circle_center = circle.Center
        circle_radius = circle.Radius

        print(f"\nProcessing Circle at {circle_center} with radius {circle_radius}")

        text_list = []

        # Loop through each text object to find those within the circle
        for text_obj in texts:
            text_center = get_bounding_box(text_obj)
            if not text_center:
                print("Skipping text object due to failed bounding box retrieval.")
                continue  # Skip if bounding box couldn't be retrieved

            # Calculate distance from text center to circle center
            distance = ((text_center[0] - circle_center[0]) ** 2 + 
                        (text_center[1] - circle_center[1]) ** 2) ** 0.5

            if distance <= circle_radius:
                text_str = text_obj.TextString
                text_list.append(text_str)
                print(f"Text '{text_str}' is inside the circle.")

        # Combine the text strings (assuming only one number per circle)
        if text_list:
            combined_text = format_number(text_list[0])
            print(f"Combined Text: {combined_text}")

            # Insert block at circle center
            ins_pt = circle_center
            print(f"Inserting block at: {ins_pt}")

            # Check if the block already exists; if not, create it
            blocks_names = get_blocks(acad, blkname)
            if blkname not in blocks_names:
                print(f"Block '{blkname}' does not exist. Creating it.")
                block_created = create_block(acad, blkname, clayerb, clayer1, ins_pt, radius, htx, wdy, styname)
                if block_created:
                    print(f"Block '{blkname}' created successfully.")
                else:
                    print(f"Failed to create block '{blkname}'. Skipping insertion.")
                    continue
            else:
                print(f"Block '{blkname}' already exists.")

            # Insert the block reference with retry mechanism
            blk_ref = None
            for attempt in range(10):
                try:
                    blk_ref = acad.model.InsertBlock(APoint(*ins_pt), blkname, sclx, scly, sclz, 0.0)
                    print(f"Block '{blkname}' inserted at {ins_pt}.")
                    break
                except win32com.client.pywintypes.com_error as e:
                    if e.hresult == -2147418111:
                        print(f"Inserting block was rejected. Retrying {attempt + 1}/10...")
                        time.sleep(0.5)
                        pythoncom.PumpWaitingMessages()
                    else:
                        print(f"Error inserting block: {e}")
                        blk_ref = None
                        break
            else:
                print(f"Failed to insert block '{blkname}' after multiple attempts.")
                blk_ref = None

            # Set attribute if block reference was successfully inserted
            if blk_ref:
                try:
                    if blk_ref.HasAttributes:
                        attribs = blk_ref.GetAttributes()
                        for attrib in attribs:
                            if attrib.TagString == "EQ_TAG":
                                attrib.TextString = final_text + combined_text
                                attrib.Update()
                                print(f"Attribute 'EQ_TAG' set to '{final_text}{combined_text}'.")
                    else:
                        print("Block reference has no attributes.")
                except win32com.client.pywintypes.com_error as e:
                    print(f"Error accessing attributes of block reference: {e}")

    # Determine save file name based on final_text
    if '_FCP' in final_text:
        default_filename = f"{platform_value}-IA-FCP.dwg"
    elif '_TML' in final_text:
        default_filename = f"{platform_value}-IA-WT.dwg"
    else:
        default_filename = f"{platform_value}-IA-UNKNOWN.dwg"

    print(f"\nDefault Save Filename: {default_filename}")

    # Use tkinter to open a "Save As" dialog
    root = tk.Tk()
    root.withdraw()  # Hide the root window

    try:
        save_file_name = filedialog.asksaveasfilename(
            initialfile=default_filename,
            defaultextension=".dwg",
            filetypes=[("DWG Files", "*.dwg")],
            title="Save Drawing As"
        )
    except Exception as e:
        print(f"Error opening Save As dialog: {e}")
        save_file_name = None

    if save_file_name:
        for attempt in range(10):
            try:
                acad.doc.SaveAs(save_file_name)
                print(f"Drawing saved as: {save_file_name}")
                break
            except win32com.client.pywintypes.com_error as e:
                if e.hresult == -2147418111:
                    print(f"SaveAs call was rejected. Retrying {attempt + 1}/10...")
                    time.sleep(0.5)
                    pythoncom.PumpWaitingMessages()
                else:
                    print(f"Error saving drawing: {e}")
                    break
        else:
            print("Failed to save drawing after multiple attempts.")
    else:
        print("Save As dialog was canceled or failed.")

    print("Done.")

# Run the TML function
if __name__ == "__main__":
    TML()
