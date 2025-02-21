"""
 Joshua Jackson
 February 19, 2025,
 FastAPI backend entry point
 MCAD Backend Authentication

 installed dependencies using PyCharm terminal:
 pip install fastapi uvicorn bcrypt pyjwt python-dotenv snowflake-connector-python
"""
##################
### Dummy Code ###
##################
# from fastapi import FastAPI, Depends, HTTPException, status
# from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
# from passlib.context import CryptContext
# import jwt
# import datetime
# from typing import Optional
# import os
# from dotenv import load_dotenv
#
# # Load environment variables
# load_dotenv()
# SECRET_KEY = os.getenv("SECRET_KEY", "your_secret_key")
# ALGORITHM = "HS256"
# ACCESS_TOKEN_EXPIRE_MINUTES = 30
#
# app = FastAPI()
#
# # Dummy users database
# org_users_db = {
#     "jjackson": {"username": "jjackson", "full_name": "Joshua Jackson", "hashed_password": "$2b$12$..."},
#     "mmata": {"username": "mmata", "full_name": "Marc Mata", "hashed_password": "$2b$12$..."},
#     "ssingh": {"username": "ssingh", "full_name": "Sukhraj Singh", "hashed_password": "$2b$12$..."},
#     "apham": {"username": "apham", "full_name": "Anthony Pham", "hashed_password": "$2b$12$..."},
#     "ksmith": {"username": "ksmith", "full_name": "Kyle Smith", "hashed_password": "$2b$12$..."}
# }
#
# # Password hashing
# pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
# oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
#
# def verify_password(plain_password, hashed_password):
#     return pwd_context.verify(plain_password, hashed_password)
#
# def get_password_hash(password):
#     return pwd_context.hash(password)
#
# def authenticate_user(username: str, password: str):
#     user = org_users_db.get(username)
#     if not user or not verify_password(password, user["hashed_password"]):
#         return False
#     return user
#
# def create_access_token(data: dict, expires_delta: Optional[datetime.timedelta] = None):
#     to_encode = data.copy()
#     expire = datetime.datetime.utcnow() + (expires_delta or datetime.timedelta(minutes=15))
#     to_encode.update({"exp": expire})
#     return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
#
# @app.post("/token")
# def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
#     user = authenticate_user(form_data.username, form_data.password)
#     if not user:
#         raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect username or password")
#     access_token = create_access_token(data={"sub": user["username"]})
#     return {"access_token": access_token, "token_type": "bearer"}

#############################################
### Step 8: Implement User Authentication ###
#############################################
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from datetime import timedelta, datetime
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


# Function to hash passwords
def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


# Function to verify passwords
def verify_password(plain_password, hashed_password) -> bool:
    return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))


# Function to create JWT token
def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


@app.post("/register", response_model=UserResponse)
def register_user(user: UserCreate):
    """Register a new user in the database."""
    conn = get_snowflake_connection()
    if conn:
        try:
            cur = conn.cursor()

            # Check if username or email already exists
            cur.execute("SELECT id FROM MCAD.MCAD_DATA.USERS WHERE username=%s OR email=%s",
                        (user.username, user.email))
            if cur.fetchone():
                raise HTTPException(status_code=400, detail="Username or email already registered")

            # Insert new user (WITHOUT RETURNING)
            hashed_password = hash_password(user.password)
            cur.execute(
                "INSERT INTO MCAD.MCAD_DATA.USERS (USERNAME, EMAIL, HASHED_PASSWORD) VALUES (%s, %s, %s)",
                (user.username, user.email, hashed_password),
            )
            conn.commit()

            # Fetch the newly created user (since RETURNING is not available)
            cur.execute("SELECT ID, USERNAME, EMAIL, IS_ACTIVE FROM MCAD.MCAD_DATA.USERS WHERE EMAIL=%s", (user.email,))
            new_user = cur.fetchone()

            cur.close()
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
            cur.execute("SELECT id, username, hashed_password FROM users WHERE username=%s", (form_data.username,))
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

