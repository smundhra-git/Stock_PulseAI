from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi_service.routes import router  # Import your routes

app = FastAPI(title="Stock Analysis API", version="1.0")

# Define allowed frontend origins
origins = [
    "http://localhost:3000",  # React frontend
    "http://localhost:5173", #Vite frontend
]

# Enable CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # Allow frontend access
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods (GET, POST, PUT, DELETE, etc.)
    allow_headers=["*"],  # Allow all headers
)

# Register API routes
app.include_router(router, prefix="/api")

@app.get("/")
def root():
    return {"message": "Welcome to the Stock Analysis API!"}
