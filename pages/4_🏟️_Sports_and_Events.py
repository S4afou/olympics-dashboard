import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from utils import load_data, create_sidebar_filters
import os
from geopy.geocoders import Nominatim

# Page configuration
st.set_page_config(
    page_title="Sports & Events - Paris 2024",
    page_icon="🏟️",
    layout="wide"
)

st.title("🏟️ Sports & Events: The Competition Arena")
st.markdown("Explore event schedules, venue locations, and sport-specific medal distributions")
st.markdown("---")

# Load data
data = load_data()
filters = create_sidebar_filters(data)

events_df = data['events'].copy()
schedules_df = data['schedules'].copy()
venues_df = data['venues'].copy()
medals_df = data['medals'].copy()

# ====== MAP GENDER FIRST (because medals_df uses W/M) ======
gender_map = {'M': 'Male', 'W': 'Female'}
if 'gender' in medals_df.columns:
    medals_df['gender'] = medals_df['gender'].map(gender_map)
if 'gender' in events_df.columns:
    events_df['gender'] = events_df['gender'].map(gender_map)
if 'gender' in schedules_df.columns:
    schedules_df['gender'] = schedules_df['gender'].map(gender_map)


# ================= APPLY FILTERS =================

# --- Sport filter ---
if filters.get('sports'):
    events_df = events_df[events_df['sport'].isin(filters['sports'])]

    if 'discipline' in schedules_df.columns:
        schedules_df = schedules_df[schedules_df['discipline'].isin(filters['sports'])]

    if 'discipline' in medals_df.columns:
        medals_df = medals_df[medals_df['discipline'].isin(filters['sports'])]


# --- Country filter ---
if filters.get('countries'):
    events_df = events_df[events_df['country_code'].isin(filters['countries'])] \
        if 'country_code' in events_df.columns else events_df

    schedules_df = schedules_df[schedules_df['country_code'].isin(filters['countries'])] \
        if 'country_code' in schedules_df.columns else schedules_df

    medals_df = medals_df[medals_df['country_code'].isin(filters['countries'])]


# --- Gender filter (NOW IT FINALLY WORKS) ---
if filters.get('genders'):
    events_df = events_df[events_df['gender'].isin(filters['genders'])] \
        if 'gender' in events_df.columns else events_df

    schedules_df = schedules_df[schedules_df['gender'].isin(filters['genders'])] \
        if 'gender' in schedules_df.columns else schedules_df

    medals_df = medals_df[medals_df['gender'].isin(filters['genders'])]


# --- Continent filter ---
from utils import add_continent_column   # if it's in another file

if 'country_code' in medals_df.columns:
    medals_df = add_continent_column(medals_df)

if 'country_code' in events_df.columns:
    events_df = add_continent_column(events_df)

if 'country_code' in schedules_df.columns:
    schedules_df = add_continent_column(schedules_df)
    
if filters.get('continents'):
    medals_df = medals_df[medals_df['continent'].isin(filters['continents'])] \
        if 'continent' in medals_df.columns else medals_df

    events_df = events_df[events_df['continent'].isin(filters['continents'])] \
        if 'continent' in events_df.columns else events_df

    schedules_df = schedules_df[schedules_df['continent'].isin(filters['continents'])] \
        if 'continent' in schedules_df.columns else schedules_df


# --- Medal type filter ---
if filters.get('medals'):
    medals_df = medals_df[medals_df['medal_type'].isin(filters['medals'])] \
        if 'medal_type' in medals_df.columns else medals_df

# ============= TASK 1: EVENT SCHEDULE (GANTT CHART) =============
st.header("📅 Event Schedule Timeline")
st.markdown("**Gantt chart showing the schedule of events for a selected sport or venue**")

# Sport/Venue selector for schedule
schedule_view = st.radio("View schedule by:", ["Sport", "Venue"], horizontal=True)

if schedule_view == "Sport":
    available_sports = sorted(schedules_df['discipline'].dropna().unique())
    if len(available_sports) > 0:
        selected_sport = st.selectbox("Select a Sport", available_sports)
        filtered_schedule = schedules_df[schedules_df['discipline'] == selected_sport].copy()
        title_suffix = f"for {selected_sport}"
    else:
        st.warning("No sports available with current filters")
        filtered_schedule = pd.DataFrame()
