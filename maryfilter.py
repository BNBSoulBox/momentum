import streamlit as st
import pandas as pd
from datetime import datetime, timezone, timedelta
import time
import logging
import os

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# CSV file path
CSV_FILE_PATH = "momentum_scores.csv"

# Set the page config
st.set_page_config(
    page_title="Momentum Score Dashboard",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for dark theme and styles
st.markdown("""
    <style>
    .css-18e3th9 {
        background-color: #0e1117;
        color: #ffffff;
    }
    .css-1lcbmhc {
        background-color: #161a25;
    }
    .css-1d391kg {
        color: #ffffff;
    }
    .stButton>button {
        color: #ffffff;
        background-color: #d4af37;
        border-color: #d4af37;
    }
    .css-1offfwp e1h7wlp60 {
        color: #ffffff;
    }
    </style>
    """, unsafe_allow_html=True)

# List of symbols (kept the same)
symbols = [
    "10000LADYSUSDT.P", "10000NFTUSDT.P", "1000BONKUSDT.P", "1000BTTUSDT.P", 
    "1000FLOKIUSDT.P", "1000LUNCUSDT.P", "1000PEPEUSDT.P", "1000XECUSDT.P", 
    "1INCHUSDT.P", "AAVEUSDT.P", "ACHUSDT.P", "ADAUSDT.P", "AGLDUSDT.P", 
    "AKROUSDT.P", "ALGOUSDT.P", "ALICEUSDT.P", "ALPACAUSDT.P", 
    "ALPHAUSDT.P", "AMBUSDT.P", "ANKRUSDT.P", "ANTUSDT.P", 
    "APEUSDT.P", "API3USDT.P", "APTUSDT.P", "ARUSDT.P", "ARBUSDT.P", "ARKUSDT.P", 
    "ARKMUSDT.P", "ARPAUSDT.P", "ASTRUSDT.P", "ATAUSDT.P", "ATOMUSDT.P", 
    "AUCTIONUSDT.P", "AUDIOUSDT.P", "AVAXUSDT.P", "AXSUSDT.P", "BADGERUSDT.P", 
    "BAKEUSDT.P", "BALUSDT.P", "BANDUSDT.P", "BATUSDT.P", "BCHUSDT.P", 
    "BELUSDT.P", "BICOUSDT.P", "BIGTIMEUSDT.P", "BLURUSDT.P", "BLZUSDT.P",
    "BTCUSDT.P", "C98USDT.P", "CEEKUSDT.P", "CELOUSDT.P", "CELRUSDT.P", "CFXUSDT.P",
    "CHRUSDT.P", "CHZUSDT.P", "CKBUSDT.P", "COMBOUSDT.P", "COMPUSDT.P",
    "COREUSDT.P", "COTIUSDT.P", "CROUSDT.P", "CRVUSDT.P", "CTCUSDT.P",
    "CTKUSDT.P", "CTSIUSDT.P", "CVCUSDT.P", "CVXUSDT.P", "CYBERUSDT.P", "DARUSDT.P",
    "DASHUSDT.P", "DENTUSDT.P", "DGBUSDT.P", "DODOUSDT.P", "DOGEUSDT.P", "DOTUSDT.P",
    "DUSKUSDT.P", "DYDXUSDT.P", "EDUUSDT.P", "EGLDUSDT.P", "ENJUSDT.P", "ENSUSDT.P",
    "EOSUSDT.P", "ETCUSDT.P", "ETHUSDT.P", "ETHWUSDT.P", "FILUSDT.P",
    "FITFIUSDT.P", "FLOWUSDT.P", "FLRUSDT.P", "FORTHUSDT.P", "FRONTUSDT.P", "FTMUSDT.P",
    "FXSUSDT.P", "GALAUSDT.P", "GFTUSDT.P", "GLMUSDT.P",
    "GLMRUSDT.P", "GMTUSDT.P", "GMXUSDT.P", "GRTUSDT.P", "GTCUSDT.P", "HBARUSDT.P", 
    "HFTUSDT.P", "HIFIUSDT.P", "HIGHUSDT.P", "HNTUSDT.P",
    "HOOKUSDT.P", "HOTUSDT.P", "ICPUSDT.P", "ICXUSDT.P", "IDUSDT.P", "IDEXUSDT.P",
    "ILVUSDT.P", "IMXUSDT.P", "INJUSDT.P", "IOSTUSDT.P", "IOTAUSDT.P", "IOTXUSDT.P",
    "JASMYUSDT.P", "JOEUSDT.P", "JSTUSDT.P", "KASUSDT.P", "KAVAUSDT.P", "KDAUSDT.P",
    "KEYUSDT.P", "KLAYUSDT.P", "KNCUSDT.P", "KSMUSDT.P", "LDOUSDT.P", "LEVERUSDT.P",
    "LINAUSDT.P", "LINKUSDT.P", "LITUSDT.P", "LOOKSUSDT.P", "LOOMUSDT.P", "LPTUSDT.P",
    "LQTYUSDT.P", "LRCUSDT.P", "LTCUSDT.P", "LUNA2USDT.P", "MAGICUSDT.P",
    "MANAUSDT.P", "MASKUSDT.P", "MATICUSDT.P", "MAVUSDT.P", "MDTUSDT.P",
    "MINAUSDT.P", "MKRUSDT.P", "MNTUSDT.P", "MTLUSDT.P", "NEARUSDT.P",
    "NEOUSDT.P", "NKNUSDT.P", "NMRUSDT.P", "NTRNUSDT.P", "OGUSDT.P",
    "OGNUSDT.P", "OMGUSDT.P", "ONEUSDT.P", "ONTUSDT.P", "OPUSDT.P", "ORBSUSDT.P",
    "ORDIUSDT.P", "OXTUSDT.P", "PAXGUSDT.P", "PENDLEUSDT.P", "PEOPLEUSDT.P", "PERPUSDT.P",
    "PHBUSDT.P", "PROMUSDT.P", "QNTUSDT.P", "QTUMUSDT.P", "RADUSDT.P", "RDNTUSDT.P", 
    "REEFUSDT.P", "RENUSDT.P", "REQUSDT.P", "RLCUSDT.P", "ROSEUSDT.P", 
    "RPLUSDT.P", "RSRUSDT.P", "RSS3USDT.P", "RUNEUSDT.P", "RVNUSDT.P",
    "SANDUSDT.P", "SCUSDT.P", "SCRTUSDT.P", "SEIUSDT.P", "SFPUSDT.P", "SHIB1000USDT.P",
    "SKLUSDT.P", "SLPUSDT.P", "SNXUSDT.P", "SOLUSDT.P", "SPELLUSDT.P", "SSVUSDT.P", 
    "STGUSDT.P", "STMXUSDT.P", "STORJUSDT.P", "STPTUSDT.P", "STXUSDT.P", "SUIUSDT.P", 
    "SUNUSDT.P", "SUSHIUSDT.P", "SWEATUSDT.P", "SXPUSDT.P",
    "TUSDT.P", "THETAUSDT.P", "TLMUSDT.P", "TOMIUSDT.P", "TONUSDT.P",
    "TRBUSDT.P", "TRUUSDT.P", "TRXUSDT.P", "TWTUSDT.P", "UMAUSDT.P", "UNFIUSDT.P",
    "UNIUSDT.P", "USDCUSDT.P", "VETUSDT.P", "VGXUSDT.P", "VRAUSDT.P",
    "WAVESUSDT.P", "WAXPUSDT.P", "WLDUSDT.P", "WOOUSDT.P", "XCNUSDT.P",
    "XEMUSDT.P", "XLMUSDT.P", "XMRUSDT.P", "XNOUSDT.P", "XRPUSDT.P", "XTZUSDT.P",
    "XVGUSDT.P", "XVSUSDT.P", "YFIUSDT.P", "YGGUSDT.P", "ZECUSDT.P", "ZENUSDT.P", "ZILUSDT.P", "ZRXUSDT.P"
]

@st.cache_data(ttl=120)
def get_historical_data():
    if not os.path.exists(CSV_FILE_PATH):
        return pd.DataFrame(columns=['Symbol', 'Momentum Score', 'Timestamp'])
    
    df = pd.read_csv(CSV_FILE_PATH, parse_dates=['Timestamp'])
    df['Timestamp'] = pd.to_datetime(df['Timestamp'], utc=True)
    
    # Filter for last 24 hours
    last_24_hours = datetime.now(timezone.utc) - timedelta(hours=24)
    df = df[df['Timestamp'] >= last_24_hours]
    
    return df.sort_values('Timestamp', ascending=False)

def display_top_20_scores(results, historical_df):
    sorted_results = sorted(results, key=lambda x: x['Momentum Score'], reverse=True)
    
    long_df = pd.DataFrame(sorted_results[:20])
    short_df = pd.DataFrame(sorted_results[-20:][::-1])
    
    for df in [long_df, short_df]:
        if not df.empty:
            df['Previous Score'] = df['Symbol'].map(historical_df.set_index('Symbol')['Momentum Score'].to_dict())
            df['Change'] = df['Momentum Score'] - df['Previous Score'].fillna(0)
            df['Momentum Score'] = df['Momentum Score'].round(2)
            df['Change'] = df['Change'].round(2)
    
    return long_df, short_df

def display_filtered_scores(results, historical_df):
    df = pd.DataFrame(results)
    df['Previous Score'] = df['Symbol'].map(historical_df.set_index('Symbol')['Momentum Score'].to_dict())
    df['Change'] = df['Momentum Score'] - df['Previous Score'].fillna(0)
    df['Momentum Score'] = df['Momentum Score'].round(2)
    df['Change'] = df['Change'].round(2)
    
    positive_filter = (df['Momentum Score'].between(0.1, 0.4)) & (df['Change'].between(1.1, 1.5))
    negative_filter = (df['Momentum Score'].between(-0.4, -0.1)) & (df['Change'].between(-1.5, -1.1))
    
    positive_df = df[positive_filter].sort_values('Change', ascending=False)
    negative_df = df[negative_filter].sort_values('Change', ascending=True)
    
    return positive_df, negative_df

@st.cache_data(ttl=120)
def identify_momentum_crossovers(df):
    avg_momentum = df['Momentum Score'].mean()

    df['Previous Score'] = df.groupby('Symbol')['Momentum Score'].shift(1)
    df['Crossed Up'] = (df['Previous Score'] < avg_momentum) & (df['Momentum Score'] >= avg_momentum)
    df['Crossed Down'] = (df['Previous Score'] > avg_momentum) & (df['Momentum Score'] <= avg_momentum)

    crossed_up = df[df['Crossed Up']].sort_values('Momentum Score', ascending=False)
    crossed_down = df[df['Crossed Down']].sort_values('Momentum Score', ascending=True)

    return crossed_up, crossed_down, avg_momentum

def main():
    st.title('Momentum Score Dashboard')
    
    col1, col2, col3 = st.columns(3)
    
    long_scores_placeholder = col1.empty()
    short_scores_placeholder = col1.empty()
    
    metrics_placeholder = col2.empty()
    
    positive_filter_placeholder = col3.empty()
    negative_filter_placeholder = col3.empty()
    
    crossover_placeholder = st.empty()
    
    while True:
        try:
            # Read existing data from CSV
            df = get_historical_data()
            historical_df = df[['Symbol', 'Momentum Score']].copy()
            
            # Get the latest results
            latest_results = df[df['Timestamp'] == df['Timestamp'].max()].to_dict('records')
            
            # Display top 20 scores
            long_df, short_df = display_top_20_scores(latest_results, historical_df)
            
            # Display filtered scores
            positive_df, negative_df = display_filtered_scores(latest_results, historical_df)
            
            # Identify momentum crossovers
            crossed_up, crossed_down, avg_momentum = identify_momentum_crossovers(df)
            
            # Update the placeholders with the latest data
            with long_scores_placeholder.container():
                st.subheader("Top 20 Long Momentum Scores:")
                st.dataframe(long_df[['Symbol', 'Momentum Score', 'Change']])
            
            with short_scores_placeholder.container():
                st.subheader("Top 20 Short Momentum Scores:")
                st.dataframe(short_df[['Symbol', 'Momentum Score', 'Change']])
            
            with metrics_placeholder.container():
                avg_change_long = long_df['Change'].mean()
                avg_change_short = short_df['Change'].mean()
                st.metric("Avg Change in Top 20 Long Scores", f"{avg_change_long:.2f}", f"{avg_change_long:.2f}")
                st.metric("Avg Change in Top 20 Short Scores", f"{avg_change_short:.2f}", f"{avg_change_short:.2f}")
                st.metric("Average Momentum Score", f"{avg_momentum:.2f}")
            
            with positive_filter_placeholder.container():
                st.subheader("Symbols with Momentum 0.1 to 0.4 & Change 1.1 to 1.5:")
                st.dataframe(positive_df[['Symbol', 'Momentum Score', 'Change']])
            
            with negative_filter_placeholder.container():
                st.subheader("Symbols with Momentum -0.4 to -0.1 & Change -1.5 to -1.1:")
                st.dataframe(negative_df[['Symbol', 'Momentum Score', 'Change']])
            
            with crossover_placeholder.container():
                col1, col2 = st.columns(2)
                with col1:
                    st.subheader("Symbols Crossing Above Average Momentum:")
                    st.dataframe(crossed_up[['Symbol', 'Momentum Score', 'Previous Score']])
                with col2:
                    st.subheader("Symbols Crossing Below Average Momentum:")
                    st.dataframe(crossed_down[['Symbol', 'Momentum Score', 'Previous Score']])
            
            # Sleep for 2 minutes before the next update
            time.sleep(120)
            
        except Exception as e:
            logging.error(f"An error occurred: {str(e)}")
            st.error(f"An error occurred: {str(e)}")
            time.sleep(300)  # Wait 5 minutes before retrying

if __name__ == "__main__":
    main()