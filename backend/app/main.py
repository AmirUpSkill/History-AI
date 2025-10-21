from fastapi import FastAPI
from app.api.v1.router import api_router
from fastapi.middleware.cors import CORSMiddleware


# --- Fast API Instance ---
app = FastAPI(
    title="History AI Wiki API",
    description="API for curating AI-generated historical and political event cards.",
    version="1.0.0"
)
# --- Add CORS middleware ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "*"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --- InClude the main Endpoint ---
app.include_router(api_router, prefix="/api/v1")

# --- Add rout check ---
@app.get("/", tags=["Root"])
def read_root():
    """
    Root endpoint for health checks.
    """
    return {"status": "ok", "message": "Welcome to the History AI Wiki API!"}