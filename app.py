"""
Rotation AI - Premier League Lineup Predictor
=============================================
Predice la alineación probable de la próxima jornada usando ML
Autor: Tu Nombre
"""

import streamlit as st
import pandas as pd
import numpy as np
import joblib
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path

# Configuración de la página
st.set_page_config(
    page_title="Rotation AI - Premier League Predictor",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        color: #3d195b;
        text-align: center;
        margin-bottom: 2rem;
    }
    .prediction-box {
        padding: 1.5rem;
        border-radius: 10px;
        margin: 1rem 0;
    }
    .will-play {
        background-color: #d4edda;
        border: 2px solid #28a745;
    }
    .wont-play {
        background-color: #f8d7da;
        border: 2px solid #dc3545;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 8px;
        text-align: center;
    }
    .stButton>button {
        width: 100%;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================================
# FUNCIONES DE CARGA
# ============================================================================

@st.cache_resource
def load_model():
    """Carga el modelo y scaler"""
    try:
        model_path = Path("models/xgboost_model.pkl")
        scaler_path = Path("models/scaler.pkl")
        
        model = joblib.load(model_path)
        scaler = joblib.load(scaler_path)
        
        return model, scaler
    except Exception as e:
        st.error(f"Error cargando modelo: {e}")
        return None, None

@st.cache_data
def load_data():
    """Carga datos de jugadores"""
    try:
        data_path = Path("data/sample_players.csv")
        df = pd.read_csv(data_path)
        return df
    except Exception as e:
        st.error(f"Error cargando datos: {e}")
        return None

# ============================================================================
# FUNCIONES DE FEATURE ENGINEERING
# ============================================================================

def create_features(df):
    """
    Crea las 17 features necesarias para el modelo
    """
    df = df.copy()
    
    # 1. market_value_missing
    df['market_value_missing'] = df['market_value'].isna().astype(int)
    
    # 2. market_value_log
    df['market_value_log'] = np.log1p(df['market_value'].fillna(0))
    
    # 3. height_percentile
    df['height_percentile'] = df['height'].rank(pct=True) * 100
    
    # 4. value_age_decay
    df['value_age_decay'] = df['market_value'].fillna(0) / (df['age'] ** 2)
    
    # 5. captain_x_market
    df['captain_x_market'] = df['captain'] * df['market_value_log']
    
    # 6. position_x_age
    position_rank = {'G': 1, 'D': 2, 'M': 3, 'F': 4}
    df['position_rank'] = df['position'].map(position_rank)
    df['position_x_age'] = df['position_rank'] * df['age']
    
    # 7. player_convocations (simplificado: usar edad como proxy)
    df['player_convocations'] = df['age'] - 16  # Aprox. años de carrera
    
    # 8. team_avg_market_value
    team_avg = df.groupby('team')['market_value'].transform('mean')
    df['team_avg_market_value'] = team_avg
    
    # 9. player_value_vs_team
    df['player_value_vs_team'] = df['market_value'].fillna(0) / (team_avg + 1)
    
    # 10-13. pos_D, pos_F, pos_G, pos_M (one-hot encoding)
    df['pos_D'] = (df['position'] == 'D').astype(int)
    df['pos_F'] = (df['position'] == 'F').astype(int)
    df['pos_G'] = (df['position'] == 'G').astype(int)
    df['pos_M'] = (df['position'] == 'M').astype(int)
    
    # 14. country_frequency
    country_freq = df['country'].value_counts(normalize=True)
    df['country_frequency'] = df['country'].map(country_freq)
    
    # 15. team_frequency
    team_freq = df['team'].value_counts(normalize=True)
    df['team_frequency'] = df['team'].map(team_freq)
    
    # 16. age_group_encoded
    df['age_group'] = pd.cut(df['age'], 
                             bins=[0, 21, 25, 29, 33, 50],
                             labels=[0, 1, 2, 3, 4])
    df['age_group_encoded'] = df['age_group'].astype(int)
    
    # 17. market_tier_encoded
    df['market_tier'] = pd.cut(df['market_value'].fillna(0),
                               bins=[0, 1e6, 5e6, 15e6, 30e6, np.inf],
                               labels=[0, 1, 2, 3, 4])
    df['market_tier_encoded'] = df['market_tier'].astype(int)
    
    return df

def get_feature_columns():
    """Devuelve las 17 features en el orden correcto"""
    return [
        'market_value_missing',
        'market_value_log',
        'height_percentile',
        'value_age_decay',
        'captain_x_market',
        'position_x_age',
        'player_convocations',
        'team_avg_market_value',
        'player_value_vs_team',
        'pos_D',
        'pos_F',
        'pos_G',
        'pos_M',
        'country_frequency',
        'team_frequency',
        'age_group_encoded',
        'market_tier_encoded'
    ]

# ============================================================================
# FUNCIÓN DE PREDICCIÓN
# ============================================================================

def predict_lineup(df, model, scaler, team):
    """Predice la alineación para un equipo"""
    
    # Filtrar jugadores del equipo
    team_df = df[df['team'] == team].copy()
    
    if len(team_df) == 0:
        return None
    
    # Crear features
    team_df = create_features(team_df)
    
    # Seleccionar features
    feature_cols = get_feature_columns()
    X = team_df[feature_cols]
    
    # Escalar
    X_scaled = scaler.transform(X)
    
    # Predecir
    predictions = model.predict(X_scaled)
    probabilities = model.predict_proba(X_scaled)[:, 1]
    
    # Agregar resultados
    team_df['prediction'] = predictions
    team_df['probability'] = probabilities
    team_df['status'] = team_df['prediction'].map({1: '✅ Jugará', 0: '❌ Banca'})
    
    return team_df

# ============================================================================
# INTERFAZ PRINCIPAL
# ============================================================================

def main():
    
    # Header
    st.markdown('<h1 class="main-header">⚽ Rotation AI</h1>', unsafe_allow_html=True)
    st.markdown("### Predictor de Alineaciones - Premier League")
    st.markdown("---")
    
    # Cargar modelo y datos
    with st.spinner("Cargando modelo..."):
        model, scaler = load_model()
        df = load_data()
    
    if model is None or df is None:
        st.error("No se pudo cargar el modelo o los datos")
        st.info("Por favor verifica que existen los archivos:")
        st.code("models/xgboost_model.pkl\\nmodels/scaler.pkl\\ndata/sample_players.csv")
        return
    
    # Sidebar
    st.sidebar.title("⚙️ Configuración")
    
    # Seleccionar equipo
    teams = sorted(df['team'].unique())
    selected_team = st.sidebar.selectbox(
        "Selecciona un equipo:",
        teams,
        index=0
    )
    
    # Threshold de probabilidad
    threshold = st.sidebar.slider(
        "Umbral de probabilidad:",
        min_value=0.0,
        max_value=1.0,
        value=0.5,
        step=0.05,
        help="Jugadores con probabilidad mayor a este valor se consideran titulares"
    )
    
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 📊 Sobre el modelo")
    st.sidebar.info("""
    **Accuracy:** 81.6%
    
    **Algoritmo:** XGBoost
    
    **Features:** 17 variables
    
    Basado en datos de valor de mercado, edad, posición y estadísticas del equipo.
    """)
    
    st.sidebar.markdown("---")
    st.sidebar.markdown("### ℹ️ Información")
    st.sidebar.markdown("""
    Esta aplicación utiliza Machine Learning para predecir qué jugadores tienen mayor probabilidad de ser titulares en el próximo partido.
    
    **Desarrollado por:** Tu Nombre  
    **GitHub:** [Ver Código](https://github.com/tu-usuario/rotation-ai)
    """)
    
    # Hacer predicción
    st.markdown(f"## 🏟️ Predicción para {selected_team}")
    
    with st.spinner(f"Analizando jugadores de {selected_team}..."):
        results = predict_lineup(df, model, scaler, selected_team)
    
    if results is None:
        st.warning(f"No hay datos disponibles para {selected_team}")
        return
    
    # Métricas generales
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("Total Jugadores", len(results))
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        will_play = (results['prediction'] == 1).sum()
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("Titulares probables", will_play)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col3:
        wont_play = (results['prediction'] == 0).sum()
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("Banca probable", wont_play)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col4:
        avg_prob = results['probability'].mean()
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("Confianza promedio", f"{avg_prob:.1%}")
        st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Tabs para diferentes vistas
    tab1, tab2, tab3 = st.tabs(["📋 Alineación Probable", "📊 Análisis Detallado", "🎯 Por Posición"])
    
    with tab1:
        # Alineación probable
        st.markdown("### ✅ Titulares Probables")
        
        starters = results[results['prediction'] == 1].sort_values('probability', ascending=False)
        
        if len(starters) > 0:
            for idx, player in starters.iterrows():
                col_player, col_prob, col_value = st.columns([3, 1, 1])
                
                with col_player:
                    st.markdown(f"**{player['player_name']}** ({player['position']})")
                    st.caption(f"{player['age']} años • {player['country']}")
                
                with col_prob:
                    prob_pct = player['probability'] * 100
                    color = '#28a745' if prob_pct >= 70 else '#ffc107'
                    st.markdown(f"<span style='color:{color}; font-size:1.2em; font-weight:bold'>{prob_pct:.1f}%</span>", 
                              unsafe_allow_html=True)
                
                with col_value:
                    value_m = player['market_value'] / 1e6 if pd.notna(player['market_value']) else 0
                    st.caption(f"€{value_m:.1f}M")
                
                st.markdown("---")
        else:
            st.info("No hay jugadores con alta probabilidad de jugar según el umbral seleccionado")
        
        # Banca
        st.markdown("### ❌ Banca Probable")
        
        bench = results[results['prediction'] == 0].sort_values('probability', ascending=False)
        
        with st.expander(f"Ver {len(bench)} jugadores en banca", expanded=False):
            for idx, player in bench.iterrows():
                col_player, col_prob = st.columns([4, 1])
                
                with col_player:
                    st.markdown(f"**{player['player_name']}** ({player['position']})")
                
                with col_prob:
                    st.caption(f"{player['probability']*100:.1f}%")
    
    with tab2:
        st.markdown("### 📊 Distribución de Probabilidades")
        
        # Histograma
        fig = px.histogram(
            results,
            x='probability',
            nbins=20,
            title="Distribución de Probabilidades de Jugar",
            labels={'probability': 'Probabilidad de Jugar', 'count': 'Nº Jugadores'},
            color_discrete_sequence=['#3d195b']
        )
        fig.add_vline(x=threshold, line_dash="dash", line_color="red", 
                     annotation_text=f"Umbral ({threshold})")
        fig.update_layout(showlegend=False)
        st.plotly_chart(fig, use_container_width=True)
        
        # Scatter plot: Valor vs Probabilidad
        st.markdown("### 💰 Valor de Mercado vs Probabilidad")
        
        fig2 = px.scatter(
            results,
            x='market_value',
            y='probability',
            color='position',
            size='age',
            hover_data=['player_name', 'age', 'country'],
            title="Relación entre Valor y Probabilidad de Jugar",
            labels={
                'market_value': 'Valor de Mercado (€)',
                'probability': 'Probabilidad de Jugar',
                'position': 'Posición'
            }
        )
        st.plotly_chart(fig2, use_container_width=True)
        
        # Tabla completa
        st.markdown("### 📋 Tabla Completa de Jugadores")
        
        display_df = results[[
            'player_name', 'position', 'age', 'market_value', 
            'probability', 'status'
        ]].sort_values('probability', ascending=False)
        
        display_df['market_value'] = display_df['market_value'].apply(
            lambda x: f"€{x/1e6:.1f}M" if pd.notna(x) else "N/A"
        )
        display_df['probability'] = display_df['probability'].apply(lambda x: f"{x*100:.1f}%")
        
        display_df.columns = ['Jugador', 'Pos', 'Edad', 'Valor', 'Probabilidad', 'Predicción']
        
        st.dataframe(display_df, use_container_width=True, hide_index=True)
    
    with tab3:
        st.markdown("### 🎯 Análisis por Posición")
        
        # Gráfico por posición
        position_stats = results.groupby('position').agg({
            'prediction': 'sum',
            'probability': 'mean'
        }).reset_index()
        
        position_stats.columns = ['Posición', 'Titulares', 'Prob. Promedio']
        
        col1, col2 = st.columns(2)
        
        with col1:
            fig = px.bar(
                position_stats,
                x='Posición',
                y='Titulares',
                title="Titulares Probables por Posición",
                color='Titulares',
                color_continuous_scale='Viridis',
                text='Titulares'
            )
            fig.update_traces(textposition='outside')
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            fig = px.bar(
                position_stats,
                x='Posición',
                y='Prob. Promedio',
                title="Probabilidad Promedio por Posición",
                color='Prob. Promedio',
                color_continuous_scale='Blues',
                text='Prob. Promedio'
            )
            fig.update_traces(texttemplate='%{text:.2f}', textposition='outside')
            st.plotly_chart(fig, use_container_width=True)
        
        # Detalles por posición
        position_names = {'G': '🥅 Porteros', 'D': '🛡️ Defensas', 'M': '⚙️ Mediocampistas', 'F': '⚽ Delanteros'}
        
        for position in ['G', 'D', 'M', 'F']:
            pos_players = results[results['position'] == position].sort_values('probability', ascending=False)
            
            if len(pos_players) > 0:
                with st.expander(f"{position_names[position]} ({len(pos_players)} jugadores)", expanded=False):
                    for _, player in pos_players.iterrows():
                        cols = st.columns([3, 1, 1])
                        with cols[0]:
                            st.write(f"**{player['player_name']}**")
                        with cols[1]:
                            prob_color = '🟢' if player['probability'] >= 0.7 else '🟡' if player['probability'] >= 0.5 else '🔴'
                            st.write(f"{prob_color} {player['probability']*100:.1f}%")
                        with cols[2]:
                            st.write(player['status'])

if __name__ == "__main__":
    main()
