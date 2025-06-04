import os
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
from plotly.offline import plot
import folium
import flagpy as fp
import io
import base64
from PIL import Image

def ensure_output_dir(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)

def generate_top_10_teams(output_dir):
    cs = pd.read_csv(os.path.join("data", "constructor_standings.csv"))
    races = pd.read_csv(os.path.join("data", "races.csv"))
    cons = pd.read_csv(os.path.join("data", "constructors.csv"))

    cs_merged = cs.merge(races[["raceId", "year", "round"]], on="raceId")
    max_rounds = (
        cs_merged.groupby("year")["round"]
        .max()
        .reset_index()
        .rename(columns={"round": "max_round"})
    )
    cs_final = cs_merged.merge(max_rounds, on="year")
    cs_final = cs_final[cs_final["round"] == cs_final["max_round"]]
    champions = cs_final[cs_final["position"] == 1]
    champ_counts = (
        champions["constructorId"]
        .value_counts()
        .rename_axis("constructorId")
        .reset_index(name="championships")
    )
    top10 = champ_counts.head(10)
    top10 = top10.merge(cons[["constructorId", "name"]], on="constructorId").sort_values(
        by="championships", ascending=False
    )
    top10_plt = top10.sort_values(by="championships", ascending=True)
    color_map = {
        "Ferrari": "#dc0000",
        "Williams": "#005aff",
        "McLaren": "#ff8700",
        "Mercedes": "#00d2be",
        "Red Bull": "#000080",
        "Team Lotus": "#bfae48",
        "Renault": "#fad400",
        "Lotus-Climax": "#064D1B",
        "Cooper-Climax": "#182849",
        "Brabham-Repco": "#46a4c0",
    }
    colors = [color_map.get(name, "#aaaaaa") for name in top10_plt["name"]]
    plt.figure(figsize=(10, 6))
    plt.barh(top10_plt["name"], top10_plt["championships"], color=colors, edgecolor="black")
    plt.xlabel("Liczba mistrzostw konstruktorów")
    plt.ylabel("Zespół")
    plt.title("Top 10 konstruktorów według liczby tytułów")
    plt.tight_layout()
    img_path = os.path.join(output_dir, "top_10_teams.png")
    plt.savefig(img_path)
    plt.close()

    fig = px.bar(
        top10,
        x="name",
        y="championships",
        title="Top 10 konstruktorów według liczby tytułów",
        labels={"name": "Zespół", "championships": "Liczba tytułów"},
    )
    fig.update_layout(xaxis_tickangle=-45)
    div = plot(fig, output_type="div", include_plotlyjs=False)
    return img_path, div

def generate_avg_pit_stop(output_dir):
    pit_stops = pd.read_csv(os.path.join("data", "pit_stops.csv"))
    races = pd.read_csv(os.path.join("data", "races.csv"))
    results = pd.read_csv(os.path.join("data", "results.csv"))
    constructors = pd.read_csv(os.path.join("data", "constructors.csv"))

    races_2021 = races[races["year"] == 2021]
    race_ids_2021 = races_2021["raceId"]
    pit_stops_2021 = pit_stops[pit_stops["raceId"].isin(race_ids_2021)]
    results_2021 = results[results["raceId"].isin(race_ids_2021)][
        ["raceId", "driverId", "constructorId"]
    ]
    merged = pd.merge(pit_stops_2021, results_2021, on=["raceId", "driverId"], how="left")
    merged_filtered = merged[merged["milliseconds"] <= 120_000]
    avg_ms = merged_filtered.groupby("constructorId")["milliseconds"].mean().reset_index()
    avg_ms["seconds"] = avg_ms["milliseconds"] / 1000.0
    avg = pd.merge(
        avg_ms, constructors[["constructorId", "name"]], on="constructorId", how="left"
    )
    avg_sorted = avg.sort_values("seconds")
    team_colors = {
        "Mercedes": "#00D2BE",
        "Red Bull": "#000080",
        "McLaren": "#FF8700",
        "Ferrari": "#DC0000",
        "Alpine F1 Team": "#F363B9",
        "Aston Martin": "#0C8040",
        "Williams": "#005AFF",
        "AlphaTauri": "#4B4B4B",
        "Alfa Romeo": "#900000",
        "Haas F1 Team": "#F9F2F2",
    }
    colors = avg_sorted["name"].map(team_colors).fillna("gray")
    plt.figure(figsize=(16, 6))
    plt.bar(avg_sorted["name"], avg_sorted["seconds"], color=colors, edgecolor="black")
    plt.xlabel("Drużyna")
    plt.ylabel("Średni czas pit stopu (sekundy)")
    plt.title("Średni czas pit stopu według drużyn w sezonie 2021")
    plt.ylim(20, 30)
    plt.xticks(rotation=45)
    plt.tight_layout()
    img_path = os.path.join(output_dir, "avg_pit_stop.png")
    plt.savefig(img_path)
    plt.close()

    fig = px.bar(
        avg_sorted,
        x="name",
        y="seconds",
        labels={"name": "Drużyna", "seconds": "Średni czas pit stopu (s)"},
        title="Średni czas pit stopu według drużyn w 2021 (po odfiltrowaniu >120s)",
    )
    fig.update_layout(xaxis_tickangle=-45)
    div = plot(fig, output_type="div", include_plotlyjs=False)
    return img_path, div

