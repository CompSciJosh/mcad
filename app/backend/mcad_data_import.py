from mcad_database_setup import MCADDatabase
import time


def main():
    # Initialize database
    print("Initializing MCAD database...")
    db = MCADDatabase()

    # Import all data
    print("Starting import of MCAD lunar data...")
    start_time = time.time()
    db.import_mcad_data()
    end_time = time.time()

    print(f"Import completed in {end_time - start_time:.2f} seconds")

    # Test a query
    print("\nTesting database queries:")

    # Get a sample image
    sample = db.get_image_data(0, 0)  # Folder 000, image_0
    if sample:
        print(f"Found image: Folder 000, Image 0")
        print(f"Resolution: {sample[11]} rows x {sample[12]} columns")
        print(f"PNG path: {sample[1]}")
    else:
        print("Sample image not found")

    # Search by FOV criteria
    print("\nSearching for images with specific FOV range:")
    results = db.search_images_by_criteria(min_fov=0.34, max_fov=0.36, limit=5)
    for result in results:
        folder, image, path, fov_x, fov_y = result
        print(f"Folder {folder:03d}, Image {image}: FOV = {fov_x:.4f} x {fov_y:.4f}")

    # Close database
    db.close()
    print("\nDatabase connection closed")


if __name__ == "__main__":
    main()