import requests
from twitchio.ext import commands
import json
import os

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

@twbot.command(name="bothelp")
async def bothelp(ctx):
    await ctx.send("*** Testing.")

# so that i can start up the bot by calling main.py with a cron job
if __name__ == "__main__":
    twbot.run()
