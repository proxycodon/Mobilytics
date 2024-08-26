import os
import pdfplumber
from src.invoice_parser import parse_invoice
from src.database_manager import save_trip_data

def main():
    invoice_dir = 'data/invoices'
    processed_count = 0
    failed_count = 0
    failed_files = []

    for filename in os.listdir(invoice_dir):
        if filename.endswith('.pdf'):
            file_path = os.path.join(invoice_dir, filename)

            with pdfplumber.open(file_path) as pdf:
                invoice_text = "\n".join([page.extract_text() for page in pdf.pages])

                trip_data = parse_invoice(invoice_text)

                if trip_data:
                    save_trip_data(trip_data)
                    processed_count += 1
                else:
                    failed_count += 1
                    failed_files.append(filename)

    # Ausgabe in der Konsole
    print(f"Processed invoices: {processed_count}")
    print(f"Failed to process: {failed_count}")
    if failed_files:
        print("Failed files:")
        for file in failed_files:
            print(f" - {file}")

if __name__ == "__main__":
    main()
