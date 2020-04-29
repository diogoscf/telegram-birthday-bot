"""
Bot that wishes happy birthday
"""

import datetime
import json
import logging
import math
import os
import requests
import sys

from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext

# Load .env file
load_dotenv()

TOKEN = os.getenv("TOKEN")

# Get ordinal function
ordinal = lambda n: "%d%s" % (
    n,
    "tsnrhtdd"[(math.floor(n / 10) % 10 != 1) * (n % 10 < 4) * n % 10 :: 4],
)

# Enabling logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger()

def start_handler(update: Update, context: CallbackContext):
    """Handles the /start command"""
    logger.info("User {} started bot".format(update.effective_user["id"]))
    update.message.reply_text(
        "Hello there! You have succesfully initiated the birthday wishing bot"
    )

    context.job_queue.run_once(
        wishHB, 0, context={"context": update.message.chat_id, "first": True}
    )

    nextHour = datetime.datetime.utcnow().hour + 1
    context.job_queue.run_repeating(
        wishHB,
        900,
        context={"context": update.message.chat_id, "first": False},
        first=datetime.time(nextHour),
    )  # Timezones can have offsets of 15 minutes and 15min = 900s


def wishHB(context: CallbackContext):
    """Wishes happy birthday"""
    bdays = getBdays()
    job = context.job
    now = datetime.datetime.utcnow()
    logger.info("RUN")
    for p in bdays:
        month = [p["utc_dob"].month, now.month]
        day = [p["utc_dob"].day, now.day]
        hour = [p["utc_dob"].hour, now.hour]
        minute = [p["utc_dob"].minute, now.minute]
        checkArr = [month, day, hour, minute]
        if job.context["first"]:
            there = now + p["delta"]
            if there.day == p["dob"].day:
                checkArr = [checkArr[0],]
        if any(l[0] != l[1] for l in checkArr):
            continue
        age = now.year - p["utc_dob"].year
        logger.info(
            "Found birthday for {}! Wishing...".format(
                p["username"] if len(p["username"]) else p["name"]
            )
        )
        context.bot.send_message(
            job.context["context"],
            "Happy {} birthday {}!".format(
                ordinal(age), p["username"] if len(p["username"]) else p["name"]
            ),
        )


def getBdays():
    """Parses the birthdays.json file"""
    # data = requests.get(
    #     "https://raw.githubusercontent.com/diogoscf/telegram-birthday-bot/master/birthdays.json"
    # ).json()
    data = json.load(open("birthdays.json", "r", encoding="utf-8"))
    output = []
    for p in data:
        diff = [int(x) for x in p["tz"].replace("UTC", "").split(":")]
        delta = datetime.timedelta(hours=diff[0], minutes=diff[1])
        output.append(
            {
                "name": p["name"],
                "dob": datetime.datetime.strptime(p["dob"], "%d.%m.%Y"),
                "utc_dob": datetime.datetime.strptime(p["dob"], "%d.%m.%Y") - delta,
                "username": p["username"],
                "delta": delta,
            }
        )
    return output


if __name__ == "__main__":
    logger.info("Starting script")
    updater = Updater(TOKEN, use_context=True)

    updater.dispatcher.add_handler(CommandHandler("start", start_handler))
    # updater.dispatcher.add_handler(CommandHandler('stop', Stop_timer, pass_job_queue=True))

    updater.start_polling()
