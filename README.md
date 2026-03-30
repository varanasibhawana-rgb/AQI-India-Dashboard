# Air Quality Intelligence Dashboard (INDIA)

A premium, interactive dashboard built with **Streamlit** and **Plotly** to visualize air quality data across various Indian cities.

## 🚀 Key Features

- **🔐 Secure Login**: Corporate-style authentication (User ID / Password).
- **📉 Real-time Trends**: Temporal AQI evolution with multi-city comparison.
- **🎨 Vibrant Analytics**:
  - **Air Health Spectrum**: Donut charts for AQI bucket distribution.
  - **Pollutant Load matrix**: High-contrast bar charts for PM2.5, NO2, SO2, etc.
  - **Critical Zone Ranking**: Top 10 most polluted metropolitan hubs.
- **⚡ Auto-Refresh**: Seamless data updates every 60 seconds (configurable).
- **📱 Responsive UI**: Modern glassmorphic dark-mode design.

## 🛠️ Setup & Installation

1.  **Clone the Repository**:
    ```bash
    git clone https://github.com/your-username/your-repo-name.git
    cd your-repo-name
    ```
2.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```
3.  **Run the Dashboard**:
    ```bash
    streamlit run app.py
    ```

## 🔒 Authentication

The dashboard is secured by a login screen. Default credentials:
- **User ID**: `admin`
- **Password**: `password123`

## 📊 Data Source

The dashboard reads from `Air Quality India.csv`. Ensure this file is updated periodically for the "Auto-Refresh" feature to provide live insights.
