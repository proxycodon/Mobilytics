import os
import pdfplumber
from src.invoice_parser import parse_invoice
from src.database_manager import save_trip_data


def main():
    invoice_dir = 'data/invoices'

    for filename in os.listdir(invoice_dir):
        if filename.endswith('.pdf'):
            file_path = os.path.join(invoice_dir, filename)
            print(f"Processing file: {filename}")

            with pdfplumber.open(file_path) as pdf:
                invoice_text = "\n".join([page.extract_text() for page in pdf.pages])

                trip_data = parse_invoice(invoice_text)

                if trip_data:
                    save_trip_data(trip_data)
                else:
                    print(f"No data extracted from {filename}.")


if __name__ == "__main__":
    main()