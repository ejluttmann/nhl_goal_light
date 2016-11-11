#!/usr/bin/python

import datetime
import time
import os
import requests


API_URL = "http://localhost:8080/api/v1"


def long_sleep(sleep_period):
    """ Function to sleep if not in season or no game. Inputs sleep period depending if it's off season or no game."""
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


def watch_team_goals(team, delay):

    old_score = 0
    new_score = 0
    gameday = False
    season = False

    # Choose and return team_id to setup code
    # team = input("Enter team you want to setup (without city) (Default: Canadiens) \n")
    # if team == "":
    #     team = "Canadiens"

    print("team : {}".format(team))

    # query the api to get the ID
    response = requests.get("{}/team/{}/id".format(API_URL, team))
    team_id = response.json()['id']
    print("team id : {}".format(team_id))

    # delay = input("Enter delay required to sync : \n")
    # if delay is "":
    #     delay = 0
    # delay = float(delay)

    print("delay : {}".format(delay))

    while (True):

         # check if in season
        response = requests.get("{}/season".format(API_URL))
        season = response.json()['season']

        print("season : {}".format(season))

        # check if game
        response = requests.get("{}/team/{}/game".format(API_URL, team))
        gameday = response.json()['game']

        # sleep 2 seconds to avoid errors in requests (might not be
        # enough...)
        time.sleep(1)

        if season:
            if gameday:

                # Check score online and save score
                response = requests.get("{}/team/{}/score".format(API_URL, team))
                new_score = response.json()['score']

                # If new game, replace old score with 0
                if old_score > new_score:
                    old_score = 0

                # If score change...
                if new_score > old_score:
                    #!!!!!!!!ADD DELAY HERE!!!!!!!
                    print("OOOOOHHHHHHH...")
                    time.sleep(delay)
                    # save new score
                    print("GOAL!")
                    old_score = new_score

                    # activate_goal_light()
                    requests.get("{}/goal_light/activate".format(API_URL))

                # If the button is pressed
                # Comment out this section if no input button is connected
                # to RPi
                # if(GPIO.input(15) == 0):
                #     # save new score
                #     print("GOAL!")
                #     old_score = new_score
                #     activate_goal_light()
            else:
                print("No Game Today!")
                long_sleep("day")
        else:
            print("OFF SEASON!")
            long_sleep("season")
