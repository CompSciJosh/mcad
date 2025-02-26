"""
Joshua Jackson
February 23, 2025

This script computes the camera's altitude (distance from the lunar surface) using the distance formula and subtracting the Moon’s radius.
It computes the real-world width and height of the area captured in the image.
Also, this script defines a function to convert crater size from pixels to meters.
If a crater spans 50 pixels, it calculates its real-world size in meters.
"""
import numpy as np

MOON_RADIUS = 1737400  # meters

def compute_camera_altitude(cam_pos):
    """Compute camera altitude above the lunar surface."""
    distance_from_center = np.linalg.norm(cam_pos)
    return distance_from_center - MOON_RADIUS

def compute_image_dimensions(altitude, fov_x, fov_y):
    """Compute the width and height of the lunar surface captured in the image."""
    image_width_m = 2 * altitude * np.tan(fov_x / 2)
    image_height_m = 2 * altitude * np.tan(fov_y / 2)
    return image_width_m, image_height_m

def crater_diameter_meters(pixel_diameter, image_width_m, image_width_px):
    """Calculate crater diameter in meters from pixel size."""
    return pixel_diameter * (image_width_m / image_width_px)

"""
Note: "def compute_camera_altitude(cam_pos)", 
"def compute_image_dimensions(altitude, fov_x, fov_y)", 
and "def crater_diameter_meters(pixel_diameter, image_width_m, image_width_px)" 
are stored in the Python file "crater_calculations.py" located at ~/PycharmProjects/mcad/backend/utils
"""