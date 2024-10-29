from routes import data_routes
from fastapi import FastAPI

# Create FastAPI instance
app = FastAPI()

# Include the routers
app.include_router(data_routes.router, prefix="/data", tags=["data"])
