import streamlit as st
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
    page_title="The Invisible Enemy | National Command",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Executive Design System (V16.3 Geo-Lock CSS) ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;700&family=Inter:wght@400;500;600&display=swap');

    /* ABSOLUTE MASTER: Destroy all margins and forced gaps (V16.3) */
    [data-testid="stAppViewContainer"] {
        padding: 0 !important;
        margin: 0 !important;
    }
    [data-testid="stMainBlockContainer"] {
        max-width: 100% !important;
        padding: 2.5rem 4rem !important;
        margin: 0 !important;
        width: 100% !important;
    }
    .main .block-container {
        max-width: 100% !important;
        padding: 2rem 4rem !important;
        margin: 0 !important;
    }
    [data-testid="stSidebar"] {
        min-width: 320px !important;
        max-width: 320px !important;
    }
    div[data-testid="stVerticalBlock"] > div {
        width: 100% !important;
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

    /* Streamlit UI Visibility */
    header[data-testid="stHeader"] {
        background-color: #ffffff !important;
        border-bottom: 2px solid #00d4ff !important;
    }
    header[data-testid="stHeader"] * { color: #000000 !important; font-weight: 900 !important; }

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

    .rec-card { background: rgba(0, 212, 255, 0.08); border: 1.5px solid rgba(0, 212, 255, 0.2); border-radius: 18px; padding: 22px; margin-bottom: 15px; }
</style>
""", unsafe_allow_html=True)

# --- Intelligence Hub Components ---

@st.cache_data(ttl=120, show_spinner=False)
def fetch_weather_v16(city, aqi_val=None, is_today=True):
    API_KEY = "7cdfaac03c68834a1deeb2491c9cf1d4"
    if is_today:
        try:
            url = f"https://api.openweathermap.org/data/2.5/weather?q={city},IN&units=metric&appid={API_KEY}"
            r = requests.get(url, timeout=5).json()
            if r['cod'] == 200:
                cond = r['weather'][0]['main']
                ico_map = {"Clear": "☀️", "Clouds": "☁️", "Rain": "🌧️", "Mist": "🌫️", "Smoke": "🌫️", "Haze": "🌫️"}
                return {'temp': int(r['main']['temp']), 'hum': r['main']['humidity'], 'wind': r['wind']['speed'], 'desc': r['weather'][0]['description'].capitalize(), 'icon': ico_map.get(cond, "☀️"), 'type': "🌐 Satellite Live"}
        except: pass
    if aqi_val:
        temp = 29 if aqi_val > 150 else 24
        desc = "Hazy Baseline" if aqi_val > 150 else "Stable Atmosphere"
        icon = "🌫️" if aqi_val > 150 else "☀️"
        return {'temp': temp, 'hum': 45, 'wind': 5.5, 'desc': desc, 'icon': icon, 'type': "📊 Assessment"}
    return None

def get_nearest_city_v16(lat, lon, df):
    # Haversine Distance Matcher
    def haversine(lat1, lon1, lat2, lon2):
        lat1, lon1, lat2, lon2 = map(np.radians, [lat1, lon1, lat2, lon2])
        dlat, dlon = lat2-lat1, lon2-lon1
        a = np.sin(dlat/2)**2 + np.cos(lat1)*np.cos(lat2)*np.sin(dlon/2)**2
        return 6371 * 2 * np.arcsin(np.sqrt(a))
    
    unique_cities = df.groupby('City').first().reset_index()
    unique_cities['dist'] = unique_cities.apply(lambda r: haversine(lat, lon, r['Lat'], r['Long']), axis=1)
    match = unique_cities.sort_values('dist').iloc[0]
    return {'city': match['City'], 'state': match['State']}

@st.cache_data(ttl=60, show_spinner=False)
def fetch_aqi_v16(city):
    TOKEN = "1da85913f99e46a6fde9072049e79435b89eb00d"
    try:
        url = f"https://api.waqi.info/feed/{city}/?token={TOKEN}"
        r = requests.get(url, timeout=5).json()
        if r['status'] == 'ok': return {'aqi': r['data']['aqi'], 'time': r['data']['time']['s']}
    except: pass
    return None

# --- Authentication ---
def check_auth_v16():
    if st.session_state.get("auth", False): return True
    _, col, _ = st.columns([1.2, 1.6, 1.2])
    with col:
        st.markdown("<h1 style='text-align: center; margin-top: 100px; font-family: Outfit;'>The Invisible Enemy</h1><p style='text-align:center; color:#888;'>National Command Hub V16.3</p>", unsafe_allow_html=True)
        u, p = st.text_input("User Name", value="admin"), st.text_input("Password", type="password")
        if st.button("Unlock Environment") and u == "admin" and p == "password123":
            st.session_state["auth"] = True
            st.rerun()
    return False

# --- Main Logic ---
if check_auth_v16():
    p_path = os.path.normpath(os.path.join(os.getcwd(), "final_india_aqi_dataset.xlsx"))
    df_national = pd.read_excel(p_path)
    df_national['Date'] = pd.to_datetime(df_national['Date'])
    
    # 1. GEO-LOCK INTELLIGENCE (V16.3)
    q_params = st.query_params
    detected_loc = None
    if 'lat' in q_params and 'lon' in q_params:
        detected_loc = get_nearest_city_v16(float(q_params['lat']), float(q_params['lon']), df_national)

    st.sidebar.markdown("<h2 style='font-family: Outfit;'>🔍 Filters</h2>", unsafe_allow_html=True)
    st.sidebar.markdown("---")
    auto_sync = st.sidebar.toggle("📍 Satellite Geo-Lock", value=True)
    
    # Browser-Side Pulse (Inject JS if not locked)
    if auto_sync and not detected_loc:
        js_geo = """
        <script>
        navigator.geolocation.getCurrentPosition(function(position) {
            const url = new URL(window.location.href);
            url.searchParams.set('lat', position.coords.latitude);
            url.searchParams.set('lon', position.coords.longitude);
            window.location.href = url.href;
        });
        </script>
        """
        components.html(js_geo, height=0)
        st.info("🛰️ Scanning Satellite Environment... Please Allow Location Access.")

    states = sorted(df_national['State'].unique())
    def_s = detected_loc['state'] if detected_loc and auto_sync else st.session_state.get('v16_s', 'Delhi')
    if def_s not in states: def_s = states[0]
    sel_state = st.sidebar.selectbox("Select State", states, index=states.index(def_s))
    st.session_state['v16_s'] = sel_state
    
    cities = sorted(df_national[df_national['State'] == sel_state]['City'].unique())
    def_c = detected_loc['city'] if detected_loc and auto_sync else st.session_state.get('v16_c', 'Delhi')
    if def_c not in cities: def_c = cities[0]
    sel_city = st.sidebar.selectbox("Select City", cities, index=cities.index(def_c) if def_c in cities else 0)
    st.session_state['v16_c'] = sel_city
    
    sel_date = st.sidebar.date_input("Audit Calendar", value=date.today())

    st.sidebar.divider()
    st.sidebar.markdown("<h2 style='font-family: Outfit;'>⚙️ Controls</h2>", unsafe_allow_html=True)
    voice_on = st.sidebar.checkbox("Enable Intelligence Voice", value=False)
    st.sidebar.button("Secure System Logout", on_click=lambda: st.session_state.update({"auth": False}))

    # 2. HUB RENDERING
    @st.fragment(run_every=60)
    def render_v16_hub(df, s_city, s_date):
        today_val = date.today()
        target_dt = pd.to_datetime(s_date)
        is_today, is_future = s_date == today_val, s_date > today_val
        
        city_archive = df[df['City'] == s_city]
        live_aqi = fetch_aqi_v16(s_city) if is_today else None
        
        if is_future:
            df_pred = city_archive.sort_values('Date').tail(7)
            aqi_val, source_label = int(df_pred['AQI'].mean()), "🔮 Predicted Risk"
            hp, time_msg, is_live = df_pred.iloc[-1], f"Forecast: {s_date.strftime('%d %b')}", False
        else:
            if not city_archive[city_archive['Date'] == target_dt].empty: hp = city_archive[city_archive['Date'] == target_dt].iloc[0]
            else: 
                city_archive['d'] = (city_archive['Date'] - target_dt).abs()
                hp = city_archive.sort_values('d').iloc[0]
            aqi_val, source_label = live_aqi['aqi'] if live_aqi else hp['AQI'], "🌐 Live AQI" if live_aqi else "📊 Database AQI"
            time_msg = f"Last Update: {live_aqi['time']}" if live_aqi else f"Archive: {hp['Date'].strftime('%d %b')}"
            is_live = live_aqi is not None

        weather = fetch_weather_v16(s_city, aqi_val, is_today)

        # UI Construction
        if aqi_val < 100: msg, cls = "✅ Air Quality Healthy", "status-safe"
        elif aqi_val < 200: msg, cls = "⚠️ Air Quality Moderate", "status-caution"
        else: msg, cls = "🚨 HAZARDOUS ATMOSPHERE!", "status-hazardous"
        st.markdown(f"<div class='status-banner {cls}'>{msg}</div>", unsafe_allow_html=True)
        
        st.markdown("<div class='section-header'>🛰️ Environmental Command Center</div>", unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        with c1: st.markdown(f"<div class='command-card'><h3 style='margin:0;'>{s_city} Pulse</h3><p style='color:#888;'>{time_msg}</p><div style='display:flex; align-items:center; gap:20px; margin-top:15px;'><h1 style='font-size:4rem; margin:0;'>{aqi_val}</h1><div class='source-tag {'live-pulse' if is_live else ''}'>{source_label}</div></div></div>", unsafe_allow_html=True)
        with c2: st.markdown(f"<div class='command-card'><h3 style='margin:0;'>Atmospheric Mastery</h3><p style='color:#888;'>{weather['type']}</p><div style='display:flex; align-items:center; gap:20px; margin-top:15px;'><h1 style='font-size:4rem; margin:0;'>{weather['temp']}°C</h1><div class='source-tag'>{weather['icon']} {weather['desc']}</div></div></div>", unsafe_allow_html=True)

        st.markdown("<div class='section-header'>📊 Body-Impact Metrics</div>", unsafe_allow_html=True)
        k1, k2, k3, k4 = st.columns(4)
        k1.metric("AQI Score", aqi_val)
        k2.metric("🌙 Recovery Rest", f"{hp['Sleep Hours']:.1f} hrs")
        k3.metric("⚡ Energy Pulse", int(np.clip(10-(aqi_val/40), 1, 10)))
        k4.metric("⚖️ Threat Tier", hp['Health Risk Level'])

        st.markdown("<div class='section-header'>🌍 National Intelligence Layer</div>", unsafe_allow_html=True)
        df_geo = df.groupby('City').tail(1)
        fig_map = px.density_mapbox(df_geo, lat='Lat', lon='Long', z='AQI', radius=12, mapbox_style="carto-darkmatter", center={"lat": 22.5, "lon": 78}, zoom=4.2, template="plotly_dark", height=600)
        fig_map.add_trace(go.Scattermapbox(lat=df_geo['Lat'], lon=df_geo['Long'], mode='markers', marker=go.scattermapbox.Marker(size=8, color=df_geo['AQI'], colorscale='Reds'), text=df_geo['City']))
        st.plotly_chart(fig_map, use_container_width=True)

        st.markdown("<div class='section-header'>⚖️ National Contrast Hub</div>", unsafe_allow_html=True)
        c_a, c_b = st.columns([1.6, 1])
        with c_a: st.plotly_chart(px.line(city_archive.tail(30), x='Date', y='AQI', title=f"Daily Intensity: {s_city}", template="plotly_dark"), use_container_width=True)
        with c_b: st.plotly_chart(px.bar(df_geo.groupby('State')['AQI'].mean().reset_index().sort_values('AQI').tail(10), x='AQI', y='State', orientation='h', template="plotly_dark"), use_container_width=True)

    render_v16_hub(df_national, sel_city, sel_date)