else:
    available_venues = sorted(schedules_df['venue'].dropna().unique())
    if len(available_venues) > 0:
        selected_venue = st.selectbox("Select a Venue", available_venues)
        filtered_schedule = schedules_df[schedules_df['venue'] == selected_venue].copy()
        title_suffix = f"at {selected_venue}"
    else:
        st.warning("No venues available")
        filtered_schedule = pd.DataFrame()

# Prepare data for Gantt chart
if not filtered_schedule.empty:
    # Convert date columns to datetime
    filtered_schedule['start_date'] = pd.to_datetime(filtered_schedule['start_date'])
    filtered_schedule['end_date'] = pd.to_datetime(filtered_schedule['end_date'])
    
    # Limit to reasonable number for readability
    display_limit = st.slider("Number of events to display", 10, 100, 50, 10)
    filtered_schedule_display = filtered_schedule.head(display_limit)
    
    # Create Gantt chart using plotly.express.timeline
    fig_gantt = px.timeline(
        filtered_schedule_display,
        x_start='start_date',
        x_end='end_date',
        y='event',
        color='discipline',
        title=f'Event Schedule {title_suffix}',
        hover_data=['venue', 'discipline', 'phase'],
        labels={'event': 'Event', 'discipline': 'Sport'}
    )
    
    fig_gantt.update_yaxes(categoryorder='total ascending')
    fig_gantt.update_layout(
        height=600,
        xaxis_title='Date',
        yaxis_title='Event',
        hovermode='closest'
    )
    
    st.plotly_chart(fig_gantt, use_container_width=True)
    
    if len(filtered_schedule) > display_limit:
        st.info(f"ℹ️ Showing {display_limit} of {len(filtered_schedule)} events. Adjust the slider to see more.")
else:
    st.warning("No events found for the selected filters.")

st.markdown("---")

# ============= TASK 2: MEDAL COUNT BY SPORT (TREEMAP) =============
st.header("🎯 Medal Count by Sport")
st.markdown("**Treemap showing the medal count by sport**")

if len(medals_df) > 0:
    # Group medals by sport (discipline)
    sport_medals = medals_df.groupby('discipline').size().reset_index(name='medal_count')
    
    # Also create hierarchical data: Sport -> Medal Type
    sport_medal_detail = medals_df.groupby(['discipline', 'medal_type']).size().reset_index(name='medal_count')
    
    # Create two columns for different treemap views
    col_tree1, col_tree2 = st.columns(2)
    
    with col_tree1:
        st.subheader("Medal Count by Sport")
        # Simple treemap: just sports
        fig_treemap1 = px.treemap(
            sport_medals,
            path=['discipline'],
            values='medal_count',
            title='Total Medals by Sport',
            color='medal_count',
            color_continuous_scale='YlOrRd',
            hover_data={'medal_count': True}
        )
        
        fig_treemap1.update_traces(
            textinfo='label+value',
            textposition='middle center',
            hovertemplate='<b>%{label}</b><br>Medals: %{value}<extra></extra>'
        )
        
        fig_treemap1.update_layout(height=500)
        st.plotly_chart(fig_treemap1, use_container_width=True)
    
    with col_tree2:
        st.subheader("Medal Count by Sport & Type")
        # Hierarchical treemap: Sport -> Medal Type
        fig_treemap2 = px.treemap(
            sport_medal_detail,
            path=['discipline', 'medal_type'],
            values='medal_count',
            title='Medals by Sport and Type',
            color='medal_count',
            color_continuous_scale='RdYlGn',
            hover_data={'medal_count': True}
        )
        
        fig_treemap2.update_traces(
            textinfo='label+value',
            textposition='middle center',
            hovertemplate='<b>%{label}</b><br>Medals: %{value}<extra></extra>'
        )
        
        fig_treemap2.update_layout(height=500)
        st.plotly_chart(fig_treemap2, use_container_width=True)
    
    # Additional bar chart for comparison
    st.subheader("Top 15 Sports by Medal Count")
    top_sports = sport_medals.nlargest(15, 'medal_count')
    
    fig_bar_sports = px.bar(
        top_sports,
        x='medal_count',
        y='discipline',
        orientation='h',
        text='medal_count',
        title='Top 15 Sports by Number of Medals Awarded',
        color='medal_count',
        color_continuous_scale='Blues',
        labels={'medal_count': 'Number of Medals', 'discipline': 'Sport'}
    )
    
    fig_bar_sports.update_traces(
        textposition='outside',
        hovertemplate='<b>%{y}</b><br>Medals: %{x}<extra></extra>'
    )
    
    fig_bar_sports.update_layout(
        yaxis={'categoryorder': 'total ascending'},
        showlegend=False,
        height=500
    )
    
    st.plotly_chart(fig_bar_sports, use_container_width=True)
    
