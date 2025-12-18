import streamlit as st
import pandas as pd
from utils.data import calculate_trip
from utils.charts import create_comparison_chart, create_impact_gauge, create_efficiency_scatter
from utils.chatbot import EcoAssistant
from dotenv import load_dotenv

# Chargement des variables d'environnement (.env)
load_dotenv()

# Configuration de la page
st.set_page_config(page_title="EcoRoute 🌱", layout="wide")

st.title("🌱 EcoRoute — Calculateur d'impact carbone")
st.markdown("Comparez l'impact environnemental de vos trajets et faites le bon choix !")

# --- Sidebar : Configuration IA ---
with st.sidebar:
    st.header("🤖 Configuration IA")
    model_choice = st.radio(
        "Modèle pour le Chatbot :",
        ["Groq (Ultra-Rapide)", "Gemini (Raisonnement)"],
        index=0
    )
    use_groq = True if "Groq" in model_choice else False
    st.divider()
    st.info(f"Modèle actif : **{'Llama 3.1 (via Groq)' if use_groq else 'Gemini 1.5 Flash'}**")

# --- Zone de saisie ---
col1, col2, col3 = st.columns([2, 2, 1])
with col1:
    start = st.text_input("📍 Ville de départ", "Paris")
with col2:
    end = st.text_input("📍 Ville d'arrivée", "Lyon")
with col3:
    st.write("") 
    st.write("") 
    calc_btn = st.button("Calculer 🔍", type="primary", use_container_width=True)

# --- GESTION DE LA MÉMOIRE (Session State) ---
# C'est ici qu'on empêche le rechargement de tout effacer

if "trip_result" not in st.session_state:
    st.session_state.trip_result = None
if "trip_dist" not in st.session_state:
    st.session_state.trip_dist = 0

# Si on clique sur le bouton, on lance le calcul ET on sauvegarde
if calc_btn and start and end:
    with st.spinner("Calcul des itinéraires et analyse CO2..."):
        df_res, dist = calculate_trip(start, end)
        if df_res is not None:
            st.session_state.trip_result = df_res
            st.session_state.trip_dist = dist
            # On vide l'historique de chat si on change de trajet
            st.session_state.messages = [] 
        else:
            st.error("Impossible de trouver ces villes.")

# --- Affichage du Résultat (si disponible en mémoire) ---
if st.session_state.trip_result is not None:
    df_res = st.session_state.trip_result
    dist = st.session_state.trip_dist
    
    # Séparation en onglets
    tab1, tab2, tab3 = st.tabs(["📊 Comparateur", "🤖 Analyse IA", "💬 Assistant"])
    
    with tab1:
        best_mode = df_res.sort_values("CO2 (kg)").iloc[0]
        worst_mode = df_res.sort_values("CO2 (kg)").iloc[-1]
        
        m1, m2, m3 = st.columns(3)
        m1.metric("Distance", f"{dist:.0f} km")
        m2.metric("Meilleur choix", f"{best_mode['Mode']}", f"{best_mode['CO2 (kg)']} kg CO2")
        m3.metric("Pire choix", f"{worst_mode['Mode']}", f"{worst_mode['CO2 (kg)']} kg CO2", delta_color="inverse")
        
        st.plotly_chart(create_comparison_chart(df_res), use_container_width=True)
        
        c1, c2 = st.columns(2)
        with c1:
            st.plotly_chart(create_efficiency_scatter(df_res), use_container_width=True)
        with c2:
            ratio = round(worst_mode['CO2 (kg)'] / max(best_mode['CO2 (kg)'], 0.1), 1)
            st.info(f"💡 Le train émet **{ratio}x moins** de CO2 que {worst_mode['Mode']} !")

    with tab2:
        # L'analyse est statique, on peut la relancer ou la stocker aussi
        # Pour simplifier, on la relance (rapide avec le cache ou le mock)
        bot = EcoAssistant()
        analysis = bot.analyze_trip(start, end, df_res)
        st.markdown(analysis)
        
    with tab3:
        st.write("Posez une question sur ce trajet ou l'écologie :")
        
        if "messages" not in st.session_state:
            st.session_state.messages = []

        for msg in st.session_state.messages:
            st.chat_message(msg["role"]).write(msg["content"])

        if prompt := st.chat_input("Ex: Comment réduire mon empreinte ?"):
            st.session_state.messages.append({"role": "user", "content": prompt})
            st.chat_message("user").write(prompt)
            
            bot = EcoAssistant()
            best_mode_name = df_res.sort_values("CO2 (kg)").iloc[0]['Mode']
            context = f"Trajet {start}-{end}. Meilleur mode: {best_mode_name}."
            
            response = bot.chat(prompt, context, use_groq=use_groq)
            
            st.session_state.messages.append({"role": "assistant", "content": response})
            st.chat_message("assistant").write(response)