#!/usr/bin/python3

import os
import json
import requests

SETTINGS = "./settings.json"

class _Settings:

    @staticmethod
    def get() -> dict:
        with open(SETTINGS) as f:
            data = json.load(f)
        return data

class FWFLocatMgr:

    def __init__(self, city: str):
        settings = _Settings.get()
        appid = settings["api"]["appid"]

        res = requests.get(
            "http://api.openweathermap.org/geo/1.0/direct",
            params = {
                'q': city,
                'limit': 5,
                'appid': appid
            }
        )
        self.data = res.json()

    def search_location(self) -> dict:
        data = {
            "name": self.data[0]['name'],
            "country": self.data[0]['country'],
            "lat": self.data[0]['lat'],
            "lon": self.data[0]['lon']
        }
        return data

class FForecast:

    def __init__(self, coords: dict, _type: str):
        self.coords = coords
        self._type = _type

        settings = _Settings.get()

        api_key = settings["api"]["appid"]
        lang = settings["app"]["lang"]
        units = settings["app"]["units"]

        res = requests.get(
            "https://api.openweathermap.org/data/2.5/onecall",
            params = {
                "lat": self.coords["lat"],
                "lon": self.coords["lon"],
                "exclude": "minutely,alerts",
                "units": units,
                "lang": lang,
                "appid": api_key
            }
        )
        self.data = res.json()
        self._type_d = self.data[_type]
        self.len_hourly = len(self.data["hourly"])
        self.len_daily = len(self.data["daily"])

    def make_cache(self, cache_dir):
        if not os.path.exists(cache_dir):
            raise FileNotFoundError

        with open(f"{cache_dir}/forecast.json.cache", "w") as f:
            json.dump(self.data, f, indent=4, ensure_ascii = True)

    def timezone(self) -> str:
        return self.data["timezone"]

    def sun_rise_set(self) -> list:
        if self._type == "current":
            data_dict = {
                "sunrise": self._type_d["sunrise"]
                "sunset": self._type_d["sunset"]
            }
            return [data_dict]
        elif self._type == "daily":
            data = []
            for i in self.len_daily:
                data_dict = {}

                data_dict["sunrise"] = self._type_d[i]["sunrise"]
                data_dict["sunset"] = self._type_d[i]["sunset"]

                data.append(data_dict)
            return data
        else:
            return [{"request": None, "error": "Данные недоступны для почасового представления"}]

    def moon_rise_set(self) -> list:
        data_list = []
        data_dict = {}
        it = self.len_daily

        for i in range(it):
            data_dict["moonrise"] = self._type_d[i]["moonrise"]
            data_dict["moonset"] = self._type_d[i]["moonset"]
            data_list.append(data_dict)

        return data_list

    def temp(self) -> list:
        dt = self._type_d
        data_dict = {}
        data_list = []

        if self._type == "current":
            data_dict = {
                "temp": dt["temp"],
                "feels_like": dt["feels_like"]
            }
            data_list.append(data_dict)

        elif self._type == "hourly":
            it = self.len_hourly

        else:
            it = self.len_daily

        for i in range(it):
            data_dict["temp"] = dt[i]["temp"]
            data_dict["feels_like"] = dt[i]["feels_like"]
            data_list.append(data_dict)

        return data_list

    def humidity(self) -> list:
        dt = self._type_d
        data_list = []

        if self._type == "current":
            data_list.append(dt['humidity'])
        elif self._type == "hourly":
            it = self.len_hourly
        else:
            it = self.len_daily

        for i in range(it):
            data = self._type_d[i]['humidity']
            data_list.append(data)

        return data_list
