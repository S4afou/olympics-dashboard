import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from utils import load_data, create_sidebar_filters, add_continent_column

# Page configuration
st.set_page_config(
    page_title="Athlete Performance - Paris 2024",
    page_icon="👤",
    layout="wide"
)

st.title("👤 Athlete Performance: The Human Story")
st.markdown("Dive deep into athlete demographics, achievements, and personal profiles")
st.markdown("---")

# Load data
data = load_data()
filters = create_sidebar_filters(data)

athletes_df = data['athletes'].copy()
medals_df = data['medals'].copy()
medalists_df = data['medalists'].copy()
coaches_df = data['coaches'].copy()

# Add continent info
athletes_df = add_continent_column(athletes_df, 'country_code')

# Apply filters
if filters['countries']:
    athletes_df = athletes_df[athletes_df['country_code'].isin(filters['countries'])]
    medals_df = medals_df[medals_df['country_code'].isin(filters['countries'])]

if filters['sports']:
    athletes_df = athletes_df[athletes_df['disciplines'].str.contains('|'.join(filters['sports']), na=False)]

# ============= ATHLETE PROFILE CARD =============
st.header("🔍 Detailed Athlete Profile")

# Create searchable athlete selector
athlete_names = sorted(athletes_df['name'].dropna().unique())
selected_athlete = st.selectbox(
    "Search and select an athlete",
    options=[""] + athlete_names,
    help="Start typing to search for an athlete"
)

if selected_athlete:
    # Get athlete details
    athlete_info = athletes_df[athletes_df['name'] == selected_athlete].iloc[0]
    
    # Create profile card layout
    profile_col1, profile_col2 = st.columns([1, 3])
    
    with profile_col1:
        # Display image or placeholder - athletes.csv doesn't have 'url' column
        # Check if there's any image column
        if 'image' in athlete_info.index and pd.notna(athlete_info.get('image')):
            st.image(athlete_info['image'], width=200)
        else:
            st.markdown("""
                <div style='
                    width: 200px; 
                    height: 200px; 
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    border-radius: 10px;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    font-size: 80px;
                '>
                    🏃
                </div>
            """, unsafe_allow_html=True)
    
    with profile_col2:
        st.markdown(f"### {athlete_info['name']}")
        
        # Get country flag emoji
        country_flag = athlete_info.get('country', '')
        st.markdown(f"**Country:** {country_flag} {athlete_info['country_code']}")
        
        # Physical stats
        col_a, col_b, col_c = st.columns(3)
        with col_a:
            height = athlete_info.get('height', 'N/A')
            st.metric("Height", f"{height} cm" if pd.notna(height) else "N/A")
        with col_b:
            weight = athlete_info.get('weight', 'N/A')
            st.metric("Weight", f"{weight} kg" if pd.notna(weight) else "N/A")
        with col_c:
            gender = athlete_info.get('gender', 'N/A')
            st.metric("Gender", gender)
        
        # Sports & Disciplines
        disciplines = athlete_info.get('disciplines', 'N/A')
        st.markdown(f"**Sports & Disciplines:** {disciplines}")
        
        # Coach information
        coach = athlete_info.get('coach', 'N/A')
        if pd.notna(coach) and coach != 'N/A':
            st.markdown(f"**Coach:** {coach}")
        
        # Find athlete code
        athlete_code = athlete_info.get('code', '')
        st.markdown(f"**Athlete Code:** {athlete_code}")
        
        # Check medals
        athlete_medals = medals_df[medals_df['name'] == selected_athlete]
        if not athlete_medals.empty:
            medal_count = len(athlete_medals)
            st.success(f"🏅 **Medals Won:** {medal_count}")
            
            medal_types = athlete_medals['medal_type'].value_counts()
            medal_str = ", ".join([f"{count} {medal}" for medal, count in medal_types.items()])
            st.write(medal_str)
        else:
            st.info("No medals won at Paris 2024")

st.markdown("---")

# ============= AGE DISTRIBUTION (BOX PLOT) =============
st.header("📊 Age Distribution Analysis")

# Calculate age (birth_date is in the dataset)
if 'birth_date' in athletes_df.columns:
    athletes_df['birth_date'] = pd.to_datetime(athletes_df['birth_date'], errors='coerce')
    athletes_df['age'] = 2024 - athletes_df['birth_date'].dt.year
    
    # Remove invalid ages (negative or unrealistic)
    athletes_df = athletes_df[(athletes_df['age'] > 10) & (athletes_df['age'] < 100)]

