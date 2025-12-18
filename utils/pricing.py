"""
utils/pricing.py
Module de calcul détaillé des coûts.
"""
from typing import Dict

# Constantes 2025
FUEL_PRICES = {
    "Essence": 1.85, "Diesel": 1.75, "Électrique": 0.22 # €/kWh
}
# Conso Moyenne (L/100km ou kWh/100km)
AVG_CONSUMPTION = {
    "Essence": 7.0, "Diesel": 6.0, "Électrique": 17.0
}
# Péage France (~0.12€/km sur autoroute, on suppose 80% du trajet sur autoroute)
TOLL_RATE = 0.12 

class PriceCalculator:
    def __init__(self, distance_km: float):
        self.distance = distance_km

    def get_car_details(self, engine_type: str) -> Dict:
        """Détail pour voiture : Carburant + Péage"""
        conso = AVG_CONSUMPTION.get(engine_type, 7.0)
        price_unit = FUEL_PRICES.get(engine_type, 1.85)
        
        # Calculs
        fuel_cost = (self.distance * conso / 100) * price_unit
        toll_cost = (self.distance * 0.8) * TOLL_RATE
        total = fuel_cost + toll_cost
        
        return {
            "type": "voiture",
            "total": round(total, 2),
            "carburant": round(fuel_cost, 2),
            "peage": round(toll_cost, 2),
            "min": round(fuel_cost, 2), # Sans péage
            "max": round(total * 1.15, 2) # Bouchons
        }

    def get_ticket_details(self, mode: str) -> Dict:
        """Détail pour Billets (Train/Avion/Bus)"""
        # Prix au km approximatif
        if "TGV" in mode: rate = 0.15
        elif "Intercités" in mode: rate = 0.10
        elif "Avion" in mode: rate = 0.12; base = 50 # Base fixe aéroport
        elif "Autocar" in mode: rate = 0.06; base = 0
        else: rate = 0; base = 0
        
        base_price = base + (self.distance * rate) if "Avion" in mode else (self.distance * rate)
        
        return {
            "type": "ticket",
            "total": round(base_price, 2),
            "min": round(base_price * 0.6, 2),  # Prem's / Low cost
            "max": round(base_price * 1.8, 2)   # Dernière minute
        }