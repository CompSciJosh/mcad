# Algorithm 6

# import cv2
# import numpy as np
# import snowflake.connector
# import io
# from skimage.morphology import remove_small_objects
# from skimage.measure import label, regionprops
# from sklearn.cluster import DBSCAN
# from scipy.linalg import svd
#
#
# def fetch_image_from_snowflake(image_id, conn_params):
#     """Fetch PNG image from Snowflake as bytes and decode it."""
#     conn = snowflake.connector.connect(**conn_params)
#     cur = conn.cursor()
#     query = f"SELECT image_data FROM MCAD.MCAD_DATA.MOON_CRATER_DATA WHERE image_id = '{image_id}'"
#     cur.execute(query)
#     image_bytes = cur.fetchone()[0]
#     cur.close()
#     conn.close()
#
#     image_array = np.asarray(bytearray(image_bytes), dtype=np.uint8)
#     image = cv2.imdecode(image_array, cv2.IMREAD_GRAYSCALE)
#     return image
#
#
# def detect_contrast_regions(image):
#     """Detect bright and dark regions using adaptive thresholding and MSER."""
#     mser = cv2.MSER_create()
#     _, binary_bright = cv2.threshold(image, 200, 255, cv2.THRESH_BINARY)
#     _, binary_dark = cv2.threshold(image, 50, 255, cv2.THRESH_BINARY_INV)
#
#     bright_regions, _ = mser.detectRegions(binary_bright)
#     dark_regions, _ = mser.detectRegions(binary_dark)
#     return bright_regions, dark_regions
#
#
# def pair_bright_dark_regions(bright_regions, dark_regions):
#     """Pair bright and dark regions based on size, distance, and illumination alignment."""
#     pairs = []
#     for b in bright_regions:
#         for d in dark_regions:
#             if np.linalg.norm(np.mean(b, axis=0) - np.mean(d, axis=0)) < 50:
#                 pairs.append((b, d))
#     return pairs
#
#
# def fit_ellipse(region):
#     """Fit an ellipse using SVD."""
#     mean = np.mean(region, axis=0)
#     centered = region - mean
#     _, s, v = svd(centered)
#     axes = (2 * np.sqrt(s[0]), 2 * np.sqrt(s[1]))
#     return mean, axes
#
#
# def detect_craters(image):
#     """Full crater detection pipeline."""
#     bright_regions, dark_regions = detect_contrast_regions(image)
#     crater_candidates = pair_bright_dark_regions(bright_regions, dark_regions)
#     craters = [fit_ellipse(np.vstack([b, d])) for b, d in crater_candidates]
#     return craters
#
#
# # Example Usage
# conn_params = {
#     'user': "SNOWFLAKE_USER",
#     'password': "SNOWFLAKE_PASSWORD",
#     'account': "SNOWFLAKE_ACCOUNT"
# }
# image_id = 'image_0.png'
# image = fetch_image_from_snowflake(image_id, conn_params)
# craters = detect_craters(image)
# print(craters)

##########################
####### Algorithm 5 ######
##########################

