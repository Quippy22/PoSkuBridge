from core import backup, initialize_database, initialize_filesystem, PdfParser
# Development tools
from tools import PoGenerator, catalog_gen, nuke_environment


def main():
    # For testng, wipe all the files before starting
    nuke_environment()

    # Set up the folder structure if it doesn't exist
    initialize_filesystem()
    # Set up the database if it doesn't exist
    initialize_database()

    # Save the initial state of the files
    backup("initial state")

    pogen = PoGenerator()
    pogen.generate_pdf()
    pogen.print_po_table()

    parser = PdfParser()
    supplier, items = parser.run(pogen.po_num)
    print(f"Supplier: {supplier}")
    print(items)
    


if __name__ == "__main__":
    main()
