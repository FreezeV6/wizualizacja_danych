import pandas as pd
import matplotlib.pyplot as plt

# Ustawienie motywu (theme) dla wykresów
plt.style.use('seaborn-whitegrid')

# Load datasets
races = pd.read_csv('data/races.csv')
drivers = pd.read_csv('data/drivers.csv')
constructors = pd.read_csv('data/constructors.csv')
results = pd.read_csv('data/results.csv')
qualifying = pd.read_csv('data/qualifying.csv')
pit_stops = pd.read_csv('data/pit_stops.csv')
lap_times = pd.read_csv('data/lap_times.csv')
statuses = pd.read_csv('data/status.csv')
driver_standings = pd.read_csv('data/driver_standings.csv')
constructor_standings = pd.read_csv('data/constructor_standings.csv')

# Convert 'position' and 'grid' to numeric for comparisons
results['position'] = pd.to_numeric(results['position'], errors='coerce')
results['grid'] = pd.to_numeric(results['grid'], errors='coerce')

# Merge status descriptions into results
results = results.merge(statuses, on='statusId')

# 1. Liczba wyścigów w każdym sezonie (Races per season)
races_per_season = races.groupby('year').size().reset_index(name='num_races')
plt.figure(figsize=(10, 5))
plt.plot(races_per_season['year'], races_per_season['num_races'], marker='o', linestyle='-')
plt.xlabel('Rok (Year)', fontsize=12)
plt.ylabel('Liczba wyścigów (Number of Races)', fontsize=12)
plt.title('Liczba wyścigów w sezonie', fontsize=14, fontweight='bold')
plt.grid(True, linestyle='--', alpha=0.7)
plt.tight_layout()
plt.show()

# 2. Top 10 kierowców według liczby zwycięstw (Top 10 drivers by wins)
wins = results[results['position'] == 1].groupby('driverId').size().reset_index(name='wins')
wins = wins.merge(drivers[['driverId', 'forename', 'surname']], on='driverId')
wins['driver_name'] = wins['forename'] + ' ' + wins['surname']
top10_drivers_wins = wins.sort_values('wins', ascending=False).head(10)[['driver_name', 'wins']]

print("\nTop 10 Kierowców według liczby zwycięstw:")
print(top10_drivers_wins.to_string(index=False))

plt.figure(figsize=(8, 6))
plt.barh(top10_drivers_wins['driver_name'][::-1], top10_drivers_wins['wins'][::-1])
plt.xlabel('Zwycięstwa (Wins)', fontsize=12)
plt.title('Top 10 Kierowców według liczby zwycięstw', fontsize=14, fontweight='bold')
plt.tight_layout()
plt.show()

# 3. Mistrzowie konstruktorów w każdym sezonie (Constructors champions by year)
final_races = races.loc[races.groupby('year')['round'].idxmax()][['raceId', 'year']]
cs = constructor_standings.merge(final_races, on='raceId')
champions = cs[cs['position'] == 1].merge(constructors[['constructorId', 'name']], on='constructorId')
champions_df = champions[['year', 'name']].sort_values('year')

print("\nMistrzowie Konstruktorów według roku:")
print(champions_df.to_string(index=False))

plt.figure(figsize=(10, 6))
plt.plot(champions_df['year'], range(len(champions_df)), 's')
for idx, row in champions_df.iterrows():
    plt.text(row['year'], row.name, row['name'], fontsize=8, va='bottom')
plt.xlabel('Rok (Year)', fontsize=12)
plt.ylabel('Mistrz Konstruktorów (Index)', fontsize=12)
plt.title('Mistrzowie Konstruktorów w każdym sezonie', fontsize=14, fontweight='bold')
plt.tight_layout()
plt.show()

