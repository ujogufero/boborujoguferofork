import requests
from loguru import logger
from bs4 import BeautifulSoup
from bs4.element import Tag

URL = "https://www.shmu.sk/sk/?page=1&id=hydro_vod_ba&station_id=5140#sbox"


def parse_shmu() -> dict[str, str | int | float | None] | None:
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36"
        }
        response = requests.get(URL, headers=headers, timeout=15)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")

        # Searching for the table by looking for the station name or specific table structure
        table: Tag | None = None
        tables = soup.find_all("table")
        for t in tables:
            if "Bratislava - Dunaj" in t.get_text():
                table = t
                break

        if not table:
            logger.warning("Could not find data table")
            return None

        rows = table.find_all("tr")
        data_row: Tag | None = None
        for row in rows:
            # Skip non-Tag nodes (like NavigableString) if found
            if not getattr(row, "find_all", None):
                continue
            tds = row.find_all("td")
            if len(tds) >= 2:
                first_cell = tds[0]
                if first_cell:
                    text = first_cell.get_text().strip()
                    # Check for "DD.MM.YYYY HH:MM" pattern
                    if "." in text and ":" in text:
                        data_row = row
                        break

        if not data_row:
            logger.warning("No data rows found")
            return None

        cols = data_row.find_all("td")
        if not cols:
            logger.warning("Invalid columns structure")
            return None

        date_time_str = cols[0].get_text().strip()
        parts = date_time_str.split()
        if len(parts) < 2:
            logger.warning("Invalid date format: {}", date_time_str)
            return None

        time = parts[1]

        if len(cols) < 2:
            logger.warning("Missing water level column")
            return None

        water_level_text = cols[1].get_text().strip()
        # Handle cases like "276 cm"
        water_level = int("".join(filter(str.isdigit, water_level_text)))

        water_temp_c: float | None = None
        if len(cols) > 2:
            water_temp_text = cols[2].get_text().strip()
            # Handle cases like "3.4 °C" -> 3.4
            try:
                water_temp_c = float(water_temp_text.split()[0].replace(",", "."))
            except (ValueError, IndexError):
                logger.warning("Could not parse water temp from '{}'", water_temp_text)

        data: dict[str, str | int | float | None] = {
            "water_last_measured": time,
            "water_level_cm": water_level,
            "water_temp_c": water_temp_c,
        }

        logger.debug("SHMU data parsed: {}", data)
        return data

    except Exception:
        logger.exception("Error parsing SHMU")
        return None


if __name__ == "__main__":
    _ = parse_shmu()
