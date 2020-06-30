from time import sleep
from twitchio.ext import commands
import json
import helpers
import markov
import random

# Pull in the config json file and parse it into a dict
config_txtfile = open("config/config_secret.json", "rt+")
config = json.load(config_txtfile)
config_txtfile.close()

# Start the bot
twbot = commands.Bot(
    irc_token=config["twitch_irc_token"],
    client_id=config["twitch_client_id"],
    nick=config["twitch_bot_username"],
    prefix=config["twitch_bot_prefix"],
    initial_channels=config["twitch_initial_channels"]
)
m = markov.MarkovChainer(2)
helpers.markov_startup(m)


# bot commands below this line
@twbot.event
async def event_ready():
    print("bot ready......")
    ws = twbot._ws
    await ws.send_privmsg(config["twitch_initial_channels"][0], f"/me has Logged In. Howdy gamers.")
    return


@twbot.command(name="h")
async def bothelp(ctx):
    # print(str(ctx.content))
    await ctx.channel.send("*** Testing.")
    return


@twbot.command(name="weather")
async def weather(ctx):
    print("Weather")
    msg = ctx.content
    ziparray = msg.split(' ', 1)
    # print(len(ziparray))
    if len(ziparray) <= 1:
        await ctx.send("Not enough arguments. Syntax: !weather zip, like this: !weather 07801")
        sleep(1.5)
        zipcd = "10001"  # NYC
    else:
        zipcd = ziparray[1]
    s = helpers.weather(zipcd, config)
    await ctx.channel.send(s)
    return


@twbot.command(name="hydrate")
async def hydrate(ctx):
    print("Hydration")
    s = helpers.hydrate(config)
    await ctx.channel.send(s)
    return


@twbot.command(name="discord")
async def discord(ctx):
    s = "Well there isn't one, but maybe one day. Subscribe to grow the channel, maybe I'll be big enough to justify " \
        "it! "
    await ctx.channel.send(s)
    return


@twbot.event
async def event_message(ctx):
    await twbot.handle_commands(ctx)
    # runs every time a message is sent.
    if ctx.author.name.lower() == config["twitch_bot_username"].lower():
        return
    msg = ctx.content
    action_calc = random.randrange(1, 31)
    helpers.markov_add(m, msg, config["markov_excluded_words"])
    s = None
    if action_calc == 10:
        s = helpers.butt_replace(msg)
    elif action_calc == 20:
        s = m.generate_sentence()
    elif action_calc == 30:
        s = "FrankerZ"
    if s is None:
        return
    else:
        await ctx.channel.send(s)
    return


# so that i can start up the bot by calling twitch_bot.py with a cron job
if __name__ == "__main__":
    twbot.run()
