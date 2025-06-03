import matplotlib.pyplot as plt
import pandas as pd
import matplotlib.dates as mdates
from datetime import datetime

# Przykładowe dane
tasks = [
    {"Task": "Analiza wymagań", "Start": "2025-05-01", "End": "2025-05-05"},
    {"Task": "Projektowanie", "Start": "2025-05-06", "End": "2025-05-10"},
    {"Task": "Implementacja", "Start": "2025-05-11", "End": "2025-05-20"},
    {"Task": "Testowanie", "Start": "2025-05-21", "End": "2025-05-25"},
    {"Task": "Wdrożenie", "Start": "2025-05-26", "End": "2025-05-30"},
]

# Konwersja do DataFrame
df = pd.DataFrame(tasks)
df["Start"] = pd.to_datetime(df["Start"])
df["End"] = pd.to_datetime(df["End"])
df["Duration"] = df["End"] - df["Start"]

# Tworzenie wykresu Gantta
fig, ax = plt.subplots(figsize=(10, 5))
for i, task in df.iterrows():
    ax.barh(task["Task"], task["Duration"].days, left=task["Start"], height=0.5)

# Formatowanie osi
ax.xaxis.set_major_locator(mdates.DayLocator(interval=2))
ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
plt.xticks(rotation=45)
plt.xlabel("Data")
plt.ylabel("Zadanie")
plt.title("Wykres Gantta - Przykład")
plt.tight_layout()

plt.show()
