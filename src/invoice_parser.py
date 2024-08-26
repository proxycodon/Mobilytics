import re
from datetime import datetime


def parse_invoice(invoice_text):
    result = {}

    try:
        # Extract invoice number and date
        invoice_number_match = re.search(r'Rechnungsnr\.:\s*(\d+)', invoice_text)
        invoice_date_match = re.search(r'Rechnungsdatum:\s*(\d{2}\.\d{2}\.\d{4})', invoice_text)

        if invoice_number_match and invoice_date_match:
            result['invoice_number'] = invoice_number_match.group(1)
            result['invoice_date'] = invoice_date_match.group(1)
            print(f"Found invoice number: {result['invoice_number']}")
            print(f"Found invoice date: {result['invoice_date']}")
        else:
            print("Could not find invoice number or date")

        # Check if this is a reservation extension
        reservation_match = re.search(r'Reservierungsverlängerung', invoice_text)
        if reservation_match:
            result['type'] = 'reservation_extension'
            amount_match = re.search(r'Gesamtbetrag\s+[\d,]+\s+[\d,]+\s+([\d,]+)', invoice_text)
            if amount_match:
                result['total_amount'] = float(amount_match.group(1).replace(',', '.'))
                print(f"Found reservation extension amount: {result['total_amount']}")
            return result

        # If not a reservation, proceed with normal trip parsing
        result['type'] = 'trip'

        # Extract trip details
        trip_pattern = r'(\d{2}\.\d{2}\.\d{2})\s+(\d{2}:\d{2})\s+(\d+,\d+)\s+(.*?)\s+(.*?)\s+Lat/Lon:\s*([\d.,]+)\s+(.*?)\s+Lat/Lon:\s*([\d.,]+)\s+(\d{2}:\d{2})\s+(.*)'
        trip_match = re.search(trip_pattern, invoice_text, re.DOTALL)

        if trip_match:
            result['date'] = trip_match.group(1)
            result['start_time'] = trip_match.group(2)
            result['end_time'] = trip_match.group(9)
            result['distance'] = float(trip_match.group(3).replace(',', '.'))
            result['vehicle'] = trip_match.group(4)
            result['start_location'] = trip_match.group(5)
            result['start_coordinates'] = trip_match.group(6)
            result['end_location'] = trip_match.group(7)
            result['end_coordinates'] = trip_match.group(8)
            result['license_plate'] = trip_match.group(10)

            print(f"Found trip details: date={result['date']}, vehicle={result['vehicle']}, distance={result['distance']} km")

            # Calculate trip duration
            start_time = datetime.strptime(result['start_time'], '%H:%M')
            end_time = datetime.strptime(result['end_time'], '%H:%M')
            duration = (end_time - start_time).total_seconds() / 60
            result['duration'] = duration
            print(f"Calculated duration: {duration} minutes")
        else:
            print("Could not extract trip details.")

        # Extract total amount
        total_amount_match = re.search(r'Gesamtbetrag\s+[\d,]+\s+[\d,]+\s+([\d,]+)', invoice_text)
        if total_amount_match:
            result['total_amount'] = float(total_amount_match.group(1).replace(',', '.'))
            print(f"Found total amount: {result['total_amount']}")

        return result

    except Exception as e:
        print(f"Error parsing invoice: {str(e)}")
        return None
