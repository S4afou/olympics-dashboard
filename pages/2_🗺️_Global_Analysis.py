import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from utils import load_data, create_sidebar_filters, add_continent_column

# Page configuration
st.set_page_config(
    page_title="Global Analysis - Paris 2024",
    page_icon="🗺️",
    layout="wide"
)

st.title("🗺️ Global Analysis: The World View")
st.markdown("Explore Olympic performance from a geographical and continental perspective")
st.markdown("---")

# Load data
data = load_data()
filters = create_sidebar_filters(data)

# Prepare datasets
medals_total_df = data['medals_total'].copy()
medals_df = data['medals'].copy()

# Add continent information
medals_total_df = add_continent_column(medals_total_df, 'country_code')
medals_df = add_continent_column(medals_df, 'country_code')

# Create gender_display for visualization (keep original for filtering)
gender_map = {'M': 'Male', 'W': 'Female'}
if 'gender' in medals_df.columns:
    medals_df['gender_display'] = medals_df['gender'].map(gender_map).fillna(medals_df['gender'])

# Apply Country filter
if filters.get('countries'):
    medals_total_df = medals_total_df[medals_total_df['country_code'].isin(filters['countries'])]
    medals_df = medals_df[medals_df['country_code'].isin(filters['countries'])]

# Apply Sport filter
if filters.get('sports'):
    medals_df = medals_df[medals_df['discipline'].isin(filters['sports'])]

# Apply Continent filter
if filters.get('continents'):
    medals_total_df = medals_total_df[medals_total_df['continent'].isin(filters['continents'])]
    medals_df = medals_df[medals_df['continent'].isin(filters['continents'])]

# Apply Gender filter (filter returns 'Male'/'Female', filter on gender_display)
if filters.get('genders'):
    medals_df = medals_df[medals_df['gender_display'].isin(filters['genders'])]

# Apply Medal Type filter
if filters.get('medals'):
    medals_df = medals_df[medals_df['medal_type'].isin(filters['medals'])]

# ============= WORLD MEDAL MAP (CHOROPLETH) =============
st.header("🌍 World Medal Map")
st.markdown("Countries colored by total medal count")

if len(medals_df) > 0:
    # Calculate medal totals from filtered medals_df (includes ALL filters: sport, gender, etc.)
    map_data = medals_df.groupby(['country_code', 'country', 'medal_type']).size().reset_index(name='count')
    
    # Pivot to get Gold, Silver, Bronze columns
    map_pivot = map_data.pivot_table(
        index=['country_code', 'country'],
        columns='medal_type',
        values='count',
        fill_value=0
    ).reset_index()
    
    # Calculate total
    medal_columns = [col for col in map_pivot.columns if 'Medal' in str(col)]
    map_pivot['Total'] = map_pivot[medal_columns].sum(axis=1)
    
    # Rename medal columns for display
    map_pivot.columns = [col.replace(' Medal', '') if 'Medal' in str(col) else col for col in map_pivot.columns]
    
    # Ensure we have Gold, Silver, Bronze columns
    for medal_type in ['Gold', 'Silver', 'Bronze']:
        if medal_type not in map_pivot.columns:
            map_pivot[medal_type] = 0
    
    fig_map = px.choropleth(
        map_pivot,
        locations='country_code',
        locationmode='ISO-3',
        color='Total',
        hover_name='country',
        hover_data={
            'country_code': False,
            'Gold': True,
            'Silver': True,
            'Bronze': True,
            'Total': True
        },
        color_continuous_scale='YlOrRd',
        title='Medal Distribution Across the Globe (Filtered)',
        labels={'Total': 'Total Medals'}
    )

    fig_map.update_layout(
        geo=dict(
            showframe=False,
            showcoastlines=True,
            projection_type='natural earth'
        ),
        height=500
    )

    st.plotly_chart(fig_map, use_container_width=True)
else:
    st.warning("No data available with current filters for the world map")

st.markdown("---")

# ============= MEDAL HIERARCHY (SUNBURST) =============
st.header("☀️ Medal Hierarchy by Continent")
st.markdown("Drill down from Continent → Country → Sport → Medal Count")

if len(medals_df) > 0:
    # Prepare data for sunburst: need hierarchy
    sunburst_data = medals_df.groupby(
        ['continent', 'country', 'discipline', 'medal_type']
    ).size().reset_index(name='medal_count')

    if len(sunburst_data) > 0:
        fig_sunburst = px.sunburst(
            sunburst_data,
            path=['continent', 'country', 'discipline', 'medal_type'],
            values='medal_count',
            color='medal_count',
            color_continuous_scale='RdYlGn',
            title='Hierarchical Medal Distribution'
        )

        fig_sunburst.update_traces(
            textinfo='label+percent parent',
            hovertemplate='<b>%{label}</b><br>Medals: %{value}<br>%{percentParent}<extra></extra>'
        )

        fig_sunburst.update_layout(height=600)

        st.plotly_chart(fig_sunburst, use_container_width=True)
    else:
        st.warning("No hierarchical data available with current filters")
else:
    st.warning("No medal data available with current filters for the sunburst chart")

st.markdown("---")

# ============= CONTINENT VS MEDALS (BAR CHART) =============
st.header("🌏 Continental Medal Comparison")

