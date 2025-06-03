import pandas as pd
import matplotlib.pyplot as plt

# Load data
races = pd.read_csv("data/races.csv")
drivers = pd.read_csv("data/drivers.csv")
results = pd.read_csv("data/results.csv")
constructors = pd.read_csv("data/constructors.csv")
constructor_standings = pd.read_csv("data/constructor_standings.csv")
pit_stops = pd.read_csv("data/pit_stops.csv")
status = pd.read_csv("data/status.csv")
circuits = pd.read_csv("data/circuits.csv")

# 1. Number of races per season
races_per_season = races.groupby("year").size().reset_index(name="num_races")
print("Liczba wyścigów na sezon:")
print(races_per_season)

plt.figure(figsize=(12, 7))
plt.plot(
    races_per_season["year"], races_per_season["num_races"], marker="o", color="#f39c12"
)
plt.xlabel("Sezon (rok)")
plt.ylabel("Liczba wyścigów")
plt.ylim((0, max(races_per_season["num_races"]) + 1))
plt.title("Liczba wyścigów na sezon")
plt.vlines(
    [2020, 2023],
    0,
    max(races_per_season["num_races"]) + 1,
    colors="red",
    linestyles="dashed",
    label="Pandemia Covid-19",
)
plt.axvspan(2020, 2023, color="red", alpha=0.1, label="Okres pandemii")
plt.text(2020, 14, "Covid-19", fontsize=8, color="red", rotation=45)
plt.tight_layout()
plt.show()
