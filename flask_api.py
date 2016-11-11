#!/usr/bin/python
from flask import Flask, render_template, request, jsonify
app = Flask(__name__)
import _thread
from lib import nhl
from lib import light
from lib import nhl_watch


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


@app.route('/api/v1/team/<team>/score')
def score(team):
    # Fetch and return the current score of the team
    response = { 'score': nhl.fetch_score(team) }
    return jsonify(response)


@app.route('/api/v1/team/<team>/game')
def game(team):
    response = { 'game' : nhl.check_if_game(team)}
    return jsonify(response)


@app.route('/api/v1/goal_light/activate')
def goal_light_activate():
    light.activate_goal_light()
    return "OK"


@app.route('/api/v1/team/<team>/watch_goals')
def watch_goals(team):

    delay = request.args.get('delay', '1')

    print("Starting goal watcher in a new thread")
    _thread.start_new_thread(nhl_watch.watch_team_goals, (team, delay))

    return "OK"


if __name__ == "__main__":


    print("Setup of the GOAL light")
    light.setup()

    print("Starting the Flask app ...")
    app.run(host='0.0.0.0', port=8080, debug=True)

    print("Cleanup of the GOAL light")
    light.cleanup()
