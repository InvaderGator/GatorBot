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

# Load the .env file
load_dotenv()

# Creates the client class for the discord bot libary
intents = discord.Intents.default()
intents.members = True
intents.emojis = True

client = discord.Bot(intents=intents)

# Admin ID
adminId = int(os.getenv('ID_GATOR'))
theFourIds = [
    adminId,
    int(os.getenv("ID_A1")),
    int(os.getenv("ID_MOSH")),
    int(os.getenv("ID_RANCH"))]

# Create formats
fmt = "%y-%m-%d %H:%M"
printFmt = "%m-%d %H:%M %Z"
printFmtNoTimezone = "%m/%d, %H:%M"

# Sends message when the bot is ready.
@client.event
async def on_ready():
    print(f"{client.user} is ready and online!")

r'''
  ____       _              _       _ _                 |
 / ___|  ___| |__   ___  __| |_   _| (_)_ __   __ _     |
 ___ \ / __| '_ \ / _ \/ _` | | | | | | '_ \ / _` |     |
  ___) | (__| | | |  __/ (_| | |_| | | | | | | (_| |    |
 |____/ \___|_| |_|\___|\__,_|\__,_|_|_|_| |_|\__, |    |
                                              |___/     |
'''

scheduling = client.create_group("scheduling", "Commands that have to do with scheduling.", integration_types={discord.IntegrationType.user_install})
timezoneArray = ["est", "cst", "mst", "pst"]

# Schedules a message based on timezone objects.
# One now and one later.
@scheduling.command(name="date", description="schedule based on timezone date.")
async def date(
    ctx: discord.ApplicationContext,
    message: discord.Option(str, description="Message you want to schedule."),
    timezone: discord.Option(str, description="Which timezone you're in.", choices=timezoneArray),
    month: discord.Option(int, description="Month 0-12 to schedule for."),
    day: discord.Option(int, description="Which day to schedule for."),
    hour: discord.Option(int, description="Which hour to schedule for"),
    isam: discord.Option(bool, description="If the message scheduled is for AM type True, otherwise, type False"),
    minute: discord.Option(int, description="What minute, leave empty for 0.", default=0)
):
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
    if isam == True and was12 == True:
        hour -= 12

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

# Schedules a message based on minutes or hours given
@scheduling.command(name="delay", description="Schedule a message based on different time inputs.")
async def delay(
        ctx: discord.ApplicationContext,
        message: discord.Option(str, description="Message you want to schedule."),
        time: discord.Option(int, description="How long you want the message to be delayed by"),
        ishour: discord.Option(bool, description="Is this scheduled for an hour? Default is False", default=False),

):
    # Converts to seconds if minutes, and to minutes if hours
    finalTime = time * 60
    minuteOrHour = "minutes"

    # If an hour is given, then it will give the user seconds still.
    if ishour == True:
        finalTime = finalTime * 60
        minuteOrHour = "hours"

    await ctx.respond(f"Message scheduled for {time} {minuteOrHour}, or {finalTime} seconds..", ephemeral=True)
    print("Time Message Scheduled..")
    await asyncio.sleep(finalTime)
    await ctx.respond(message, ephemeral = False)

# Returns time in given timezone
@scheduling.command(name="timein", description="Gives time in X timezone.")
async def time_in(
    ctx: discord.ApplicationContext,
    timezone: discord.Option(str, description="Which timezone to use to get the time?", choices=timezoneArray)
):
    # String of timezone
    tzString=find_time_zone(timezone)

    # Initializes timezone converter
    tz = pytz.timezone(find_time_zone(tzString))

    # Makes a tzinfo class and converts it to timezone
    basicTimeNow = datetime.now()
    tz_now = basicTimeNow.astimezone(tz=tz)

    # Print message to discord
    tz_print = tz_now.strftime(printFmtNoTimezone)
    await ctx.respond(f'The day and hour is {tz_print} in {tzString}.')

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


r'''
     _    _   ____        _   _   _        ____                  _  __ _        |
    / \  / | | __ )  ___ | |_| |_| | ___  / ___| _ __   ___  ___(_)/ _(_) ___   |
   / _ \ | | |  _ \ / _ \| __| __| |/ _ \ \___ \| '_ \ / _ \/ __| | |_| |/ __|  |
  / ___ \| | | |_) | (_) | |_| |_| |  __/  ___) | |_) |  __/ (__| |  _| | (__   |
 /_/   \_\_| |____/ \___/ \__|\__|_|\___| |____/| .__/ \___|\___|_|_| |_|\___|  |
                                                |_|                             |                            
'''

a1bottle = client.create_group("a1bottle", "Commands meant for use in the A1 Bottle", integration_types={discord.IntegrationType.guild_install})

# Answers for the polling group!


@a1bottle.command(name="immigrationpoll", description="Start a poll on to let someone into the A1Bottle or not.")
async def immigration_poll(ctx: discord.ApplicationContext, user: str):
    answers = [
        discord.PollAnswer("Yes!", emoji=client.get_emoji(1464663059489489250)),
        discord.PollAnswer("No!", emoji=client.get_emoji(1464663099008090385)),
        discord.PollAnswer("Gulag!", emoji=client.get_emoji(1464663163873001737))
    ]

    fixedUserId = remove_extra(user)
    person = client.get_user(fixedUserId)

    if is_four(ctx.author.id):
        poll = discord.Poll(question=f"Let in {person} into the A1 Bottle?", answers=answers, duration=24)
        await ctx.respond(poll=poll)
    else:
        await ctx.respond("You are not authorized to use this bot. You have been reported to the Four.")

def is_four(userid: int):
    for x in theFourIds:
        if x == userid:
            return True
    return False
def remove_extra(userid: str):
    newUserIdArray = []

    for x in userid:
        if (not (x == "<" or x == ">" or x == "@" or x == " ")):
            newUserIdArray.append(x)

    newUserId = "".join(newUserIdArray)
    return int(newUserId)

r'''
  _____                 _   _                   |
 |  ___|   _ _ __   ___| |_(_) ___  _ __  ___   |
 | |_ | | | | '_ \ / __| __| |/ _ \| '_ \/ __|  |
 |  _|| |_| | | | | (__| |_| | (_) | | | \__ |  |
 |_|   \__,_|_| |_|\___|\__|_|\___/|_| |_|___/  |
                                            
'''
# Returns github link for the bot
@client.slash_command(name="github", description="View source code and instructions.", integration_types={discord.IntegrationType.user_install}, ephemeral=True)
async def github(ctx: discord.ApplicationContext):
    await ctx.respond("https://github.com/InvaderGator/GatorBot")

# Run the Bot
client.run(os.getenv('DISCORD_TOKEN'))
