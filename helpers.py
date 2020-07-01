import requests
import json
import random
import re
import datetime


# helper functions to keep the twitch_bot.py file relatively clean.

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
            s = "Beep boop. Something went wrong with the API Call. HTTP Status Code: " + str(streamdata.status_code)
        else:
            if len(streamdata.json()["data"]) == 0:
                s = "The stream is offline. You may uncontrollably guzzle cum at your " \
                    "convenience. Stay hydrated, gamers :)"
            else:
                stream = streamdata.json()["data"][0]
                time_str = stream["started_at"]
                started_time = datetime.datetime.strptime(time_str, '%Y-%m-%dT%H:%M:%SZ')
                print(str(started_time))
                current_time = datetime.datetime.utcnow()
                print(str(current_time))
                timedelta = current_time - started_time
                # calculate how much cum i should have ingested by this point.
                daily_cum_intake = 3.7  # liters
                cum_intake_per_sec = daily_cum_intake / 86400.0  # number of seconds per day
                sec_total = timedelta.seconds
                cum_intake_recommended = sec_total * cum_intake_per_sec
                live_time = str(timedelta).split(".")[0]
                s = "The stream has been going for " + live_time + ". Mico should have guzzled about " + \
                    format(cum_intake_recommended, '.2f') + " Liters of cum so far. Stay hydrated, gamers :)"
    return s


def markov_startup(m):
    f = open("markov-brain//markov_brain.txt", "rt+")
    for line in f:
        m.add_text(line)
    f.close()


def markov_add(m, txt, exclusion):
    # ok i think it's probably for the best if we scrub out any URL's before sending it to the markov chainer
    txt_cleaned = re.sub(r"http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+", "", txt)
    if len(txt_cleaned) == 0:
        # if we clean the URL and we have an empty string, then that means that was the only thing in the message
        # and there's no sense in adding it...
        # print("Just a test, should be a blank string if only a URL was sent : "+txt_cleaned)
        return
    for w in exclusion:
        if w in txt_cleaned:
            print("OK we found an excluded word, we're not going to add this one. For debugging purposes")
            print("the entire string is: " + txt)
            return
    f = open("markov-brain//markov_brain.txt", "at+")
    f.write("\n" + txt_cleaned)
    f.close()
    m.add_text(txt_cleaned)


def butt_replace(txt):
    exclf = open("config//butt_exclusions.txt", "rt+")
    excl = []
    for i in exclf:
        excl.append(i)
    exclf.close()
    txt_arr = txt.split()
    victim = 0  # pycharm gets mad without this but its not required
    for w in txt_arr:
        if w.lower() == 'butt':
            print("the word butt already exists in the input")
            return
    sentence_length = len(txt_arr)
    if sentence_length == 0:
        # something has gone wrong if we are in here, i have no idea how we could've gotten a blank input
        return "butt ass??????"
    # if there's only one word in the message, it's not really a good candidate for butt replacement
    # this will also completely break the random number generator anyway
    if sentence_length == 1:
        return
    loop = True
    while loop:
        victim = random.randrange(0, sentence_length)  # randrange : lower <= rando < upper
        if txt_arr[victim] not in str(excl):
            loop = False
    replace_with = 'butt'
    # handle for a couple of edge cases like...
    # case 1: init caps
    if re.search(r'^[A-Z]', txt_arr[victim]) is not None:
        replace_with = replace_with.title()
    # case 2: possessive
    if re.search(r"\w+'[Ss]$", txt_arr[victim]) is not None:
        replace_with = replace_with + "'s"
    # case 3: all caps
    if re.search(r'^[^a-z0-9]*$', txt_arr[victim]) is not None:
        replace_with = replace_with.upper()
    txt_arr[victim] = re.sub(r'([0-9a-zA-Z\']+)', replace_with, txt_arr[victim], count=1)
    # reconstructive surgery
    s = ""
    for word in txt_arr:
        s = s + word + " "
    return s.strip()
