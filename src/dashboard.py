import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from database_manager import get_all_data
from datetime import timedelta

# Set the page to wide mode and enable dark theme
st.set_page_config(layout="wide", page_title="Mobilytics Dashboard", initial_sidebar_state="expanded")

# Apply dark theme styling for the dashboard
st.markdown(
    """
    <style>
    .css-18e3th9 {
        background-color: #0e1117;
    }
    .css-1d391kg {
        background-color: #0e1117;
    }
    </style>
    """,
    unsafe_allow_html=True
)


# Function to load and process the data
def load_data():
    data = get_all_data()
    df = pd.DataFrame(data)

    # Convert 'invoice_date' to datetime and create 'trip_date'
    df['invoice_date'] = pd.to_datetime(df['invoice_date'], format='%d.%m.%Y', errors='coerce')
    df['trip_date'] = df['invoice_date']

    # Update 'trip_date' for trips based on the 'date' field if available
    mask = df['type'] == 'Trip'
    if 'date' in df.columns:
        df.loc[mask, 'trip_date'] = pd.to_datetime(df.loc[mask, 'date'], format='%d.%m.%y', errors='coerce')

    # Convert 'total_amount' to numeric
    if 'total_amount' in df.columns:
        df['total_amount'] = pd.to_numeric(df['total_amount'], errors='coerce')
    else:
        df['total_amount'] = 0

    # Convert 'Strecke in km' to numeric for distance
    if 'Strecke in km' in df.columns:
        df['distance'] = pd.to_numeric(df['Strecke in km'], errors='coerce')

    # Extract start and end times, then calculate duration
    if 'Zeit' in df.columns:
        df['start_time'] = pd.to_datetime(df['Zeit'].str.split('-').str[0], format='%H:%M', errors='coerce')
        df['end_time'] = pd.to_datetime(df['Zeit'].str.split('-').str[1], format='%H:%M', errors='coerce')

        # Handle cases where end time is earlier than start time (overnight trips)
        mask = df['end_time'] < df['start_time']
        df.loc[mask, 'end_time'] += timedelta(days=1)

        df['duration'] = (df['end_time'] - df['start_time']).dt.total_seconds() / 60  # Duration in minutes

    # Extract vehicle brand from 'vehicle' column
    if 'vehicle' in df.columns:
        df['brand'] = df['vehicle'].str.split().str[0]

    # Create a 'year' column based on 'invoice_date'
    df['year'] = df['invoice_date'].dt.year

    # Update cost types to be more user-friendly
    df['type'] = df['type'].replace({
        'trip': 'Trip',
        'share_now_pass': 'ShareNow Pass',
        'reservation': 'Reservation',
        'processing_fee': 'Traffic Violation'
    })

    return df


# Function to format duration in hours and minutes
def format_duration(total_minutes):
    hours = total_minutes // 60
    minutes = total_minutes % 60
    return f"{int(hours)}h {int(minutes)}m"


