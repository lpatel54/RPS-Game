# Deploying to Render

The production web service runs Flask through Gunicorn. The free instance can
serve both the game and the stocks report. Use the course AlphaVantage key with
access to `TIME_SERIES_DAILY_ADJUSTED`. Render and GitHub Actions use separate
secret settings, so enter the same key in Render even if the Actions checks pass.

## Deploy using the Render Blueprint

1. Sign in to the [Render dashboard](https://dashboard.render.com/) and choose
   **New → Blueprint**.
2. Connect GitHub and select **lpatel54/RPS-Game** and the **main** branch. If the
   repository is missing, grant Render's GitHub integration access to it.
3. Give the Blueprint a name, such as `rps-stocks`. Review the web service and
   confirm it uses the **Free** plan.
4. In the prompted environment variables, paste the real key as
   `ALPHAVANTAGE_API_KEY` without quotes. The Blueprint generates `SECRET_KEY`,
   which Flask uses for sessions and flash messages.
5. Choose **Deploy Blueprint**. Open the web service in Render and wait for its
   deploy to become live. Copy its public `.onrender.com` URL.

## Configure a web service manually

The course walkthrough also shows how to choose **New → Web Service** and
connect the GitHub repo or enter its public Git URL. Leave the root directory
empty and configure these settings.

| Render setting | Value |
| --- | --- |
| Repository | `https://github.com/lpatel54/RPS-Game` |
| Branch | `main` |
| Language | Python 3 |
| Instance type | Free |
| Build command | `python -m pip install -r requirements.txt` |
| Start command | `gunicorn --no-control-socket --bind 0.0.0.0:$PORT --workers 1 --threads 4 "web_app:create_app()"` |
| Health check path | `/` |
| `PYTHON_VERSION` | `3.12.14` |
| `ALPHAVANTAGE_API_KEY` | Your course key |
| `SECRET_KEY` | A random secret generated in Render |

Keep the key and secret in the service's **Environment** settings. If you
connected GitHub, Render can deploy new commits to the linked branch
automatically. For a service linked only by public Git URL, trigger future
deploys manually from the service's **Manual Deploy** menu.

## Verify the hosted app

Open the public URL in a private browser window. Free instances can take about
a minute to wake up after inactivity.

- Load **Home**, **About**, and **Hello**. Try `/hello?name=Harper` and expect
  `Hello, Harper!`
- Open **RPS Game**, choose a move, and click **Play**. Verify the result shows
  both moves and the outcome. **Play again** returns to the dropdown.
- Open **Stocks Report**, submit `NFLX`, and look for the interactive chart and
  a table of dated adjusted closes. Then try `AAPL` and check that the report's
  symbol and prices change. **See a sample report** opens fictional demo prices.
- Submit `???` as the symbol. The app returns to the form with a red validation
  alert. Reloading the form clears the message.
- Save the public URL and the merged web app PR link for the assignment.

If live prices fail, confirm that the deployed service has the
`ALPHAVANTAGE_API_KEY` variable and that the key has access to the adjusted
daily endpoint. After updating the key, save it and redeploy.

[Course deployment checkpoint](https://github.com/prof-rossetti/intro-to-python/blob/main/exercises/web-app-2023/deployment/DEPLOYING.md) · [Render Flask deployment guide](https://render.com/docs/deploy-flask) · [Render Blueprint guide](https://render.com/docs/infrastructure-as-code)
