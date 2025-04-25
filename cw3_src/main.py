from math import floor, ceil

import matplotlib.pyplot as plt
import pandas as pd

# zadanie 1

dane = pd.read_csv('dane/dane.csv', sep =';', decimal =',', index_col=0)
dane['Sprzedaz całkowita'] = dane['prodA'] + dane['prodB']
sprzedaz = dane.drop(['prodA', 'prodB'], axis = 1)

sprzedaz['mies_cat'] = pd.Categorical(sprzedaz.Miesiac,
                      categories=["styczen","luty","marzec"],
                      ordered=True)

# sprzedaz.sort_values(['mies_cat', 'dzien'], inplace = True, ignore_index = True)

# plt.plot(sprzedaz['Sprzedaz całkowita'])
#
# s_min = floor(sprzedaz['Sprzedaz całkowita'].min())
# s_max = ceil(sprzedaz['Sprzedaz całkowita'].max())
# s_half = ((s_max - s_min) / 2) + s_min
#
# scale_y = [s_min, s_min + 2, s_half, s_max-2, s_max]
#
# plt.xticks([0,30,31,58,59,90],('1', '31', '1', '28', '1', '31')) # skala osi x
# plt.yticks(scale_y, ('0k', '2k', '11k', '20k', '22k'))
#
# plt.xlabel('Sprzedaż w tyś.')
# plt.ylabel('Dzień')
# plt.ylim(scale_y[0], scale_y[-1])
# plt.title('Sprzedaż całkowita w koljnych dniach kwartału 1.')
# for line in scale_y[1:4]:
#     plt.axhline(y=line, color='gray', linestyle='dashed')
# # plt.grid(axis='y', linestyle='--')
#
# plt.show()

# zadanie 2

sprzedaz = sprzedaz[sprzedaz.Miesiac != 'luty']
s_min = floor(sprzedaz['Sprzedaz całkowita'].min())
s_max = ceil(sprzedaz['Sprzedaz całkowita'].max())
s_half = ((s_max - s_min) / 2) + s_min

plt.ylabel('Miesiąc')
plt.barh(sprzedaz['mies_cat'], sprzedaz['Sprzedaz całkowita'])
plt.show()

