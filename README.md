# my-first-app-fall-2026

## Prerequisites

Install python version 3.x (for example using Anaconda).

## Setup

some instructions here

1. Clone [the repo](https://github.com/s2t2/my-first-app-fall-2026) from GitHub, and put it somewhere (like your Desktop).
2. Navigate to the local repo from the command line (for example if on your desktop):

```sh
cd ~/Desktop/my-first-app-fall-2026
```

3. Create a new Anaconda virtual environment called "rps-env" (first time only):

```sh
conda create -n rps-env python=3.11
```

4. Activate the virtual environment as necessary (every time you come back to the project):

```sh
conda activate rps-env
```

5. Install package dependencies:

```sh
pip install -r requirements.txt
```

## Usage

some commands here to run our file(s)

Run the example script:

```sh
python app/my_script.py

# alternatively:
python -m app.my_script
```


Run the example script:

```sh
python app/rps.py

# alternatively:
python -m app.rps
```

## Testing

To run tests:

```sh
pytest
```

## Run the stocks dashboard

### Try it without an API key

```sh
python -m app.stocks --demo --open
```

This uses five **fictional sample prices**, labeled DEMO. It verifies the local
dashboard flow; it does not fetch or represent market data.

### Configure live stock data securely

Obtain an AlphaVantage key from your professor's course page, or from
[AlphaVantage](https://www.alphavantage.co/support/#api-key). The class example
uses `TIME_SERIES_DAILY_ADJUSTED`, which may require a premium plan. Use a key
with access to that endpoint. A free key may return an access or quota message.

Copy `.env.example` to `.env` in the repository root:

macOS / Linux:

```sh
cp .env.example .env
```

Windows PowerShell:

```powershell
Copy-Item .env.example .env
```

Edit `.env` locally:

```dotenv
ALPHAVANTAGE_API_KEY=replace_with_your_real_key
```

`.env` is ignored by Git; `.env.example` contains no key. Never put a real key in
source files, tests, commit messages, screenshots, or this README. Environment
variables already set in the terminal take precedence over `.env`. The app reads
the `.env` in this repository, regardless of the shell's working directory.

Fetch prices and open the local dashboard:

```sh
python -m app.stocks --symbol NFLX --open
```

Or run `python -m app.stocks` and enter a ticker when prompted (blank defaults to
NFLX). Quotes are fetched only when you run the command; the chart does not refresh
automatically. By default, the dashboard is saved at `work/stocks-dashboard.html`.
You can open that file manually or choose another output path:

```sh
python -m app.stocks --symbol GOOGL --output work/googl.html
```

The standalone HTML includes Plotly, so viewing a saved chart needs no internet
connection. Hover to inspect prices, drag to zoom, and use the date range slider.
Dates and adjusted prices are sorted chronologically. Prices remain in the
instrument's quote currency; the app does not perform currency conversion. Period
change compares the first and last displayed adjusted closes. AlphaVantage may
return about 100 trading days for a compact response; the app displays the valid
data returned, without inventing missing days. These are historical daily prices.

Missing credentials, invalid symbols, API limits, network failures, and malformed
data produce readable errors. Error messages omit request URLs and provider error
contents to keep the API key out of terminal output.

## Run tests

```sh
python -m pytest -q
```

The tests directly call application code. They cover all nine possible outcomes,
input normalization, invalid input for either player, cancellation, a round with
a controlled computer choice, both launch commands, and safe imports without prompts.
Stocks tests cover the actual fetch function with mocked HTTP responses, request
parameters, environment loading, CSV validation, price ordering, rate limits,
network and HTTP errors, credential redaction, chart values, HTML output, and CLI
behavior. The demo path writes a real standalone HTML chart during tests.

Tests do not need network access, credentials, or an API key. CI uses these same
tests, so it needs no repository secret. Mocked responses make automated tests
repeatable; a successful live fetch still depends on a valid key, endpoint access,
and AlphaVantage availability. To check live access, run the live command above
locally and confirm a dated chart is produced. Live access is not asserted by the
offline tests.

## Code structure

```text
app/
  __init__.py          Python package marker
  rps.py               Reusable game functions and CLI entry point
  stocks.py            Fetching, validation, dashboard, and CLI
tests/
  test_rps.py          Unit and command-line integration tests
  test_stocks.py       Stocks unit and local HTML integration tests
.github/workflows/
  tests.yml            GitHub Actions test workflow
requirements.txt       Pinned test dependency
pytest.ini             Test discovery and import configuration
.env.example           Blank local API configuration template
```

`normalize_choice()` handles validation in one place. `determine_winner(u, c)`
returns `USER WINS`, `COMPUTER WINS`, or `TIE GAME`. A single rule mapping avoids
duplicating nine conditional branches. `main()` handles input, random selection,
and output. The main guard makes functions safe to import into other programs.
The stocks module similarly separates `normalize_symbol()`, `parse_stocks_csv()`,
`fetch_stocks_csv()`, `build_dashboard()`, and `main()` so the data and chart logic
can be reused and tested independently.

## Version control and pull requests

Create your own GitHub repository; do not fork the class example. To contribute:

```sh
git switch main
git pull --ff-only
git switch -c improve-game
# Edit code and run python -m pytest -q.
git add app tests README.md requirements.txt .github pytest.ini .gitignore .env.example
git commit -m "Describe the improvement"
git push -u origin improve-game
```

Open a pull request into `main` from GitHub's **Pull requests** tab. The `Tests`
workflow runs automatically on pull requests and pushes to `main`. Inspect the
checks, fix any failures, and merge only after the checks pass. After merging,
check the Actions run for `main` as well. The Actions tab is the source of truth
for hosted CI status; passing local tests alone does not establish passing CI.

The professor's Fall 2026 update waives the PR requirement for this assignment,
but a merged PR provides useful workflow evidence. Only code on `main` will be
evaluated. This README describes the workflow; actual commits, PRs, and Actions
runs provide the evidence.

## Assignment scope and references

This project implements the required rock paper scissors app and the optional
AlphaVantage stocks dashboard. The original repository is owned by `lpatel54`.
Only live stock fetching requires a secret; the game, demo, and tests do not.

Class reference: [Code Cleanup and Testing](https://github.com/s2t2/my-first-app-fall-2026/pull/1).
The project follows its `app.rps.determine_winner(u, c)` interface and outcome
labels, with simplified rules and additional validation and tests.
Stocks reference: [Stocks Dashboard PR #5](https://github.com/s2t2/my-first-repo-fall-2025/pull/5).
The bonus follows its daily-adjusted CSV endpoint and adjusted-close chart, with
separate parsing and chart functions and offline tests.

When finished, run `deactivate` to leave a `.venv` environment, or
`conda deactivate` to leave an Anaconda environment.
=======
# My First Repo!

Learning and practicing version control!

## Setup

Clone the repo to download it from GitHub. Perhaps onto the Desktop.

Navigate to the repo using the command line.

```sh
cd ~/Desktop/my-first-repo-fall-2025
```

Create a virtual environment:

```sh
conda create -n my-first-env-fall-2025 python=3.11
```

Activate the virtual environment:

```sh
conda activate my-first-env-fall-2025
```

Install package dependencies:

```sh
pip install -r requirements.txt
```

## Configuration

The stocks functionality requires an AlphaVantage API key. Obtain a premium AlphaVantage API Key (using the [form](https://www.alphavantage.co/support/#api-key) or shared by the prof).

Create a local ".env" file and store your environment variable in there:

```sh
# this is the ".env" file...

ALPHAVANTAGE_API_KEY="______________"

# also tell flask where our web app is defined:
FLASK_APP=web_app
```

## Usage

Example script:

```sh
python app/my_script.py
```

Game of rock, paper, scissors:

```sh
python app/rps.py

# alternative "modular style" command:
python -m app.rps
```

Stocks dashboard:

```sh
python -m app.stocks
```

### Web App

Run the web app (then view in the browser at http://localhost:5000/):

```sh
# if we have the FLASK_APP=web_app env var in the ".env" file:
flask run

# Mac OS:
FLASK_APP=web_app flask run

# Windows OS:
# ... if `export` doesn't work for you, try `set` instead
# ... or set FLASK_APP variable via ".env" file
export FLASK_APP=web_app
flask run
```

## Testing

Run tests:

```sh
pytest
```
>>>>>>> Stashed changes
