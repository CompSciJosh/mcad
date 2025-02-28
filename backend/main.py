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
 pip install fastapi uvicorn bcrypt pyjwt python-dotenv snowflake-connector-python
 In PyCharm terminal press: Ctrl + C to stop the server
"""
#############################################
### Step 8: Implement User Authentication ###
#############################################
import re
import nltk
import jwt
import bcrypt
import os
import numpy as np
import base64
from nltk.corpus import words
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
#from fastapi.responses import JSONResponse, StreamingResponse
from pydantic import BaseModel
from datetime import datetime, timedelta, UTC  # Ensure UTC is imported
from dotenv import load_dotenv
from database import get_snowflake_connection
from utils.crater_calculations import compute_camera_altitude, compute_image_dimensions, crater_diameter_meters
from typing import List

# Load environment variables
load_dotenv()

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
            cur.execute("SELECT id FROM users WHERE LOWER(username)=%s OR email=%sc", (username_lower, user.email))
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
###########################################
################ Old Version ##############
###########################################
# @app.get("/list_png_files/{folder_number}")
# def list_png_files(folder_number: str):
#     """
#     Retrieves a list of PNG files from the specified folder in Snowflake.
#     """
#     # Validate folder input
#     if not folder_number.isdigit() or not (0 <= int(folder_number) <= 275):
#         raise HTTPException(status_code=400, detail="Invalid folder number. Must be between '000' and '275'.")
#
#     folder_number = folder_number.zfill(3)  # Ensure format "000", "001", ..., "275"
#
#     conn = get_snowflake_connection()
#     if conn:
#         try:
#             cur = conn.cursor()
#             query = f"""
#                 SELECT METADATA$FILENAME
#                 FROM DIRECTORY(@MCAD.MCAD_DATA.INTERNAL_STAGE_FOR_ORIGINAL_DATA)
#                 WHERE METADATA$FILENAME LIKE '{folder_number}/%.png'
#             """
#             cur.execute(query)
#             png_files = [row[0].split("/")[-1] for row in cur.fetchall()]
#             cur.close()
#
#             return JSONResponse(content={"png_files": png_files})
#         except Exception as e:
#             raise HTTPException(status_code=500, detail=f"Database error: {e}")
#         finally:
#             conn.close()
#     raise HTTPException(status_code=500, detail="Database connection failed")

##############################
######## New Version #########
##############################

@app.get("/list_png_files/{folder_number}")
def list_png_files(folder_number: str):
    """Fetch PNG filenames from Snowflake based on the folder number."""
    conn = get_snowflake_connection()
    if conn:
        try:
            cur = conn.cursor()

            # Query staged files for the selected folder
            query = f"""
            SELECT METADATA$FILENAME 
            FROM @MCAD/MCAD_DATA/MOON_CRATER_IMAGES 
            WHERE METADATA$FILENAME LIKE 'Folder {folder_number}/%.png'
            """
            cur.execute(query)

            # Extract filenames
            png_files = [row[0].split("/")[-1] for row in cur.fetchall()]
            cur.close()
            return {"png_files": png_files}

        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


###########################################################
####### 1st get_png script (w/o base64 or streaming) ######
###########################################################
# @app.get("/get_png/{folder_number}/{file_name}")
# def get_png(folder_number: str, file_name: str):
#     """
#     Retrieves a PNG image from Snowflake, converts it to Base64, and sends it to the frontend.
#     """
#     # Validate inputs
#     if not folder_number.isdigit() or not (0 <= int(folder_number) <= 275):
#         raise HTTPException(status_code=400, detail="Invalid folder number. Must be between '000' and '275'.")
#     if not file_name.endswith(".png"):
#         raise HTTPException(status_code=400, detail="Invalid file format. Must be a PNG file.")
#
#     folder_number = folder_number.zfill(3)
#     file_path = f'@MCAD.MCAD_DATA.INTERNAL_STAGE_FOR_ORIGINAL_DATA/{folder_number}/{file_name}'
#
#     conn = get_snowflake_connection()
#     if conn:
#         try:
#             cur = conn.cursor()
#             query = f"SELECT TO_BASE64(DATA) FROM {file_path}"
#             cur.execute(query)
#             result = cur.fetchone()
#
#             if result:
#                 image_base64 = result[0]
#                 return JSONResponse(content={"image_base64": image_base64})
#             else:
#                 raise HTTPException(status_code=404, detail="Image not found.")
#         except Exception as e:
#             raise HTTPException(status_code=500, detail=f"Database error: {e}")
#         finally:
#             conn.close()
#     raise HTTPException(status_code=500, detail="Database connection failed")

