import json
import re


def convert_percent_to_decimal(percent_str):
    """
    Converts a percentage string to a decimal value.

    Args:
        percent_str (str): The percentage string to be converted.

    Returns:
        float: The decimal value equivalent to the percentage.

    Raises:
        ValueError: If the input string cannot be converted to a float.

    Example:
        >>> convert_percent_to_decimal("20%")
        0.2
    """
    try:
        # Remove the '%' sign and convert to float
        decimal_value = float(percent_str.strip("%"))

        # Convert to decimal (e.g., 20% -> 0.20)
        return decimal_value / 100
    except ValueError as e:
        print(f"Error converting percent to decimal: {e}")
        return None


def extract_json_from_string(s):
    """
    Extracts a JSON structure from a string and returns it as a dictionary.

    Args:
        s (str): The input string.

    Returns:
        dict: The extracted JSON structure as a dictionary, or None if no JSON structure is found or if there is an error parsing the JSON.

    """
    try:
        # Find the start of the JSON structure
        json_start = s.find("{")
        if json_start == -1:
            return None

        # Extract the JSON part and convert it to a dictionary
        json_str = s[json_start:]
        return json.loads(json_str)
    except Exception as e:
        print(f"Error parsing JSON: {e}")
        return None


def parse_response(response):
    """
    Parses the given response and returns a dictionary with the type and data.

    Args:
        response (str): The response to parse.

    Returns:
        dict: A dictionary with the type and data extracted from the response.
              The dictionary has the following structure:
              {
                  "type": <response_type>,
                  "data": <response_data>
              }
              If the response is "DONE", the type is "DONE" and the data is None.
              If the response starts with "CLICK", the type is "CLICK" and the data is a JSON object.
              If the response starts with "TYPE", the type is "TYPE" and the data is the text to type.
              If the response starts with "SEARCH", the type is "SEARCH" and the data is the search query.
              If the response doesn't match any of the above patterns, the type is "UNKNOWN" and the data is the original response.
    """
    response = response.strip()
    
    if response == "DONE":
        return {"type": "DONE", "data": None}
    elif response.startswith("CLICK"):
        # Adjust the regex to match the correct format
        click_data = re.search(r"CLICK \{ (.+) \}", response).group(1)
        click_data_json = json.loads(f"{{{click_data}}}")
        return {"type": "CLICK", "data": click_data_json}

    elif response.startswith("TYPE"):
        # Extract the text to type
        try:
            type_data = re.search(r"TYPE (.+)", response, re.DOTALL).group(1)
        except:
            type_data = re.search(r'TYPE "(.+)"', response, re.DOTALL).group(1)
        return {"type": "TYPE", "data": type_data}

    elif response.startswith("SEARCH"):
        # Extract the search query
        try:
            search_data = re.search(r'SEARCH "(.+)"', response).group(1)
        except:
            search_data = re.search(r"SEARCH (.+)", response).group(1)
        return {"type": "SEARCH", "data": search_data}

    return {"type": "UNKNOWN", "data": response}
