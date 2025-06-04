import pandas as pd
import folium  # Interactive map library
import flagpy as fp  # Do pobierania obrazków flag jako PIL.Image
import io
import base64
from PIL import Image

# ------------------------------------------------------------------------
# 1. Wczytanie danych i filtrowanie sezonu 2021
# ------------------------------------------------------------------------

# Ścieżki do plików CSV (dostosuj ścieżki do swojego katalogu)
RACES_CSV = 'data/races.csv'
CIRCUITS_CSV = 'data/circuits.csv'

# 1.1. Wczytanie tabel za pomocą pandas
races = pd.read_csv(RACES_CSV)  # :contentReference[oaicite:0]{index=0}
circuits = pd.read_csv(CIRCUITS_CSV)  # :contentReference[oaicite:1]{index=1}

# 1.2. Wybranie tylko wyścigów z roku 2021
races_2021 = races[races['year'] == 2021]  # :contentReference[oaicite:2]{index=2}

# 1.3. Połączenie z informacjami o torach (latitude, longitude, country)
merged = races_2021.merge(
    circuits[['circuitId', 'lat', 'lng', 'name', 'country']],
    on='circuitId',
    how='left'
).rename(columns={
    'name_x': 'race_name',  # nazwa Grand Prix
    'name_y': 'circuit_name',  # nazwa toru
    'lat': 'latitude',
    'lng': 'longitude'
})


# Teraz `merged` zawiera kolumny: race_name, circuit_name, latitude, longitude, country

# ------------------------------------------------------------------------
# 2. Pobranie obrazków flag jako Base64 (data URI)
# ------------------------------------------------------------------------

def get_flag_base64(country_name: str) -> str:
    """
    Pobiera obrazek flagi dla podanej nazwy kraju za pomocą flagpy.get_flag_img(country_name),
    następnie:
      1. zapisuje go do bufora BytesIO jako PNG,
      2. koduje bajty w Base64,
      3. zwraca ciąg 'data:image/png;base64,...', który można wkleić w CustomIcon.
    Jeśli wystąpi błąd (nieznana nazwa kraju), zwraca None.
    """
    try:
        img: Image.Image = fp.get_flag_img(country_name)  # :contentReference[oaicite:3]{index=3}
        buffered = io.BytesIO()
        img.save(buffered, format="PNG")  #
        img_bytes = buffered.getvalue()
        buffered.close()
        img_b64 = base64.b64encode(img_bytes).decode('utf-8')
        return f"data:image/png;base64,{img_b64}"
    except Exception:
        return None


# 2.1. Dodanie kolumny 'flag_uri' do DataFrame: Base64 dla każdej flagi
merged['flag_uri'] = merged['country'].apply(get_flag_base64)  # :contentReference[oaicite:5]{index=5}

# ------------------------------------------------------------------------
# 3. Tworzenie interaktywnej mapy Folium z CustomIcon (flagami)
# ------------------------------------------------------------------------

# 3.1. Ustal punkt startowy mapy – środek geograficzny wszystkich wyścigów
mean_lat = merged['latitude'].mean()
mean_lon = merged['longitude'].mean()

# 3.2. Utworzenie obiektu folium.Map, z zoom_start tak, aby objął wszystkie punkty
m = folium.Map(
    location=[mean_lat, mean_lon],
    zoom_start=2,  # odpowiedni zoom, by widać było cały świat
    tiles='CartoDB positron',  # neutralny tile set
    attr='CartoDB'
)  # :contentReference[oaicite:6]{index=6}

# 3.3. Dodanie punktów (markerów) z CustomIcon (flagami)
for _, row in merged.iterrows():
    lat = row['latitude']
    lon = row['longitude']
    country = row['country']
    race = row['race_name']
    circuit = row['circuit_name']
    flag_uri = row['flag_uri']

    if flag_uri:
        # 3.3.1. Tworzymy CustomIcon z obrazem Base64
        icon = folium.features.CustomIcon(
            icon_image=flag_uri,
            icon_size=(40, 25),  # szerokość 40px, wysokość 25px
            icon_anchor=(20, 12)  # punkt kotwiczenia w środku flagi (środek)
        )  # :contentReference[oaicite:7]{index=7}
    else:
        # Jeśli nie udało się pobrać flagi, używamy domyślnej ikony
        icon = folium.Icon(color='gray', icon='flag')

    # Tekst w popupie / tooltip: "Grand Prix X – Tor Y (Kraj)"
    popup_text = f"{race} – {circuit} ({country})"

    folium.Marker(
        location=[lat, lon],
        icon=icon,
        popup=popup_text,
        tooltip=country
    ).add_to(m)

# 3.4. (Opcjonalnie) Dodaj warstwę klastrów, linie poliliniowe itp.

# ------------------------------------------------------------------------
# 4. Zapisanie mapy do pliku HTML
# ------------------------------------------------------------------------

OUTPUT_HTML = 'f1_2021_map_flags.html'
m.save(OUTPUT_HTML)
print(f"Mapa zapisana w pliku: {OUTPUT_HTML}")
