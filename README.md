# RPS Game and Stocks Dashboard

A Flask web app and Python CLI for the Fall 2026 Quality Control and Web App exercises.
Play one round against the computer: rock beats scissors, scissors beats paper,
and paper beats rock. Matching choices tie. The stocks dashboard fetches daily
adjusted stock prices from AlphaVantage and saves an interactive HTML chart with
the latest adjusted close and the change over the displayed period.

## Prerequisites

- Python 3.11 or newer (CI checks Python 3.11, 3.12, and 3.13).
- Git to clone the repository and save changes.
- A terminal such as Terminal, PowerShell, or the VS Code terminal.

## Download

Clone [your repository](https://github.com/lpatel54/RPS-Game):

```sh
git clone https://github.com/lpatel54/RPS-Game.git
cd RPS-Game
```

If you downloaded a ZIP instead, extract it and open a terminal in the extracted
folder. All following commands run from the folder containing this README.

## Create and activate a virtual environment

Create the environment once:

```sh
python -m venv .venv
```

On macOS or Linux, use `python3` instead of `python` if needed. On Windows,
`py -3` can also be used to create the environment.

Activate it every time you open a new terminal:

macOS / Linux:

```sh
source .venv/bin/activate
```

Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

Windows Command Prompt:

```bat
.venv\Scripts\activate.bat
```

If PowerShell blocks activation, use Command Prompt, or run the environment's
Python directly: `.venv\Scripts\python.exe -m pip install -r requirements.txt`
and `.venv\Scripts\python.exe -m app.rps`.

### Anaconda alternative

Use this instead of the `.venv` steps if following the class's Anaconda setup:

```sh
conda create -n rps-env python=3.11
conda activate rps-env
```

## Install packages

After activating either environment:

```sh
python -m pip install -r requirements.txt
```

`requirements.txt` lists pinned versions of pandas (data preparation), Plotly
(interactive charts), requests (API access), python-dotenv (local configuration),
pytest (tests), Flask (web routes), and Gunicorn (production server). The game itself uses Python's standard library. Virtual
environments and caches are excluded from Git.

## Run the web app

From the repository root, configure the AlphaVantage key in `.env` for live
stocks, then run the class's command on macOS or Linux:

```sh
FLASK_APP=web_app flask run
```

This equivalent command also works in Windows PowerShell or Command Prompt:

```sh
python -m flask --app web_app run
```

Open [localhost:5000](http://localhost:5000/) and press Ctrl+C in the terminal
to stop the local server. Use **RPS Game** to play a round, or **Stocks Report**
to enter a ticker and see its dated price table and interactive chart. The RPS
game and the clearly labeled sample stocks report work without an API key.
**Hello** accepts a name at `/hello?name=Harper`, and the checkpoint's stock JSON
route is available at `/api/stocks.json?symbol=NFLX` with a configured API key.

See [DEPLOYING.md](DEPLOYING.md) for Render setup and verification.

## Run the game

```sh
python -m app.rps
```

Alternatively:

```sh
python app/rps.py
```

Enter `rock`, `paper`, or `scissors`. Capitalization and surrounding spaces are
accepted. For example, choosing `paper` against the computer's `rock` prints
`USER WINS`. The computer chooses randomly each round. Run the command again to
play another round. Invalid choices print a helpful message and exit with status
1; Ctrl+C or end-of-input cancels gracefully.

The additional in-class practice script can be run with:

```sh
python -m app.my_script
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
Flask tests cover home routes, dropdown submission and results, stock form and
dashboard rendering, provider errors, flash redirects, and the JSON route.

The default test run uses mocked HTTP responses and needs no network or API key.
It skips the opt-in live integration test. GitHub Actions runs the offline tests
on three Python versions, then runs one separate live check using the repository
secret named `AlphaVantage_Secret`. The workflow maps that secret to the app's
`ALPHAVANTAGE_API_KEY` environment variable only for the live test step. The key
is never written into source files or uploaded with the generated chart.

The live check calls the actual `fetch_stocks_csv()` function, requires at least
100 daily adjusted prices, and generates the actual dashboard. It fails if the
secret is missing, invalid, rate-limited, or lacks endpoint access. Fork PRs skip
the secret-dependent job. Same-repository PRs and pushes to `main` run it.

To run the same live check locally, configure `.env` as described above, then:

macOS / Linux:

```sh
RUN_LIVE_STOCKS=1 python -m pytest -q integration/test_stocks_live.py -m live --tb=short
```

Windows PowerShell:

```powershell
$env:RUN_LIVE_STOCKS = "1"
python -m pytest -q integration/test_stocks_live.py -m live --tb=short
Remove-Item Env:RUN_LIVE_STOCKS
```

A GitHub repository secret is available to Actions only; it does not create a
local `.env` file. Local live fetching still needs the key in `.env` under the
name `ALPHAVANTAGE_API_KEY`.

Pytest discovers `tests/` (the detailed game and dashboard tests), `test/` (the
additional in-class examples), and `integration/` (the opt-in live check).

## Code structure

```text
app/
  __init__.py          Python package marker
  my_script.py         Additional in-class practice script
  rps.py               Reusable game functions and CLI entry point
  stocks.py            Fetching, validation, dashboard, and CLI
web_app/              Flask app factory, route blueprints, and Bootstrap templates
tests/
  test_web_app.py      Flask route and form tests
  test_rps.py          Unit and command-line integration tests
  test_stocks.py       Stocks unit and local HTML integration tests
test/
  rps_test.py          Additional in-class game tests
integration/
  test_stocks_live.py  Opt-in real API and dashboard check
.github/workflows/
  tests.yml            GitHub Actions test workflow
render.yaml            Render Blueprint
DEPLOYING.md           Production deployment and smoke-test guide
requirements.txt       Pinned application and test dependencies
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
git add <files-you-changed>
git commit -m "Describe the improvement"
git push -u origin improve-game
```

Open a pull request into `main` from GitHub's **Pull requests** tab. The `Tests`
workflow runs automatically on pull requests and pushes to `main`. Inspect the
checks, fix any failures, and merge only after the checks pass. After merging,
check the Actions run for `main` as well. The Actions tab is the source of truth
for hosted CI status; passing local tests alone does not establish passing CI.

The Web App exercise requires at least one merged PR containing web app work.
Verify the merged code on `main` before deploying it.

## Course references

- [Professor's Web App exercise](https://github.com/prof-rossetti/intro-to-python/tree/main/exercises/web-app-2023) for routing, layouts, dashboards, Flask tests, and Render.
- [Fall 2026 in-class Web App PR](https://github.com/s2t2/my-first-app-fall-2026/pull/2) and [Fall 2025 routing and RPS PR](https://github.com/s2t2/my-first-repo-fall-2025/pull/7) for the Flask factory, blueprints, and HTML forms.
- [Fall 2025 Bootstrap PR](https://github.com/s2t2/my-first-repo-fall-2025/pull/8) for the shared Bootstrap layout.
- [Quality Control example](https://github.com/s2t2/my-first-app-fall-2026/pull/1) and [Stocks Dashboard PR](https://github.com/s2t2/my-first-repo-fall-2025/pull/5) for the original game, tests, and adjusted-price data.

When finished, run `deactivate` to leave a `.venv` environment, or
`conda deactivate` to leave an Anaconda environment.
