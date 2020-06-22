import requests
import json
import datetime


# helper functions to keep the main.py file relatively clean.

def checkzipcode(zipcode):
    res = True
    if len(zipcode) != 5:
        res = False
    else:
        try:
            int(zipcode)
        except:
            res = False
    return res


def weather(zipcode, config):
    if not checkzipcode(zipcode):
        s = "Bad zip code entered: " + zipcode
    else:
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


def twitchbearertoken(config):
    api_url = "https://id.twitch.tv/oauth2/token?client_id=" + config["twitch_client_id"] + "&client_secret=" \
              + config["twitch_client_secret"] + "&grant_type=client_credentials"
    tokenreq = requests.post(api_url)
    if tokenreq.status_code != 200:
        return "None"
    else:
        tokendict = tokenreq.json()
        bearer_token = tokendict["access_token"]
        return bearer_token


def hydrate(config):
    # step 1: figure out how long stream has been online
    # this requires two api calls, one to get the auth token and another to actually get the data we need
    token = twitchbearertoken(config)
    s = ""
    if token == "None":
        s = "Couldn't connect to the Twitch Helix API to get a token."
    else:
        client_id = config["twitch_client_id"]
        h = {
            "Authorization": "Bearer " + token,
            "Client-ID": client_id
        }
        api_url = "https://api.twitch.tv/helix/streams?user_login=" + config["twitch_initial_channels"][0]
        streamdata = requests.get(api_url, headers=h)
        if streamdata.status_code != 200:
            s = "Something went wrong with the API Call. HTTP Status Code: " + str(streamdata.status_code)
        else:
            if len(streamdata.json()["data"]) == 0:
                s = "The stream is offline. You may uncontrollably guzzle cum at your " \
                    "convenience. Stay hydrated, gamers :)"
            else:
                stream = streamdata.json()["data"][0]
                time_str = stream["started_at"]
                started_time = datetime.datetime.strptime(time_str, '%Y-%m-%dT%H:%M:%S.%fZ')
                print(str(started_time))
                current_time = datetime.datetime.utcnow()
                print(str(current_time))
                timedelta = current_time - started_time
                # calculate how much cum i should have ingested by this point.
                daily_cum_intake = 3.7  # liters
                cum_intake_per_sec = daily_cum_intake / 86400.0  # number of seconds per day
                sec_total = timedelta.seconds
                cum_intake_recommended = sec_total * cum_intake_per_sec
                live_time = str(timedelta)
                s = "The stream has been going for " + live_time + ". Mico should have guzzled about " + \
                    str(cum_intake_recommended) + " Liters of cum so far. Stay hydrated, gamers :)"
    return s
