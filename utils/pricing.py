"""
Module de calcul de fourchette de prix pour les trajets
Système similaire à Mappy avec estimation MIN / MOYEN / MAX
"""

from typing import Dict, Tuple
from datetime import datetime
import math

# ==================== CONSTANTES DE PRIX ====================

# Prix des carburants (euros par litre)
FUEL_PRICES = {
    "Essence": 1.85,
    "Diesel": 1.75,
    "GPL": 0.95,
    "Électrique": 0.18,  # par kWh
    "Hybride": 1.60  # Moyenne essence/électrique
}

# Consommations moyennes par type de véhicule (L/100km ou kWh/100km)
AVG_CONSUMPTION = {
    "Essence": 7.0,
    "Diesel": 6.0,
    "GPL": 8.5,
    "Électrique": 15.0,  # kWh/100km
    "Hybride": 4.5
}

# Tarifs ferroviaires (euros par km selon classe et type)
TRAIN_RATES = {
    "TGV": {
        "2nde_classe": {"min": 0.10, "avg": 0.15, "max": 0.25},
        "1ere_classe": {"min": 0.15, "avg": 0.22, "max": 0.35}
    },
    "Intercités": {
        "2nde_classe": {"min": 0.08, "avg": 0.12, "max": 0.18},
        "1ere_classe": {"min": 0.12, "avg": 0.17, "max": 0.25}
    },
    "TER": {
        "2nde_classe": {"min": 0.06, "avg": 0.10, "max": 0.15},
        "1ere_classe": {"min": 0.09, "avg": 0.14, "max": 0.20}
    }
}

# Tarifs bus/car (euros par km)
BUS_RATES = {
    "min": 0.05,
    "avg": 0.08,
    "max": 0.12
}

# Tarifs aériens
FLIGHT_BASE_COST = 50  # Coût de base
FLIGHT_RATE_PER_KM = 0.20  # Coût par km
AIRPORT_TAXES = 25  # Taxes aéroportuaires
BAGGAGE_FEE = {"min": 0, "avg": 15, "max": 40}  # Frais bagages

# Coûts annexes voiture
TOLL_RATE_PER_KM = 0.08  # Moyenne des péages autoroutiers
PARKING_COST = {"short": 0, "medium": 10, "long": 20}  # Selon durée trajet
VEHICLE_WEAR_RATE = 0.08  # Usure et amortissement par km

# Covoiturage
CARPOOL_SHARE_RATE = 0.5  # Division des coûts par X passagers


# ==================== CLASSE PRINCIPALE ====================

