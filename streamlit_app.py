import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from geopy.distance import geodesic
import seaborn as sns
import geopandas as gpd

import streamlit as st
import altair as alt

# SETTING PAGE CONFIG TO WIDE MODE AND ADDING A TITLE AND FAVICON
st.set_page_config(layout="wide", page_title="Forest Coverage Prediction", page_icon=":airplane:")

# LOAD AND PREP DATA ONCE
@st.cache_resource
def get_data(path='data/deplacements-presidents-republique-et-premiers-ministres-depuis-1945.json'):
    
    data =  pd.read_json(path)

    # DATA CLEANING
    data.loc[
        (data['lieu'] == 'Bonn') | (data['lieu'] == 'Allemagne'),
        'lieu_normalise'
    ] = 'Allemagne'

    data['lieu_normalise'].fillna(data['lieu'], inplace=True)


    # fixed according to contenu_initial
    data.loc[data.date_de_debut.apply(lambda x: str(x)[:4]) == '2?-0', 'date_de_debut'] = '1945-04-02'

    data.loc[data.date_de_debut.apply(lambda x: str(x)[-2:]) == '9.', 'date_de_debut'] = '1998-06-29'

    data.loc[data.date_de_debut.apply(lambda x: str(x)[-2:]) == '37', 'date_de_debut'] = '1966-09-03'

    extracted_days = data['contenu_initial'].str.extract(r'(\d{1,2}(?![\d]))[^\d]+(\d{1,2}(?![\d]))?')
    extracted_days.columns = ['day_debut', 'day_fin']
    extracted_days['day_fin'].fillna(extracted_days['day_debut'], inplace=True)
    extracted_days = extracted_days.astype(str).apply(lambda x: x.str.zfill(2))

    data['date_de_debut'].fillna(data['date_de_fin'].apply(lambda x: x[:8] if x != None else x) + extracted_days['day_debut'], inplace=True)
    data['date_de_fin'].fillna(data['date_de_debut'].apply(lambda x: x[:8] if x != None else x) + extracted_days['day_fin'], inplace=True)

    data.loc[data.date_de_debut.apply(lambda x: str(x)[-2:]) == '75', ['date_de_debut', 'date_de_fin']] = '2007-01-14'

    data.loc[data.index == 944, ['date_de_debut', 'date_de_fin']] = '2006-03-09'
    data.loc[data.index == 1669, ['date_de_debut', 'date_de_fin']] = '2004-04-29'
    data.loc[data.index == 46, ['date_de_debut', 'date_de_fin']] = "1958-11-01" 
    data.loc[data.index == 262, ['date_de_debut', 'date_de_fin']] = "1976-12-17" 
    data.loc[data.index == 416, ['date_de_debut', 'date_de_fin']] = "1993-10-01" 
    data.loc[data.index == 692, ['date_de_debut', 'date_de_fin']] = "1975-12-01" 
    data.loc[data.index == 771, ['date_de_debut', 'date_de_fin']] = "1975-12-01" 
    data.loc[data.index == 900, ['date_de_debut', 'date_de_fin']] = "1975-12-01" 
    data.loc[data.index == 868, ['date_de_debut', 'date_de_fin']] = "1983-01-01" 
    data.loc[data.index == 1414, ['date_de_debut', 'date_de_fin']] = "2005-04-25"
    data.loc[data.index == 1601, ['date_de_debut', 'date_de_fin']] = "1991-09-01"
    data.loc[data.index == 2140, ['date_de_debut', 'date_de_fin']] = "1982-10-01"
    data.loc[data.index == 2430, ['date_de_debut', 'date_de_fin']] = "1948-03-01" 
    data.loc[data.index == 2474, ['date_de_debut', 'date_de_fin']] = "1984-02-01"
    data.loc[data.index == 1953, ['date_de_debut', 'date_de_fin']] = "2007-05-31"

    data.loc[data.index == 1453, 'annee_du_voyage'] = 2007
    data.loc[data.index == 1960, 'annee_du_voyage'] = 2008

    extracted_years = data['contenu_initial'].str.extract(r'(194[5-9]|19[5-9][0-9]|20[0-9][0-9])')

    inconsistency = data.date_de_debut.apply(lambda x: x[:4]) != data.annee_du_voyage.astype(str)
    data.loc[inconsistency, "date_de_debut"] = (extracted_years.loc[:, 0] + data.loc[:, 'date_de_debut'].apply(lambda x: x[4:])).loc[inconsistency]

    inconsistency = data.date_de_debut.apply(lambda x: x[:4]) != data.date_de_fin.apply(lambda x: x[:4])
    data.loc[inconsistency, "date_de_fin"] = (extracted_years.loc[:, 0] + data.loc[:, 'date_de_fin'].apply(lambda x: x[4:])).loc[inconsistency]

    data['date_de_debut'] = pd.to_datetime(data['date_de_debut'])
    data['date_de_fin'] = pd.to_datetime(data['date_de_fin'])

    data.loc[data['date_de_fin'] < data['date_de_debut'], 'date_de_fin'] = data['date_de_debut']

    data = data.drop_duplicates(subset=['contenu_initial'], keep='first')

    return data

election_years = [1947, 1953, 1958, 1965, 1969, 1974, 1981, 1988, 1995, 2002, 2007, 2012, 2017, 2022]

data = get_data()


# STREAMLIT APP PREPARATION

