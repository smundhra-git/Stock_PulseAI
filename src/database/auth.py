# Handles all authentication

from src.database.base import *
import jwt as pyjwt
from passlib.context import CryptContext
from datetime import datetime, timedelta


# JWT Secret Key and Algorithm
SECRET_KEY = "your_secret_key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def create_access_token(data: dict, expires_delta: timedelta):
    """Generates a JWT access token with an expiration time."""
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    return pyjwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def signup_user(username: str, password: str):
    """Registers a new user in the database."""
    conn = get_db_connection()
    cursor = conn.cursor()

    # Check if user already exists
    cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
    existing_user = cursor.fetchone()
    if existing_user:
        cursor.close()
        conn.close()
        return {"error": "Username already exists"}

    # Hash password and insert into database
    hashed_password = pwd_context.hash(password)
    cursor.execute(
        "INSERT INTO users (username, password) VALUES (%s, %s)",
        (username, hashed_password),
    )

    conn.commit()
    cursor.close()
    conn.close()
    return {"message": "User created successfully"}


def authenticate_user(username: str, password: str):
    """Validates user credentials and returns a JWT token if successful."""
    conn = get_db_connection()
    cursor = conn.cursor()

    # Fetch user from database
    cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
    user = cursor.fetchone()
    cursor.close()
    conn.close()

    if not user:
        return {"error": "Invalid username or password"}

    user_id, db_username, db_password = user  # Unpacking user data

    # Verify password
    if not pwd_context.verify(password, db_password):
        return {"error": "Invalid username or password"}

    # Generate JWT token
    access_token = create_access_token(
        data={"sub": db_username}, expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )

    return {"access_token": access_token, "token_type": "bearer"}


def verify_token(token: str):
    """Verifies a JWT token and extracts the username."""
    try:
        payload = pyjwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return {"username": payload["sub"]}
    except pyjwt.ExpiredSignatureError:
        return {"error": "Token expired"}
    except pyjwt.InvalidTokenError:
        return {"error": "Invalid token"}
