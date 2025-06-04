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
    plt.title("Ranking 10 najlepszych konstruktorów według liczby tytułów")
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
    general_avg = avg["seconds"].mean()
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
    plt.title("Średni czas pit stopu według zespołów w sezonie 2021")
    plt.ylim(20, 30)
    plt.xlim(-1, 10)
    plt.hlines(general_avg, -1, 10, color="black", linestyles="dashed")
    plt.text(0.02, general_avg + 0.2, f"Średni czas pit stopu: {round(general_avg, 3)}", fontsize=8, color="black")
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
    plt.title("Liczba wyścigów w latach 1950-2024")
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
        title='Punkty zdobyte na wyścig – Verstappen vs Hamilton w sezonie 2021',
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
        title='Skumulowane zdobyte punkty – Verstappen vs Hamilton w sezonie 2021',
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
    plt.title("DNF-y według toru w sezonie 2021")
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


def generate_retirements_per_constructor(output_dir):
    results = pd.read_csv("data/results.csv")
    status = pd.read_csv("data/status.csv")
    races = pd.read_csv("data/races.csv")
    constructors = pd.read_csv("data/constructors.csv")
    races_2021 = races[races["year"] == 2021]
    results = results[results["raceId"].isin(races_2021["raceId"])]
    results = results.merge(status, on="statusId")
    results = results.merge(constructors, on="constructorId")
    dnf = results[
        (~results["status"].str.startswith("+")) &
        (~results["status"].isin(["Finished", "Disqualified", "Not classified"]))
        ]
    category_map = {
        "Kolizja": ["Collision", "Accident", "Spun off", "Collision damage", "Debris"],
        "Silnik": ["Engine", "Engine fire", "Engine misfire", "Oil leak", "Oil pressure", "Oil pump", "Oil pipe",
                   "Crankshaft", "Ignition", "Spark plugs", "Turbo", "Oil line"],
        "Skrzynia biegów / Przeniesienie napędu": ["Gearbox", "Transmission", "Clutch", "Drivetrain", "Differential",
                                                   "Halfshaft", "Axle", "CV joint"],
        "Układ elektryczny": ["Electrical", "Electronics", "Battery", "Magneto", "Ignition", "Distributor"],
        "Zawieszenie / Kierowanie": ["Suspension", "Steering", "Handling", "Rear wing", "Front wing", "Broken wing",
                                     "Chassis", "Undertray"],
        "Hamulce": ["Brakes", "Brake duct"],
        "Opony": ["Tyre", "Puncture", "Tyre puncture", "Wheel", "Wheel nut", "Wheel rim"],
        "Jednostka napędowa / ERS": ["Power loss", "Power Unit", "ERS"],
        "Usterka mechaniczna": ["Mechanical", "Technical", "Damage", "Stalled", "Throttle", "Vibrations", "Mechanical",
                                "Seat", "Driver Seat"],
        "Inne": ["Not restarted", "Injury", "Driver unwell", "Illness", "Safety belt", "Excluded", "Retired",
                 "Withdrew", "Did not qualify", "107% Rule", "Disqualified", "Physical", "Safety concerns"]
    }
    reverse_map = {}
    for category, terms in category_map.items():
        for term in terms:
            reverse_map[term] = category

    dnf = dnf.copy()
    dnf["Kategoria"] = dnf["status"].map(reverse_map).fillna("Inne")
    grouped = dnf.groupby(["name", "Kategoria"]).size().unstack(fill_value=0)
    categories_order = [
        "Kolizja",
        "Silnik",
        "Skrzynia biegów / Przeniesienie napędu",
        "Układ elektryczny",
        "Zawieszenie / Kierowanie",
        "Hamulce",
        "Opony",
        "Jednostka napędowa / ERS",
        "Usterka mechaniczna",
        "Inne"
    ]
    for cat in categories_order:
        if cat not in grouped.columns:
            grouped[cat] = 0
    grouped = grouped[categories_order]
    grouped = grouped.loc[grouped.sum(axis=1).sort_values(ascending=False).index]
    colors = [
        "#db6100",
        "#108010",
        "#b40c0d",
        "#74499c",
        "#c159a1",
        "#a65628",
        "#272727",
        "#009dae",
        "#dbdb79",
        "#C7C7C7",
    ]
    fig, ax = plt.subplots(figsize=(14, 8))
    grouped.plot(kind="barh", stacked=True, color=colors, edgecolor="black", ax=ax)
    ax.set_title("DNF-y konstruktorów z uwzględnieniem przyczyn w sezonie 2021")
    ax.set_xlabel("Liczba DNF")
    ax.set_ylabel("Konstruktor")
    ax.xaxis.set_minor_locator(plt.MultipleLocator(1))
    ax.tick_params(axis='x', which='minor', length=4, color='gray')
    ax.tick_params(axis='x', which='major', length=7, color='black')
    ax.legend(title="Przyczyna", bbox_to_anchor=(1.05, 1), loc="upper left")
    plt.tight_layout()
    os.makedirs(output_dir, exist_ok=True)
    path = os.path.join(output_dir, "dnf_konstruktorzy_2021.png")
    plt.savefig(path)
    plt.close()
    return path


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
    plt.title("Ranking 10 najlepszych kierowców ze względu na liczbę zwycięstw")
    plt.tight_layout()
    img_path = os.path.join(output_dir, "top_10_drivers_by_wins.png")
    plt.savefig(img_path)
    plt.close()

    fig = px.bar(
        top_10_winners,
        x="full_name",
        y="wins",
        title="Ranking 10 najlepszych kierowców ze względu na liczbę zwycięstw",
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
    ax.set_title(f'Liczba okrążeń spędzonych na poszczególnych pozycjach przez kierowcę w sezonie {year}')
    fig.colorbar(c, ax=ax, label='Liczba okrążeń')

    plt.tight_layout()
    img_path = os.path.join(output_dir, f"laps_per_position_{year}.png")
    plt.savefig(img_path)
    plt.close()

    return img_path


def generate_world_map(output_dir):
    races = pd.read_csv(os.path.join("data", "races.csv"))
    results = pd.read_csv(os.path.join("data", "results.csv"))
    drivers = pd.read_csv(os.path.join("data", "drivers.csv"))
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
    winners_2021 = results[(
                                   results["positionText"] == "1")
                           & (results["raceId"].isin(races_2021["raceId"]))
                           ][["raceId", "driverId"]].merge(
        drivers[
            [
                "driverId",
                "code",
                "forename",
                "surname",
            ]
        ],
        on="driverId",
        how="left",
    )
    merged = merged.merge(winners_2021, on="raceId")

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
        popup_text = f"{row['race_name']} <br>–<br> {row['circuit_name']} ({row['country']}) <br>–<br> Winner: {row['forename']} {row['surname']} ({row['code']})"
        popup = folium.Popup(popup_text, min_width=100, max_width=300)
        folium.Marker(
            location=[lat, lon],
            icon=icon,
            popup=popup,
            tooltip=row['country'],
        ).add_to(m)

    map_path = os.path.join(output_dir, "world_map.html")
    m.save(map_path)
    return map_path


def build_html_report(output_dir, html_path):
    ensure_output_dir(output_dir)

    sections = []

    img_races = generate_number_of_races(output_dir)
    long_desc_races = "Powyższy wykres liniowy obrazuje, jak w poszczególnych latach rosła liczba wyścigów Formuły 1 od początku istniania 1950 do 2024. Na osi poziomej znajduje się rok, natomiast oś pionowa przedstawia liczbę Grand Prix (rund) rozgrywanych w danym sezonie. Punkty i łącząca je linia pokazują stopniowy wzrost ilości organizowanych rajdów od około 10 wyścigów w latach 50. do około 16–17 w latach 80. i 90., a później aż do rekordowych 22–24 wyścigów w ostatnich latach. Dodatkowo, czerwone, przerywane pionowe linie oraz wypełnione tło oznaczają okres pandemii COVID-19 (2020–2023), kiedy kalendarz uległ skróceniu (np. w 2020 roku spadek do 17 wyścigów). Dzięki tej wizualizacji łatwo dostrzec ogólny trend rozrostu mistrzostw oraz wyjątkowe odchylenia spowodowane globalnymi wydarzeniami."
    sections.append(("Liczba wyścigów w latach 1950-2024", img_races, None, long_desc_races))

    img_t10, div_t10 = generate_top_10_teams(output_dir)
    long_desc_t10 = "Powyższy wykres prezentuje dziesięć najbardziej utytułowanych zespołów w historii Formuły 1. Oś pionowa zawiera nazwy konstruktorów, natomiast oś pozioma to łączna liczba zdobytych tytułów mistrza konstruktorów. Ferrari dominuje z 16 tytułami, co stanowi najwyższy wynik, następnie McLaren i Williams posiadają po 9 tytułów każdy, a Mercedes plasuje się na czwartym miejscu z 8. Red Bull może się pochwalić 6 wieńcami, natomiast klasyczne marki, jak Team Lotus (4) czy Cooper-Climax (2), również znalazły się w zestawieniu. Kolory słupków odnoszą się do barw charakterystycznych dla danego zespołu. Taki wykres umożliwia porównanie sukcesów historycznych zespołów i odzwierciedla ewolucję dominacji różnych drużyn."
    sections.append(("Ranking 10 najlepszych konstruktorów według liczby tytułów", img_t10, None, long_desc_t10))

    img_dw, div_dw = generate_top_10_drivers_by_wins(output_dir)
    long_desc_t10_drivers = "Na poziomym wykresie słupkowym zestawiono dziesięciu kierowców, którzy w historii Formuły 1 odnieśli najwięcej triumfów. Oś pionowa prezentuje nazwiska kierowców, zaś oś pozioma – liczbę zwycięstw. Lewis Hamilton stoi na czele z imponującymi 105 wygranymi, tuż za nim Michael Schumacher z 91 zwycięstwami. Max Verstappen, pomimo młodego wieku, osiągnął 63 triumfów, wyprzedzając legendy pokroju Vettela i Prosta."
    sections.append(
        ("Ranking 10 najlepszych kierowców ze względu na liczbę zwycięstw", img_dw, None, long_desc_t10_drivers))

    img_pit, div_pit = generate_avg_pit_stop(output_dir)
    long_desc_pit_stop = "Wykres kolumnowy ukazuje, jak efektywne w zmianie kół były poszczególne zespoły w sezonie 2021. Na osi poziomej widnieją nazwy dziesięciu ekip, a na osi pionowej – średni czas pit stopu wyrażony w sekundach.  Przerywana linia pozioma wskazuje ogólną średnią dla wszystkich zespołów (około 25,4 s), co pozwala zorientować się, które zespoły były poniżej lub powyżej tej wartości. Tego typu analiza pokazuje, że Red Bull i Ferrari dysponowały najsprawniej działającymi pit stopami, co często przekładało się na zyski czasowe podczas wyścigów, zaś Haas notował najwolniejsze przestoje, co mogło negatywnie wpływać na ich osiągi w stawce."
    sections.append(("Średni czas pit stopu według zespołów w sezonie 2021", img_pit, None, long_desc_pit_stop))

    img_ret, div_ret = generate_retirements_per_track(output_dir)
    long_desc_retirements_per_track = "Powyższy wykres słupkowy przedstawia, ile razy kierowcy musieli wycofać się z wyścigu na każdym torze kalendarza 2021. Na osi pionowej znajdują się nazwy obiektów, a oś pozioma pokazuje liczbę DNF-ów (Did Not Finish) w danym Grand Prix. Największą liczbę wycofań odnotowano na Hungaroringu – aż 7 kierowców nie ukończyło wyścigu, co jest spowodowane ogromnym wypadkiem na pierwszym okrążeniu. Tuż za nim plasuje się Yas Marina (6 DNF-ów), a dalej Monza i Jeddah – po 5. Kolejne obiekty notowały od 4 do zaledwie 1 wycofania (np. Algarve, Barcelona). Dzięki tej wizualizacji można ocenić, na których torach sezonu 2021 najczęściej dochodziło do awarii lub wypadków, co pomaga zrozumieć specyfikę każdego obiektu i wyzwań stawianych przed zawodnikami."
    sections.append(("DNF-y według toru w sezonie 2021", img_ret, None, long_desc_retirements_per_track))

    img_ret = generate_retirements_per_constructor(output_dir)
    long_desc_retirements_per_constr = "Stosowany, poziomy wykres słupkowy pokazuje łączną liczbę wycofań (DNF) każdego z dziesięciu zespołów w sezonie 2021 wraz z rozbiciem na kategorie przyczyn. Oś pionowa to nazwy ekip, natomiast oś pozioma – liczba DNF. Poszczególne kolory w słupkach oznaczają konkretne źródło awarii.  Williams zaliczył aż 11 wycofań – najwięcej w stawce; w większości z powodu kolizji (5 DNF), problemy ze skrzynią biegów (3) i inne kategorie. Dzięki takiemu rozbiciu widać, w których zespołach najczęściej dochodziło do wypadków, a w których dominowały awarie techniczne, co może służyć jako punkt wyjścia do analizy niezawodności bolidów i stylu jazdy kierowców poszczególnych dużyn."
    sections.append(("DNF-y konstruktorów z uwzględnieniem przyczyn w sezonie 2021", img_ret, None,
                     long_desc_retirements_per_constr))

    div_ham_pts, div_ham_cum = generate_ham_vs_ver(output_dir)
    long_descr_ham_ver = "Powyższe wykresy przedstawiają sezon Formuły 1 z 2021 roku, porównując wyniki Red Bulla Maxa Verstappena oraz Mercedesa Lewisa Hamiltona. Pierwszy z nich (“Punkty zdobyte na wyścigu”) ilustruje punktację w każdej z 22 rund sezonu. Na osi poziomej oznaczono numer rundy, a na osi pionowej liczbę punktów zdobytych w danym wyścigu. Można zauważyć, że w początkowych wyścigach oba nazwiska wymieniały się na czele: w rundzie 1 Verstappen zdobył maksymalne 25 punktów, podczas gdy Hamilton zdobył 18, w drugiej sytuacja się odwróciła, a następnie oba kierowcy utrzymywali się w okolicach czołówki. Runda 6 przyniosła zerowy dorobek obu zawodników, co odzwierciedla się wspólnym minimum. W kolejnych wyścigach zdarzały się gwałtowne spadki, na przykład Hamilton w rundzie 11 nie zdobył punktów, a Verstappen w tej samej rundzie uzyskał najwyższy wynik. Drugi wykres (“Skumulowane punkty”) prezentuje progres sumarycznej punktacji obu kierowców w miarę upływu kolejnych wyścigów. Linia obu zawodników startuje w tym samym miejscu, ale już od połowy sezonu widać narastającą przewagę Verstappena, która ulegała minimalnym wyrównaniom, np. po rundzie 10 wynik był zbliżony. Do ostatniej rundy sześcio-punktowa różnica między nimi świadczy o niezwykle wyrównanym pojedynku o tytuł, który ostatecznie padł łupem Verstappena."
    sections.append(("Hamilton vs Verstappen w sezonie 2021", None, div_ham_pts + div_ham_cum, long_descr_ham_ver))

    img_laps = generate_laps_per_position(output_dir, year=2021)
    long_descr_laps_per_pos = "Powyższa mapa cieplna przedstawia, ile okrążeń w sezonie 2021 każdy z wybranych kierowców przejechał na poszczególnych pozycjach od 1. do 20. Wiersze reprezentują nazwiska zawodników  zaś kolumny – miejsca na torze w kolejnych okrążeniach. Kolory skali od granatowego (niewiele okrążeń) przez zielony po żółty i czerwony (dużo okrążeń) wskazują, na których pozycjach dany kierowca spędził najwięcej czasu.  Ta mapa pozwala szybko analizować, jak poszczególni zawodnicy kontrolowali tor i jak długo utrzymywali swoją pozycję w wyścigu, odzwierciedlając ich regularność i konkurencyjność."
    sections.append(("Liczba okrążeń spędzonych na poszczególnych pozycjach przez kierowcę w sezonie 2021", img_laps,
                     None, long_descr_laps_per_pos))

    # Build HTML

    html_parts = [
        "<!DOCTYPE html>",
        "<html>",
        "<center>",
        "<head>",
        '    <meta charset="utf-8">',
        "    <title>Analiza wyników Mistrzostw Świata F1</title>",
        "</head>",
        '<style>:root {--quarto-font-monospace: SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace;}body {font-family: var(--quarto-font-monospace);}</style>'
        "<body>",
        "    <h1>Analiza wyników Mistrzostw Świata F1</h1>",
        '    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>'
    ]

    for i, section in enumerate(sections):
        if i == 2:
            html_parts.append("    <h2 style='margin-top: 150px'>Analiza wyników Mistrzostw Świata F1 sezonu 2021</h2>")
        html_parts.append(f"    <h2 style='margin-top: 90px'>{section[0]}</h2>")
        if section[1]:
            img_name = os.path.basename(section[1])
            html_parts.append(f'    <img src="static/{img_name}" alt="{section[0]}" style="max-width:100%;">')
        if section[2]:
            html_parts.append(section[2])
        html_parts.append(f"    <p>{section[3]}</p>")

    # Add world map section
    map_path = generate_world_map(output_dir)
    desc_map = "Interaktywna mapa torów wyścigowych sezonu 2021 z flagami krajów."
    html_parts.append("    <h2 style='margin-top: 90px'>Mapa torów wyścigowych (2021)</h2>")
    html_parts.append(f"    <p>{desc_map}</p>")
    html_parts.append(f'    <iframe src="{map_path}" width="75%" height="600"></iframe>')
    html_parts.append("</body>")
    html_parts.append("</center>")
    html_parts.append(
        "<footer style='margin-top: 50px'><p style='text-align: right; margin-right: 15px'>Autorzy: Krzysztof Tarabuła, Kamil Safaryjski</p></footer>")
    html_parts.append("</html>")

    with open(html_path, "w", encoding="utf-8") as f:
        f.write("\n".join(html_parts))


if __name__ == "__main__":
    output_dir = "static"
    html_file = os.path.join("report.html")
    build_html_report(output_dir, html_file)
    print(f"Generated HTML report at {html_file}")