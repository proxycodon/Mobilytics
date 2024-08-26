import json
from datetime import datetime, date


class JSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (date, datetime)):
            return obj.isoformat()
        return super().default(obj)


def save_trip_data(trip_data, filename='carsharing_data.json'):
    try:
        with open(filename, 'r') as f:
            data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        data = []

    # Check if the invoice number already exists
    invoice_numbers = [item.get('invoice_number') for item in data]
    if trip_data.get('invoice_number') in invoice_numbers:
        print(f"Invoice {trip_data.get('invoice_number')} already exists. Skipping.")
        return

    data.append(trip_data)

    with open(filename, 'w') as f:
        json.dump(data, f, cls=JSONEncoder, indent=4)

    print(f"Data for invoice {trip_data.get('invoice_number')} added successfully.")


def get_all_data(filename='carsharing_data.json'):
    try:
        with open(filename, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []