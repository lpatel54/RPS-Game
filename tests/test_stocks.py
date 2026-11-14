"""Exercise stock parsing, HTTP handling, chart data, and the local CLI."""

import subprocess
import sys
from pathlib import Path
from unittest.mock import Mock

import pandas as pd
import pytest
import requests

from app import stocks

CSV = "timestamp,open,adjusted_close\n2026-01-06,119,120\n2026-01-02,99,100\n2026-01-05,109,110\n"


@pytest.fixture
def http(monkeypatch):
    response = Mock(text=CSV)
    response.raise_for_status.return_value = None
    get = Mock(return_value=response)
    monkeypatch.setattr(stocks.requests, "get", get)
    return get


@pytest.mark.parametrize("raw,expected", [(" nflx ", "NFLX"), ("brk.b", "BRK.B"), ("BRK-B", "BRK-B")])
def test_normalize_symbol(raw, expected):
    assert stocks.normalize_symbol(raw) == expected


@pytest.mark.parametrize("symbol", ["", "  ", "../.env", "<script>", "A&B", "A" * 21])
def test_invalid_symbols(symbol):
    with pytest.raises(stocks.StocksError, match="valid stock symbol"):
        stocks.normalize_symbol(symbol)


def test_parses_numeric_prices_and_sorts_dates():
    frame = stocks.parse_stocks_csv(CSV)
    assert isinstance(frame, pd.DataFrame)
    assert list(frame["adjusted_close"]) == [100, 110, 120]
    assert list(frame["timestamp"].dt.strftime("%Y-%m-%d")) == ["2026-01-02", "2026-01-05", "2026-01-06"]
    assert "open" in frame.columns


@pytest.mark.parametrize("csv", [
    "", "timestamp,adjusted_close\n", "timestamp,close\n2026-01-02,100\n",
    "timestamp,adjusted_close\ninvalid,100\n", "timestamp,adjusted_close\n,100\n",
    "timestamp,adjusted_close\n2026-01-02,abc\n",
    "timestamp,adjusted_close\n2026-01-02,\n",
    "timestamp,adjusted_close\n2026-01-02,0\n",
    "timestamp,adjusted_close\n2026-01-02,-1\n",
    "timestamp,adjusted_close\n2026-01-02,inf\n",
    "timestamp,adjusted_close\n2026-01-02,100\n2026-01-02,101\n",
])
def test_rejects_bad_csv(csv):
    with pytest.raises(stocks.StocksError, match="empty or invalid"):
        stocks.parse_stocks_csv(csv)


@pytest.mark.parametrize("payload,match", [
    ('{"Note":"secret-key"}', "rate limit"),
    ('{"Information":"secret-key"}', "premium"),
    ('{"Error Message":"secret-key"}', "rejected"),
])
def test_api_errors_are_helpful_without_echoing_payload(payload, match):
    with pytest.raises(stocks.StocksError, match=match) as error:
        stocks.parse_stocks_csv(payload)
    assert "secret-key" not in str(error.value)


def test_fetch_calls_expected_endpoint_and_parses_data(http):
    frame = stocks.fetch_stocks_csv(" googl ", api_key="test-only-key")
    http.assert_called_once_with(stocks.API_URL, params={
        "function": "TIME_SERIES_DAILY_ADJUSTED", "symbol": "GOOGL",
        "apikey": "test-only-key", "datatype": "csv", "outputsize": "compact",
    }, timeout=20)
    assert frame["adjusted_close"].tolist() == [100, 110, 120]


def test_fetch_loads_local_environment_without_override(monkeypatch, http):
    load = Mock()
    monkeypatch.setattr(stocks, "load_dotenv", load)
    monkeypatch.setenv("ALPHAVANTAGE_API_KEY", "test-only-env-key")
    stocks.fetch_stocks_csv()
    load.assert_called_once_with(stocks.PROJECT_ROOT / ".env", override=False)
    assert http.call_args.kwargs["params"]["apikey"] == "test-only-env-key"


