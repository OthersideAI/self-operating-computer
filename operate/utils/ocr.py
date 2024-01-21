from operate.config import Config
from operate.config import Config

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
