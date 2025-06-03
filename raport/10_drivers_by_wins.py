import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
import matplotlib.cm as cm

# 1. Wczytanie plików
results = pd.read_csv(r"data/results.csv")
drivers = pd.read_csv(r"data/drivers.csv")

# 2. Filtrujemy tylko zwycięstwa (positionOrder == 1)
winners = results[results["positionOrder"] == 1]

# 3. Liczymy liczbę zwycięstw na kierowcę (grupowanie po kolumnie 'driverId')
wins_per_driver = (
    winners.groupby("driverId")  # grupujemy po driverId
    .size()  # zliczamy wiersze (= zwycięstwa)
    .reset_index(name="wins")  # nadajemy nazwę kolumnie z liczbą zwycięstw
)

# Teraz wins_per_driver ma dokładnie dwie kolumny: ['driverId', 'wins']

# 4. Łączymy z nazwiskami kierowców
top_winners = wins_per_driver.merge(
    drivers[["driverId", "forename", "surname"]], on="driverId", how="left"
)

# 5. Tworzymy pełne nazwisko i sortujemy malejąco po liczbie zwycięstw
top_winners["full_name"] = top_winners["forename"] + " " + top_winners["surname"]
top_winners = top_winners.sort_values(by="wins", ascending=False).reset_index(drop=True)

# 6. Wybieramy top 10
top_10_winners = top_winners.head(10).copy()
top_10_winners_plt = top_10_winners.sort_values(by="wins", ascending=True)

# 7. Wyświetlamy wyniki w konsoli (lub można użyć biblioteki ace_tools do interaktywnej tabeli)
print(top_10_winners[["full_name", "wins"]])

# 8. Opcjonalnie: wykres matplotlib
num_bars = len(top_10_winners_plt)
cmap = cm.get_cmap("tab10")
colors = [cmap(i / num_bars) for i in range(num_bars)]
plt.figure(figsize=(10, 6))
plt.barh(top_10_winners_plt["full_name"], top_10_winners_plt["wins"], color=colors)
plt.xlabel("Liczba zwycięstw")
plt.ylabel("Kierowca")
plt.title("10 najlepszych kierowców według liczby zwycięstw")
plt.tight_layout()
plt.show()

# 9. Opcjonalnie: wykres interaktywny Plotly
fig = px.bar(
    top_10_winners,
    x="full_name",
    y="wins",
    title="10 najlepszych kierowców według liczby zwycięstw",
    labels={"full_name": "Kierowca", "wins": "Liczba zwycięstw"},
)
fig.update_layout(xaxis_tickangle=-45)
fig.show()
