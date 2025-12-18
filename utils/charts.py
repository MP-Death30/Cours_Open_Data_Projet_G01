import plotly.express as px
import plotly.graph_objects as go

def create_comparison_chart(df):
    """1. Comparateur visuel des modes (Bar Chart)."""
    # On travaille sur une copie pour ne pas impacter le dataframe original
    df_chart = df.copy()
    
    # Code couleur : Vert pour peu polluant, Rouge pour très polluant
    df_chart['Color'] = df_chart['CO2 (kg)'].apply(lambda x: 'red' if x > 50 else ('orange' if x > 10 else 'green'))
    
    fig = px.bar(
        df_chart.sort_values("CO2 (kg)"), 
        x="Mode", 
        y="CO2 (kg)",
        color="Color",
        color_discrete_map="identity",
        title="Impact Carbone par Mode de Transport",
        text_auto=True
    )
    return fig

def create_impact_gauge(co2_value):
    """2. Jauge d'impact pour le mode choisi (Gauge Chart)."""
    fig = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = co2_value,
        title = {'text': "Emissions (kg CO2)"},
        gauge = {
            'axis': {'range': [0, 200]},
            'bar': {'color': "darkblue"},
            'steps': [
                {'range': [0, 10], 'color': "lightgreen"},
                {'range': [10, 50], 'color': "yellow"},
                {'range': [50, 200], 'color': "salmon"}],
        }
    ))
    return fig

def create_efficiency_scatter(df):
    """3. Nuage de points : Distance vs Emission (Scatter)."""
    df_chart = df.copy()
    
    # --- CORRECTION ET ADAPTATION ---
    # 1. On crée une colonne temporaire en grammes pour que les bulles soient visibles
    # (0.1 kg ferait une bulle invisible, alors que 100 g fait une belle bulle)
    df_chart['Taille_Bulle'] = df_chart['Facteur (kgCO2/km)'] * 1000
    
    # 2. On met une taille minimale pour le vélo (sinon 0 * 1000 = 0 -> invisible)
    df_chart['Taille_Bulle'] = df_chart['Taille_Bulle'].replace(0, 10) 

    fig = px.scatter(
        df_chart, 
        x="Distance (km)", 
        y="CO2 (kg)", 
        size="Taille_Bulle",     # On utilise notre colonne calculée
        color="Mode",
        hover_data=['Facteur (kgCO2/km)'], # On affiche quand même la vraie donnée au survol
        title="Efficacité Énergétique (Taille = Facteur Pollution)"
    )
    return fig