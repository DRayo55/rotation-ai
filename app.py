import streamlit as st
import pandas as pd
import numpy as np
import joblib
from pathlib import Path
from datetime import datetime
import base64

st.set_page_config(
    page_title="⚽ MatchLineup AI - Premier League",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Diccionario con URLs de escudos de equipos

TEAM_BADGES = {
    'Arsenal': 'https://upload.wikimedia.org/wikipedia/en/5/53/Arsenal_FC.svg',
    'Manchester City': 'https://upload.wikimedia.org/wikipedia/en/e/eb/Manchester_City_FC_badge.svg',
    'Aston Villa': 'https://upload.wikimedia.org/wikipedia/en/f/f9/Aston_Villa_FC_crest_%282016%29.svg',
    'Manchester United': 'https://upload.wikimedia.org/wikipedia/en/7/7a/Manchester_United_FC_crest.svg',
    'Chelsea': 'https://upload.wikimedia.org/wikipedia/en/c/cc/Chelsea_FC.svg',
    'Liverpool': 'https://upload.wikimedia.org/wikipedia/en/0/0c/Liverpool_FC.svg',
    'Brighton & Hove Albion': 'https://upload.wikimedia.org/wikipedia/en/f/fd/Brighton_%26_Hove_Albion_logo.svg',
    'Newcastle United': 'https://upload.wikimedia.org/wikipedia/en/5/56/Newcastle_United_Logo.svg',
    'Tottenham Hotspur': 'https://upload.wikimedia.org/wikipedia/en/b/b4/Tottenham_Hotspur.svg',
    'Brentford': 'https://upload.wikimedia.org/wikipedia/en/2/2a/Brentford_FC_crest.svg',
    'Everton': 'https://upload.wikimedia.org/wikipedia/en/7/7c/Everton_FC_logo.svg',
    'Bournemouth': 'https://upload.wikimedia.org/wikipedia/en/e/e5/AFC_Bournemouth_%282013%29.svg',
    'West Ham United': 'https://upload.wikimedia.org/wikipedia/en/c/c2/West_Ham_United_FC_logo.svg',
    'Fulham': 'https://upload.wikimedia.org/wikipedia/en/e/eb/Fulham_FC_%28shield%29.svg',
    'Crystal Palace': 'https://upload.wikimedia.org/wikipedia/en/0/0c/Crystal_Palace_FC_logo.svg',
    'Wolverhampton': 'https://upload.wikimedia.org/wikipedia/en/f/fc/Wolverhampton_Wanderers.svg',
    'Nottingham Forest': 'https://upload.wikimedia.org/wikipedia/en/e/e5/Nottingham_Forest_F.C._logo.svg',
    'Burnley': 'https://upload.wikimedia.org/wikipedia/en/6/6d/Burnley_FC_Logo.svg',
    'Leeds United': 'https://upload.wikimedia.org/wikipedia/en/5/54/Leeds_United_F.C._logo.svg',
    'Sunderland': 'https://upload.wikimedia.org/wikipedia/en/7/77/Logo_Sunderland.svg'
}

def get_team_badge(team_name):
    """Obtiene la URL del escudo del equipo"""
    return TEAM_BADGES.get(team_name, None)

def load_logo_as_base64(logo_path):
    """Carga el logo y lo convierte a base64 para embeber en HTML"""
    try:
        with open(logo_path, 'rb') as f:
            data = f.read()
        return base64.b64encode(data).decode()
    except:
        return None

def display_app_header():
    """Muestra el header principal de la app con el logo"""
    logo_path = Path("assets/logo.png")

    # Intentar cargar el logo local
    logo_base64 = load_logo_as_base64(logo_path)

    if logo_base64:
        # Logo desde archivo local
        header_html = f'''
        <div style="text-align: center; padding: 0px 0; margin-bottom: 0px;">
            <img src="data:image/png;base64,{logo_base64}" 
                 style="max-width: 300px; width: 100%; height: auto; display: block; margin: 0 auto;" />
        </div>
        '''
    else:
        # Fallback: texto si no encuentra el logo
        header_html = '''
        <div style="text-align: center; padding: 20px 0; margin-bottom: 10px;">
            <h1 style="color: #a8ff5e; font-size: 48px; margin: 0; font-weight: 800;">
                <span style="color: white;">Match</span><span style="color: #a8ff5e;">Lineup</span> 
                <span style="color: #a8ff5e;">AI</span>
            </h1>
        </div>
        '''

    st.markdown(header_html, unsafe_allow_html=True)

def display_team_header(team_name, next_match_info=None, show_formation=True):
    """Muestra el header con escudo, nombre y próximo partido - TODO CENTRADO"""
    badge_url = get_team_badge(team_name)

    # HTML completo para centrar todo
    header_html = '<div style="text-align: center; padding: 20px 0; margin-bottom: 20px;">'

    # Escudo centrado
    if badge_url:
        header_html += f'<img src="{badge_url}" style="width: 100px; display: block; margin: 0 auto 15px auto;" />'

    # Nombre del equipo
    header_html += f'<h1 style="color: white; margin: 10px 0 5px 0; font-size: 36px;">{team_name}</h1>'

    # Formación (solo si show_formation=True)
    if show_formation:
        header_html += '<p style="color: #ffd700; font-size: 18px; font-weight: 600; margin: 5px 0;">Formación: 4-3-3</p>'

    # Próximo partido
    if next_match_info:
        if next_match_info['is_home']:
            match_text = f"📅 Próximo: {next_match_info['date']} vs {next_match_info['opponent']} ({next_match_info['location']})"
        else:
            match_text = f"📅 Próximo: {next_match_info['date']} vs {next_match_info['opponent']} ({next_match_info['location']})"

        header_html += f'<p style="color: white; background: rgba(0,0,0,0.3); padding: 8px 15px; border-radius: 8px; margin: 10px auto 0 auto; font-size: 14px; display: inline-block;">{match_text}</p>'

    header_html += '</div>'

    st.markdown(header_html, unsafe_allow_html=True)

def load_custom_css():
    st.markdown("""
    <style>
    .football-field {
        background: linear-gradient(180deg, #2d5016 0%, #1a3a0f 100%);
        border: 3px solid #ffffff;
        border-radius: 10px;
        padding: 40px 20px;
        position: relative;
        min-height: 700px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.3);
        width: 100%;
        max-width: 1400px;
        margin: 0 auto;
    }

    .center-line {
        position: absolute;
        top: 50%;
        left: 0;
        width: 100%;
        height: 2px;
        background: white;
        transform: translateY(-50%);
        opacity: 0.3;
    }

    .center-circle {
        position: absolute;
        top: 50%;
        left: 50%;
        width: 120px;
        height: 120px;
        border: 2px solid white;
        border-radius: 50%;
        transform: translate(-50%, -50%);
        opacity: 0.3;
    }

    .lineup-row {
        display: flex;
        justify-content: center;
        align-items: center;
        flex-wrap: wrap;
        margin: 20px 0;
        gap: 15px;
        position: relative;
        z-index: 10;
        width: 100%;
    }

    .player-card {
        background: rgba(255, 255, 255, 0.95);
        border: 2px solid #1a3a0f;
        border-radius: 10px;
        padding: 12px 16px;
        text-align: center;
        width: 140px;
        flex-shrink: 0;
        box-shadow: 0 4px 6px rgba(0,0,0,0.2);
        transition: all 0.3s ease;
    }

    .player-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 12px rgba(0,0,0,0.3);
    }

    .player-number {
        font-weight: 900;
        font-size: 28px;
        color: #1a3a0f;
        margin-bottom: 6px;
        text-shadow: 1px 1px 2px rgba(0,0,0,0.1);
    }

    .player-name {
        font-weight: 600;
        font-size: 11px;
        color: #1a3a0f;
        margin-bottom: 4px;
        text-transform: uppercase;
        letter-spacing: 0.3px;
        word-wrap: break-word;
        line-height: 1.2;
    }

    .player-position-badge {
        font-size: 9px;
        color: #666;
        font-weight: 600;
        background: rgba(0,0,0,0.05);
        padding: 2px 6px;
        border-radius: 4px;
        display: inline-block;
        margin-top: 3px;
    }

    .line-label {
        text-align: center;
        color: white;
        font-weight: 700;
        font-size: 15px;
        margin: 15px 0 8px 0;
        text-transform: uppercase;
        letter-spacing: 2px;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.5);
        width: 100%;
    }

    .goalkeeper .player-card {
        background: rgba(255, 215, 0, 0.95);
        border-color: #d4af37;
    }

    .bench-section {
        margin-top: 30px;
        padding: 20px;
        background: rgba(255, 255, 255, 0.05);
        border-radius: 10px;
        max-width: 1400px;
        margin-left: auto;
        margin-right: auto;
    }

    .bench-title {
        color: white;
        font-size: 20px;
        font-weight: 700;
        text-align: center;
        margin-bottom: 15px;
        text-transform: uppercase;
        letter-spacing: 1px;
    }

    .bench-player {
        display: flex;
        align-items: center;
        padding: 10px 15px;
        margin: 8px 0;
        background: rgba(255, 255, 255, 0.9);
        border-radius: 8px;
        transition: all 0.2s ease;
    }

    .bench-player:hover {
        background: rgba(255, 255, 255, 1);
        transform: translateX(5px);
    }

    .bench-player-top5 {
        background: linear-gradient(135deg, rgba(255, 215, 0, 0.3) 0%, rgba(255, 255, 255, 0.9) 100%);
        border-left: 4px solid #ffd700;
        font-weight: 600;
    }

    .bench-number {
        font-size: 20px;
        font-weight: 900;
        color: #1a3a0f;
        min-width: 40px;
        text-align: center;
    }

    .bench-name {
        flex-grow: 1;
        font-size: 14px;
        color: #1a3a0f;
        margin-left: 15px;
    }

    .bench-position {
        font-size: 12px;
        color: #666;
        font-weight: 600;
        background: rgba(0,0,0,0.05);
        padding: 4px 10px;
        border-radius: 4px;
        margin-right: 10px;
    }

    .bench-rank {
        font-size: 11px;
        color: #888;
        min-width: 30px;
        text-align: right;
    }

    .stat-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 20px;
        border-radius: 10px;
        color: white;
        text-align: center;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }

    .stat-number {
        font-size: 32px;
        font-weight: 900;
        margin-bottom: 5px;
    }

    .stat-label {
        font-size: 14px;
        opacity: 0.9;
    }

    .match-card {
        padding: 15px;
        margin: 10px 0;
        border-radius: 8px;
        background: white;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        transition: all 0.2s ease;
    }

    .match-card:hover {
        box-shadow: 0 4px 8px rgba(0,0,0,0.15);
        transform: translateY(-2px);
    }

    .match-finished {
        border-left: 4px solid #28a745;
    }

    .match-scheduled {
        border-left: 4px solid #ffc107;
    }

    .match-postponed {
        border-left: 4px solid #dc3545;
    }

    .match-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 10px;
    }

    .match-date {
        font-size: 13px;
        color: #666;
        font-weight: 600;
    }

    .match-status {
        font-size: 11px;
        padding: 3px 8px;
        border-radius: 4px;
        font-weight: 600;
    }

    .status-finished {
        background: #28a745;
        color: white;
    }

    .status-scheduled {
        background: #ffc107;
        color: #000;
    }

    .status-postponed {
        background: #dc3545;
        color: white;
    }

    .match-teams {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 10px 0;
    }

    .team-home, .team-away {
        flex: 1;
        font-size: 15px;
        font-weight: 600;
        color: #1a3a0f;
    }

    .team-away {
        text-align: right;
    }

    .match-score {
        font-size: 24px;
        font-weight: 900;
        color: #1a3a0f;
        min-width: 80px;
        text-align: center;
    }

    .match-vs {
        font-size: 16px;
        color: #999;
        font-weight: 600;
        min-width: 80px;
        text-align: center;
    }
    </style>
    """, unsafe_allow_html=True)

def calculate_temporal_features_from_history(df_historico):
    df_hist = df_historico.copy()
    df_hist['minutesPlayed'] = df_hist['minutesPlayed'].fillna(0)

    df_hist['player_avg_minutes_temp'] = df_hist.groupby('id_player')['minutesPlayed'].expanding().mean().reset_index(level=0, drop=True)
    df_hist['player_last_3_avg_temp'] = df_hist.groupby('id_player')['minutesPlayed'].transform(lambda x: x.rolling(3, min_periods=1).mean())
    df_hist['player_consistency_temp'] = df_hist.groupby('id_player')['minutesPlayed'].expanding().std().reset_index(level=0, drop=True).fillna(0)
    df_hist['performance_trend_temp'] = df_hist.groupby('id_player')['minutesPlayed'].diff().fillna(0)

    features_temporales = df_hist.groupby('id_player').agg({
        'player_avg_minutes_temp': 'last',
        'player_last_3_avg_temp': 'last',
        'player_consistency_temp': 'last',
        'performance_trend_temp': 'last',
        'team': 'last',
        'position': 'last',
        'captain': 'last',
        'height': 'last',
        'country_': 'last',
        'market_value': 'last',
        'age': 'last'
    }).reset_index()

    features_temporales.rename(columns={
        'player_avg_minutes_temp': 'player_avg_minutes',
        'player_last_3_avg_temp': 'player_last_3_avg',
        'player_consistency_temp': 'player_consistency',
        'performance_trend_temp': 'performance_trend'
    }, inplace=True)

    features_temporales['momentum'] = features_temporales['player_last_3_avg'] - features_temporales['player_avg_minutes']

    return features_temporales

def create_features(df):
    df = df.copy()

    df['market_value_missing'] = df['market_value'].isna().astype(int)
    df['market_value'] = df['market_value'].fillna(0)
    df['market_value_log'] = np.log1p(df['market_value'])
    df['value_age_decay'] = df['market_value'] / (df['age'] ** 2)
    df['captain_x_market'] = df['captain'] * df['market_value_log']

    position_rank = {'G': 1, 'D': 2, 'M': 3, 'F': 4}
    df['position_rank'] = df['position'].map(position_rank)
    df['position_x_age'] = df['position_rank'] * df['age']

    df['pos_D'] = (df['position'] == 'D').astype(int)
    df['pos_F'] = (df['position'] == 'F').astype(int)
    df['pos_G'] = (df['position'] == 'G').astype(int)
    df['pos_M'] = (df['position'] == 'M').astype(int)

    df['player_convocations'] = df['age'] - 16

    team_avg = df.groupby('team')['market_value'].transform('mean')
    df['team_avg_market_value'] = team_avg
    df['player_value_vs_team'] = df['market_value'] / (team_avg + 1)

    country_freq = df['country_'].value_counts(normalize=True)
    df['country_frequency'] = df['country_'].map(country_freq).fillna(0)

    team_freq = df['team'].value_counts(normalize=True)
    df['team_frequency'] = df['team'].map(team_freq).fillna(0)

    df['age_group'] = pd.cut(df['age'], bins=[0, 21, 25, 29, 33, 50], labels=[0, 1, 2, 3, 4])
    df['age_group_encoded'] = df['age_group'].astype(int)

    df['market_tier'] = pd.cut(df['market_value'], bins=[0, 1e6, 5e6, 15e6, 30e6, np.inf], labels=[0, 1, 2, 3, 4])
    df['market_tier_encoded'] = df['market_tier'].astype(int)

    df = df.replace([np.inf, -np.inf], 0)
    df = df.fillna(0)

    return df

def get_feature_columns():
    return [
        'market_value_missing', 'market_value_log', 'value_age_decay',
        'captain_x_market', 'position_x_age', 'player_convocations',
        'player_avg_minutes', 'player_last_3_avg', 'player_consistency',
        'performance_trend', 'momentum', 'team_avg_market_value',
        'player_value_vs_team', 'pos_D', 'pos_F', 'pos_G', 'pos_M',
        'country_frequency', 'team_frequency', 'age_group_encoded',
        'market_tier_encoded'
    ]

def select_best_11_by_formation(df, model, scaler, team):
    team_df = df[df['team'] == team].copy()

    if len(team_df) == 0:
        return None, None

    team_df = create_features(team_df)
    feature_cols = get_feature_columns()
    X = team_df[feature_cols]
    X_scaled = scaler.transform(X)

    probabilities = model.predict_proba(X_scaled)[:, 1]
    team_df['probability'] = probabilities

    formation = {'G': 1, 'D': 4, 'M': 3, 'F': 3}
    lineup = {}
    starters_ids = []

    for position, num_players in formation.items():
        position_players = team_df[team_df['position'] == position].copy()

        if len(position_players) == 0:
            lineup[position] = []
            continue

        position_players = position_players.sort_values('probability', ascending=False)
        best_players = position_players.head(num_players)
        best_players['rank'] = range(1, len(best_players) + 1)

        starters_ids.extend(best_players['id_player'].tolist())

        lineup[position] = best_players[[
            'id_player', 'position', 'player_name', 'shirt_number',
            'probability', 'captain'
        ]].to_dict('records')

    bench_df = team_df[~team_df['id_player'].isin(starters_ids)].copy()
    bench_df = bench_df.sort_values('probability', ascending=False)
    bench_df['bench_rank'] = range(1, len(bench_df) + 1)

    bench_players = bench_df[[
        'id_player', 'player_name', 'shirt_number', 'position', 
        'probability', 'bench_rank'
    ]].to_dict('records')

    return lineup, bench_players

def normalize_team_name(name):
    """Normaliza los nombres de equipos para coincidir entre datasets"""
    name_mapping = {
        'Arsenal FC': 'Arsenal',
        'Aston Villa FC': 'Aston Villa',
        'AFC Bournemouth': 'Bournemouth',
        'Brentford FC': 'Brentford',
        'Brighton & Hove Albion FC': 'Brighton',
        'Burnley FC': 'Burnley',
        'Chelsea FC': 'Chelsea',
        'Crystal Palace FC': 'Crystal Palace',
        'Everton FC': 'Everton',
        'Fulham FC': 'Fulham',
        'Leeds United FC': 'Leeds United',
        'Liverpool FC': 'Liverpool',
        'Manchester City FC': 'Manchester City',
        'Manchester United FC': 'Manchester Utd',
        'Newcastle United FC': 'Newcastle United',
        'Nottingham Forest FC': 'Nottingham Forest',
        'Sunderland AFC': 'Sunderland',
        'Tottenham Hotspur FC': 'Tottenham Hotspur',
        'West Ham United FC': 'West Ham United',
        'Wolverhampton Wanderers FC': 'Wolves'
    }
    return name_mapping.get(name, name)

def get_next_match(df_matches, team_name):
    """Obtiene el próximo partido del equipo"""
    if df_matches is None or len(df_matches) == 0:
        return None

    team_variations = [team_name]
    if team_name == 'Arsenal':
        team_variations.append('Arsenal FC')
    elif team_name == 'Manchester Utd':
        team_variations.append('Manchester United FC')
    elif team_name == 'Wolves':
        team_variations.append('Wolverhampton Wanderers FC')

    team_matches = df_matches[
        (df_matches['home_team_name'].isin(team_variations)) | 
        (df_matches['away_team_name'].isin(team_variations))
    ].copy()

    if len(team_matches) == 0:
        return None

    team_matches['utcDate'] = pd.to_datetime(team_matches['utcDate'])

    scheduled = team_matches[team_matches['status'].isin(['TIMED', 'POSTPONED'])].copy()

    if len(scheduled) == 0:
        return None

    scheduled = scheduled.sort_values('utcDate')
    next_match = scheduled.iloc[0]

    is_home = next_match['home_team_name'] in team_variations
    opponent = next_match['away_team_name'] if is_home else next_match['home_team_name']
    opponent = normalize_team_name(opponent)

    location = 'Local' if is_home else 'Visitante'
    date_str = next_match['utcDate'].strftime('%d/%m/%Y')

    return {
        'opponent': opponent,
        'location': location,
        'date': date_str,
        'is_home': is_home
    }

def display_formation_433(lineup, bench_players):
    total_players = sum(len(lineup.get(pos, [])) for pos in ['G', 'D', 'M', 'F'])

    if total_players == 0:
        st.warning("⚠️ No hay jugadores suficientes")
        return

    field_html = '<div class="football-field">'
    field_html += '<div class="center-line"></div>'
    field_html += '<div class="center-circle"></div>'

    # DELANTEROS
    field_html += '<div class="line-label">⚡ DELANTEROS</div>'
    forwards = lineup.get('F', [])
    if forwards:
        field_html += '<div class="lineup-row">'
        for player in forwards:
            name = player.get('player_name', f"Jugador {player['id_player']}")
            number = player.get('shirt_number', '?')
            field_html += f'<div class="player-card"><div class="player-number">{number}</div><div class="player-name">{name}</div><div class="player-position-badge">DEL</div></div>'
        field_html += '</div>'

    # MEDIOCAMPISTAS
    field_html += '<div class="line-label">⚙️ MEDIOCAMPISTAS</div>'
    midfielders = lineup.get('M', [])
    if midfielders:
        field_html += '<div class="lineup-row">'
        for player in midfielders:
            name = player.get('player_name', f"Jugador {player['id_player']}")
            number = player.get('shirt_number', '?')
            captain = ' (C)' if player.get('captain', 0) == 1 else ''
            field_html += f'<div class="player-card"><div class="player-number">{number}</div><div class="player-name">{name}{captain}</div><div class="player-position-badge">MED</div></div>'
        field_html += '</div>'

    # DEFENSAS
    field_html += '<div class="line-label">🛡️ DEFENSAS</div>'
    defenders = lineup.get('D', [])
    if defenders:
        field_html += '<div class="lineup-row">'
        for player in defenders:
            name = player.get('player_name', f"Jugador {player['id_player']}")
            number = player.get('shirt_number', '?')
            field_html += f'<div class="player-card"><div class="player-number">{number}</div><div class="player-name">{name}</div><div class="player-position-badge">DEF</div></div>'
        field_html += '</div>'

    # PORTERO
    field_html += '<div class="line-label">🧤 PORTERO</div>'
    goalkeeper = lineup.get('G', [])
    if goalkeeper:
        gk = goalkeeper[0]
        name = gk.get('player_name', f"Jugador {gk['id_player']}")
        number = gk.get('shirt_number', '?')
        field_html += '<div class="lineup-row goalkeeper">'
        field_html += f'<div class="player-card"><div class="player-number">{number}</div><div class="player-name">{name}</div><div class="player-position-badge">POR</div></div>'
        field_html += '</div>'

    field_html += '</div>'
    st.markdown(field_html, unsafe_allow_html=True)

    # BANCA
    if bench_players and len(bench_players) > 0:
        bench_html = '<div class="bench-section">'
        bench_html += '<div class="bench-title">JUGADORES EN BANCA</div>'

        for player in bench_players:
            number = player.get('shirt_number', '?')
            name = player.get('player_name', f"Jugador {player['id_player']}")
            position = player.get('position', '?')
            rank = player.get('bench_rank', 0)

            css_class = 'bench-player bench-player-top5' if rank <= 5 else 'bench-player'

            pos_labels = {'G': 'POR', 'D': 'DEF', 'M': 'MED', 'F': 'DEL'}
            pos_label = pos_labels.get(position, position)

            bench_html += f'<div class="{css_class}"><div class="bench-number">{number}</div><div class="bench-name">{name}</div><div class="bench-position">{pos_label}</div><div class="bench-rank">#{rank}</div></div>'

        bench_html += '</div>'
        st.markdown(bench_html, unsafe_allow_html=True)

def display_team_matches(df_matches, team_name):
    """Muestra los partidos de un equipo específico"""

    team_variations = [team_name]
    if team_name == 'Arsenal':
        team_variations.append('Arsenal FC')
    elif team_name == 'Manchester Utd':
        team_variations.append('Manchester United FC')
    elif team_name == 'Wolves':
        team_variations.append('Wolverhampton Wanderers FC')

    team_matches = df_matches[
        df_matches['home_team_name'].isin(team_variations) | 
        df_matches['away_team_name'].isin(team_variations)
    ].copy()

    if len(team_matches) == 0:
        st.warning(f"⚠️ No se encontraron partidos para {team_name}")
        return

    team_matches['utcDate'] = pd.to_datetime(team_matches['utcDate'])
    team_matches = team_matches.sort_values('utcDate')

    finished = team_matches[team_matches['status'] == 'FINISHED'].copy()
    scheduled = team_matches[team_matches['status'].isin(['TIMED', 'POSTPONED'])].copy()

    wins = 0
    draws = 0
    losses = 0
    goals_for = 0
    goals_against = 0

    for _, match in finished.iterrows():
        is_home = match['home_team_name'] in team_variations
        team_score = match['score_home'] if is_home else match['score_away']
        opp_score = match['score_away'] if is_home else match['score_home']

        goals_for += team_score
        goals_against += opp_score

        if team_score > opp_score:
            wins += 1
        elif team_score == opp_score:
            draws += 1
        else:
            losses += 1

    col1, col2, col3, col4, col5, col6 = st.columns(6)

    with col1:
        st.markdown(f'<div class="stat-card"><div class="stat-number">{len(finished)}</div><div class="stat-label">Jugados</div></div>', unsafe_allow_html=True)

    with col2:
        st.markdown(f'<div class="stat-card" style="background: linear-gradient(135deg, #28a745 0%, #20c997 100%);"><div class="stat-number">{wins}</div><div class="stat-label">Ganados</div></div>', unsafe_allow_html=True)

    with col3:
        st.markdown(f'<div class="stat-card" style="background: linear-gradient(135deg, #ffc107 0%, #ffb300 100%);"><div class="stat-number">{draws}</div><div class="stat-label">Empates</div></div>', unsafe_allow_html=True)

    with col4:
        st.markdown(f'<div class="stat-card" style="background: linear-gradient(135deg, #dc3545 0%, #c82333 100%);"><div class="stat-number">{losses}</div><div class="stat-label">Perdidos</div></div>', unsafe_allow_html=True)

    with col5:
        st.markdown(f'<div class="stat-card" style="background: linear-gradient(135deg, #17a2b8 0%, #138496 100%);"><div class="stat-number">{int(goals_for)}</div><div class="stat-label">GF</div></div>', unsafe_allow_html=True)

    with col6:
        st.markdown(f'<div class="stat-card" style="background: linear-gradient(135deg, #6c757d 0%, #5a6268 100%);"><div class="stat-number">{int(goals_against)}</div><div class="stat-label">GC</div></div>', unsafe_allow_html=True)

    st.markdown("---")

    col_past, col_next = st.columns(2)

    with col_past:
        st.markdown("### 📊 Últimos Partidos")

        last_matches = finished.tail(10).iloc[::-1]

        for _, match in last_matches.iterrows():
            is_home = match['home_team_name'] in team_variations
            team_score = int(match['score_home']) if is_home else int(match['score_away'])
            opp_score = int(match['score_away']) if is_home else int(match['score_home'])
            opponent = match['away_team_name'] if is_home else match['home_team_name']
            opponent = normalize_team_name(opponent)

            date_str = match['utcDate'].strftime('%d/%m/%Y')
            location = 'Local' if is_home else 'Visitante'

            if team_score > opp_score:
                match_class = 'match-finished'
                status_class = 'status-finished'
                status_text = 'VICTORIA'
            elif team_score == opp_score:
                match_class = 'match-finished'
                status_class = 'status-scheduled'
                status_text = 'EMPATE'
            else:
                match_class = 'match-finished'
                status_class = 'status-postponed'
                status_text = 'DERROTA'

            match_html = f'''
            <div class="match-card {match_class}">
                <div class="match-header">
                    <div class="match-date">📅 {date_str} • {location}</div>
                    <div class="match-status {status_class}">{status_text}</div>
                </div>
                <div class="match-teams">
                    <div class="team-home">{team_name if is_home else opponent}</div>
                    <div class="match-score">{team_score} - {opp_score}</div>
                    <div class="team-away">{opponent if is_home else team_name}</div>
                </div>
            </div>
            '''
            st.markdown(match_html, unsafe_allow_html=True)

    with col_next:
        st.markdown("### 📅 Próximos Partidos")

        next_matches = scheduled.head(10)

        if len(next_matches) == 0:
            st.info("✅ No hay más partidos programados")
        else:
            for _, match in next_matches.iterrows():
                is_home = match['home_team_name'] in team_variations
                opponent = match['away_team_name'] if is_home else match['home_team_name']
                opponent = normalize_team_name(opponent)

                date_str = match['utcDate'].strftime('%d/%m/%Y')
                location = 'Local' if is_home else 'Visitante'

                status = match['status']
                if status == 'POSTPONED':
                    match_class = 'match-postponed'
                    status_class = 'status-postponed'
                    status_text = 'POSPUESTO'
                else:
                    match_class = 'match-scheduled'
                    status_class = 'status-scheduled'
                    status_text = 'PROGRAMADO'

                match_html = f'''
                <div class="match-card {match_class}">
                    <div class="match-header">
                        <div class="match-date">📅 {date_str} • {location}</div>
                        <div class="match-status {status_class}">{status_text}</div>
                    </div>
                    <div class="match-teams">
                        <div class="team-home">{team_name if is_home else opponent}</div>
                        <div class="match-vs">vs</div>
                        <div class="team-away">{opponent if is_home else team_name}</div>
                    </div>
                </div>
                '''
                st.markdown(match_html, unsafe_allow_html=True)

@st.cache_data
def load_data():
    historico_path = Path("data/historico.csv")
    convocatoria_path = Path("data/convocatoria_siguiente.csv")
    jugadores_path = Path("data/jugadores_info.csv")

    if not historico_path.exists():
        st.error(f"❌ No se encontró: {historico_path}")
        st.stop()

    if not convocatoria_path.exists():
        st.error(f"❌ No se encontró: {convocatoria_path}")
        st.stop()

    df_historico = pd.read_csv(historico_path)
    df_features_temporales = calculate_temporal_features_from_history(df_historico)
    df_convocatoria = pd.read_csv(convocatoria_path)

    df_final = df_convocatoria.merge(
        df_features_temporales[['id_player', 'player_avg_minutes', 'player_last_3_avg',
                                 'player_consistency', 'performance_trend', 'momentum']],
        on='id_player',
        how='left'
    )

    if jugadores_path.exists():
        df_jugadores = pd.read_csv(jugadores_path)
        df_final = df_final.merge(
            df_jugadores[['id_player', 'player_name', 'shirt_number']],
            on='id_player',
            how='left'
        )
        df_final['player_name'] = df_final['player_name'].fillna(
            df_final['id_player'].astype(str).apply(lambda x: f"Jugador {x}")
        )
        df_final['shirt_number'] = df_final['shirt_number'].fillna(0).astype(int)
    else:
        st.warning("⚠️ No se encontró data/jugadores_info.csv")
        df_final['player_name'] = df_final['id_player'].astype(str).apply(lambda x: f"Jugador {x}")
        df_final['shirt_number'] = 0

    df_final['player_avg_minutes'].fillna(45.0, inplace=True)
    df_final['player_last_3_avg'].fillna(45.0, inplace=True)
    df_final['player_consistency'].fillna(15.0, inplace=True)
    df_final['performance_trend'].fillna(0.0, inplace=True)
    df_final['momentum'].fillna(0.0, inplace=True)

    df_final['captain'] = df_final['captain'].apply(lambda x: 1 if x in [True, 1, '1'] else 0)

    return df_final

@st.cache_data
def load_plantilla():
    plantilla_path = Path("data/plantilla.csv")

    if not plantilla_path.exists():
        st.error(f"❌ No se encontró: {plantilla_path}")
        return None

    df_plantilla = pd.read_csv(plantilla_path)
    df_plantilla['minutes_played'] = df_plantilla['minutes_played'].astype(str).str.replace(',', '').astype(int)

    return df_plantilla

@st.cache_data
def load_matches():
    matches_path = Path("data/premier_matches.csv")

    if not matches_path.exists():
        st.error(f"❌ No se encontró: {matches_path}")
        return None

    df_matches = pd.read_csv(matches_path)
    return df_matches

@st.cache_resource
def load_model_and_scaler():
    model = joblib.load(Path("models/xgboost_model.pkl"))
    scaler = joblib.load(Path("models/scaler.pkl"))
    return model, scaler

def main():
    load_custom_css()

    # Logo principal de la app
    display_app_header()

    df = load_data()
    df_plantilla = load_plantilla()
    df_matches = load_matches()
    model, scaler = load_model_and_scaler()

    matches_count = len(df_matches) if df_matches is not None else 0

    with st.sidebar:
        st.header("Configuración")
        teams = sorted(df['team'].unique())
        selected_team = st.selectbox("Equipo:", teams, index=0)

        st.markdown("---")
        st.markdown("### Descripción:")
        st.markdown("""
        MatchLineup AI es una aplicación web interactiva que predice las alineaciones de los equipos de la Premier League utilizando machine learning y algoritmos de IA.
        """)

    tab1, tab2, tab3 = st.tabs(["⚽ Alineación", "👥 Plantilla", "📅 Partidos"])

    with tab1:
        # Header con escudo CENTRADO
        next_match = get_next_match(df_matches, selected_team)
        display_team_header(selected_team, next_match, show_formation=True)

        # Título de sección DESPUÉS del header
        st.markdown("### 🎯 Alineación y Banca")

        lineup, bench_players = select_best_11_by_formation(df, model, scaler, selected_team)

        if lineup:
            display_formation_433(lineup, bench_players)
        else:
            st.warning("⚠️ No hay jugadores")

    with tab2:
        if df_plantilla is not None:
            # Header con escudo CENTRADO
            next_match = get_next_match(df_matches, selected_team)
            display_team_header(selected_team, next_match, show_formation=False)

            st.markdown("### 👥 Plantilla Completa")

            team_plantilla = df_plantilla[df_plantilla['team'] == selected_team].copy()

            if len(team_plantilla) == 0:
                st.warning(f"⚠️ No se encontró información de plantilla para {selected_team}")
            else:
                col1, col2, col3, col4 = st.columns(4)

                with col1:
                    st.markdown(f'<div class="stat-card"><div class="stat-number">{len(team_plantilla)}</div><div class="stat-label">Jugadores</div></div>', unsafe_allow_html=True)

                with col2:
                    avg_age = team_plantilla['age'].mean()
                    st.markdown(f'<div class="stat-card"><div class="stat-number">{avg_age:.1f}</div><div class="stat-label">Edad Promedio</div></div>', unsafe_allow_html=True)

                with col3:
                    total_goals = team_plantilla['goals'].sum()
                    st.markdown(f'<div class="stat-card"><div class="stat-number">{total_goals}</div><div class="stat-label">Goles Totales</div></div>', unsafe_allow_html=True)

                with col4:
                    total_assists = team_plantilla['assits'].sum()
                    st.markdown(f'<div class="stat-card"><div class="stat-number">{total_assists}</div><div class="stat-label">Asistencias</div></div>', unsafe_allow_html=True)

                st.markdown("---")

                st.markdown("#### 📋 Todos los Jugadores")

                display_df = team_plantilla.copy()
                display_df = display_df.sort_values('minutes_played', ascending=False)

                pos_map = {'GK': '🧤 POR', 'DF': '🛡️ DEF', 'MF': '⚙️ MED', 'FW': '⚡ DEL'}
                display_df['position_label'] = display_df['position'].map(pos_map)

                display_df['goals_per_match'] = (display_df['goals'] / display_df['matchs']).fillna(0)
                display_df['assists_per_match'] = (display_df['assits'] / display_df['matchs']).fillna(0)
                display_df['minutes_per_match'] = (display_df['minutes_played'] / display_df['matchs']).fillna(0)

                final_df = display_df[[
                    'player_name', 'position_label', 'age', 'matchs', 
                    'minutes_played', 'minutes_per_match', 'goals', 'goals_per_match',
                    'assits', 'assists_per_match'
                ]].copy()

                final_df.columns = [
                    'Jugador', 'Pos', 'Edad', 'PJ', 
                    'Min', 'Min/PJ', 'Goles', 'G/PJ',
                    'Asist', 'A/PJ'
                ]

                final_df['Min/PJ'] = final_df['Min/PJ'].apply(lambda x: f"{x:.0f}")
                final_df['G/PJ'] = final_df['G/PJ'].apply(lambda x: f"{x:.2f}")
                final_df['A/PJ'] = final_df['A/PJ'].apply(lambda x: f"{x:.2f}")

                st.dataframe(final_df, use_container_width=True, hide_index=True, height=500)

                st.markdown("---")

                col1, col2, col3 = st.columns(3)

                with col1:
                    st.markdown("#### ⚽ Top Goleadores")
                    top_scorers = team_plantilla.nlargest(5, 'goals')[['player_name', 'goals', 'matchs']]
                    top_scorers['goals_per_match'] = (top_scorers['goals'] / top_scorers['matchs']).apply(lambda x: f"{x:.2f}")
                    top_scorers = top_scorers[['player_name', 'goals', 'goals_per_match']]
                    top_scorers.columns = ['Jugador', 'Goles', 'G/PJ']
                    st.dataframe(top_scorers, hide_index=True, use_container_width=True)

                with col2:
                    st.markdown("#### 🎯 Top Asistencias")
                    top_assists = team_plantilla.nlargest(5, 'assits')[['player_name', 'assits', 'matchs']]
                    top_assists['assists_per_match'] = (top_assists['assits'] / top_assists['matchs']).apply(lambda x: f"{x:.2f}")
                    top_assists = top_assists[['player_name', 'assits', 'assists_per_match']]
                    top_assists.columns = ['Jugador', 'Asist', 'A/PJ']
                    st.dataframe(top_assists, hide_index=True, use_container_width=True)

                with col3:
                    st.markdown("#### ⏱️ Top Minutos")
                    top_minutes = team_plantilla.nlargest(5, 'minutes_played')[['player_name', 'minutes_played', 'matchs']]
                    top_minutes['minutes_per_match'] = (top_minutes['minutes_played'] / top_minutes['matchs']).apply(lambda x: f"{x:.0f}")
                    top_minutes = top_minutes[['player_name', 'minutes_played', 'minutes_per_match']]
                    top_minutes.columns = ['Jugador', 'Minutos', 'Min/PJ']
                    st.dataframe(top_minutes, hide_index=True, use_container_width=True)
        else:
            st.error("❌ No se pudo cargar el archivo de plantilla")

    with tab3:
        if df_matches is not None:
            # Header con escudo CENTRADO
            next_match = get_next_match(df_matches, selected_team)
            display_team_header(selected_team, next_match, show_formation=False)

            st.markdown("### 📅 Calendario de Partidos")

            display_team_matches(df_matches, selected_team)
        else:
            st.error("❌ No se pudo cargar el archivo de partidos")

    st.markdown("---")

if __name__ == "__main__":
    main()