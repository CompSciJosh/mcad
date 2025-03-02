"""
 Joshua Jackson
 February 19, 2025,
 FastAPI backend entry point
 MCAD Backend Authentication
 ###########################################
 ################ Reminders ################
 ##########################################
1. REMEMBER! Run the FastAPI server: uvicorn main:app --reload
   First, navigate to the backend directory (cd ~/PycharmProjects/mcad/backend)
2. Open http://127.0.0.1:8000/docs in my browser
3. Run the PyQt6 GUI script in PyCharm
        Note: To troubleshoot, could also run:
        cd ~/PycharmProjects/mcad/frontend
        python mcad_gui.py

# # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # #
 installed dependencies using PyCharm terminal:
 pip install fastapi uvicorn bcrypt pyjwt python-dotenv sqlalchemy
 In PyCharm terminal press: Ctrl + C to stop the server
"""
#############################################
### Step 8: Implement User Authentication ###
#############################################
import json
import re
import nltk
import jwt
import bcrypt
import os
import numpy as np
import base64
from pathlib import Path
from nltk.corpus import words
from fastapi import FastAPI, Depends, HTTPException, status, File, UploadFile
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.responses import JSONResponse, FileResponse
from pydantic import BaseModel
from datetime import datetime, timedelta, UTC
from dotenv import load_dotenv
from sqlalchemy import create_engine, Column, Integer, String, Boolean, Float, ForeignKey, Text, LargeBinary
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from utils.crater_calculations import compute_camera_altitude, compute_image_dimensions, crater_diameter_meters
from typing import List, Optional

# Load environment variables
load_dotenv()

# Database configuration
DATABASE_URL = "sqlite:////Users/joshuajackson/PycharmProjects/mcad/data/database/mcad.db"
DATA_DIR = "/Users/joshuajackson/PycharmProjects/mcad/data/original/mcad_moon_data"

# Create engine
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Define database models
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)

class MoonCraterData(Base):
    __tablename__ = "moon_crater_data"

    id = Column(Integer, primary_key=True, index=True)
    folder_number = Column(String, index=True)
    file_name = Column(String, index=True)
    png_file = Column(String, unique=True)
    data = Column(Text)  # JSON data as text

class MoonCraterImage(Base):
    __tablename__ = "moon_crater_images"

    id = Column(Integer, primary_key=True, index=True)
    folder_number = Column(String, index=True)
    file_name = Column(String, index=True)
    png_file = Column(String, unique=True)
    image_data = Column(LargeBinary)

# Create tables
Base.metadata.create_all(bind=engine)

