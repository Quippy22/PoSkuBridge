from core import initialize_filesystem, sync_database, backup


def main():
    # Set up the folder structure if it doesn't exist
    initialize_filesystem()

    # Sync the database
    sync_database()

    # Save the initial state of the files
    backup("INITIAL_STATE")


if __name__ == "__main__":
    main()
    