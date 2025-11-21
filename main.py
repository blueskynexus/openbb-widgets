from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import util.configure_logging as util

# Initialize FastAPI application with metadata
app = FastAPI(
    title="Hello World",
    description="Hello World app for OpenBB Workspace",
    version="0.0.1"
)

# Define allowed origins for CORS (Cross-Origin Resource Sharing)
# This restricts which domains can access the API
origins = [
    "https://pro.openbb.co",
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

@app.get("/")
def read_root():
    """Root endpoint that returns basic information about the API"""
    return {"Info": "Hello World example"}


def main():
    util.configure_logging()



if __name__ == "__main__":
    main()
