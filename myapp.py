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
from blue.breakaway.breakaway import breakaway
import pprint


app = Flask(__name__)

app.register_blueprint(breakaway, url_prefix="/breakaway")

# set a 'SECRET_KEY' to enable the Flask session cookies
app.config["SECRET_KEY"] = "not_very_secret"

basedir = pathlib.Path(__file__).parent.resolve()

#
# from flask_debugtoolbar import DebugToolbarExtension
#
# # the toolbar is only enabled in debug mode:
# app.debug = True
# toolbar = DebugToolbarExtension(app)
# # DEBUG_TB_INTERCEPT_REDIRECTS = False
# app.config["DEBUG_TB_INTERCEPT_REDIRECTS"] = False
# # Set the secret key to the debugtoolbar
# app.secret_key = "my_secret"


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
        session["is_meteo"] = request.form["is_meteo"]

    # begin dealing with breakaway options
    if "breakaway_option" in request.form:
        # setup the breakaway variables
        session["breakaway_option"] = request.form["breakaway_option"]
        session.modified = True
        return render_template("breakaway/breakaway_deck_choice.html")
    session.modified = True
    return redirect(url_for("choose_deck"))


@app.route("/choose_deck")
def choose_deck():
    session["chosen_cards"] = []
    session["round"] += 1
    if session.get("is_meteo"):
        session["deck_1"]["hand_size"] = 4
        session["deck_2"]["hand_size"] = 4
    session.modified = True
    # freeze the state to come back to the beginning of the round
    # freeze_state = dict(session)
    return render_template("choose_deck.html")


@app.route("/card_picker_1/<chosen_deck>", methods=["POST", "GET"])
def card_picker_1(chosen_deck):

    shuffle_and_draw(chosen_deck)
    current_hand = session["current_hand"]
    session["current_deck"] = chosen_deck

    deck_for_title = session[chosen_deck]["name"]

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
    if session["current_deck"] == "deck_1":
        session["chosen_cards"].insert(0, chosen_card)
    else:
        session["chosen_cards"].insert(1, chosen_card)

    # add rest of hand to facedown cards
    current_deck = session["current_deck"]

    session[current_deck]["recycled"].extend(session["current_hand"])
    session["current_hand"] = []
    session[current_deck]["discards"].append(chosen_card)

    # shuffle and deal hand for other deck

    if session["current_deck"] == "deck_1":
        shuffle_and_draw("deck_2")
        session["current_deck"] = "deck_2"
        current_deck = session["current_deck"]
    else:
        shuffle_and_draw("deck_1")
        session["current_deck"] = "deck_1"
        current_deck = session["current_deck"]

    current_hand = session["current_hand"]

    deck_for_title = session[current_deck]["name"]

    previous_card = chosen_card
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
    if session["current_deck"] == "deck_1":
        session["chosen_cards"].insert(0, chosen_card)
    else:
        session["chosen_cards"].insert(1, chosen_card)

    # add rest of hand to facedown cards
    current_deck = session["current_deck"]
    session[current_deck]["recycled"].extend(session["current_hand"])
    session["current_hand"] = []
    session[current_deck]["discards"].append(chosen_card)

    session["current_deck"] = []

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
    action = request.form["action"]
    print(action)

    # add an exaustion card to recylced deck
    if action == "add":
        session[deck]["recycled"].append(
            [2, session[deck]["card-letter"], "exhaustion-card"]
        )
    if action == "remove":
        session[deck]["recycled"].pop()

    session.modified = True
    return redirect(url_for("revealed_cards"))


@app.route("/change_hand_size", methods=["POST"])
def change_hand_size():
    size_change_info = request.form["deck_id"]
    print(size_change_info)
    if size_change_info == "deck_1_tailwind":
        session["deck_1"]["hand_size"] = 5

    if size_change_info == "deck_1_headwind":
        session["deck_1"]["hand_size"] = 3

    if size_change_info == "deck_1_nowind":
        session["deck_1"]["hand_size"] = 4

    if size_change_info == "deck_2_tailwind":
        session["deck_2"]["hand_size"] = 5
    if size_change_info == "deck_2_headwind":
        session["deck_2"]["hand_size"] = 3
    if size_change_info == "deck_2_nowind":
        session["deck_2"]["hand_size"] = 4
    session.modified = True
    return ("", 204)


# @app.route("/test_endpoint", methods=["POST", "GET"])
# def test_endpoint():
#
#     return render_template("trial.html")


# if __name__ == "__main__":
#     # app.run(debug=True)
#     app.run(host="0.0.0.0")
