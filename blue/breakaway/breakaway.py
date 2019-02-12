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

    shuffle_and_draw(chosen_breakaway_deck)
    current_hand = session["current_hand"]
    session["current_deck"] = chosen_breakaway_deck

    deck_for_title = session[chosen_breakaway_deck]["name"]
    session.modified = True
    form_destination = "breakaway.hidden_first_breakaway"
    return render_template(
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
    current_deck = session["current_deck"]
    session[current_deck]["recycled"].extend(session["current_hand"])
    session["current_hand"] = []

    breakaway_card_backs = session[current_deck]["card-back"]
    central_letter = session[current_deck]["card-letter"]

    session.modified = True
    return render_template(
        "breakaway/breakaway_hidden_1.html",
        current_deck=current_deck,
        breakaway_card_backs=breakaway_card_backs,
        central_letter=central_letter,
    )


@breakaway.route("/revealed_breakaway_card_1")
def revealed_breakaway_card_1():
    chosen_cards = session["chosen_cards"]

    return render_template(
        "breakaway/breakaway_revealed_card_1.html", chosen_cards=chosen_cards
    )


@breakaway.route("/breakaway_picker_2")
def breakaway_picker_2():
    chosen_breakaway_deck = session["current_deck"]
    shuffle_and_draw(chosen_breakaway_deck)

    current_hand = session["current_hand"]

    deck_for_title = session[chosen_breakaway_deck]["name"]
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

    current_deck = session["current_deck"]

    # add rest of hand to recylced cards, then recylce cards to energy deck
    session[current_deck]["recycled"].extend(session["current_hand"])
    session["current_hand"] = []
    session[current_deck]["energy"].extend(session[current_deck]["recycled"])
    session[current_deck]["recycled"] = []

    chosen_cards = session["chosen_cards"]

    breakaway_card_backs = session[current_deck]["card-back"]
    central_letter = session[current_deck]["card-letter"]

    session.modified = True
    return render_template(
        "breakaway/breakaway_hidden_2.html",
        chosen_cards=chosen_cards,
        breakaway_card_backs=breakaway_card_backs,
        central_letter=central_letter,
    )


@breakaway.route("/breakaway_revealed_card_2")
def breakaway_revealed_card_2():

    # replace chosen cards with exhaustion
    chosen_cards = session["chosen_cards"]
    session.modified = True
    return render_template(
        "/breakaway/breakaway_revealed_card_2.html", chosen_cards=chosen_cards
    )


@breakaway.route("/breakaway_winner", methods=["Post"])
def breakaway_winner():
    place = request.form["place"]
    place = place[-1]
    place = int(place)
    print(place)
    current_deck = session["current_deck"]

    session[current_deck]["energy"].append([2, "S", "exhaustion-card"])
    session[current_deck]["discards"].append(session["chosen_cards"].pop(place))
    session["chosen_cards"].insert(place, "place holder")

    session.modified = True
    return ("", 204)


@breakaway.route("/breakaway_final_check")
def breakaway_final_check():
    current_deck = session["current_deck"]
    session[current_deck]["energy"].extend(session["chosen_cards"])
    session.modified = True
    return redirect(url_for("choose_deck"))
