"""FastAPI backend for OpenBB Workspace integrations with Vianexus API.

This module sets up the FastAPI application and registers all widgets.
Individual widget implementations are located in the widgets/ directory.
"""

import json
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

import utils.logging as logging_utils
from registry import WIDGETS, register_widget

# Initialize FastAPI application with metadata
app = FastAPI(
    title="Vianexus Stock Stats",
    description="Stock statistics widgets powered by Vianexus API",
    version="0.1.0"
)

# Define allowed origins for CORS (Cross-Origin Resource Sharing)
origins = [
    "https://pro.openbb.co",
    "https://pro.openbb.dev",
    "http://localhost:1420"
]

# Configure CORS middleware to handle cross-origin requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)


@app.get("/")
def read_root():
    """Root endpoint that returns basic information about the API."""
    return {"Info": "Vianexus Stock Stats Widget Backend"}


@app.get("/widgets.json")
def get_widgets():
    """Widgets configuration file for OpenBB Workspace.

    Returns:
        JSONResponse: The WIDGETS dictionary containing all registered widgets.
    """
    return JSONResponse(content=WIDGETS)


@app.get("/apps.json")
def get_apps():
    """Apps configuration file for OpenBB Workspace.

    Returns:
        JSONResponse: The contents of apps.json file.
    """
    return JSONResponse(
        content=json.load((Path(__file__).parent.resolve() / "documents" / "apps.json").open())
    )


# Import all widgets to register them with the application
# This must come after the app is defined so widgets can register their routes
from widgets.stock_stats import get_stock_stats
from widgets.hello_world import hello_world

# Register widget routes with the FastAPI app
app.get("/stock_stats")(get_stock_stats)
app.get("/hello_world")(hello_world)


def main():
    """Initialize logging configuration."""
    logging_utils.configure_logging()


if __name__ == "__main__":
    main()
