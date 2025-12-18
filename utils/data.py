import pandas as pd
from geopy.geocoders import Nominatim
from geopy.distance import geodesic

# Facteurs d'émission (Source: ADEME Base Carbone - Moyennes approximatives)
# gCO2e par km par passager
EMISSION_FACTORS = {
    "Voiture (Thermique)": 192,
    "Voiture (Électrique)": 20,
    "Avion (Court courrier)": 145, # Radiatif inclus
    "Train (TGV)": 2.4,
    "Train (Intercités)": 5.2,
    "Autocar": 30,
    "Vélo / Marche": 0
}

def get_coordinates(city_name):
    """Récupère (lat, lon) pour une ville donnée via OpenStreetMap."""
    geolocator = Nominatim(user_agent="ecoroute_app_student_project")
    try:
        location = geolocator.geocode(city_name + ", France") # On limite à la France pour simplifier
        if location:
            return (location.latitude, location.longitude)
        return None
    except:
        return None

def calculate_trip(start_city, end_city):
    """Calcule la distance et les émissions pour tous les modes."""
    coord_start = get_coordinates(start_city)
    coord_end = get_coordinates(end_city)
    
    if not coord_start or not coord_end:
        return None
    
    # Calcul distance vol d'oiseau (approximatif mais suffisant pour le TP)
    distance_km = geodesic(coord_start, coord_end).km
    
    # On ajoute un facteur de détour pour la route (+20%)
    dist_road = distance_km * 1.2
    
    results = []
    for mode, factor in EMISSION_FACTORS.items():
        # Distance ajustée selon le mode (Avion = direct, autres = détour)
        d = distance_km if "Avion" in mode else dist_road
        
        co2_kg = (d * factor) / 1000
        
        results.append({
            "Mode": mode,
            "Distance (km)": round(d, 1),
            "CO2 (kg)": round(co2_kg, 2),
            "Facteur (gCO2/km)": factor
        })
        
    return pd.DataFrame(results), distance_km