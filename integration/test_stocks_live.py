"""Opt-in check of real stock data and dashboard generation."""

import os

import pytest

from app.stocks import StocksError, build_dashboard, fetch_stocks_csv

pytestmark = [
    pytest.mark.live,
    pytest.mark.skipif(
        os.getenv("RUN_LIVE_STOCKS") != "1",
        reason="Set RUN_LIVE_STOCKS=1 to opt into the real API check.",
    ),
]


def test_live_stocks_fetch_and_dashboard(tmp_path):
    """Verify the class endpoint returns prices usable by the real dashboard."""
    try:
        frame = fetch_stocks_csv("NFLX")
    except StocksError as error:
        # Application errors omit the key and provider response body.
        pytest.fail(f"Live API check (Actions secret: AlphaVantage_Secret): {error}", pytrace=False)

    assert {"timestamp", "adjusted_close"}.issubset(frame.columns)
    assert len(frame) >= 100, "Expected at least 100 daily prices from the compact response."
    figure = build_dashboard(frame, "NFLX")
    output = tmp_path / "live-stocks-dashboard.html"
    figure.write_html(output, include_plotlyjs=True, full_html=True)
    assert output.stat().st_size > 0
    assert len(figure.data[2].y) == len(frame)
