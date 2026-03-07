import json


class Config:
    def __init__(self):
        with open("config.json", "r", encoding="utf-8") as f:
            data = json.load(f)
            parser = data["parser"]
            self.SLEEP = parser["sleep"]
            self.ERROR_SLEEP = parser["error_sleep"]
            self.TIMEOUT = parser["requests"]["timeout"]
            self.RETRIES = parser["retries"]


config = Config()