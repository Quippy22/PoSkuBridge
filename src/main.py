from core import backup, initialize_filesystem, parser, sync_database
from tools import PoGenerator, catalog_gen, nuke_environment


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

    pdf = PoGenerator()
    pdf.generate_pdf()
    pdf.print_po_table()

    parser.run(pdf.po_num + ".pdf")
    print(parser.po_table)


if __name__ == "__main__":
    main()
