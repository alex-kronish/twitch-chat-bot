import requests
import json
import os

# helper functions to keep the main.py file relatively clean.


def weather(zipcode, config):
    api_url = "https://api.openweathermap.org/data/2.5/weather?zip=" + \
              zipcode + "&units=imperial&appid=" + \
              config["openweathermap_api_key"]
    req = requests.get(api_url)
    status = req.status_code
    if status != 200:
        s = "Sorry, something went wrong with the OpenWeatherMap API."
    else:
        res = req.json()
        city = res["name"]
        temp = str(res["main"]["temp"]) + " F"
        desc = res["weather"][0]["description"]
        s = "The weather in " + city + " is " + desc + " with a temperature of " + temp + "."
    return s
