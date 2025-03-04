import requests
import base64


def reformat_messages(response_json: dict):
    """
    example of a screen_info:
    ID: 1, Text: xlt
    ID: 2, Text: 4t8
    ID: 3, Text: Rt
    ID: 4, Text: BA
    ID: 5, Text: #B
    ID: 6, Text: 16.04
    ID: 7, Text: YouTube
    ID: 8, Text: youtube.com
    """
    screen_info = ""
    for idx, element in enumerate(response_json["parsed_content_list"]):
        element['idx'] = idx
        if element['type'] == 'text':
            screen_info += f'ID: {idx}, Text: {element["content"]}\n'
        elif element['type'] == 'icon':
            screen_info += f'ID: {idx}, Icon: {element["content"]}\n'
    response_json['screen_info'] = screen_info
    return response_json


class OmniParserClient:
    def __init__(self, url: str) -> None:
        self.url = url

    def parse_screenshot(self, raw_screenshot_filename: str, som_screenshot_filename: str):
        with open(raw_screenshot_filename, "rb") as image_file:
            image_base64 = base64.b64encode(image_file.read()).decode("utf-8")
        response = requests.post(f"{self.url}/parse/", json={"base64_image": image_base64})
        response.raise_for_status()
        response_json = response.json()
        print('omniparser latency:', response_json['latency'])

        som_image_data = base64.b64decode(response_json['som_image_base64'])
        with open(som_screenshot_filename, "wb") as f:
            f.write(som_image_data)

        response_json['raw_screenshot_base64'] = image_base64
        response_json = reformat_messages(response_json)
        return response_json

    @staticmethod
    def get_click_position(box_id, parsed_contents: list[dict]) -> tuple[str, str]:
        """
        example of a parsed content:
        {
            "type": "text",
            "bbox": [
                0.01778179593384266, // min_x
                0.024020226672291756, // max_x
                0.3725135624408722, // min_y
                0.06510745733976364 // max_y
            ],
            "interactivity": false,
            "content": "OmniParser for Pure Vision Based General GUI Agent",
            "source": "box_ocr_content_ocr"
        }
        """
        bbox = parsed_contents[box_id]["bbox"]
        x = (bbox[0] + bbox[2]) / 2
        y = (bbox[1] + bbox[3]) / 2
        return f"{x:.2f}", f"{y:.2f}"
