from flask import (
    Flask,
    session,
    render_template,
    url_for,
    redirect,
    request,
    flash,
    Blueprint,
)
import random
import json
import pathlib
from functions import *
from breakaway import breakaway


app = Flask(__name__)

app.register_blueprint(breakaway, url_prefix="/breakaway")

# set a 'SECRET_KEY' to enable the Flask session cookies
app.config["SECRET_KEY"] = "not_very_secret"

basedir = pathlib.Path(__file__).parent.resolve()


from flask_debugtoolbar import DebugToolbarExtension

# the toolbar is only enabled in debug mode:
app.debug = True
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


# @app.route("/home2")
# def home2():
#     # clear all cookies to setup new player
#     session.clear()
#     return render_template("home2.html")


@app.route("/setup", methods=["POST", "GET"])
def setup():
    # collect form info
    team_color = request.form["team_color"]

    initialize_session()
    load_player_deck(team_color)
    check_for_ai_teams()

    # general options checked
    if "exhaustion_reminder" in request.form:
        session["is_exhaustion_reminder"] = request.form["exhaustion_reminder"]

    if "view_played" in request.form:
        session["view_played"] = request.form["view_played"]

    if "is_meteo" in request.form:
        session["options"]["is_meteo"] = request.form["is_meteo"]

    # begin dealing with breakaway options
    if "breakaway_option" in request.form:
        # setup the breakaway variables
        session["breakaway_option"] = request.form["breakaway_option"]
        session["is_breakaway_winner_0"] = False
        session["is_breakaway_winner_1"] = False
        session.modified = True
        return render_template("breakaway/breakaway_deck_choice.html")
    session.modified = True
    return redirect(url_for("choose_deck"))


@app.route("/choose_deck")
def choose_deck():
    session["chosen_cards"] = []
    session["round"] += 1
    session["is_sprint_exaust"] = False
    session["is_roll_exaust"] = False
    if session.get("is_meteo"):
        session["hand_size"] = 4
    session.modified = True
    return render_template("choose_deck.html")


@app.route("/card_picker_1/<chosen_deck>", methods=["POST", "GET"])
def card_picker_1(chosen_deck):
    # chosen_deck = request.form["deck_choice"]
    shuffle_and_draw(chosen_deck, session["hand_size"])
    current_hand = session["current_hand"]
    session["current_deck"] = chosen_deck
    if session["current_deck"] == "sprint":
        deck_for_title = "Sprinter"
    else:
        deck_for_title = "Roller"
    session.modified = True
    form_destination = "card_picker_2"
    return render_template(
        "card_picker.html",
        current_hand=current_hand,
        deck_for_title=deck_for_title,
        form_destination=form_destination,
    )


@app.route("/card_picker_2", methods=["POST", "GET"])
def card_picker_2():
    # get card choice from last page
    chosen_card_position = request.form["card_choice"]
    # assign that card choice to chosen card and add that to session list
    chosen_card = session["current_hand"].pop(int(chosen_card_position))
    session["chosen_cards"].append(chosen_card)

    # add rest of hand to facedown cards
    if session["current_deck"] == "sprint":
        session["sprint_faceup"].extend(session["current_hand"])
        session["current_hand"] = []
        session["sprint_discards"].append(chosen_card)
    else:
        session["roll_faceup"].extend(session["current_hand"])
        session["current_hand"] = []
        session["roll_discards"].append(chosen_card)

    # shuffle and deal hand for other deck
    if session["current_deck"] == "sprint":
        shuffle_and_draw("roll", session["hand_size"])
        session["current_deck"] = "roll"
    else:
        shuffle_and_draw("sprint", session["hand_size"])
        session["current_deck"] = "sprint"

    current_hand = session["current_hand"]
    if session["current_deck"] == "roll":
        deck_for_title = "Roller"
    else:
        deck_for_title = "Sprinter"
    previous_card = session["chosen_cards"][0]
    session.modified = True
    form_destination = "hidden_cards"
    return render_template(
        "card_picker.html",
        current_hand=current_hand,
        deck_for_title=deck_for_title,
        previous_card=previous_card,
        form_destination=form_destination,
    )


@app.route("/hidden_cards", methods=["POST", "GET"])
def hidden_cards():
    # get card choice from last page
    chosen_card_position = request.form["card_choice"]
    # assign that card choice to chosen card and add that to session list
    chosen_card = session["current_hand"].pop(int(chosen_card_position))
    session["chosen_cards"].append(chosen_card)

    # add rest of hand to facedown cards
    if session["current_deck"] == "sprint":
        session["sprint_faceup"].extend(session["current_hand"])
        session["current_hand"] = []
        session["sprint_discards"].append(chosen_card)
    else:
        session["roll_faceup"].extend(session["current_hand"])
        session["current_hand"] = []
        session["roll_discards"].append(chosen_card)
    session["current_deck"] = []
    session["current_hand"] = []
    session.modified = True
    return render_template("hidden_cards.html")


@app.route("/revealed_cards/")
def revealed_cards():
    chosen_cards = session["chosen_cards"]
    next_round = int(session["round"]) + 1
    return render_template(
        "revealed_cards.html", chosen_cards=chosen_cards, next_round=next_round
    )


@app.route("/add_exhaustion", methods=["POST"])
def add_exhaustion():
    deck = request.form["deck_id"]
    print("I am inside the add_exhaustion route")
    print(deck)
    if deck == "sprint":
        session["sprint_faceup"].append([2, "S", "exhaustion-card"])
        # flash("Exhaustion card added to Sprinter Deck")
        session["is_sprint_exaust"] = True

    else:
        session["roll_faceup"].append([2, "R", "exhaustion-card"])
        # flash("Exhaustion card added to Roller Deck")
        session["is_roll_exaust"] = True
    session.modified = True
    return redirect(url_for("revealed_cards"))


@app.route("/test_endpoint", methods=["POST", "GET"])
def test_endpoint():

    return render_template("trial.html")


if __name__ == "__main__":
    # app.run(debug=True)
    app.run(host="0.0.0.0")
