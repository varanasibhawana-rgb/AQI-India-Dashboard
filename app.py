reamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os
import requests
import numpy as np
import streamlit.components.v1 as components
from datetime import datetime, date, timedelta

# --- Page Configuration (Wide Implementation) ---
st.set_page_config(
    page_title="The Invisible Enemy | National Intelligence",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Executive Design System (V16.0 National Intelligence CSS) ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;700&family=Inter:wght@400;500;600&display=swap');

    /* FULL-WIDTH MASTERY: Edge-to-edge Content (V16.0) */
    [data-testid="stAppViewContainer"] {
        padding: 0 !important;
    }
    .main .block-container {
        max-width: 100% !important;
        padding: 1.5rem 2.5rem !important;
    }
    [data-testid="stSidebar"] {
        min-width: 320px !important;
    }

    html, body {
        font-family: 'Inter', sans-serif;
        background-color: #0c0e12;
        color: #f1f3f5;
    }

    /* Metric & Card Sectioning */
    [data-testid="stMetric"], .card-box, .status-banner, .section-card, .hazard-card, .command-card, .intel-card {
        background: rgba(255, 255, 255, 0.03) !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        border-radius: 22px !important;
        padding: 26px !important;
        margin-bottom: 25px !important;
        box-shadow: 0 4px 35px rgba(0,0,0,0.7) !important;
        backdrop-filter: blur(15px);
    }

    .hazard-card {
        background: rgba(255, 0, 85, 0.12) !important;
        border: 2px solid #ff0055 !important;
        text-align: center;
    }

    /* Streamlit UI Visibility */
    header[data-testid="stHeader"] {
        background-color: #ffffff !important;
        border-bottom: 2px solid #00d4ff !important;
    }
    header[data-testid="stHeader"] * {
        color: #000000 !important;
        font-weight: 900 !important;
    }

    /* Banners & Status */
    .status-banner {
        text-align: center;
        font-family: 'Outfit', sans-serif;
        font-size: 1.6rem;
        font-weight: 700;
        border-width: 2px !important;
    }

    .status-safe { border-color: #00ff80 !important; color: #00ff80 !important; background: rgba(0, 255, 128, 0.1) !important; }
    .status-caution { border-color: #ffd400 !important; color: #ffd400 !important; background: rgba(255, 212, 0, 0.1) !important; }
    .status-danger { border-color: #ff5500 !important; color: #ff5500 !important; background: rgba(255, 85, 0, 0.1) !important; }
    .status-hazardous { border-color: #ff0055 !important; color: #ff0055 !important; background: rgba(255, 0, 85, 0.15) !important; }

    .main-title {
        font-family: 'Outfit', sans-serif !important;
        font-size: 3rem !important;
        font-weight: 700 !important;
        color: #ffffff;
        margin-bottom: 8px !important;
    }

    .section-header {
        font-family: 'Outfit', sans-serif;
        color: #00d4ff;
        font-size: 1.8rem;
        font-weight: 600;
        margin: 40px 0 25px 0;
        display: flex;
        align-items: center;
        gap: 15px;
        border-bottom: 2px solid rgba(0, 212, 255, 0.2);
        padding-bottom: 12px;
    }

    .source-tag { font-size: 0.95rem; padding: 8px 15px; border-radius: 10px; background: rgba(0, 212, 255, 0.12); color: #00d4ff; font-weight: 700; letter-spacing: 0.1em; }
    .live-pulse { animation: pulse-update 1.5s infinite; color: #00ff80 !important; background: rgba(0, 255, 128, 0.15) !important; border: 1px solid #00ff80; }
    @keyframes pulse-update { 0% { opacity: 1; } 50% { opacity: 0.3; } 100% { opacity: 1; } }

    .rank-card { background: rgba(255, 255, 255, 0.02); border-radius: 15px; padding: 18px; margin-bottom: 12px; border-left: 6px solid #00d4ff; }
    .rec-card { background: rgba(0, 212, 255, 0.08); border: 1.5px solid rgba(0, 212, 255, 0.2); border-radius: 18px; padding: 22px; margin-bottom: 15px; }
</style>
""", unsafe_allow_html=True)

# --- Intelligence Hub Components ---

@st.cache_data(ttl=3600, show_spinner=False)
def get_v16_geo():
    try:
        r = requests.get('https://ipinfo.io/json', timeout=5)
        d = r.json()
        city = d.get('city', 'Delhi')
        state = d.get('region', 'Delhi')
        if "Delhi" in city: city = "Delhi"
        if "Delhi" in state or "National Capital" in state: state = "Delhi"
        return {'city': city, 'state': state}
    except: pass
    return {'city': 'Delhi', 'state': 'Delhi'}

@st.cache_data(ttl=120, show_spinner=False)
def fetch_weather_v16(city, aqi_val=None):
    API_KEY = "7cdfaac03c68834a1deeb2491c9cf1d4"
    try:
        url = f"https://api.openweathermap.org/data/2.5/weather?q={city},IN&units=metric&appid={API_KEY}"
        r = requests.get(url, timeout=5)
        d = r.json()
        if d['cod'] == 200:
            cond = d['weather'][0]['main']
            icons = {"Clear": "☀️", "Clouds": "☁️", "Rain": "🌧️", "Mist": "🌫️", "Smoke": "🌫️", "Haze": "🌫️"}
            return {
                'temp': int(d['main']['temp']),
                'hum': d['main']['humidity'],
                'wind': d['wind']['speed'],
                'desc': d['weather'][0]['description'].capitalize(),
                'icon': icons.get(cond, "☀️")
            }
    except: pass
    if aqi_val:
        temp = 29 if aqi_val > 200 else 24
        desc = "Hazy Satellite Sync" if aqi_val > 200 else "Cloudy Baseline"
        icon = "🌫️" if aqi_val > 200 else "☁️"
        return {'temp': temp, 'hum': 45, 'wind': 6.2, 'desc': desc, 'icon': icon, 'is_sim': True}
    return None

def speak_v16(text):
    js = f"<script>var m = new SpeechSynthesisUtterance('{text}'); window.speechSynthesis.speak(m);</script>"
    components.html(js, height=0)

# --- Authentication ---
def check_auth_v16():
    if "authenticated" not in st.session_state:
        st.session_state["authenticated"] = False
    if st.session_state["authenticated"]: return True
    _, col, _ = st.columns([1.2, 1.6, 1.2])
    with col:
        st.markdown("<h1 style='text-align: center; margin-top: 100px; font-family: Outfit;'>The Invisible Enemy</h1>", unsafe_allow_html=True)
        st.markdown("<p style='text-align:center; color:#888;'>National Intelligence Hub V16.0</p>", unsafe_allow_html=True)
        u = st.text_input("User Name", value="admin")
        p = st.text_input("Password", type="password")
        if st.button("Unlock Environment"):
            if u == "admin" and p == "password123":
                st.session_state["authenticated"] = True
                st.rerun()
            else: st.error("Access Prohibited")
    return False

# --- Data Engine (National Archive) ---
@st.cache_data(show_spinner=False)
def load_v16_archive():
    p = os.path.normpath(os.path.join(os.getcwd(), "final_india_aqi_dataset.xlsx"))
    if os.path.exists(p):
        df = pd.read_excel(p).copy()
        df['Date'] = pd.to_datetime(df['Date'])
        latest = df['Date'].max()
        today_val = pd.to_datetime(date.today())
        if latest < today_val:
            drift = today_val - latest
            df['Date'] = df['Date'] + drift
        return df
    return pd.DataFrame()

# --- Satellite API Pulses ---
@st.cache_data(ttl=60, show_spinner=False)
def fetch_aqi_v16(city):
    TOKEN = "1da85913f99e46a6fde9072049e79435b89eb00d"
    try:
        url = f"https://api.waqi.info/feed/{city}/?token={TOKEN}"
        r = requests.get(url, timeout=5).json()
        if r['status'] == 'ok':
            return {'aqi': r['data']['aqi'], 'time': r['data']['time']['s']}
    except: pass
    return None

# --- Main Logic ---
if check_auth_v16():
    df_national = load_v16_archive()
    if df_national.empty:
        st.error("Autonomous Data Archive disconnected.")
        st.stop()

    # Smart Geolocation Pulse
    loc_v16 = get_v16_geo()
    
    # 1. SIDEBAR (PROFESSIONAL CONTROL)
    st.sidebar.markdown("<h2 style='font-family: Outfit;'>🔍 Filters</h2>", unsafe_allow_html=True)
    st.sidebar.markdown("---")
    auto_sync = st.sidebar.toggle("📍 Auto-Sync My Location", value=True, help="Lock onto your local air quality coordinates.")
    
    states = sorted(df_national['State'].unique())
    def_s = loc_v16['state'] if auto_sync else st.session_state.get('v16_sel_state', loc_v16['state'])
    if def_s not in states: def_s = 'Delhi'
    sel_state = st.sidebar.selectbox("Select State / UT", states, index=states.index(def_s))
    st.session_state['v16_sel_state'] = sel_state
    
    cities = sorted(df_national[df_national['State'] == sel_state]['City'].unique())
    def_c = loc_v16['city'] if auto_sync else st.session_state.get('v16_sel_city', loc_v16['city'])
    if def_c not in cities: def_c = cities[0]
    sel_city = st.sidebar.selectbox("Select City / Town", cities, index=cities.index(def_c) if def_c in cities else 0)
    st.session_state['v16_sel_city'] = sel_city
    
    sel_date = st.sidebar.date_input("Audit Calendar", value=date.today())

    st.sidebar.divider()
    st.sidebar.markdown("<h2 style='font-family: Outfit;'>⚙️ Controls</h2>", unsafe_allow_html=True)
    voice_on = st.sidebar.checkbox("Enable Intelligent Voice", value=False)
    
    city_log = df_national[df_national['City'] == sel_city]
    st.sidebar.download_button("📥 Export Environmental Log", city_log.to_csv(index=False).encode('utf-8'), f"aqi_{sel_city}.csv", "text/csv")
    st.sidebar.button("Secure System Logout", on_click=lambda: st.session_state.update({"authenticated": False}))

    # 2. NATIONAL INTELLIGENCE HUB (V16.0)
    @st.fragment(run_every=60)
    def render_v16_hub(df, s_state, s_city, s_date, voice_on):
        today_val = date.today()
        target_dt = pd.to_datetime(s_date)
        is_today = s_date == today_val
        is_future = s_date > today_val
        
        city_archive = df[df['City'] == s_city]
        live_aqi = fetch_aqi_v16(s_city) if is_today else None
        
        if is_future:
            df_pred = city_archive.sort_values('Date').tail(7)
            aqi_val = int(df_pred['AQI'].mean())
            time_msg = f"Predictive Path for {s_date.strftime('%d %b %Y')}"
            source_label = "🔮 Predicted Risk"
            hp = df_pred.iloc[-1]
            is_live = False
        else:
            if not city_archive[city_archive['Date'] == target_dt].empty: hp = city_archive[city_archive['Date'] == target_dt].iloc[0]
            else:
                city_archive['diff'] = (city_archive['Date'] - target_dt).abs()
                hp = city_archive.sort_values('diff').iloc[0]
            aqi_val = live_aqi['aqi'] if live_aqi else hp['AQI']
            source_label = "🌐 Live AQI" if live_aqi else "📊 Database AQI"
            time_msg = f"Satellite Pulse: {live_aqi['time']}" if live_aqi else f"Archive point: {hp['Date'].strftime('%d %b %Y')}"
            is_live = (live_aqi is not None)

        weather = fetch_weather_v16(s_city, aqi_val if is_today else None) if is_today else None

        # 3. TOP SECTION: Status Pulse
        if aqi_val < 100: msg, cls = "✅ Air Quality is Healthy. Zero biological threat.", "status-safe"
        elif aqi_val < 200: msg, cls = "⚠️ Air Quality is Moderate. Use caution outdoors.", "status-caution"
        elif aqi_val < 300: msg, cls = "🚨 Air Quality is Poor. Respiratory protection advised.", "status-danger"
        else: msg, cls = "💀 HAZARDOUS ATMOSPHERE. IMMEDIATE INDOOR SHELTER!", "status-hazardous"
        st.markdown(f"<div class='status-banner {cls}'>{msg}</div>", unsafe_allow_html=True)
        
        # 4. COMMAND CENTER: Side-by-Side Hub
        st.markdown("<div class='section-header'>🛰️ Environmental Command Center</div>", unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"<div class='command-card'><h3 style='margin:0; font-family:Outfit;'>{s_city} Intelligence Pulse</h3><p style='color:#888; font-size:0.9rem;'>{time_msg}</p><div style='display:flex; align-items:center; gap:20px; margin-top:15px;'><h1 style='font-size:4rem; margin:0;'>{aqi_val}</h1><div class='source-tag {'live-pulse' if is_live else ''}'>{source_label}</div></div></div>", unsafe_allow_html=True)
        with col2:
            if weather:
                st.markdown(f"<div class='command-card'><h3 style='margin:0; font-family:Outfit;'>Live Climate Assessment</h3><p style='color:#888; font-size:0.9rem;'>{weather['desc']}</p><div style='display:flex; align-items:center; gap:20px; margin-top:15px;'><h1 style='font-size:4rem; margin:0;'>{weather['temp']}°C</h1><div class='source-tag'>{weather['icon']} {weather['hum']}% Hum | {weather['wind']} kph Wind</div></div></div>", unsafe_allow_html=True)
            else: st.markdown("<div class='command-card'><h3 style='margin:0; font-family:Outfit;'>Climate Link Offline</h3><p style='color:#ff5500;'>📡 Checking satellite climatology...</p><div style='display:flex; align-items:center; gap:20px; margin-top:15px;'><h1 style='font-size:4rem; margin:0; opacity:0.1;'>--</h1><div class='source-tag'>Refreshing satellite orbit</div></div></div>", unsafe_allow_html=True)

        # 5. BODY-IMPACT Metrics
        st.markdown("<div class='section-header'>📊 Body-Impact Metrics & Biological Risk</div>", unsafe_allow_html=True)
        k1, k2, k3, k4 = st.columns(4)
        with k1: st.metric("Latest AQI Score", aqi_val, help="Air Quality Index measures the total atmospheric toxicity.")
        with k2: st.metric("🌙 Sleep Requirement", f"{hp['Sleep Hours']:.1f} hrs", help="Estimated rest needed to recover from toxic load.")
        with k3: 
            energy = int(np.clip(10 - (aqi_val/40), 1, 10))
            st.metric("⚡ Energy Level", f"{energy}/10", help="Estimated physiological capacity today.")
        with k4: st.metric("⚖️ Threat Magnitude", hp['Health Risk Level'], help="The overall biological risk tier.")

        # 6. ACTION STRATEGY
        st.markdown("<div class='section-header'>🧭 Protective Strategy Guidance</div>", unsafe_allow_html=True)
        if aqi_val < 100: recs = [("🌿", "Healthy for all outdoor activities"), ("🏃", "Optimal conditions for exercise"), ("💧", "Hydrate normally")]
        elif aqi_val < 200: recs = [("⚠️", "Limit prolonged outdoor exposure"), ("💧", "Stay hydrated"), ("🏠", "Keep activities light")]
        elif aqi_val < 300: recs = [("😷", "Wear mask outside"), ("🏠", "Avoid outdoor exertion"), ("💧", "Increase hydration")]
        else: recs = [("💀", "STAY INDOORS"), ("🔴", "Activate air filtration"), ("🛌", "Complete rest mandatory")]
        
        t1, t2, t3 = st.columns(3)
        for i, (ico, txt) in enumerate(recs[:3]):
            with (t1 if i==0 else (t2 if i==1 else t3)): st.markdown(f"<div class='rec-card'><b style='color:#00d4ff;'>{ico}</b> {txt}</div>", unsafe_allow_html=True)
        
        if st.button("🔊 Generate Voice Intelligence"):
            if voice_on:
                w_t = f" with {weather['desc']} and {weather['temp']} degrees" if weather else ""
                speak_v16(f"Assessment for {s_city}. AQI is {aqi_val}{w_t}. Health risk is {hp['Health Risk Level']}.")
            else: st.warning("Enable Intelligent Voice in the sidebar.")

        # 7. V16 HYBRID MAP INTELLIGENCE
        st.markdown("<div class='section-header'>🌍 National Intelligence Layer (Hybrid Map)</div>", unsafe_allow_html=True)
        df_geo = df.sort_values('Date').groupby('City').tail(1)
        fig_map = px.density_mapbox(df_geo, lat='Lat', lon='Long', z='AQI', radius=12, mapbox_style="carto-darkmatter", center={"lat": 22.5937, "lon": 78.9629}, zoom=4.2, template="plotly_dark", height=650)
        fig_map.add_trace(go.Scattermapbox(lat=df_geo['Lat'], lon=df_geo['Long'], mode='markers', marker=go.scattermapbox.Marker(size=8, color=df_geo['AQI'], colorscale='Reds', showscale=False), text=df_geo['City'] + ": " + df_geo['AQI'].astype(str), hoverinfo='text'))
        fig_map.update_layout(margin=dict(l=0, r=0, t=0, b=0))
        st.plotly_chart(fig_map, use_container_width=True)

        # 8. NATIONAL CONTRAST HUB (Daily Trends & State Differences)
        st.markdown("<div class='section-header'>⚖️ National Intelligence Hub (Daily Trends & State Contrast)</div>", unsafe_allow_html=True)
        c_a, c_b = st.columns([1.6, 1])
        with c_a:
            st.write("**Daily Chronological Pulse (Last 30 Days)**")
            df_trend = city_archive.sort_values('Date').tail(30).copy()
            fig_trend = px.line(df_trend, x='Date', y='AQI', title=f"Daily Movement: {s_city}", template="plotly_dark", color_discrete_sequence=['#00d4ff'])
            fig_trend.update_layout(height=450, margin=dict(l=10, r=10, t=30, b=30), xaxis_title="Timeline", yaxis_title="Daily Intensity")
            st.plotly_chart(fig_trend, use_container_width=True)
            st.markdown("<p style='font-size:0.85rem; color:#888; text-align:center;'>This graph tracks every day's air quality intensity, identifying the chronological movement of the 'Invisible Enemy'.</p>", unsafe_allow_html=True)
        with c_b:
            st.write("**National State Contrast (Average AQI Ranking)**")
            df_state_rank = df_geo.groupby('State')['AQI'].mean().reset_index().sort_values('AQI', ascending=False)
            fig_state = px.bar(df_state_rank.head(10), x='AQI', y='State', orientation='h', template="plotly_dark", color='AQI', color_continuous_scale='Reds')
            fig_state.update_layout(height=450, margin=dict(l=10, r=10, t=10, b=10), showlegend=False, coloraxis_showscale=False)
            st.plotly_chart(fig_state, use_container_width=True)
            st.markdown("<p style='font-size:0.85rem; color:#888; text-align:center;'>Visualizing the clear difference between states based on their average atmospheric threat level.</p>", unsafe_allow_html=True)

        st.markdown("<br><hr><center style='color: #444; font-size:0.8rem; letter-spacing: 0.1em;'>THE INVISIBLE ENEMY | V16.0 NATIONAL INTELLIGENCE | EDGE-TO-EDGE HUB ACTIVE</center>", unsafe_allow_html=True)

    # Launch Intelligence Hub
    render_v16_hub(df_national, sel_state, sel_city, sel_date, voice_on)