class PriceCalculator:
    """
    Calculateur de fourchette de prix pour différents modes de transport.
    Retourne toujours : prix_min, prix_moyen, prix_max avec détails.
    """
    
    def __init__(self, distance_km: float):
        """
        Args:
            distance_km: Distance du trajet en kilomètres
        """
        self.distance = distance_km
        
    def calculate_car_price(self, 
                           vehicle_type: str = "Essence",
                           consumption: float = None,
                           passengers: int = 1,
                           use_highway: bool = True) -> Dict:
        """
        Calcule le coût d'un trajet en voiture avec fourchette MIN/MOY/MAX.
        
        Args:
            vehicle_type: Type de carburant
            consumption: Consommation du véhicule (optionnel, utilise moyenne si None)
            passengers: Nombre de passagers pour division des coûts
            use_highway: Utilisation d'autoroute (péages)
            
        Returns:
            Dict avec min_price, avg_price, max_price et breakdown détaillé
        """
        
        # Consommation du véhicule
        if consumption is None:
            consumption = AVG_CONSUMPTION.get(vehicle_type, 7.0)
        
        # Prix du carburant
        fuel_price = FUEL_PRICES.get(vehicle_type, FUEL_PRICES["Essence"])
        
        # 1. COÛT CARBURANT
        if vehicle_type == "Électrique":
            # Pour électrique : kWh/100km * distance * prix_kWh
            fuel_cost_min = (consumption / 100) * self.distance * fuel_price * 0.85
            fuel_cost_avg = (consumption / 100) * self.distance * fuel_price
            fuel_cost_max = (consumption / 100) * self.distance * fuel_price * 1.15
        else:
            # Pour thermique : L/100km * distance * prix_litre
            fuel_cost_min = (consumption / 100) * self.distance * fuel_price * 0.85
            fuel_cost_avg = (consumption / 100) * self.distance * fuel_price
            fuel_cost_max = (consumption / 100) * self.distance * fuel_price * 1.15
        
        # 2. PÉAGES (si autoroute)
        if use_highway and self.distance > 50:
            toll_min = self.distance * TOLL_RATE_PER_KM * 0.5
            toll_avg = self.distance * TOLL_RATE_PER_KM
            toll_max = self.distance * TOLL_RATE_PER_KM * 1.3
        else:
            toll_min = toll_avg = toll_max = 0
        
        # 3. USURE ET AMORTISSEMENT
        wear_cost = self.distance * VEHICLE_WEAR_RATE
        
        # 4. PARKING (selon distance du trajet)
        if self.distance < 100:
            parking = PARKING_COST["short"]
        elif self.distance < 300:
            parking = PARKING_COST["medium"]
        else:
            parking = PARKING_COST["long"]
        
        # CALCUL TOTAL (sans parking dans min, avec parking dans max)
        min_price = fuel_cost_min + toll_min
        avg_price = fuel_cost_avg + toll_avg + wear_cost * 0.5 + parking * 0.5
        max_price = fuel_cost_max + toll_max + wear_cost + parking
        
        # Division par nombre de passagers si > 1
        if passengers > 1:
            min_price /= passengers
            avg_price /= passengers
            max_price /= passengers
        
        return {
            "min_price": round(min_price, 2),
            "avg_price": round(avg_price, 2),
            "max_price": round(max_price, 2),
            "price_range": round(max_price - min_price, 2),
            "breakdown": {
                "carburant": {
                    "min": round(fuel_cost_min / passengers, 2),
                    "avg": round(fuel_cost_avg / passengers, 2),
                    "max": round(fuel_cost_max / passengers, 2)
                },
                "péages": {
                    "min": round(toll_min / passengers, 2),
                    "avg": round(toll_avg / passengers, 2),
                    "max": round(toll_max / passengers, 2)
                },
                "usure": round(wear_cost / passengers, 2),
                "parking": round(parking / passengers, 2),
                "passagers": passengers,
                "consommation": consumption,
                "type_véhicule": vehicle_type
            }
        }
    
    def calculate_train_price(self,
                             train_type: str = "TGV",
                             class_type: str = "2nde_classe",
                             advance_booking: bool = True,
                             discount_card: bool = False) -> Dict:
        """
        Calcule le coût d'un trajet en train avec fourchette.
        
        Args:
            train_type: TGV, Intercités, ou TER
            class_type: 2nde_classe ou 1ere_classe
            advance_booking: Réservation anticipée (moins cher)
            discount_card: Carte de réduction (ex: Avantage, -30%)
            
        Returns:
            Dict avec min_price, avg_price, max_price et breakdown
        """
        
        # Récupérer les tarifs
        rates = TRAIN_RATES.get(train_type, TRAIN_RATES["TGV"])[class_type]
        
        # Calcul de base
        min_price = self.distance * rates["min"]
        avg_price = self.distance * rates["avg"]
        max_price = self.distance * rates["max"]
        
        # Réservation anticipée : -20% sur min/avg
        if advance_booking:
            min_price *= 0.80
            avg_price *= 0.90
        
        # Carte de réduction : -30%
        if discount_card:
            min_price *= 0.70
            avg_price *= 0.80
            max_price *= 0.85
        
        # Supplément dernière minute sur le max
        if not advance_booking:
            max_price *= 1.4
        
        return {
            "min_price": round(min_price, 2),
            "avg_price": round(avg_price, 2),
            "max_price": round(max_price, 2),
            "price_range": round(max_price - min_price, 2),
            "breakdown": {
                "type_train": train_type,
                "classe": class_type,
                "tarif_km_base": rates["avg"],
                "réservation_anticipée": advance_booking,
                "carte_réduction": discount_card,
                "supplément_dernière_minute": not advance_booking
            }
        }
    
    def calculate_bus_price(self, operator_type: str = "standard") -> Dict:
        """
        Calcule le coût d'un trajet en bus/car.
        
        Args:
            operator_type: standard, low_cost, ou premium
            
        Returns:
            Dict avec min_price, avg_price, max_price
        """
        
        # Tarif de base
        base_fee = 5  # Frais de dossier
        
        min_price = base_fee + self.distance * BUS_RATES["min"]
        avg_price = base_fee + self.distance * BUS_RATES["avg"]
        max_price = base_fee + self.distance * BUS_RATES["max"]
        
        # Ajustement selon opérateur
        if operator_type == "low_cost":
            min_price *= 0.8
            avg_price *= 0.85
            max_price *= 0.9
        elif operator_type == "premium":
            min_price *= 1.2
            avg_price *= 1.3
            max_price *= 1.4
        
        return {
            "min_price": round(min_price, 2),
            "avg_price": round(avg_price, 2),
            "max_price": round(max_price, 2),
            "price_range": round(max_price - min_price, 2),
            "breakdown": {
                "tarif_base": base_fee,
                "tarif_km": BUS_RATES["avg"],
                "opérateur": operator_type
            }
        }
    
    def calculate_flight_price(self,
                              airline_type: str = "standard",
                              luggage: bool = True,
                              season: str = "standard") -> Dict:
        """
        Calcule le coût d'un trajet en avion.
        
        Args:
            airline_type: low_cost, standard, ou premium
            luggage: Bagage en soute inclus
            season: low, standard, ou high (saison touristique)
            
        Returns:
            Dict avec min_price, avg_price, max_price
        """
        
        # Calcul de base
        base_price = FLIGHT_BASE_COST + (self.distance * FLIGHT_RATE_PER_KM)
        
        # Taxes aéroportuaires
        taxes = AIRPORT_TAXES
        
        # Frais bagages
        if luggage:
            luggage_min = BAGGAGE_FEE["min"]
            luggage_avg = BAGGAGE_FEE["avg"]
            luggage_max = BAGGAGE_FEE["max"]
        else:
            luggage_min = luggage_avg = luggage_max = 0
        
        # Prix avant ajustements
        min_price = base_price * 0.7 + taxes + luggage_min
        avg_price = base_price + taxes + luggage_avg
        max_price = base_price * 1.5 + taxes + luggage_max
        
        # Ajustement par type de compagnie
        if airline_type == "low_cost":
            min_price *= 0.6
            avg_price *= 0.75
            max_price *= 0.85
        elif airline_type == "premium":
            min_price *= 1.5
            avg_price *= 2.0
            max_price *= 2.5
        
        # Ajustement saisonnier
        season_multipliers = {
            "low": 0.8,
            "standard": 1.0,
            "high": 1.6
        }
        multiplier = season_multipliers.get(season, 1.0)
        
        min_price *= multiplier
        avg_price *= multiplier
        max_price *= multiplier
        
        return {
            "min_price": round(min_price, 2),
            "avg_price": round(avg_price, 2),
            "max_price": round(max_price, 2),
            "price_range": round(max_price - min_price, 2),
            "breakdown": {
                "billet_base": round(base_price, 2),
                "taxes_aéroport": taxes,
                "bagages": luggage_avg if luggage else 0,
                "type_compagnie": airline_type,
                "saison": season
            }
        }
    
    def calculate_carpool_price(self, vehicle_type: str = "Essence") -> Dict:
        """
        Calcule le coût d'un trajet en covoiturage.
        Le prix est calculé comme une voiture divisée par le nombre de passagers,
        avec des frais de service de la plateforme.
        
        Returns:
            Dict avec min_price, avg_price, max_price (par passager)
        """
        
        # Calculer le coût voiture de base
        car_cost = self.calculate_car_price(vehicle_type=vehicle_type, passengers=1)
        
        # Division typique par 3 passagers (conducteur + 2)
        typical_passengers = 3
        
        # Frais de service plateforme (15-20%)
        service_fee_rate = 0.18
        
        min_price = (car_cost["min_price"] / typical_passengers) * (1 + service_fee_rate * 0.8)
        avg_price = (car_cost["avg_price"] / typical_passengers) * (1 + service_fee_rate)
        max_price = (car_cost["max_price"] / typical_passengers) * (1 + service_fee_rate * 1.2)
        
        return {
            "min_price": round(min_price, 2),
            "avg_price": round(avg_price, 2),
            "max_price": round(max_price, 2),
            "price_range": round(max_price - min_price, 2),
            "breakdown": {
                "coût_voiture_total": car_cost["avg_price"],
                "passagers_moyens": typical_passengers,
                "frais_service": round(avg_price * service_fee_rate, 2),
                "économie_vs_voiture_solo": round(car_cost["avg_price"] - avg_price, 2)
            }
        }
    
    def calculate_ebike_price(self) -> Dict:
        """
        Calcule le coût d'un trajet en vélo électrique.
        Principalement coût électricité + entretien.
        
        Returns:
            Dict avec min_price, avg_price, max_price
        """
        
        # Consommation moyenne vélo électrique : 1 kWh/100km
        consumption_per_100km = 1.0
        electricity_price = FUEL_PRICES["Électrique"]
        
        # Coût électricité
        electricity_cost = (consumption_per_100km / 100) * self.distance * electricity_price
        
        # Entretien/amortissement : 0.02€/km
        maintenance_cost = self.distance * 0.02
        
        min_price = electricity_cost
        avg_price = electricity_cost + maintenance_cost * 0.5
        max_price = electricity_cost + maintenance_cost
        
        return {
            "min_price": round(min_price, 2),
            "avg_price": round(avg_price, 2),
            "max_price": round(max_price, 2),
            "price_range": round(max_price - min_price, 2),
            "breakdown": {
                "électricité": round(electricity_cost, 2),
                "entretien": round(maintenance_cost, 2),
                "consommation_kwh": round((consumption_per_100km / 100) * self.distance, 2)
            }
        }
    
    def calculate_all_modes(self, **kwargs) -> Dict:
        """
        Calcule les prix pour tous les modes de transport disponibles.
        
        Returns:
            Dict avec les résultats pour chaque mode
        """
        
        results = {
            "Voiture (Essence)": self.calculate_car_price(vehicle_type="Essence"),
            "Voiture (Électrique)": self.calculate_car_price(vehicle_type="Électrique"),
            "Train (TGV)": self.calculate_train_price(train_type="TGV"),
            "Train (Intercités)": self.calculate_train_price(train_type="Intercités"),
            "Autocar": self.calculate_bus_price(),
            "Avion (Court courrier)": self.calculate_flight_price(),
            "Covoiturage": self.calculate_carpool_price(),
            "Vélo Électrique": self.calculate_ebike_price()
        }
        
        return results


