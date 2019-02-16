from flask import session, request
import pathlib
import json
import random

basedir = pathlib.Path(__file__).parent.resolve()


def initialize_session():
    session["round"] = 0
    session["current_hand"] = []
    session["chosen_cards"] = []
    session["current_deck"] = ""
    session["view_played"] = False
    session["is_exhaustion_reminder"] = False
    session["options"] = {}
    session["deck_1"] = {"hand_size": 4}
    session["deck_2"] = {"hand_size": 4}


def load_player_deck(team_color):
    # load cards from json data and add team colors

    if "add_sprint_exhaustion" in request.form:
        add_sprint_exhaustion = int(request.form["add_sprint_exhaustion"])
        add_roll_exhaustion = int(request.form["add_roll_exhaustion"])

    # build sprinter deck
    session["deck_1"]["name"] = "Sprinteur"
    session["deck_1"]["recycled"] = []
    session["deck_1"]["discards"] = []
    session["deck_1"]["card-back"] = "sprinteur-back"
    session["deck_1"]["card-letter"] = "S"
    target_directory = basedir / "static" / "data_files" / "sprinter_cards.json"
    with open(target_directory) as f:
        session["deck_1"]["energy"] = json.load(f)
    for card in session["deck_1"]["energy"]:
        card.append(team_color)

    if add_sprint_exhaustion > 0:
        for card in range(add_sprint_exhaustion):
            session["deck_1"]["energy"].append([2, "S", "exhaustion-card"])

    # build roller deck
    session["deck_2"]["name"] = "Rouleur"
    session["deck_2"]["recycled"] = []
    session["deck_2"]["discards"] = []
    session["deck_2"]["card-back"] = "rouleur-back"
    session["deck_2"]["card-letter"] = "R"
    target_directory = basedir / "static" / "data_files" / "roller_cards.json"
    with open(target_directory) as f:
        session["deck_2"]["energy"] = json.load(f)
    for card in session["deck_2"]["energy"]:
        card.append(team_color)

    if add_roll_exhaustion > 0:
        for card in range(add_roll_exhaustion):
            session["deck_2"]["energy"].append([2, "R", "exhaustion-card"])


def check_for_ai_teams():
    if "muscle_team_color" in request.form:
        muscle_team_color = request.form["muscle_team_color"]
        session["is_muscle_team"] = True

        # setup muscle sprinter deck
        target_directory = basedir / "static" / "data_files" / "sprinter_cards.json"
        with open(target_directory) as f:
            session["muscle_sprint_deck"] = json.load(f)
        for card in session["muscle_sprint_deck"]:
            card.append(muscle_team_color)
        # add special muscle card
        session["muscle_sprint_deck"].append([5, "S", "muscle-card"])

        # setup muscle team roller deck
        target_directory = basedir / "static" / "data_files" / "roller_cards.json"
        with open(target_directory) as f:
            session["muscle_roll_deck"] = json.load(f)
        for card in session["muscle_roll_deck"]:
            card.append(muscle_team_color)

        random.shuffle(session["muscle_sprint_deck"])
        random.shuffle(session["muscle_roll_deck"])

        for card in range(5):
            session["muscle_sprint_deck"].append([2, "S", "exhaustion-card"])
            session["muscle_roll_deck"].append([2, "R", "exhaustion-card"])

    if "second_muscle_team_color" in request.form:
        second_muscle_team_color = request.form["second_muscle_team_color"]
        session["is_muscle_team_2"] = True

        # setup muscle sprinter deck
        target_directory = basedir / "static" / "data_files" / "sprinter_cards.json"
        with open(target_directory) as f:
            session["muscle_sprint_deck_2"] = json.load(f)
        for card in session["muscle_sprint_deck_2"]:
            card.append(second_muscle_team_color)
        # add special muscle card
        session["muscle_sprint_deck_2"].append([5, "S", "muscle-card"])

        # setup muscle team roller deck
        target_directory = basedir / "static" / "data_files" / "roller_cards.json"
        with open(target_directory) as f:
            session["muscle_roll_deck_2"] = json.load(f)
        for card in session["muscle_roll_deck_2"]:
            card.append(second_muscle_team_color)

        random.shuffle(session["muscle_sprint_deck_2"])
        random.shuffle(session["muscle_roll_deck_2"])

        for card in range(5):
            session["muscle_sprint_deck_2"].append([2, "S", "exhaustion-card"])
            session["muscle_roll_deck_2"].append([2, "R", "exhaustion-card"])

    if "peloton_team_color" in request.form:
        peloton_team_color = request.form["peloton_team_color"]
        session["is_peloton_team"] = True

        # setup peloton sprinter deck
        target_directory = basedir / "static" / "data_files" / "peloton_cards.json"
        with open(target_directory) as f:
            session["peloton_deck"] = json.load(f)
        for card in session["peloton_deck"]:
            card.append(peloton_team_color)

        random.shuffle(session["peloton_deck"])

        for card in range(5):
            session["peloton_deck"].append([2, "P", "exhaustion-card"])


def print_debug(cards_needed, hand_size, number):
    print()
    print("cards needed " + str(number) + ": " + str(cards_needed))
    print("  hand size " + str(number) + ": " + str(hand_size))
    print("current hand " + str(number) + ": ")
    print(session["current_hand"])
    print("sprint deck " + str(number) + ": ")
    print(session["sprint_deck"])
    print("sprint faceup " + str(number) + ": ")
    print(session["sprint_faceup"])


def shuffle_and_draw(deck):
    # set initial hand size
    cards_needed = session[deck]["hand_size"]

    # check to see if cards need to be recycled
    if len(session[deck]["energy"]) < session[deck]["hand_size"]:
        # set cards needed to amount less than what is in rest of deck
        cards_needed = session[deck]["hand_size"] - len(session[deck]["energy"])
        # add deck into current hand
        session["current_hand"].extend(session[deck]["energy"])
        # put recycled cards into deck
        session[deck]["energy"] = session[deck]["recycled"]
        # zero out recycled cards
        session[deck]["recycled"] = []
        # check to see if there are fewer cards in play than need for the hand
        if (
            len(session[deck]["energy"]) + len(session["current_hand"])
            < session[deck]["hand_size"]
        ):
            # set new lower number of cards needed
            cards_needed = len(session[deck]["energy"]) + len(session["current_hand"])
    random.shuffle(session[deck]["energy"])
    # add cards to hand from deck
    for x in range(cards_needed):
        current_card = session[deck]["energy"].pop()
        session["current_hand"].append(current_card)
    # if hand is empty added exhaustion card so rider can move the 2 minimum
    if session["current_hand"] == []:
        session["current_hand"].append([2, "S", "exhaustion-card"])
