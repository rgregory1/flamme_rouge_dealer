from flask import Flask, session, render_template, url_for, redirect, request, flash
import random
import json
import pathlib

app = Flask(__name__)

basedir = pathlib.Path(__file__).parent.resolve()

# set a 'SECRET_KEY' to enable the Flask session cookies
app.config["SECRET_KEY"] = "not_very_secret"


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
    # session["player_name"] = request.form["player_name"]
    team_color = request.form["team_color"]
    session["round"] = 0
    session["current_hand"] = []
    session["chosen_cards"] = []

    # general options checked
    if "exhaustion_reminder" in request.form:
        session["is_exhaustion_reminder"] = request.form["exhaustion_reminder"]

    if "view_played" in request.form:
        session["view_played"] = request.form["view_played"]

    if "add_sprint_exhaustion" in request.form:
        add_sprint_exhaustion = int(request.form["add_sprint_exhaustion"])
        add_roll_exhaustion = int(request.form["add_roll_exhaustion"])

    # load cards from json data and add team colors
    target_directory = basedir / "static" / "sprinter_cards.json"
    with open(target_directory) as f:
        session["sprint_deck"] = json.load(f)
    for card in session["sprint_deck"]:
        card.append(team_color)

    if add_sprint_exhaustion > 0:
        for card in range(add_sprint_exhaustion):
            session["sprint_deck"].append([2, "S", "exhaustion-card"])

    target_directory = basedir / "static" / "roller_cards.json"
    with open(target_directory) as f:
        session["roll_deck"] = json.load(f)
    for card in session["roll_deck"]:
        card.append(team_color)

    if add_roll_exhaustion > 0:
        for card in range(add_roll_exhaustion):
            session["roll_deck"].append([2, "R", "exhaustion-card"])

    if "muscle_team_color" in request.form:
        muscle_team_color = request.form["muscle_team_color"]
        session["is_muscle_team"] = True

        # setup muscle sprinter deck
        target_directory = basedir / "static" / "sprinter_cards.json"
        with open(target_directory) as f:
            session["muscle_sprint_deck"] = json.load(f)
        for card in session["muscle_sprint_deck"]:
            card.append(muscle_team_color)
        # add special muscle card
        session["muscle_sprint_deck"].append([5, "S", "muscle-card"])

        # setup muscle team roller deck
        target_directory = basedir / "static" / "roller_cards.json"
        with open(target_directory) as f:
            session["muscle_roll_deck"] = json.load(f)
        for card in session["muscle_roll_deck"]:
            card.append(muscle_team_color)

        random.shuffle(session["muscle_sprint_deck"])
        random.shuffle(session["muscle_roll_deck"])

    if "peloton_team_color" in request.form:
        peloton_team_color = request.form["peloton_team_color"]
        session["is_peloton_team"] = True

        # setup peloton sprinter deck
        target_directory = basedir / "static" / "peloton_cards.json"
        with open(target_directory) as f:
            session["peloton_deck"] = json.load(f)
        for card in session["peloton_deck"]:
            card.append(peloton_team_color)

        session["peloton_deck"].append(["A", "P", peloton_team_color])
        session["peloton_deck"].append(["A", "P", peloton_team_color])

        random.shuffle(session["peloton_deck"])

    session["sprint_discards"] = []
    session["sprint_faceup"] = []
    session["roll_discards"] = []
    session["roll_faceup"] = []
    session["current_deck"] = ""
    session["is_sprint_exaust"] = False
    session["is_roll_exaust"] = False
    # begin dealing with breakaway options
    if "breakaway_option" in request.form:
        session["breakaway_option"] = request.form["breakaway_option"]
        session["is_breakaway_winner_0"] = False
        session["is_breakaway_winner_1"] = False
        session.modified = True
        return render_template("breakaway_deck_choice.html")
    session.modified = True
    return redirect(url_for("choose_deck"))


#
# @app.route("/breakaway_deck_choice")
# def breakaway_deck_choice():
#     return render_template("breakaway_deck_choice.html")


@app.route("/breakaway_picker_1/<chosen_breakaway_deck>", methods=["POST", "GET"])
def breakaway_picker_1(chosen_breakaway_deck):
    # chosen_deck = request.form["deck_choice"]
    if chosen_breakaway_deck == "sprint":
        random.shuffle(session["sprint_deck"])
        for x in range(4):
            current_card = session["sprint_deck"].pop()
            session["current_hand"].append(current_card)
    else:
        random.shuffle(session["roll_deck"])
        for x in range(4):
            current_card = session["roll_deck"].pop()
            session["current_hand"].append(current_card)
    current_hand = session["current_hand"]
    session["current_deck"] = chosen_breakaway_deck
    if session["current_deck"] == "sprint":
        deck_for_title = "Sprinter"
    else:
        deck_for_title = "Roller"
    session.modified = True
    return render_template(
        "breakaway_picker_1.html",
        current_hand=current_hand,
        deck_for_title=deck_for_title,
    )