else:
    st.warning("No medal data available with current filters")

st.markdown("---")

# ============= TASK 3: VENUE MAP (SCATTER MAPBOX) =============
st.header("📍 Olympic Venues Map")
st.markdown("**Scatter mapbox showing the locations of Olympic venues in the Paris area**")

# Load or generate coordinates
coord_path = "data/venue_coordinates.csv"

if os.path.exists(coord_path):
    # Load existing coordinates
    coords_df = pd.read_csv(coord_path)
    st.info("✓ Using cached venue coordinates")
else:
    # Generate coordinates using geopy
    st.warning("🔄 Geocoding venues... This may take a moment (only runs once)")
    
    geolocator = Nominatim(user_agent="paris_olympic_dashboard")
    
    def get_coords(venue_name):
        """Geocode venue name to get latitude and longitude"""
        try:
            # Try with Paris, France first
            location = geolocator.geocode(f"{venue_name}, Paris, France", timeout=10)
            if location:
                return pd.Series([location.latitude, location.longitude])

        except Exception as e:
            st.warning(f"Could not geocode {venue_name}: {e}")
        
        return pd.Series([None, None])
    
    # Apply geocoding to all venues
    venues_df[['latitude_x', 'longitude_x']] = venues_df['venue'].apply(get_coords)
    
    # Save coordinates to CSV for future use
    coords_df = venues_df[['venue', 'latitude_x', 'longitude_x']].copy()
    coords_df.to_csv(coord_path, index=False)
    st.success(f"✓ Coordinates saved to {coord_path}")

# Merge coordinates with venues dataframe
venues_with_coords = venues_df.merge(coords_df, on="venue", how="left", suffixes=('', '_coord'))

# Use the coordinate columns (handle both column name scenarios)
if 'latitude_x' not in venues_with_coords.columns:
    venues_with_coords = venues_with_coords.rename(columns={
        'latitude_x_coord': 'latitude_x',
        'longitude_x_coord': 'longitude_x'
    })

# Filter venues with valid coordinates
venues_mapped = venues_with_coords.dropna(subset=['latitude_x', 'longitude_x'])

if len(venues_mapped) > 0:
    st.success(f"📍 Successfully mapped {len(venues_mapped)} out of {len(venues_df)} venues")
    
    # Parse sports list for better display
    venues_mapped['sports_display'] = venues_mapped['sports'].apply(
        lambda x: ', '.join(eval(x)) if isinstance(x, str) and x.startswith('[') else str(x)
    )
    
    # Create scatter mapbox with plotly
    fig_map = px.scatter_mapbox(
        venues_mapped,
        lat="latitude_x",
        lon="longitude_x",
        hover_name="venue",
        hover_data={
            "sports_display": True,
            "date_start": True,
            "date_end": True,
            "latitude_x": False,
            "longitude_x": False
        },
        color="sports_display",
        zoom=10,
        height=600,
        title="Olympic Venues - Interactive Map",
        labels={"sports_display": "Sports"}
    )
    
    fig_map.update_layout(
        mapbox_style="open-street-map",
        margin={"r": 0, "t": 50, "l": 0, "b": 0},
        hovermode='closest'
    )
    
    fig_map.update_traces(
        marker=dict(size=12, opacity=0.8)
    )
    
    st.plotly_chart(fig_map, use_container_width=True)
    
    # Alternative: Streamlit native map
    st.subheader("📌 Alternative View: Streamlit Native Map")
    
    df_clean = venues_mapped.dropna(subset=['latitude_x', 'longitude_x']).copy()
    
    if len(df_clean) > 0:
        # Rename columns for st.map compatibility
        df_clean_map = df_clean.rename(columns={
            'latitude_x': 'latitude',
            'longitude_x': 'longitude'
        })
        
        st.map(
            data=df_clean_map,
            latitude="latitude",
            longitude="longitude",
            zoom=10,
            use_container_width=True
        )
    
    # Display venue information table
    st.subheader("📋 Venue Details with Coordinates")
    
    display_venues = venues_mapped[['venue', 'sports_display', 'latitude_x', 'longitude_x']].copy()
    display_venues.columns = ['Venue', 'Sports', 'Latitude', 'Longitude']
    
    # Format coordinates to 4 decimal places
    display_venues['Latitude'] = display_venues['Latitude'].round(4)
    display_venues['Longitude'] = display_venues['Longitude'].round(4)
    
    st.dataframe(display_venues, use_container_width=True, hide_index=True)
    
    # Additional statistics
    col_stat1, col_stat2, col_stat3 = st.columns(3)
    
    with col_stat1:
        st.metric("Total Venues", len(venues_df))
    
    with col_stat2:
        st.metric("Mapped Venues", len(venues_mapped))
    
    with col_stat3:
        unmapped = len(venues_df) - len(venues_mapped)
        st.metric("Unmapped Venues", unmapped)
    
    if unmapped > 0:
        st.info("💡 Some venues couldn't be geocoded automatically. You can add their coordinates manually to venue_coordinates.csv")

