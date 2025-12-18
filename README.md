# EcoRoute — Calculateur d'impact carbone transport

## 📋 Description
EcoRoute est une application intelligente qui calcule et compare l'empreinte carbone de différents modes de transport (Train, Voiture, Avion, Vélo) pour un trajet donné. Elle vise à sensibiliser les utilisateurs à l'impact environnemental de leurs déplacements en proposant des alternatives moins polluantes et des équivalences concrètes générées par IA.

## 🎯 Fonctionnalités
- **Calcul d'empreinte CO2** : Estimation précise des émissions pour un trajet donné.
- **Comparateur de modes** : Visualisation graphique (Train vs Voiture vs Avion vs Vélo).
- **Assistant Éco-mobilité (IA)** : Chatbot pour conseiller sur le meilleur mode de transport et répondre aux questions écologiques.
- **Multi-LLM & Résilience** : Utilisation conjointe de **Groq** (Llama 3.1), **Gemini** (1.5 Flash) et **Hugging Face** (Zephyr) avec un système de bascule automatique en cas de panne.
- **Équivalences concrètes** : Traduction de l'impact carbone en termes parlants (ex: "ce trajet en voiture équivaut à X arbres coupés").

## 🛠️ Installation

### 1. Cloner le projet

``` bash
git clone https://github.com/votre-username/ecoroute-app.git
cd ecoroute-app
```

### 2. Installer les dépendances
Ce projet utilise `uv` pour la gestion des paquets.

``` bash
uv sync
```

### 3. Configuration des Clés API (Indispensable)
Pour que l'intelligence artificielle fonctionne, vous devez récupérer des clés API gratuites.

**A. Google Gemini (Pour l'analyse de fond)**
1. Allez sur [Google AI Studio](https://aistudio.google.com/app/apikey).
2. Connectez-vous avec un compte Google.
3. Cliquez sur **"Create API Key"**.

**B. Groq (Pour la rapidité du chat)**
1. Allez sur [Groq Cloud Console](https://console.groq.com/keys).
2. Créez un compte et cliquez sur **"Create API Key"**.

**C. Hugging Face (Filet de sécurité)**
1. Allez sur [Hugging Face Tokens](https://huggingface.co/settings/tokens).
2. Créez un nouveau token en mode "Read".

### 4. Créer le fichier .env
Créez un fichier nommé `.env` à la racine du projet et collez-y vos clés :

``` bash
# Fichier .env

# 1. Clé Google (Obligatoire pour l'analyse)
GEMINI_API_KEY="AIzaSyB..."

# 2. Clé Groq (Recommandé pour la vitesse)
GROQ_API_KEY="gsk_..."

# 3. Clé Hugging Face (Backup de sécurité)
HUGGINGFACE_API_KEY="hf_..."
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
Membre du Groupe 1

## 📄 Licence
MIT