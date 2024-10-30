from fast_api.routes import rag_qa_routes
from fastapi import FastAPI

# Create FastAPI instance
app = FastAPI()

# Include the routers
app.include_router(rag_qa_routes.router, prefix="/ragqa", tags=["rag"])