else:
    st.error("❌ No venue coordinates available. The geocoding process may have failed.")
    st.info("""
    **Troubleshooting:**
    1. Check your internet connection (needed for geocoding)
    2. The geopy service may be temporarily unavailable
    3. Try running the app again after a few minutes
    4. Or manually create `data/venue_coordinates.csv` with columns: venue, latitude_x, longitude_x
    """)

st.markdown("---")
# ============================================================
# TASK 4: COUNTRY HEAD-TO-HEAD COMPARISON
# ============================================================
st.header("4️⃣ Country Head-to-Head Comparison")

countries = sorted(medals_df["country_code"].unique())

c1, c2 = st.columns(2)
with c1:
    country_a = st.selectbox("Country A:", countries)
with c2:
    country_b = st.selectbox("Country B:", countries)

# Filter only these two countries
comp_df = medals_df[medals_df['country_code'].isin([country_a, country_b])]

# Count medals by type for each country
comp_count = comp_df.groupby(['medal_type', 'country_code']).size().reset_index(name='count')

fig_compare = px.bar(
    comp_count,
    x='medal_type',
    y='count',
    color='country_code',
    barmode='group',
    title=f"{country_a} vs {country_b} — Medal Comparison",
    labels={'count':'Number of Medals', 'medal_type':'Medal Type', 'country_code':'Country'}
)
st.plotly_chart(fig_compare, use_container_width=True)

# ================= TASK 5: WHO WON THE DAY =================
st.header(" Who Won the Day? — Medals & Events Timeline")

# Convert date columns to datetime.date
medals_df['medal_date'] = pd.to_datetime(medals_df['medal_date']).dt.date
schedules_df['start_date'] = pd.to_datetime(schedules_df['start_date']).dt.date

# Games period
min_date = min(schedules_df['start_date'].min(), medals_df['medal_date'].min())
max_date = max(schedules_df['start_date'].max(), medals_df['medal_date'].max())

# Day selector
selected_date = st.slider(
    "Select a Day of the Games:",
    min_value=min_date,
    max_value=max_date,
    value=min_date,
    format="YYYY-MM-DD"
)

# --- Medals ---
medals_today = medals_df[medals_df['medal_date'] == selected_date]

if medals_today.empty:
    st.info(f"No medals awarded on {selected_date}.")
else:
    summary = medals_today.groupby(['country_code', 'medal_type']).size().reset_index(name='count')
    fig_medals = px.bar(
        summary,
        x='country_code',
        y='count',
        color='medal_type',
        text='count',
        labels={'count': 'Number of Medals', 'country_code': 'Country', 'medal_type': 'Medal Type'},
        title=f"Medals Awarded on {selected_date}",
        barmode='stack'
    )
    fig_medals.update_traces(textposition='outside')
    fig_medals.update_layout(height=500, margin=dict(t=50, b=50))
    st.plotly_chart(fig_medals, use_container_width=True)

# --- Events ---
events_today = schedules_df[schedules_df['start_date'] == selected_date]

if events_today.empty:
    st.info(f"No events scheduled on {selected_date}.")
else:
    st.subheader(f"Events on {selected_date}")
    display_events = events_today[['discipline', 'event', 'venue', 'start_date', 'end_date', 'phase', 'gender']].copy()
    display_events = display_events.rename(columns={
        'discipline': 'Sport',
        'event': 'Event',
        'venue': 'Venue',
        'start_date': 'Start Date',
        'end_date': 'End Date',
        'phase': 'Phase',
        'gender': 'Gender'
    })
    st.dataframe(display_events, use_container_width=True)
st.caption("💡 Use the sidebar filters to explore specific sports and countries. Click on map markers for venue details!")