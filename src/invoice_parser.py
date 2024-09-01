import re
from datetime import datetime, timedelta


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
            return None

        # Check for SHARE NOW Pass purchase
        share_now_pass_match = re.search(r'SHARE NOW Pass\d+\s+(\d{2}\.\d{2}\.\d{2})\s+-\s+(\d{2}\.\d{2}\.\d{2})',
                                         invoice_text)
        if share_now_pass_match:
            result['type'] = 'share_now_pass'
            result['period_start'] = share_now_pass_match.group(1)
            result['period_end'] = share_now_pass_match.group(2)
            print(f"Found SHARE NOW Pass period: {result['period_start']} to {result['period_end']}")

            # Extract gross amount (Brutto)
            amount_match = re.search(r'Gesamtbetrag\s+[\d,]+\s+[\d,]+\s+([\d,]+)', invoice_text)
            if amount_match:
                result['total_amount'] = float(amount_match.group(1).replace(',', '.'))
                print(f"Found SHARE NOW Pass gross amount: {result['total_amount']}")
            return result

        # Check for processing fee
        if "SHARE NOW Bearbeitungspauschale" in invoice_text:
            result['type'] = 'processing_fee'
            # Extract gross amount (Brutto)
            amount_match = re.search(r'Gesamtbetrag\s+[\d,]+\s+[\d,]+\s+([\d,]+)', invoice_text)
            if amount_match:
                result['total_amount'] = float(amount_match.group(1).replace(',', '.'))
                print(f"Found processing fee gross amount: {result['total_amount']}")
            # Extract description or details
            description_match = re.search(
                r'SHARE NOW Bearbeitungspauschale für (.*?) - Deine Fahrt vom (\d{2}\.\d{2}\.\d{4}), (.*?) -',
                invoice_text)
            if description_match:
                result['description'] = description_match.group(1)
                result['date_of_offense'] = description_match.group(2)
                result['license_plate'] = description_match.group(3)
                print(
                    f"Found processing fee details: {result['description']}, date of offense: {result['date_of_offense']}, license plate: {result['license_plate']}")
            return result

        # Check for reservation types and group them together as 'reservation'
        if "Mehrfachreservierung" in invoice_text or "Reservierungsverlängerung" in invoice_text:
            result['type'] = 'reservation'
            # Extract gross amount (Brutto)
            amount_match = re.search(r'Gesamtbetrag\s+[\d,]+\s+[\d,]+\s+([\d,]+)', invoice_text)
            if amount_match:
                result['total_amount'] = float(amount_match.group(1).replace(',', '.'))
                print(f"Found reservation gross amount: {result['total_amount']}")
            return result

        # If it's a trip, continue extracting trip details
        result['type'] = 'trip'
        trip_pattern = (
            r'(?P<date>\d{2}\.\d{2}\.\d{2})\s+'
            r'(?P<start_time>\d{2}:\d{2})\s+'
            r'(?P<distance>[\d,]+)\s+'
            r'(?P<vehicle>.*?)\s+'
            r'(?P<start_location>.*?)\s+'
            r'(?P<end_location>.*?)\s+'
            r'(?P<end_time>\d{2}:\d{2})\s+'
            r'(?P<license_plate>[A-Z]{1,2}-[A-Z0-9]{1,4})'
        )
        trip_match = re.search(trip_pattern, invoice_text, re.DOTALL)

        if trip_match:
            result['date'] = trip_match.group('date')
            result['start_time'] = trip_match.group('start_time')
            result['end_time'] = trip_match.group('end_time')
            result['distance'] = float(trip_match.group('distance').replace(',', '.'))

            # Capture the vehicle information more accurately
            vehicle_info = trip_match.group('vehicle').replace('\n', ' ').strip()
            vehicle_parts = vehicle_info.split()
            if len(vehicle_parts) >= 2:
                result['vehicle'] = vehicle_parts[0] + ' ' + vehicle_parts[1]
            else:
                result['vehicle'] = vehicle_info

            result['start_location'] = trip_match.group('start_location').strip()
            result['end_location'] = trip_match.group('end_location').strip()
            result['license_plate'] = trip_match.group('license_plate')

            print(
                f"Found trip details: date={result['date']}, vehicle={result['vehicle']}, distance={result['distance']} km")

            # Calculate trip duration with date handling
            start_time = datetime.strptime(result['date'] + " " + result['start_time'], '%d.%m.%y %H:%M')
            end_time = datetime.strptime(result['date'] + " " + result['end_time'], '%d.%m.%y %H:%M')

            # If end_time is earlier in the day than start_time, it means the trip went past midnight
            if end_time < start_time:
                end_time += timedelta(days=1)

            duration = (end_time - start_time).total_seconds() / 60
            result['duration'] = duration
            print(f"Calculated duration: {duration} minutes")

            # Check if SHARE NOW Pass discount was applied
            if "SHARE NOW Pass" in invoice_text:
                result['share_now_pass_applied'] = True
                print("SHARE NOW Pass discount applied to this trip")
            else:
                result['share_now_pass_applied'] = False

        else:
            print("Could not extract trip details.")
            return None

        # Extract gross amount for trips
        total_amount_match = re.search(r'Gesamtbetrag\s+[\d,]+\s+[\d,]+\s+([\d,]+)', invoice_text)
        if total_amount_match:
            result['total_amount'] = float(total_amount_match.group(1).replace(',', '.'))
            print(f"Found gross amount: {result['total_amount']}")

        return result

    except Exception as e:
        print(f"Error parsing invoice: {str(e)}")
        return None