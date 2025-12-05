# 🏅 Paris 2024 Olympics Dashboard

**LA28 Volunteer Selection Challenge Submission**

An interactive, multi-page Streamlit dashboard providing comprehensive analysis of the Paris 2024 Olympic Games dataset.

---

## 📊 Project Overview

This dashboard transforms raw Olympic data into compelling, interactive narratives across four dedicated analytical perspectives:

1. **Overview** - Command center with KPIs and global medal standings
2. **Global Analysis** - Geographical and continental performance insights
3. **Athlete Performance** - Individual athlete profiles and demographic analysis
4. **Sports & Events** - Competition schedules, venues, and sport-specific breakdowns

---

## 🚀 How to Run Locally

### Prerequisites
- Python 3.8 or higher
- pip package manager

### Installation Steps

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd olympic-dashboard
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Download the dataset**
   - Visit: https://www.kaggle.com/datasets/piterfm/paris-2024-olympic-summer-games
   - Download all CSV files
   - Place them in a `data/` folder in the project root

4. **Run the application**
   ```bash
   streamlit run 1_🏠_Overview.py
   ```

5. **Access the dashboard**
   - Open your browser and navigate to `http://localhost:8501`

---

## 🎯 Key Features

### Global Filters (Available on Every Page)
- **Country Selection**: Multi-select filter for specific nations
- **Sport Selection**: Filter by Olympic sports
- **Medal Type**: Toggle Gold, Silver, and Bronze medals
- **Continent Filter**: Creative addition for regional analysis

### Page-Specific Highlights

#### 1. Overview Page
- Real-time KPI metrics (Athletes, Countries, Sports, Medals, Events)
- Global medal distribution (donut chart)
- Top 10 countries ranking (horizontal bar chart)
- Quick insights section

#### 2. Global Analysis Page
- **World Medal Map**: Interactive choropleth showing medal distribution
- **Hierarchical Sunburst**: Drill-down from Continent → Country → Sport → Medal
- **Continental Comparison**: Grouped bar charts by continent
- **Top 20 Countries**: Detailed medal breakdown
- **Treemap**: Alternative hierarchical visualization

#### 3. Athlete Performance Page
- **Searchable Athlete Profiles**: Complete personal information cards with images
- **Age Distribution**: Box/Violin plots by sport or gender
- **Gender Analysis**: Drillable from World → Continent → Country levels
- **Top 10 Medal Winners**: Ranked bar chart with detailed table

#### 4. Sports & Events Page
- **Event Schedule**: Interactive Gantt chart by sport or venue
- **Medal Treemap**: Hierarchical sport and medal type visualization
- **Venue Map**: Scatter mapbox of all Olympic locations in Paris
- **Sport Statistics**: Comparative analysis dashboards
- **Detailed Sport Analysis**: Deep dive into individual sports

---

## 🎨 Design Choices

### Technical Implementation
- **Multi-page architecture**: Leverages Streamlit's native page routing
- **Data caching**: `@st.cache_data` decorator for optimal performance
- **Continent mapping**: Custom utility using `pycountry` libraries
- **Consistent filtering**: Centralized filter logic across all pages

### Visualization Strategy
- **Plotly**: Chosen for interactivity and professional aesthetics
- **Color coding**: Consistent medal colors (Gold: #FFD700, Silver: #C0C0C0, Bronze: #CD7F32)
- **Layout optimization**: Strategic use of columns, tabs, and containers
- **Responsive design**: Mobile-friendly with proper scaling

### User Experience
- **Progressive disclosure**: Start broad (Overview) → drill deep (specific pages)
- **Contextual help**: Tooltips and captions throughout
- **Interactive elements**: Click-to-drill, hover details, dynamic updates
- **Performance**: Cached data loading, efficient filtering

---

## 🌟 Creative Features

### Continent Filter
Added as a "creative challenge" filter allowing users to analyze performance by geographical regions beyond individual countries.

### Hierarchical Visualizations
Both Sunburst and Treemap charts provide intuitive drill-down capabilities, revealing insights at multiple levels of granularity.

### Athlete Profile Cards
Comprehensive athlete search with visual profile cards displaying personal stats, coaches, and medal achievements.

### Multi-level Gender Analysis
Gender distribution viewable at World, Continental, or Country level for comparative demographic insights.

---

## 📦 Project Structure

```
olympic-dashboard/
│
├── 1_🏠_Overview.py                 # Main landing page
├── pages/
│   ├── 2_🗺️_Global_Analysis.py      # Geographical analysis
│   ├── 3_👤_Athlete_Performance.py   # Athlete-focused insights
│   └── 4_🏟️_Sports_and_Events.py    # Competition details
│
├── utils.py                          # Helper functions
├── requirements.txt                  # Python dependencies
├── README.md                         # This file
│
└── data/                             # CSV files (not in repo)
    ├── athletes.csv
    ├── medals.csv
    ├── medals_total.csv
    ├── events.csv
    ├── nocs.csv
    ├── schedule.csv
    ├── venues.csv
    ├── coaches.csv
    └── medalists.csv
```

---

## 🔗 Links

- **GitHub Repository**: https://github.com/S4afou/Test-SEDS
- **Kaggle Dataset**: https://www.kaggle.com/datasets/piterfm/paris-2024-olympic-summer-games

---

## 👥 Team Members

- Medjahri Mohammed Safouane
- Aini Ines

---

## 📝 License

This project is created for educational purposes as part of the Software Engineering for Data Science course at ESI-SBA.

---

## 🙏 Acknowledgments

- Dr. Belkacem KHALDI for project guidance
- Paris 2024 Olympic Games dataset by piterfm on Kaggle
- Streamlit community for excellent documentation
