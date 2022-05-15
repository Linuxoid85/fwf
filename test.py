#!/usr/bin/python3

import fwf

FLM = fwf.FLocationManager("Vyazniki", "Vladimir Oblast", "RU")
data = FLM.search_location()
crd = {'lat': data['lat'], 'lon': data['lon']}

FF = fwf.FForecast(crd)
FF.make_cache("./cache")
