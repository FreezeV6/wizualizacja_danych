import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px

# Ustawienie stylu wykresów
plt.style.use('seaborn-deep')

# -------------- Wczytanie danych --------------
seasons = pd.read_csv('data/seasons.csv')
races = pd.read_csv('data/races.csv')
drivers = pd.read_csv('data/drivers.csv')
constructors = pd.read_csv('data/constructors.csv')
results = pd.read_csv('data/results.csv')
driver_standings = pd.read_csv('data/driver_standings.csv')
constructor_standings = pd.read_csv('data/constructor_standings.csv')
qualifying = pd.read_csv('data/qualifying.csv')
circuits = pd.read_csv('data/circuits.csv')
status = pd.read_csv('data/status.csv')
pit_stops = pd.read_csv('data/pit_stops.csv')

# 1. Liczba wyścigów w sezonie
races_per_season = races.groupby('year')['raceId'].count().reset_index(name='num_races')

plt.figure(figsize=(10, 6))
plt.plot(races_per_season['year'], races_per_season['num_races'], marker='o', color='tab:blue')
plt.title('Number of Races per Season', fontsize=14)
plt.xlabel('Year', fontsize=12)
plt.ylabel('Number of Races', fontsize=12)
plt.grid(False)
plt.tight_layout()
plt.show()

# 2. Top 10 kierowców według liczby zwycięstw (korekta: używamy positionOrder == 1)
wins = results[results['positionOrder'] == 1]
driver_wins = wins.groupby('driverId')['raceId'].count().reset_index(name='wins')
top10_drivers = driver_wins.merge(drivers, on='driverId')
top10_drivers['full_name'] = top10_drivers['forename'] + ' ' + top10_drivers['surname']
top10_drivers = top10_drivers.sort_values(by='wins', ascending=False).head(10)[['full_name', 'wins']]

plt.figure(figsize=(10, 6))
bars = plt.barh(top10_drivers['full_name'][::-1], top10_drivers['wins'][::-1], color=plt.cm.viridis(range(10)))
plt.title('Top 10 Drivers by Number of Wins', fontsize=14)
plt.xlabel('Wins', fontsize=12)
plt.ylabel('Driver', fontsize=12)
plt.tight_layout()
plt.show()

# 3. Top 10 zespołów według liczby tytułów mistrza konstruktorów
last_race_per_season = races.groupby('year')['round'].max().reset_index()
last_races = races.merge(last_race_per_season, on=['year', 'round'])
final_race_ids = last_races['raceId']

champ_winners = constructor_standings[constructor_standings['raceId'].isin(final_race_ids)]
champ_winners = champ_winners[champ_winners['position'] == 1]
champ_counts = champ_winners.groupby('constructorId')['raceId'].count().reset_index(name='championship_wins')
top10_teams = champ_counts.merge(constructors, on='constructorId')[['name', 'championship_wins']]
top10_teams = top10_teams.sort_values(by='championship_wins', ascending=False).head(10)

plt.figure(figsize=(10, 6))
bars = plt.barh(top10_teams['name'][::-1], top10_teams['championship_wins'][::-1], color=plt.cm.plasma(range(10)))
plt.title('Top 10 Teams by Constructor Championship Wins', fontsize=14)
plt.xlabel('Championship Wins', fontsize=12)
plt.ylabel('Team', fontsize=12)
plt.tight_layout()
plt.show()

# 4. Zależność pozycji startowych od wygranych na poszczególnych torach (korekta: positionOrder == 1)
winners = results[results['positionOrder'] == 1][['raceId', 'driverId', 'grid']]
winners_with_track = winners.merge(races[['raceId', 'circuitId']], on='raceId')
winners_with_track = winners_with_track.merge(circuits[['circuitId', 'name']], on='circuitId')
avg_grid_per_circuit = winners_with_track.groupby('name')['grid'].mean().reset_index(name='average_grid')

plt.figure(figsize=(12, 8))
bars = plt.barh(avg_grid_per_circuit['name'], avg_grid_per_circuit['average_grid'], color=plt.cm.inferno(range(len(avg_grid_per_circuit))))
plt.title('Average Starting Grid Position for Winners by Circuit', fontsize=14)
plt.xlabel('Average Starting Grid Position', fontsize=12)
plt.ylabel('Circuit', fontsize=12)
plt.tight_layout()
plt.show()

# 5. Średni czas pit stopu według drużyny (mapowanie 'Jaguar' → 'Red Bull')
pit_with_results = pit_stops.merge(results[['raceId', 'driverId', 'constructorId']], on=['raceId', 'driverId'])
pit_with_constructors = pit_with_results.merge(constructors[['constructorId', 'name']], on='constructorId')
pit_with_constructors['team_name'] = pit_with_constructors['name'].replace({'Jaguar': 'Red Bull'})
avg_pit_time = pit_with_constructors.groupby('team_name')['milliseconds'].mean().reset_index(name='avg_pit_duration_ms')
avg_pit_time_sorted = avg_pit_time.sort_values(by='avg_pit_duration_ms')

