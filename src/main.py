from core import initialize_filesystem, sync_database, backup
from tools.catalog_generator import catalog_gen


def main():
    # Set up the folder structure if it doesn't exist
    initialize_filesystem()

    # Sync the database
    sync_database()

    # Save the initial state of the files
    backup("INITIAL_STATE")

    # Fill the catalog with fake data
    catalog_gen() 
    sync_database()

    # Back up the new data
    backup("Manual")


if __name__ == "__main__":
    main()
    