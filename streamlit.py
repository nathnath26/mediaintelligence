import streamlit as st
import pandas as pd
import plotly.express as px

# Set page configuration
st.set_page_config(layout="wide", page_title="Interactive Media Intelligence Dashboard")

# --- Styling ---
def local_css(file_name):
    with open(file_name) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

# You can create a style.css file for more advanced styling if needed
# For now, we'll use Streamlit's built-in capabilities and some custom CSS via markdown
st.markdown("""
<style>
    .main {
        background-color: #FFF7F9;
    }
    .st-emotion-cache-16txtl3 {
        padding-top: 2rem;
    }
    h1 {
        color: #D946EF;
        text-align: center;
    }
    .stButton>button {
        background: linear-gradient(90deg, #F472B6, #EC4899);
        color: white;
        border-radius: 0.5rem;
        padding: 0.75rem 1.5rem;
        border: none;
    }
    .stButton>button:hover {
        opacity: 0.9;
        color: white;
    }
</style>
""", unsafe_allow_html=True)


# --- Data Cleaning Function ---
@st.cache_data
def clean_data(df):
    """Cleans and preprocesses the uploaded dataframe."""
    # Convert 'Date' column to datetime objects, coercing errors to NaT
    df['Date'] = pd.to_datetime(df['Date'], errors='coerce')

    # Convert 'Engagements' to numeric, coercing errors to NaN, then fill NaNs with 0
    df['Engagements'] = pd.to_numeric(df['Engagements'], errors='coerce').fillna(0)
    
    # Drop rows where Date could not be parsed
    df.dropna(subset=['Date'], inplace=True)
    
    # Ensure column types are correct
    df['Engagements'] = df['Engagements'].astype(int)
    df['Platform'] = df['Platform'].astype(str).fillna('Unknown')
    df['Sentiment'] = df['Sentiment'].astype(str).fillna('Unknown')
    df['Media Type'] = df['Media Type'].astype(str).fillna('Unknown')
    df['Location'] = df['Location'].astype(str).fillna('Unknown')

    return df

# --- Main App Logic ---

# Initialize session state for data persistence
if 'df' not in st.session_state:
    st.session_state.df = None

# --- UI: File Uploader View ---
if st.session_state.df is None:
    st.title("Interactive Media Intelligence Dashboard")
    
    upload_container = st.container()
    with upload_container:
        st.markdown('<div style="text-align: center;">', unsafe_allow_html=True)
        st.subheader("Unggah File CSV Anda")
        st.write("Silakan unggah file CSV yang berisi data intelijen media Anda. Pastikan memiliki kolom untuk 'Date', 'Engagements', 'Sentiment', 'Platform', 'Media Type', dan 'Location'.")
        
        uploaded_file = st.file_uploader("Pilih File", type="csv", label_visibility="collapsed")
        
        if uploaded_file is not None:
            try:
                df = pd.read_csv(uploaded_file)
                st.session_state.df = clean_data(df)
                st.rerun() # Rerun the script to move to the dashboard view
            except Exception as e:
                st.error(f"Error: Gagal memproses file. Pastikan formatnya benar. Detail: {e}")
        st.markdown('</div>', unsafe_allow_html=True)

