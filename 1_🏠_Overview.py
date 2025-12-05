import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from utils import load_data, create_sidebar_filters, add_continent_column

# Page configuration
st.set_page_config(
    page_title="Paris 2024 Olympics Dashboard",
    page_icon="🏅",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
    <style>
    /* Main Header - big & bold with shadow */
    .main-header {
        font-size: 3.5rem;
        font-weight: 900;
        color: #0F172A;  /* dark navy */
        text-align: center;
        padding: 1.5rem 0;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
        font-family: 'Arial Black', sans-serif;
    }

    /* Sub-header - lighter & subtle gradient */
    .sub-header {
        font-size: 1.3rem;
        color: #334155;  /* slate-ish */
        text-align: center;
        padding-bottom: 2.5rem;
        font-style: italic;
        letter-spacing: 0.5px;
        background: linear-gradient(90deg, #6366F1, #3B82F6);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }

    /* Add hover effect to sub-header just for fun */
    .sub-header:hover {
        color: #1E40AF;
        cursor: pointer;
    }
    </style>
""", unsafe_allow_html=True)

# Load data
data = load_data()

# Create sidebar filters
filters = create_sidebar_filters(data)

# Main title
st.markdown('<div class="main-header">🏅 Paris 2024 Olympics Dashboard</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Dive into the ultimate Paris 2024 Olympics Dashboard! Track athletes, medal counts, and event stats in real time. Filter by country, sport, medal type or continent to get the insights you need. Perfect for volunteers, fans, and analysts who want the full picture of the Games!</div>', unsafe_allow_html=True)

st.markdown("---")

# Filter data based on selections
medals_df = data['medals'].copy()
athletes_df = data['athletes'].copy()
events_df = data['events'].copy()
medals_total_df = data['medals_total'].copy()

# Identify the medal column name (could be 'medal_type' or 'medal')
medal_col = 'medal_type' if 'medal_type' in medals_df.columns else 'medal'

# Add continent column for filtering
medals_total_df = add_continent_column(medals_total_df, 'country_code')

# Apply filters
if filters['countries']:
    if 'country_code' in medals_df.columns:
        medals_df = medals_df[medals_df['country_code'].isin(filters['countries'])]
    if 'country_code' in athletes_df.columns:
        athletes_df = athletes_df[athletes_df['country_code'].isin(filters['countries'])]
    if 'country_code' in medals_total_df.columns:
        medals_total_df = medals_total_df[medals_total_df['country_code'].isin(filters['countries'])]

if filters['sports']:
    if 'sport' in events_df.columns:
        events_df = events_df[events_df['sport'].isin(filters['sports'])]
    # Try different column names for sport/discipline
    sport_col = 'discipline' if 'discipline' in medals_df.columns else 'sport'
    if sport_col in medals_df.columns:
        medals_df = medals_df[medals_df[sport_col].isin(filters['sports'])]
        
# --- Gender filter ---
# Map M/F to Male/Female in medals_df
gender_map = {'M': 'Male', 'W': 'Female'}
if 'gender' in medals_df.columns:
    medals_df['gender'] = medals_df['gender'].map(gender_map)

# Filter both athletes_df and medals_df
if filters['genders']:
    if 'gender' in athletes_df.columns:
        athletes_df = athletes_df[athletes_df['gender'].isin(filters['genders'])]
    if 'gender' in medals_df.columns:
        medals_df = medals_df[medals_df['gender'].isin(filters['genders'])]
if filters['continents']:
    if 'continent' in medals_total_df.columns:
        medals_total_df = medals_total_df[medals_total_df['continent'].isin(filters['continents'])]

if filters['medals']:
    if medal_col in medals_df.columns:
        medals_df = medals_df[medals_df[medal_col].isin(filters['medals'])]

# ============= KPI METRICS SECTION =============
st.header("📊 Key Performance Indicators")

col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    total_athletes = athletes_df['name'].nunique()
    st.metric(
        label="👥 Total Athletes",
        value=f"{total_athletes:,}",
        help="Number of unique athletes participating"
    )

with col2:
    if 'country_code' in athletes_df.columns:
        total_countries = athletes_df['country_code'].nunique()
    else:
        total_countries = 0
    st.metric(
        label="🌍 Total Countries",
        value=f"{total_countries}",
        help="Number of participating nations"
    )

with col3:
    total_sports = events_df['sport'].nunique()
    st.metric(
        label="🏃 Total Sports",
        value=f"{total_sports}",
        help="Number of different sports"
    )

with col4:
    total_medals = len(medals_df)
    st.metric(
        label="🥇 Total Medals",
        value=f"{total_medals:,}",
        help="Total medals awarded"
    )

with col5:
    total_events = events_df['event'].nunique()
    st.metric(
        label="🎯 Total Events",
        value=f"{total_events:,}",
        help="Number of competitive events"
    )

st.markdown("---")

# ============= VISUALIZATIONS SECTION =============
col_left, col_right = st.columns(2)

# Left column: Medal Distribution (Donut Chart)
with col_left:
    st.subheader("🥇 Global Medal Distribution")
    
    if len(medals_df) > 0:
        # Count medals by type
        medal_counts = medals_df[medal_col].value_counts().reset_index()
        medal_counts.columns = ['Medal Type', 'Count']
        
        # Create color map based on actual medal names
        color_map = {}
        for medal in medal_counts['Medal Type']:
            medal_lower = str(medal).lower()
            if 'gold' in medal_lower:
                color_map[medal] = '#FFD700'
            elif 'silver' in medal_lower:
                color_map[medal] = '#C0C0C0'
            elif 'bronze' in medal_lower:
                color_map[medal] = '#CD7F32'
            else:
                color_map[medal] = '#888888'
        
        # Create donut chart
        fig_donut = px.pie(
            medal_counts,
            values='Count',
            names='Medal Type',
            hole=0.4,  # This makes it a donut chart
            color='Medal Type',
            color_discrete_map=color_map,
            title="Distribution by Medal Type"
        )
        
        fig_donut.update_traces(
            textposition='inside',
            textinfo='percent+label',
            hovertemplate='<b>%{label}</b><br>Count: %{value}<br>Percentage: %{percent}<extra></extra>'
        )
        
        fig_donut.update_layout(
            showlegend=True,
            height=400
        )
        
        st.plotly_chart(fig_donut, use_container_width=True)
    else:
        st.warning("No medal data available with current filters")

# Right column: Top 10 Medal Standings (Horizontal Bar)
with col_right:
    st.subheader("🏆 Top 10 Countries by Total Medals")
    
    if len(medals_total_df) > 0:
        # Get top 10 countries by total medal count
        if 'Total' in medals_total_df.columns:
            top_countries = medals_total_df.nlargest(10, 'Total')
            country_col_display = 'country' if 'country' in top_countries.columns else 'country_code'
        else:
            # Calculate total if column doesn't exist
            medals_total_df['Total'] = medals_total_df.get('Gold', 0) + medals_total_df.get('Silver', 0) + medals_total_df.get('Bronze', 0)
            top_countries = medals_total_df.nlargest(10, 'Total')
            country_col_display = 'country' if 'country' in top_countries.columns else 'country_code'
        
        if len(top_countries) > 0:
            # Create horizontal bar chart
            fig_bar = px.bar(
                top_countries,
                y=country_col_display,
                x='Total',
                orientation='h',
                text='Total',
                color='Total',
                color_continuous_scale='Viridis',
                title="Medal Count Rankings"
            )
            
            fig_bar.update_traces(
                texttemplate='%{text}',
                textposition='outside',
                hovertemplate='<b>%{y}</b><br>Total Medals: %{x}<extra></extra>'
            )
            
            fig_bar.update_layout(
                yaxis_title="Country",
                xaxis_title="Total Medals",
                showlegend=False,
                height=400,
                yaxis={'categoryorder': 'total ascending'}
            )
            
            st.plotly_chart(fig_bar, use_container_width=True)
        else:
            st.warning("No countries found with current filters")
    else:
        st.warning("No medal total data available with current filters")

# ============= ADDITIONAL INSIGHTS =============
st.markdown("---")
st.header("📈 Quick Insights")

insight_col1, insight_col2, insight_col3 = st.columns(3)

with insight_col1:
    try:
        if len(top_countries) > 0:
            country_name = top_countries.iloc[0].get('country', top_countries.iloc[0].get('country_code', 'N/A'))
            total = top_countries.iloc[0]['Total']
            st.info(f"""
        **🌟 Most Medals Won**
        
        {country_name} leads with {total} total medals!
        """)
        else:
            st.info("""
        **🌟 Most Medals Won**
        
        No data available with current filters
        """)
    except:
        st.warning("No medal data available with current filters")

with insight_col2:
    if 'Gold' in medals_total_df.columns and len(medals_total_df) > 0:
        gold_leader = medals_total_df.nlargest(1, 'Gold')
        if len(gold_leader) > 0:
            country_name = gold_leader.iloc[0].get('country', gold_leader.iloc[0].get('country_code', 'N/A'))
            gold_count = gold_leader.iloc[0]['Gold']
            st.success(f"""
    **🥇 Most Gold Medals**
    
    {country_name} secured {gold_count} gold medals!
    """)
        else:
            st.success("No gold medal data with current filters")
    else:
        st.success("Gold medal data not available")

with insight_col3:
    st.warning(f"""
    **🎭 Event Diversity**
    
    {total_sports} different sports across {total_events} events!
    """)

st.markdown("---")
st.caption("💡 Use the sidebar filters to explore specific countries, sports, or medal types. Navigate to other pages for deeper analysis!")