# Create age distribution by sport or gender
if 'age' in athletes_df.columns and not athletes_df['age'].isna().all():
    viz_choice = st.radio("View age distribution by:", ["Sport", "Gender"], horizontal=True)

    if viz_choice == "Sport":
        # Parse disciplines column safely (it's a string representation of a list)
        def parse_discipline(disc_str):
            """Safely parse discipline string to extract first sport"""
            if pd.isna(disc_str):
                return None
            if isinstance(disc_str, str):
                # Remove brackets and quotes, split by comma, take first
                clean = disc_str.strip("[]'\"")
                if ',' in clean:
                    return clean.split(',')[0].strip("'\"")
                return clean.strip("'\"")
            return str(disc_str)
        
        athletes_df['disciplines_parsed'] = athletes_df['disciplines'].apply(parse_discipline)
        
        # Get top 10 sports by participant count
        top_sports = athletes_df['disciplines_parsed'].value_counts().head(10).index.tolist()
        athletes_sport = athletes_df[athletes_df['disciplines_parsed'].isin(top_sports)].copy()
        
        if len(athletes_sport) > 0:
            fig_age = px.box(
                athletes_sport,
                x='disciplines_parsed',
                y='age',
                color='disciplines_parsed',
                title='Age Distribution by Sport (Top 10 Sports)',
                labels={'disciplines_parsed': 'Sport', 'age': 'Age (years)'},
                points='outliers'
            )
            
            fig_age.update_layout(
                xaxis_tickangle=-45,
                showlegend=False,
                height=500,
                xaxis_title='Sport',
                yaxis_title='Age (years)'
            )
            
            st.plotly_chart(fig_age, use_container_width=True)
        else:
            st.warning("No sport data available with current filters")
        
    else:  # Gender
        if 'gender' in athletes_df.columns:
            athletes_gender = athletes_df.dropna(subset=['age', 'gender'])
            
            if len(athletes_gender) > 0:
                fig_age = px.violin(
                    athletes_gender,
                    x='gender',
                    y='age',
                    color='gender',
                    box=True,
                    title='Age Distribution by Gender',
                    labels={'gender': 'Gender', 'age': 'Age (years)'},
                    color_discrete_map={'Male': '#3B82F6', 'Female': '#EC4899'}
                )
                
                fig_age.update_layout(
                    height=500,
                    showlegend=True
                )
                
                st.plotly_chart(fig_age, use_container_width=True)
                
                # Show statistics
                col_stats1, col_stats2 = st.columns(2)
                
                with col_stats1:
                    male_avg = athletes_gender[athletes_gender['gender'] == 'Male']['age'].mean()
                    st.metric("Average Age (Male)", f"{male_avg:.1f} years")
                
                with col_stats2:
                    female_avg = athletes_gender[athletes_gender['gender'] == 'Female']['age'].mean()
                    st.metric("Average Age (Female)", f"{female_avg:.1f} years")
            else:
                st.warning("No gender/age data available")
        else:
            st.warning("Gender column not found")

else:
    st.warning("Age data not available in the dataset. Birth dates may be missing.")
    st.info("💡 The athletes.csv file needs valid birth_date values to calculate ages.")

st.markdown("---")

# ============= GENDER DISTRIBUTION =============
st.header("⚖️ Gender Distribution Analysis")

# Add continent/country filter for gender analysis
geo_level = st.radio("Analyze gender distribution by:", ["World", "Continent", "Country"], horizontal=True)

if geo_level == "World":
    gender_counts = athletes_df['gender'].value_counts().reset_index()
    gender_counts.columns = ['Gender', 'Count']
    title = "Global Gender Distribution"
    
elif geo_level == "Continent":
    selected_cont = st.selectbox("Select Continent", sorted(athletes_df['continent'].unique()))
    continent_athletes = athletes_df[athletes_df['continent'] == selected_cont]
    gender_counts = continent_athletes['gender'].value_counts().reset_index()
    gender_counts.columns = ['Gender', 'Count']
    title = f"Gender Distribution in {selected_cont}"
    
else:  # Country
    selected_country = st.selectbox("Select Country", sorted(athletes_df['country_code'].unique()))
    country_athletes = athletes_df[athletes_df['country_code'] == selected_country]
    gender_counts = country_athletes['gender'].value_counts().reset_index()
    gender_counts.columns = ['Gender', 'Count']
    title = f"Gender Distribution in {selected_country}"

# Create pie chart
fig_gender = px.pie(
    gender_counts,
    names='Gender',
    values='Count',
    title=title,
    color='Gender',
    color_discrete_map={'Male': '#3B82F6', 'Female': '#EC4899'},
    hole=0.3
)

fig_gender.update_traces(
    textposition='inside',
    textinfo='percent+label+value'
)

st.plotly_chart(fig_gender, use_container_width=True)

st.markdown("---")

# ============= TOP ATHLETES BY MEDALS =============
st.header("🏆 Top 10 Athletes by Medal Count")

# Count medals per athlete
athlete_medal_counts = medals_df.groupby('name').agg({
    'medal_type': 'count',
    'country': 'first',
    'country_code': 'first'
}).reset_index()

athlete_medal_counts.columns = ['Athlete', 'Total Medals', 'Country', 'Country Code']
athlete_medal_counts = athlete_medal_counts.sort_values('Total Medals', ascending=False).head(10)

# Create bar chart
fig_top_athletes = px.bar(
    athlete_medal_counts,
    x='Total Medals',
    y='Athlete',
    orientation='h',
    text='Total Medals',
    color='Total Medals',
    color_continuous_scale='Plasma',
    title='Top 10 Medal Winners',
    hover_data=['Country']
)

fig_top_athletes.update_traces(
    textposition='outside'
)

fig_top_athletes.update_layout(
    yaxis={'categoryorder': 'total ascending'},
    height=500,
    showlegend=False
)

st.plotly_chart(fig_top_athletes, use_container_width=True)

# Display detailed table
st.subheader("📋 Detailed Medal Breakdown")
st.dataframe(
    athlete_medal_counts,
    use_container_width=True,
    hide_index=True
)

st.caption("💡 Use the athlete search at the top to view detailed profiles of specific competitors!")