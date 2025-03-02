"""
Joshua Jackson
March 2, 2025,
MCAD Database Setup (w/o Snowflake since I've experienced multiple obstacles).
This script contains functions such as initializing a database, creating a database and tables, import JSON
and PNG data, etc.

"""
import json
import sqlite3
from pathlib import Path


class MCADDatabase:
    def __init__(self, db_path="/Users/joshuajackson/PycharmProjects/mcad/data/database/mcad.db"):
        """Initialize the MCAD database"""
        self.db_path = Path(db_path)
        # Ensure parent directory exists
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

        self.connection = None
        self.cursor = None
        self.initialize_database()

    def initialize_database(self):
        """Create the database and tables if they don't exist"""
        self.connection = sqlite3.connect(str(self.db_path))
        self.cursor = self.connection.cursor()

        # Create tables
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS lunar_images (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            folder_num INTEGER NOT NULL,
            image_num INTEGER NOT NULL,
            png_path TEXT NOT NULL,
            json_path TEXT NOT NULL,
            time_s TEXT,
            sun_los TEXT,
            cam_pos_m TEXT,
            cam_quat_s REAL,
            cam_quat_v TEXT,
            cam_los TEXT,
            fov_x_rad REAL,
            fov_y_rad REAL,
            nrows INTEGER,
            ncols INTEGER,
            UNIQUE(folder_num, image_num)
        )
        ''')

        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS detected_craters (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            image_id INTEGER NOT NULL,
            center_x REAL NOT NULL,
            center_y REAL NOT NULL,
            diameter_pixels REAL NOT NULL,
            diameter_meters REAL NOT NULL,
            diameter_miles REAL NOT NULL,
            confidence_score REAL,
            detection_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (image_id) REFERENCES lunar_images (id)
        )
        ''')

        self.connection.commit()

    def import_mcad_data(self, base_path="/Users/joshuajackson/PycharmProjects/mcad/data/original/mcad_moon_data"):
        """Import all JSON and PNG files from the mcad_moon_data directory"""
        base_path = Path(base_path)

        # Loop through all folders (000-275)
        for folder_num in range(276):
            folder_name = f"{folder_num:03d}"
            folder_path = base_path / folder_name

            if not folder_path.exists():
                print(f"Warning: Folder {folder_name} does not exist. Skipping.")
                continue

            # Max files is 10 per folder (0-9), except folder 275 which has 7
            max_files = 7 if folder_num == 275 else 10

            # Process each image in the folder
            for image_num in range(max_files):
                json_filename = f"image_{image_num}.json"
                png_filename = f"image_{image_num}.png"

                json_path = folder_path / json_filename
                png_path = folder_path / png_filename

                # Check if both files exist
                if not json_path.exists() or not png_path.exists():
                    print(f"Warning: Missing file(s) for folder {folder_name}, image {image_num}. Skipping.")
                    continue

                # Load JSON data
                try:
                    with open(json_path, 'r') as f:
                        json_data = json.load(f)

                    # Insert record into database
                    self.cursor.execute('''
                    INSERT OR REPLACE INTO lunar_images (
                        folder_num, image_num, png_path, json_path, 
                        time_s, sun_los, cam_pos_m, cam_quat_s, cam_quat_v, 
                        cam_los, fov_x_rad, fov_y_rad, nrows, ncols
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        folder_num,
                        image_num,
                        str(png_path),
                        str(json_path),
                        json_data.get("Time (s)"),
                        str(json_data.get("SUN LoS")),
                        str(json_data.get("Cam Pos (m)")),
                        json_data.get("Cam Quat (s)"),
                        str(json_data.get("Cam Quat (v)")),
                        str(json_data.get("Cam LoS")),
                        json_data.get("FOV X (rad)"),
                        json_data.get("FOV Y (rad)"),
                        json_data.get("Nrows"),
                        json_data.get("Ncols")
                    ))

                    if (folder_num * 10 + image_num) % 100 == 0:
                        print(f"Imported {folder_num:03d}/image_{image_num}")
                        self.connection.commit()  # Commit every 100 records

                except Exception as e:
                    print(f"Error processing {json_path}: {e}")

        # Final commit
        self.connection.commit()
        print("Import complete!")

    def add_crater_detection(self, folder_num, image_num, crater_data):
        """Add crater detection results for a specific lunar image"""
        # First, get the image_id
        self.cursor.execute('''
        SELECT id FROM lunar_images 
        WHERE folder_num = ? AND image_num = ?
        ''', (folder_num, image_num))

        result = self.cursor.fetchone()
        if not result:
            raise ValueError(f"Image not found: folder {folder_num}, image {image_num}")

        image_id = result[0]

        # Add each crater
        for crater in crater_data:
            self.cursor.execute('''
            INSERT INTO detected_craters (
                image_id, center_x, center_y, diameter_pixels,
                diameter_meters, diameter_miles, confidence_score
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                image_id,
                crater['center_x'],
                crater['center_y'],
                crater['diameter_pixels'],
                crater['diameter_meters'],
                crater['diameter_miles'],
                crater.get('confidence_score')
            ))

        self.connection.commit()
        return len(crater_data)

    def get_image_data(self, folder_num, image_num):
        """Get image data and path information for a specific image"""
        self.cursor.execute('''
        SELECT id, png_path, json_path, time_s, sun_los, cam_pos_m,
               cam_quat_s, cam_quat_v, cam_los, fov_x_rad, fov_y_rad,
               nrows, ncols
        FROM lunar_images
        WHERE folder_num = ? AND image_num = ?
        ''', (folder_num, image_num))

        return self.cursor.fetchone()

    def get_craters_for_image(self, folder_num, image_num):
        """Get all detected craters for a specific image"""
        # First, get the image_id
        self.cursor.execute('''
        SELECT id FROM lunar_images 
        WHERE folder_num = ? AND image_num = ?
        ''', (folder_num, image_num))

        result = self.cursor.fetchone()
        if not result:
            return []

        image_id = result[0]

        # Get all craters for this image
        self.cursor.execute('''
        SELECT center_x, center_y, diameter_pixels, diameter_meters, 
               diameter_miles, confidence_score, detection_date
        FROM detected_craters
        WHERE image_id = ?
        ORDER BY diameter_pixels DESC
        ''', (image_id,))

        return self.cursor.fetchall()

    def search_images_by_criteria(self, min_fov=None, max_fov=None, limit=10):
        """Search for images based on criteria like field of view"""
        query = "SELECT folder_num, image_num, png_path, fov_x_rad, fov_y_rad FROM lunar_images WHERE 1=1"
        params = []

        if min_fov is not None:
            query += " AND fov_x_rad >= ?"
            params.append(min_fov)

        if max_fov is not None:
            query += " AND fov_x_rad <= ?"
            params.append(max_fov)

        query += " ORDER BY folder_num, image_num LIMIT ?"
        params.append(limit)

        self.cursor.execute(query, params)
        return self.cursor.fetchall()

    def close(self):
        """Close the database connection"""
        if self.connection:
            self.connection.close()
            self.connection = None
            self.cursor = None