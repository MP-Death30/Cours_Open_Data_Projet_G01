import pandas as pd
import requests
import streamlit as st
from geopy.geocoders import Nominatim
from geopy.distance import geodesic
import time
from utils.pricing import PriceCalculator

# --- CONFIG API ADEME & CO2 ---
DEFAULT_EMISSION_FACTORS = {
    "Voiture (Thermique)": 0.192, "Voiture (Électrique)": 0.020,
    "Avion (Court courrier)": 0.230, "Train (TGV)": 0.0024,
    "Train (Intercités)": 0.0052, "Autocar": 0.030, "Vélo / Marche": 0.0
}
API_MAPPING = {
    4: "Voiture (Thermique)", 5: "Voiture (Électrique)",
    2: "Train (TGV)", 3: "Train (Intercités)",
    1: "Avion (Court courrier)", 8: "Autocar"
}

@st.cache_data(ttl=3600*24)
def get_emission_factors():
    """Récupère facteurs CO2 via API ADEME (Impact CO2)."""
    factors = DEFAULT_EMISSION_FACTORS.copy()
    try:
        r = requests.get("https://impactco2.fr/api/v1/transport", params={"km": 1, "displayAll": 1}, timeout=5)
        if r.status_code == 200:
            for item in r.json().get('data', []):
                if item.get('id') in API_MAPPING:
                    factors[API_MAPPING[item.get('id')]] = float(item.get('value'))
    except: pass
    return factors

def get_coordinates(city_name):
    """Géocodage robuste."""
    geolocator = Nominatim(user_agent="ecoroute_app_details_v3")
    try:
        loc = geolocator.geocode(city_name + ", France", timeout=10)
        if loc: return (loc.latitude, loc.longitude)
        time.sleep(1)
        loc = geolocator.geocode(city_name, timeout=10)
        return (loc.latitude, loc.longitude) if loc else None
    except: return None

def calculate_trip(start_city, end_city):
    """Calcule tout : Distance, CO2, et Détails Prix."""
    c_start = get_coordinates(start_city)
    c_end = get_coordinates(end_city)
    
    if not c_start or not c_end: return None, None, None, None
    
    dist_bird = geodesic(c_start, c_end).km
    dist_road = dist_bird * 1.2
    
    factors = get_emission_factors()
    
    # Calculateurs
    pricer_road = PriceCalculator(dist_road)
    pricer_bird = PriceCalculator(dist_bird * 1.1) # +10% détour train
    
    results = []
    for mode, factor in factors.items():
        d = dist_bird if "Avion" in mode else dist_road
        co2 = d * factor
        
        # --- LOGIQUE DÉTAIL PRIX ---
        details = {}
        if "Voiture (Thermique)" in mode:
            details = pricer_road.get_car_details("Essence")
        elif "Voiture (Électrique)" in mode:
            details = pricer_road.get_car_details("Électrique")
        elif "Train" in mode:
            details = pricer_bird.get_ticket_details(mode)
        elif "Avion" in mode:
            details = PriceCalculator(dist_bird).get_ticket_details(mode) # Avion direct
        elif "Autocar" in mode:
            details = pricer_road.get_ticket_details(mode)
        else: # Vélo
            details = {"type": "free", "total": 0, "min": 0, "max": 0}

        results.append({
            "Mode": mode,
            "Distance (km)": round(d, 1),
            "CO2 (kg)": round(co2, 2),
            # 👇 C'EST CETTE LIGNE QUI MANQUAIT 👇
            "Facteur (kgCO2/km)": round(factor, 4),
            # 👆 FIN DE LA CORRECTION 👆
            "Prix Moyen (€)": details.get("total", 0),
            "Prix Min (€)": details.get("min", 0),
            "Prix Max (€)": details.get("max", 0),
            "Details": details
        })
        
    return pd.DataFrame(results), dist_road, c_start, c_end