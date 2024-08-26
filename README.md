# Mobilytics

Mobilytics is a tool for analyzing carsharing usage based on PDF invoices.

## Project Setup

1. Clone the repository:
   ```
   git clone https://github.com/proxycodon/Mobilytics.git
   cd Mobilytics
   ```

2. Create and activate a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

## Development

To start the development environment, you need to run two components:

1. Start the main script to process invoices:
   ```
   python main.py
   ```
   This script processes PDF invoices in the `data/invoices/` directory.

2. Start the dashboard in a new terminal tab:
   ```
   streamlit run src/dashboard.py
   ```
   The dashboard runs on `http://localhost:8501` by default.

## Data Processing

To process new invoices:

1. Place PDF invoices in the `data/invoices/` directory.
2. Run the main script:
   ```
   python main.py
   ```

## Viewing the Dashboard

After processing the data, view the dashboard by running:
```
streamlit run src/dashboard.py
```

## Linting

To check your code for style and potential errors:
```
flake8 .
```

## Testing

To run the test suite:
```
pytest
```