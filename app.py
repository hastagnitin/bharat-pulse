import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title="Bharat Pulse Dashboard", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
<style>
    div[data-testid="metric-container"] {
        background-color: #ffffff;
        border: 1px solid #e6e6e6;
        padding: 15px;
        border-radius: 5px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
</style>
""", unsafe_allow_html=True)

def load_data():
    conn = sqlite3.connect('bharat_pulse.db')
    df = pd.read_sql_query("SELECT * FROM checks ORDER BY timestamp DESC", conn)
    conn.close()
    return df

df = load_data()

if not df.empty:
    latest_df = df.drop_duplicates(subset=['service_name'], keep='first')
    
    st.markdown("<h3 style='color: #333333;'>Infrastructure Activity Overview</h3>", unsafe_allow_html=True)
    
    total_services = len(latest_df)
    up_count = len(latest_df[latest_df['status'] == 'UP'])
    down_count = len(latest_df[latest_df['status'] == 'DOWN'])
    avg_resp = latest_df['response_time_ms'].mean()
    uptime_pct = (up_count / total_services) * 100 if total_services > 0 else 0
    
    kpi1, kpi2, kpi3, kpi4 = st.columns(4)
    kpi1.metric("Total Monitored Lots", total_services)
    kpi2.metric("Operational Uptime", f"{uptime_pct:.1f}%")
    kpi3.metric("Critical Alerts", down_count)
    kpi4.metric("Avg Latency", f"{avg_resp:.0f} ms")
    
    st.write("---")
    
    col_left, col_right = st.columns([2, 1])
    
    with col_left:
        fig_bar = px.bar(
            latest_df, 
            x='service_name', 
            y='response_time_ms', 
            color='status',
            color_discrete_map={'UP': '#00c39a', 'DOWN': '#ff4b4b'},
            title="Service Latency Activity",
            template="plotly_white"
        )
        fig_bar.update_layout(
            margin=dict(l=20, r=20, t=40, b=20),
            xaxis_title="",
            yaxis_title="Latency (ms)",
            plot_bgcolor='rgba(0,0,0,0)'
        )
        st.plotly_chart(fig_bar, use_container_width=True)
        
    with col_right:
        status_counts = latest_df['status'].value_counts().reset_index()
        status_counts.columns = ['status', 'count']
        
        fig_pie = px.pie(
            status_counts, 
            values='count', 
            names='status',
            color='status',
            color_discrete_map={'UP': '#00c39a', 'DOWN': '#333333'},
            title="Distribution by Status",
            template="plotly_white"
        )
        fig_pie.update_layout(margin=dict(l=20, r=20, t=40, b=20))
        st.plotly_chart(fig_pie, use_container_width=True)
        
    st.write("---")
    
    st.markdown("<h4 style='color: #333333;'>Detailed Infrastructure Logs</h4>", unsafe_allow_html=True)
    st.dataframe(latest_df[['service_name', 'status', 'response_time_ms', 'error_message', 'timestamp']], use_container_width=True, hide_index=True)

else:
    st.warning("No data available. Please wait for the database to populate.")