@app.route("/hidden_first_breakaway", methods=["POST", "GET"])
def hidden_first_breakaway():
    # get card choice from last page
    chosen_card_position = request.form["card_choice"]
    # assign that card choice to chosen card and add that to session list
    chosen_card = session["current_hand"].pop(int(chosen_card_position))
    session["chosen_cards"].append(chosen_card)

    # add rest of hand to facedown cards
    if session["current_deck"] == "sprint":
        session["sprint_faceup"].extend(session["current_hand"])
        session["current_hand"] = []
        # session["sprint_discards"].append(chosen_card)
    else:
        session["roll_faceup"].extend(session["current_hand"])
        session["current_hand"] = []
        # session["roll_discards"].append(chosen_card)
    current_deck = session["current_deck"]
    session.modified = True
    return render_template("breakaway_hidden_1.html", current_deck=current_deck)


@app.route("/revealed_breakaway_card_1")
def revealed_breakaway_card_1():
    chosen_cards = session["chosen_cards"]
    return render_template("revealed_breakaway_card_1.html", chosen_cards=chosen_cards)


@app.route("/breakaway_picker_2")
def breakaway_picker_2():
    # chosen_deck = request.form["deck_choice"]
    if session["current_deck"] == "sprint":
        random.shuffle(session["sprint_deck"])
        for x in range(4):
            current_card = session["sprint_deck"].pop()
            session["current_hand"].append(current_card)
    else:
        random.shuffle(session["roll_deck"])
        for x in range(4):
            current_card = session["roll_deck"].pop()
            session["current_hand"].append(current_card)
    current_hand = session["current_hand"]
    if session["current_deck"] == "sprint":
        deck_for_title = "Sprinter"
    else:
        deck_for_title = "Roller"
    session.modified = True
    return render_template(
        "breakaway_picker_2.html",
        current_hand=current_hand,
        deck_for_title=deck_for_title,
    )


@app.route("/breakaway_hidden_2", methods=["POST", "GET"])
def breakaway_hidden_2():
    # get card choice from last page
    chosen_card_position = request.form["card_choice"]
    # assign that card choice to chosen card and add that to session list
    chosen_card = session["current_hand"].pop(int(chosen_card_position))
    session["chosen_cards"].append(chosen_card)

    # add rest of hand to facedown cards
    if session["current_deck"] == "sprint":
        session["sprint_faceup"].extend(session["current_hand"])
        session["current_hand"] = []
        session["sprint_deck"].extend(session["sprint_faceup"])
        session["sprint_faceup"] = []
        # session["sprint_discards"].append(chosen_card)
    else:
        session["roll_faceup"].extend(session["current_hand"])
        session["current_hand"] = []
        session["roll_deck"].extend(session["roll_faceup"])
        session["roll_faceup"] = []
        # session["roll_discards"].append(chosen_card)
    # current_deck = session["current_deck"]
    revealed_card = session["chosen_cards"][0]
    hidden_card = session["chosen_cards"][1]
    current_deck = session["current_deck"]

    session.modified = True
    return render_template(
        "breakaway_hidden_2.html",
        revealed_card=revealed_card,
        hidden_card=hidden_card,
        current_deck=current_deck,
    )


@app.route("/breakaway_revealed_card_2")
def breakaway_revealed_card_2():

    # replace chosen cards with exhaustion
    chosen_card_0 = session["chosen_cards"][0]
    chosen_card_1 = session["chosen_cards"][1]
    session.modified = True
    return render_template(
        "breakaway_revealed_card_2.html",
        chosen_card_0=chosen_card_0,
        chosen_card_1=chosen_card_1,
    )


@app.route("/breakaway_winner/<place>")
def breakaway_winner(place):
    place = int(place)
    if session["current_deck"] == "sprint":
        session["sprint_deck"].append([2, "S", "exhaustion-card"])
        session["sprint_discards"].append(session["chosen_cards"][place])
    else:
        session["roll_deck"].append([2, "R", "exhaustion-card"])
        session["roll_discards"].append(session["chosen_cards"][place])
    if place == 0:
        session["is_breakaway_winner_0"] = True
    if place == 1:
        session["is_breakaway_winner_1"] = True

    session.modified = True
    return redirect(url_for("breakaway_revealed_card_2"))


