import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import random
import time
from datetime import datetime, timedelta
import numpy as np

# Page configuration
st.set_page_config(
    page_title="Battery Cell Monitoring Dashboard",
    page_icon="🔋",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Enhanced Custom CSS for better styling and animations
st.markdown("""
<style>
    .main-header {
        text-align: center;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 3rem;
        font-weight: bold;
        margin-bottom: 2rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
    }
    
    .metric-card {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        padding: 1.5rem;
        border-radius: 15px;
        border-left: 5px solid #1f77b4;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        transition: transform 0.3s ease;
    }
    
    .metric-card:hover {
        transform: translateY(-5px);
    }
    
    .health-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 20px;
        border-radius: 20px;
        color: white;
        text-align: center;
        margin: 10px 0;
        box-shadow: 0 8px 25px rgba(0,0,0,0.15);
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
    }
    
    .health-card::before {
        content: '';
        position: absolute;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background: linear-gradient(45deg, transparent, rgba(255,255,255,0.1), transparent);
        transform: rotate(45deg);
        transition: all 0.6s ease;
    }
    
    .health-card:hover::before {
        animation: shine 0.6s ease-in-out;
    }
    
    @keyframes shine {
        0% { transform: translateX(-100%) translateY(-100%) rotate(45deg); }
        100% { transform: translateX(100%) translateY(100%) rotate(45deg); }
    }
    
    .health-excellent {
        background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
        animation: pulse-green 2s infinite;
    }
    
    .health-good {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    
    .health-warning {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        animation: pulse-orange 2s infinite;
    }
    
    .health-critical {
        background: linear-gradient(135deg, #ff416c 0%, #ff4b2b 100%);
        animation: pulse-red 1s infinite;
    }
    
    @keyframes pulse-green {
        0%, 100% { box-shadow: 0 8px 25px rgba(17, 153, 142, 0.3); }
        50% { box-shadow: 0 8px 35px rgba(17, 153, 142, 0.6); }
    }
    
    @keyframes pulse-orange {
        0%, 100% { box-shadow: 0 8px 25px rgba(240, 147, 251, 0.3); }
        50% { box-shadow: 0 8px 35px rgba(240, 147, 251, 0.6); }
    }
    
    @keyframes pulse-red {
        0%, 100% { box-shadow: 0 8px 25px rgba(255, 65, 108, 0.4); }
        50% { box-shadow: 0 8px 35px rgba(255, 65, 108, 0.8); }
    }
    
    .status-excellent {
        color: #00ff88;
        font-weight: bold;
        text-shadow: 0 0 10px rgba(0, 255, 136, 0.5);
    }
    
    .status-good {
        color: #28a745;
        font-weight: bold;
        text-shadow: 0 0 10px rgba(40, 167, 69, 0.5);
    }
    
    .status-warning {
        color: #ff6b35;
        font-weight: bold;
        text-shadow: 0 0 10px rgba(255, 107, 53, 0.5);
        animation: blink 1.5s infinite;
    }
    
    .status-critical {
        color: #ff3838;
        font-weight: bold;
        text-shadow: 0 0 15px rgba(255, 56, 56, 0.8);
        animation: blink 0.8s infinite;
    }
    
    @keyframes blink {
        0%, 50% { opacity: 1; }
        51%, 100% { opacity: 0.6; }
    }
    
    .battery-icon {
        font-size: 2.5rem;
        margin-bottom: 10px;
        display: block;
    }
    
    .health-percentage {
        font-size: 2.5rem;
        font-weight: bold;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }
    
    .cell-name {
        font-size: 1.1rem;
        font-weight: 600;
        margin-bottom: 5px;
        opacity: 0.9;
    }
    
    .overview-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 20px;
        border-radius: 15px;
        text-align: center;
        box-shadow: 0 8px 25px rgba(0,0,0,0.15);
        margin: 10px 0;
    }
    
    .overview-number {
        font-size: 2rem;
        font-weight: bold;
        display: block;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }
    
    .overview-label {
        font-size: 0.9rem;
        opacity: 0.8;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'cells_data' not in st.session_state:
    st.session_state.cells_data = {}
if 'historical_data' not in st.session_state:
    st.session_state.historical_data = []
if 'is_monitoring' not in st.session_state:
    st.session_state.is_monitoring = False

# Cell type configurations with enhanced colors
CELL_CONFIGS = {
    "LFP": {
        "nominal_voltage": 3.2,
        "min_voltage": 2.8,
        "max_voltage": 3.6,
        "color": "#00ff88",
        "gradient": "linear-gradient(135deg, #11998e 0%, #38ef7d 100%)"
    },
    "NMC": {
        "nominal_voltage": 3.6,
        "min_voltage": 3.2,
        "max_voltage": 4.0,
        "color": "#ff6b6b",
        "gradient": "linear-gradient(135deg, #ff416c 0%, #ff4b2b 100%)"
    },
    "LTO": {
        "nominal_voltage": 2.4,
        "min_voltage": 1.5,
        "max_voltage": 2.8,
        "color": "#ffa726",
        "gradient": "linear-gradient(135deg, #f093fb 0%, #f5576c 100%)"
    },
    "LiCoO2": {
        "nominal_voltage": 3.7,
        "min_voltage": 3.0,
        "max_voltage": 4.2,
        "color": "#ab47bc",
        "gradient": "linear-gradient(135deg, #667eea 0%, #764ba2 100%)"
    }
}

def get_battery_icon(health):
    """Return battery icon based on health percentage"""
    if health >= 90:
        return "🔋"  # Full battery
    elif health >= 75:
        return "🔋"  # Good battery
    elif health >= 50:
        return "🪫"  # Medium battery
    elif health >= 25:
        return "🪫"  # Low battery
    else:
        return "🪫"  # Critical battery

def get_health_class(health):
    """Return CSS class based on health percentage"""
    if health >= 90:
        return "health-excellent"
    elif health >= 75:
        return "health-good"
    elif health >= 50:
        return "health-warning"
    else:
        return "health-critical"

def get_status_class(status):
    """Return CSS class based on status"""
    if status == "Excellent":
        return "status-excellent"
    elif status == "Good":
        return "status-good"
    elif status == "Warning":
        return "status-warning"
    else:
        return "status-critical"

def generate_cell_data(cell_type, cell_id, current_time):
    """Generate realistic battery cell data with enhanced status"""
    config = CELL_CONFIGS[cell_type]
    
    # Simulate realistic voltage fluctuations
    base_voltage = config["nominal_voltage"]
    voltage_variation = random.uniform(-0.1, 0.1)
    voltage = round(base_voltage + voltage_variation, 3)
    
    # Simulate current (positive for charging, negative for discharging)
    current = round(random.uniform(-5.0, 5.0), 2)
    
    # Temperature simulation with some correlation to current
    base_temp = 25
    temp_variation = abs(current) * 0.5 + random.uniform(-2, 8)
    temperature = round(base_temp + temp_variation, 1)
    
    # Calculate power and capacity
    power = round(voltage * abs(current), 2)
    capacity = round(random.uniform(2.8, 3.2), 2)  # Ah
    
    # Enhanced health calculation
    voltage_health = 100 * (1 - abs(voltage - config["nominal_voltage"]) / config["nominal_voltage"])
    temp_health = 100 * max(0, 1 - max(0, temperature - 35) / 20)
    overall_health = round((voltage_health + temp_health) / 2, 1)
    
    # Enhanced status determination
    if voltage < config["min_voltage"] or voltage > config["max_voltage"] or temperature > 45:
        status = "Critical"
    elif temperature > 40 or overall_health < 75:
        status = "Warning"
    elif overall_health >= 90:
        status = "Excellent"
    else:
        status = "Good"
    
    return {
        "cell_id": cell_id,
        "cell_type": cell_type,
        "voltage": voltage,
        "current": current,
        "temperature": temperature,
        "power": power,
        "capacity": capacity,
        "health": overall_health,
        "status": status,
        "timestamp": current_time,
        "min_voltage": config["min_voltage"],
        "max_voltage": config["max_voltage"]
    }

# Main Dashboard
st.markdown('<h1 class="main-header">🔋 Battery Cell Monitoring Dashboard</h1>', unsafe_allow_html=True)

# Sidebar for configuration
with st.sidebar:
    st.header("⚙️ Configuration")
    
    # Bench and group information
    bench_name = st.text_input("Bench Name", value="Bench-001", key="bench_name")
    group_num = st.number_input("Group Number", min_value=1, max_value=100, value=1, key="group_num")
    
    st.divider()
    
    # Cell configuration
    st.subheader("Cell Configuration")
    num_cells = st.slider("Number of Cells", min_value=1, max_value=16, value=8)
    
    cell_types = []
    for i in range(num_cells):
        cell_type = st.selectbox(
            f"Cell {i+1} Type",
            options=list(CELL_CONFIGS.keys()),
            key=f"cell_type_{i}"
        )
        cell_types.append(cell_type)
    
    st.divider()
    
    # Control panel
    st.subheader("🎛️ Control Panel")
    
    if st.button("Initialize Cells", type="primary"):
        current_time = datetime.now()
        st.session_state.cells_data = {}
        for i, cell_type in enumerate(cell_types):
            cell_id = f"Cell_{i+1}_{cell_type}"
            st.session_state.cells_data[cell_id] = generate_cell_data(cell_type, cell_id, current_time)
        st.success("Cells initialized successfully!")
    
    # Monitoring controls
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Start Monitoring"):
            st.session_state.is_monitoring = True
            st.success("Monitoring started!")
    
    with col2:
        if st.button("Stop Monitoring"):
            st.session_state.is_monitoring = False
            st.info("Monitoring stopped!")
    
    # Auto-refresh
    auto_refresh = st.checkbox("Auto Refresh (5s)", value=True)
    
    if auto_refresh and st.session_state.is_monitoring:
        time.sleep(5)
        st.rerun()

# Main content area
if st.session_state.cells_data:
    
    # Update data if monitoring
    if st.session_state.is_monitoring:
        current_time = datetime.now()
        for cell_id in st.session_state.cells_data.keys():
            cell_type = st.session_state.cells_data[cell_id]["cell_type"]
            st.session_state.cells_data[cell_id] = generate_cell_data(cell_type, cell_id, current_time)
        
        # Store historical data
        st.session_state.historical_data.append({
            "timestamp": current_time,
            "data": st.session_state.cells_data.copy()
        })
        
        # Keep only last 100 records
        if len(st.session_state.historical_data) > 100:
            st.session_state.historical_data = st.session_state.historical_data[-100:]
    
    # System overview with enhanced styling
    st.header(f"📊 System Overview - {bench_name} (Group {group_num})")
    
    # Summary metrics with enhanced cards
    total_cells = len(st.session_state.cells_data)
    excellent_cells = sum(1 for cell in st.session_state.cells_data.values() if cell["status"] == "Excellent")
    good_cells = sum(1 for cell in st.session_state.cells_data.values() if cell["status"] == "Good")
    warning_cells = sum(1 for cell in st.session_state.cells_data.values() if cell["status"] == "Warning")
    critical_cells = sum(1 for cell in st.session_state.cells_data.values() if cell["status"] == "Critical")
    avg_health = np.mean([cell["health"] for cell in st.session_state.cells_data.values()])
    total_power = sum([cell["power"] for cell in st.session_state.cells_data.values()])
    
    col1, col2, col3, col4, col5, col6, col7 = st.columns(7)
    
    with col1:
        st.markdown(f"""
        <div class="overview-card">
            <span class="overview-number">{total_cells}</span>
            <span class="overview-label">Total Cells</span>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="overview-card" style="background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);">
            <span class="overview-number">{excellent_cells}</span>
            <span class="overview-label">Excellent</span>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="overview-card" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);">
            <span class="overview-number">{good_cells}</span>
            <span class="overview-label">Good</span>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class="overview-card" style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);">
            <span class="overview-number">{warning_cells}</span>
            <span class="overview-label">Warning</span>
        </div>
        """, unsafe_allow_html=True)
    
    with col5:
        st.markdown(f"""
        <div class="overview-card" style="background: linear-gradient(135deg, #ff416c 0%, #ff4b2b 100%);">
            <span class="overview-number">{critical_cells}</span>
            <span class="overview-label">Critical</span>
        </div>
        """, unsafe_allow_html=True)
    
    with col6:
        st.markdown(f"""
        <div class="overview-card">
            <span class="overview-number">{avg_health:.1f}%</span>
            <span class="overview-label">Avg Health</span>
        </div>
        """, unsafe_allow_html=True)
    
    with col7:
        st.markdown(f"""
        <div class="overview-card">
            <span class="overview-number">{total_power:.1f}W</span>
            <span class="overview-label">Total Power</span>
        </div>
        """, unsafe_allow_html=True)
    
    # Tabs for different views
    tab1, tab2, tab3, tab4 = st.tabs(["📈 Real-time Data", "🔋 Enhanced Health", "🔥 Temperature Monitor", "⚡ Historical Trends"])
    
    with tab1:
        st.subheader("Real-time Cell Data")
        
        # Create DataFrame for display
        df = pd.DataFrame(st.session_state.cells_data.values())
        
        # Display data table with colored status
        df_display = df[["cell_id", "cell_type", "voltage", "current", "temperature", "power", "capacity", "health", "status"]].copy()
        st.dataframe(df_display, use_container_width=True)
        
        # Enhanced voltage comparison chart with better colors
        fig_voltage = px.bar(
            df, 
            x="cell_id", 
            y="voltage", 
            color="cell_type",
            title="🔋 Cell Voltage Comparison",
            color_discrete_map={cell_type: config["color"] for cell_type, config in CELL_CONFIGS.items()}
        )
        fig_voltage.update_traces(marker_line_width=2, marker_line_color='white')
        fig_voltage.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font_color='#333',
            title_font_size=20
        )
        st.plotly_chart(fig_voltage, use_container_width=True)
    
    with tab2:
        st.subheader("🔋 Enhanced Battery Health Indicators")
        
        # Enhanced health cards with animations and better visuals
        cols = st.columns(4)
        for i, (cell_id, cell_data) in enumerate(st.session_state.cells_data.items()):
            with cols[i % 4]:
                health_class = get_health_class(cell_data["health"])
                battery_icon = get_battery_icon(cell_data["health"])
                status_class = get_status_class(cell_data["status"])
                
                st.markdown(f"""
                <div class="health-card {health_class}">
                    <div class="battery-icon">{battery_icon}</div>
                    <div class="cell-name">{cell_id}</div>
                    <div class="health-percentage">{cell_data["health"]:.1f}%</div>
                    <div class="{status_class}" style="margin-top: 10px; font-size: 1.1rem;">
                        {cell_data["status"]}
                    </div>
                    <div style="margin-top: 8px; font-size: 0.9rem; opacity: 0.8;">
                        {cell_data["cell_type"]} • {cell_data["voltage"]}V
                    </div>
                </div>
                """, unsafe_allow_html=True)
        
        # Enhanced circular health indicators
        st.subheader("🎯 Health Overview Gauges")
        gauge_cols = st.columns(4)
        
        for i, (cell_id, cell_data) in enumerate(st.session_state.cells_data.items()):
            with gauge_cols[i % 4]:
                # Create enhanced gauge with better colors
                health_value = cell_data["health"]
                
                # Determine colors based on health
                if health_value >= 90:
                    gauge_color = "#00ff88"
                    bar_color = "#11998e"
                elif health_value >= 75:
                    gauge_color = "#667eea"
                    bar_color = "#764ba2"
                elif health_value >= 50:
                    gauge_color = "#f093fb"
                    bar_color = "#f5576c"
                else:
                    gauge_color = "#ff416c"
                    bar_color = "#ff4b2b"
                
                fig_gauge = go.Figure(go.Indicator(
                    mode = "gauge+number+delta",
                    value = health_value,
                    domain = {'x': [0, 1], 'y': [0, 1]},
                    title = {'text': f"🔋 {cell_id}", 'font': {'size': 14, 'color': '#333'}},
                    delta = {'reference': 100, 'increasing': {'color': gauge_color}},
                    gauge = {
                        'axis': {'range': [None, 100], 'tickcolor': '#666'},
                        'bar': {'color': bar_color, 'thickness': 0.8},
                        'bgcolor': "rgba(255,255,255,0.1)",
                        'borderwidth': 3,
                        'bordercolor': gauge_color,
                        'steps': [
                            {'range': [0, 25], 'color': "rgba(255, 65, 108, 0.2)"},
                            {'range': [25, 50], 'color': "rgba(240, 147, 251, 0.2)"},
                            {'range': [50, 75], 'color': "rgba(102, 126, 234, 0.2)"},
                            {'range': [75, 90], 'color': "rgba(17, 153, 142, 0.2)"},
                            {'range': [90, 100], 'color': "rgba(0, 255, 136, 0.3)"}
                        ],
                        'threshold': {
                            'line': {'color': gauge_color, 'width': 4},
                            'thickness': 0.75,
                            'value': 90
                        }
                    }
                ))
                
                fig_gauge.update_layout(
                    height=280,
                    font={'color': "#333", 'size': 12},
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)'
                )
                st.plotly_chart(fig_gauge, use_container_width=True)
        
        # Enhanced health distribution with better colors
        fig_health = px.histogram(
            df, 
            x="health", 
            nbins=15, 
            title="🎯 Health Distribution Analysis",
            color="status",
            color_discrete_map={
                "Excellent": "#00ff88", 
                "Good": "#667eea", 
                "Warning": "#f093fb", 
                "Critical": "#ff416c"
            }
        )
        fig_health.update_traces(marker_line_width=2, marker_line_color='white')
        fig_health.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font_color='#333',
            title_font_size=18
        )
        st.plotly_chart(fig_health, use_container_width=True)
    
    with tab3:
        st.subheader("🔥 Temperature Monitoring")
        
        # Enhanced temperature heatmap
        temp_data = df.pivot_table(values='temperature', index='cell_type', columns='cell_id', fill_value=0)
        fig_temp = px.imshow(
            temp_data, 
            title="🌡️ Temperature Heatmap",
            color_continuous_scale="plasma",
            aspect="auto"
        )
        fig_temp.update_layout(
            title_font_size=18,
            font_color='#333'
        )
        st.plotly_chart(fig_temp, use_container_width=True)
        
        # Enhanced temperature vs power scatter with better styling
        fig_scatter = px.scatter(
            df, 
            x="temperature", 
            y="power", 
            color="cell_type",
            size="health",
            title="🔥 Temperature vs Power Analysis",
            hover_data=["cell_id", "voltage", "current"],
            color_discrete_map={cell_type: config["color"] for cell_type, config in CELL_CONFIGS.items()}
        )
        fig_scatter.update_traces(marker_line_width=2, marker_line_color='white')
        fig_scatter.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font_color='#333',
            title_font_size=18
        )
        st.plotly_chart(fig_scatter, use_container_width=True)
    
    with tab4:
        st.subheader("⚡ Historical Trends")
        
        if len(st.session_state.historical_data) > 1:
            # Prepare historical data
            hist_df = []
            for record in st.session_state.historical_data[-50:]:  # Last 50 records
                for cell_id, cell_data in record["data"].items():
                    hist_df.append({
                        "timestamp": record["timestamp"],
                        "cell_id": cell_id,
                        "voltage": cell_data["voltage"],
                        "current": cell_data["current"],
                        "temperature": cell_data["temperature"],
                        "health": cell_data["health"]
                    })
            
            hist_df = pd.DataFrame(hist_df)
            
            # Enhanced multi-line charts with better colors
            fig_trends = make_subplots(
                rows=2, cols=2,
                subplot_titles=("⚡ Voltage Trends", "🔄 Current Trends", "🌡️ Temperature Trends", "💚 Health Trends"),
                vertical_spacing=0.08
            )
            
            # Color palette for different cells
            colors = ['#00ff88', '#ff416c', '#f093fb', '#667eea', '#ffa726', '#ab47bc', '#26c6da', '#66bb6a']
            
            # Voltage trends
            for i, cell_id in enumerate(hist_df["cell_id"].unique()):
                cell_hist = hist_df[hist_df["cell_id"] == cell_id]
                fig_trends.add_trace(
                    go.Scatter(
                        x=cell_hist["timestamp"], 
                        y=cell_hist["voltage"], 
                        name=f"{cell_id}_V", 
                        line=dict(width=3, color=colors[i % len(colors)])
                    ),
                    row=1, col=1
                )
            
            # Current trends
            for i, cell_id in enumerate(hist_df["cell_id"].unique()):
                cell_hist = hist_df[hist_df["cell_id"] == cell_id]
                fig_trends.add_trace(
                    go.Scatter(
                        x=cell_hist["timestamp"], 
                        y=cell_hist["current"], 
                        name=f"{cell_id}_I", 
                        showlegend=False,
                        line=dict(width=3, color=colors[i % len(colors)])
                    ),
                    row=1, col=2
                )
            
            # Temperature trends
            for i, cell_id in enumerate(hist_df["cell_id"].unique()):
                cell_hist = hist_df[hist_df["cell_id"] == cell_id]
                fig_trends.add_trace(
                    go.Scatter(
                        x=cell_hist["timestamp"], 
                        y=cell_hist["temperature"], 
                        name=f"{cell_id}_T", 
                        showlegend=False,
                        line=dict(width=3, color=colors[i % len(colors)])
                    ),
                    row=2, col=1
                )
            
            # Health trends
            for i, cell_id in enumerate(hist_df["cell_id"].unique()):
                cell_hist = hist_df[hist_df["cell_id"] == cell_id]
                fig_trends.add_trace(
                    go.Scatter(
                        x=cell_hist["timestamp"], 
                        y=cell_hist["health"], 
                        name=f"{cell_id}_H", 
                        showlegend=False,
                        line=dict(width=3, color=colors[i % len(colors)]
