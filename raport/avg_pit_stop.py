import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px

# 1. Wczytanie danych
pit_stops    = pd.read_csv('data/pit_stops.csv')
races        = pd.read_csv('data/races.csv')
results      = pd.read_csv('data/results.csv')
constructors = pd.read_csv('data/constructors.csv')

# 2. Filtracja wyścigów z sezonu 2021
races_2021    = races[races['year'] == 2021]
race_ids_2021 = races_2021['raceId']

# 3. Wybranie pit stopów i wyników tylko dla tych wyścigów
pit_stops_2021 = pit_stops[pit_stops['raceId'].isin(race_ids_2021)]
results_2021   = results[results['raceId'].isin(race_ids_2021)][['raceId', 'driverId', 'constructorId']]

# 4. Scalanie pit_stops z results, by wiedzieć, do której drużyny (constructorId) należy każdy pit stop
merged = pd.merge(
    pit_stops_2021,
    results_2021,
    on=['raceId', 'driverId'],
    how='left'
)

# 5. USUNIĘCIE ANOMALII:
#    - Niektóre wpisy w 'duration' mają format "MM:SS.mmm" i w efekcie 'milliseconds' potrafią być > 100 000 (czyli ponad minutę).
#    - Realistyczny czas pit stopu to ok. 20–30 sekund. Ucinamy więc wszystkie z wartością 'milliseconds' > 120 000.
merged_filtered = merged[merged['milliseconds'] <= 120_000]

# 6. Obliczenie średniego czasu pit stopu (ms → s) wg constructorów
avg_ms = merged_filtered.groupby('constructorId')['milliseconds'].mean().reset_index()
avg_ms['seconds'] = avg_ms['milliseconds'] / 1000.0

# 7. Podstawienie nazwy drużyny
avg = pd.merge(
    avg_ms,
    constructors[['constructorId', 'name']],
    on='constructorId',
    how='left'
)
avg_sorted = avg.sort_values('seconds')



# 9. WYKRES SŁUPKOWY W MATPLOTLIB:
plt.figure(figsize=(12, 6))
plt.bar(avg_sorted['name'], avg_sorted['seconds'], color='skyblue')
plt.xlabel('Drużyna')
plt.ylabel('Średni czas pit stopu (sekundy)')
plt.title('Średni czas pit stopu według drużyn w sezonie 2021 (filtr >120s)')
plt.xticks(rotation=45, ha='right')
plt.tight_layout()
plt.show()

# 10. INTERAKTYWNY WYKRES W PLOTLY:
fig = px.bar(
    avg_sorted,
    x='name',
    y='seconds',
    labels={'name': 'Drużyna', 'seconds': 'Średni czas pit stopu (s)'},
    title='Średni czas pit stopu według drużyn w 2021 (po odfiltrowaniu >120s)'
)
fig.update_layout(xaxis_tickangle=-45)
fig.show()
