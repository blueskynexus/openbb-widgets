"""Stock Price Chart Widget.

This widget displays historical stock price data as an interactive Plotly chart.
It shows price trends over a 1-month period with customizable metrics (future).
"""

import json
import logging
from fastapi import HTTPException
import plotly.graph_objects as go

from registry import register_widget
from vianexus.dataset import stock_stats
from utils.plotly_config import base_layout

logger = logging.getLogger(__name__)


@register_widget(
    {
        "name": "Stock Price Chart",
        "description": "Historical stock price chart (1 month)",
        "category": "Stock Data",
        "endpoint": "stock_chart",
        "gridData": {"w": 12, "h": 8},
        "type": "chart",
        "raw": True,  # Enable raw data access for AI
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
def get_stock_chart(symbol: str = "AAPL"):
    """Returns historical stock price chart for a given symbol.

    Args:
        symbol (str): Stock ticker symbol. Defaults to "AAPL".

    Returns:
        dict: Plotly figure JSON with historical price data.

    Raises:
        HTTPException: If the API call fails or symbol is invalid.
    """
    try:
        # Fetch 30 days of historical data
        response = stock_stats.historical_data([symbol.upper()], last=30)

        # Check if we got valid data
        if not response or len(response) == 0:
            raise HTTPException(
                status_code=404, detail=f"No historical data found for symbol: {symbol}"
            )

        # Extract dates and moving averages from the response
        dates = []
        ma_50 = []
        ma_200 = []

        for record in response:
            if "date" in record:
                dates.append(record["date"])
                # Extract 50-day MA (if available)
                ma_50.append(record.get("day50MovingAverage", None))
                # Extract 200-day MA (if available)
                ma_200.append(record.get("day200MovingAverage", None))

        # If we don't have enough data, raise an error
        if len(dates) == 0:
            raise HTTPException(
                status_code=404,
                detail=f"Insufficient historical data for symbol: {symbol}",
            )

        # Create the Plotly figure
        fig = go.Figure()

        # Add 50-Day Moving Average trace
        fig.add_trace(
            go.Scatter(
                x=dates,
                y=ma_50,
                mode="lines+markers",
                name="50-Day MA",
                line={"color": "#00B140", "width": 2},
                marker={"size": 4},
                hovertemplate="<b>%{x}</b><br>50-Day MA: $%{y:.2f}<extra></extra>",
            )
        )

        # Add 200-Day Moving Average trace
        fig.add_trace(
            go.Scatter(
                x=dates,
                y=ma_200,
                mode="lines+markers",
                name="200-Day MA",
                line={"color": "#FF8000", "width": 2},
                marker={"size": 4},
                hovertemplate="<b>%{x}</b><br>200-Day MA: $%{y:.2f}<extra></extra>",
            )
        )

        # Apply the dark theme layout
        layout = base_layout(x_title="Date", y_title="Price (USD)", y_format="$,.2f")
        layout["title"] = f"{symbol.upper()} - Moving Averages (1 Month)"
        layout["showlegend"] = True  # Show legend for multiple series

        fig.update_layout(layout)

        # Return the Plotly figure as JSON
        return json.loads(fig.to_json())  # type: ignore

    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        # Log the error and return a friendly message
        logger.error(f"Error fetching stock chart for {symbol}: {str(e)}")

        raise HTTPException(
            status_code=500, detail=f"Error fetching chart data for symbol {symbol}: {str(e)}"
        )
