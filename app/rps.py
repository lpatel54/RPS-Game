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


def generate_random_choice() -> str:
    """Choose the computer's move for either app interface."""
    return random.choice(VALID_OPTIONS)


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

    computer_choice = generate_random_choice()
    print("USER:", user_choice)
    print("COMP:", computer_choice)
    print(determine_winner(user_choice, computer_choice))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
