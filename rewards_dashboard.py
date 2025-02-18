import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import pandas as pd
from algo_rewards import AlgorandRewardsTracker
import requests
import os
from supabase import create_client, Client
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Supabase client
supabase_url = os.getenv('SUPABASE_URL')
supabase_key = os.getenv('SUPABASE_KEY')

if not supabase_url or not supabase_key:
    st.error("Missing Supabase credentials")
    st.stop()

try:
    supabase: Client = create_client(
        supabase_url=supabase_url,
        supabase_key=supabase_key
    )
    st.success("Connected to Supabase successfully")
except Exception as e:
    st.error(f"Failed to initialize Supabase client: {e}")
    st.stop()

# Page config
st.set_page_config(
    page_title="Algorand Node Rewards Dashboard",
    page_icon="💰",
    layout="wide"
)

# Constants
address = "KK4KTUPTKX3YNA5G2HMYO4CD63F6MTKXDJLIOJ5RRT7TRQK6HC25NUGZTY"
start_date = datetime(2025, 2, 15)
original_balance = 145726.37  # Updated original balance

def get_data_from_supabase():
    """Fetch data from Supabase."""
    try:
        # Get latest node status
        node_status = supabase.table('node_status')\
            .select('*')\
            .eq('address', address)\
            .order('timestamp', desc=True)\
            .limit(1)\
            .execute()
        
        # Get all rewards
        rewards = supabase.table('rewards')\
            .select('*')\
            .eq('address', address)\
            .order('timestamp')\
            .execute()
        
        # Convert to DataFrame
        if rewards.data:
            df = pd.DataFrame(rewards.data)
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            df['cumulative_rewards'] = df['amount'].cumsum()
            
            # Calculate metrics
            total_rewards = df['amount'].sum()
            current_balance = original_balance + total_rewards  # Calculate current balance
            roi = (total_rewards / original_balance) * 100  # Calculate ROI based on original balance
            
            return df, current_balance, roi, original_balance, total_rewards, node_status.data[0] if node_status.data else None
            
        return pd.DataFrame(), original_balance, 0, original_balance, 0, None
        
    except Exception as e:
        st.error(f"Error fetching data from Supabase: {e}")
        return pd.DataFrame(), original_balance, 0, original_balance, 0, None

# Get data
df, current_balance, roi, original_balance, total_rewards, node_status = get_data_from_supabase()

# Dashboard title
st.title("🏦 Algorand Node Rewards Dashboard")

# Top metrics
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "Total Rewards",
        f"{total_rewards:.2f} ALGO",
        f"{df['amount'].mean():.2f} ALGO/reward" if not df.empty else None
    )

with col2:
    daily_rewards = df.groupby(df['timestamp'].dt.date)['amount'].sum().mean() if not df.empty else 0
    monthly_projection = daily_rewards * 30 if not pd.isna(daily_rewards) else 0
    st.metric(
        "Average Daily Rewards",
        f"{daily_rewards:.2f} ALGO",
        f"{monthly_projection:.2f} ALGO/month (projected)"
    )

with col3:
    st.metric(
        "Current Balance",
        f"{current_balance:.2f} ALGO",
        f"Original Balance: {original_balance:.2f} ALGO"
    )

with col4:
    st.metric(
        "ROI Since Start",
        f"{roi:.2f}%",
        f"Based on {original_balance:.2f} ALGO initial"
    )

# Cumulative rewards over time
st.subheader("📈 Cumulative Rewards Over Time")
if not df.empty:
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df['timestamp'],
        y=df['cumulative_rewards'],
        mode='lines+markers',
        name='Cumulative Rewards',
        line=dict(width=2, color='#2ecc71'),
        hovertemplate="Date: %{x}<br>Total Rewards: %{y:.2f} ALGO<extra></extra>"
    ))
    fig.update_layout(
        title='Cumulative Rewards Growth',
        xaxis_title='Date',
        yaxis_title='Total Rewards (ALGO)',
        hovermode='x unified',
        showlegend=False
    )
    st.plotly_chart(fig, use_container_width=True)

# Rewards statistics
st.subheader("📊 Rewards Statistics")
col1, col2 = st.columns(2)

with col1:
    st.write("Recent Rewards")
    if not df.empty:
        recent_rewards = df.sort_values('timestamp', ascending=False).head(5)
        recent_rewards['time'] = recent_rewards['timestamp'].dt.strftime('%Y-%m-%d %H:%M:%S')
        st.dataframe(
            recent_rewards[['time', 'amount', 'cumulative_rewards']]
            .rename(columns={
                'time': 'Time',
                'amount': 'Reward Amount',
                'cumulative_rewards': 'Total Rewards'
            })
            .style.format({
                'Reward Amount': '{:.6f}',
                'Total Rewards': '{:.6f}'
            }),
            hide_index=True
        )

with col2:
    if not df.empty:
        # Calculate time between rewards
        df['time_diff'] = df['timestamp'].diff()
        avg_time_between = df['time_diff'].mean()
        
        st.write("Performance Metrics")
        metrics_df = pd.DataFrame([
            {'Metric': 'Original Balance', 'Value': f"{original_balance:.6f} ALGO"},
            {'Metric': 'Current Balance', 'Value': f"{current_balance:.6f} ALGO"},
            {'Metric': 'Total Rewards Earned', 'Value': f"{total_rewards:.6f} ALGO"},
            {'Metric': 'Number of Rewards', 'Value': str(len(df))},
            {'Metric': 'Average Reward Size', 'Value': f"{df['amount'].mean():.6f} ALGO"},
            {'Metric': 'ROI Since Start', 'Value': f"{roi:.2f}%"},
            {'Metric': 'Avg Time Between Rewards', 'Value': f"{avg_time_between.total_seconds() / 3600:.1f} hours"},
        ])
        st.dataframe(metrics_df, hide_index=True)

# Node status details
st.subheader("🖥️ Node Status")
if node_status:
    status_df = pd.DataFrame([
        {'Metric': 'Online Status', 'Value': 'Online' if node_status['is_online'] else 'Offline'},
        {'Metric': 'Current Round', 'Value': f"{node_status['current_round']:,}"},
        {'Metric': 'Participation Keys', 'Value': 'Present' if node_status['participation_key_present'] else 'Not Found'},
        {'Metric': 'Time Remaining', 'Value': node_status['time_remaining']},
        {'Metric': 'Last Updated', 'Value': datetime.fromisoformat(node_status['timestamp']).strftime('%Y-%m-%d %H:%M:%S')},
    ])
    st.dataframe(status_df, hide_index=True)

# Add refresh button
if st.button("🔄 Refresh Data"):
    st.experimental_rerun() 