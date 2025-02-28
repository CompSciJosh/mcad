# import sys
# import requests
# from PyQt6.QtWidgets import QApplication, QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QMessageBox, QHBoxLayout
# from PyQt6.QtGui import QPixmap
#
# API_URL = "http://127.0.0.1:8000/compute_crater_size/"  # FastAPI endpoint
#
#
# class CraterGUI(QWidget):
#     def __init__(self):
#         super().__init__()
#
#         # Initialize UI components as instance attributes inside __init__
#         self.setWindowTitle("MCAD GUI")
#         self.setGeometry(100, 100, 600, 500)
#
#         # Set up layout (main vertical layout)
#         main_layout = QVBoxLayout()
#
#         # NASA Logo
#         self.nasa_logo = QLabel(self)
#         pixmap = QPixmap("nasa_logo.png")  # Load the image file
#         self.nasa_logo.setPixmap(pixmap)
#         self.nasa_logo.setScaledContents(True)  # Scale the image to fit the label
#         self.nasa_logo.setFixedSize(150, 150)  # Decide if this size is okay for me
#
#         # Center the NASA logo using QHBoxLayout
#         logo_layout = QHBoxLayout()
#         logo_layout.addStretch()  # Push logo to the center
#         logo_layout.addWidget(self.nasa_logo)
#         logo_layout.addStretch()  # Push logo to the center
#
#         # Add the logo layout to the main layout
#         main_layout.addLayout(logo_layout)
#
#         # First Pair of Labels and Input Fields
#         self.cam_pos_label = QLabel("Camera Position (x, y, z):")
#         self.cam_pos_input = QLineEdit()
#         self.cam_pos_input.setPlaceholderText("e.g., 1890303.16, 1971386.84, 2396504.62")
#
#         # Second Pair of Labels and Input Fields
#         self.pixel_diameter_label = QLabel("Crater Pixel Diameter:")
#         self.pixel_diameter_input = QLineEdit()
#         self.pixel_diameter_input.setPlaceholderText("e.g., 50")
#
#         # Compute Button
#         self.compute_button = QPushButton("Compute Crater Size")
#         self.compute_button.clicked.connect(self.compute_crater_size)
#
#         # Result Label
#         self.result_label = QLabel("Results will be displayed here")
#
#         # Add widgets to main layout
#         main_layout.addWidget(self.cam_pos_label)
#         main_layout.addWidget(self.cam_pos_input)
#         main_layout.addWidget(self.pixel_diameter_label)
#         main_layout.addWidget(self.pixel_diameter_input)
#         main_layout.addWidget(self.compute_button)
#         main_layout.addWidget(self.result_label)
#
#         self.setLayout(main_layout)
#
#     def compute_crater_size(self):
#         try:
#             # Validate and parse inputs
#             cam_pos_text = self.cam_pos_input.text().strip()
#             pixel_diameter_text = self.pixel_diameter_input.text().strip()
#
#             if not cam_pos_text or not pixel_diameter_text:
#                 raise ValueError("All fields must be filled in.")
#
#             cam_pos = list(map(float, cam_pos_text.split(",")))
#             pixel_diameter = int(pixel_diameter_text)
#
#             if len(cam_pos) != 3:
#                 raise ValueError("Camera position must have exactly three values (x, y, z).")
#
#             if pixel_diameter <= 0:
#                 raise ValueError("Crater pixel diameter must be a positive integer.")
#
#             # Prepare data for the API request
#             data = {"cam_pos": cam_pos, "pixel_diameter": pixel_diameter}
#             response = requests.post(API_URL, json=data)
#
#             # Handle API response
#             if response.status_code == 200:
#                 result = response.json()
#
#                 # Convert meters to miles
#                 altitude_m = result['camera_altitude_m']
#                 altitude_miles = altitude_m * 0.000621371
#
#                 # Convert meters to miles
#                 image_width_m = result['image_width_m']
#                 image_width_miles = image_width_m * 0.000621371
#
#                 # Convert meters to miles
#                 crater_diameter_m = result['crater_diameter_m']
#                 crater_diameter_miles = crater_diameter_m * 0.000621371
#
#                 # Display the calculations in both meters and miles
#                 self.result_label.setText(
#                     f"Altitude: {altitude_m:.2f} m ({altitude_miles:.4f} mi)\n"
#                     f"Image Width: {image_width_m:.2f} m ({image_width_miles:.4f} mi)\n"
#                     f"Crater Diameter: {crater_diameter_m:.2f} m ({crater_diameter_miles:.4f} mi)"
#                 )
#             else:
#                 QMessageBox.critical(self, "Error", f"Failed to compute crater size.\nServer Response: {response.text}")
#
#         except ValueError as ve:
#             QMessageBox.warning(self, "Input Error", str(ve))
#         except Exception as e:
#             QMessageBox.critical(self, "Error", f"Unexpected error: {str(e)}")
#
#
# if __name__ == "__main__":
#     app = QApplication(sys.argv)
#     window = CraterGUI()
#     window.show()
#     sys.exit(app.exec())

#####################################################################
############################ Updated GUI ############################
#####################################################################

import sys
import requests
import base64
from PyQt6.QtWidgets import (QApplication, QWidget, QLabel, QPushButton, QVBoxLayout,
                             QComboBox, QHBoxLayout, QLineEdit, QMessageBox)
from PyQt6.QtGui import QPixmap