#############################################
####### 2nd get_png script (w/ base64) ######
#############################################
# @app.get("/get_png/{folder_number}/{file_name}")
# def get_png(folder_number: str, file_name: str):
#     if not folder_number.isdigit() or not (0 <= int(folder_number) <= 275):
#         raise HTTPException(status_code=400, detail="Invalid folder number. Must be between '000' and '275'.")
#     if not file_name.endswith(".png"):
#         raise HTTPException(status_code=400, detail="Invalid file format. Must be a PNG file.")
#
#     folder_number = folder_number.zfill(3)
#     file_path = f'@MCAD.MCAD_DATA.INTERNAL_STAGE_FOR_ORIGINAL_DATA/{folder_number}/{file_name}'
#
#     conn = get_snowflake_connection()
#     if conn:
#         try:
#             cur = conn.cursor()
#             query = f"SELECT DATA FROM {file_path}"
#             cur.execute(query)
#             result = cur.fetchone()
#
#             if result:
#                 image_bytes = result[0]  # Assuming this returns binary data
#                 image_base64 = base64.b64encode(image_bytes).decode("utf-8")
#                 return JSONResponse(content={"image_base64": image_base64})
#             else:
#                 raise HTTPException(status_code=404, detail="Image not found.")
#         except Exception as e:
#             raise HTTPException(status_code=500, detail=f"Database error: {e}")
#         finally:
#             conn.close()
#     raise HTTPException(status_code=500, detail="Database connection failed")

################################################
####### 3rd get_png script (w/ streaming) ######
################################################
# from fastapi.responses import StreamingResponse
# from io import BytesIO
#
# @app.get("/get_png/{folder_number}/{file_name}")
# def get_png(folder_number: str, file_name: str):
#     if not folder_number.isdigit() or not (0 <= int(folder_number) <= 275):
#         raise HTTPException(status_code=400, detail="Invalid folder number. Must be between '000' and '275'.")
#     if not file_name.endswith(".png"):
#         raise HTTPException(status_code=400, detail="Invalid file format. Must be a PNG file.")
#
#     folder_number = folder_number.zfill(3)
#     file_path = f'@MCAD.MCAD_DATA.INTERNAL_STAGE_FOR_ORIGINAL_DATA/{folder_number}/{file_name}'
#
#     conn = get_snowflake_connection()
#     if conn:
#         try:
#             cur = conn.cursor()
#             query = f"SELECT DATA FROM {file_path}"
#             cur.execute(query)
#             result = cur.fetchone()
#
#             if result:
#                 image_bytes = result[0]
#                 return StreamingResponse(BytesIO(image_bytes), media_type="image/png")
#             else:
#                 raise HTTPException(status_code=404, detail="Image not found.")
#         except Exception as e:
#             raise HTTPException(status_code=500, detail=f"Database error: {e}")
#         finally:
#             conn.close()
#     raise HTTPException(status_code=500, detail="Database connection failed")

#############################
######## 4th Version ########
#############################
@app.get("/get_png/{folder_number}/{file_name}")
def get_png(folder_number: str, file_name: str):
    """Fetch PNG image from Snowflake and return it as a base64 string."""
    conn = get_snowflake_connection()
    if conn:
        try:
            cur = conn.cursor()

            # Query to retrieve the PNG file as BLOB
            query = f"""
            SELECT GET_BINARY(PNG_IMAGE) 
            FROM MCAD.MCAD_DATA.MOON_CRATER_IMAGES
            WHERE FILE_PATH = 'Folder {folder_number}/{file_name}'
            """
            cur.execute(query)
            image_blob = cur.fetchone()

            if image_blob and image_blob[0]:
                image_base64 = base64.b64encode(image_blob[0]).decode("utf-8")
                cur.close()
                return {"image_base64": image_base64}
            else:
                raise HTTPException(status_code=404, detail="Image not found")

        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")



