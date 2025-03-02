from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QFontDatabase

app = QApplication([])  # Initialize a QApplication instance

fonts = QFontDatabase.families()  # Get available fonts
print(fonts)

app.quit()  # Exit the application


