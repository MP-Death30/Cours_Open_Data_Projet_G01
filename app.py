import streamlit as st
import pandas as pd
from streamlit_folium import st_folium
from utils.data import calculate_trip
from utils.charts import create_comparison_chart, create_efficiency_scatter
from utils.chatbot import EcoAssistant
from utils.map_viz import create_trip_map
from dotenv import load_dotenv

# Chargement des variables d'environnement
load_dotenv()

# Configuration de la page
st.set_page_config(page_title="EcoRoute 🎄", layout="wide", page_icon="🎅")

# --- CSS PERSONNALISÉ NOËL ---
st.markdown("""
    <style>
    /* Titre Principal avec dégradé Rouge/Or */
    h1 {
        background: -webkit-linear-gradient(45deg, #D42426, #FFD700);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800;
    }
    
    /* Bouton Calculer en Vert Sapin pour contraster */
    div.stButton > button {
        background: linear-gradient(to right, #165B33, #1A8D4A);
        color: white;
        border: 2px solid #FFD700; /* Bordure Or */
        border-radius: 10px;
        font-size: 18px;
        font-weight: bold;
        transition: all 0.3s ease;
    }
    div.stButton > button:hover {
        transform: scale(1.05);
        border-color: #D42426;
    }

    /* Cartes (Containers) avec petite ombre dorée */
    div[data-testid="stExpander"] {
        border: 1px solid #E0E0E0;
        border-radius: 8px;
        box-shadow: 0 4px 6px rgba(255, 215, 0, 0.1);
    }
    </style>
""", unsafe_allow_html=True)

# Titre avec émojis
st.title("🎅 EcoRoute — Édition de Noël 🎄")
st.markdown("Comparez l'impact environnemental **et économique** de vos trajets pour les fêtes ! 🎁")

# --- Sidebar : IA ---
with st.sidebar:
    st.header("🤖 Configuration IA")
    model_choice = st.radio("Modèle chatbot :", ["Groq (Rapide)", "Gemini (Smart)"])
    use_groq = True if "Groq" in model_choice else False
    st.info(f"Actif : **{'Llama 3' if use_groq else 'Gemini 1.5'}**")

# --- Inputs ---
col1, col2, col3 = st.columns([2, 2, 1])
with col1:
    start = st.text_input("📍 Départ", "Paris")
with col2:
    end = st.text_input("📍 Arrivée", "Brest")
with col3:
    st.write(""); st.write("") 
    calc_btn = st.button("Calculer 🔍", type="primary", use_container_width=True)

# --- Session State ---
if "trip_result" not in st.session_state:
    st.session_state.trip_result = None
    st.session_state.coords = None

if calc_btn and start and end:
    with st.spinner("Calcul des itinéraires, prix et CO2..."):
        df, dist, cs, ce = calculate_trip(start, end)
        if df is not None:
            st.session_state.trip_result = df
            st.session_state.trip_dist = dist
            st.session_state.coords = (cs, ce)
            st.session_state.messages = [] 
        else:
            st.error("Ville introuvable. Essayez avec des grandes villes.")