# Main function to render the dashboard
def main():
    st.title('Mobilytics: Your Carsharing Usage Analysis')

    # Load the data
    df = load_data()

    st.sidebar.header('Filters')

    # Add a year filter with an option to select all years
    available_years = ['All Years'] + sorted(df['year'].dropna().unique(), reverse=True)
    selected_year = st.sidebar.selectbox('Select Year', available_years, index=0)

    # Add a vehicle filter with an option to select all vehicles
    available_vehicles = ['All Vehicles'] + sorted(df['brand'].dropna().unique())
    selected_vehicle = st.sidebar.selectbox('Select Vehicle', available_vehicles, index=0)

    # Add a cost type filter with an option to select all types
    available_types = ['All'] + sorted(df['type'].unique())
    selected_type = st.sidebar.selectbox('Select Cost Type', available_types, index=0)

    # Filter data based on the selected year
    if selected_year != 'All Years':
        df = df[df['year'] == selected_year]

    # Filter data based on the selected vehicle
    if selected_vehicle != 'All Vehicles':
        df = df[df['brand'] == selected_vehicle]

    # Filter data based on the selected cost type
    if selected_type != 'All':
        df = df[df['type'] == selected_type]

    # Usage overview metrics
    st.header('Usage Overview')
    col1, col2, col3, col4 = st.columns(4)

    total_cost = df['total_amount'].sum()

    # Display total distance if available
    if 'distance' in df.columns:
        total_distance = df[df['type'] == 'Trip']['distance'].sum()
        col1.metric('Total Distance (km)', f"{total_distance:.2f}")
    else:
        col1.metric('Total Distance (km)', "N/A")

    col2.metric('Invoices', len(df))
    col3.metric('Total Cost (€)', f"{total_cost:.2f}")

    # Calculate and display total driving time
    total_duration_minutes = df[df['type'] == 'Trip']['duration'].sum()
    formatted_duration = format_duration(total_duration_minutes)
    col4.metric('Total Driving Time', formatted_duration)

    # Cost breakdown pie chart
    st.header('Cost Breakdown')
    cost_df = df.groupby('type')['total_amount'].sum().reset_index()
    fig_cost = px.pie(cost_df, values='total_amount', names='type', title='Cost Distribution')
    st.plotly_chart(fig_cost)

    # Bar chart for total costs per year
    st.header('Total Costs per Year')
    yearly_costs = df.groupby('year')['total_amount'].sum().reset_index()
    st.bar_chart(yearly_costs.set_index('year'))

    # Vehicle brand usage treemap
    trip_df = df[df['type'] == 'Trip']
    if not trip_df.empty:
        st.header('Trip Statistics')
        col1, col2 = st.columns(2)
        if 'distance' in trip_df.columns:
            col1.metric('Total Distance (km)', f"{trip_df['distance'].sum():.2f}")
        else:
            col1.metric('Total Distance (km)', "N/A")

        if 'duration' in trip_df.columns:
            col2.metric('Average Trip Duration (min)', f"{trip_df['duration'].mean():.0f}")
        else:
            col2.metric('Average Trip Duration (min)', "N/A")

        # Display vehicle brand usage as a treemap
        if 'brand' in trip_df.columns:
            st.header('Vehicle Brand Usage')
            brand_usage = trip_df.groupby('brand').agg({
                'total_amount': 'sum',
                'trip_date': 'count'
            }).reset_index()
            if 'distance' in trip_df.columns:
                brand_usage['Total Distance'] = trip_df.groupby('brand')['distance'].sum().values
                brand_usage.columns = ['Brand', 'Total Cost', 'Number of Trips', 'Total Distance']
            else:
                brand_usage.columns = ['Brand', 'Total Cost', 'Number of Trips']

            if not brand_usage.empty:
                fig_brand = px.treemap(brand_usage,
                                       path=['Brand'],
                                       values='Total Cost',
                                       color='Number of Trips',
                                       hover_data=['Total Distance'] if 'Total Distance' in brand_usage.columns else None,
                                       color_continuous_scale='RdBu',
                                       title='Vehicle Brand Usage (Size: Total Cost, Color: Number of Trips)')
                st.plotly_chart(fig_brand)
            else:
                st.warning("Treemap could not be displayed: No data available for vehicle brands.")
        else:
            st.warning("Treemap could not be displayed: No 'brand' column in the data.")
            st.write("Available columns:", trip_df.columns)

        # Trip activity over time
        st.header('Trip Activity Over Time')
        if not trip_df['trip_date'].empty:
            daily_amount = trip_df.resample('D', on='trip_date')['total_amount'].sum().reset_index()
            daily_count = trip_df.resample('D', on='trip_date').size().reset_index(name='Number of Trips')

            daily_trips = pd.merge(daily_amount, daily_count, on='trip_date')

            if 'distance' in trip_df.columns:
                daily_distance = trip_df.resample('D', on='trip_date')['distance'].sum().reset_index()
                daily_trips = pd.merge(daily_trips, daily_distance, on='trip_date')

            daily_trips.columns = ['Date', 'Total Cost', 'Number of Trips'] + (
                ['Total Distance'] if 'distance' in daily_trips.columns else [])

            fig_activity = go.Figure()
            if 'Total Distance' in daily_trips.columns:
                fig_activity.add_trace(go.Bar(x=daily_trips['Date'], y=daily_trips['Total Distance'],
                                              name='Distance (km)', yaxis='y'))
            fig_activity.add_trace(go.Scatter(x=daily_trips['Date'], y=daily_trips['Total Cost'],
                                              mode='lines+markers', name='Cost (€)', yaxis='y2'))
            fig_activity.update_layout(
                title='Daily Trip Activity and Cost',
                yaxis=dict(title='Distance (km)' if 'Total Distance' in daily_trips.columns else ''),
                yaxis2=dict(title='Cost (€)', overlaying='y', side='right')
            )
            st.plotly_chart(fig_activity)
        else:
            st.warning("Time axis graph could not be displayed: No date information in the trip data.")
            st.write("Debug Info: trip_date column")
            st.write(trip_df['trip_date'])
    else:
        st.warning("No trip data available.")
        st.write("Debug Info:")
        st.write("Available columns:", df.columns)
        st.write("Number of trips:", len(trip_df))

    # Display the data table
    st.header('Data Table')
    st.dataframe(df)


if __name__ == "__main__":
    main()
