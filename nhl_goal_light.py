#!/usr/bin/python

import datetime
import time
import os
import requests
import platform

if "armv" in platform.machine():
    # import RPI GPIO if running on RPI
    import RPi.GPIO as GPIO
else:
    # import mock GPIO if not running on RPI
    from lib import gpio_mock as GPIO

# Setup GPIO on raspberry pi
GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(False)
# Tell the program you want to use pin number 15 as the input
GPIO.setup(15, GPIO.IN, GPIO.PUD_DOWN)  # If no input button connected, comment this line out


def sleep(sleep_period):
    """ Function to sleep if not in season or no game.
    Inputs sleep period depending if it's off season or no game."""

    # Get current time
    now = datetime.datetime.now()
    # Set sleep time for no game today
    if "day" in sleep_period:
        delta = datetime.timedelta(days=1)
    # Set sleep time for not in season
    elif "season" in sleep_period:
        # If in August, 31 days else 30
        if now.month is 8:
            delta = datetime.timedelta(days=31)
        else:
            delta = datetime.timedelta(days=30)
    next_day = datetime.datetime.today() + delta
    next_day = next_day.replace(hour=0, minute=0)
    sleep = next_day - now
    sleep = sleep.total_seconds()
    time.sleep(sleep)


def setup_nhl():
    """Function to setup the nhl_goal_light.py with team,
    team_id and API_URL"""

    lines = ""
    """
    Try to find a settings.txt file in the folder to automaticly setup
    the goal light with pre-desired team, delay and API_URL.
    settings.txt file should as such : Enter API URL, team_id, delay,
    each on a separate line in this order. LEAVE EMPTY if you want to
    manually input every time. If program can't find settings.txt file or if
    file is empty, it will ask for user input.
    """
    if os.path.exists('./settings.txt'):
        # get settings from file
        f = open('settings.txt', 'r')
        lines = f.readlines()

    # find API_URL
    try:
        API_URL = lines[1].strip('\n')
    except IndexError:
        API_URL = ""
    if API_URL == "":
        API_URL = input(
            "Enter Flask API IP or URL. (If empty, default will be localhost) \n")
        if API_URL == "":
            API_URL = "http://localhost:8080/api/v1/"
        else:
            API_URL = "http://" + API_URL + ":8080/api/v1/"

    # find team_id
    try:
        team_id = lines[2].strip('\n')
    except IndexError:
        team_id = ""
    if team_id == "":
        team = input(
            "Enter team you want to setup (without city) (Default: Canadiens) \n")
        if team == "":
            team = "Canadiens"
        else:
            team = team.title()
    # query the api to get the ID
    response = requests.get("{}team/{}/id".format(API_URL, team))
    team_id = response.json()['id']

    # find delay
    try:
        delay = lines[3].strip('\n')
    except IndexError:
        delay = ""
    if delay is "":
        delay = input("Enter delay required to sync : \n")
        if delay is "":
            delay = 0
    delay = float(delay)
    print(team_id, API_URL, delay)
    return (team_id, API_URL, delay)


if __name__ == "__main__":

    old_score = 0
    new_score = 0
    gameday = False
    season = False

    team_id, API_URL, delay = setup_nhl()

    try:

        while (True):

            # If the button is pressed, activate light and sound
            # Comment out this section if no input button or not on RPI
            if "armv" in platform.machine() and (GPIO.input(15) == GPIO.HIGH):
                print("Button Pressed!")
                requests.get("{}goal_light/activate".format(API_URL))

            # check if in season
            response = requests.get("{}season".format(API_URL))
            season = response.json()['season']

            print("season : {}".format(season))

            # check if game
            response = requests.get("{}team/{}/game".format(API_URL, team_id))
            gameday = response.json()['game']

            print("gameday : {}".format(gameday))

            time.sleep(1)

            if season:
                if gameday:

                    # Check score online and save score
                    response = requests.get(
                        "{}team/{}/score".format(API_URL, team_id))
                    new_score = response.json()['score']

                    # If new game, replace old score with 0
                    if old_score > new_score:
                        old_score = 0

                    # If score change...
                    if new_score > old_score:
                        """!!!!!!!!ADD DELAY HERE!!!!!!!"""
                        print("OOOOOHHHHHHH...")
                        time.sleep(delay)
                        # save new score
                        print("GOAL!")
                        old_score = new_score
                        # activate_goal_light()
                        requests.get("{}goal_light/activate".format(API_URL))

                else:
                    print("No Game Today!")
                    sleep("day")
            else:
                print("OFF SEASON!")
                sleep("season")

    except KeyboardInterrupt:
        print("\nCtrl-C pressed")
