import sys
import json
import requests
import base64
from PyQt6.QtWidgets import (QApplication, QWidget, QLabel, QPushButton, QVBoxLayout,
                             QComboBox, QHBoxLayout, QLineEdit, QMessageBox,
                             QTextEdit, QTabWidget, QScrollArea, QSplitter, QSizePolicy)
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt

API_URL = "http://127.0.0.1:8000/compute_crater_size/"  # FastAPI endpoint


class MCAD_GUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("MCAD (Lunar Crater Analysis Tool)")
        self.setGeometry(100, 100, 1000, 800)  # Increased width for the new layout

        # Main horizontal layout to split left and right sides
        main_layout = QHBoxLayout(self)

        # Left side layout (logo, image, and results)
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)

        # NASA Logo Container with fixed width and left alignment
        logo_container = QWidget()
        logo_layout = QHBoxLayout(logo_container)
        logo_layout.setContentsMargins(0, 0, 0, 0)  # Remove padding

        # NASA Logo with fixed size
        self.nasa_logo = QLabel()
        try:
            pixmap = QPixmap("nasa_logo.png")
            scaled_pixmap = pixmap.scaled(150, 150, Qt.AspectRatioMode.KeepAspectRatio,
                                          Qt.TransformationMode.SmoothTransformation)
            self.nasa_logo.setPixmap(scaled_pixmap)
            self.nasa_logo.setFixedSize(150, 150)
            self.nasa_logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        except Exception as e:
            print(f"Error loading NASA logo: {e}")
            # Create a placeholder if logo can't be loaded
            self.nasa_logo.setText("NASA")
            self.nasa_logo.setStyleSheet("font-weight: bold; font-size: 24px;")
            self.nasa_logo.setFixedSize(150, 150)
            self.nasa_logo.setAlignment(Qt.AlignmentFlag.AlignCenter)

        logo_layout.addWidget(self.nasa_logo)
        logo_layout.addStretch()  # Push logo to the left
        left_layout.addWidget(logo_container)

        # Image container with flexible size policy
        self.image_container = QWidget()
        self.image_container.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        image_container_layout = QVBoxLayout(self.image_container)

        # Image display label
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_label.setStyleSheet("font-family: Chalkboard; background-color: #2E3192; font-size: 20px; border: 5px solid #2E3192;")
        self.image_label.setText("No image loaded")
        self.image_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        image_container_layout.addWidget(self.image_label)
        left_layout.addWidget(self.image_container, 1)  # Give it more stretch factor

        # Results section - now on the left under the image
        results_container = QWidget()
        results_layout = QVBoxLayout(results_container)

        results_title = QLabel("Analysis Results:")
        self.result_label = QLabel("Results will be displayed here")
        self.result_label.setWordWrap(True)
        self.result_label.setStyleSheet("font-family: Chalkboard; font-size: 16px; background-color: #2E3192; color: white; padding: 10px; border-radius: 5px;")

        results_layout.addWidget(results_title)
        results_layout.addWidget(self.result_label)

        left_layout.addWidget(results_container)

        # Right side with tabs - make it narrower
        right_panel = QWidget()
        right_panel.setMaximumWidth(400)  # Limit the width of the right panel
        right_layout = QVBoxLayout(right_panel)

        # Create tab widget for the right side
        self.tab_widget = QTabWidget()

        # Create tabs
        self.image_controls_tab = QWidget()
        self.data_tab = QWidget()
        self.analysis_tab = QWidget()

        self.setup_image_controls_tab()
        self.setup_data_tab()
        self.setup_analysis_tab()

        # Add tabs to widget
        self.tab_widget.addTab(self.image_controls_tab, "Image View")
        self.tab_widget.addTab(self.data_tab, "JSON Data")
        self.tab_widget.addTab(self.analysis_tab, "Crater Analysis")

        right_layout.addWidget(self.tab_widget)

        # Add the left and right panels to the main layout
        # Use a splitter to allow resizing
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.addWidget(left_panel)
        splitter.addWidget(right_panel)
        splitter.setSizes([700, 300])  # Give more space to the left panel initially

        main_layout.addWidget(splitter)

        # Initialize current JSON data
        self.current_json_data = None
        self.current_image_data = None

    def setup_image_controls_tab(self):
        # Dropdown for selecting folder
        self.folder_combo = QComboBox()
        self.folder_combo.addItems([str(i).zfill(3) for i in range(276)])

        # Dropdown for selecting PNG file
        self.png_combo = QComboBox()

        # Load PNG files button
        self.load_png_btn = QPushButton("Load PNG Files")
        self.load_png_btn.clicked.connect(self.load_png_files)

        # Load Image button
        self.load_img_btn = QPushButton("Load Image/Data")
        self.load_img_btn.clicked.connect(self.load_image_and_data)

        # Layout
        folder_hbox = QHBoxLayout()
        folder_hbox.addWidget(QLabel("Select Folder:"))
        folder_hbox.addWidget(self.folder_combo)
        folder_hbox.addWidget(self.load_png_btn)

        png_hbox = QHBoxLayout()
        png_hbox.addWidget(QLabel("Select Image:"))
        png_hbox.addWidget(self.png_combo)
        png_hbox.addWidget(self.load_img_btn)

        vbox = QVBoxLayout()
        vbox.addLayout(folder_hbox)
        vbox.addLayout(png_hbox)
        vbox.addStretch()

        self.image_controls_tab.setLayout(vbox)

    def setup_data_tab(self):
        # JSON data display
        self.json_display = QTextEdit()
        self.json_display.setReadOnly(True)
        self.json_display.setStyleSheet("font-family: Chalkboard; font-size: 16px")

        # Layout
        vbox = QVBoxLayout()
        vbox.addWidget(QLabel("JSON Data for Selected Image:"))
        vbox.addWidget(self.json_display)

        self.data_tab.setLayout(vbox)

    def setup_analysis_tab(self):
        # Input fields for crater size computation
        self.cam_pos_label = QLabel("Camera Position (x, y, z):")
        self.cam_pos_input = QLineEdit()
        self.cam_pos_input.setPlaceholderText("e.g., 1890303.16, 1971386.84, 2396504.62")

        self.pixel_diameter_label = QLabel("Crater Pixel Diameter:")
        self.pixel_diameter_input = QLineEdit()
        self.pixel_diameter_input.setPlaceholderText("e.g., 50")

        # Auto-fill button
        self.auto_fill_btn = QPushButton("Auto-fill from JSON")
        self.auto_fill_btn.clicked.connect(self.auto_fill_from_json)

        # Compute crater size button
        self.compute_button = QPushButton("Compute Crater Size")
        self.compute_button.clicked.connect(self.compute_crater_size)

        # Layout
        vbox = QVBoxLayout()
        vbox.addWidget(self.cam_pos_label)
        vbox.addWidget(self.cam_pos_input)

        hbox_auto = QHBoxLayout()
        hbox_auto.addWidget(self.auto_fill_btn)
        vbox.addLayout(hbox_auto)

        vbox.addWidget(self.pixel_diameter_label)
        vbox.addWidget(self.pixel_diameter_input)
        vbox.addWidget(self.compute_button)
        vbox.addStretch()

        self.analysis_tab.setLayout(vbox)

    def load_png_files(self):
        folder_number = self.folder_combo.currentText()
        url = f"http://127.0.0.1:8000/list_png_files/{folder_number}"

        try:
            response = requests.get(url, timeout=10)

            # Check if response is successful and contains valid JSON
            if response.status_code == 200:
                try:
                    data = response.json()
                    png_files = data.get("png_files", [])
                    self.png_combo.clear()
                    self.png_combo.addItems(png_files)
                except json.JSONDecodeError:
                    QMessageBox.critical(self, "Error", "Invalid JSON response from server")
            else:
                QMessageBox.critical(self, "Error", f"Server error: {response.status_code}")
        except requests.exceptions.ConnectionError:
            QMessageBox.critical(self, "Connection Error", "Could not connect to the server. Is the API running?")
        except requests.exceptions.Timeout:
            QMessageBox.critical(self, "Timeout Error", "Server request timed out")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error fetching PNG files: {str(e)}")

    def load_image_and_data(self):
        folder_number = self.folder_combo.currentText()
        file_name = self.png_combo.currentText()
        if not file_name:
            QMessageBox.warning(self, "Warning", "No file selected")
            return

        # Load the image
        self.load_image(folder_number, file_name)

        # Load the corresponding JSON data
        self.load_json_data(folder_number, file_name)

    def load_image(self, folder_number, file_name):
        url = f"http://127.0.0.1:8000/get_png/{folder_number}/{file_name}"

        try:
            # Display loading message
            self.image_label.setText("Loading image...")
            QApplication.processEvents()  # Update UI

            response = requests.get(url, timeout=15)

            if response.status_code == 200:
                # Check for raw image data first (binary response)
                content_type = response.headers.get('Content-Type', '')

                if 'image' in content_type:
                    # Direct binary image data
                    image_data = response.content
                    pixmap = QPixmap()
                    pixmap.loadFromData(image_data)
                    self.current_image_data = image_data
                else:
                    # Try to parse as JSON with base64 image
                    try:
                        data = response.json()
                        image_base64 = data.get("image_base64", "")
                        image_data = base64.b64decode(image_base64)
                        pixmap = QPixmap()
                        pixmap.loadFromData(image_data)
                        self.current_image_data = image_data
                    except json.JSONDecodeError:
                        # If not JSON, try to use content directly as image
                        image_data = response.content
                        pixmap = QPixmap()
                        if pixmap.loadFromData(image_data):
                            self.current_image_data = image_data
                        else:
                            raise ValueError("Could not parse image data")

                # Calculate the available space in the image container
                container_width = self.image_container.width()
                container_height = self.image_container.height()

                # Scale the image to fit the container while maintaining aspect ratio
                scaled_pixmap = pixmap.scaled(
                    container_width,
                    container_height,
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation
                )

                # Set the pixmap and let it adjust dynamically when window is resized
                self.image_label.setPixmap(scaled_pixmap)

                # Store original pixmap for rescaling on resize
                self.original_pixmap = pixmap

                # Connect resize event if not already connected
                self.image_container.resizeEvent = self.image_container_resized
            else:
                self.image_label.setText(f"Error: {response.status_code}")
                QMessageBox.critical(self, "Error", f"Server returned status code: {response.status_code}")

        except requests.exceptions.ConnectionError:
            self.image_label.setText("Connection Error")
            QMessageBox.critical(self, "Connection Error", "Could not connect to the server. Is the API running?")
        except requests.exceptions.Timeout:
            self.image_label.setText("Request Timeout")
            QMessageBox.critical(self, "Timeout Error", "Server request timed out")
        except Exception as e:
            self.image_label.setText("Error loading image")
            QMessageBox.critical(self, "Error", f"Error fetching image: {str(e)}")

    def image_container_resized(self, event):
        """Handle resizing of the image container to scale the image properly"""
        if hasattr(self, 'original_pixmap') and not self.original_pixmap.isNull():
            # Get the container's new size
            container_width = self.image_container.width()
            container_height = self.image_container.height()

            # Scale the image to fit the container
            scaled_pixmap = self.original_pixmap.scaled(
                container_width - 20,  # Allow for margins
                container_height - 20,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )

            # Update the image label
            self.image_label.setPixmap(scaled_pixmap)

        # Make sure to call the parent class's resizeEvent
        super(QWidget, self.image_container).resizeEvent(event)

    def load_json_data(self, folder_number, file_name):
        # Convert PNG filename to JSON filename
        json_file_name = file_name.replace(".png", ".json")

        # Call API to get JSON data
        url = f"http://127.0.0.1:8000/get_json/{folder_number}/{json_file_name}"

        try:
            # Display loading message
            self.json_display.setText("Loading JSON data...")
            QApplication.processEvents()  # Update UI

            response = requests.get(url, timeout=10)

            if response.status_code == 200:
                try:
                    data = response.json()
                    json_data = data.get("json_data", {})

                    # If json_data is a string, try to parse it
                    if isinstance(json_data, str):
                        json_data = json.loads(json_data)

                    self.current_json_data = json_data

                    # Format JSON for display
                    formatted_json = json.dumps(json_data, indent=2)
                    self.json_display.setText(formatted_json)

                    # Switch to the JSON data tab
                    self.tab_widget.setCurrentIndex(1)
                except json.JSONDecodeError as e:
                    self.json_display.setText(f"Error parsing JSON: {str(e)}")
                    self.current_json_data = None
            else:
                self.json_display.setText(f"Server error: {response.status_code}")
                self.current_json_data = None

        except requests.exceptions.ConnectionError:
            self.json_display.setText("Connection Error: Could not connect to server")
            QMessageBox.critical(self, "Connection Error", "Could not connect to the server. Is the API running?")
        except requests.exceptions.Timeout:
            self.json_display.setText("Request Timeout")
            QMessageBox.critical(self, "Timeout Error", "Server request timed out")
        except Exception as e:
            self.json_display.setText(f"Error: {str(e)}")
            QMessageBox.critical(self, "Error", f"Error fetching JSON data: {str(e)}")
            self.current_json_data = None

    def auto_fill_from_json(self):
        if not self.current_json_data:
            QMessageBox.warning(self, "Warning", "No JSON data loaded")
            return

        try:
            # Get camera position from JSON
            cam_pos = self.current_json_data.get("Cam Pos (m)", "")

            # If cam_pos is a string, parse it to extract the values
            if isinstance(cam_pos, str):
                # Remove brackets if present and split by commas
                cam_pos = cam_pos.strip("[]").split(",")
                cam_pos = [value.strip() for value in cam_pos]
            elif isinstance(cam_pos, list):
                # Already a list, just ensure strings
                cam_pos = [str(value) for value in cam_pos]
            else:
                raise ValueError(f"Unexpected camera position format: {type(cam_pos)}")

            # Join the values with commas
            cam_pos_str = ", ".join(map(str, cam_pos))

            # Set the input field
            self.cam_pos_input.setText(cam_pos_str)

            # Switch to the analysis tab
            self.tab_widget.setCurrentIndex(2)
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Could not extract camera position: {str(e)}")

    def compute_crater_size(self):
        try:
            cam_pos_text = self.cam_pos_input.text().strip()
            pixel_diameter_text = self.pixel_diameter_input.text().strip()

            if not cam_pos_text or not pixel_diameter_text:
                raise ValueError("All fields must be filled in.")

            # Handle various formats of cam_pos input
            try:
                # Try to handle format with brackets like [x, y, z]
                if cam_pos_text.startswith('[') and cam_pos_text.endswith(']'):
                    cam_pos_text = cam_pos_text[1:-1]

                # Split by comma and convert to float
                cam_pos = [float(x.strip()) for x in cam_pos_text.split(',')]
            except Exception:
                raise ValueError("Invalid camera position format. Use comma-separated values.")

            pixel_diameter = int(pixel_diameter_text)

            if len(cam_pos) != 3:
                raise ValueError("Camera position must have exactly three values (x, y, z).")

            if pixel_diameter <= 0:
                raise ValueError("Crater pixel diameter must be a positive integer.")

            data = {"cam_pos": cam_pos, "pixel_diameter": pixel_diameter}

            # Show processing message
            self.result_label.setText("Computing crater size...")
            QApplication.processEvents()  # Update UI

            response = requests.post(API_URL, json=data, timeout=15)

            if response.status_code == 200:
                try:
                    result = response.json()

                    altitude_m = result.get('camera_altitude_m', 0)
                    altitude_miles = altitude_m * 0.000621371

                    image_width_m = result.get('image_width_m', 0)
                    image_width_miles = image_width_m * 0.000621371

                    # Calculate image height (assuming it's proportional to the width)
                    if self.current_json_data:
                        try:
                            fov_x = float(self.current_json_data.get("FOV X (rad)", 0.3490658503988659))
                            fov_y = float(self.current_json_data.get("FOV Y (rad)", 0.27580511636453603))
                            image_height_m = (image_width_m / fov_x) * fov_y
                            image_height_miles = image_height_m * 0.000621371
                        except (ValueError, TypeError, ZeroDivisionError):
                            image_height_m = 0
                            image_height_miles = 0
                    else:
                        image_height_m = 0
                        image_height_miles = 0

                    crater_diameter_m = result.get('crater_diameter_m', 0)
                    crater_diameter_miles = crater_diameter_m * 0.000621371

                    self.result_label.setText(
                        f"Camera Altitude: {altitude_m:.2f} m ({altitude_miles:.4f} mi)\n\n"
                        f"Image Width: {image_width_m:.2f} m ({image_width_miles:.4f} mi)\n"
                        f"Image Height: {image_height_m:.2f} m ({image_height_miles:.4f} mi)\n\n"
                        f"Crater Diameter: {crater_diameter_m:.2f} m ({crater_diameter_miles:.4f} mi)"
                    )
                except json.JSONDecodeError:
                    self.result_label.setText("Error: Could not parse server response")
                    QMessageBox.critical(self, "Error", "Invalid response from server")
            else:
                self.result_label.setText(f"Error: Server returned status {response.status_code}")
                QMessageBox.critical(self, "Error", f"Failed to compute crater size.\nServer Response: {response.text}")

        except ValueError as ve:
            self.result_label.setText(f"Input Error: {str(ve)}")
            QMessageBox.warning(self, "Input Error", str(ve))
        except requests.exceptions.ConnectionError:
            self.result_label.setText("Connection Error")
            QMessageBox.critical(self, "Connection Error", "Could not connect to the server. Is the API running?")
        except requests.exceptions.Timeout:
            self.result_label.setText("Request Timeout")
            QMessageBox.critical(self, "Timeout Error", "Server request timed out")
        except Exception as e:
            self.result_label.setText(f"Error: {str(e)}")
            QMessageBox.critical(self, "Error", f"Unexpected error: {str(e)}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MCAD_GUI()
    window.show()
    sys.exit(app.exec())