# Streamlit app title
st.title("France Presidential Travels Visualization")

col00, col01 = st.columns(2) 

# FILTERS
with col00:
    # Filter by year range
    from_year = st.slider('Start year', min(data["annee_du_voyage"]), max(data["annee_du_voyage"]), min(data["annee_du_voyage"]))
    to_year = st.slider('End year', min(data["annee_du_voyage"]), max(data["annee_du_voyage"]), max(data["annee_du_voyage"]))

    data = data[(
        (from_year <= data["annee_du_voyage"]) &
        (data["annee_du_voyage"] <= to_year)
    )]

    # Filter by function: President or Prime Minister
    function_choice = st.radio("Select Function:", ('Président de la République', 'Premier ministre'))
    data = data[data['fonction'] == function_choice]

    if st.checkbox('Select Trips Outside France Only'):
        data = data[data['code_pays'] != 'FRA']
    
    if st.checkbox('Select Trips on Election Years Only'):
        data = data[data["annee_du_voyage"].isin(election_years)]


# Load world data
@st.cache_resource
def load_world():
    return gpd.read_file(gpd.datasets.get_path('naturalearth_lowres'))

world = load_world()

# Unique country codes from the data
country_codes = data['code_pays'].unique()
filtered_world = world[world['iso_a3'].isin(country_codes)]

# World Map
with col01:
    st.subheader("Map of Visited Countries")
    fig, ax = plt.subplots(figsize=(4, 2))
    filtered_world.plot(ax=ax, color='darkblue', edgecolor='white', linewidth=0.3)
    st.pyplot(fig)

# Create columns for layout
col10, col11 = st.columns([2, 1])

with col10:
    st.subheader("Top 10 Visited Locations")

    top_10_visited = data['lieu'].value_counts().nlargest(10)

    st.write(f"The top three most visited locations overall were: {top_10_visited.index[:3].tolist()}")

    top_10_df = top_10_visited.reset_index()
    top_10_df.columns = ['Location', 'Visit Count']

    chart = alt.Chart(top_10_df).mark_bar().encode(
        x=alt.X('Visit Count', title='Number of Visits', scale=alt.Scale(domain=[0, top_10_df['Visit Count'].max() + 5])),
        y=alt.Y('Location', title='Location', sort='-x'),
        color=alt.condition(
            alt.datum['Visit Count'] > top_10_df['Visit Count'].mean(),
            alt.value('steelblue'),
            alt.value('lightgray')
        ),
        tooltip=['Location', 'Visit Count']
    ).properties(
        title='Top 10 Most Visited Locations',
        width=600,
        height=400
    ).configure_title(
        fontSize=20
    ).configure_axis(
        labelFontSize=12,
        titleFontSize=14
    )

    st.altair_chart(chart, use_container_width=True)


# Visits per Month
with col11:
    st.subheader("Number of Trips per Month")
    
    # Check if 'date_de_debut' has valid data
    if 'date_de_debut' in data.columns and not data['date_de_debut'].isnull().all():
        data['month'] = data['date_de_debut'].dt.month_name()
        trip_counts = data['month'].value_counts().reindex([
            'January', 'February', 'March', 'April', 'May', 'June', 
            'July', 'August', 'September', 'October', 'November', 'December'
        ])
        st.bar_chart(trip_counts)
    else:
        st.write("No valid trip data available for month counts.")


col20, col21 = st.columns(2)

# Most Visited Countries
with col20:
    st.subheader("Top 5 Most Visited Countries")
    
    top_5_countries = data['code_pays'].value_counts().nlargest(5)

    top_5_df = top_5_countries.reset_index()
    top_5_df.columns = ['Country Code', 'Visit Count']

    chart = alt.Chart(top_5_df).mark_bar().encode(
        x=alt.X('Visit Count', title='Number of Visits', scale=alt.Scale(domain=[0, top_5_df['Visit Count'].max() + 5])),
        y=alt.Y('Country Code', title='Country Code', sort='-x'),
        color=alt.condition(
            alt.datum['Visit Count'] > top_5_df['Visit Count'].mean(),
            alt.value('orange'),
            alt.value('lightgray')
        ),
        tooltip=['Country Code', 'Visit Count']
    ).properties(
        title='Top 5 Most Visited Countries',
        width=600,
        height=400
    ).configure_title(
        fontSize=20
    ).configure_axis(
        labelFontSize=12,
        titleFontSize=14
    )

    st.altair_chart(chart, use_container_width=True)

# Most Visited Locations
with col21:
    travel_counts = data['annee_du_voyage'].value_counts().sort_index()
    
    travel_data = pd.DataFrame({
        'Year': travel_counts.index,
        'Travels Count': travel_counts.values
    })

    chart = alt.Chart(travel_data).mark_line(point=True).encode(
        x=alt.X('Year:O', title='Year'),
        y=alt.Y('Travels Count:Q', title='Number of Travels'),
        tooltip=['Year', 'Travels Count']
    ).properties(
        title='Number of Travels Per Year',
        width=800,
        height=400
    ).configure_title(
        fontSize=20
    ).configure_axis(
        labelFontSize=12,
        titleFontSize=14
    )

    st.altair_chart(chart, use_container_width=True)


# Additional notes
st.markdown("---")
st.markdown("### Additional Information")
st.write("This app visualizes France presidential travel data, showing where trips have occurred, frequency by year and month, and the most popular locations and countries visited abroad.")
