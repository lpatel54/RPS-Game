"""Play the original rock paper scissors game from a web form."""

from flask import Blueprint, flash, redirect, render_template, request, url_for

from app.rps import VALID_OPTIONS, determine_winner, generate_random_choice, normalize_choice

rps_routes = Blueprint("rps_routes", __name__, url_prefix="/rps")


@rps_routes.get("/form")
def form():
    return render_template("rps_form.html", choices=VALID_OPTIONS)


@rps_routes.post("/results")
def results():
    try:
        user_choice = normalize_choice(request.form.get("user_choice", ""))
    except ValueError as error:
        flash(str(error), "danger")
        return redirect(url_for("rps_routes.form"), code=303)

    computer_choice = generate_random_choice()
    return render_template(
        "rps_results.html",
        user_choice=user_choice,
        computer_choice=computer_choice,
        outcome=determine_winner(user_choice, computer_choice),
    )
