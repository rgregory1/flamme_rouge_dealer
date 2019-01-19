from flask import Flask, session, render_template, url_for, redirect, request
import random
from flask_debugtoolbar import DebugToolbarExtension
import json

app = Flask(__name__)

# the toolbar is only enabled in debug mode:
app.debug = True

# set a 'SECRET_KEY' to enable the Flask session cookies
app.config["SECRET_KEY"] = "not_very_secret"

# app.config['PERMANENT_SESSION_LIFETIME'] = False

toolbar = DebugToolbarExtension(app)
# DEBUG_TB_INTERCEPT_REDIRECTS = False
app.config["DEBUG_TB_INTERCEPT_REDIRECTS"] = False

# Set the secret key to the debugtoolbar
app.secret_key = "my_secret"


@app.route("/")
def home():
    # clear all cookies to setup new player
    session.clear()
    return render_template("home.html")


@app.route("/setup", methods=["POST", "GET"])
def setup():
    # collect form info
    session["player_name"] = request.form["player_name"]
    team_color = request.form["team_color"]
    session["round"] = 0
    session['current_hand'] = []
    session['choosen_cards'] = []
    # load cards from json data and add team colors
    with open('static/sprinter_cards.json', 'r') as f:
        session['sprint_deck'] = json.load(f)
    for card in session['sprint_deck']:
        card.append(team_color)
    with open('static/roller_cards.json', 'r') as f:
        session['roll_deck'] = json.load(f)
    for card in session['roll_deck']:
        card.append(team_color)
    session['sprint_discards'] = []
    session['sprint_faceup'] = []
    session['roll_discards'] = []
    session['roll_faceup'] = []
    session['deck_number'] = 0
    session['current_deck'] = ''
    session.modified = True
    return redirect(url_for("choose_deck"))

@app.route('/choose_deck')
def choose_deck():
    session['round'] += 1
    return render_template('choose_deck.html')

@app.route("/card_picker_1", methods=["POST", "GET"])
def card_picker_1():
    chosen_deck = request.form["deck_choice"]
    if chosen_deck == 'sprint':
        random.shuffle(session["sprint_deck"])
        for x in range(4):
            current_card = session["sprint_deck"].pop()
            session["current_hand"].append(current_card)
    else:
        random.shuffle(session["roll_deck"])
        for x in range(4):
            current_card = session["roll_deck"].pop()
            session["current_hand"].append(current_card)
    current_hand = session['current_hand']
    session['current_deck'] = chosen_deck
    if session['current_deck'] == 'sprint':
        deck_for_title = 'Sprinter'
    else:
        deck_for_title = 'Roller'
    session.modified = True
    return render_template("card_picker.html", current_hand=current_hand, deck_for_title=deck_for_title)

@app.route('/card_picker_2', methods=["POST", "GET"])
def card_picker_2():
    # get card choice from last page
    choosen_card_position = request.form['card_choice']
    #assign that card choice to chosen card and add that to session list
    chosen_card = session['current_hand'].pop(int(choosen_card_position))
    session['choosen_cards'].append(chosen_card)

    #add rest of hand to facedown cards
    if session['current_deck'] == 'sprint':
        session['sprint_faceup'].extend(session['current_hand'])
        session['current_hand'] = []
        session['sprint_discards'].append(chosen_card)
    else:
        session['roll_faceup'].extend(session['current_hand'])
        session['current_hand'] = []
        session['roll_discards'].append(chosen_card)

    if session['current_deck'] == 'roll':
        random.shuffle(session["sprint_deck"])
        for x in range(4):
            current_card = session["sprint_deck"].pop()
            session["current_hand"].append(current_card)
        session['current_deck'] = 'sprint'
    else:
        random.shuffle(session["roll_deck"])
        for x in range(4):
            current_card = session["roll_deck"].pop()
            session["current_hand"].append(current_card)
        session['current_deck'] = 'roll'
    current_hand = session['current_hand']
    if session['current_deck'] == 'roll':
        deck_for_title = 'Roller'
    else:
        deck_for_title = 'Sprinter'
    previous_card = session['choosen_cards'][0]
    session.modified = True
    return render_template('card_picker_2.html', current_hand=current_hand, deck_for_title=deck_for_title, previous_card=previous_card)

@app.route('/hidden_cards', methods=['POST', 'GET'])
def hidden_cards():
    return render_template('hidden_cards.html')

@app.route('/test_endpoint', methods=["POST", "GET"])
def test_endpoint():

    return render_template('trial.html')


if __name__ == "__main__":
    app.run(debug=True)
# app.run(host="0.0.0.0")
