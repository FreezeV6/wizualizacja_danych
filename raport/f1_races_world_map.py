import pandas as pd
import plotly.express as px

# 1) Wczytanie danych
races = pd.read_csv('data/races.csv')
circuits = pd.read_csv('data/circuits.csv')

# 2) Wybranie wyścigów z sezonu 2021
races_2021 = races[races['year'] == 2021]

# 3) Połączenie z danymi o torach: chcemy lat/lng oraz kraj toru
merged = races_2021.merge(
    circuits[['circuitId', 'circuitRef', 'lat', 'lng', 'name', 'country']],
    on='circuitId',
    how='left',
    suffixes=('_race', '_circuit')
)

# Zmiana nazw kolumn, żeby było czytelniej
merged = merged.rename(columns={
    'name_race': 'race_name',
    'name_circuit': 'circuit_name',
    'circuitRef': 'circuit_ref',
    'lat': 'latitude',
    'lng': 'longitude'
})

# 4) Przygotowanie etykiety (hover) w formacie: "Nazwa Wyścigu - Nazwa Toru (Kraj)"
merged['label'] = merged['race_name'] + " - " + merged['circuit_name'] + " (" + merged['country'] + ")"

# 5) Rysowanie mapy w Plotly
fig = px.scatter_geo(
    merged,
    lat='latitude',
    lon='longitude',
    hover_name='label',
    projection='natural earth',
    title='F1 2021 Season Race Locations',
    scope='world'
)

fig.show()
