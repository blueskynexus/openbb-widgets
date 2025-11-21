from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import util.configure_logging as util
import json
from pathlib import Path
from fastapi.responses import JSONResponse
from functools import wraps
import asyncio
from via_nexus.dataset import stock_stats

# Initialize FastAPI application with metadata
app = FastAPI(
    title="Vianexus Stock Stats",
    description="Stock statistics widgets powered by Vianexus API",
    version="0.1.0"
)

# Define allowed origins for CORS (Cross-Origin Resource Sharing)
# This restricts which domains can access the API
origins = [
    "https://pro.openbb.co",
    "https://pro.openbb.dev",
    "http://localhost:1420"
]

# Configure CORS middleware to handle cross-origin requests
# This allows the specified origins to make requests to the API
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)


# Initialize empty dictionary for widgets
WIDGETS = {}


def register_widget(widget_config):
    """
    Decorator that registers a widget configuration in the WIDGETS dictionary.

    Args:
        widget_config (dict): The widget configuration to add to the WIDGETS
            dictionary. This should follow the same structure as other entries
            in WIDGETS.

    Returns:
        function: The decorated function.
    """
    def decorator(func):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            # Call the original function
            return await func(*args, **kwargs)

        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            # Call the original function
            return func(*args, **kwargs)

        # Extract the endpoint from the widget_config
        endpoint = widget_config.get("endpoint")
        if endpoint:
            # Add an id field to the widget_config if not already present
            if "widgetId" not in widget_config:
                widget_config["widgetId"] = endpoint

            # Use id as the key to allow multiple widgets per endpoint
            widget_id = widget_config["widgetId"]
            WIDGETS[widget_id] = widget_config

        # Return the appropriate wrapper based on whether the function is async
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        return sync_wrapper
    return decorator


@app.get("/")
def read_root():
    """Root endpoint that returns basic information about the API"""
    return {"Info": "Vianexus Stock Stats Widget Backend"}


# Widgets configuration file for the OpenBB Workspace
# it contains the information and configuration about all the
# widgets that will be displayed in the OpenBB Workspace
@app.get("/widgets.json")
def get_widgets():
    """Widgets configuration file for the OpenBB Workspace

    Returns:
        JSONResponse: The WIDGETS dictionary containing all registered widgets
    """
    # Return the registered widgets configuration
    return JSONResponse(content=WIDGETS)


# Apps configuration file for the OpenBB Workspace
# it contains the information and configuration about all the
# apps that will be displayed in the OpenBB Workspace
@app.get("/apps.json")
def get_apps():
    """Apps configuration file for the OpenBB Workspace

    Returns:
        JSONResponse: The contents of apps.json file
    """
    # Read and return the apps configuration file
    return JSONResponse(
        content=json.load((Path(__file__).parent.resolve() / "documents" / "apps.json").open())
    )


# Stock Stats Metric Widget
@register_widget({
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
            "description": "Enter a stock ticker symbol (e.g., AAPL, MSFT, GOOGL)"
        }
    ]
})
@app.get("/stock_stats")
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
            raise HTTPException(
                status_code=404,
                detail=f"No data found for symbol: {symbol}"
            )

        # Extract the first (and only) result
        data = response[0]

        # Build metrics array
        metrics = []

        # Company name and symbol
        if "issuerName" in data:
            metrics.append({
                "label": "Company",
                "value": data["issuerName"]
            })

        # 52-Week High
        if "52weekHigh" in data:
            metrics.append({
                "label": "52-Week High",
                "value": f"${data['52weekHigh']:.2f}",
                "description": f"Date: {data.get('52weekHighDate', 'N/A')}"
            })

        # 52-Week Low
        if "52weekLow" in data:
            metrics.append({
                "label": "52-Week Low",
                "value": f"${data['52weekLow']:.2f}",
                "description": f"Date: {data.get('52weekLowDate', 'N/A')}"
            })

        # 52-Week Change
        if "52weekChange" in data:
            change_pct = data["52weekChange"] * 100
            metrics.append({
                "label": "52-Week Change",
                "value": f"{change_pct:+.2f}%",
                "delta": f"{data['52weekChange']:.4f}"
            })

        # YTD Change
        if "ytdChange" in data:
            ytd_pct = data["ytdChange"] * 100
            metrics.append({
                "label": "YTD Change",
                "value": f"{ytd_pct:+.2f}%",
                "delta": f"{data['ytdChange']:.4f}"
            })

        # PE Ratio
        if "peRatioTtm" in data:
            metrics.append({
                "label": "P/E Ratio (TTM)",
                "value": f"{data['peRatioTtm']:.2f}"
            })

        # EPS
        if "epsTtm" in data:
            metrics.append({
                "label": "EPS (TTM)",
                "value": f"${data['epsTtm']:.2f}"
            })

        # Beta
        if "beta" in data:
            metrics.append({
                "label": "Beta",
                "value": f"{data['beta']:.2f}",
                "description": "Volatility measure vs. market"
            })

        # 50-Day Moving Average
        if "day50MovingAverage" in data:
            metrics.append({
                "label": "50-Day MA",
                "value": f"${data['day50MovingAverage']:.2f}"
            })

        # 200-Day Moving Average
        if "day200MovingAverage" in data:
            metrics.append({
                "label": "200-Day MA",
                "value": f"${data['day200MovingAverage']:.2f}"
            })

        # Average 30-Day Volume
        if "avg30DayVolume" in data:
            volume = data["avg30DayVolume"]
            if volume >= 1_000_000:
                volume_str = f"{volume / 1_000_000:.2f}M"
            elif volume >= 1_000:
                volume_str = f"{volume / 1_000:.2f}K"
            else:
                volume_str = f"{volume:,}"

            metrics.append({
                "label": "Avg 30-Day Volume",
                "value": volume_str
            })

        # Shares Outstanding
        if "sharesOutstanding" in data:
            shares = data["sharesOutstanding"]
            if shares >= 1_000_000_000:
                shares_str = f"{shares / 1_000_000_000:.2f}B"
            elif shares >= 1_000_000:
                shares_str = f"{shares / 1_000_000:.2f}M"
            else:
                shares_str = f"{shares:,}"

            metrics.append({
                "label": "Shares Outstanding",
                "value": shares_str
            })

        return JSONResponse(content=metrics)

    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        # Log the error and return a friendly message
        util.configure_logging()
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Error fetching stock stats for {symbol}: {str(e)}")

        raise HTTPException(
            status_code=500,
            detail=f"Error fetching data for symbol {symbol}: {str(e)}"
        )


# Hello World endpoint - for it to be recognized by the OpenBB Workspace
# it needs to be added to the widgets.json file endpoint
@app.get("/hello_world")
def hello_world(name: str = ""):
    """Returns a personalized greeting message.

    Args:
        name (str, optional): Name to include in the greeting. Defaults to empty string.

    Returns:
        str: A greeting message with the provided name in markdown format.
    """
    # Return a markdown-formatted greeting with the provided name
    return f"# Hello World {name}"


def main():
    util.configure_logging()


if __name__ == "__main__":
    main()
