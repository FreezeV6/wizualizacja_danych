import pandas as pd
import matplotlib.pyplot as plt

# Wczytanie danych
df = pd.read_excel('WielkiSzlem.xlsx')

# Obliczamy wiek w momencie rozpoczęcia, zakończenia kariery i zdobycia Wielkiego Szlema
df['Wiek_poczatek'] = df['Poczatek'] - df['Urodzenie']
df['Wiek_koniec'] = df['Koniec'] - df['Urodzenie']
df['Wiek_GS1'] = df['GS1'] - df['Urodzenie']
df['Wiek_GS2'] = df.apply(lambda row: row['GS2'] - row['Urodzenie']
if pd.notnull(row['GS2']) else None, axis=1)

# --- NOWOŚĆ: Obliczamy długość kariery i sortujemy ---
df['Dlugosc_kariery'] = df['Wiek_koniec'] - df['Wiek_poczatek']
df = df.sort_values(by='Dlugosc_kariery', ascending=False).reset_index(drop=True)

# Przygotowanie wykresu "dumbbell"
fig, ax = plt.subplots(figsize=(9, 4))

y_positions = range(len(df))

# Aby w legendzie nie powtarzać etykiet, użyjemy prostego „triku”:
# Podajemy etykiety tylko dla pierwszego wiersza, w następnych – pusty string
for i, row in df.iterrows():
    # Horyzontalna linia od początku do końca kariery
    ax.hlines(
        y=i,
        xmin=row['Wiek_poczatek'],
        xmax=row['Wiek_koniec'],
        linestyles='-',
        label='Okres kariery' if i == 0 else ''
    )

    # Punkt oznaczający początek kariery
    ax.plot(
        row['Wiek_poczatek'], i,
        marker='o',
        label='Początek kariery' if i == 0 else ''
    )

    # Punkt oznaczający koniec kariery
    ax.plot(
        row['Wiek_koniec'], i,
        marker='^',
        label='Koniec kariery' if i == 0 else ''
    )

    # Punkt (lub punkty) oznaczające moment zdobycia Wielkiego Szlema
    ax.plot(
        row['Wiek_GS1'], i,
        marker='s',
        label='Wielki Szlem' if i == 0 else ''
    )

    # Jeśli gracz zdobył Wielki Szlem po raz drugi (Rod Laver), zaznaczamy kolejny punkt
    if row['Wiek_GS2'] is not None:
        ax.plot(
            row['Wiek_GS2'], i,
            marker='s',
            label='Wielki Szlem (drugi)' if i == 0 else ''
        )

# Etykiety na osi Y: nazwiska zawodników (po posortowaniu)
ax.set_yticks(list(y_positions))
ax.set_yticklabels(df['Zawodnik'])

# Etykiety osi i tytuł
ax.set_xlabel('Wiek (lata)')
ax.set_ylabel('Zawodnik')
ax.set_title('Porównanie wieku rozpoczęcia i zakończenia kariery \n'
             'oraz momentów zdobycia Wielkiego Szlema\n'
             '(posortowane wg długości kariery)')

# Dodanie legendy – wyświetli się tylko raz każda unikatowa etykieta
ax.legend(loc='upper right')

plt.tight_layout()
plt.show()
