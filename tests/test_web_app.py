"""Exercise the Flask routes with the original game and stocks code."""

from unittest.mock import Mock

import pytest

from app import stocks
from web_app import create_app


@pytest.fixture
def client(monkeypatch):
    monkeypatch.delenv("RENDER", raising=False)
    app = create_app()
    app.config.update(TESTING=True)
    return app.test_client()


@pytest.fixture
def stock_api(monkeypatch):
    monkeypatch.setenv("ALPHAVANTAGE_API_KEY", "test-only-key")
    response = Mock(text="timestamp,adjusted_close\n2026-01-05,110\n2026-01-02,100\n")
    get = Mock(return_value=response)
    monkeypatch.setattr(stocks.requests, "get", get)
    return get


@pytest.mark.parametrize(
    "path,heading",
    [
        ("/", "Welcome Home"),
        ("/home", "Welcome Home"),
        ("/about", "About Me"),
        ("/hello", "Hello, World!"),
        ("/hello?name=Harper", "Hello, Harper!"),
        ("/hello?name=%3Cb%3EHarper%3C%2Fb%3E", "Hello, &lt;b&gt;Harper&lt;/b&gt;!"),
    ],
)
def test_home_routes_use_shared_layout(client, path, heading):
    response = client.get(path)
    assert response.status_code == 200
    assert f"<h1>{heading}</h1>" in response.text
    assert 'aria-label="Main navigation"' in response.text
    assert "bootstrap.min.css" in response.text


def test_rps_form_and_results(client, monkeypatch):
    form = client.get("/rps/form")
    assert form.status_code == 200
    assert '<form method="post" action="/rps/results">' in form.text
    assert '<select class="form-select mb-3" name="user_choice"' in form.text
    for choice in ("rock", "paper", "scissors"):
        assert f'<option value="{choice}">' in form.text

    monkeypatch.setattr("web_app.routes.rps_routes.generate_random_choice", lambda: "rock")
    results = client.post("/rps/results", data={"user_choice": "paper"})
    assert results.status_code == 200
    assert "Game Result" in results.text
    assert "USER WINS" in results.text
    assert "Paper</dd>" in results.text
    assert "Rock</dd>" in results.text
    assert 'href="/rps/form">Play again' in results.text


def test_rps_rejects_invalid_submission(client):
    response = client.post("/rps/results", data={"user_choice": "lizard"}, follow_redirects=True)
    assert response.history[0].status_code == 303
    assert response.request.path == "/rps/form"
    assert "Please choose rock, paper, or scissors." in response.text


def test_stocks_form_and_dashboard(client, stock_api):
    form = client.get("/stocks/form")
    assert form.status_code == 200
    assert '<form method="post" action="/stocks/dashboard">' in form.text
    assert 'name="symbol"' in form.text

    dashboard = client.post("/stocks/dashboard", data={"symbol": " aapl "})
    assert dashboard.status_code == 200
    assert stock_api.call_args.kwargs["params"]["symbol"] == "AAPL"
    assert "Stocks Dashboard (AAPL)" in dashboard.text
    assert 'id="stock-price-chart"' in dashboard.text
    assert "Plotly.newPlot" in dashboard.text
    assert "+10.00%" in dashboard.text
    table = dashboard.text.split("<tbody>", 1)[1].split("</tbody>", 1)[0]
    assert table.count("<tr>") == 2
    assert table.index("2026-01-05") < table.index("2026-01-02")
    assert "110.00" in table
    assert "100.00" in table
    assert "test-only-key" not in dashboard.text


@pytest.mark.parametrize(
    "query,expected_symbol",
    [("", "NFLX"), ("?symbol=GOOGL", "GOOGL")],
)
def test_stocks_dashboard_get_matches_class_example(client, stock_api, query, expected_symbol):
    response = client.get(f"/stocks/dashboard{query}")
    assert response.status_code == 200
    assert f"Stocks Dashboard ({expected_symbol})" in response.text
    assert stock_api.call_args.kwargs["params"]["symbol"] == expected_symbol


def test_stocks_api_returns_price_records(client, stock_api):
    response = client.get("/api/stocks.json?symbol=MSFT")
    assert response.status_code == 200
    assert response.json == {
        "symbol": "MSFT",
        "data": [
            {"timestamp": "2026-01-05", "adjusted_close": 110.0},
            {"timestamp": "2026-01-02", "adjusted_close": 100.0},
        ],
    }


@pytest.mark.parametrize(
    "symbol,provider_request,message",
    [
        ("", False, "Enter a valid stock symbol"),
        ("???", False, "Enter a valid stock symbol"),
        ("ZZZZZZ", True, "AlphaVantage rejected the request"),
    ],
)
def test_invalid_stock_redirects_with_one_time_flash(client, stock_api, symbol, provider_request, message):
    stock_api.return_value.text = '{"Error Message":"private error detail"}'
    response = client.post("/stocks/dashboard", data={"symbol": symbol}, follow_redirects=True)
    assert response.history[0].status_code == 303
    assert response.request.path == "/stocks/form"
    assert bool(stock_api.call_count) is provider_request
    assert 'role="alert"' in response.text
    assert message in response.text
    assert "private error detail" not in response.text
    assert message not in client.get("/stocks/form").text


def test_stock_demo_uses_labeled_sample_data(client, stock_api):
    response = client.get("/stocks/dashboard?demo=1")
    assert response.status_code == 200
    assert "Stocks Dashboard (DEMO)" in response.text
    assert "fictional sample prices" in response.text
    assert "Plotly.newPlot" in response.text
    assert "108.00" in response.text
    stock_api.assert_not_called()
