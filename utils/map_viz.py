import folium
import requests

def get_route_osrm(start_coords, end_coords, profile="driving"):
    """
    Récupère le tracé via OSRM.
    profile : 'driving' (voiture) ou 'cycling' (vélo)
    """
    # OSRM attend : lon,lat;lon,lat
    start_str = f"{start_coords[1]},{start_coords[0]}"
    end_str = f"{end_coords[1]},{end_coords[0]}"
    
    url = f"http://router.project-osrm.org/route/v1/{profile}/{start_str};{end_str}?overview=full&geometries=geojson"
    
    try:
        r = requests.get(url, timeout=5)
        if r.status_code == 200:
            data = r.json()
            geometry = data['routes'][0]['geometry']['coordinates']
            # Conversion [lon, lat] -> [lat, lon] pour Folium
            route_coords = [(point[1], point[0]) for point in geometry]
            return route_coords
    except:
        return None

def create_trip_map(start_coords, end_coords, start_name, end_name, selected_mode="Route"):
    """Génère une carte adaptée au mode de transport choisi (Route/Train/Avion)."""
    
    # Centrage
    center_lat = (start_coords[0] + end_coords[0]) / 2
    center_lon = (start_coords[1] + end_coords[1]) / 2
    m = folium.Map(location=[center_lat, center_lon], zoom_start=6, tiles="CartoDB positron")
    
    # Marqueurs
    folium.Marker(start_coords, popup=f"Départ: {start_name}", icon=folium.Icon(color="green", icon="play")).add_to(m)
    folium.Marker(end_coords, popup=f"Arrivée: {end_name}", icon=folium.Icon(color="red", icon="flag")).add_to(m)
    
    # --- LOGIQUE SIMPLIFIÉE ---
    color = "blue"
    route_coords = None
    dash_array = None
    tooltip = selected_mode
    
    # 1. Mode ROUTE (Voiture, Bus, Covoiturage)
    # On checke "Route" ou les anciens noms pour compatibilité
    if selected_mode == "Route" or "Voiture" in selected_mode or "Autocar" in selected_mode:
        route_coords = get_route_osrm(start_coords, end_coords, profile="driving")
        color = "orange" # Orange pour la route
        tooltip = "Itinéraire Routier (OSRM)"
        
    # 2. Mode TRAIN
    elif selected_mode == "Train" or "Train" in selected_mode:
        # Ligne droite pour le train (Pas d'API rail publique simple)
        route_coords = None 
        color = "blue" # Bleu SNCF
        dash_array = '5, 10' # Pointillés
        tooltip = "Ligne Ferroviaire (Vol d'oiseau)"

    # 3. Mode AVION
    elif selected_mode == "Avion" or "Avion" in selected_mode:
        route_coords = None
        color = "purple" # Violet pour l'avion
        dash_array = '5, 10'
        tooltip = "Liaison Aérienne"

    # Autres (Vélo, etc.)
    else:
        route_coords = None
        color = "gray"

    # --- TRACÉ ---
    if route_coords:
        folium.PolyLine(
            locations=route_coords,
            color=color,
            weight=5,
            opacity=0.8,
            tooltip=tooltip
        ).add_to(m)
    else:
        # Ligne droite (Vol d'oiseau)
        folium.PolyLine(
            locations=[start_coords, end_coords],
            color=color,
            weight=3,
            opacity=0.6,
            dash_array=dash_array,
            tooltip=tooltip
        ).add_to(m)

    return m