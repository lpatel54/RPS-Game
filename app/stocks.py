"""Fetch AlphaVantage adjusted daily prices and build a local HTML dashboard."""

import argparse
from io import StringIO
import json
import os
from pathlib import Path
import re

from dotenv import load_dotenv
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import requests

API_URL = "https://www.alphavantage.co/query"
PROJECT_ROOT = Path(__file__).resolve().parents[1]


class StocksError(ValueError):
    """An actionable configuration, API, or data error safe to show users."""


def normalize_symbol(symbol: str) -> str:
    """Validate and normalize common ticker formats, including BRK.B."""
    symbol = symbol.strip().upper()
    if not re.fullmatch(r"[A-Z][A-Z0-9.-]{0,19}", symbol):
        raise StocksError("Enter a valid stock symbol, for example NFLX or BRK.B.")
    return symbol


def parse_stocks_csv(csv_text: str) -> pd.DataFrame:
    """Validate a daily-adjusted CSV and sort it from oldest to newest."""
    try:
        payload = json.loads(csv_text)
    except (ValueError, TypeError):
        payload = None
    if isinstance(payload, dict):
        if "Note" in payload:
            raise StocksError("AlphaVantage rate limit reached. Try again later.")
        if "Information" in payload:
            raise StocksError(
                "AlphaVantage could not provide data. Check your API key, rate "
                "limit, and access to the premium daily-adjusted endpoint."
            )
        raise StocksError("AlphaVantage rejected the request. Check the symbol and API key.")

    try:
        frame = pd.read_csv(StringIO(csv_text))
        if not {"timestamp", "adjusted_close"}.issubset(frame.columns):
            raise ValueError("Missing columns")
        if frame.empty:
            raise ValueError("No prices")
        frame["timestamp"] = pd.to_datetime(frame["timestamp"], format="%Y-%m-%d", errors="raise")
        frame["adjusted_close"] = pd.to_numeric(frame["adjusted_close"], errors="raise")
        prices = frame["adjusted_close"]
        if (frame["timestamp"].isna().any() or frame["timestamp"].duplicated().any()
                or prices.isna().any() or (prices <= 0).any()
                or prices.isin([float("inf"), float("-inf")]).any()):
            raise ValueError("Invalid prices or dates")
        return frame.sort_values("timestamp").reset_index(drop=True)
    except (ValueError, TypeError, pd.errors.ParserError):
        raise StocksError("Stock data is empty or invalid; expected dates and adjusted closing prices.") from None


def fetch_stocks_csv(symbol: str = "NFLX", api_key: str | None = None) -> pd.DataFrame:
    """Fetch validated prices without exposing credentials in error messages.

    Uses the same TIME_SERIES_DAILY_ADJUSTED endpoint as the class example.
    Tests mock HTTP at this boundary so CI needs no secret or network request.
    """
    symbol = normalize_symbol(symbol)
    if api_key is None:
        load_dotenv(PROJECT_ROOT / ".env", override=False)
        api_key = os.getenv("ALPHAVANTAGE_API_KEY")
    if not api_key or not api_key.strip():
        raise StocksError("Set ALPHAVANTAGE_API_KEY in your local .env file before fetching prices.")
    try:
        response = requests.get(
            API_URL,
            params={
                "function": "TIME_SERIES_DAILY_ADJUSTED", "symbol": symbol,
                "apikey": api_key.strip(), "datatype": "csv", "outputsize": "compact",
            },
            timeout=20,
        )
        response.raise_for_status()
    except requests.RequestException:
        # Requests exceptions can contain the complete URL, including the key.
        raise StocksError("Unable to fetch stock prices. Check your connection and try again.") from None
    return parse_stocks_csv(response.text)


def build_dashboard(stocks_df: pd.DataFrame, symbol: str) -> go.Figure:
    """Build an interactive chart with the latest close and period change."""
    symbol = normalize_symbol(symbol)
    frame = parse_stocks_csv(stocks_df.to_csv(index=False))
    first = float(frame.iloc[0]["adjusted_close"])
    latest = float(frame.iloc[-1]["adjusted_close"])
    change = (latest / first - 1) * 100
    fig = make_subplots(
        rows=2, cols=2,
        specs=[[{"type": "indicator"}, {"type": "indicator"}],
               [{"type": "scatter", "colspan": 2}, None]],
        row_heights=[0.25, 0.75], vertical_spacing=0.15,
    )
    fig.add_trace(go.Indicator(
        mode="number", value=latest, number={"valueformat": ",.2f"},
        title={"text": "Latest adjusted close (quote currency)"},
    ), row=1, col=1)
    fig.add_trace(go.Indicator(
        mode="number", value=change, number={"suffix": "%", "valueformat": "+.2f"},
        title={"text": "Change over displayed period"},
    ), row=1, col=2)
    fig.add_trace(go.Scatter(
        x=frame["timestamp"], y=frame["adjusted_close"],
        mode="lines" if len(frame) > 1 else "markers",
        name="Adjusted close", line={"color": "#2563eb", "width": 3},
    ), row=2, col=1)
    start = frame.iloc[0]["timestamp"].date()
    end = frame.iloc[-1]["timestamp"].date()
    fig.update_layout(
        title=f"Stock Prices ({symbol}) — {start} to {end}",
        template="plotly_white", height=700, showlegend=False,
        margin={"t": 100, "b": 70},
    )
    fig.update_xaxes(title_text="Trading date", rangeslider_visible=True, row=2, col=1)
    fig.update_yaxes(title_text="Adjusted close (quote currency)", row=2, col=1)
    return fig


def demo_prices() -> pd.DataFrame:
    """Return the fictional sample prices shared by both interfaces."""
    return parse_stocks_csv(
        "timestamp,adjusted_close\n2026-01-02,100\n2026-01-05,103\n"
        "2026-01-06,101\n2026-01-07,105\n2026-01-08,108\n"
    )


def main(argv: list[str] | None = None) -> int:
    """Save a standalone dashboard; optionally open it in a local browser."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--symbol", help="Stock ticker; prompts when omitted")
    parser.add_argument("--demo", action="store_true", help="Use fictional sample prices without an API key")
    parser.add_argument("--output", type=Path, default=Path("work/stocks-dashboard.html"))
    parser.add_argument("--open", action="store_true", help="Open the saved HTML in your browser")
    args = parser.parse_args(argv)
    try:
        symbol = normalize_symbol(args.symbol or ("DEMO" if args.demo else input("Please choose a stock symbol [NFLX]: ") or "NFLX"))
        if args.demo:
            frame = demo_prices()
            symbol = "DEMO"
            print("Demo mode: fictional sample prices, not market data.")
        else:
            frame = fetch_stocks_csv(symbol)
        fig = build_dashboard(frame, symbol)
        args.output.parent.mkdir(parents=True, exist_ok=True)
        fig.write_html(args.output, include_plotlyjs=True, full_html=True, auto_open=args.open)
        print(frame[["timestamp", "adjusted_close"]].tail().to_string(index=False))
        print(f"Dashboard saved to {args.output.resolve()}")
        return 0
    except (StocksError, OSError) as error:
        print(f"Stocks dashboard: {error}")
        return 1
    except (EOFError, KeyboardInterrupt):
        print("\nDashboard cancelled.")
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
