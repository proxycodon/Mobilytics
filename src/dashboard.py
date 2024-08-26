import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from database_manager import get_all_data
from datetime import timedelta


def load_data():
    data = get_all_data()
    df = pd.DataFrame(data)

    df['invoice_date'] = pd.to_datetime(df['invoice_date'], format='%d.%m.%Y', errors='coerce')
    df['trip_date'] = df['invoice_date']

    mask = df['type'] == 'trip'
    if 'date' in df.columns:
        df.loc[mask, 'trip_date'] = pd.to_datetime(df.loc[mask, 'date'], format='%d.%m.%y', errors='coerce')

    df['total_amount'] = pd.to_numeric(df['total_amount'], errors='coerce')

    # Extract distance from the 'Strecke in km' column
    if 'Strecke in km' in df.columns:
        df['distance'] = pd.to_numeric(df['Strecke in km'], errors='coerce')

    # Extract start and end times, then calculate duration
    if 'Zeit' in df.columns:
        df['start_time'] = pd.to_datetime(df['Zeit'].str.split('-').str[0], format='%H:%M', errors='coerce')
        df['end_time'] = pd.to_datetime(df['Zeit'].str.split('-').str[1], format='%H:%M', errors='coerce')

        # Handling cases where end time is on the next day
        mask = df['end_time'] < df['start_time']
        df.loc[mask, 'end_time'] += timedelta(days=1)

        df['duration'] = (df['end_time'] - df['start_time']).dt.total_seconds() / 60  # Duration in minutes

    if 'vehicle' in df.columns:
        df['brand'] = df['vehicle'].str.split().str[0]

    return df


def main():
    st.title('Mobilytics: Carsharing Usage Analysis Dashboard')

    df = load_data()

    st.sidebar.header('Filters')
    date_range = st.sidebar.date_input('Date range', [df['trip_date'].min(), df['trip_date'].max()])

    filtered_df = df[(df['trip_date'].dt.date >= date_range[0]) &
                     (df['trip_date'].dt.date <= date_range[1])]

    st.header('Usage Overview')
    col1, col2, col3, col4, col5 = st.columns(5)
    trip_cost = filtered_df[filtered_df['type'] == 'trip']['total_amount'].sum()
    reservation_cost = filtered_df[filtered_df['type'] == 'reservation_extension']['total_amount'].sum()

    if 'distance' in filtered_df.columns:
        total_distance = filtered_df[filtered_df['type'] == 'trip']['distance'].sum()
        col1.metric('Total Distance (km)', f"{total_distance:.2f}")
    else:
        col1.metric('Total Distance (km)', "N/A")
        st.warning("'distance' column not present in the data.")

    col2.metric('Total Trips', len(filtered_df[filtered_df['type'] == 'trip']))
    col3.metric('Total Reservations', len(filtered_df[filtered_df['type'] == 'reservation_extension']))
    col4.metric('Trip Costs (€)', f"{trip_cost:.2f}")
    col5.metric('Reservation Costs (€)', f"{reservation_cost:.2f}")

    # New section: Yearly Spend Analysis
    st.header('Yearly Spend Analysis')
    filtered_df['year'] = filtered_df['trip_date'].dt.year
    yearly_spend = filtered_df.groupby('year')['total_amount'].sum().reset_index()
    st.bar_chart(yearly_spend.set_index('year'))

    st.header('Cost Breakdown')
    cost_df = filtered_df.groupby('type')['total_amount'].sum().reset_index()
    fig_cost = px.pie(cost_df, values='total_amount', names='type', title='Cost Distribution')
    st.plotly_chart(fig_cost)

    trip_df = filtered_df[filtered_df['type'] == 'trip']
    if not trip_df.empty:
        st.header('Trip Statistics')
        col1, col2 = st.columns(2)
        if 'distance' in trip_df.columns:
            col1.metric('Total Distance (km)', f"{trip_df['distance'].sum():.2f}")
        else:
            col1.metric('Total Distance (km)', "N/A")
            st.warning("'distance' column not present in the trip data.")

        if 'duration' in trip_df.columns:
            col2.metric('Average Trip Duration (min)', f"{trip_df['duration'].mean():.0f}")
        else:
            col2.metric('Average Trip Duration (min)', "N/A")
            st.warning("'duration' column not present in the trip data.")

        if 'brand' in trip_df.columns:
            st.header('Vehicle Brand Usage')
            brand_usage = trip_df.groupby('brand').agg({
                'total_amount': 'sum',
                'trip_date': 'count'
            }).reset_index()
            if 'distance' in trip_df.columns:
                brand_usage['Total Distance'] = trip_df.groupby('brand')['distance'].sum().values
            brand_usage.columns = ['Brand', 'Total Cost', 'Number of Trips'] + (
                ['Total Distance'] if 'distance' in trip_df.columns else [])

            if not brand_usage.empty:
                fig_brand = px.treemap(brand_usage,
                                       path=['Brand'],
                                       values='Total Cost',
                                       color='Number of Trips',
                                       hover_data=[
                                           'Total Distance'] if 'Total Distance' in brand_usage.columns else None,
                                       color_continuous_scale='RdBu',
                                       title='Vehicle Brand Usage (Size: Total Cost, Color: Number of Trips)')
                st.plotly_chart(fig_brand)
            else:
                st.warning("Treemap could not be displayed: No data available for vehicle brands.")
                st.write("Debug Info:")
                st.write(brand_usage)
        else:
            st.warning("Treemap could not be displayed: No 'brand' column in the data.")
            st.write("Available columns:", trip_df.columns)

        st.header('Trip Activity Over Time')
        if not trip_df['trip_date'].empty:
            # Separate aggregations for total_amount and trip count
            daily_amount = trip_df.resample('D', on='trip_date')['total_amount'].sum().reset_index()
            daily_count = trip_df.resample('D', on='trip_date').size().reset_index(name='Number of Trips')

            # Merge the results
            daily_trips = pd.merge(daily_amount, daily_count, on='trip_date')

            if 'distance' in trip_df.columns:
                daily_distance = trip_df.resample('D', on='trip_date')['distance'].sum().reset_index()
                daily_trips = pd.merge(daily_trips, daily_distance, on='trip_date')

            daily_trips.columns = ['Date', 'Total Cost', 'Number of Trips'] + (
                ['Total Distance'] if 'distance' in daily_trips.columns else [])

            if not daily_trips.empty:
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
                st.warning("Time axis graph could not be displayed: No aggregated data available.")
                st.write("Debug Info:")
                st.write(daily_trips)
        else:
            st.warning("Time axis graph could not be displayed: No date information in the trip data.")
            st.write("Debug Info: trip_date column")
            st.write(trip_df['trip_date'])
    else:
        st.warning("No trip data available.")
        st.write("Debug Info:")
        st.write("Available columns:", filtered_df.columns)
        st.write("Number of trips:", len(trip_df))

    st.header('Data Table')
    st.dataframe(filtered_df)


if __name__ == "__main__":
    main()
