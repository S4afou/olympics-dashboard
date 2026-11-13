# Paris 2024 Olympics dashboard

A four-page Streamlit dashboard over the Paris 2024 Olympic Games dataset. It turns the raw
CSV exports into four views: the medal table, the geography, the athletes, and the sports
and venues.

## Pages

| Page | What it shows |
| --- | --- |
| Overview | Headline counts (athletes, countries, sports, events, medals), the medal split, and the top ten countries with the current filters applied |
| Global analysis | World medal map, a sunburst from continent to country to sport to medal, continental comparison, and a treemap |
| Athlete performance | Searchable athlete cards, age distribution by sport and gender, gender breakdown at world, continent and country level, and the top ten medallists |
| Sports and events | Event schedule as a Gantt chart, medal treemap by sport, a map of the Paris venues, and per-sport statistics |

## Filters

Four global controls sit above every page: country, sport, medal type and continent. They
are applied to the medal, athlete and country frames before any chart is drawn, so the
headline numbers and the charts always agree.

The continent control is the one addition beyond the assignment. Countries are mapped to
continents with `pycountry`, which keeps the physical-country list small enough to filter on
without a hand-written table.

## Run it

```bash
pip install -r requirements.txt
streamlit run "1_🏠_Overview.py"
```

The app opens on `http://localhost:8501`. The dataset is committed under `data/`, so a clone
runs without a download step.

## Repository layout

```text
1_🏠_Overview.py                    entry point, KPIs and the medal table
pages/2_🗺️_Global_Analysis.py       geography and hierarchy
pages/3_👤_Athlete_Performance.py   athlete search and demographics
pages/4_🏟️_Sports_and_Events.py     schedules, venues and per-sport views
utils.py                            data loading, continent mapping, shared filters
data/                               the Paris 2024 CSV exports
requirements.txt
```

## Data

- Source: Kaggle, "Paris 2024 Olympic Summer Games" by `piterfm`
- Contents: athletes, coaches, events, medallists, medals, medal totals, NOCs, schedules,
  teams, technical officials, venues and per-sport results
- Access: public, check the Kaggle terms before redistributing
- Included here so the dashboard runs from a clone; `data/torch_route.csv` holds the torch
  relay coordinates used on the map

## Stack

Streamlit, pandas, Plotly, pycountry and pycountry-convert for the continent mapping, geopy
for venue coordinates.

## Team and context

Course project for Software Engineering for Data Science at ESI-SBA (2025/2026), taught by
Dr. Belkacem Khaldi. Built by Medjahri Mohammed Safouane and Aini Ines.

## Notes

- All data loading goes through cached loaders in `utils.py`, so switching filters does not
  re-read the CSVs.
- The dashboard is read-only. There is no backend and no database; the CSVs are the source
  of truth.