# 4. Rozkład pozycji startowych (Distribution of grid positions)
plt.figure(figsize=(8, 5))
plt.hist(results['grid'].dropna(), bins=range(int(results['grid'].max())+2), align='left', edgecolor='black')
plt.xlabel('Pozycja startowa (Grid)', fontsize=12)
plt.ylabel('Liczba przypadków (Count)', fontsize=12)
plt.title('Rozkład pozycji startowych kierowców', fontsize=14, fontweight='bold')
plt.tight_layout()
plt.show()

# 5. Pole positions – liczba zdobytych pole position przez kierowcę (Pole position count)
qualifying['position'] = pd.to_numeric(qualifying['position'], errors='coerce')
poles = qualifying[qualifying['position'] == 1].groupby('driverId').size().reset_index(name='pole_positions')
poles = poles.merge(drivers[['driverId', 'forename', 'surname']], on='driverId')
poles['driver_name'] = poles['forename'] + ' ' + poles['surname']
top10_poles = poles.sort_values('pole_positions', ascending=False).head(10)[['driver_name', 'pole_positions']]

print("\nTop 10 Kierowców według liczby pole positions:")
print(top10_poles.to_string(index=False))

plt.figure(figsize=(8, 6))
plt.barh(top10_poles['driver_name'][::-1], top10_poles['pole_positions'][::-1])
plt.xlabel('Pole positions', fontsize=12)
plt.title('Top 10 Kierowców według liczby pole positions', fontsize=14, fontweight='bold')
plt.tight_layout()
plt.show()

# 6. Średni czas postoju na pit stop w ms per kierowcę (Average pit stop duration per driver)
avg_pit = pit_stops.groupby('driverId')['milliseconds'].mean().reset_index(name='avg_pit_ms')
avg_pit = avg_pit.merge(drivers[['driverId', 'forename', 'surname']], on='driverId')
avg_pit['driver_name'] = avg_pit['forename'] + ' ' + avg_pit['surname']
top10_fastest_pit = avg_pit.sort_values('avg_pit_ms').head(10)[['driver_name', 'avg_pit_ms']]

print("\nTop 10 Kierowców według najszybszego średniego czasu pit stop:")
print(top10_fastest_pit.to_string(index=False))

plt.figure(figsize=(8, 6))
plt.barh(top10_fastest_pit['driver_name'][::-1], top10_fastest_pit['avg_pit_ms'][::-1])
plt.xlabel('Średni czas pit stop [ms]', fontsize=12)
plt.title('Top 10 Kierowców według najszybszego średniego czasu pit stop', fontsize=14, fontweight='bold')
plt.tight_layout()
plt.show()

# 7. Liczba zdobytych najszybszych okrążeń (Fastest laps count)
fastest_laps = results[results['rank'] == 1].groupby('driverId').size().reset_index(name='fastest_laps')
fastest_laps = fastest_laps.merge(drivers[['driverId', 'forename', 'surname']], on='driverId')
fastest_laps['driver_name'] = fastest_laps['forename'] + ' ' + fastest_laps['surname']
top10_fastest_laps = fastest_laps.sort_values('fastest_laps', ascending=False).head(10)[['driver_name', 'fastest_laps']]

print("\nTop 10 Kierowców według liczby najszybszych okrążeń:")
print(top10_fastest_laps.to_string(index=False))

plt.figure(figsize=(8, 6))
plt.barh(top10_fastest_laps['driver_name'][::-1], top10_fastest_laps['fastest_laps'][::-1])
plt.xlabel('Liczba najszybszych okrążeń', fontsize=12)
plt.title('Top 10 Kierowców według liczby najszybszych okrążeń', fontsize=14, fontweight='bold')
plt.tight_layout()
plt.show()

# 8. Liczba wycofań (DNF) na kierowcę (DNF count per driver)
dnfs = results[results['status'] != 'Finished'].groupby('driverId').size().reset_index(name='dnf_count')
dnfs = dnfs.merge(drivers[['driverId', 'forename', 'surname']], on='driverId')
dnfs['driver_name'] = dnfs['forename'] + ' ' + dnfs['surname']
top10_dnfs = dnfs.sort_values('dnf_count', ascending=False).head(10)[['driver_name', 'dnf_count']]

