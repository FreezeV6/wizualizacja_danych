import pandas as pd
import numpy as np
import plotly.express as px

x = list(range(1, 101))
y2 = np.log2(x)
y10 = np.log10(x)

quiz = pd.DataFrame({'Odpowiedź': ['Tak', 'Nie'],
                     'Wartość': [4532, 2497]})

sprzedaz = pd.DataFrame({'Miasto': ['Katowice', 'Kraków', 'Wrocław'],
                         'Desktop': [2, 7, 3],
                         'Laptop': [12, 7, 13]})

sprzedaz_melted = sprzedaz.melt(id_vars='Miasto', var_name='Produkt', value_name='Sprzedaż')

fig = px.bar(sprzedaz_melted,
             x='Miasto',
             y='Sprzedaż',
             color='Miasto',
             facet_col='Produkt',
             title='Rozkład sprzedaży produktów w miastach',
             labels={'Miasto': 'Miasto sprzedaży',
                     'Sprzedaż': 'Liczba sprzedanych produktów',
                     'Produkt': 'Rodzaj produktu'},
             template='simple_white')

fig.for_each_annotation(lambda a: a.update(text=a.text.split("=")[-1]))

fig.update_layout(showlegend=False)
fig.show()