API_URL = "http://127.0.0.1:8000/compute_crater_size/"  # FastAPI endpoint


class MCAD_GUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("MCAD GUI")
        self.setGeometry(100, 100, 600, 600)

        # NASA Logo
        self.nasa_logo = QLabel(self)
        pixmap = QPixmap("nasa_logo.png")
        self.nasa_logo.setPixmap(pixmap)
        self.nasa_logo.setFixedSize(pixmap.width(), pixmap.height())

        # Dropdown for selecting folder
        self.folder_combo = QComboBox(self)
        self.folder_combo.addItems([str(i).zfill(3) for i in range(276)])

        # Dropdown for selecting PNG file
        self.png_combo = QComboBox(self)

        # Load PNG files button
        self.load_png_btn = QPushButton("Load PNG Files", self)
        self.load_png_btn.clicked.connect(self.load_png_files)

        # Load Image button
        self.load_img_btn = QPushButton("Load Image", self)
        self.load_img_btn.clicked.connect(self.load_image)

        # Image display label
        self.image_label = QLabel(self)
        self.image_label.setFixedSize(400, 400)

        # Input fields for crater size computation
        self.cam_pos_label = QLabel("Camera Position (x, y, z):")
        self.cam_pos_input = QLineEdit()
        self.cam_pos_input.setPlaceholderText("e.g., 1890303.16, 1971386.84, 2396504.62")

        self.pixel_diameter_label = QLabel("Crater Pixel Diameter:")
        self.pixel_diameter_input = QLineEdit()
        self.pixel_diameter_input.setPlaceholderText("e.g., 50")

        # Compute crater size button
        self.compute_button = QPushButton("Compute Crater Size")
        self.compute_button.clicked.connect(self.compute_crater_size)

        # Result Label
        self.result_label = QLabel("Results will be displayed here")

        # Layout
        hbox = QHBoxLayout()
        hbox.addWidget(self.folder_combo)
        hbox.addWidget(self.load_png_btn)

        hbox2 = QHBoxLayout()
        hbox2.addWidget(self.png_combo)
        hbox2.addWidget(self.load_img_btn)

        vbox = QVBoxLayout()
        vbox.addWidget(self.nasa_logo)
        vbox.addLayout(hbox)
        vbox.addLayout(hbox2)
        vbox.addWidget(self.image_label)
        vbox.addWidget(self.cam_pos_label)
        vbox.addWidget(self.cam_pos_input)
        vbox.addWidget(self.pixel_diameter_label)
        vbox.addWidget(self.pixel_diameter_input)
        vbox.addWidget(self.compute_button)
        vbox.addWidget(self.result_label)

        self.setLayout(vbox)

    def load_png_files(self):
        folder_number = self.folder_combo.currentText()
        url = f"http://127.0.0.1:8000/list_png_files/{folder_number}"
        response = requests.get(url)

        if response.status_code == 200:
            png_files = response.json().get("png_files", [])
            self.png_combo.clear()
            self.png_combo.addItems(png_files)
        else:
            print("Error fetching PNG files")

    def load_image(self):
        folder_number = self.folder_combo.currentText()
        file_name = self.png_combo.currentText()
        if not file_name:
            print("No file selected")
            return

        url = f"http://127.0.0.1:8000/get_png/{folder_number}/{file_name}"
        response = requests.get(url)

        if response.status_code == 200:
            image_base64 = response.json().get("image_base64", "")
            image_data = base64.b64decode(image_base64)
            pixmap = QPixmap()
            pixmap.loadFromData(image_data)
            self.image_label.setPixmap(pixmap)
        else:
            print("Error fetching image")

    def compute_crater_size(self):
        try:
            cam_pos_text = self.cam_pos_input.text().strip()
            pixel_diameter_text = self.pixel_diameter_input.text().strip()

            if not cam_pos_text or not pixel_diameter_text:
                raise ValueError("All fields must be filled in.")

            cam_pos = list(map(float, cam_pos_text.split(",")))
            pixel_diameter = int(pixel_diameter_text)

            if len(cam_pos) != 3:
                raise ValueError("Camera position must have exactly three values (x, y, z).")

            if pixel_diameter <= 0:
                raise ValueError("Crater pixel diameter must be a positive integer.")

            data = {"cam_pos": cam_pos, "pixel_diameter": pixel_diameter}
            response = requests.post(API_URL, json=data)

            if response.status_code == 200:
                result = response.json()

                altitude_m = result['camera_altitude_m']
                altitude_miles = altitude_m * 0.000621371

                image_width_m = result['image_width_m']
                image_width_miles = image_width_m * 0.000621371

                crater_diameter_m = result['crater_diameter_m']
                crater_diameter_miles = crater_diameter_m * 0.000621371

                self.result_label.setText(
                    f"Altitude: {altitude_m:.2f} m ({altitude_miles:.4f} mi)\n"
                    f"Image Width: {image_width_m:.2f} m ({image_width_miles:.4f} mi)\n"
                    f"Crater Diameter: {crater_diameter_m:.2f} m ({crater_diameter_miles:.4f} mi)"
                )
            else:
                QMessageBox.critical(self, "Error", f"Failed to compute crater size.\nServer Response: {response.text}")
        except ValueError as ve:
            QMessageBox.warning(self, "Input Error", str(ve))
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Unexpected error: {str(e)}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MCAD_GUI()
    window.show()
    sys.exit(app.exec())



