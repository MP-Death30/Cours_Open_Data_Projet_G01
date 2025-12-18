import pandas as pd
import requests
import streamlit as st
from geopy.geocoders import Nominatim
from geopy.distance import geodesic

# 1. Valeurs de secours
DEFAULT_EMISSION_FACTORS = {
    "Voiture (Thermique)": 0.192,
    "Voiture (Électrique)": 0.020,
    "Avion (Court courrier)": 0.230,
    "Train (TGV)": 0.0024,
    "Train (Intercités)": 0.0052,
    "Autocar": 0.030,
    "Vélo / Marche": 0.0
}

# 2. Mapping API
API_MAPPING = {
    4: "Voiture (Thermique)",
    5: "Voiture (Électrique)",
    2: "Train (TGV)",
    3: "Train (Intercités)",
    1: "Avion (Court courrier)",
    8: "Autocar"
}

@st.cache_data(ttl=3600*24)
def get_emission_factors():
    """
    Récupère les facteurs via l'API Impact CO2.
    CORRECTION : Plus de st.toast ici pour éviter le crash CacheReplayClosureError.
    """
    factors = DEFAULT_EMISSION_FACTORS.copy()
    url = "https://impactco2.fr/api/v1/transport"
    params = {"km": 1, "displayAll": 1} # Astuce km=1
    
    print("🔄 Connexion à l'API Impact CO2...")
    
    try:
        response = requests.get(url, params=params, timeout=5)
        if response.status_code == 200:
            data = response.json()
            items = data.get('data', [])
            
            for item in items:
                api_id = item.get('id')
                raw_value = item.get('value')
                
                if api_id in API_MAPPING and raw_value is not None:
                    name = API_MAPPING[api_id]
                    factors[name] = float(raw_value)
                    print(f"✅ {name} : {raw_value}")
                    
            # ON A SUPPRIMÉ st.toast ICI POUR RÉGLER LE BUG
            
    except Exception as e:
        print(f"⚠️ Erreur API : {e}")

    return factors

def get_coordinates(city_name):
    """Récupère (lat, lon) pour une ville."""
    geolocator = Nominatim(user_agent="ecoroute_app_student_project_final")
    try:
        location = geolocator.geocode(city_name + ", France")
        return (location.latitude, location.longitude) if location else None
    except:
        return None

def calculate_trip(start_city, end_city):
    coord_start = get_coordinates(start_city)
    coord_end = get_coordinates(end_city)
    
    if not coord_start or not coord_end:
        return None, None
    
    distance_km = geodesic(coord_start, coord_end).km
    dist_road = distance_km * 1.2
    
    current_factors = get_emission_factors()
    
    results = []
    for mode, factor in current_factors.items():
        d = distance_km if "Avion" in mode else dist_road
        co2_kg = d * factor
        
        results.append({
            "Mode": mode,
            "Distance (km)": round(d, 1),
            "CO2 (kg)": round(co2_kg, 2),
            "Facteur (kgCO2/km)": round(factor, 4)
        })
        
    return pd.DataFrame(results), distance_km