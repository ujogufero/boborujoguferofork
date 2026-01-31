import requests
from loguru import logger
from bs4 import BeautifulSoup
import json
import re
from typing import cast

URL = "https://www.saunabobor.sk/"


def parse_bobor() -> str | None:
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36"
        }
        response = requests.get(URL, headers=headers, timeout=15)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")

        status_text: str = "Unknown"

        script = soup.find("script", class_="Marquee-props")
        if script and script.string:
            try:
                raw_data = cast(object, json.loads(script.string))
                if isinstance(raw_data, dict):
                    data_dict = cast(dict[str, object], raw_data)
                    raw_items = data_dict.get("marqueeItems")
                    if isinstance(raw_items, list) and raw_items:
                        marquee_items = cast(list[object], raw_items)
                        first_item = marquee_items[0]
                        if isinstance(first_item, dict):
                            item_dict = cast(dict[str, object], first_item)
                            val = item_dict.get("text")
                            if isinstance(val, str):
                                status_text = (
                                    BeautifulSoup(val, "html.parser").get_text().strip()
                                )
            except json.JSONDecodeError:
                logger.warning("Failed to decode json")

        if status_text == "Unknown":
            marquee_content = soup.select_one(".Marquee-content")
            if marquee_content:
                status_text = marquee_content.get_text().strip()

        if re.search(r"otvoren[eé]:?|Po[cč]et [lľ]ud[ií]:?", status_text, flags=re.IGNORECASE):
            status_text = re.sub(
                r"otvoren[eé]:?|Počet ľudí:?", "", status_text, flags=re.IGNORECASE
            ).strip()
        else:
            status_text = "closed"

        logger.debug("Bobor data parsed: {}", status_text)
        return status_text

    except Exception:
        logger.exception("Error parsing Sauna Bobor")
        return None


if __name__ == "__main__":
    _ = parse_bobor()
