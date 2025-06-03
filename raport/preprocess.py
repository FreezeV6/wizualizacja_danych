import pandas as pd

# 1. Załaduj tabelę constructors.csv i przygotuj funkcję normalizującą nazwy
constructors = pd.read_csv('data/constructors.csv')

def normalize_constructor(name: str) -> str:
    """
    - Usuwa prefiks 'Team ' (np. 'Team Lotus' → 'Lotus').
    - Jeżeli w nazwie występuje '-', bierze część przed myślnikiem (np. 'Lotus-Climax' → 'Lotus').
    - W pozostałych przypadkach zwraca oryginalną nazwę.
    """
    # Usuń prefiks 'Team ' (jeśli występuje)
    name_no_team = name.replace('Team ', '')
    # Jeżeli jest myślnik '-', weź część przed nim
    if '-' in name_no_team:
        base = name_no_team.split('-', 1)[0].strip()
    else:
        base = name_no_team.strip()
    return base

# Stwórz nową kolumnę 'constructor_group'
constructors['constructor_group'] = constructors['name'].apply(normalize_constructor)

# (Opcjonalnie) Sprawdźmy, ile unikalnych grup powstało
orig_unique = constructors['name'].nunique()
group_unique = constructors['constructor_group'].nunique()
print(f"Liczba unikalnych oryginalnych nazw: {orig_unique}")
print(f"Liczba unikalnych zgrupowanych nazw: {group_unique}")

# Wyświetl 10 grup, które zebrały najwięcej wariantów oryginalnych nazw
grp_counts = constructors.groupby('constructor_group')['name'].nunique().sort_values(ascending=False)
print("Top 10 grup po liczbie zgrupowanych wariantów:")
print(grp_counts.head(10))

# 2. Dołącz kolumnę 'constructor_group' do pozostałych tabel:
#    - results.csv
#    - constructor_results.csv
#    - constructor_standings.csv
#    (możesz analogicznie dołączyć do każdej innej tabeli, która ma kolumnę constructorId)

# Załaduj pozostałe tabele
results = pd.read_csv('data/results.csv')
constructor_results = pd.read_csv('data/constructor_results.csv')
constructor_standings = pd.read_csv('data/constructor_standings.csv')

# Dołączenie: najpierw wybieramy z constructors tylko kluczowe kolumny
constructors_small = constructors[['constructorId', 'constructor_group']]

# 2.1 Wyniki poszczególnych wyścigów (results)
results = results.merge(
    constructors_small,
    on='constructorId',
    how='left'
)

# 2.2 Wyniki konstruktorów w poszczególnych wyścigach (constructor_results)
constructor_results = constructor_results.merge(
    constructors_small,
    on='constructorId',
    how='left'
)

# 2.3 Stan klasyfikacji konstruktorów w sezonie (constructor_standings)
constructor_standings = constructor_standings.merge(
    constructors_small,
    on='constructorId',
    how='left'
)

# Teraz w każdej z tych tabel masz kolumnę 'constructor_group',
# po której możesz grupować dane np. łącząc Team Lotus i Lotus-Climax w jedno.

# 3. (Przykład) Agregacja liczby punktów per grouped constructor w sezonie 2024:
#    – najpierw zabezpieczmy się, że mamy sezon 2024 w tabeli standings
cs_2024 = constructor_standings[constructor_standings['season'] == 2024]
agg_2024 = (
    cs_2024
    .groupby('constructor_group')['points']
    .sum()
    .sort_values(ascending=False)
    .reset_index()
)
print("\nSuma punktów w sezonie 2024 (zgrupowane):")
print(agg_2024)

# 4. Zapisz przetworzone tabele (opcjonalnie) do nowych plików CSV
constructors.to_csv('data/constructors_preprocessed.csv', index=False)
results.to_csv('data/results_preprocessed.csv', index=False)
constructor_results.to_csv('data/constructor_results_preprocessed.csv', index=False)
constructor_standings.to_csv('data/constructor_standings_preprocessed.csv', index=False)
