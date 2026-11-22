"""Render the stock form, prices dashboard, and the checkpoint JSON route."""

from flask import Blueprint, flash, redirect, render_template, request, url_for

from app.stocks import StocksError, build_dashboard, demo_prices, fetch_stocks_csv, normalize_symbol

stocks_routes = Blueprint("stocks_routes", __name__)


def _price_records(frame):
    """Serialize the two fields used in the dashboard and the JSON response."""
    return [
        {"timestamp": date.strftime("%Y-%m-%d"), "adjusted_close": float(price)}
        for date, price in zip(frame["timestamp"], frame["adjusted_close"])
    ]


@stocks_routes.get("/stocks/form")
def stocks_form():
    return render_template("stocks_form.html")


@stocks_routes.route("/stocks/dashboard", methods=["GET", "POST"])
def stocks_dashboard():
    fields = request.form if request.method == "POST" else request.args
    demo = fields.get("demo") == "1"
    try:
        symbol = "DEMO" if demo else normalize_symbol(fields.get("symbol", "NFLX"))
        frame = demo_prices() if demo else fetch_stocks_csv(symbol)
        figure = build_dashboard(frame, symbol)
    except StocksError as error:
        flash(str(error), "danger")
        return redirect(url_for("stocks_routes.stocks_form"), code=303)

    # The HTML summary stays readable on narrow screens. Reuse the existing
    # price series and date slider from the command-line dashboard.
    latest, change = (trace.value for trace in figure.select_traces(selector={"type": "indicator"}))
    figure.data = tuple(figure.select_traces(selector={"type": "scatter"}))
    figure.update_yaxes(domain=[0, 1])
    figure.update_layout(title=None, height=420, margin={"t": 20, "b": 65, "l": 70, "r": 20})
    chart = figure.to_html(
        full_html=False,
        include_plotlyjs="cdn",
        config={"displaylogo": False, "responsive": True},
        div_id="stock-price-chart",
    )
    return render_template(
        "stocks_dashboard.html",
        symbol=symbol,
        prices=_price_records(frame.iloc[::-1]),
        latest=latest,
        change=change,
        chart=chart,
        demo=demo,
    )


@stocks_routes.get("/api/stocks.json")
def stocks_api():
    try:
        symbol = normalize_symbol(request.args.get("symbol", "NFLX"))
    except StocksError as error:
        return {"message": str(error)}, 400
    try:
        frame = fetch_stocks_csv(symbol)
    except StocksError as error:
        return {"message": str(error)}, 502
    return {"symbol": symbol, "data": _price_records(frame.iloc[::-1])}