def generate_number_of_races(output_dir):
    races = pd.read_csv(os.path.join("data", "races.csv"))
    races_per_season = races.groupby("year").size().reset_index(name="num_races")
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
    img_path = os.path.join(output_dir, "number_of_races.png")
    plt.savefig(img_path)
    plt.close()
    return img_path

def generate_ham_vs_ver(output_dir):
    drivers = pd.read_csv(os.path.join("data", "drivers.csv"))
    races = pd.read_csv(os.path.join("data", "races.csv"))
    driver_standings = pd.read_csv(os.path.join("data", "driver_standings.csv"))

    verst_id = drivers[(drivers['forename'] == 'Max') & (drivers['surname'] == 'Verstappen')]['driverId'].iloc[0]
    ham_id = drivers[(drivers['forename'] == 'Lewis') & (drivers['surname'] == 'Hamilton')]['driverId'].iloc[0]

    races_2021 = races[races['year'] == 2021][['raceId', 'round']].sort_values('round')
    ds_2021 = driver_standings[driver_standings['raceId'].isin(races_2021['raceId'])]
    ds_two = ds_2021[ds_2021['driverId'].isin([verst_id, ham_id])].copy()
    ds_two = ds_two.merge(races_2021, on='raceId', how='left')
    ds_two.sort_values(['driverId', 'round'], inplace=True)

    ham_ds = ds_two[ds_two['driverId'] == ham_id][['round', 'points']].rename(columns={'points': 'cum_ham'})
    verst_ds = ds_two[ds_two['driverId'] == verst_id][['round', 'points']].rename(columns={'points': 'cum_verst'})

    cum_df = pd.merge(ham_ds, verst_ds, on='round')
    cum_df.sort_values('round', inplace=True)
    cum_df.reset_index(drop=True, inplace=True)
    cum_df['pts_ham'] = cum_df['cum_ham'].diff().fillna(cum_df['cum_ham'])
    cum_df['pts_verst'] = cum_df['cum_verst'].diff().fillna(cum_df['cum_verst'])

    df_long_pts = cum_df.melt(id_vars='round', value_vars=['pts_verst', 'pts_ham'],
                              var_name='Driver', value_name='Points')
    df_long_pts['Driver'] = df_long_pts['Driver'].map({'pts_verst': 'Verstappen', 'pts_ham': 'Hamilton'})

    df_long_cum = cum_df.melt(id_vars='round', value_vars=['cum_verst', 'cum_ham'],
                              var_name='Driver', value_name='Cumulative Points')
    df_long_cum['Driver'] = df_long_cum['Driver'].map({'cum_verst': 'Verstappen', 'cum_ham': 'Hamilton'})

    color_map = {'Verstappen': '#000080', 'Hamilton': '#00D2BE'}

    fig_pts = px.line(
        df_long_pts,
        x='round',
        y='Points',
        color='Driver',
        color_discrete_map=color_map,
        markers=True,
        title='2021: Punkty zdobyte na wyścig – Verstappen vs Hamilton',
        labels={'round': 'Runda', 'Points': 'Punkty w wyścigu'}
    )
    fig_pts.update_layout(xaxis=dict(dtick=1), legend_title_text='Kierowca')
    div_pts = plot(fig_pts, output_type="div", include_plotlyjs=True)

    fig_cum = px.line(
        df_long_cum,
        x='round',
        y='Cumulative Points',
        color='Driver',
        color_discrete_map=color_map,
        markers=True,
        title='2021: Skumulowane punkty – Verstappen vs Hamilton',
        labels={'round': 'Runda', 'Cumulative Points': 'Skumulowane punkty'}
    )
    fig_cum.update_layout(xaxis=dict(dtick=1), legend_title_text='Kierowca')
    div_cum = plot(fig_cum, output_type="div", include_plotlyjs=True)
    return div_pts, div_cum

