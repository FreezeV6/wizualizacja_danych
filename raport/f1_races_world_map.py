import pandas as pd
import plotly.graph_objects as go
import flagpy as fp
import io
import base64

# Load data
races = pd.read_csv('data/races.csv')
circuits = pd.read_csv('data/circuits.csv')

# Filter for 2021 season and merge with circuits
races_2021 = races[races['year'] == 2021]
merged = races_2021.merge(
    circuits[['circuitId', 'circuitRef', 'lat', 'lng', 'name', 'country']],
    on='circuitId',
    how='left'
).rename(columns={
    'name_x': 'race_name',
    'name_y': 'circuit_name',
    'lat': 'latitude',
    'lng': 'longitude'
})

# Function to get flag image, convert to base64 URL
def get_flag_url(country_name: str) -> str:
    try:
        img = fp.get_flag_img(country_name)  # PIL Image
        buffered = io.BytesIO()
        img.save(buffered, format="PNG")
        img_str = base64.b64encode(buffered.getvalue()).decode()
        return f"data:image/png;base64,{img_str}"
    except:
        return None

# Generate URLs for each country's flag
merged['flag_url'] = merged['country'].apply(get_flag_url)

# Prepare hover text
merged['hover_text'] = merged['race_name'] + " – " + merged['circuit_name'] + " (" + merged['country'] + ")"

# Create ScatterGeo with custom marker symbols (flags)
fig = go.Figure()

fig.add_trace(go.Scattergeo(
    lat=merged['latitude'],
    lon=merged['longitude'],
    hovertext=merged['hover_text'],
    hoverinfo="text",
    mode='markers',
    marker=dict(
        size=20,  # adjust size to fit flag icons
        symbol=merged['flag_url']  # custom symbol per point
    ),
))

fig.update_layout(
    title='F1 2021 Season Race Locations with Country Flag Images',
    geo=dict(
        projection_type='natural earth',
        showland=True,
    )
)

fig.show()