@pytest.mark.parametrize("api_key", ["", "  "])
def test_missing_key_stops_before_http(http, api_key):
    with pytest.raises(stocks.StocksError, match="ALPHAVANTAGE_API_KEY"):
        stocks.fetch_stocks_csv(api_key=api_key)
    http.assert_not_called()


@pytest.mark.parametrize("failure", [requests.Timeout, requests.ConnectionError, requests.HTTPError])
def test_request_errors_do_not_expose_api_key(http, failure):
    http.side_effect = failure("https://example.test/?apikey=secret-key")
    with pytest.raises(stocks.StocksError, match="Unable to fetch") as error:
        stocks.fetch_stocks_csv(api_key="secret-key")
    assert "secret-key" not in str(error.value)


def test_http_error_checked_before_parsing(http):
    http.return_value.raise_for_status.side_effect = requests.HTTPError("apikey=secret-key")
    with pytest.raises(stocks.StocksError, match="Unable to fetch") as error:
        stocks.fetch_stocks_csv(api_key="secret-key")
    assert "secret-key" not in str(error.value)


def test_fetch_validates_provider_response(http):
    http.return_value.text = '{"Note":"request limit"}'
    with pytest.raises(stocks.StocksError, match="rate limit"):
        stocks.fetch_stocks_csv(api_key="test-only-key")


def test_dashboard_uses_adjusted_prices_and_correct_summary():
    figure = stocks.build_dashboard(stocks.parse_stocks_csv(CSV), "nflx")
    assert figure.data[0].value == 120
    assert figure.data[1].value == pytest.approx(20)
    assert list(figure.data[2].y) == [100, 110, 120]
    assert "NFLX" in figure.layout.title.text
    assert "2026-01-02 to 2026-01-06" in figure.layout.title.text


def test_demo_saves_standalone_html_without_network(monkeypatch, tmp_path, http, capsys):
    output = tmp_path / "nested" / "demo.html"
    assert stocks.main(["--demo", "--output", str(output)]) == 0
    html = output.read_text()
    assert "Stock Prices (DEMO)" in html
    assert "plotly.js" in html
    assert "fictional sample prices" in capsys.readouterr().out
    http.assert_not_called()


def test_cli_fetches_requested_symbol(monkeypatch, tmp_path, capsys):
    fetch = Mock(return_value=stocks.parse_stocks_csv(CSV))
    monkeypatch.setattr(stocks, "fetch_stocks_csv", fetch)
    assert stocks.main(["--symbol", " googl ", "--output", str(tmp_path / "chart.html")]) == 0
    fetch.assert_called_once_with("GOOGL")
    assert "Dashboard saved" in capsys.readouterr().out


def test_cli_reports_safe_failure(monkeypatch, capsys):
    monkeypatch.setattr(stocks, "fetch_stocks_csv", Mock(side_effect=stocks.StocksError("Missing key")))
    assert stocks.main(["--symbol", "NFLX"]) == 1
    assert "Missing key" in capsys.readouterr().out


def test_cli_reports_output_failure(monkeypatch, tmp_path, capsys):
    output = tmp_path / "file"
    output.write_text("A file cannot also be a directory")
    assert stocks.main(["--demo", "--output", str(output / "chart.html")]) == 1
    assert "Stocks dashboard:" in capsys.readouterr().out


@pytest.mark.parametrize("exception", [EOFError, KeyboardInterrupt])
def test_cli_cancellation(monkeypatch, capsys, exception):
    def cancel(prompt):
        raise exception
    monkeypatch.setattr("builtins.input", cancel)
    assert stocks.main([]) == 0
    assert "Dashboard cancelled." in capsys.readouterr().out


def test_stocks_import_has_no_side_effects():
    result = subprocess.run([sys.executable, "-c", "import app.stocks"],
                            input="", text=True, capture_output=True,
                            cwd=Path(__file__).resolve().parents[1], timeout=20)
    assert result.returncode == 0, result.stderr
    assert result.stdout == ""
