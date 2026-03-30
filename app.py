import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os
from datetime import datetime

# --- Page Configuration ---
st.set_page_config(
    page_title="AQI India | Premium Analytics",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Premium Design System (Custom CSS) ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;700&family=Inter:wght@400;600&display=swap');

    html, body, [data-testid="stAppViewContainer"] {
        font-family: 'Inter', sans-serif;
        background-color: #05070a;
        background-image: 
            radial-gradient(at 0% 0%, rgba(0, 212, 255, 0.1) 0px, transparent 50%),
            radial-gradient(at 100% 100%, rgba(0, 85, 255, 0.1) 0px, transparent 50%);
    }

    .stApp {
        background: transparent;
    }

    /* Glassmorphism Containers */
    [data-testid="stMetric"], .st-emotion-cache-1r6p8d1, .st-emotion-cache-ke07id, .chart-container {
        background: rgba(255, 255, 255, 0.02) !important;
        backdrop-filter: blur(16px) !important;
        border: 1px solid rgba(255, 255, 255, 0.05) !important;
        border-radius: 20px !important;
        padding: 24px !important;
        box-shadow: 0 12px 40px 0 rgba(0, 0, 0, 0.4) !important;
    }

    .stMetric:hover {
        border-color: rgba(0, 212, 255, 0.3) !important;
        transform: translateY(-2px);
        transition: all 0.3s ease;
    }

    /* Headlines */
    h1, h2, h3 {
        font-family: 'Outfit', sans-serif !important;
        font-weight: 700 !important;
        color: #ffffff !important;
    }

    .main-title {
        background: linear-gradient(135deg, #fff 0%, #00d4ff 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 3.5rem !important;
        margin-bottom: 5px !important;
    }

    /* Sidebar Styling */
    section[data-testid="stSidebar"] {
        background-color: rgba(5, 7, 10, 0.98) !important;
        border-right: 1px solid rgba(255, 255, 255, 0.05) !important;
    }

    /* Custom Tooltip Styling */
    .stTooltipIcon {
        color: #00d4ff !important;
    }

    /* Status Badges */
    .aqi-badge {
        padding: 4px 12px;
        border-radius: 24px;
        font-size: 0.85rem;
        font-weight: 600;
        display: inline-block;
        margin-top: 8px;
    }
    
    .aqi-good { background: rgba(0, 255, 128, 0.1); color: #00ff80; border: 1px solid rgba(0, 255, 128, 0.2); }
    .aqi-moderate { background: rgba(255, 212, 0, 0.1); color: #ffd400; border: 1px solid rgba(255, 212, 0, 0.2); }
    .aqi-poor { background: rgba(255, 85, 0, 0.1); color: #ff5500; border: 1px solid rgba(255, 85, 0, 0.2); }
</style>
""", unsafe_allow_html=True)

# --- Authentication Logic ---
def check_password():
    if "authenticated" not in st.session_state:
        st.session_state["authenticated"] = False

    if st.session_state["authenticated"]:
        return True

    _, col, _ = st.columns([1, 2, 1])
    with col:
        st.markdown("<h1 style='text-align: center; margin-top: 100px;'>E-Intelligence | AQI Portal</h1>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: #888;'>Enter credentials to access atmospheric data</p>", unsafe_allow_html=True)
        
        user = st.text_input("User ID", placeholder="admin")
        pw = st.text_input("Password", type="password", placeholder="••••••••")
        
        if st.button("Authenticate"):
            if user == "admin" and pw == "password123":
                st.session_state["authenticated"] = True
                st.rerun()
            else:
                st.error("Invalid credentials.")
                
    return False

# --- Data Engine (CSV Ingestion) ---
@st.cache_data(show_spinner=False)
def fetch_aqi_data():
    csv_path = "Air Quality India.csv" # Moved to relative path for GitHub/Cloud
    try:
        # Check if file exists to avoid crashes
        if not os.path.exists(csv_path):
             return pd.DataFrame()
        
        df = pd.read_csv(csv_path)
        df['Date'] = pd.to_datetime(df['Date'], format='%d-%m-%Y', errors='coerce')
        df = df.dropna(subset=['Date', 'AQI'])
        return df
    except Exception as e:
        st.sidebar.error(f"Error loading CSV: {e}")
        return pd.DataFrame()

# --- Main App Execution ---
if check_password():
    # Load Data
    df_raw = fetch_aqi_data()
    
    if df_raw.empty:
        st.error(f"Critical Error: Source file not found or empty at `{r'C:\Users\Rajasekhar\Downloads\Air Quality India.csv'}`")
        st.stop()

    # Sidebar Filters
    st.sidebar.markdown("<h2 style='color: #00d4ff;'>Dashboard Controls</h2>", unsafe_allow_html=True)
    
    # Auto-Refresh Control
    refresh_rate = st.sidebar.slider("Refresh Interval (s)", 10, 300, 60)
    
    # Advanced Filters
    cities = sorted(df_raw['City'].unique())
    selected_cities = st.sidebar.multiselect("Select Cities", cities, default=cities)
    
    # Default to last 30 days of data if range isn't touched
    max_d = df_raw['Date'].max()
    min_d = df_raw['Date'].min()
    date_range = st.sidebar.date_input("Date Horizon", [min_d, max_d])
    
    if st.sidebar.button("System Logout"):
        st.session_state["authenticated"] = False
        st.rerun()

    # Title Section
    st.markdown("<h1 class='main-title'>Atmospheric Intelligence</h1>", unsafe_allow_html=True)
    
    # Visual Legend Row
    st.markdown("""
    <div style='display: flex; gap: 20px; flex-wrap: wrap; margin-bottom: 25px; background: rgba(255,255,255,0.02); padding: 15px; border-radius: 12px; border: 1px solid rgba(255,255,255,0.05);'>
        <span style='color: #888; font-weight: 600; margin-right: 10px;'>LEGEND:</span>
        <span class='aqi-badge aqi-good'>● GOOD [0-50]</span>
        <span class='aqi-badge aqi-moderate' style='background: rgba(255,212,0,0.1); color: #ffd400;'>● MODERATE [51-100]</span>
        <span class='aqi-badge' style='background: rgba(255,165,0,0.1); color: #ffa500;'>● POOR [101-200]</span>
        <span class='aqi-badge aqi-poor'>● UNHEALTHY [201-300]</span>
        <span class='aqi-badge' style='background: rgba(255,0,0,0.2); color: #ff0000;'>● SEVERE [300+]</span>
    </div>
    """, unsafe_allow_html=True)

    # Filtering Data
    if len(date_range) == 2:
        mask = (df_raw['City'].isin(selected_cities)) & \
               (df_raw['Date'] >= pd.to_datetime(date_range[0])) & \
               (df_raw['Date'] <= pd.to_datetime(date_range[1]))
        df = df_raw.loc[mask]
    else:
        df = df_raw[df_raw['City'].isin(selected_cities)]

    # --- Fragment for Auto-Refreshing Analytics ---
    @st.fragment(run_every=refresh_rate)
    def render_advanced_analytics():
        if df.empty:
            st.warning("Please adjust your filters. No data found for select criteria.")
            return

        # Metrics Row (6 Columns for better detail)
        m1, m2, m3, m4, m5, m6 = st.columns(6)
        avg_aqi = df['AQI'].mean()
        max_aqi = df['AQI'].max()
        
        with m1: st.metric("Live India AQI", f"{avg_aqi:.0f}")
        with m2: st.metric("Peak Criticality", f"{max_aqi:.0f}")
        with m3: st.metric("Avg PM2.5", f"{df['PM2.5'].mean():.1f}")
        with m4: st.metric("Avg NO2", f"{df['NO2'].mean():.1f}")
        with m5: st.metric("Avg SO2", f"{df['SO2'].mean():.1f}")
        with m6:
             st.markdown(f"**Network State**<br><span class='aqi-badge aqi-good'>ONLINE</span>", unsafe_allow_html=True)
             st.markdown(f"<p style='color: #444; font-size: 0.7rem;'>TS: {datetime.now().strftime('%H:%M:%S')}</p>", unsafe_allow_html=True)

        st.divider()

        # Complex Charts Row 1
        c1, c2 = st.columns([2, 1])
        
        with c1:
            st.subheader("📊 Multi-City Temporal AQI Evolution")
            # Vibrant multi-color sequence
            fig_trend = px.area(df, x="Date", y="AQI", color="City",
                               template="plotly_dark", 
                               color_discrete_sequence=px.colors.qualitative.Alphabet)
            fig_trend.update_layout(
                paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                margin=dict(l=0, r=0, t=20, b=0), height=450,
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
            )
            st.plotly_chart(fig_trend, use_container_width=True)

        with c2:
            st.subheader("🥧 Atmospheric Distribution")
            bucket_data = df['AQI_Bucket'].value_counts().reset_index()
            # Rainbow-like sequential color for pie
            fig_pie = px.pie(bucket_data, values='count', names='AQI_Bucket',
                            hole=0.6, template="plotly_dark",
                            color_discrete_sequence=px.colors.sequential.Sunset_r)
            fig_pie.update_layout(
                margin=dict(l=10, r=10, t=10, b=10), height=450,
                showlegend=True, legend=dict(orientation="h", y=-0.1)
            )
            st.plotly_chart(fig_pie, use_container_width=True)

        st.divider()

        # Row 2: Advanced Correlation
        r1, r2 = st.columns([1, 1])
        
        with r1:
            st.subheader("🏭 Pollution Load Matrix")
            pollutants = ['PM2.5', 'PM10', 'NO2', 'SO2', 'O3', 'CO']
            avg_pollutants = df[pollutants].mean().reset_index()
            avg_pollutants.columns = ['Pollutant', 'Level']
            
            # Using Neon Gradient
            fig_bar = px.bar(avg_pollutants, x='Pollutant', y='Level',
                            color='Level', color_continuous_scale='Turbo',
                            template="plotly_dark")
            fig_bar.update_layout(
                paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                coloraxis_showscale=False, height=400
            )
            st.plotly_chart(fig_bar, use_container_width=True)

        with r2:
            st.subheader("🏙️ Top Polluted Metropolitan Hubs")
            city_ranking = df.groupby('City')['AQI'].mean().sort_values(ascending=False).head(12).reset_index()
            fig_h_bar = px.bar(city_ranking, x='AQI', y='City',
                              orientation='h', template="plotly_dark",
                              color='AQI', color_continuous_scale='Magma_r')
            fig_h_bar.update_layout(
                paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                coloraxis_showscale=False, height=400,
                yaxis={'categoryorder':'total ascending'}
            )
            st.plotly_chart(fig_h_bar, use_container_width=True)

    # Initial Render
    render_advanced_analytics()

    # Footer
    st.markdown("<br><hr><center style='color: #444; font-size: 0.8rem;'>AQI PLATFORM V2.0 | REAL-TIME GEOSPATIAL INTELLIGENCE SERVICE</center>", unsafe_allow_html=True)
