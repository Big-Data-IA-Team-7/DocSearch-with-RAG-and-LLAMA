from fast_api.routes import index_routes, pdf_routes, query_routes
from fastapi import FastAPI

# Create FastAPI instance
app = FastAPI()

# Include the routers
app.include_router(pdf_routes.router, prefix="/pdf", tags=["PDF Operations"])
app.include_router(index_routes.router, prefix="/index", tags=["Index Operations"])
app.include_router(query_routes.router, prefix="/query", tags=["Query Operations"])