def generate_retirements_per_track(output_dir):
    races = pd.read_csv(os.path.join("data", "races.csv"))
    results = pd.read_csv(os.path.join("data", "results.csv"))
    status = pd.read_csv(os.path.join("data", "status.csv"))
    circuits = pd.read_csv(os.path.join("data", "circuits.csv"))

    races_2021 = races[races["year"] == 2021]
    results_with_status = results.merge(
        status, left_on="statusId", right_on="statusId", how="left"
    )
    results_with_race = results_with_status.merge(
        races_2021[["raceId", "circuitId"]], on="raceId", how="inner"
    )
    results_with_circuit = results_with_race.merge(
        circuits[["circuitId", "name"]], on="circuitId", how="left"
    )
    retirements = results_with_circuit[
        (~results_with_circuit["status"].eq("Finished"))
        & (~results_with_circuit["status"].str.startswith("+"))
    ]
    retirements_count = (
        retirements.groupby("name").size().reset_index(name="retirements_count")
    )
    retirements_count = retirements_count.sort_values(
        by="retirements_count", ascending=True
    )
    colors = [
        "red" if name == "Hungaroring" else "#138D75" for name in retirements_count["name"]
    ]
    plt.figure(figsize=(12, 6))
    plt.barh(
        retirements_count["name"], retirements_count["retirements_count"], color=colors, edgecolor="black"
    )
    plt.xlabel("Liczba wycofań")
    plt.ylabel("Tor wyścigowy")
    plt.title("Liczba wycofań według toru w sezonie 2021")
    plt.tight_layout()
    img_path = os.path.join(output_dir, "retirements_per_track.png")
    plt.savefig(img_path)
    plt.close()

    fig = px.bar(
        retirements_count,
        x="name",
        y="retirements_count",
        title="Liczba wycofań według toru w sezonie 2021",
        labels={"name": "Tor wyścigowy", "retirements_count": "Liczba wycofań"},
    )
    fig.update_layout(xaxis_tickangle=-45)
    div = plot(fig, output_type="div", include_plotlyjs=False)
    return img_path, div

def generate_top_10_drivers_by_wins(output_dir):
    results = pd.read_csv(os.path.join("data", "results.csv"))
    drivers = pd.read_csv(os.path.join("data", "drivers.csv"))

    winners = results[results["positionOrder"] == 1]
    wins_per_driver = (
        winners.groupby("driverId")
        .size()
        .reset_index(name="wins")
    )
    top_winners = wins_per_driver.merge(
        drivers[["driverId", "forename", "surname"]], on="driverId", how="left"
    )
    top_winners["full_name"] = top_winners["forename"] + " " + top_winners["surname"]
    top_winners = top_winners.sort_values(by="wins", ascending=False).reset_index(drop=True)
    top_10_winners = top_winners.head(10).copy()
    top_10_winners_plt = top_10_winners.sort_values(by="wins", ascending=True)

    num_bars = len(top_10_winners_plt)
    colors = plt.cm.get_cmap("tab10")(range(num_bars))

    plt.figure(figsize=(10, 6))
    plt.barh(top_10_winners_plt["full_name"], top_10_winners_plt["wins"], color=colors, edgecolor="black")
    plt.xlabel("Liczba zwycięstw")
    plt.ylabel("Kierowca")
    plt.title("10 najlepszych kierowców według liczby zwycięstw")
    plt.tight_layout()
    img_path = os.path.join(output_dir, "top_10_drivers_by_wins.png")
    plt.savefig(img_path)
    plt.close()

    fig = px.bar(
        top_10_winners,
        x="full_name",
        y="wins",
        title="10 najlepszych kierowców według liczby zwycięstw",
        labels={"full_name": "Kierowca", "wins": "Liczba zwycięstw"},
    )
    fig.update_layout(xaxis_tickangle=-45)
    div = plot(fig, output_type="div", include_plotlyjs=False)
    return img_path, div

