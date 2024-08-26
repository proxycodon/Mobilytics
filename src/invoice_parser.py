import re
from datetime import datetime


def parse_invoice(invoice_text):
    print("Parsing invoice text:")
    print(invoice_text[:500] + "...")  # Print first 500 characters for debugging

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

        # Extract trip details
        date_match = re.search(r'(\d{2}\.\d{2}\.)(\d{2})', invoice_text)
        time_matches = re.findall(r'(\d{2}:\d{2})', invoice_text)
        distance_match = re.search(r'(\d+,\d+)', invoice_text)
        vehicle_match = re.search(r'(\w+(?:\s+\w+)*)\s+(?=Essener Bogen|Lat/Lon)', invoice_text)
        location_matches = re.findall(r'(\w+(?:\s+\w+)*\s+\d+,\s+\d+\s+\w+)', invoice_text)
        coordinates_matches = re.findall(r'Lat/Lon:\s*([\d.,]+)', invoice_text)
        license_plate_match = re.search(r'([A-Z]{2}-[A-Z0-9]+)', invoice_text)
        total_amount_match = re.search(r'Gesamtbetrag\s+[\d,]+\s+[\d,]+\s+([\d,]+)', invoice_text)

        if date_match:
            # Correct the year to match the invoice date
            invoice_year = result['invoice_date'][-2:]  # Get last two digits of invoice year
            result['date'] = f"{date_match.group(1)}{invoice_year}"
            print(f"Found date: {result['date']}")

        if len(time_matches) >= 2:
            result['start_time'] = time_matches[0]
            result['end_time'] = time_matches[1]
            print(f"Found start time: {result['start_time']}")
            print(f"Found end time: {result['end_time']}")

        if distance_match:
            result['distance'] = float(distance_match.group(1).replace(',', '.'))
            print(f"Found distance: {result['distance']}")

        if vehicle_match:
            result['vehicle'] = vehicle_match.group(1).strip()
            print(f"Found vehicle: {result['vehicle']}")
        else:
            print("Could not find vehicle information")

        if len(location_matches) >= 2:
            result['start_location'] = location_matches[0]
            result['end_location'] = location_matches[1]
            print(f"Found start location: {result['start_location']}")
            print(f"Found end location: {result['end_location']}")

        if len(coordinates_matches) >= 2:
            result['start_coordinates'] = coordinates_matches[0]
            result['end_coordinates'] = coordinates_matches[1]
            print(f"Found start coordinates: {result['start_coordinates']}")
            print(f"Found end coordinates: {result['end_coordinates']}")

        if license_plate_match:
            result['license_plate'] = license_plate_match.group(1)
            print(f"Found license plate: {result['license_plate']}")

        if total_amount_match:
            result['total_amount'] = float(total_amount_match.group(1).replace(',', '.'))
            print(f"Found total amount: {result['total_amount']}")

        if 'start_time' in result and 'end_time' in result:
            start_time = datetime.strptime(result['start_time'], '%H:%M')
            end_time = datetime.strptime(result['end_time'], '%H:%M')
            duration = (end_time - start_time).total_seconds() / 60
            result['duration'] = duration
            print(f"Calculated duration: {duration} minutes")

        return result

    except Exception as e:
        print(f"Error parsing invoice: {str(e)}")
        return result