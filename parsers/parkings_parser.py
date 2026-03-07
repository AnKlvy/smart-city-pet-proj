import requests
import json
import time

from helpers.config import config

OVERPASS_URL = "https://overpass-api.de/api/interpreter"
QUERY = """
        [out:json][timeout:180];
        way["amenity"="parking"]({south},{west},{north},{east});
        out geom;
        """


class ParkingsParser:
    def __init__(self):
        self.all_parkings = []
        self.sleep = config.SLEEP
        self.error_sleep = config.ERROR_SLEEP
        self.timeout = config.TIMEOUT
        self.retries = config.RETRIES

    def parse(self):
        tiles = self.get_tiles()
        self.get_parkings(tiles)
        self.insert_into_db()

    @staticmethod
    def get_tiles():
        tiles = [
            (43.25, 76.75, 43.35, 76.90),
            (43.25, 76.90, 43.35, 77.05),
            (43.15, 76.75, 43.25, 76.90),
            (43.15, 76.90, 43.25, 77.05)
        ]
        return tiles

    def get_parkings(self, tiles):
        for bbox in tiles:
            south, west, north, east = bbox
            query = QUERY.format(south=south, west=west, north=north, east=east)
            for attempt in range(self.retries):
                try:
                    resp = requests.post(OVERPASS_URL, data=query, timeout=self.timeout)
                    resp.raise_for_status()

                    data = resp.json()

                    # фильтруем элементы: только id, type, geometry, tags
                    for el in data['elements']:
                        filtered = {
                            "type": el.get("type"),
                            "id": el.get("id"),
                            "geometry": el.get("geometry"),
                            "tags": el.get("tags")
                        }
                        self.all_parkings.append(filtered)

                    print(f"Tile {bbox} - {len(data['elements'])} элементов")
                    time.sleep(self.sleep)
                    break

                except (requests.exceptions.RequestException, json.JSONDecodeError) as e:
                    print(f"Ошибка: {e}, повтор через {self.error_sleep} секунд")
                    time.sleep(self.error_sleep)

        print("Всего парковок:", len(self.all_parkings))

    def insert_into_db(self):
        with open("almaty_parking_polygons.json", "w", encoding="utf-8") as f:
            json.dump(self.all_parkings, f, ensure_ascii=False, indent=2)
