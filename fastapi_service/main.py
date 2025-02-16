from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi_service.routes import router  # Your routes

app = FastAPI(title="Stock Analysis API", version="1.0")

# Configure CORS
origins = [
    "http://localhost:3000",  # React app's origin
    # Add any other origins if needed, e.g. production domain
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API routes with prefix /api
app.include_router(router, prefix="/api")

@app.get("/")
def root():
    return {"message": "Welcome to the Stock Analysis API!"}
