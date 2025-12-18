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
    
    # Sélecteur pour laisser l'utilisateur choisir son "cerveau"
    model_choice = st.radio(
        "Modèle pour le Chatbot :",
        ["Groq (Ultra-Rapide)", "Gemini (Raisonnement)"],
        help="Groq est idéal pour la fluidité. Gemini est meilleur pour les analyses complexes.",
        index=0 # Groq par défaut
    )
    
    # On transforme ce choix en booléen
    use_groq = True if "Groq" in model_choice else False
    
    st.divider()
    # Mise à jour des noms affichés
    st.info(f"Modèle actif : **{'Llama 3.1 (via Groq)' if use_groq else 'Gemini 1.5 Flash'}**")

# --- Zone de saisie ---
col1, col2, col3 = st.columns([2, 2, 1])
with col1:
    start = st.text_input("📍 Ville de départ", "Paris")
with col2:
    end = st.text_input("📍 Ville d'arrivée", "Lyon")
with col3:
    st.write("") # Spacer pour aligner le bouton
    st.write("") 
    # CORRECTION WARNING : width="stretch" au lieu de use_container_width=True pour les boutons récents
    calc_btn = st.button("Calculer 🔍", type="primary") 

# --- Résultat ---
if calc_btn and start and end:
    with st.spinner("Calcul des itinéraires et analyse CO2..."):
        # 1. Calculs via utils/data.py
        df_res, dist = calculate_trip(start, end)
        
        if df_res is not None:
            # Séparation en onglets
            tab1, tab2, tab3 = st.tabs(["📊 Comparateur", "🤖 Analyse IA", "💬 Assistant"])
            
            with tab1:
                # --- Onglet 1 : Graphiques et KPIs ---
                best_mode = df_res.sort_values("CO2 (kg)").iloc[0]
                worst_mode = df_res.sort_values("CO2 (kg)").iloc[-1]
                
                # Métriques
                m1, m2, m3 = st.columns(3)
                m1.metric("Distance", f"{dist:.0f} km")
                m2.metric("Meilleur choix", f"{best_mode['Mode']}", f"{best_mode['CO2 (kg)']} kg CO2")
                m3.metric("Pire choix", f"{worst_mode['Mode']}", f"{worst_mode['CO2 (kg)']} kg CO2", delta_color="inverse")
                
                # Graphiques (CORRECTION WARNING : use_container_width est correct ici pour plotly, 
                # mais si vous avez encore le warning, essayez sans paramètre car c'est souvent par défaut maintenant)
                st.plotly_chart(create_comparison_chart(df_res), use_container_width=True)
                
                c1, c2 = st.columns(2)
                with c1:
                    st.plotly_chart(create_efficiency_scatter(df_res), use_container_width=True)
                with c2:
                    # Petit calcul de ratio pour l'impact
                    ratio = round(worst_mode['CO2 (kg)'] / max(best_mode['CO2 (kg)'], 0.1), 1)
                    st.info(f"💡 Le train émet **{ratio}x moins** de CO2 que {worst_mode['Mode']} !")

            with tab2:
                # --- Onglet 2 : Analyse automatique du trajet ---
                bot = EcoAssistant()
                analysis = bot.analyze_trip(start, end, df_res)
                st.markdown(analysis)
                
            with tab3:
                # --- Onglet 3 : Chatbot interactif ---
                st.write("Posez une question sur ce trajet ou l'écologie :")
                
                # Gestion de l'historique de chat
                if "messages" not in st.session_state:
                    st.session_state.messages = []

                # Affichage des anciens messages
                for msg in st.session_state.messages:
                    st.chat_message(msg["role"]).write(msg["content"])

                # Zone de saisie utilisateur
                if prompt := st.chat_input("Ex: Comment réduire mon empreinte ?"):
                    # 1. Afficher message user
                    st.session_state.messages.append({"role": "user", "content": prompt})
                    st.chat_message("user").write(prompt)
                    
                    # 2. Appeler l'IA avec le modèle choisi
                    bot = EcoAssistant()
                    
                    # On injecte le contexte du trajet actuel
                    context = f"Trajet {start}-{end}. Meilleur mode: {best_mode['Mode']}."
                    
                    # On passe le choix utilisateur
                    response = bot.chat(prompt, context, use_groq=use_groq)
                    
                    # 3. Afficher réponse assistant
                    st.session_state.messages.append({"role": "assistant", "content": response})
                    st.chat_message("assistant").write(response)

        else:
            st.error("Impossible de trouver ces villes. Essayez avec des grandes villes françaises (ex: Paris, Marseille, Bordeaux).")