def generate_laps_per_position(output_dir, year=2021):
    lap_times = pd.read_csv(os.path.join("data", "lap_times.csv"))
    drivers = pd.read_csv(os.path.join("data", "drivers.csv"))
    races = pd.read_csv(os.path.join("data", "races.csv"))

    drivers['driver_name'] = drivers['forename'] + ' ' + drivers['surname']
    driver_map = drivers.set_index('driverId')['driver_name']

    race_ids_season = races[races['year'] == year]['raceId']
    lap_times_season = lap_times[lap_times['raceId'].isin(race_ids_season)]

    counts = (
        lap_times_season
        .groupby(['driverId', 'position'])
        .size()
        .reset_index(name='laps')
    )

    pivot = counts.pivot(index='driverId', columns='position', values='laps').fillna(0)
    pivot.index = pivot.index.map(driver_map)

    if 1 in pivot.columns:
        pivot = pivot.sort_values(by=1, ascending=False)
    pivot = pivot.reindex(sorted(pivot.columns), axis=1)

    data = pivot.values
    n_rows, n_cols = data.shape

    fig, ax = plt.subplots(figsize=(12, 8))
    c = ax.pcolormesh(data, cmap='turbo', edgecolors='white', linewidth=0.5)
    ax.invert_yaxis()

    for i in range(n_rows):
        for j in range(n_cols):
            val = int(data[i, j])
            if val > 0:
                text_color = 'white' if data[i, j] < data.max() / 4 else 'black'
                ax.text(j + 0.5, i + 0.5, val, ha='center', va='center', color=text_color, fontsize=8)

    ax.set_xticks(range(n_cols))
    ax.set_xticklabels(pivot.columns, rotation=0)
    ax.set_yticks([i + 0.5 for i in range(n_rows)])
    ax.set_yticklabels(pivot.index)

    ax.set_xlabel('Pozycja')
    ax.set_ylabel('Kierowca')
    ax.set_title(f'Liczba okrążeń spędzonych na każdej pozycji przez kierowcę w sezonie {year}')
    fig.colorbar(c, ax=ax, label='Liczba okrążeń')

    plt.tight_layout()
    img_path = os.path.join(output_dir, f"laps_per_position_{year}.png")
    plt.savefig(img_path)
    plt.close()

    return img_path

def generate_world_map(output_dir):
    races = pd.read_csv(os.path.join("data", "races.csv"))
    circuits = pd.read_csv(os.path.join("data", "circuits.csv"))
    races_2021 = races[races["year"] == 2021]
    merged = races_2021.merge(
        circuits[['circuitId', 'lat', 'lng', 'name', 'country']],
        on='circuitId',
        how='left'
    ).rename(columns={
        'name_x': 'race_name',
        'name_y': 'circuit_name',
        'lat': 'latitude',
        'lng': 'longitude'
    })

    def get_flag_base64(country_name: str) -> str:
        try:
            if country_name == "USA":
                country_name = "The United States"
            elif country_name == "UAE":
                country_name = "The United Arab Emirates"
            elif country_name == "UK":
                country_name = "The United Kingdom"
            elif country_name == "Netherlands":
                country_name = "The Netherlands"
            img: Image.Image = fp.get_flag_img(country_name)
            buffered = io.BytesIO()
            img.save(buffered, format="PNG")
            img_bytes = buffered.getvalue()
            buffered.close()
            img_b64 = base64.b64encode(img_bytes).decode('utf-8')
            return f"data:image/png;base64,{img_b64}"
        except Exception:
            return None

    merged['flag_uri'] = merged['country'].apply(get_flag_base64)

    mean_lat = merged['latitude'].mean()
    mean_lon = merged['longitude'].mean()

    m = folium.Map(
        location=[mean_lat, mean_lon],
        zoom_start=2,
        tiles='CartoDB positron',
        attr='CartoDB'
    )

    for _, row in merged.iterrows():
        lat = row['latitude']
        lon = row['longitude']
        flag_uri = row['flag_uri']
        if flag_uri:
            icon = folium.features.CustomIcon(
                icon_image=flag_uri,
                icon_size=(40, 25),
                icon_anchor=(20, 12)
            )
        else:
            icon = folium.Icon(color='gray', icon='flag')
        popup_text = f"{row['race_name']} – {row['circuit_name']} ({row['country']})"
        folium.Marker(
            location=[lat, lon],
            icon=icon,
            popup=popup_text,
            tooltip=row['country']
        ).add_to(m)

    map_path = os.path.join(output_dir, "world_map.html")
    m.save(map_path)
    return map_path

