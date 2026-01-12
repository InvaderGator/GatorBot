#IMPORT REQUIREMENTS
from unittest import case

import discord
import os
import asyncio
from dotenv import load_dotenv
import pytz
import datetime


#LOADS ENV FILE
load_dotenv()

#CREATES CLIENT CLASS
client = discord.Bot()

@client.event
async def on_ready():
    print(f"{client.user} is ready and online!")

@client.slash_command(name="schedule", description="Schedule a message.")
async def schedule_command(ctx: discord.ApplicationContext, message: str, timezone: str, month: int, day: int, hour: int, minute: int):
    tz = find_time_zone(timezone)

    timeNow = pytz.timezone(find_time_zone(timezone))
    timeLater = datetime.datetime(2026, month, day, hour, minute, 0, 0, tzinfo=tz)

    print(tz)
    print(timeNow)
    print(timeLater)

@client.slash_command(name="delaymessage", description="send a message to be delayed by x time.")
async def delay_message(ctx: discord.ApplicationContext, message: str, delay: int):
    await ctx.send(f"Message scheduled in {delay} seconds.")

    await asyncio.sleep(delay)  # Wait for the specified delay
    await ctx.send(message)  # Send the message

@client.slash_command(name="github", description="View source code and instructions.", integration_types={discord.IntegrationType.user_install})
async def github(ctx: discord.ApplicationContext):
    await ctx.respond("https://github.com/InvaderGator/GatorBot")

def find_time_zone(string):
    match string:
        case "EST":
            return pytz.timezone("US/Eastern")
        case "CST":
            return pytz.timezone("US/Central")
        case "MST":
            return pytz.timezone("US/Mountain")
        case "PST":
            return pytz.timezone("US/Pacific")
        case _:
            return "ERROR, CHOOSE FROM LIST!"

#RUNS BOT
client.run(os.getenv('DISCORD_TOKEN'))

print("end of code.")