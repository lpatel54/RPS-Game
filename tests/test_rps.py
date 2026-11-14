"""Tests exercise the application functions and command-line entry points."""

import subprocess
import sys
from pathlib import Path

import pytest

from app import rps

ROOT = Path(__file__).resolve().parents[1]


@pytest.mark.parametrize(
    "user,computer,expected",
    [
        ("rock", "rock", "TIE GAME"),
        ("rock", "paper", "COMPUTER WINS"),
        ("rock", "scissors", "USER WINS"),
        ("paper", "rock", "USER WINS"),
        ("paper", "paper", "TIE GAME"),
        ("paper", "scissors", "COMPUTER WINS"),
        ("scissors", "rock", "COMPUTER WINS"),
        ("scissors", "paper", "USER WINS"),
        ("scissors", "scissors", "TIE GAME"),
    ],
)
def test_all_outcomes(user, computer, expected):
    assert rps.determine_winner(u=user, c=computer) == expected


@pytest.mark.parametrize("choice", ["rock", "paper", "scissors"])
def test_normalizes_case_and_whitespace(choice):
    assert rps.normalize_choice(f"  {choice.upper()}  ") == choice


@pytest.mark.parametrize("invalid", ["", "   ", "lizard", "r"])
@pytest.mark.parametrize("position", ["user", "computer"])
def test_rejects_invalid_choices(invalid, position):
    with pytest.raises(ValueError, match="Please choose"):
        rps.determine_winner(
            invalid if position == "user" else "rock",
            invalid if position == "computer" else "rock",
        )


def test_winner_normalizes_both_inputs():
    assert rps.determine_winner(" PAPER ", " Rock ") == "USER WINS"


def test_main_plays_round(monkeypatch, capsys):
    monkeypatch.setattr("builtins.input", lambda prompt: " PAPER ")

    def choose(options):
        assert options == rps.VALID_OPTIONS
        return "rock"

    monkeypatch.setattr(rps.random, "choice", choose)
    assert rps.main() == 0
    output = capsys.readouterr().out
    assert "USER: paper" in output
    assert "COMP: rock" in output
    assert "USER WINS" in output


def test_main_rejects_input_before_computer_choice(monkeypatch, capsys):
    monkeypatch.setattr("builtins.input", lambda prompt: "lizard")

    def unexpected_choice(options):
        pytest.fail("Invalid input should stop the round")

    monkeypatch.setattr(rps.random, "choice", unexpected_choice)
    assert rps.main() == 1
    assert "Please choose rock, paper, or scissors." in capsys.readouterr().out


@pytest.mark.parametrize("exception", [EOFError, KeyboardInterrupt])
def test_main_handles_cancellation(monkeypatch, capsys, exception):
    def cancel(prompt):
        raise exception

    monkeypatch.setattr("builtins.input", cancel)
    assert rps.main() == 0
    assert "Game cancelled." in capsys.readouterr().out


@pytest.mark.parametrize("entry", [["-m", "app.rps"], ["app/rps.py"]])
def test_command_line_entry_points(entry):
    result = subprocess.run(
        [sys.executable, *entry], input="rock\n", text=True,
        capture_output=True, cwd=ROOT, timeout=10,
    )
    assert result.returncode == 0, result.stderr
    assert "USER: rock" in result.stdout
    assert "COMP:" in result.stdout
    assert any(outcome in result.stdout for outcome in (
        "TIE GAME", "USER WINS", "COMPUTER WINS"
    ))


def test_import_has_no_interactive_side_effects():
    result = subprocess.run(
        [sys.executable, "-c", "import app.rps"], input="", text=True,
        capture_output=True, cwd=ROOT, timeout=10,
    )
    assert result.returncode == 0, result.stderr
    assert result.stdout == ""
