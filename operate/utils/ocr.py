from operate.config import Config
from PIL import Image, ImageDraw
import os
from datetime import datetime
from difflib import SequenceMatcher

# Load configuration
config = Config()


def _fuzzy_match(text_a, text_b):
    """Return similarity ratio between two strings (0.0 to 1.0)"""
    return SequenceMatcher(None, text_a.lower(), text_b.lower()).ratio()


def get_text_element(result, search_text, image_path):
    """
    Searches for a text element in the OCR results using exact substring match
    followed by fuzzy matching. Returns index or None if not found.

    Args:
        result (list): The list of results returned by EasyOCR.
        search_text (str): The text to search for in the OCR results.
        image_path (str): Path to the original image.

    Returns:
        int or None: The index of the element containing the search text.
    """
    if config.verbose:
        print("[get_text_element]")
        print("[get_text_element] search_text", search_text)
        ocr_dir = "ocr"
        if not os.path.exists(ocr_dir):
            os.makedirs(ocr_dir)
        image = Image.open(image_path)
        draw = ImageDraw.Draw(image)

    search_lower = search_text.lower().strip()

    # Phase 1: exact substring match
    for index, element in enumerate(result):
        text = element[1]
        if search_lower in text.lower():
            if config.verbose:
                print(f"[get_text_element] exact match found at index {index}: '{text}'")
            _draw_debug(result, index, image, draw, ocr_dir)
            return index

    # Phase 2: fuzzy match (for OCR errors)
    best_score = 0.0
    best_index = None
    for index, element in enumerate(result):
        text = element[1]
        score = _fuzzy_match(search_lower, text.lower())
        if score > best_score:
            best_score = score
            best_index = index

    if best_score >= 0.6 and best_index is not None:
        if config.verbose:
            matched_text = result[best_index][1]
            print(f"[get_text_element] fuzzy match (score={best_score:.2f}): '{matched_text}'")
        _draw_debug(result, best_index, image, draw, ocr_dir)
        return best_index

    if config.verbose:
        print(f"[get_text_element] not found (best fuzzy score={best_score:.2f})")

    return None


def _draw_debug(result, index, image, draw, ocr_dir):
    """Draw bounding boxes on the image for debug visualization."""
    if not config.verbose:
        return
    try:
        for element in result:
            draw.polygon([tuple(point) for point in element[0]], outline="blue")
        box = result[index][0]
        draw.polygon([tuple(point) for point in box], outline="red", width=3)
        datetime_str = datetime.now().strftime("%Y%m%d_%H%M%S")
        ocr_image_path = os.path.join(ocr_dir, f"ocr_image_{datetime_str}.png")
        image.save(ocr_image_path)
        print("[get_text_element] OCR debug image saved at:", ocr_image_path)
    except Exception:
        pass


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
    percent_x = round((center_x / width), 3)
    percent_y = round((center_y / height), 3)

    return {"x": percent_x, "y": percent_y}