# ==================== FONCTIONS UTILITAIRES ====================

def format_price_range(price_data: Dict) -> str:
    """
    Formate une fourchette de prix en chaîne lisible.
    
    Args:
        price_data: Dict avec min_price, avg_price, max_price
        
    Returns:
        Chaîne formatée, ex: "45€ - 67€ (moy: 56€)"
    """
    return (f"{price_data['min_price']:.2f}€ - {price_data['max_price']:.2f}€ "
            f"(moy: {price_data['avg_price']:.2f}€)")


def get_cheapest_mode(all_results: Dict) -> Tuple[str, float]:
    """
    Trouve le mode de transport le moins cher (prix moyen).
    
    Args:
        all_results: Résultats de calculate_all_modes()
        
    Returns:
        Tuple (nom_mode, prix_moyen)
    """
    cheapest = min(all_results.items(), key=lambda x: x[1]["avg_price"])
    return cheapest[0], cheapest[1]["avg_price"]


def compare_price_co2(price_data: Dict, co2_data: Dict) -> Dict:
    """
    Crée un score combinant prix et CO2 pour recommandation.
    
    Args:
        price_data: Résultats pricing
        co2_data: Résultats CO2
        
    Returns:
        Dict avec score composite
    """
    # Normaliser prix et CO2 (0-100)
    # Plus c'est bas, mieux c'est
    price_score = max(0, 100 - price_data["avg_price"])
    co2_score = max(0, 100 - co2_data["co2_kg"])
    
    # Score composite (poids égaux)
    composite_score = (price_score + co2_score) / 2
    
    return {
        "price_score": round(price_score, 1),
        "co2_score": round(co2_score, 1),
        "composite_score": round(composite_score, 1),
        "recommendation": "Excellent" if composite_score > 75 else "Bon" if composite_score > 50 else "Moyen"
    }


