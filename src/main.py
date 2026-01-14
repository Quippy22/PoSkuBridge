from core.backup import backup
from core.logger import log
from core.pdf_parser import PdfParser
from core.setup import initialize_database, initialize_filesystem

# Development tools
from tools.po_generator import PoGenerator
from tools.wipe_data import nuke_environment


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

    while log.has_messages():
        print(log.get_next_message())


if __name__ == "__main__":
    main()
