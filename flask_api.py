#!/usr/bin/python
from flask import Flask, render_template, request, jsonify
app = Flask(__name__)

from lib import nhl
from lib import light

 
#mute flask to only errors
import logging
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)



@app.route('/')
def home():
    return render_template("home.html")


@app.route('/api/v1/season')
def season():
    response = { 'season': nhl.check_season() }
    return jsonify(response)


@app.route('/api/v1/teams')
def teams():
    # Fetch the list of teams
    teams = nhl.get_teams()
    return jsonify(teams)


@app.route('/api/v1/team/<team>/id')
def team_id(team):
    # Fetch and return the official ID of the team
    response = { 'id': nhl.get_team_id(team) }
    return jsonify(response)


@app.route('/api/v1/team/<team_id>/score')
def score(team_id):
    # Fetch and return the current score of the team
    response = { 'score': nhl.fetch_score(team_id) }
    return jsonify(response)


@app.route('/api/v1/team/<team_id>/game')
def game(team_id):
    response = { 'game' : nhl.check_if_game(team_id)}
    return jsonify(response)
  
  
@app.route('/api/v1/team/<team_id>/end_game')
def end_game(team_id):
    response = { 'end_game' : nhl.check_game_end(team_id)}
    return jsonify(response)


@app.route('/api/v1/goal_light/activate')
def goal_light_activate():
    light.activate_goal_light()
    return "OK"


if __name__ == "__main__":

    print("Setup of the GOAL light")
    light.setup()


    print("Starting the Flask app ...")
#    app.run(host='0.0.0.0', port=8080, debug=True)
    app.run(host='0.0.0.0', port=8080)

    print("\nCleanup of the GOAL light")
    light.cleanup()


