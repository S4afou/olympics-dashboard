import pandas as pd
import streamlit as st
import pycountry
import pycountry_convert as pc

@st.cache_data
def load_data():
    """
    Load all required CSV files with caching for performance.
    The @st.cache_data decorator ensures data is loaded only once.
    """
    data = {
        'athletes': pd.read_csv('data/athletes.csv'),
        'medals': pd.read_csv('data/medals.csv'),
        'medals_total': pd.read_csv('data/medals_total.csv'),
        'events': pd.read_csv('data/events.csv'),
        'nocs': pd.read_csv('data/nocs.csv'),
        'schedules': pd.read_csv('data/schedules.csv'),  # Note: schedules.csv not schedule.csv
        'venues': pd.read_csv('data/venues.csv'),
        'coaches': pd.read_csv('data/coaches.csv'),
        'medalists': pd.read_csv('data/medallists.csv')  # Note: medallists.csv
    }
    
    # Fix NOCs: rename 'code' to 'country_code' for consistency
    if 'code' in data['nocs'].columns and 'country_code' not in data['nocs'].columns:
        data['nocs']['country_code'] = data['nocs']['code']
    
    # Standardize medal column names in medals_total (they have spaces!)
    if 'Gold Medal' in data['medals_total'].columns:
        data['medals_total'].rename(columns={
            'Gold Medal': 'Gold',
            'Silver Medal': 'Silver',
            'Bronze Medal': 'Bronze'
        }, inplace=True)
    
    return data

def get_continent_from_country_code(country_code):
    """
    Convert a 3-letter country code (NOC) to its continent.
    
    Why? We need continent-level analysis but the dataset only has country codes.
    This uses the pycountry library to map countries to continents.
    """
    if pd.isna(country_code) or country_code == '':
        return 'Unknown'
    
    try:
        # Handle special Olympic codes that aren't standard ISO codes
        special_codes = {
            'ROC': 'Europe',  # Russian Olympic Committee
            'AIN': 'Europe',  # Individual Neutral Athletes
            'EOR': 'Unknown', # Refugee Olympic Team
            'IOP': 'Unknown'  # Independent Olympic Participants
        }
        
        if country_code in special_codes:
            return special_codes[country_code]
        
        country_alpha2 = pc.country_alpha3_to_country_alpha2(country_code)
        continent_code = pc.country_alpha2_to_continent_code(country_alpha2)
        continent_name = pc.convert_continent_code_to_continent_name(continent_code)
        return continent_name
    except:
        return 'Unknown'

def add_continent_column(df, country_col='country_code'):
    """
    Add a 'continent' column to any dataframe that has country codes.
    
    This is essential because many visualizations require continent grouping.
    """
    if country_col in df.columns:
        df['continent'] = df[country_col].apply(get_continent_from_country_code)
    else:
        # If column doesn't exist, add Unknown
        df['continent'] = 'Unknown'
    return df

def apply_filters(df, selected_countries, selected_sports, selected_medals):
    """
    Apply sidebar filters to a dataframe.
    
    Why? Every page needs consistent filtering behavior.
    This function handles the logic once instead of repeating it everywhere.
    """
    filtered_df = df.copy()
    
    if selected_countries and 'country_code' in filtered_df.columns:
        filtered_df = filtered_df[filtered_df['country_code'].isin(selected_countries)]
    
    if selected_sports and 'sport' in filtered_df.columns:
        filtered_df = filtered_df[filtered_df['sport'].isin(selected_sports)]
    
    # Handle different medal column names
    medal_col = None
    if 'medal_type' in filtered_df.columns:
        medal_col = 'medal_type'
    elif 'medal' in filtered_df.columns:
        medal_col = 'medal'
    
    if selected_medals and medal_col:
        filtered_df = filtered_df[filtered_df[medal_col].isin(selected_medals)]
    
    return filtered_df

def create_sidebar_filters(data):
    """
    Create consistent sidebar filters across all pages.
    
    Returns: Dictionary with all selected filter values
    """
    st.sidebar.header("🔍 Global Filters")
    
    # Get unique continents
    if 'country_code' in data['nocs'].columns:
        nocs_with_continent = add_continent_column(data['nocs'].copy(), 'country_code')
        all_continents = sorted([c for c in nocs_with_continent['continent'].unique() if c != 'Unknown'])
        
        selected_continents = st.sidebar.multiselect(
            "Select Continents",
            options=all_continents,
            default=[],
            help="Filter by geographical continents"
        )
    else:
        selected_continents = []
        
    # Country filter - find the right dataframe with country info
    country_df = data['nocs'] if 'country_code' in data['nocs'].columns else data['athletes']
    
    if 'country_code' in country_df.columns:
        all_countries = sorted(country_df['country_code'].dropna().unique())
        selected_countries = st.sidebar.multiselect(
            "Select Countries",
            options=all_countries,
            default=[],
            help="Filter by specific countries (NOC codes)"
        )
    else:
        st.sidebar.warning("⚠️ Country code column not found")
        selected_countries = []
    
    # Sport filter
    if 'sport' in data['events'].columns:
        all_sports = sorted(data['events']['sport'].dropna().unique())
        selected_sports = st.sidebar.multiselect(
            "Select Sports",
            options=all_sports,
            default=[],
            help="Filter by Olympic sports"
        )
    else:
        selected_sports = []
        
    # ---- Gender filter ----
    if 'gender' in data['athletes'].columns:
        all_genders = sorted(data['athletes']['gender'].dropna().unique())
        selected_genders = st.sidebar.multiselect(
            "Select Gender",
            options=all_genders,
            default=[],
            help="Filter by athlete gender"
        )
    else:
        selected_genders = []
    
    # Medal type filter - check what the column is actually called
    medal_df = data['medals']
    medal_col = 'medal_type' if 'medal_type' in medal_df.columns else 'medal'
    
    if medal_col in medal_df.columns:
        # Get actual medal values from data
        unique_medals = medal_df[medal_col].dropna().unique()
        
        # Try to identify gold, silver, bronze (case-insensitive)
        medal_types = []
        for medal in unique_medals:
            medal_lower = str(medal).lower()
            if 'gold' in medal_lower:
                medal_types.append(('Gold', medal))
            elif 'silver' in medal_lower:
                medal_types.append(('Silver', medal))
            elif 'bronze' in medal_lower:
                medal_types.append(('Bronze', medal))
        
        selected_medals = []
        st.sidebar.write("**Medal Types:**")
        
        for display_name, actual_value in medal_types:
            if st.sidebar.checkbox(f"{display_name} Medal", value=True):
                selected_medals.append(actual_value)
    else:
        selected_medals = []
    
    return {
        'countries': selected_countries,
        'sports': selected_sports,
        'genders': selected_genders,
        'medals': selected_medals,
        'continents': selected_continents
    }