# Dependency to get the database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Download English words dataset (only needed once)
nltk.download("words")
english_words = set(words.words())

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
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    """Register a new user in the database."""
    try:
        # Convert username to lowercase
        username_lower = user.username.lower()

        # Check if username or email already exists (case-insensitive check)
        if db.query(User).filter((User.username.ilike(username_lower)) | (User.email == user.email)).first():
            raise HTTPException(status_code=400, detail="Username or email already registered")

        # Validate and hash the password
        hashed_password = hash_password(user.password)

        # Create new user with lowercase username
        new_user = User(
            username=username_lower,
            email=user.email,
            hashed_password=hashed_password
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)

        return UserResponse(
            id=new_user.id,
            username=new_user.username,
            email=new_user.email,
            is_active=new_user.is_active
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {e}")

@app.post("/token")
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """Authenticate user and return JWT token."""
    try:
        # Convert username to lowercase when querying (case-insensitive login)
        user = db.query(User).filter(User.username.ilike(form_data.username.lower())).first()

        if not user or not verify_password(form_data.password, user.hashed_password):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

        # Generate JWT token
        access_token = create_access_token(data={"sub": user.username})
        return {"access_token": access_token, "token_type": "bearer"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {e}")

####################################################################################
############ Calculate Camera Distance From Moon ###################################
############ Calculate Diameter of Craters Using Their Pixel Size ##################
####################################################################################
"""
Next as of Feb. 23, 2025 - Test the API using:
uvicorn main:app --reload

Then, send a test request using cURL or Postman:
curl -X 'POST' 'http://127.0.0.1:8000/compute_crater_size/' \
-H 'Content-Type: application/json' \
-d '{"cam_pos": [1890303.161771466, 1971386.8433341454, 2396504.6261527603], "pixel_diameter": 50}'

"""

# Constants
FOV_X = 0.3490658503988659  # Field of View in radians (X)
FOV_Y = 0.27580511636453603  # Field of View in radians (Y)
IMAGE_WIDTH_PX = 2592  # Image width in pixels
IMAGE_HEIGHT_PX = 2048  # Image height in pixels

class CraterRequest(BaseModel):
    cam_pos: List[float]  # Camera position in meters
    pixel_diameter: int  # Crater size in pixels

@app.post("/compute_crater_size/")
async def compute_crater_size(request: CraterRequest):
    """API endpoint to compute crater diameter in meters from pixel size."""
    cam_pos = np.array(request.cam_pos)
    altitude = compute_camera_altitude(cam_pos)
    image_width_m, _ = compute_image_dimensions(altitude, FOV_X, FOV_Y)
    crater_size_m = crater_diameter_meters(request.pixel_diameter, image_width_m, IMAGE_WIDTH_PX)

    return {
        "message": "Request received!",
        "cam_pos": request.cam_pos,
        "pixel_diameter": request.pixel_diameter,
        "camera_altitude_m": altitude,
        "image_width_m": image_width_m,
        "crater_diameter_m": crater_size_m
    }

@app.get("/list_folders")
def list_folders():
    """List all available folders in the data directory."""
    try:
        folder_path = Path(DATA_DIR)
        folders = [f.name for f in folder_path.iterdir() if f.is_dir() and f.name.startswith("Folder")]
        return {"folders": folders}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading folders: {str(e)}")

@app.get("/list_png_files/{folder_number}")
def list_png_files(folder_number: str):
    """List all PNG files in the specified folder."""
    try:
        folder_path = Path(DATA_DIR) / folder_number
        png_files = [f.name for f in folder_path.iterdir() if f.is_file() and f.suffix.lower() == '.png']
        return {"png_files": png_files}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading files: {str(e)}")

@app.get("/get_json/{folder_number}/{file_name}")
def get_json(folder_number: str, file_name: str):
    """Fetch JSON data from the local filesystem."""
    try:
        # Construct the path to the JSON file (replacing .png with .json if needed)
        json_file_name = file_name.replace(".png", ".json")
        json_path = Path(DATA_DIR) / folder_number / json_file_name

        # Check if JSON file exists
        if not json_path.exists():
            raise HTTPException(status_code=404, detail="JSON file not found")

        # Read and parse the JSON file
        with open(json_path, 'r') as f:
            json_data = json.load(f)

        return {"json_data": json_data}
    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail="Error decoding JSON file")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@app.get("/get_png/{folder_number}/{file_name}")
def get_png(folder_number: str, file_name: str):
    """Fetch and return PNG image file directly."""
    try:
        png_path = Path(DATA_DIR) / folder_number / file_name

        # Check if the file exists
        if not png_path.exists():
            raise HTTPException(status_code=404, detail="Image not found")

        # Return the image file directly
        return FileResponse(png_path, media_type="image/png")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@app.get("/get_image_base64/{folder_number}/{file_name}")
def get_image_base64(folder_number: str, file_name: str):
    """Fetch PNG image and return it as a base64 string."""
    try:
        png_path = Path(DATA_DIR) / folder_number / file_name

        # Check if the file exists
        if not png_path.exists():
            raise HTTPException(status_code=404, detail="Image not found")

        # Read the file and convert to base64
        with open(png_path, 'rb') as f:
            image_data = f.read()
            image_base64 = base64.b64encode(image_data).decode("utf-8")

        return {"image_base64": image_base64}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

# Utility endpoint to initialize the database with local data
@app.post("/init_database")
def init_database(db: Session = Depends(get_db)):
    """Initialize the database with data from local files."""
    try:
        data_dir = Path(DATA_DIR)
        folders = [f for f in data_dir.iterdir() if f.is_dir() and f.name.startswith("Folder")]

        processed_files = 0

        for folder in folders:
            folder_number = folder.name.split(" ")[1]
            png_files = [f for f in folder.iterdir() if f.is_file() and f.suffix.lower() == '.png']

            for png_file in png_files:
                file_name = png_file.name
                png_file_path = str(folder.name) + "/" + file_name

                # Check for corresponding JSON file
                json_file = png_file.with_suffix('.json')

                if json_file.exists():
                    # Read JSON data
                    with open(json_file, 'r') as f:
                        json_data = json.load(f)

                    # Read image data
                    with open(png_file, 'rb') as f:
                        image_data = f.read()

                    # Store in database
                    db_json = MoonCraterData(
                        folder_number=folder_number,
                        file_name=file_name,
                        png_file=png_file_path,
                        data=json.dumps(json_data)
                    )

                    db_image = MoonCraterImage(
                        folder_number=folder_number,
                        file_name=file_name,
                        png_file=png_file_path,
                        image_data=image_data
                    )

                    db.add(db_json)
                    db.add(db_image)
                    processed_files += 1

        db.commit()
        return {"message": f"Database initialized with {processed_files} files"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database initialization error: {str(e)}")