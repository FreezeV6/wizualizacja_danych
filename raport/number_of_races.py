import pandas as pd
import matplotlib.pyplot as plt

# Load data
races = pd.read_csv('data/races.csv')
drivers = pd.read_csv('data/drivers.csv')
results = pd.read_csv('data/results.csv')
constructors = pd.read_csv('data/constructors.csv')
constructor_standings = pd.read_csv('data/constructor_standings.csv')
pit_stops = pd.read_csv('data/pit_stops.csv')
status = pd.read_csv('data/status.csv')
circuits = pd.read_csv('data/circuits.csv')

# 1. Number of races per season
races_per_season = races.groupby('year').size().reset_index(name='num_races')
print("Number of races per season:")
print(races_per_season)

plt.figure(figsize=(12, 7))
plt.plot(races_per_season['year'], races_per_season['num_races'], marker='o', color='#f39c12')
plt.xlabel('Season (Year)')
plt.ylabel('Number of Races')
plt.ylim((0 , max(races_per_season['num_races']) + 1))
plt.title('Number of Races per Season')
plt.vlines(2020, 0, max(races_per_season['num_races']) + 1, colors='red', linestyles='dashed', label='Covid-19 Pandemic')
plt.tight_layout()
plt.show()
