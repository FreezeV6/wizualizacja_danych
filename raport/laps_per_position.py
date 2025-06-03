import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Wczytanie danych
lap_times = pd.read_csv('data/lap_times.csv')
drivers = pd.read_csv('data/drivers.csv')
races = pd.read_csv('data/races.csv')
seasons = pd.read_csv('data/seasons.csv')

# Parametry
year = 2021  # możesz podmienić na dowolny sezon

# Przygotowanie mapowania driverId -> pełne imię i nazwisko
drivers['driver_name'] = drivers['forename'] + ' ' + drivers['surname']
driver_map = drivers.set_index('driverId')['driver_name']

# Filtrujemy okrążenia z wybranego sezonu
race_ids_2022 = races[races['year'] == year]['raceId']
lap_times_season = lap_times[lap_times['raceId'].isin(race_ids_2022)]

# Zliczanie liczby okrążeń spędzonych na każdej pozycji przez każdego kierowcę
counts = (
    lap_times_season
    .groupby(['driverId', 'position'])
    .size()
    .reset_index(name='laps')
)

# Pivot na format: index=driverId, columns=position
pivot = counts.pivot(index='driverId', columns='position', values='laps').fillna(0)

# Zamiana indexu na nazwy kierowców
pivot.index = pivot.index.map(driver_map)

# Sortowanie według liczby okrążeń na pozycji 1 (malejąco) – Verstappen będzie pierwszy
if 1 in pivot.columns:
    pivot = pivot.sort_values(by=1, ascending=False)

# Upewniamy się, że kolumny (pozycje) są w kolejności rosnącej
pivot = pivot.reindex(sorted(pivot.columns), axis=1)

# Przygotowanie siatki do rysowania pcolormesh
data = pivot.values
n_rows, n_cols = data.shape

# Rysowanie heatmapy z obramowaniami i etykietami w kafelkach
fig, ax = plt.subplots(figsize=(12, 8))
# pcolormesh z wyraźnymi granicami
c = ax.pcolormesh(data, cmap='turbo', edgecolors='white', linewidth=0.5)

# Odwrócenie osi Y, tak żeby pierwszy wiersz (Verstappen) był na górze
ax.invert_yaxis()

# Dodanie liczby okrążeń w środku każdego "kafelka"
for i in range(n_rows):
    for j in range(n_cols):
        # pobieramy wartość
        val = int(data[i, j])
        if val > 0:
            text_color = 'white' if data[i, j] < data.max() / 4 else 'black'
            ax.text(j + 0.5, i + 0.5, val, ha='center', va='center', color=text_color, fontsize=8)

# Ustawienie ticków
ax.set_xticks(np.arange(n_cols) + 0.5)
ax.set_xticklabels(pivot.columns, rotation=0)
ax.set_yticks(np.arange(n_rows) + 0.5)
ax.set_yticklabels(pivot.index)

# Etykiety osi i tytuł
ax.set_xlabel('Pozycja')
ax.set_ylabel('Kierowca')
ax.set_title(f'Liczba okrążeń spędzonych na każdej pozycji przez kierowcę w sezonie {year}')

# Dodanie kolorowej legendy (colorbar)
fig.colorbar(c, ax=ax, label='Liczba okrążeń')

plt.tight_layout()
plt.show()
