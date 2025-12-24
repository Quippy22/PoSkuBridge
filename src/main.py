from core.setup import initialize_filesystem, sync_database

def main():
    # Set up the folder structure if it doesn't exist
    initialize_filesystem()

    # Sync the database
    sync_database()

if __name__ == "__main__":
    main()
    