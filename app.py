import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os
import requests
import numpy as np
import streamlit.components.v1 as components
from datetime import datetime, date

# --- Page Configuration ---
st.set_page_config(
    page_title="The Invisible Enemy | National Scale",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Executive Design System (Custom CSS) ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;700&family=Inter:wght@400;500;600&display=swap');

    html, body, [data-testid="stAppViewContainer"] {
        font-family: 'Inter', sans-serif;
        background-color: #0c0e12;
        color: #f1f3f5;
    }

    [data-testid="stMetric"], .card-box, .status-banner {
        background: rgba(255, 255, 255, 0.03) !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        border-radius: 18px !important;
        padding: 22px !important;
        margin-bottom: 20px !important;
        box-shadow: 0 4px 20px rgba(0,0,0,0.5) !important;
    }

    .status-banner {
        text-align: center;
        font-family: 'Outfit', sans-serif;
        font-size: 1.4rem;
        font-weight: 700;
        border-width: 2px !important;
    }

    .status-safe { border-color: #00ff80 !important; color: #00ff80 !important; background: rgba(0, 255, 128, 0.08) !important; }
    .status-caution { border-color: #ffd400 !important; color: #ffd400 !important; background: rgba(255, 212, 0, 0.08) !important; }
    .status-danger { border-color: #ff5500 !important; color: #ff5500 !important; background: rgba(255, 85, 0, 0.08) !important; }
    .status-hazardous { border-color: #ff0055 !important; color: #ff0055 !important; background: rgba(255, 0, 85, 0.12) !important; }

    .main-title {
        font-family: 'Outfit', sans-serif !important;
        font-size: 2.8rem !important;
        font-weight: 700 !important;
        color: #ffffff;
        margin-bottom: 5px !important;
    }

    .section-header {
        font-family: 'Outfit', sans-serif;
        color: #00d4ff;
        font-size: 1.4rem;
        font-weight: 600;
        margin: 25px 0 15px 0;
        display: flex;
        align-items: center;
        gap: 10px;
    }

    .source-tag { font-size: 0.75rem; padding: 4px 10px; border-radius: 4px; background: rgba(0, 212, 255, 0.1); color: #00d4ff; font-weight: 700; letter-spacing: 0.1em; }
    .live-pulse { animation: pulse-update 1.5s infinite; color: #00ff80 !important; }
    @keyframes pulse-update { 0% { opacity: 1; } 50% { opacity: 0.3; } 100% { opacity: 1; } }

    .rank-card { background: rgba(255, 255, 255, 0.02); border-radius: 12px; padding: 12px; margin-bottom: 8px; border-left: 4px solid #00d4ff; }
    .rank-name { font-weight: 600; color: #fff; }
    .rank-val { color: #888; font-size: 0.9rem; }

    /* FORCED VISIBILITY: Share, Deploy, and Menu */
    header[data-testid="stHeader"] {
        background-color: #ffffff !important;
        border-bottom: 2px solid #00d4ff !important;
    }
    header[data-testid="stHeader"] * {
        color: #000000 !important;
        font-weight: 900 !important;
        fill: #000000 !important;
    }

    /* Recommendations */
    .rec-card {
        background: rgba(0, 212, 255, 0.05);
        border: 1px solid rgba(0, 212, 255, 0.15);
        border-radius: 12px;
        padding: 15px;
        margin-bottom: 12px;
    }
    .rec-tag { color: #00d4ff; font-weight: 700; margin-right: 8px; }
</style>
""", unsafe_allow_html=True)

# --- AI Voice Component ---
def voice_announcement(text):
    js_code = f"<script>var msg = new SpeechSynthesisUtterance('{text}'); window.speechSynthesis.speak(msg);</script>"
    components.html(js_code, height=0)

# --- Authentication ---
def check_authentication():
    if "authenticated" not in st.session_state:
        st.session_state["authenticated"] = False
    if st.session_state["authenticated"]:
        return True
    _, col, _ = st.columns([1, 2, 1])
    with col:
        st.markdown("<h1 style='text-align: center; margin-top: 100px; font-family: Outfit;'>The Invisible Enemy</h1>", unsafe_allow_html=True)
        uname = st.text_input("Enter User Name", placeholder="admin")
        upass = st.text_input("Enter Password", type="password")
        if st.button("Unlock Executive Hub"):
            if uname == "admin" and upass == "password123":
                st.session_state["authenticated"] = True
                st.rerun()
            else: st.error("Access Denied")
    return False

# --- Data Engine ---
@st.cache_data(show_spinner=False)
def load_national_archive():
    master_path = os.path.normpath(os.path.join(os.getcwd(), "final_india_aqi_dataset.xlsx"))
    if os.path.exists(master_path):
        df = pd.read_excel(master_path)
        df['Date'] = pd.to_datetime(df['Date'])
        return df
    return pd.DataFrame()

def fetch_satellite_aqi(city, token):
    if not token or token == "demo": return None
    try:
        url = f"https://api.waqi.info/feed/{city}/?token={token}"
        r = requests.get(url)
        data = r.json()
        if data['status'] == 'ok':
            return {'aqi': data['data']['aqi'], 'pm25': data['data']['iaqi'].get('pm25', {}).get('v', 0), 'source': 'LIVE SATELLITE'}
    except: pass
    return None

# --- Main Logic ---
if check_authentication():
    df_national = load_national_archive()
    if df_national.empty:
        st.error("Executive master data not found.")
        st.stop()

    # 1. SIDEBAR (STATIC FILTERS)
    st.sidebar.markdown("<h2 style='font-family: Outfit;'>📡 Executive Watchtower</h2>", unsafe_allow_html=True)
    
    # API Integration
    api_token = st.sidebar.text_input("AQICN API Token (Real-Time)", type="password", key="api_tok")
    
    st.sidebar.divider()
    
    # National Location Selectors
    states = sorted(df_national['State'].unique())
    sel_state = st.sidebar.selectbox("INDIA STATE/UT", states)
    
    cities = sorted(df_national[df_national['State'] == sel_state]['City'].unique())
    sel_city = st.sidebar.selectbox("CITY / TOWN SEARCH", cities)
    
    # NEW: Date Selector
    min_date = df_national['Date'].min().date()
    max_date = df_national['Date'].max().date()
    sel_date = st.sidebar.date_input("VIEW HISTORY (Calendar)", value=max_date, min_value=min_date, max_value=max_date)

    # Export Tool
    processed_df = df_national[df_national['City'] == sel_city]
    csv_data = processed_df.to_csv(index=False).encode('utf-8')
    st.sidebar.download_button("📥 Export City History (CSV)", csv_data, f"aqi_{sel_city}.csv", "text/csv")
    st.sidebar.button("System Logout", on_click=lambda: st.session_state.update({"authenticated": False}))

    # 2. AUTO-REFRESHING CONTENT ZONE (FRAGMENT)
    @st.fragment(run_every=60)
    def render_content(df, sel_state, sel_city, sel_date, api_token):
        # Data Selection (Filter by City + Date)
        target_date = pd.to_datetime(sel_date)
        city_data = df[df['City'] == sel_city]
        
        # Closest Match Logic for Date
        if not city_data[city_data['Date'] == target_date].empty:
            hist_point = city_data[city_data['Date'] == target_date].iloc[0]
        else:
            # Find closest date
            city_data['date_diff'] = (city_data['Date'] - target_date).abs()
            hist_point = city_data.sort_values('date_diff').iloc[0]
        
        # Live Feed Handling
        live_feed = fetch_satellite_aqi(sel_city, api_token)
        current_aqi = live_feed['aqi'] if (live_feed and sel_date == date.today()) else hist_point['AQI']
        source_msg = "📡 LIVE SATELLITE" if (live_feed and sel_date == date.today()) else "💾 DATABASE RECORD"

        # Voice Notification
        voice_key = f"voice_{sel_city}_{sel_date}"
        if voice_key not in st.session_state:
            st.session_state[voice_key] = True
            voice_announcement(f"Displaying air quality for {sel_city}. AQI is {current_aqi}.")

        # Top Banner & Status Message
        if current_aqi < 100: status_msg, status_class = "✅ Air Quality is Good. Safe for outdoor activities.", "status-safe"
        elif current_aqi < 200: status_msg, status_class = "⚠️ Air Quality is Moderate. Limit prolonged outdoor exposure.", "status-caution"
        elif current_aqi < 300: status_msg, status_class = "🚨 Air Quality is Poor. Avoid outdoor exercise and wear a mask.", "status-danger"
        else: status_msg, status_class = "💀 Hazardous Air Quality. STAY INDOORS! Keep windows closed.", "status-hazardous"
        
        st.markdown(f"<div class='status-banner {status_class}'>{status_msg}</div>", unsafe_allow_html=True)
        
        h1, h2 = st.columns([2, 1])
        with h1:
            st.markdown("<h1 class='main-title'>The Invisible Enemy: AQI Impact Dashboard</h1>", unsafe_allow_html=True)
            st.markdown(f"<p style='color:#888; font-size:1rem; margin-top:-10px;'>Watching {sel_city}, {sel_state} | Data from {hist_point['Date'].strftime('%d %b %Y')}</p>", unsafe_allow_html=True)
        with h2:
            st.markdown(f"<div style='text-align: right; color: #888; font-family: Outfit; font-size: 1.1rem; margin-top: 20px;'>🕒 {datetime.now().strftime('%H:%M:%S')} (Auto-Sync)</div>", unsafe_allow_html=True)

        # KPI Metrics
        k1, k2, k3, k4 = st.columns(4)
        with k1:
            st.metric("Current AQI", current_aqi)
            st.markdown(f"<div class='source-tag {'live-pulse' if (live_feed and sel_date == date.today()) else ''}'>{source_msg}</div>", unsafe_allow_html=True)
        with k2:
            st.metric("🌙 Sleep Recommendation", f"{hist_point['Sleep Hours']:.1f} hrs")
            st.markdown("<p style='font-size:0.8rem; color:#888;'>Atmospheric recovery need</p>", unsafe_allow_html=True)
        with k3:
            st.metric("⚡ Energy Level", f"{hist_point['Energy Level']}/10")
            st.markdown("<p style='font-size:0.8rem; color:#888;'>Physiological capacity today</p>", unsafe_allow_html=True)
        with k4:
            st.metric("💼 Productivity Score", f"{int(hist_point['Productivity Score'])}")
            st.markdown("<p style='font-size:0.8rem; color:#888;'>Estimated performance output</p>", unsafe_allow_html=True)

        # Action Panel
        st.markdown("<div class='section-header'>🛡️ What Should You Do Today?</div>", unsafe_allow_html=True)
        if current_aqi < 100: tips = ["Safe for all activities", "Encourage exercise", "Maintain normal routine", "Open windows for ventilation"]
        elif current_aqi < 200: tips = ["Limit outdoor exposure", "Stay hydrated", "Light outdoor activity only", "Eat antioxidant-rich foods"]
        elif current_aqi < 300: tips = ["Avoid outdoor exercise", "Wear a N95 mask outside", "Reduce physical exertion", "Stay indoors when possible"]
        else: tips = ["Do NOT go outside", "Keep ALL windows closed", "Use dedicated air purifier", "Focus on recovery and rest"]
        
        t1, t2 = st.columns(2)
        for i, tip in enumerate(tips):
            with (t1 if i % 2 == 0 else t2):
                st.markdown(f"<div class='rec-card'><span class='rec-tag'>INSTRUCTION:</span> {tip}</div>", unsafe_allow_html=True)

        # Health Guidance Explanation
        with st.expander("🔬 How pollution affects your health today"):
            st.markdown(f"**Health Risk Level: {hist_point['Health Risk Level']}**")
            st.markdown("High PM2.5 levels can penetrate deep into the lungs and enter the bloodstream, causing fatigue, headaches, and respiratory strain. Today's air quality may significantly reduce your energy efficiency.")

        # Map & Ranking Section
        st.markdown("<div class='section-header'>🗺️ All-India Heatmap & National Rankings</div>", unsafe_allow_html=True)
        m1, m2 = st.columns([1.8, 1])
        with m1:
            # Map synced to same date
            df_map = df[df['Date'] == target_date]
            if df_map.empty: df_map = df.sort_values('Date').groupby('City').tail(1)
            
            fig_heat = px.density_mapbox(df_map, lat='Lat', lon='Long', z='AQI', radius=15, mapbox_style="carto-darkmatter", template="plotly_dark", color_continuous_scale="Reds", height=500, zoom=3.5)
            fig_heat.update_layout(margin=dict(l=0, r=0, t=0, b=0))
            st.plotly_chart(fig_heat, use_container_width=True)
        with m2:
            df_rank = df_map.sort_values('AQI', ascending=False)
            st.markdown("<b>TOP 5 POLLUTION THREATS (Selected Date)</b>", unsafe_allow_html=True)
            for _, r in df_rank.head(5).iterrows():
                st.markdown(f"<div class='rank-card'><span class='rank-name'>{r['City']}</span><br><span class='rank-val'>AQI: {r['AQI']} | {r['State']}</span></div>", unsafe_allow_html=True)
            st.markdown("<br><b>TOP 5 CLEANEST CITIES</b>", unsafe_allow_html=True)
            for _, r in df_rank.tail(5).iterrows():
                st.markdown(f"<div class='rank-card' style='border-left: 4px solid #00ff80;'><span class='rank-name'>{r['City']}</span><br><span class='rank-val'>AQI: {r['AQI']} | {r['State']}</span></div>", unsafe_allow_html=True)

        # Analytics Row
        st.markdown("<div class='section-header'>📊 Predictive Insights & Trends</div>", unsafe_allow_html=True)
        a1, a2 = st.columns(2)
        with a1:
            st.write("**AQI vs 7-Day Prediction (Rolling Average)**")
            df_trend = city_data.sort_values('Date').tail(45)
            df_trend['Prediction'] = df_trend['AQI'].rolling(window=7).mean().shift(-1).fillna(df_trend['AQI'])
            fig_trend = go.Figure()
            fig_trend.add_trace(go.Scatter(x=df_trend['Date'], y=df_trend['AQI'], name='Trend', line=dict(color='#00d4ff', width=3)))
            fig_trend.add_trace(go.Scatter(x=df_trend['Date'], y=df_trend['Prediction'], name='Predictor', line=dict(color='#ff0055', dash='dot')))
            fig_trend.update_layout(template="plotly_dark", margin=dict(l=0, r=0, t=10, b=0), height=350, legend=dict(orientation="h", y=1.1, x=0))
            st.plotly_chart(fig_trend, use_container_width=True)
            st.markdown("<p style='font-size:0.8rem; color:#888;'>Examines historical patterns to forecast potential atmospheric recovery trends.</p>", unsafe_allow_html=True)
        with a2:
            st.write("**Pollution vs Lifestyle Impact Correlation**")
            fig_corr = px.scatter(df_trend, x="AQI", y="Energy Level", template="plotly_dark", color="AQI", color_continuous_scale="Reds")
            fig_corr.update_layout(margin=dict(l=0, r=0, t=10, b=0), height=350, showlegend=False, coloraxis_showscale=False)
            st.plotly_chart(fig_corr, use_container_width=True)
            st.markdown("<p style='font-size:0.8rem; color:#888;'>Visualizing the direct drop in biological performance as the 'Invisible Enemy' rises.</p>", unsafe_allow_html=True)

        st.markdown("<br><hr><center style='color: #444; font-size:0.75rem; letter-spacing: 0.1em;'>THE INVISIBLE ENEMY | NATIONAL SCALE V7.0 | AUTO-SYNC ACTIVE</center>", unsafe_allow_html=True)

    # Launch Final Hub
    render_content(df_national, sel_state, sel_city, sel_date, api_token)
