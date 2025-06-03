import pandas as pd
import plotly.express as px

# Load datasets
drivers = pd.read_csv('data/drivers.csv')
races = pd.read_csv('data/races.csv')
driver_standings = pd.read_csv('data/driver_standings.csv')

# Identify driver IDs for Max Verstappen and Lewis Hamilton
verst_id = drivers[(drivers['forename'] == 'Max') & (drivers['surname'] == 'Verstappen')]['driverId'].iloc[0]
ham_id = drivers[(drivers['forename'] == 'Lewis') & (drivers['surname'] == 'Hamilton')]['driverId'].iloc[0]

# Filter races for the 2021 season and get raceId, round
races_2021 = races[races['year'] == 2021][['raceId', 'round']].sort_values('round')

# Filter driver_standings for 2021 races and the two drivers
ds_2021 = driver_standings[driver_standings['raceId'].isin(races_2021['raceId'])]
ds_two = ds_2021[ds_2021['driverId'].isin([verst_id, ham_id])].copy()

# Merge with race info to get round
ds_two = ds_two.merge(races_2021, on='raceId', how='left')
ds_two.sort_values(['driverId', 'round'], inplace=True)

# Split into separate DataFrames for each driver
ham_ds = ds_two[ds_two['driverId'] == ham_id][['round', 'points']].rename(columns={'points': 'cum_ham'})
verst_ds = ds_two[ds_two['driverId'] == verst_id][['round', 'points']].rename(columns={'points': 'cum_verst'})

# Merge to align rounds
cum_df = pd.merge(ham_ds, verst_ds, on='round')
cum_df.sort_values('round', inplace=True)
cum_df.reset_index(drop=True, inplace=True)

# Compute per-race points by differencing cumulative points
cum_df['pts_ham'] = cum_df['cum_ham'].diff().fillna(cum_df['cum_ham'])
cum_df['pts_verst'] = cum_df['cum_verst'].diff().fillna(cum_df['cum_verst'])

# Create dataframe in long format for Plotly
df_long_pts = cum_df.melt(id_vars='round', value_vars=['pts_verst', 'pts_ham'],
                          var_name='Driver', value_name='Points')
df_long_pts['Driver'] = df_long_pts['Driver'].map({'pts_verst': 'Verstappen', 'pts_ham': 'Hamilton'})

df_long_cum = cum_df.melt(id_vars='round', value_vars=['cum_verst', 'cum_ham'],
                          var_name='Driver', value_name='Cumulative Points')
df_long_cum['Driver'] = df_long_cum['Driver'].map({'cum_verst': 'Verstappen', 'cum_ham': 'Hamilton'})

# Plotly: Points per race
fig_pts = px.line(
    df_long_pts,
    x='round',
    y='Points',
    color='Driver',
    markers=True,
    title='2021: Punkty zdobyte na wyścig – Verstappen vs Hamilton',
    labels={'round': 'Runda', 'Points': 'Punkty w wyścigu'}
)
fig_pts.update_layout(xaxis=dict(dtick=1), legend_title_text='Kierowca')
fig_pts.show()

# Plotly: Cumulative points
fig_cum = px.line(
    df_long_cum,
    x='round',
    y='Cumulative Points',
    color='Driver',
    markers=True,
    title='2021: Skumulowane punkty – Verstappen vs Hamilton',
    labels={'round': 'Runda', 'Cumulative Points': 'Skumulowane punkty'}
)
fig_cum.update_layout(xaxis=dict(dtick=1), legend_title_text='Kierowca')
fig_cum.show()
