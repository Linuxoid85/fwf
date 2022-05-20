#!/usr/bin/python3
# Simplified API for getting weather forecasts
# Copyright (C) 2022 Michail Krasnov <linuxoid85@gmail.com>

# Единая Россия едина ПРОТИВ россиян. Бей ЕР - СПАСАЙ РОССИЮ

import os
import json
import requests
import matplotlib.pyplot as plt

SETTINGS = "./settings.json"
AIR_POLLUTION = "./air_pollution_index.json"
MASTER_URL = "http://api.openweathermap.org"

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
            f"{MASTER_URL}/geo/1.0/direct",
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
        it = len(self.data)

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

    def select_location2(self) -> list:
        """
        Для агрессивно настроенных разработчиков метод, аналогичный первому, но
        с баннером.
        """
        print(
            "\033[1mЕдиная Россия едина ПРОТИВ россиян. Бей ЕР - СПАСАЙ РОССИЮ\033[0m"
        )
        return self.select_location()

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
            f"{MASTER_URL}/data/2.5/onecall",
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
            return [
                {
                    "request": None,
                    "error": "Данные недоступны для почасового представления"
                }
            ]

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
            f"{MASTER_URL}/data/2.5/onecall",
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

        ax.legend()

        plt.title(f"Temperature {self._type} plot")
        plt.xlabel("UNIX Time")
        plt.ylabel("Temperature & humidity")
        
        if _type == "save":
            plt.savefig(filename)
        elif _type == "show":
            plt.show()
        else:
            print(f"\033[1m\033[31mUnknown type: '{_type}'\033[0m")

class FWFAirPoll:

    def __init__(self, coords: dict, start_time = None, end_time = None):
        settings = _Settings.get()
        conf = {
            'lat': coords['lat'],
            'lon': coords['lon'],
            'appid': settings['api']['appid']
        } # Initial dict
        
        if all((start_time, end_time)):
            conf['start'] = start_time
            conf['end'] = end_time
            url = f"{MASTER_URL}/data/2.5/air_pollution/history"
        else:
            url = f"{MASTER_URL}/data/2.5/air_pollution/forecast"

        res = requests.get(url, params = conf)
        self.data = res.json()

        # Besides basic Air Quality Index, the API returns data about polluting
        # gases, such as Carbon monoxide (CO), Nitrogen monoxide (NO), Nitrogen
        # dioxide (NO2), Ozone (O3), Sulphur dioxide (SO2), Ammonia (NH3), and
        # particulates (PM2.5 and PM10).

        # Air pollution forecast is available for 5 days with hourly
        # granularity. Historical data is accessible from 27th November 2020.
        with open(AIR_POLLUTION) as f:
            self.index = json.load(f)

    def get_index(self, _type: str):
        return self.index[_type]

    def get_status(self, component: str) -> dict:
        # FIXME: в том случае, если в какой-то секции нужное значение
        # отсутствует, либо явно равно 'null', переходить на предыдущую секцию

        # Значения из 'very_poor' не используются, так как на данный момент нет
        # функции для обработки значений 'null'
        _types = ("good", "fair", "moderate", "poor")
        data = {}
        it = len(self.data['list'])

        for i in range(it):
            for _type in _types:
                comp = self.data['list'][i][component]
                if comp is not None and comp >= self.index[_type][comp]:
                    data[_type] = True
                else:
                    data[_type] = False

        return data
