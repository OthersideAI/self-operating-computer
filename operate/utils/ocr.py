from operate.config import Config
from PIL import Image

# Load configuration
VERBOSE = Config().verbose


def get_text_element(result, search_text):
    """
    Searches for a text element in the OCR results and returns its index.
    Args:
        result (list): The list of results returned by EasyOCR.
        search_text (str): The text to search for in the OCR results.

    Returns:
        int: The index of the element containing the search text.

    Raises:
        Exception: If the text element is not found in the results.
    """
    if VERBOSE:
        print("[get_text_element]")
        print("[get_text_element] search_text", search_text)
    for index, element in enumerate(result):
        text = element[1]
        if VERBOSE:
            print("[get_text_element][loop] text", text)
        if search_text in text:
            if VERBOSE:
                print("[get_text_element][loop] found search_text, index:", index)

            return index
    raise Exception("The text element was not found in the image")


def get_text_coordinates(result, index, image_path):
    """
    Gets the coordinates of the text element at the specified index as a percentage of screen width and height.
    Args:
        result (list): The list of results returned by EasyOCR.
        index (int): The index of the text element in the results list.
        image_path (str): Path to the screenshot image.

    Returns:
        dict: A dictionary containing the 'x' and 'y' coordinates as percentages of the screen width and height.
    """
    if index >= len(result):
        raise Exception("Index out of range in OCR results")

    # Get the bounding box of the text element
    bounding_box = result[index][0]

    # Calculate the center of the bounding box
    min_x = min([coord[0] for coord in bounding_box])
    max_x = max([coord[0] for coord in bounding_box])
    min_y = min([coord[1] for coord in bounding_box])
    max_y = max([coord[1] for coord in bounding_box])

    center_x = (min_x + max_x) / 2
    center_y = (min_y + max_y) / 2

    # Get image dimensions
    with Image.open(image_path) as img:
        width, height = img.size

    # Convert to percentages
    percent_x = round((center_x / width), 1)
    percent_y = round((center_y / height), 1)

    return {"x": percent_x, "y": percent_y}
