import plotly.express as px
import plotly.graph_objects as go

def create_comparison_chart(df):
    """1. Comparateur visuel des modes (Bar Chart)."""
    # Code couleur : Vert pour peu polluant, Rouge pour très polluant
    df['Color'] = df['CO2 (kg)'].apply(lambda x: 'red' if x > 50 else ('orange' if x > 10 else 'green'))
    
    fig = px.bar(
        df.sort_values("CO2 (kg)"), 
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
    fig = px.scatter(
        df, 
        x="Distance (km)", 
        y="CO2 (kg)", 
        size="Facteur (gCO2/km)", 
        color="Mode",
        title="Efficacité Énergétique (Taille = Facteur Pollution)"
    )
    return fig