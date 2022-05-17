#!/usr/bin/python3
# Simplified API for getting weather forecasts
# Copyright (C) 2022 Michail Krasnov <linuxoid85@gmail.com>

import os
import json
import requests
import matplotlib.pyplot as plt

SETTINGS = "./settings.json"

class _Settings:

    @staticmethod
    def get() -> dict:
        with open(SETTINGS) as f:
            data = json.load(f)
        return data

class FWFLocatMgr:

    def __init__(self, city: str):
        self.settings = _Settings.get()
        appid = self.settings["api"]["appid"]

        res = requests.get(
            "http://api.openweathermap.org/geo/1.0/direct",
            params = {
                'q': city,
                'limit': 5,
                'appid': appid
            }
        )
        self.data = res.json()

    def search_location(self, func) -> dict:
        raw_data = self.data

        if len(self.data) > 1:
            # NOTE: CHANGE IN v0.1 VERSION:
            # В том случае, если при выполнении поиска было получено более одной
            # локации, вызвать функцию-диалог, получающую полученый словарь с
            # найденными локациями и возвращающую список, состоящий из
            # **одного** словаря с информацией только о той локации, которую
            # выбрал пользователь.
            select_data = func()
            raw_data = select_data
        data = {
            "name": raw_data[0]['name'],
            "country": raw_data[0]['country'],
            "lat": raw_data[0]['lat'],
            "lon": raw_data[0]['lon']
        }
        return data

    def select_location(self) -> list:
        # TODO: need to tests!
        it = len(self.data)
        #lang = self.settings['app']['lang']

        for i in range(it):
            print(f"""[{i}] - {
                self.data[i]['name']
            },{
                self.data[i].get('state')
            },{
                self.data[i]['country']
            }""")

        sel = int(input("Select the NUMBER of the location you need: "))
        return [self.data[sel]]

class FForecast:

    def __init__(self, coords: dict, _type: str):
        # TODO: добавить использование кеша, если он создавался менее получаса
        # назад. Это требуется для уменьшения доступов к API.

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

    def _get_it(self) -> int:
        # NOTE: DEPRECATED
        if self._type == "daily":
            return self.len_daily
        elif self._type == "hourly":
            return self.len_hourly
        else:
            return -1

    def make_cache(self, cache_dir):
        if not os.path.exists(cache_dir):
            raise FileNotFoundError

        with open(f"{cache_dir}/forecast.json", "w") as f:
            json.dump(self.data, f, indent=4, ensure_ascii = True)

    def timezone(self) -> str:
        return self.data["timezone"]

    def dt(self) -> list:
        data_list = []

        if self._type == "current":
            return [self._type_d["dt"]]

        it = self._get_it()

        for i in range(it):
            data = self._type_d[i]["dt"]
            data_list.append(data)

        return data_list

    def description(self) -> list:
        data_list = []

        if self._type == "current":
            data_list.append(self._type_d['weather'][0]['description'])
            return data_list
        else:
            it = self._get_it()

            for i in range(it):
                data = self._type_d[i]['weather'][0]['description']
                data_list.append(data)
                del(data)

            return data_list

    def sun_rise_set(self) -> list:
        if self._type == "current":
            data_dict = {
                "sunrise": self._type_d["sunrise"],
                "sunset": self._type_d["sunset"]
            }
            return [data_dict]
        elif self._type == "daily":
            data = []
            for i in range(self.len_daily):
                data_dict = {}

                data_dict["sunrise"] = self._type_d[i]["sunrise"]
                data_dict["sunset"] = self._type_d[i]["sunset"]

                data.append(data_dict)
                del(data_dict)
            return data
        else:
            return [{"request": None, "error": "Данные недоступны для почасового представления"}]

    def moon_rise_set(self) -> list:
        data_list = []
        data_dict = {}
        it = self.len_daily

        for i in range(it):
            for prm in "rise", "set":
                data_dict[f"moon{prm}"] = self._type_d[i][f"moon{prm}"]
            data_list.append(data_dict)
        return data_list

    def temp(self) -> list:
        dt = self._type_d
        data_list = []

        params = ("temp", "feels_like")

        if self._type == "current":
            data_dict = {}
            for prm in params:
                data_dict[prm] = dt[prm]
            data_list.append(data_dict)
            return data_list

        it = self._get_it()

        for i in range(it):
            data_dict = {}
            for prm in params:
                data_dict[prm] = dt[i][prm]
            data_list.append(data_dict)
            del(data_dict)

        return data_list

    def humidity(self) -> list:
        dt = self._type_d
        data_list = []

        if self._type == "current":
            data_list.append(dt['humidity'])
            return data_list
        elif self._type == "hourly":
            it = self.len_hourly
        else:
            it = self.len_daily

        for i in range(it):
            data = self._type_d[i]['humidity']
            data_list.append(data)

        return data_list

class FWFPlots:

    def __init__(self, coords: dict, _type: str):
        self.coords = coords
        self._type = _type

        settings = _Settings.get()

        api_key = settings["api"]["appid"]
        units = settings["app"]["units"]

        res = requests.get(
            "https://api.openweathermap.org/data/2.5/onecall",
            params = {
                "lat": self.coords["lat"],
                "lon": self.coords["lon"],
                "exclude": "minutely,alerts",
                "units": units,
                "appid": api_key
            }
        )

        self.data = res.json()
        self._type_d = self.data[_type]
        
        self.len_hourly = len(self.data["hourly"])
        self.len_daily = len(self.data["daily"])

        if _type == "daily":
            self.it = self.len_daily
        elif _type == "hourly":
            self.it = self.len_hourly
        else:
            self.it = -1

        self.FF = FForecast(coords, _type)

    def mkplot(self, _type: str, filename = None):
        if os.path.isfile(filename):
            os.remove(filename)

        dt = self.FF.dt()
        temp = self.FF.temp()
        humidity = self.FF.humidity()

        fx, ax = plt.subplots()
        
        if self._type == "daily":
            temp_day_plot = []
            temp_night_plot = []
            for i in range(self.it):
                temp_day_plot.append(temp[i]['temp']['day'])
                temp_night_plot.append(temp[i]['temp']['night'])
            ax.plot(dt, temp_day_plot, label = "Temperature (day)")
            ax.plot(dt, temp_night_plot, label = "Temperature (night)")
        elif self._type == "hourly":
            temp_plot = []
            temp_fl_plot = []
            for i in range(self.it):
                temp_plot.append(temp[i]['temp'])
                temp_fl_plot.append(temp[i]['feels_like'])
            ax.plot(dt, temp_plot, label = "Temperature")
            ax.plot(dt, temp_fl_plot, label = "Temperature (feels like)")

        ax.plot(dt, humidity, label = "Humidity")
        ax.legend()

        plt.title(f"Temperature & humidity {self._type} plot")
        plt.xlabel("UNIX Time")
        plt.ylabel("Temperature & humidity")
        
        if _type == "save":
            plt.savefig(filename)
        elif _type == "show":
            plt.show()
        else:
            print(f"\033[1m\033[31mUnknown type: '{_type}'\033[0m")
