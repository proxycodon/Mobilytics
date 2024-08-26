import json
from datetime import datetime, date


class JSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (date, datetime)):
            return obj.isoformat()
        return super().default(obj)


def save_trip_data(trip_data, filename='carsharing_trips.json'):
    try:
        with open(filename, 'r') as f:
            data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        data = []

    # Check if the invoice number already exists
    invoice_numbers = [trip.get('invoice_number') for trip in data]
    if trip_data.get('invoice_number') in invoice_numbers:
        print(f"Invoice {trip_data.get('invoice_number')} already exists. Skipping.")
        return

    data.append(trip_data)

    with open(filename, 'w') as f:
        json.dump(data, f, cls=JSONEncoder, indent=4)

    print(f"Invoice {trip_data.get('invoice_number')} added successfully.")


def get_all_trips(filename='carsharing_trips.json'):
    try:
        with open(filename, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []


def update_trip_data(trip_data, filename='carsharing_trips.json'):
    try:
        with open(filename, 'r') as f:
            data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        data = []

    for i, trip in enumerate(data):
        if trip.get('invoice_number') == trip_data.get('invoice_number'):
            data[i] = trip_data
            with open(filename, 'w') as f:
                json.dump(data, f, cls=JSONEncoder, indent=4)
            print(f"Invoice {trip_data.get('invoice_number')} updated successfully.")
            return

    print(f"Invoice {trip_data.get('invoice_number')} not found. No update performed.")


def delete_trip_data(invoice_number, filename='carsharing_trips.json'):
    try:
        with open(filename, 'r') as f:
            data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        data = []

    initial_length = len(data)
    data = [trip for trip in data if trip.get('invoice_number') != invoice_number]

    if len(data) < initial_length:
        with open(filename, 'w') as f:
            json.dump(data, f, cls=JSONEncoder, indent=4)
        print(f"Invoice {invoice_number} deleted successfully.")
    else:
        print(f"Invoice {invoice_number} not found. No deletion performed.")