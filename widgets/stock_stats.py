"""Stock Statistics Metric Widget.

This widget displays key stock statistics and metrics powered by the Vianexus API.
It shows fundamental and technical indicators including PE ratio, EPS, moving averages,
52-week highs/lows, and volume data.
"""

from fastapi import HTTPException
from fastapi.responses import JSONResponse
import logging

from registry import register_widget
from vianexus.dataset import stock_stats

logger = logging.getLogger(__name__)


@register_widget(
    {
        "name": "Stock Statistics",
        "description": "Key stock statistics and metrics powered by Vianexus",
        "category": "Stock Data",
        "endpoint": "stock_stats",
        "gridData": {"w": 12, "h": 8},
        "type": "metric",
        "params": [
            {
                "paramName": "symbol",
                "value": "AAPL",
                "label": "Stock Symbol",
                "type": "text",
                "description": "Enter a stock ticker symbol (e.g., AAPL, MSFT, GOOGL)",
            }
        ],
    }
)
def get_stock_stats(symbol: str = "AAPL"):
    """Returns stock statistics as metrics for a given symbol.

    Args:
        symbol (str): Stock ticker symbol. Defaults to "AAPL".

    Returns:
        JSONResponse: Array of metric objects with stock statistics.

    Raises:
        HTTPException: If the API call fails or symbol is invalid.
    """
    try:
        # Fetch data from Vianexus API
        response = stock_stats.data([symbol.upper()])

        # Check if we got valid data
        if not response or len(response) == 0:
            raise HTTPException(status_code=404, detail=f"No data found for symbol: {symbol}")

        # Extract the first (and only) result
        data = response[0]

        # Build metrics array
        metrics = []

        # Company name and symbol
        if "issuerName" in data:
            metrics.append({"label": "Company", "value": data["issuerName"]})

        # 52-Week High
        if "52weekHigh" in data:
            metrics.append(
                {
                    "label": "52-Week High",
                    "value": f"${data['52weekHigh']:.2f}",
                    "description": f"Date: {data.get('52weekHighDate', 'N/A')}",
                }
            )

        # 52-Week Low
        if "52weekLow" in data:
            metrics.append(
                {
                    "label": "52-Week Low",
                    "value": f"${data['52weekLow']:.2f}",
                    "description": f"Date: {data.get('52weekLowDate', 'N/A')}",
                }
            )

        # 52-Week Change
        if "52weekChange" in data:
            change_pct = data["52weekChange"] * 100
            metrics.append(
                {
                    "label": "52-Week Change",
                    "value": f"{change_pct:+.2f}%",
                    "delta": f"{data['52weekChange']:.4f}",
                }
            )

        # YTD Change
        if "ytdChange" in data:
            ytd_pct = data["ytdChange"] * 100
            metrics.append(
                {
                    "label": "YTD Change",
                    "value": f"{ytd_pct:+.2f}%",
                    "delta": f"{data['ytdChange']:.4f}",
                }
            )

        # PE Ratio
        if "peRatioTtm" in data:
            metrics.append({"label": "P/E Ratio (TTM)", "value": f"{data['peRatioTtm']:.2f}"})

        # EPS
        if "epsTtm" in data:
            metrics.append({"label": "EPS (TTM)", "value": f"${data['epsTtm']:.2f}"})

        # Beta
        if "beta" in data:
            metrics.append(
                {
                    "label": "Beta",
                    "value": f"{data['beta']:.2f}",
                    "description": "Volatility measure vs. market",
                }
            )

        # 50-Day Moving Average
        if "day50MovingAverage" in data:
            metrics.append({"label": "50-Day MA", "value": f"${data['day50MovingAverage']:.2f}"})

        # 200-Day Moving Average
        if "day200MovingAverage" in data:
            metrics.append({"label": "200-Day MA", "value": f"${data['day200MovingAverage']:.2f}"})

        # Average 30-Day Volume
        if "avg30DayVolume" in data:
            volume = data["avg30DayVolume"]
            if volume >= 1_000_000:
                volume_str = f"{volume / 1_000_000:.2f}M"
            elif volume >= 1_000:
                volume_str = f"{volume / 1_000:.2f}K"
            else:
                volume_str = f"{volume:,}"

            metrics.append({"label": "Avg 30-Day Volume", "value": volume_str})

        # Shares Outstanding
        if "sharesOutstanding" in data:
            shares = data["sharesOutstanding"]
            if shares >= 1_000_000_000:
                shares_str = f"{shares / 1_000_000_000:.2f}B"
            elif shares >= 1_000_000:
                shares_str = f"{shares / 1_000_000:.2f}M"
            else:
                shares_str = f"{shares:,}"

            metrics.append({"label": "Shares Outstanding", "value": shares_str})

        return JSONResponse(content=metrics)

    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        # Log the error and return a friendly message
        logger.error(f"Error fetching stock stats for {symbol}: {str(e)}")

        raise HTTPException(
            status_code=500, detail=f"Error fetching data for symbol {symbol}: {str(e)}"
        )