# --- UI: Dashboard View ---
else:
    df = st.session_state.df
    st.title("Media Intelligence Dashboard")

    # --- Sidebar for Filters ---
    st.sidebar.header("Saring Data")
    
    # Reset Button
    if st.sidebar.button("Unggah File Baru"):
        st.session_state.df = None
        st.rerun()

    # Platform Filter
    unique_platforms = ['All'] + sorted(df['Platform'].unique().tolist())
    platform = st.sidebar.selectbox("Platform", unique_platforms)

    # Sentiment Filter
    unique_sentiments = ['All'] + sorted(df['Sentiment'].unique().tolist())
    sentiment = st.sidebar.selectbox("Sentimen", unique_sentiments)
    
    # Media Type Filter
    unique_media_types = ['All'] + sorted(df['Media Type'].unique().tolist())
    media_type = st.sidebar.selectbox("Jenis Media", unique_media_types)
    
    # Location Filter
    unique_locations = ['All'] + sorted(df['Location'].unique().tolist())
    location = st.sidebar.selectbox("Lokasi", unique_locations)

    # Date Range Filter
    min_date = df['Date'].min().date()
    max_date = df['Date'].max().date()
    start_date = st.sidebar.date_input("Tanggal Mulai", min_date, min_value=min_date, max_value=max_date)
    end_date = st.sidebar.date_input("Tanggal Berakhir", max_date, min_value=min_date, max_value=max_date)

    # --- Filtering Logic ---
    filtered_df = df[
        (df['Date'].dt.date >= start_date) & 
        (df['Date'].dt.date <= end_date)
    ]
    if platform != 'All':
        filtered_df = filtered_df[filtered_df['Platform'] == platform]
    if sentiment != 'All':
        filtered_df = filtered_df[filtered_df['Sentiment'] == sentiment]
    if media_type != 'All':
        filtered_df = filtered_df[filtered_df['Media Type'] == media_type]
    if location != 'All':
        filtered_df = filtered_df[filtered_df['Location'] == location]

    # --- Dashboard Content ---
    
    # Key Action Summary
    st.markdown("### Ringkasan Strategi Kampanye")
    st.info("""
    Berdasarkan analisis sentimen dan engagement, kampanye yang berfokus pada konten visual di Instagram & TikTok terbukti efektif. Optimalkan postingan pada jam puncak untuk jangkauan maksimal dan pertimbangkan kolaborasi dengan influencer lokal di lokasi dengan interaksi tertinggi.
    """)

    if filtered_df.empty:
        st.warning("Tidak ada data yang cocok dengan filter yang dipilih. Harap sesuaikan filter Anda.")
    else:
        # --- Charting Section ---
        col1, col2 = st.columns(2)

        with col1:
            # Sentiment Breakdown
            st.markdown("#### Sentiment Breakdown")
            sentiment_counts = filtered_df['Sentiment'].value_counts()
            fig_sentiment = px.pie(
                sentiment_counts, 
                values=sentiment_counts.values, 
                names=sentiment_counts.index, 
                hole=0.4,
                color_discrete_sequence=px.colors.sequential.RdBu
            )
            fig_sentiment.update_layout(showlegend=True)
            st.plotly_chart(fig_sentiment, use_container_width=True)

            # Platform Engagements
            st.markdown("#### Platform Engagements")
            platform_engagements = filtered_df.groupby('Platform')['Engagements'].sum().sort_values(ascending=False)
            fig_platform = px.bar(
                platform_engagements, 
                x=platform_engagements.index, 
                y=platform_engagements.values,
                labels={'y': 'Total Engagements', 'x': 'Platform'}
            )
            st.plotly_chart(fig_platform, use_container_width=True)

        with col2:
            # Engagement Trend over Time
            st.markdown("#### Engagement Trend over Time")
            engagement_by_date = filtered_df.groupby(filtered_df['Date'].dt.date)['Engagements'].sum()
            fig_engagement = px.line(
                engagement_by_date, 
                x=engagement_by_date.index, 
                y=engagement_by_date.values,
                labels={'y': 'Total Engagements', 'x': 'Date'}
            )
            fig_engagement.update_traces(mode='lines+markers')
            st.plotly_chart(fig_engagement, use_container_width=True)

            # Media Type Mix
            st.markdown("#### Media Type Mix")
            media_type_counts = filtered_df['Media Type'].value_counts()
            fig_media_type = px.pie(
                media_type_counts, 
                values=media_type_counts.values, 
                names=media_type_counts.index, 
                hole=0.4,
                color_discrete_sequence=px.colors.sequential.Agsunset
            )
            st.plotly_chart(fig_media_type, use_container_width=True)

        # Top 5 Locations (Full Width)
        st.markdown("#### Top 5 Locations by Post Count")
        location_counts = filtered_df['Location'].value_counts().nlargest(5)
        fig_location = px.bar(
            location_counts,
            x=location_counts.index,
            y=location_counts.values,
            labels={'y': 'Number of Posts', 'x': 'Location'}
        )
        st.plotly_chart(fig_location, use_container_width=True)

