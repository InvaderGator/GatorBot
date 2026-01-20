#IMPORT REQUIREMENTS
import discord
import os
import asyncio
from dotenv import load_dotenv
from datetime import datetime, timedelta
import pytz
import json

# Imports year from .json
with open('data.json', 'r') as file:
    data = json.load(file)

# Sets year to year from .json
year = data['year']

#LOADS ENV FILE
load_dotenv()

#CREATES CLIENT CLASS
client = discord.Bot()

#ADMIN ID
adminId = os.getenv('ADMIN_ID')

# Create formats
fmt = "%y-%m-%d %H:%M"
printFmt = "%m-%d %H:%M %Z"

# Sends message when the bot is ready.
@client.event
async def on_ready():
    print(f"{client.user} is ready and online!")

# Schedules a message based on timezone objects.
# One now and one later.
@client.slash_command(name="schedule", description="Schedule a message.", integration_types={discord.IntegrationType.user_install})
async def schedule_command(ctx: discord.ApplicationContext, message: str, timezone: str, month: int, day: int, hour: int, isam: bool, minute: int):
    # Checks to send this message or another message...
    timeErrorTriggered = False

    # initializes timezone local and timezone UST
    timezoneUTC = pytz.timezone("UTC")
    timezoneLocal = pytz.timezone(find_time_zone(timezone))

    # make a tzinfo class for now, then makes a UTC time
    basicTimeNow = datetime.now()
    tz_now = basicTimeNow.astimezone(tz=timezoneUTC)

    # Accounts for user input on timezones
    if hour == 12:
        was12 = True
    else:
        was12 = False
    hour = subtract_initial_time_zone(hour, timezone)

    # Also checks if the user input AM or NOT
    if isam == False and was12 == False:
        hour += 12

    # Checks if the hours exceed 24, if it does, then it will add a day and take into account extra hours.
    if hour > 24:
        day += 1
        tempHour = 0
        while hour > 24:
            tempHour += 1
            hour -= 1
        hour = tempHour

    # Makes a later date and formats it to UTC
    laterDate = time_zone_format(year, month, day, hour, minute)
    basicTimeLater = datetime.strptime(laterDate, fmt)
    tz_later = basicTimeLater.astimezone(tz=timezoneUTC)

    # Takes the difference in seconds
    timeDifferenceSeconds = subtract_time_zone(tz_later, tz_now)

    # Prepares for printing
    tz_final = basicTimeLater.astimezone(tz=timezoneLocal)
    tz_print = tz_final.strftime(printFmt)

    # Checks if the error was triggered or not
    if timeErrorTriggered:
        await ctx.respond("Choose valid perimeters.. Check to see if you chose the correct option for 'isam' If it is 12pm choose false.", ephemeral=False)
    else:
        print("Message scheduled..")
        await ctx.respond(f"Message scheduled for {tz_print} or {timeDifferenceSeconds} seconds.", ephemeral=True)
        await asyncio.sleep(timeDifferenceSeconds)
        await ctx.respond(message, ephemeral = False)

# Returns github link for the bot
@client.slash_command(name="github", description="View source code and instructions.", integration_types={discord.IntegrationType.user_install}, ephemeral=True)
async def github(ctx: discord.ApplicationContext):
    await ctx.respond("https://github.com/InvaderGator/GatorBot")

# Function to match timezone with pytz libary
def find_time_zone(string):
    # Lowercase then match case to always get a proper timezone
    # If there is not a match then it just returns what the user inputed.
    lowercase = string.lower()
    match lowercase:
        case "est":
            return "US/Eastern"
        case "cst":
            return "US/Central"
        case "mst":
            return "US/Mountain"
        case "pst":
            return "US/Pacific"
        case _:
            return string

# Function to actually ADD hours to the timezone, resulting in proper scheduling times in the main schedule call.
def subtract_initial_time_zone(hour, timezone):
    # Another match case, this time returns time offset.
    # If there is no match it returns an empty string to mess up the program intentionally
    lowercase = timezone.lower()
    match lowercase:
        case "est":
            return hour + 0
        case "cst":
            return hour + 1
        case "mst":
            return hour + 2
        case "pst":
            return hour + 3
        case _:
            return ""

# Function to return difference in time in seconds for async sleep.
# If tz1 is greater than tz2 returns an empty string.
def subtract_time_zone(tz2, tz1):
    # Accounts if tz1 is greater than tz2
    # Usually if tz1 is greater than tz2 it returns a negative number, and instantly submits a message.
    if(tz1 > tz2):
        timeErrorTriggered = True
        return ""

    # Takes the difference in seconds and returns it as an INT
    timeDelta = tz2 - tz1
    timeDeltaSeconds = timeDelta.total_seconds()
    return int(timeDeltaSeconds)

# Function to format timezone
def time_zone_format(year, month, day, hour, minute):
    # New variables to have zeros in the final format.
    newMonth = add_zero(month)
    newDay = add_zero(day)
    newHour = add_zero(hour)
    newMinute = add_zero(minute)

    # Returns a new string that is formatted literally
    newString = f"{year}-{newMonth}-{newDay} {newHour}:{newMinute}"
    return newString

# Function to add zero to assist in time_zone_format()
def add_zero(number):
    # Adds zero based on whether the number is greater than nine.
    returnNumber = number
    if number < 10:
        returnNumber = f'0{number}'
    return returnNumber

#RUNS BOT
client.run(os.getenv('DISCORD_TOKEN'))