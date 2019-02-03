from flask import (
    Flask,
    Blueprint,
    session,
    render_template,
    url_for,
    redirect,
    request,
    flash,
)
import random
import json
import pathlib
from functions import *

breakaway = Blueprint("breakaway", __name__, template_folder="breakaway")


@breakaway.route("/breakaway_picker_1/<chosen_breakaway_deck>", methods=["POST", "GET"])
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
    form_destination = "breakaway.hidden_first_breakaway"
    return render_template(
        # "breakaway/breakaway_picker_1.html",
        "card_picker.html",
        current_hand=current_hand,
        deck_for_title=deck_for_title,
        form_destination=form_destination,
    )


@breakaway.route("/hidden_first_breakaway", methods=["POST", "GET"])
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
    return render_template(
        "breakaway/breakaway_hidden_1.html", current_deck=current_deck
    )


@breakaway.route("/revealed_breakaway_card_1")
def revealed_breakaway_card_1():
    chosen_cards = session["chosen_cards"]
    return render_template(
        "breakaway/breakaway_revealed_card_1.html", chosen_cards=chosen_cards
    )


@breakaway.route("/breakaway_picker_2")
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
    form_destination = "breakaway.breakaway_hidden_2"
    return render_template(
        "card_picker.html",
        current_hand=current_hand,
        deck_for_title=deck_for_title,
        form_destination=form_destination,
    )


@breakaway.route("/breakaway_hidden_2", methods=["POST", "GET"])
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
        "breakaway/breakaway_hidden_2.html",
        revealed_card=revealed_card,
        hidden_card=hidden_card,
        current_deck=current_deck,
    )


@breakaway.route("/breakaway_revealed_card_2")
def breakaway_revealed_card_2():

    # replace chosen cards with exhaustion
    chosen_card_0 = session["chosen_cards"][0]
    chosen_card_1 = session["chosen_cards"][1]
    session.modified = True
    return render_template(
        "/breakaway/breakaway_revealed_card_2.html",
        chosen_card_0=chosen_card_0,
        chosen_card_1=chosen_card_1,
    )


@breakaway.route("/breakaway_winner/<place>")
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
    return redirect(url_for("breakaway.breakaway_revealed_card_2"))


@breakaway.route("/breakaway_final_check")
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
