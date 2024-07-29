import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import time
from datetime import datetime, timedelta

# Set up Streamlit page config
st.set_page_config(page_title="Crypto Momentum Plot", layout="wide")

# CSV file path
CSV_FILE_PATH = "momentum_scores.csv"

# Symbols to plot
SYMBOLS = ["BTCUSDT.P", "COMBOUSDT.P"]

@st.cache_data(ttl=300)  # Cache for 5 minutes
def get_historical_data():
    df = pd.read_csv(CSV_FILE_PATH, parse_dates=['Timestamp'])
    df['Timestamp'] = pd.to_datetime(df['Timestamp'], utc=True)
    return df[
        (df['Timestamp'] >= datetime.now(df['Timestamp'].dt.tz) - timedelta(hours=24)) &
        (df['Symbol'].isin(SYMBOLS))
    ].sort_values('Timestamp', ascending=False)

@st.cache_data(ttl=300)  # Cache for 5 minutes
def get_average_momentum():
    df = pd.read_csv(CSV_FILE_PATH, parse_dates=['Timestamp'])
    df['Timestamp'] = pd.to_datetime(df['Timestamp'], utc=True)
    return df[df['Timestamp'] >= datetime.now(df['Timestamp'].dt.tz) - timedelta(hours=24)].groupby('Timestamp')['Momentum Score'].mean().reset_index().sort_values('Timestamp', ascending=False)

def update_plot(df, avg_df, hours_to_display):
    # Filter data based on selected time range
    end_time = df['Timestamp'].max()
    start_time = end_time - timedelta(hours=hours_to_display)
    df_filtered = df[df['Timestamp'] >= start_time]
    avg_df_filtered = avg_df[avg_df['Timestamp'] >= start_time]
    
    fig = go.Figure()
    
    # Plot individual symbol momentum scores
    colors = ['blue', 'green']
    for i, symbol in enumerate(SYMBOLS):
        symbol_data = df_filtered[df_filtered['Symbol'] == symbol]
        fig.add_trace(go.Scatter(
            x=symbol_data['Timestamp'],
            y=symbol_data['Momentum Score'],
            mode='lines',
            name=symbol,
            line=dict(color=colors[i], width=2),
            hovertemplate=f"{symbol}: %{{y:.2f}}<extra></extra>"
        ))
        
        # Add yellow dot to the latest plot point
        fig.add_trace(go.Scatter(
            x=[symbol_data['Timestamp'].iloc[-1]],
            y=[symbol_data['Momentum Score'].iloc[-1]],
            mode='markers',
            marker=dict(color='yellow', size=10, line=dict(color=colors[i], width=2)),
            showlegend=False,
            hoverinfo='skip'
        ))
    
    # Plot color-coded average momentum
    avg_momentum = avg_df_filtered['Momentum Score']
    for i in range(1, len(avg_momentum)):
        start = avg_df_filtered['Timestamp'].iloc[i-1]
        end = avg_df_filtered['Timestamp'].iloc[i]
        y1 = avg_momentum.iloc[i-1]
        y2 = avg_momentum.iloc[i]
        
        if y1 > 0.5 and y2 > 0.5:
            color = 'green'
        elif y1 < -0.5 and y2 < -0.5:
            color = 'red'
        elif -0.5 <= y1 <= 0.5 and -0.5 <= y2 <= 0.5:
            color = 'grey'
        else:
            if y2 > 0.5:
                color = 'green'
            elif y2 < -0.5:
                color = 'red'
            else:
                color = 'grey'
        
        fig.add_trace(go.Scatter(
            x=[start, end],
            y=[y1, y2],
            mode='lines',
            line=dict(color=color, width=2),
            showlegend=False,
            hovertemplate="Average: %{y:.2f}<extra></extra>"
        ))
    
    # Add a legend entry for Average Total Momentum Scores
    fig.add_trace(go.Scatter(
        x=[None],
        y=[None],
        mode='lines',
        name='Average Total Momentum Scores',
        line=dict(color='blue', width=2)
    ))
    
    # Add yellow dot to the latest average momentum point
    fig.add_trace(go.Scatter(
        x=[avg_df_filtered['Timestamp'].iloc[-1]],
        y=[avg_momentum.iloc[-1]],
        mode='markers',
        marker=dict(color='yellow', size=10, line=dict(color='blue', width=2)),
        showlegend=False,
        hoverinfo='skip'
    ))
    
    fig.add_hline(y=0, line_dash="dash", line_color="black")
    
    fig.update_layout(
        title='Crypto Market Momentum Plot',
        xaxis_title='Timestamp (UTC)',
        yaxis_title='Momentum Score',
        yaxis_range=[-2, 2],
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        height=600,
        hovermode="x unified"
    )
    
    return fig

def main():
    st.title('Crypto Market Momentum Plot')
    
    # Add a slider for selecting the time range
    hours_to_display = st.slider("Select time range to display (hours)", min_value=1, max_value=24, value=6, step=1)
    
    plot_placeholder = st.empty()
    
    while True:
        try:
            # Get data
            df = get_historical_data()
            avg_df = get_average_momentum()
            
            # Update plot
            fig = update_plot(df, avg_df, hours_to_display)
            plot_placeholder.plotly_chart(fig, use_container_width=True)
            
            # Display last update time
            st.text(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} UTC")
            
            # Sleep for 3 minutes before the next update
            time.sleep(180)
            
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")
            time.sleep(120)  # Wait 2 minutes before retrying

if __name__ == "__main__":
    main()