"""
 Joshua Jackson
 February 19, 2025,
 FastAPI backend entry point
 MCAD Backend Authentication

 installed dependencies using PyCharm terminal:
 pip install fastapi uvicorn bcrypt pyjwt python-dotenv snowflake-connector-python
 In PyCharm terminal press: Ctrl + C to stop the server
"""
#############################################
### Step 8: Implement User Authentication ###
#############################################
import re
import nltk # *** could comment-out ***
from nltk.corpus import words # *** could comment-out ***
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from datetime import datetime, timedelta, UTC  # Ensure UTC is imported
import jwt
import bcrypt
import os
from dotenv import load_dotenv
from database import get_snowflake_connection

# Load environment variables
load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

"""
words used
"""
# Download English words dataset (only needed once)
nltk.download("words") # *** could comment-out ***
english_words = set(words.words()) # *** could comment-out ***

app = FastAPI()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# User schema for registration
class UserCreate(BaseModel):
    username: str
    email: str
    password: str

# User schema for response (excluding password)
class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    is_active: bool


# Function to validate password complexity
def validate_password(password: str) -> bool:
    """Validates password strength."""
    print(f"Validating password: {password}")  # Debugging

    if len(password) < 16 or len(password) > 64:
        print("Failed: Length check")
        return False
    if not any(c.islower() for c in password):
        print("Failed: No lowercase letter")
        return False
    if not any(c.isupper() for c in password):
        print("Failed: No uppercase letter")
        return False
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        print("Failed: No special character")
        return False

    # Tokenize password into words and check against English words
    password_words = [word for word in re.findall(r'\b[a-zA-Z]+\b', password) if len(word) > 1]
    print(f"Extracted words: {password_words}")  # Debugging

    if any(word.lower() in english_words for word in password_words):
        print(f"Failed: Contains dictionary words -> {password_words}")
        return False

    print("Password is valid!")  # Debugging
    return True

####################################
#### Debugging Password Example ####
##################################
# def validate_password(password: str) -> bool:
#     """Validates password strength."""
#     print(f"Validating password: {password}")  # Debugging
#
#     if len(password) < 16 or len(password) > 64:
#         print("Failed: Length check")
#         return False
#     if not any(c.islower() for c in password):
#         print("Failed: No lowercase letter")
#         return False
#     if not any(c.isupper() for c in password):
#         print("Failed: No uppercase letter")
#         return False
#     if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
#         print("Failed: No special character")
#         return False
#
#     # Tokenize password into whole words and check against dictionary
#     password_words = re.findall(r'\b[a-zA-Z]+\b', password)  # Extract whole words only
#     print(f"Extracted words: {password_words}")  # Debugging
#
#     if any(word.lower() in english_words for word in password_words):
#         print(f"Failed: Contains dictionary words -> {password_words}")
#         return False
#
#     print("Password is valid!")  # Debugging
#     return True
###################################################

# Function to hash passwords
def hash_password(password: str) -> str:
    """Hashes the password if it meets complexity requirements."""
    if not validate_password(password):
        raise HTTPException(
            status_code=400,
            detail="Password must be 16-64 characters long, include uppercase, lowercase, special characters, and not contain dictionary words."
        )
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

# Function to verify passwords
def verify_password(plain_password, hashed_password) -> bool:
    return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))

# Function to create JWT token
def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = datetime.now(UTC) + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

@app.post("/register", response_model=UserResponse)
def register_user(user: UserCreate):
    """Register a new user in the database."""
    conn = get_snowflake_connection()
    if conn:
        try:
            cur = conn.cursor()

            # Convert username to lowercase
            username_lower = user.username.lower()

            # Check if username or email already exists (case-insensitive check)
            cur.execute("SELECT id FROM users WHERE LOWER(username)=%s OR email=%s", (username_lower, user.email))
            if cur.fetchone():
                raise HTTPException(status_code=400, detail="Username or email already registered")

            # Validate and hash the password
            hashed_password = hash_password(user.password)

            # Insert new user with lowercase username
            cur.execute(
                "INSERT INTO users (username, email, hashed_password) VALUES (%s, %s, %s)",
                (username_lower, user.email, hashed_password),
            )
            conn.commit()
            cur.close()

            # Retrieve the newly created user
            cur = conn.cursor()
            cur.execute("SELECT id, username, email, is_active FROM users WHERE LOWER(username)=%s", (username_lower,))
            new_user = cur.fetchone()

            return UserResponse(id=new_user[0], username=new_user[1], email=new_user[2], is_active=new_user[3])
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Database error: {e}")
        finally:
            conn.close()
    raise HTTPException(status_code=500, detail="Database connection failed")

@app.post("/token")
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    """Authenticate user and return JWT token."""
    conn = get_snowflake_connection()
    if conn:
        try:
            cur = conn.cursor()

            # Convert username to lowercase when querying (case-insensitive login)
            cur.execute("SELECT id, username, hashed_password FROM users WHERE LOWER(username)=%s", (form_data.username.lower(),))
            user = cur.fetchone()
            if not user or not verify_password(form_data.password, user[2]):
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

            # Generate JWT token
            access_token = create_access_token(data={"sub": user[1]})
            return {"access_token": access_token, "token_type": "bearer"}
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Database error: {e}")
        finally:
            conn.close()
    raise HTTPException(status_code=500, detail="Database connection failed")