print("\nTop 10 Kierowców według liczby DNF:")
print(top10_dnfs.to_string(index=False))

plt.figure(figsize=(8, 6))
plt.barh(top10_dnfs['driver_name'][::-1], top10_dnfs['dnf_count'][::-1])
plt.xlabel('Liczba DNF', fontsize=12)
plt.title('Top 10 Kierowców według liczby wycofań', fontsize=14, fontweight='bold')
plt.tight_layout()
plt.show()

# 9. Średnia poprawa pozycji: grid - finish (Average improvement of position)
valid_positions = results[(results['position'].notna()) & (results['grid'].notna())].copy()
valid_positions['improve'] = valid_positions['grid'] - valid_positions['position']
avg_improve = valid_positions.groupby('driverId')['improve'].mean().reset_index(name='avg_improve')
avg_improve = avg_improve.merge(drivers[['driverId', 'forename', 'surname']], on='driverId')
avg_improve['driver_name'] = avg_improve['forename'] + ' ' + avg_improve['surname']
top10_gainers = avg_improve.sort_values('avg_improve', ascending=False).head(10)[['driver_name', 'avg_improve']]

print("\nTop 10 Kierowców według średniej poprawy pozycji (grid - finish):")
print(top10_gainers.to_string(index=False))

plt.figure(figsize=(8, 6))
plt.barh(top10_gainers['driver_name'][::-1], top10_gainers['avg_improve'][::-1])
plt.xlabel('Średnia poprawa pozycji (grid - finish)', fontsize=12)
plt.title('Top 10 Kierowców według średniej poprawy pozycji', fontsize=14, fontweight='bold')
plt.tight_layout()
plt.show()

# 10. Trend punktowy mistrza ostatniego sezonu (Points trend of the champion of the latest season)
latest_year = races['year'].max()
final_race_latest = races[races['year'] == latest_year].sort_values('round', ascending=False).iloc[0]
champion_info = driver_standings[
    (driver_standings['raceId'] == final_race_latest['raceId']) &
    (driver_standings['position'] == 1)
]
champion_driver_id = champion_info['driverId'].iloc[0]
champion_name_row = drivers[drivers['driverId'] == champion_driver_id].iloc[0]
champion_name = f"{champion_name_row['forename']} {champion_name_row['surname']}"

season_races = races[races['year'] == latest_year][['raceId', 'round', 'name']].sort_values('round')
champion_points = driver_standings[
    (driver_standings['driverId'] == champion_driver_id) &
    (driver_standings['raceId'].isin(season_races['raceId']))
].merge(races[['raceId', 'round', 'name']], on='raceId').sort_values('round')

plt.figure(figsize=(12, 6))
plt.plot(champion_points['round'], champion_points['points'], marker='o', linestyle='-')
plt.xlabel('Runda (Round)', fontsize=12)
plt.ylabel('Punkty (Points)', fontsize=12)
plt.title(f'Trend punktowy {champion_name} w sezonie {latest_year}', fontsize=14, fontweight='bold')
plt.xticks(champion_points['round'], champion_points['name'], rotation=45, ha='right')
plt.tight_layout()
plt.show()

# 11. Rozkład najszybszych okrążeń w każdym wyścigu (Distribution of fastest lap times per race)
fastest_per_race = lap_times.groupby('raceId')['milliseconds'].min().reset_index(name='fastest_lap_ms')
fastest_per_race['fastest_lap_s'] = fastest_per_race['fastest_lap_ms'] / 1000.0

plt.figure(figsize=(8, 5))
plt.hist(fastest_per_race['fastest_lap_s'], bins=20, edgecolor='black')
plt.xlabel('Najszybszy czas okrążenia [s]', fontsize=12)
plt.ylabel('Liczba wyścigów', fontsize=12)
plt.title('Rozkład najszybszych czasów okrążeń w wyścigach', fontsize=14, fontweight='bold')
plt.tight_layout()
plt.show()