@app.route("/breakaway_final_check")
def breakaway_final_check():
    breakaway_card_0 = session["chosen_cards"][0]
    breakaway_card_1 = session["chosen_cards"][1]

    if (
        session["is_breakaway_winner_0"] == True
        and session["is_breakaway_winner_1"] == True
    ):
        return redirect(url_for("choose_deck"))
    if session["is_breakaway_winner_0"] == False:
        print("inside 0 false loop")
        if session["current_deck"] == "sprint":
            session["sprint_deck"].append(breakaway_card_0)
        else:
            session["roll_deck"].append(breakaway_card_0)
    if session["is_breakaway_winner_1"] == False:
        print("inside 1 false loop")
        if session["current_deck"] == "sprint":
            session["sprint_deck"].append(breakaway_card_1)
        else:
            session["roll_deck"].append(breakaway_card_1)
    session.modified = True
    return redirect(url_for("choose_deck"))


@app.route("/choose_deck")
def choose_deck():
    session["chosen_cards"] = []
    session["round"] += 1
    session["is_sprint_exaust"] = False
    session["is_roll_exaust"] = False
    session.modified = True
    return render_template("choose_deck.html")


@app.route("/card_picker_1/<chosen_deck>", methods=["POST", "GET"])
def card_picker_1(chosen_deck):
    # chosen_deck = request.form["deck_choice"]
    if chosen_deck == "sprint":
        if len(session["sprint_deck"]) < 4:
            cards_needed = 4 - len(session["sprint_deck"])
            session["current_hand"].extend(session["sprint_deck"])
            session["sprint_deck"] = session["sprint_faceup"]
            session["sprint_faceup"] = []
            random.shuffle(session["sprint_deck"])
            for x in range(cards_needed):
                current_card = session["sprint_deck"].pop()
                session["current_hand"].append(current_card)

        else:
            random.shuffle(session["sprint_deck"])
            for x in range(4):
                current_card = session["sprint_deck"].pop()
                session["current_hand"].append(current_card)
    else:
        if len(session["roll_deck"]) < 4:
            cards_needed = 4 - len(session["roll_deck"])
            session["current_hand"].extend(session["roll_deck"])
            session["roll_deck"] = session["roll_faceup"]
            session["roll_faceup"] = []
            random.shuffle(session["roll_deck"])
            for x in range(cards_needed):
                current_card = session["roll_deck"].pop()
                session["current_hand"].append(current_card)
        else:
            random.shuffle(session["roll_deck"])
            for x in range(4):
                current_card = session["roll_deck"].pop()
                session["current_hand"].append(current_card)
    current_hand = session["current_hand"]
    session["current_deck"] = chosen_deck
    if session["current_deck"] == "sprint":
        deck_for_title = "Sprinter"
    else:
        deck_for_title = "Roller"
    session.modified = True
    return render_template(
        "card_picker.html", current_hand=current_hand, deck_for_title=deck_for_title
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

    # begin suffle of other deck
    if session["current_deck"] == "roll":
        if len(session["sprint_deck"]) < 4:
            cards_needed = 4 - len(session["sprint_deck"])
            session["current_hand"].extend(session["sprint_deck"])
            session["sprint_deck"] = session["sprint_faceup"]
            session["sprint_faceup"] = []
            random.shuffle(session["sprint_deck"])
            for x in range(cards_needed):
                current_card = session["sprint_deck"].pop()
                session["current_hand"].append(current_card)

        else:
            random.shuffle(session["sprint_deck"])
            for x in range(4):
                current_card = session["sprint_deck"].pop()
                session["current_hand"].append(current_card)
        session["current_deck"] = "sprint"
    else:
        if len(session["roll_deck"]) < 4:
            cards_needed = 4 - len(session["roll_deck"])
            session["current_hand"].extend(session["roll_deck"])
            session["roll_deck"] = session["roll_faceup"]
            session["roll_faceup"] = []
            random.shuffle(session["roll_deck"])
            for x in range(cards_needed):
                current_card = session["roll_deck"].pop()
                session["current_hand"].append(current_card)
        else:
            random.shuffle(session["roll_deck"])
            for x in range(4):
                current_card = session["roll_deck"].pop()
                session["current_hand"].append(current_card)
        session["current_deck"] = "roll"
    current_hand = session["current_hand"]
    if session["current_deck"] == "roll":
        deck_for_title = "Roller"
    else:
        deck_for_title = "Sprinter"
    previous_card = session["chosen_cards"][0]
    session.modified = True
    return render_template(
        "card_picker_2.html",
        current_hand=current_hand,
        deck_for_title=deck_for_title,
        previous_card=previous_card,
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


@app.route("/add_exhaustion/<deck>")
def add_exhaustion(deck):
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


# if __name__ == "__main__":
#     # app.run(debug=True)
#     app.run(host="0.0.0.0")
