from fastapi import FastAPI
from fastapi_service.routes import router  # Import routes

app = FastAPI(title="Stock Analysis API", version="1.0")

# Register API routes
app.include_router(router, prefix="/api")

@app.get("/")
def root():
    return {"message": "Welcome to the Stock Analysis API!"}
