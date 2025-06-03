import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px

# 1. Wczytanie zestawów danych
races = pd.read_csv('data/races.csv')
results = pd.read_csv('data/results.csv')
status = pd.read_csv('data/status.csv')
circuits = pd.read_csv('data/circuits.csv')

# 2. Wybranie wyścigów z sezonu 2021
races_2021 = races[races['year'] == 2021]

# 3. Połączenie wyników z opisem statusu
results_with_status = results.merge(status, left_on='statusId', right_on='statusId', how='left')

# 4. Połączenie z tabelą wyścigów, aby uzyskać circuitId tylko dla 2021
results_with_race = results_with_status.merge(
    races_2021[['raceId', 'circuitId']],
    on='raceId',
    how='inner'
)

# 5. Połączenie z tabelą torów, aby uzyskać nazwy obiektów
results_with_circuit = results_with_race.merge(
    circuits[['circuitId', 'name']],
    on='circuitId',
    how='left'
)

# 6. Zdefiniowanie wycofań (status != 'Finished' i nie zaczynający się od '+')
retirements = results_with_circuit[
    (~results_with_circuit['status'].eq('Finished')) &
    (~results_with_circuit['status'].str.startswith('+'))
]

# 7. Zliczenie wycofań w podziale na tor
retirements_count = retirements.groupby('name').size().reset_index(name='retirements_count')

# 8. Posortowanie malejąco wg liczby wycofań
retirements_count = retirements_count.sort_values(by='retirements_count', ascending=False)

# 9. Wyświetlenie wynikowej tabeli
print("Liczba wycofań według toru w sezonie 2021:")
retirements_count.head()

# 10. Wykres słupkowy w Matplotlib
plt.figure(figsize=(12, 6))
plt.bar(retirements_count['name'], retirements_count['retirements_count'], color='orange')
plt.xticks(rotation=90)
plt.xlabel('Tor wyścigowy')
plt.ylabel('Liczba wycofań')
plt.title('Liczba wycofań według toru w sezonie 2021')
plt.tight_layout()
plt.show()

# 11. Interaktywny wykres słupkowy w Plotly
fig = px.bar(
    retirements_count,
    x='name',
    y='retirements_count',
    title='Liczba wycofań według toru w sezonie 2021',
    labels={'name': 'Tor wyścigowy', 'retirements_count': 'Liczba wycofań'}
)
fig.update_layout(xaxis_tickangle=-45)
fig.show()
