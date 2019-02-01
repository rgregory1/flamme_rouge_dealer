from flask import session, request
import pathlib
import json
import random

basedir = pathlib.Path(__file__).parent.resolve()


def initialize_session():
    session["round"] = 0
    session["current_hand"] = []
    session["chosen_cards"] = []
    session["sprint_discards"] = []
    session["sprint_faceup"] = []
    session["roll_discards"] = []
    session["roll_faceup"] = []
    session["current_deck"] = ""
    session["is_sprint_exaust"] = False
    session["is_roll_exaust"] = False
    session["view_played"] = False
    session["is_exhaustion_reminder"] = False
    session["hand_size"] = 4


def load_player_deck(team_color):
    # load cards from json data and add team colors

    if "add_sprint_exhaustion" in request.form:
        add_sprint_exhaustion = int(request.form["add_sprint_exhaustion"])
        add_roll_exhaustion = int(request.form["add_roll_exhaustion"])

    target_directory = basedir / "static" / "data_files" / "sprinter_cards.json"
    with open(target_directory) as f:
        session["sprint_deck"] = json.load(f)
    for card in session["sprint_deck"]:
        card.append(team_color)

    if add_sprint_exhaustion > 0:
        for card in range(add_sprint_exhaustion):
            session["sprint_deck"].append([2, "S", "exhaustion-card"])

    target_directory = basedir / "static" / "data_files" / "roller_cards.json"
    with open(target_directory) as f:
        session["roll_deck"] = json.load(f)
    for card in session["roll_deck"]:
        card.append(team_color)

    if add_roll_exhaustion > 0:
        for card in range(add_roll_exhaustion):
            session["roll_deck"].append([2, "R", "exhaustion-card"])


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


def shuffle_and_draw(deck, hand_size):
    # set initial hand size
    cards_needed = hand_size
    if deck == "sprint":
        # check to see if cards need to be recycled
        if len(session["sprint_deck"]) < hand_size:
            # set cards needed to amount less than what is in rest of deck
            cards_needed = hand_size - len(session["sprint_deck"])
            # add deck into current hand
            session["current_hand"].extend(session["sprint_deck"])
            # put recycled cards into deck
            session["sprint_deck"] = session["sprint_faceup"]
            # zero out recycled cards
            session["sprint_faceup"] = []
            # check to see if there are fewer cards in play than need for the hand
            if len(session["sprint_deck"]) + len(session["current_hand"]) < hand_size:
                # set new lower number of cards needed
                cards_needed = len(session["sprint_deck"]) + len(
                    session["current_hand"]
                )
        random.shuffle(session["sprint_deck"])
        # add cards to hand from deck
        for x in range(cards_needed):
            current_card = session["sprint_deck"].pop()
            session["current_hand"].append(current_card)
        # if hand is empty added exhaustion card so rider can move the 2 minimum
        if session["current_hand"] == []:
            session["current_hand"].append([2, "S", "exhaustion-card"])

    else:
        # check to see if cards need to be recycled
        if len(session["roll_deck"]) < hand_size:
            # set cards needed to amount less than what is in rest of deck
            cards_needed = hand_size - len(session["roll_deck"])
            # add deck into current hand
            session["current_hand"].extend(session["roll_deck"])
            # put recycled cards into deck
            session["roll_deck"] = session["roll_faceup"]
            # zero out recycled cards
            session["roll_faceup"] = []
            # check to see if there are fewer cards in play than need for the hand
            if len(session["roll_deck"]) + len(session["current_hand"]) < hand_size:
                # set new lower number of cards needed
                cards_needed = len(session["roll_deck"]) + len(session["current_hand"])
        random.shuffle(session["roll_deck"])
        # add cards to hand from deck
        for x in range(cards_needed):
            current_card = session["roll_deck"].pop()
            session["current_hand"].append(current_card)
        # if hand is empty added exhaustion card so rider can move the 2 minimum
        if session["current_hand"] == []:
            session["current_hand"].append([2, "S", "exhaustion-card"])
