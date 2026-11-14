<<<<<<< Updated upstream
"""Play a round of rock paper scissors from the command line."""

import random

VALID_OPTIONS = ("rock", "paper", "scissors")
BEATS = {"rock": "scissors", "paper": "rock", "scissors": "paper"}


def normalize_choice(choice: str) -> str:
    """Normalize a player's input, raising ValueError for invalid choices."""
    choice = choice.strip().lower()
    if choice not in VALID_OPTIONS:
        raise ValueError("Please choose rock, paper, or scissors.")
    return choice


def determine_winner(u: str, c: str) -> str:
    """Return the outcome from the user's perspective; validate both choices."""
    user_choice = normalize_choice(u)
    computer_choice = normalize_choice(c)
    if user_choice == computer_choice:
        return "TIE GAME"
    if BEATS[user_choice] == computer_choice:
        return "USER WINS"
    return "COMPUTER WINS"


def main() -> int:
    """Play one round and return a process exit status."""
    print("Welcome to Rock Paper Scissors!")
    try:
        user_choice = normalize_choice(
            input("Please choose rock, paper, or scissors: ")
        )
    except ValueError as error:
        print(error)
        return 1
    except (EOFError, KeyboardInterrupt):
        print("\nGame cancelled.")
        return 0

    computer_choice = random.choice(VALID_OPTIONS)
    print("USER:", user_choice)
    print("COMP:", computer_choice)
    print(determine_winner(user_choice, computer_choice))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
=======
import random


VALID_OPTIONS = ["rock", "paper", "scissors"]


def determine_winner(u, c):
    if u == "rock" and c == "rock":
        return "TIE GAME"
    elif u == "rock" and c == "paper":
        return "COMPUTER WINS"
    elif u == "rock" and c == "scissors":
        return "USER WINS"
    elif u == "paper" and c == "rock":
        return "USER WINS"
    elif u == "paper" and c == "paper":
        return "TIE GAME"
    elif u == "paper" and c == "scissors":
        return "COMPUTER WINS"
    elif u == "scissors" and c == "rock":
        return "COMPUTER WINS"
    elif u == "scissors" and c == "paper":
        return "USER WINS"
    elif u == "scissors" and c == "scissors":
        return "TIE GAME"


if __name__ == "__main__":
    # ONLY RUN THE CODE BELOW
    # IF WE ARE RUNNING THIS SCRIPT FROM THE COMMAND LINE
    # BUT NOT IF WE'RE TRYING TO JUST IMPORT SOME STUFF FROM THIS FILE

    # ASK USER FOR AN INPUT (R/P/S)

    user_choice = input("Please choose one of 'rock', 'paper', or 'scissors': ")
    print("USER:", user_choice)

    # VALIDATIONS

    if user_choice not in VALID_OPTIONS:
        print("OOPS INVALID INPUT, PLEASE TRY AGAIN")
        # exit()
        quit()

    # GENERATE RANDOM COMPUTER CHOICE

    computer_choice = random.choice(VALID_OPTIONS)
    print("COMP:", computer_choice)

    # DETERMINE THE WINNER

    result = determine_winner(user_choice, computer_choice)
    print(result)
>>>>>>> Stashed changes
