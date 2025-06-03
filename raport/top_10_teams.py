import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px

# 1. Wczytanie danych
cs = pd.read_csv("data/constructor_standings.csv")
races = pd.read_csv("data/races.csv")
cons = pd.read_csv("data/constructors.csv")

# 2. Połączenie standings z tabelą wyścigów, aby uzyskać rok i rundę
cs_merged = cs.merge(races[["raceId", "year", "round"]], on="raceId")

# 3. Wyznaczenie ostatniej rundy w każdym roku
max_rounds = (
    cs_merged.groupby("year")["round"]
    .max()
    .reset_index()
    .rename(columns={"round": "max_round"})
)

# 4. Filtrowanie tylko tych wpisów, które dotyczą końcowych wyników sezonu
cs_final = cs_merged.merge(max_rounds, on="year")
cs_final = cs_final[cs_final["round"] == cs_final["max_round"]]

# 5. Wybranie drużyn, które zajęły 1. miejsce (czyli mistrza) w każdym sezonie
champions = cs_final[cs_final["position"] == 1]

# 6. Zliczenie, ile tytułów ma każda drużyna
champ_counts = (
    champions["constructorId"]
    .value_counts()
    .rename_axis("constructorId")
    .reset_index(name="championships")
)

# 7. Wybranie top 10
top10 = champ_counts.head(10)

# 8. Dołączenie nazwy konstruktora
top10 = top10.merge(cons[["constructorId", "name"]], on="constructorId").sort_values(
    by="championships", ascending=False
)

top10_plt = top10.sort_values(by="championships", ascending=True)

# 9. Ręczne przypisanie kolorów
color_map = {
    "Ferrari": "#dc0000",  # Czerwony
    "Williams": "#005aff",  # Niebieski
    "McLaren": "#ff8700",  # Pomarańczowy
    "Mercedes": "#00d2be",  # Morski (turkusowy)
    "Red Bull": "#000080",
    "Team Lotus": "#bfae48",  # Złoty
    "Renault": "#fad400",  # Żółty
    "Lotus-Climax": "#064D1B",  # Zielony
    "Cooper-Climax": "#182849",  # Zielony ciemny
    "Brabham-Repco": "#46a4c0",  # Ciemnoszary
}

colors = [color_map.get(name, "#aaaaaa") for name in top10_plt["name"]]

# 10. Wykres słupkowy w matplotlib
plt.figure(figsize=(10, 6))
plt.barh(top10_plt["name"], top10_plt["championships"], color=colors)
plt.xlabel("Liczba mistrzostw konstruktorów")
plt.ylabel("Zespół")
plt.title("Top 10 konstruktorów według liczby tytułów")
plt.tight_layout()
plt.show()

# 11. Interaktywny wykres w Plotly (jeśli chcesz, z domyślnymi kolorami Plotly)
fig = px.bar(
    top10,
    x="name",
    y="championships",
    title="Top 10 konstruktorów według liczby tytułów",
    labels={"name": "Zespół", "championships": "Liczba tytułów"},
)
fig.update_layout(xaxis_tickangle=-45)
# fig.show()
