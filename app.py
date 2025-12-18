import streamlit as st
import pandas as pd
from utils.data_enhanced import calculate_trip
from utils.charts import create_comparison_chart, create_impact_gauge, create_efficiency_scatter
from utils.chatbot import EcoAssistant
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(page_title="EcoRoute 🌱", layout="wide")

st.title("🌱 EcoRoute — Calculateur d'impact carbone")
st.markdown("Comparez l'impact environnemental de vos trajets et faites le bon choix !")

# --- Zone de saisie ---
col1, col2, col3 = st.columns([2, 2, 1])
with col1:
    start = st.text_input("📍 Ville de départ", "Paris")
with col2:
    end = st.text_input("📍 Ville d'arrivée", "Lyon")
with col3:
    st.write("") # Spacer
    st.write("") 
    calc_btn = st.button("Calculer 🔍", type="primary", use_container_width=True)

# --- Résultat ---
# --- Résultat ---
if calc_btn and start and end:
    with st.spinner("Calcul des itinéraires et analyse CO2..."):
        try:
            result = calculate_trip(start, end)
            
            if result is None or result[0] is None:
                st.error("❌ Impossible de trouver ces villes. Vérifiez l'orthographe ou essayez :")
                st.info("✅ Paris, Lyon, Marseille, Toulouse, Bordeaux, Nice, Nantes, Strasbourg, Montpellier, Lille")
            else:
                df_res, dist = result
                
                # Séparation en onglets
                tab1, tab2, tab3 = st.tabs(["📊 Comparateur", "🤖 Analyse IA", "💬 Assistant"])
                
            with tab1:
                # Métriques clés
                best_mode = df_res.sort_values("CO2 (kg)").iloc[0]
                worst_mode = df_res.sort_values("CO2 (kg)").iloc[-1]
                cheapest_mode = df_res.sort_values("Prix Moyen (€)").iloc[0]
    
                st.markdown("### 📊 Comparaison Complète")
    
                # Afficher UNIQUEMENT les colonnes importantes
                display_columns = ['Mode', 'Distance (km)', 'CO2 (kg)', 'Prix Min (€)', 'Prix Moyen (€)', 'Prix Max (€)']
                st.dataframe(
                    df_res[display_columns].style.highlight_min(
                        subset=['CO2 (kg)', 'Prix Moyen (€)'],
                        color='lightgreen'
                    ),
                    use_container_width=True
            )
    
                # Métriques principales
                st.markdown("### 🎯 Recommandations")
                m1, m2, m3, m4 = st.columns(4)
                
                m1.metric("📏 Distance", f"{dist:.0f} km")
                
                m2.metric(
                    "🌱 Plus Écologique", 
                    f"{best_mode['Mode']}", 
                    f"{best_mode['CO2 (kg)']} kg CO2"
                )
                
                m3.metric(
                    "💰 Moins Cher", 
                    f"{cheapest_mode['Mode']}", 
                    f"{cheapest_mode['Prix Moyen (€)']}€"
                )
                
                m4.metric(
                    "🚨 Plus Polluant", 
                    f"{worst_mode['Mode']}", 
                    f"{worst_mode['CO2 (kg)']} kg CO2"
                )
                
                # Détails des fourchettes de prix
                st.markdown("### 💰 Détail des Fourchettes de Prix")
                
                for _, row in df_res.iterrows():
                    with st.expander(f"**{row['Mode']}** - {row['Prix Moyen (€)']:.0f}€ en moyenne"):
                        col1, col2, col3, col4 = st.columns(4)
                        
                        col1.metric("💵 Prix Minimum", f"{row['Prix Min (€)']:.2f}€", help="Conditions optimales")
                        col2.metric("💰 Prix Moyen", f"{row['Prix Moyen (€)']:.2f}€", help="Estimation réaliste")
                        col3.metric("💸 Prix Maximum", f"{row['Prix Max (€)']:.2f}€", help="Conditions défavorables")
                        col4.metric("🌱 CO2", f"{row['CO2 (kg)']} kg")
                
                # Graphiques
                st.markdown("### 📈 Visualisations")
                st.plotly_chart(create_comparison_chart(df_res), use_container_width=True)
                
                c1, c2 = st.columns(2)
                with c1:
                    st.plotly_chart(create_efficiency_scatter(df_res), use_container_width=True)
                with c2:
                    st.info(f"💡 Le train émet {round(worst_mode['CO2 (kg)'] / max(best_mode['CO2 (kg)'], 0.1), 1)}x moins de CO2 !")
                    
                    price_range = df_res['Prix Moyen (€)'].max() - df_res['Prix Moyen (€)'].min()
                    st.success(f"💰 Écart de prix : {price_range:.0f}€ entre le moins cher et le plus cher")
                
                with tab2:
                    st.markdown("### 🤖 Analyse Intelligente par IA")
                    
                    try:
                        bot = EcoAssistant()
                        
                        with st.spinner("🧠 Analyse en cours..."):
                            analysis = bot.analyze_trip(start, end, df_res)
                        
                        st.markdown(analysis)
                    
                    except Exception as e:
                        st.warning("⚠️ L'assistant IA est temporairement indisponible")
                        st.markdown("""
                        ### Analyse Automatique
                        
                        **🌱 Recommandation Écologique :**
                        Le **train** reste le champion de l'éco-mobilité.
                        
                        **💰 Recommandation Économique :**
                        Le **covoiturage** et le **bus** offrent les meilleurs prix.
                        
                        Consultez le tableau comparatif ci-dessus !
                        """)
                        
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
                        context = f"Trajet {start}-{end}. Meilleur mode: {best_mode['Mode']}."
                        response = bot.chat(prompt, context)
                        
                        st.session_state.messages.append({"role": "assistant", "content": response})
                        st.chat_message("assistant").write(response)
        
        except Exception as e:
            st.error(f"❌ Erreur lors du calcul : {str(e)}")
            st.info("💡 Essayez avec des grandes villes françaises : Paris, Lyon, Marseille, Toulouse...")
