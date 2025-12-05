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

# Apply filters
if filters['countries']:
    medals_total_df = medals_total_df[medals_total_df['country_code'].isin(filters['countries'])]
    medals_df = medals_df[medals_df['country_code'].isin(filters['countries'])]

if filters['sports']:
    medals_df = medals_df[medals_df['discipline'].isin(filters['sports'])]

if filters['continents']:
    medals_total_df = medals_total_df[medals_total_df['continent'].isin(filters['continents'])]
    medals_df = medals_df[medals_df['continent'].isin(filters['continents'])]

if filters['medals']:
    medals_df = medals_df[medals_df['medal_type'].isin(filters['medals'])]

# ============= WORLD MEDAL MAP (CHOROPLETH) =============
st.header("🌍 World Medal Map")
st.markdown("Countries colored by total medal count")

# Create choropleth map
fig_map = px.choropleth(
    medals_total_df,
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
    title='Medal Distribution Across the Globe',
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

st.markdown("---")

# ============= MEDAL HIERARCHY (SUNBURST) =============
st.header("☀️ Medal Hierarchy by Continent")
st.markdown("Drill down from Continent → Country → Sport → Medal Count")

# Prepare data for sunburst: need hierarchy
sunburst_data = medals_df.groupby(
    ['continent', 'country', 'discipline', 'medal_type']
).size().reset_index(name='medal_count')

# Create sunburst chart
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

st.markdown("---")

# ============= CONTINENT VS MEDALS (BAR CHART) =============
st.header("🌏 Continental Medal Comparison")

# Aggregate medals by continent
continent_medals = medals_total_df.groupby('continent')[['Gold', 'Silver', 'Bronze']].sum().reset_index()

# Create grouped bar chart
fig_continent = go.Figure()

fig_continent.add_trace(go.Bar(
    name='Gold',
    x=continent_medals['continent'],
    y=continent_medals['Gold'],
    marker_color='#FFD700',
    hovertemplate='<b>%{x}</b><br>Gold: %{y}<extra></extra>'
))

fig_continent.add_trace(go.Bar(
    name='Silver',
    x=continent_medals['continent'],
    y=continent_medals['Silver'],
    marker_color='#C0C0C0',
    hovertemplate='<b>%{x}</b><br>Silver: %{y}<extra></extra>'
))

fig_continent.add_trace(go.Bar(
    name='Bronze',
    x=continent_medals['continent'],
    y=continent_medals['Bronze'],
    marker_color='#CD7F32',
    hovertemplate='<b>%{x}</b><br>Bronze: %{y}<extra></extra>'
))

fig_continent.update_layout(
    title='Medal Count by Continent',
    xaxis_title='Continent',
    yaxis_title='Medal Count',
    barmode='group',
    hovermode='x unified',
    height=400
)

st.plotly_chart(fig_continent, use_container_width=True)

st.markdown("---")

# ============= TOP 20 COUNTRIES (BAR CHART) =============
st.header("🏆 Top 20 Countries Medal Breakdown")

# Get top 20 countries
top_20 = medals_total_df.nlargest(20, 'Total')

# Create grouped bar chart
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
    title='Medal Distribution for Top 20 Nations',
    xaxis_title='Country',
    yaxis_title='Medal Count',
    barmode='group',
    hovermode='x unified',
    height=500,
    xaxis={'tickangle': -45}
)

st.plotly_chart(fig_top20, use_container_width=True)

# ============= TREEMAP ALTERNATIVE =============
st.markdown("---")
st.header("📦 Continental Medal Treemap")
st.markdown("Alternative hierarchical view with size representing medal count")

# Create treemap
treemap_data = medals_df.groupby(['continent', 'country', 'discipline']).size().reset_index(name='medal_count')

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

st.caption("💡 Click on sections in the Sunburst or Treemap to drill down into specific regions!")