def build_html_report(output_dir, html_path):
    ensure_output_dir(output_dir)

    sections = []

    img_t10, div_t10 = generate_top_10_teams(output_dir)
    desc_t10 = "Wykres przedstawia dziesięć zespołów z największą liczbą mistrzostw konstruktorów w historii Formuły 1."
    sections.append(("Top 10 zespołów wg mistrzostw", desc_t10, img_t10, div_t10))

    img_pit, div_pit = generate_avg_pit_stop(output_dir)
    desc_pit = "Średni czas pit stopów poszczególnych zespołów podczas sezonu 2021, z odfiltrowaniem anomalii powyżej 120 sekund."
    sections.append(("Średni czas pit stopu (2021)", desc_pit, img_pit, div_pit))

    img_races = generate_number_of_races(output_dir)
    desc_races = "Trend liczby wyścigów rozgrywanych w sezonach Formuły 1 na przestrzeni lat, z zaznaczeniem okresu pandemii COVID-19 (2020-2023)."
    sections.append(("Liczba wyścigów na sezon", desc_races, img_races, None))

    div_ham_pts, div_ham_cum = generate_ham_vs_ver(output_dir)
    desc_ham = "Porównanie punktów zdobywanych przez Lewisa Hamiltona i Maxa Verstappena w sezonie 2021: punkty za każdy wyścig oraz skumulowane punkty."
    sections.append(("Hamilton vs Verstappen (2021)", desc_ham, None, div_ham_pts + div_ham_cum))

    img_ret, div_ret = generate_retirements_per_track(output_dir)
    desc_ret = "Liczba wycofań (DNF) na poszczególnych torach podczas sezonu 2021. Tor Hungaroring wyróżniony kolorem czerwonym."
    sections.append(("Wycofania według toru (2021)", desc_ret, img_ret, div_ret))

    img_dw, div_dw = generate_top_10_drivers_by_wins(output_dir)
    desc_dw = "Dziesięciu kierowców z największą liczbą zwycięstw w wyścigach Formuły 1."
    sections.append(("10 najlepszych kierowców wg zwycięstw", desc_dw, img_dw, div_dw))

    img_laps = generate_laps_per_position(output_dir, year=2021)
    desc_laps = "Liczba okrążeń spędzonych na każdej pozycji przez kierowcę w sezonie 2021 – mapa cieplna pokazująca dominację kierowców w różnych pozycjach."
    sections.append(("Okrążenia wg pozycji (2021)", desc_laps, img_laps, None))

    # Build HTML
    html_parts = [
        "<!DOCTYPE html>",
        "<html>",
        "<head>",
        '    <meta charset="utf-8">',
        "    <title>Raport Formuła 1</title>",
        "</head>",
        "<body>",
        "    <h1>Raport wizualizacji danych F1</h1>",
        '    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>'
    ]

    for title, desc, img_path, div in sections:
        html_parts.append(f"    <h2>{title}</h2>")
        html_parts.append(f"    <p>{desc}</p>")
        if img_path:
            img_name = os.path.basename(img_path)
            html_parts.append(f'    <img src="{img_name}" alt="{title}" style="max-width:100%;">')
        if div:
            html_parts.append(div)

    # Add world map section
    map_path = generate_world_map(output_dir)
    desc_map = "Interaktywna mapa torów wyścigowych sezonu 2021 z flagami krajów."
    html_parts.append("    <h2>Mapa torów wyścigowych (2021)</h2>")
    html_parts.append(f"    <p>{desc_map}</p>")
    html_parts.append(f'    <iframe src="{os.path.basename(map_path)}" width="100%" height="600"></iframe>')

    html_parts.append("</body>")
    html_parts.append("</html>")

    with open(html_path, "w", encoding="utf-8") as f:
        f.write("\n".join(html_parts))

if __name__ == "__main__":
    output_dir = "report_output"
    html_file = os.path.join(output_dir, "report.html")
    build_html_report(output_dir, html_file)
    print(f"Generated HTML report at {html_file}")