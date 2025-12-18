# from duckdb import df
import pandas as pd
from geopy.geocoders import Nominatim
from geopy.distance import geodesic
from utils.pricing import PriceCalculator

# Facteurs d'émission (Source: ADEME Base Carbone - Moyennes approximatives)
# gCO2e par km par passager
EMISSION_FACTORS = {
    "Voiture (Thermique)": 192,
    "Voiture (Électrique)": 20,
    "Avion (Court courrier)": 145, # Radiatif inclus
    "Train (TGV)": 2.4,
    "Train (Intercités)": 5.2,
    "Autocar": 30,
    "Covoiturage": 64,  # ~Voiture/3
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
    """
    Calcule la distance et les émissions pour tous les modes.
    NOUVELLE VERSION : Inclut aussi les prix !
    
    Returns:
        Tuple (DataFrame, distance_km)
        DataFrame contient : Mode, Distance, CO2, Prix Min, Prix Moy, Prix Max, Facteur CO2
    """
    coord_start = get_coordinates(start_city)
    coord_end = get_coordinates(end_city)
    
    if not coord_start or not coord_end:
        return None, 0
    
    # Calcul distance vol d'oiseau (approximatif mais suffisant pour le TP)
    distance_km = geodesic(coord_start, coord_end).km
    
    # On ajoute un facteur de détour pour la route (+20%)
    dist_road = distance_km * 1.2
    
    # Créer le calculateur de prix
    price_calc = PriceCalculator(dist_road)
    
    results = []
    
    # Mapping des modes vers les fonctions de calcul de prix
    mode_pricing = {
        "Voiture (Thermique)": price_calc.calculate_car_price(vehicle_type="Essence"),
        "Voiture (Électrique)": price_calc.calculate_car_price(vehicle_type="Électrique"),
        "Train (TGV)": price_calc.calculate_train_price(train_type="TGV"),
        "Train (Intercités)": price_calc.calculate_train_price(train_type="Intercités"),
        "Autocar": price_calc.calculate_bus_price(),
        "Avion (Court courrier)": price_calc.calculate_flight_price(),
        "Covoiturage": price_calc.calculate_carpool_price(),
        "Vélo / Marche": {"min_price": 0, "avg_price": 0, "max_price": 0}  # Gratuit !
    }
    
    for mode, factor in EMISSION_FACTORS.items():
        # Distance ajustée selon le mode (Avion = direct, autres = détour)
        d = distance_km if "Avion" in mode else dist_road
        
        # Calcul CO2
        co2_kg = (d * factor) / 1000
        
        # Récupération des prix
        price_data = mode_pricing.get(mode, {"min_price": 0, "avg_price": 0, "max_price": 0})
        
        results.append({
            "Mode": mode,
            "Distance (km)": round(d, 1),
            "CO2 (kg)": round(co2_kg, 2),
            "Prix Min (€)": round(price_data["min_price"], 2),
            "Prix Moyen (€)": round(price_data["avg_price"], 2),
            "Prix Max (€)": round(price_data["max_price"], 2),
            "Facteur (gCO2/km)": factor
        })
        
    df = pd.DataFrame(results)
    
    # Ajouter une colonne de score composite Prix/CO2
    # Normalisation : plus c'est bas, mieux c'est
    max_price = df["Prix Moyen (€)"].max()
    max_co2 = df["CO2 (kg)"].max()
    
    # NOUVEAU (corrigé)
    if max_price > 0 and max_co2 > 0:
        df["Score Prix"] = (100 - (df["Prix Moyen (€)"] / max_price * 100)).clip(0, 100)
        df["Score CO2"] = (100 - (df["CO2 (kg)"] / max_co2 * 100)).clip(0, 100)
        df["Score Global"] = ((df["Score Prix"] + df["Score CO2"]) / 2).round(1)
    else:
        df["Score Prix"] = 50
        df["Score CO2"] = 50
        df["Score Global"] = 50
    
    return df, distance_km


def calculate_trip_with_options(start_city, end_city, user_preferences=None):
    """
    Version avancée avec options utilisateur.
    
    Args:
        start_city: Ville de départ
        end_city: Ville d'arrivée
        user_preferences: Dict avec préférences utilisateur
            {
                'vehicle_type': 'Essence',
                'consumption': 6.5,
                'passengers': 2,
                'train_class': '2nde_classe',
                'advance_booking': True,
                'discount_card': False
            }
    
    Returns:
        DataFrame enrichi avec options personnalisées
    """
    
    if user_preferences is None:
        user_preferences = {}
    
    coord_start = get_coordinates(start_city)
    coord_end = get_coordinates(end_city)
    
    if not coord_start or not coord_end:
        return None, 0
    
    distance_km = geodesic(coord_start, coord_end).km
    dist_road = distance_km * 1.2
    
    price_calc = PriceCalculator(dist_road)
    
    results = []
    
    # Voiture avec options personnalisées
    vehicle_type = user_preferences.get('vehicle_type', 'Essence')
    consumption = user_preferences.get('consumption', None)
    passengers = user_preferences.get('passengers', 1)
    
    car_price = price_calc.calculate_car_price(
        vehicle_type=vehicle_type,
        consumption=consumption,
        passengers=passengers
    )
    
    co2_factor = EMISSION_FACTORS.get(f"Voiture ({'Thermique' if vehicle_type != 'Électrique' else 'Électrique'})", 192)
    co2_kg = (dist_road * co2_factor) / 1000 / passengers
    
    results.append({
        "Mode": f"Voiture ({vehicle_type})",
        "Distance (km)": round(dist_road, 1),
        "CO2 (kg)": round(co2_kg, 2),
        "Prix Min (€)": car_price["min_price"],
        "Prix Moyen (€)": car_price["avg_price"],
        "Prix Max (€)": car_price["max_price"],
        "Détails": f"{passengers} passager(s), {consumption if consumption else 'conso. moy.'} L/100km"
    })
    
    # Train avec options
    train_class = user_preferences.get('train_class', '2nde_classe')
    advance_booking = user_preferences.get('advance_booking', True)
    discount_card = user_preferences.get('discount_card', False)
    
    for train_type in ["TGV", "Intercités"]:
        train_price = price_calc.calculate_train_price(
            train_type=train_type,
            class_type=train_class,
            advance_booking=advance_booking,
            discount_card=discount_card
        )
        
        co2_factor = EMISSION_FACTORS.get(f"Train ({train_type})", 2.4)
        co2_kg = (dist_road * co2_factor) / 1000
        
        results.append({
            "Mode": f"Train ({train_type})",
            "Distance (km)": round(dist_road, 1),
            "CO2 (kg)": round(co2_kg, 2),
            "Prix Min (€)": train_price["min_price"],
            "Prix Moyen (€)": train_price["avg_price"],
            "Prix Max (€)": train_price["max_price"],
            "Détails": f"{train_class}, {'anticipée' if advance_booking else 'dernière min.'}"
        })
    
    # Autres modes standards
    for mode, factor in [("Autocar", 30), ("Avion (Court courrier)", 145), ("Covoiturage", 64)]:
        d = distance_km if "Avion" in mode else dist_road
        co2_kg = (d * factor) / 1000
        
        if "Autocar" in mode:
            price_data = price_calc.calculate_bus_price()
        elif "Avion" in mode:
            price_data = price_calc.calculate_flight_price()
        else:
            price_data = price_calc.calculate_carpool_price()
        
        results.append({
            "Mode": mode,
            "Distance (km)": round(d, 1),
            "CO2 (kg)": round(co2_kg, 2),
            "Prix Min (€)": round(price_data["min_price"], 2),
            "Prix Moyen (€)": round(price_data["avg_price"], 2),
            "Prix Max (€)": round(price_data["max_price"], 2),
            "Détails": ""
        })
    
    df = pd.DataFrame(results)
    
    # Score composite
    max_price = df["Prix Moyen (€)"].max()
    max_co2 = df["CO2 (kg)"].max()
    
    if max_price > 0 and max_co2 > 0:
        df["Score Prix"] = 100 - (df["Prix Moyen (€)"] / max_price * 100)
        df["Score CO2"] = 100 - (df["CO2 (kg)"] / max_co2 * 100)
        df["Score Global"] = ((df["Score Prix"] + df["Score CO2"]) / 2).round(1)
    
    return df, distance_km


def get_best_choice(df, priority="balanced"):
    """
    Recommande le meilleur mode selon la priorité.
    
    Args:
        df: DataFrame des résultats
        priority: "price" (moins cher), "eco" (moins CO2), ou "balanced" (score global)
        
    Returns:
        Series de la meilleure option
    """
    
    if priority == "price":
        return df.loc[df["Prix Moyen (€)"].idxmin()]
    elif priority == "eco":
        return df.loc[df["CO2 (kg)"].idxmin()]
    else:  # balanced
        return df.loc[df["Score Global"].idxmax()]


def format_comparison_summary(df):
    """
    Génère un résumé textuel de la comparaison.
    
    Returns:
        String avec résumé formaté
    """
    
    best_price = df.loc[df["Prix Moyen (€)"].idxmin()]
    best_eco = df.loc[df["CO2 (kg)"].idxmin()]
    worst_eco = df.loc[df["CO2 (kg)"].idxmax()]
    
    summary = f"""
📊 **RÉSUMÉ DE LA COMPARAISON**

💰 **Prix le plus bas** : {best_price['Mode']} - {best_price['Prix Moyen (€)']}€
🌱 **Impact CO2 le plus faible** : {best_eco['Mode']} - {best_eco['CO2 (kg)']} kg
🚨 **Impact CO2 le plus élevé** : {worst_eco['Mode']} - {worst_eco['CO2 (kg)']} kg

💡 **Économie possible** : En choisissant {best_eco['Mode']} au lieu de {worst_eco['Mode']}, 
   vous économisez {round(worst_eco['CO2 (kg)'] - best_eco['CO2 (kg)'], 1)} kg de CO2 !
   
   Cela équivaut à planter {round((worst_eco['CO2 (kg)'] - best_eco['CO2 (kg)']) / 22, 1)} arbres 🌳
"""
    
    return summary