# ==================== EXEMPLE D'UTILISATION ====================

if __name__ == "__main__":
    # Exemple : Paris - Lyon (465 km)
    distance = 465
    
    calc = PriceCalculator(distance)
    
    print("=== CALCUL DE PRIX POUR PARIS - LYON ===\n")
    
    # Voiture
    car_price = calc.calculate_car_price(vehicle_type="Essence", passengers=1)
    print(f"🚗 Voiture (seul) : {format_price_range(car_price)}")
    
    # Train
    train_price = calc.calculate_train_price(advance_booking=True)
    print(f"🚂 Train TGV : {format_price_range(train_price)}")
    
    # Covoiturage
    carpool_price = calc.calculate_carpool_price()
    print(f"🚙 Covoiturage : {format_price_range(carpool_price)}")
    
    # Bus
    bus_price = calc.calculate_bus_price()
    print(f"🚌 Bus : {format_price_range(bus_price)}")
    
    # Avion
    flight_price = calc.calculate_flight_price()
    print(f"✈️ Avion : {format_price_range(flight_price)}")
    
    print("\n=== MODE LE MOINS CHER ===")
    all_results = calc.calculate_all_modes()
    cheapest_mode, cheapest_price = get_cheapest_mode(all_results)
    print(f"🏆 {cheapest_mode} : {cheapest_price:.2f}€")
