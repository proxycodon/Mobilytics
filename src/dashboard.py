import streamlit as st
import pandas as pd
import plotly.express as px
from database_manager import get_all_trips

def load_data():
    trips = get_all_trips()
    df = pd.DataFrame(trips)
    df['date'] = pd.to_datetime(df['date'], format='%d.%m.%y')
    df['duration'] = pd.to_numeric(df['duration'])
    df['distance'] = pd.to_numeric(df['distance'])
    df['total_amount'] = pd.to_numeric(df['total_amount'])
    return df

def main():
    st.title('Carsharing Trip Analysis Dashboard')

    df = load_data()

    st.sidebar.header('Filters')
    date_range = st.sidebar.date_input('Date range', [df['date'].min(), df['date'].max()])
    selected_vehicles = st.sidebar.multiselect('Select vehicles', options=df['vehicle'].unique(), default=df['vehicle'].unique())

    filtered_df = df[(df['date'].dt.date >= date_range[0]) &
                     (df['date'].dt.date <= date_range[1]) &
                     (df['vehicle'].isin(selected_vehicles))]

    st.header('Trip Overview')
    col1, col2, col3, col4 = st.columns(4)
    col1.metric('Total Trips', len(filtered_df))
    col2.metric('Total Distance (km)', f"{filtered_df['distance'].sum():.2f}")
    col3.metric('Total Duration (min)', f"{filtered_df['duration'].sum():.0f}")
    col4.metric('Total Cost (€)', f"{filtered_df['total_amount'].sum():.2f}")

    st.header('Trip History')
    st.dataframe(filtered_df)

    st.header('Distance by Vehicle')
    fig_distance = px.bar(filtered_df.groupby('vehicle')['distance'].sum().reset_index(),
                          x='vehicle', y='distance', title='Total Distance by Vehicle')
    st.plotly_chart(fig_distance)

    st.header('Cost by Vehicle')
    fig_cost = px.pie(filtered_df, values='total_amount', names='vehicle', title='Total Cost by Vehicle')
    st.plotly_chart(fig_cost)

    st.header('Trips Over Time')
    fig_time = px.line(filtered_df.groupby('date').size().reset_index(name='count'),
                       x='date', y='count', title='Number of Trips Over Time')
    st.plotly_chart(fig_time)

if __name__ == "__main__":
    main()