# --- Affichage Résultats ---
if st.session_state.trip_result is not None:
    df = st.session_state.trip_result
    dist = st.session_state.trip_dist
    coords = st.session_state.coords
    
    # Onglets
    t1, t2, t3, t4 = st.tabs(["📊 Comparateur", "🤖 Analyse IA", "💬 Chat", "🗺️ Carte"])
    
    with t1:
        # --- KPI ---
        best_co2 = df.sort_values("CO2 (kg)").iloc[0]
        best_price = df.sort_values("Prix Moyen (€)").iloc[0]
        
        k1, k2, k3 = st.columns(3)
        k1.metric("Distance", f"{dist:.0f} km")
        k2.metric("Meilleur Prix", f"{best_price['Mode']}", f"{best_price['Prix Moyen (€)']} €")
        k3.metric("Meilleur CO2", f"{best_co2['Mode']}", f"{best_co2['CO2 (kg)']} kg")
        
        st.divider()

        # --- Détail Prix ---
        st.subheader("💰 Détail des Fourchettes de Prix")
        for _, row in df.iterrows():
            label = f"**{row['Mode']}** — {row['Prix Moyen (€)']:.0f}€ en moyenne"
            with st.expander(label):
                c1, c2, c3, c4 = st.columns(4)
                c1.metric("💵 Prix Min", f"{row['Prix Min (€)']:.2f}€")
                c2.metric("💰 Prix Moyen", f"{row['Prix Moyen (€)']:.2f}€")
                c3.metric("💸 Prix Max", f"{row['Prix Max (€)']:.2f}€")
                c4.metric("🌱 CO2", f"{row['CO2 (kg)']} kg", delta_color="inverse")

        st.divider()
        st.subheader("📈 Comparaison Visuelle")
        st.plotly_chart(create_comparison_chart(df), use_container_width=True)
        st.plotly_chart(create_efficiency_scatter(df), use_container_width=True)

    with t2:
        bot = EcoAssistant()
        st.markdown(bot.analyze_trip(start, end, df))
        
    with t3:
        st.write("Discutez avec EcoBot :")
        if "messages" not in st.session_state: st.session_state.messages = []
        for m in st.session_state.messages: st.chat_message(m["role"]).write(m["content"])
        
        if p := st.chat_input("Votre question..."):
            st.session_state.messages.append({"role": "user", "content": p})
            st.chat_message("user").write(p)
            bot = EcoAssistant()
            ctx = f"Trajet {start}-{end}. Best CO2: {best_co2['Mode']}."
            r = bot.chat(p, ctx, use_groq)
            st.session_state.messages.append({"role": "assistant", "content": r})
            st.chat_message("assistant").write(r)

    with t4:
        st.subheader(f"🗺️ Itinéraire : {start} ➝ {end}")
        
        # 1. Sélecteur de mode
        options_carte = ["Route", "Train", "Avion"]
        mode_choisi = st.selectbox("Afficher le tracé pour :", options_carte, index=0)
        
        # 2. Création des colonnes (Carte à gauche, Infos à droite)
        col_map, col_info = st.columns([2, 1])
        
        with col_map:
            # Affichage de la Carte
            map_obj = create_trip_map(coords[0], coords[1], start, end, selected_mode=mode_choisi)
            # On adapte la largeur à la colonne
            st_folium(map_obj, height=500, use_container_width=True)
            
        with col_info:
            st.markdown(f"### ℹ️ Infos : {mode_choisi}")
            
            # 3. Logique de filtrage selon votre demande
            target_keywords = []
            
            if mode_choisi == "Route":
                # Voiture (Thermique/Élec), Autocar, Vélo
                target_keywords = ["Voiture", "Autocar", "Vélo"]
            elif mode_choisi == "Train":
                # Tous les trains (TGV, Intercités, TER...)
                target_keywords = ["Train"]
            elif mode_choisi == "Avion":
                # Seulement l'avion
                target_keywords = ["Avion"]
            
            # 4. Boucle d'affichage des cartes d'info
            # On parcourt le dataframe et on affiche si le mode correspond aux mots-clés
            count = 0
            for _, row in df.iterrows():
                # On vérifie si le nom du mode contient un des mots-clés (ex: "Voiture" est dans "Voiture (Thermique)")
                if any(keyword in row['Mode'] for keyword in target_keywords):
                    count += 1
                    # Création d'une petite carte visuelle (Container)
                    with st.container(border=True):
                        st.markdown(f"**{row['Mode']}**")
                        
                        ci1, ci2 = st.columns(2)
                        ci1.metric("Prix Moy.", f"{row['Prix Moyen (€)']:.0f} €")
                        ci2.metric("CO2", f"{row['CO2 (kg)']} kg")
                        
                        # Petite barre de progression visuelle pour le CO2 (base 200kg)
                        st.progress(min(row['CO2 (kg)'] / 200, 1.0))

            if count == 0:
                st.info("Aucune donnée disponible pour ce mode.")