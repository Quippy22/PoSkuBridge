from core import initialize_filesystem, sync_database, backup
from tools import  nuke_environment, catalog_gen, pdf


def main():
    # For testng, wipe all the files before starting
    nuke_environment()
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

    pdf.generate_pdf()
    pdf.print_po_table()


if __name__ == "__main__":
    main()
    