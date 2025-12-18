# EcoRoute — Calculateur d'impact carbone transport

## 📋 Description
EcoRoute est une application intelligente qui calcule et compare l'empreinte carbone de différents modes de transport (Train, Voiture, Avion, Vélo) pour un trajet donné. Elle vise à sensibiliser les utilisateurs à l'impact environnemental de leurs déplacements en proposant des alternatives moins polluantes et des équivalences concrètes générées par IA.

## 🎯 Fonctionnalités
- **Calcul d'empreinte CO2** : Estimation précise des émissions pour un trajet donné.
- **Comparateur de modes** : Visualisation graphique (Train vs Voiture vs Avion vs Vélo).
- **Assistant Éco-mobilité (IA)** : Chatbot pour conseiller sur le meilleur mode de transport et répondre aux questions écologiques.
- **Équivalences concrètes** : Traduction de l'impact carbone en termes parlants (ex: "ce trajet en voiture équivaut à X arbres coupés") via IA.
- **Suggestions d'optimisation** : Propositions d'itinéraires alternatifs plus respectueux de l'environnement.

## 🛠️ Installation

### 1. Cloner le projet

``` bash
git clone https://github.com/MP-Death30/Cours_Open_Data_Projet_G01.git
cd ecoroute-app
```

### 2. Installer les dépendances
Ce projet utilise `uv` pour la gestion des paquets.

``` bash
uv sync
```

### 3. Configurer les variables d'environnement
Créez un fichier `.env` à la racine du projet et ajoutez vos clés API (nécessaire pour le module IA et géocodage).

``` bash
cp .env.example .env
# Ouvrez le fichier .env et ajoutez votre clé :
# GEMINI_API_KEY="votre_clé_api_ici"
```

## 🚀 Lancement

Pour démarrer l'interface utilisateur Streamlit :

``` bash
uv run streamlit run app.py
```

L'application sera accessible dans votre navigateur à l'adresse : `http://localhost:8501`.

## 📊 Sources de données
- **[SNCF Open Data](https://ressources.data.sncf.com/)** : Horaires et trajets ferroviaires.
- **[ADEME Base Carbone](https://www.data.gouv.fr/fr/datasets/base-carbone-r/)** : Facteurs d'émission officiels pour les différents modes de transport.
- **[OpenStreetMap / Nominatim](https://wiki.openstreetmap.org/wiki/Nominatim)** : Service de géocodage pour le calcul des distances entre villes.
- **[Atmo](https://www.data.gouv.fr/fr/datasets/donnees-temps-reel-de-mesure-des-concentrations-de-polluants-atmospheriques-reglementes-1/)** : Données sur la qualité de l'air (optionnel).

## 👥 Équipe
Membre de l'équipe du groupe 1.

## 📄 Licence
MIT