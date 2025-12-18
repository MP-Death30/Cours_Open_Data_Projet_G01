# 🎅 EcoRoute — Calculateur d'impact carbone & Économique 🎄

## 📋 Description
**EcoRoute** est une application intelligente qui calcule et compare l'empreinte carbone de différents modes de transport (Train, Voiture, Avion, Vélo) pour un trajet donné.

Au-delà de l'écologie, l'application estime désormais le **coût financier détaillé** (carburant, péages, billets) et permet de visualiser l'itinéraire sur une **carte interactive**.

> **Note festive :** L'application arbore actuellement un thème spécial pour les fêtes de fin d'année ! 🎁✨

## 🎯 Fonctionnalités Clés

### 1. 📊 Comparateur Hybride (Écologie & Économie)
- **Calcul d'empreinte CO2** : Estimation précise selon la méthodologie ADEME.
- **Calculateur de Prix Détaillé** :
    - Distinction Essence/Diesel/Électrique (Carburant + Péages).
    - Estimation des billets de Train (TGV/Intercités) et Avion.
    - Affichage des fourchettes de prix (Min / Moyen / Max).

### 2. 🗺️ Cartographie Interactive
- **Visualisation sur carte** : Intégration de Folium pour afficher le trajet.
- **Tracés Réalistes** : Utilisation de l'API OSRM pour tracer la route réelle (Voiture/Vélo) ou le vol d'oiseau (Avion/Train).
- **Filtrage Intelligent** : Affichage contextuel des informations à côté de la carte selon le mode choisi.

### 3. 🤖 Assistant IA (EcoBot)
- **Multi-LLM** : Utilisation conjointe de **Groq** (Llama 3.1), **Gemini** (2.5 Flash) et **HuggingFaceH4** (zephyr-7b-beta).
- **Conseils personnalisés** : Analyse du trajet pour suggérer des alternatives et donner des équivalences concrètes (ex: "ce trajet équivaut à X repas.").

## 🛠️ Installation

### 1. Cloner le projet

``` bash
git clone https://github.com/MP-Death30/Cours_Open_Data_Projet_G01.git
cd ecoroute-app
```

### 2. Installer les dépendances
Ce projet utilise `uv` pour la gestion des paquets (rapide et moderne).

``` bash
uv sync
```

*(Alternativement avec pip : `pip install -r requirements.txt`)*

### 3. Configuration des Clés API (Pour l'IA)
Le calculateur et la carte fonctionnent sans clé, mais pour activer l'assistant IA, configurez le fichier `.env` :

``` bash
# Fichier .env

# 1. Clé Google (Pour l'analyse de fond Gemini)
GEMINI_API_KEY="AIzaSyB..."

# 2. Clé Groq (Pour la rapidité du chat Llama 3)
GROQ_API_KEY="gsk_..."

# 3. Clé Hugging Face (Backup optionnel)
HUGGINGFACE_API_KEY="hf_..."
```

## 🚀 Lancement

Pour démarrer l'interface utilisateur Streamlit :

``` bash
uv run streamlit run app.py
```

L'application sera accessible dans votre navigateur à l'adresse : `http://localhost:8501`.

## 📂 Architecture du Projet

Le projet a été restructuré pour être modulaire :

``` text
ecoroute-app/
├── app.py               # 🚀 Point d'entrée (Interface Streamlit)
├── .env                 # 🔑 Variables d'environnement
├── .streamlit/
│   └── config.toml      # 🎨 Thème graphique (Noël)
├── utils/
│   ├── data.py          # 🌍 Gestion API ADEME & Géocodage Nominatim
│   ├── pricing.py       # 💶 Logique de calcul des coûts (Carburant, Péages...)
│   ├── map_viz.py       # 🗺️ Génération des cartes Folium & OSRM
│   ├── charts.py        # 📊 Graphiques Plotly
│   └── chatbot.py       # 🤖 Gestion des LLMs
└── README.md            # 📄 Documentation
```

## 📊 Sources de données
- **[ADEME Impact CO2](https://impactco2.fr/)** : API officielle pour les facteurs d'émission carbone.
- **[OpenStreetMap / Nominatim](https://wiki.openstreetmap.org/wiki/Nominatim)** : Service de géocodage pour convertir les villes en coordonnées GPS.
- **[OSRM (Open Source Routing Machine)](http://project-osrm.org/)** : Calcul d'itinéraires routiers et cyclables pour la carte.
- **SNCF Open Data** : Base pour les estimations de temps ferroviaires.

## 👥 Équipe
Membre du Groupe 1

## 📄 Licence
MIT