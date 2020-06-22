from time import sleep
from twitchio.ext import commands
import json
import helpers

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


# bot commands below this line
@twbot.event
async def event_ready():
    print("bot ready......")
    ws = twbot._ws
    await ws.send_privmsg(config["twitch_initial_channels"][0], f"/me has Logged In. Howdy gamers.")


@twbot.command(name="h")
async def bothelp(ctx):
    # print(str(ctx.content))
    await ctx.send("*** Testing.")


@twbot.command(name="weather")
async def weather(ctx):
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
    await ctx.send(s)


@twbot.command(name="hydrate")
async def hydrate(ctx):
    s = helpers.hydrate(config)
    await ctx.send(s)


# so that i can start up the bot by calling main.py with a cron job
if __name__ == "__main__":
    twbot.run()