plt.figure(figsize=(12, 8))
bars = plt.barh(avg_pit_time_sorted['team_name'], avg_pit_time_sorted['avg_pit_duration_ms'], color=plt.cm.cividis(range(len(avg_pit_time_sorted))))
plt.title('Average Pit Stop Duration by Team', fontsize=14)
plt.xlabel('Average Duration (ms)', fontsize=12)
plt.ylabel('Team', fontsize=12)
plt.tight_layout()
plt.show()

# 6. Średnia liczba wycofań według toru (pokazujemy tylko TOP 10 najbardziej problematycznych torów)
retirements = results[results['statusId'] != 1]
retirements_with_track = retirements.merge(races[['raceId', 'circuitId']], on='raceId')
retirements_per_race = retirements_with_track.groupby(['raceId', 'circuitId'])['driverId'].count().reset_index(name='num_retirements')
avg_retirements_track = retirements_per_race.groupby('circuitId')['num_retirements'].mean().reset_index(name='avg_retirements')
avg_retirements_track = avg_retirements_track.merge(circuits[['circuitId', 'name']], on='circuitId')
top10_retire_circuits = avg_retirements_track.sort_values(by='avg_retirements', ascending=False).head(10)

plt.figure(figsize=(10, 6))
bars = plt.barh(top10_retire_circuits['name'][::-1], top10_retire_circuits['avg_retirements'][::-1], color='crimson')
plt.title('Top 10 Circuits by Average Number of Retirements', fontsize=14)
plt.xlabel('Average Retirements', fontsize=12)
plt.ylabel('Circuit', fontsize=12)
plt.tight_layout()
plt.show()

# 7. Trend punktowy Max Verstappen vs Lewis Hamilton (2021)
verstappen_id = drivers[(drivers['surname'] == 'Verstappen') & (drivers['forename'] == 'Max')]['driverId'].iloc[0]
hamilton_id  = drivers[(drivers['surname'] == 'Hamilton')  & (drivers['forename'] == 'Lewis')]['driverId'].iloc[0]

races_2021 = races[races['year'] == 2021][['raceId', 'round']]
standings_2021 = driver_standings.merge(races_2021, on='raceId')
verstappen_standings = standings_2021[standings_2021['driverId'] == verstappen_id]
hamilton_standings  = standings_2021[standings_2021['driverId'] == hamilton_id]

plt.figure(figsize=(10, 6))
plt.plot(verstappen_standings['round'], verstappen_standings['points'], marker='o', color='#000080', label='Max Verstappen')
plt.plot(hamilton_standings['round'],  hamilton_standings['points'],  marker='s', color='#48c9b0', label='Lewis Hamilton')
plt.title('Point Trend: Max Verstappen vs Lewis Hamilton (2021)', fontsize=14)
plt.xlabel('Round', fontsize=12)
plt.ylabel('Points', fontsize=12)
plt.legend()
plt.tight_layout()
plt.show()

# 8. Trend punktowy Ayrton Senna vs Alain Prost (1989)
senna_id = drivers[(drivers['surname'] == 'Senna') & (drivers['forename'] == 'Ayrton')]['driverId'].iloc[0]
prost_id = drivers[(drivers['surname'] == 'Prost') & (drivers['forename'] == 'Alain')]['driverId'].iloc[0]

races_1989 = races[races['year'] == 1989][['raceId', 'round']]
standings_1989 = driver_standings.merge(races_1989, on='raceId')
senna_standings = standings_1989[standings_1989['driverId'] == senna_id]
prost_standings = standings_1989[standings_1989['driverId'] == prost_id]

plt.figure(figsize=(10, 6))
plt.plot(senna_standings['round'], senna_standings['points'], marker='o', color='tab:red', label='Ayrton Senna')
plt.plot(prost_standings['round'], prost_standings['points'], marker='s', color='tab:blue', label='Alain Prost')
plt.title('Point Trend: Ayrton Senna vs Alain Prost (1989)', fontsize=14)
plt.xlabel('Round', fontsize=12)
plt.ylabel('Points', fontsize=12)
plt.legend()
plt.grid(False)
plt.tight_layout()
plt.show()

# 9. Analiza z mapą: średnia liczba wycofań na podstawie lokalizacji torów
avg_retirements_location = avg_retirements_track.merge(circuits[['circuitId', 'lat', 'lng']], on='circuitId')

fig = px.scatter_geo(
    avg_retirements_location,
    lat='lat',
    lon='lng',
    size='avg_retirements',
    hover_name='name',
    projection='natural earth',
    title='Average Number of Retirements per Circuit Location'
)
fig.show()