# import cv2
# import numpy as np
# from sklearn.cluster import AgglomerativeClustering
# from skimage.measure import find_contours, EllipseModel
# import matplotlib.pyplot as plt
#
#
# def detect_craters(image_path, threshold=200, scale_factor=1.2):
#     # Load image in grayscale
#     img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
#
#     # Step 1: Filter Bright Pixels
#     _, binary = cv2.threshold(img, threshold, 255, cv2.THRESH_BINARY)
#
#     # Step 2: Cluster Bright Pixels
#     yx_coords = np.column_stack(np.where(binary == 255))
#     clustering = AgglomerativeClustering(n_clusters=None, distance_threshold=5).fit(yx_coords)
#     labels = clustering.labels_
#
#     clustered_img = np.zeros_like(img)
#     for i, label in enumerate(labels):
#         clustered_img[yx_coords[i][0], yx_coords[i][1]] = label + 1
#
#     # Step 3: Find Edges of Clusters
#     edge_map = np.zeros_like(binary)
#     for label in np.unique(labels):
#         cluster = (labels == label)
#         cluster_coords = yx_coords[cluster]
#
#         if len(cluster_coords) > 10:
#             contour = find_contours(clustered_img == label + 1, 0.5)
#             if contour:
#                 for point in contour[0]:
#                     edge_map[int(point[0]), int(point[1])] = 255
#
#     # Step 4: Determine Center and Diameter
#     detected_craters = []
#     for contour in find_contours(edge_map, 0.5):
#         if len(contour) >= 5:
#             ellipse = EllipseModel()
#             ellipse.estimate(contour)
#             yc, xc, a, b, theta = ellipse.params
#             radius = max(a, b) * scale_factor
#             detected_craters.append((xc, yc, radius))
#
#     # Plot results
#     fig, axes = plt.subplots(1, 4, figsize=(16, 4))
#     axes[0].imshow(binary, cmap='gray');
#     axes[0].set_title('Filter bright pixels')
#     axes[1].imshow(clustered_img, cmap='jet');
#     axes[1].set_title('Cluster bright pixels')
#     axes[2].imshow(edge_map, cmap='gray');
#     axes[2].set_title('Find edges of clusters')
#
#     axes[3].imshow(img, cmap='gray')
#     for xc, yc, r in detected_craters:
#         circle = plt.Circle((xc, yc), r, color='green', fill=False)
#         axes[3].add_patch(circle)
#     axes[3].set_title('Determine center and diameter')
#
#     plt.show()
#     return detected_craters
#
#
# # Example usage
# detected_craters = detect_craters("example_crater_image.png")

#################################
########## Algorithm 5 ##########
#### Outputs the following: #####
### 1. Filtered Bright Pixels ###
### 2. Clustered Bright Pixels ##
### 3. Edge Detection ###########
### 4. Final Crater Detection ###
#################################

import cv2
import numpy as np
import matplotlib.pyplot as plt
from scipy.spatial import distance
from sklearn.cluster import AgglomerativeClustering


def display_and_save(image, title, step):
    """ Display and save the intermediate step image """
    plt.imshow(image, cmap='gray')
    plt.title(title)
    plt.axis('off')
    plt.show()
    cv2.imwrite(f"crater_detection_step_{step}.png", image)


def detect_craters(image_path):
    # Load image
    image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)

    # Step 1: Filter bright pixels
    _, bright_regions = cv2.threshold(image, 200, 255, cv2.THRESH_BINARY)
    display_and_save(bright_regions, "Filtered Bright Pixels", 1)

    # Step 2: Cluster bright pixels
    bright_pixels = np.column_stack(np.where(bright_regions > 0))
    if len(bright_pixels) > 1:
        clustering = AgglomerativeClustering(n_clusters=None, distance_threshold=10).fit(bright_pixels)
        clustered_image = np.zeros_like(image)
        for i, label in enumerate(clustering.labels_):
            clustered_image[bright_pixels[i][0], bright_pixels[i][1]] = 255
        display_and_save(clustered_image, "Clustered Bright Pixels", 2)

    # Step 3: Find edges of clusters
    edges = cv2.Canny(clustered_image, 50, 150)
    display_and_save(edges, "Edges of Clusters", 3)

    # Step 4: Fit ellipse and determine crater center and diameter
    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    final_image = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)

    for contour in contours:
        if len(contour) >= 5:  # Minimum points required to fit an ellipse
            ellipse = cv2.fitEllipse(contour)
            cv2.ellipse(final_image, ellipse, (0, 255, 0), 2)
            center, axes, angle = ellipse
            cv2.circle(final_image, tuple(map(int, center)), 2, (0, 255, 0), -1)

    display_and_save(final_image, "Final Crater Detection", 4)


# Example usage
detect_craters("your_image.png")  # Replace with actual image
# detect_craters("/path/to/your/image.png") # Replace with actual image path