if len(medals_df) > 0:
    # Calculate from filtered medals_df (includes ALL filters)
    continent_medal_data = medals_df.groupby(['continent', 'medal_type']).size().reset_index(name='count')
    
    # Pivot to get medal types as columns
    continent_pivot = continent_medal_data.pivot_table(
        index='continent',
        columns='medal_type',
        values='count',
        fill_value=0
    ).reset_index()
    
    # Rename columns
    continent_pivot.columns = [col.replace(' Medal', '') if 'Medal' in str(col) else col for col in continent_pivot.columns]
    
    # Ensure we have Gold, Silver, Bronze columns
    for medal_type in ['Gold', 'Silver', 'Bronze']:
        if medal_type not in continent_pivot.columns:
            continent_pivot[medal_type] = 0

    if len(continent_pivot) > 0:
        fig_continent = go.Figure()

        fig_continent.add_trace(go.Bar(
            name='Gold',
            x=continent_pivot['continent'],
            y=continent_pivot['Gold'],
            marker_color='#FFD700',
            hovertemplate='<b>%{x}</b><br>Gold: %{y}<extra></extra>'
        ))

        fig_continent.add_trace(go.Bar(
            name='Silver',
            x=continent_pivot['continent'],
            y=continent_pivot['Silver'],
            marker_color='#C0C0C0',
            hovertemplate='<b>%{x}</b><br>Silver: %{y}<extra></extra>'
        ))

        fig_continent.add_trace(go.Bar(
            name='Bronze',
            x=continent_pivot['continent'],
            y=continent_pivot['Bronze'],
            marker_color='#CD7F32',
            hovertemplate='<b>%{x}</b><br>Bronze: %{y}<extra></extra>'
        ))

        fig_continent.update_layout(
            title='Medal Count by Continent (Filtered)',
            xaxis_title='Continent',
            yaxis_title='Medal Count',
            barmode='group',
            hovermode='x unified',
            height=400
        )

        st.plotly_chart(fig_continent, use_container_width=True)
    else:
        st.warning("No continent data available with current filters")
else:
    st.warning("No medal data available with current filters for continental comparison")

st.markdown("---")

# ============= TOP 20 COUNTRIES (BAR CHART) =============
st.header("🏆 Top 20 Countries Medal Breakdown")

if len(medals_df) > 0:
    # Calculate from filtered medals_df (includes ALL filters: sport, gender, etc.)
    country_medal_data = medals_df.groupby(['country', 'country_code', 'medal_type']).size().reset_index(name='count')
    
    # Pivot to get medal types as columns
    country_pivot = country_medal_data.pivot_table(
        index=['country', 'country_code'],
        columns='medal_type',
        values='count',
        fill_value=0
    ).reset_index()
    
    # Rename columns
    country_pivot.columns = [col.replace(' Medal', '') if 'Medal' in str(col) else col for col in country_pivot.columns]
    
    # Ensure we have Gold, Silver, Bronze columns
    for medal_type in ['Gold', 'Silver', 'Bronze']:
        if medal_type not in country_pivot.columns:
            country_pivot[medal_type] = 0
    
    # Calculate total
    country_pivot['Total'] = country_pivot['Gold'] + country_pivot['Silver'] + country_pivot['Bronze']
    
    # Get top 20 countries
    top_20 = country_pivot.nlargest(20, 'Total')

    if len(top_20) > 0:
        fig_top20 = go.Figure()

        fig_top20.add_trace(go.Bar(
            name='Gold',
            x=top_20['country'],
            y=top_20['Gold'],
            marker_color='#FFD700',
            text=top_20['Gold'],
            textposition='auto'
        ))

        fig_top20.add_trace(go.Bar(
            name='Silver',
            x=top_20['country'],
            y=top_20['Silver'],
            marker_color='#C0C0C0',
            text=top_20['Silver'],
            textposition='auto'
        ))

        fig_top20.add_trace(go.Bar(
            name='Bronze',
            x=top_20['country'],
            y=top_20['Bronze'],
            marker_color='#CD7F32',
            text=top_20['Bronze'],
            textposition='auto'
        ))

        fig_top20.update_layout(
            title='Medal Distribution for Top 20 Nations (Filtered)',
            xaxis_title='Country',
            yaxis_title='Medal Count',
            barmode='group',
            hovermode='x unified',
            height=500,
            xaxis={'tickangle': -45}
        )

        st.plotly_chart(fig_top20, use_container_width=True)
    else:
        st.warning("No countries available with current filters")
else:
    st.warning("No medal data available with current filters for top countries")

# ============= TREEMAP ALTERNATIVE =============
st.markdown("---")
st.header("📦 Continental Medal Treemap")
st.markdown("Alternative hierarchical view with size representing medal count")

if len(medals_df) > 0:
    # Create treemap
    treemap_data = medals_df.groupby(['continent', 'country', 'discipline']).size().reset_index(name='medal_count')

    if len(treemap_data) > 0:
        fig_treemap = px.treemap(
            treemap_data,
            path=['continent', 'country', 'discipline'],
            values='medal_count',
            color='medal_count',
            color_continuous_scale='Bluered',
            title='Treemap: Continent → Country → Sport'
        )

        fig_treemap.update_traces(
            textinfo='label+value',
            hovertemplate='<b>%{label}</b><br>Medals: %{value}<extra></extra>'
        )

        fig_treemap.update_layout(height=600)

        st.plotly_chart(fig_treemap, use_container_width=True)
    else:
        st.warning("No treemap data available with current filters")
else:
    st.warning("No medal data available with current filters for treemap")

st.caption("💡 Click on sections in the Sunburst or Treemap to drill down into specific regions!")