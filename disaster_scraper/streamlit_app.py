import streamlit as st
import pandas as pd
import os
from datetime import datetime
import subprocess
from io import BytesIO
import xlsxwriter
from fpdf import FPDF

DATA_PATH = "data/disaster_news.csv"
SCRAPER_SCRIPT = "scraper/main.py"

st.set_page_config(page_title="Disaster News Monitor", layout="wide")
st.title("🌪️ Disaster News Monitor")
st.markdown("Tracking natural disasters in Mexico and Central America from various news sources.")

if st.button("🔄 Refresh News (Run Scraper)"):
    with st.spinner("Running scraper..."):
        try:
            subprocess.run(["python", SCRAPER_SCRIPT], check=True)
            st.success("Scraper completed successfully.")
        except Exception as e:
            st.error(f"Scraper failed: {e}")

if not os.path.exists(DATA_PATH):
    st.warning("No data file found. Run the scraper first.")
    st.stop()

df = pd.read_csv(DATA_PATH)
df.drop_duplicates(subset='url', inplace=True)

if 'scraped_at' not in df.columns:
    df['scraped_at'] = datetime.today().strftime('%Y-%m-%d')

df['scraped_at'] = pd.to_datetime(df['scraped_at'], errors='coerce')

with st.sidebar:
    st.header("🔍 Filter Articles")
    keyword = st.text_input("Keyword search").lower()
    sources = sorted(set(df['url'].str.extract(r'https?://(?:www\.)?([^/]+)')[0].dropna()))
    selected_sources = st.multiselect("News Sources", options=sources, default=sources)
    min_date, max_date = df['scraped_at'].min(), df['scraped_at'].max()
    start_date, end_date = st.date_input("Scrape Date Range", value=(min_date, max_date), min_value=min_date, max_value=max_date)
    tag_options = sorted(df['disaster_type'].dropna().unique())
    selected_tags = st.multiselect("Disaster Type", tag_options, default=tag_options)

filtered_df = df.copy()

if keyword:
    filtered_df = filtered_df[filtered_df['title'].str.lower().str.contains(keyword)]
if selected_sources:
    filtered_df = filtered_df[filtered_df['url'].str.contains('|'.join(selected_sources))]
filtered_df = filtered_df[
    (filtered_df['scraped_at'] >= pd.to_datetime(start_date)) &
    (filtered_df['scraped_at'] <= pd.to_datetime(end_date))
]
if selected_tags:
    filtered_df = filtered_df[filtered_df['disaster_type'].isin(selected_tags)]

st.subheader(f"📰 {len(filtered_df)} articles found")
for _, row in filtered_df.iterrows():
    st.markdown(f"**[{row['title']}]({row['url']})**  — *{row['scraped_at'].date()}*  — 🏷️ `{row['disaster_type']}`")

st.sidebar.header("📤 Export Results")

def convert_to_excel(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='DisasterNews')
    output.seek(0)
    return output

def convert_to_pdf(df):
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    for _, row in df.iterrows():
        pdf.multi_cell(0, 10, f"{row['title']}\n{row['url']}\n{row['scraped_at'].date()}\n", border=0)
        pdf.ln()
    pdf_output = BytesIO()
    pdf.output(pdf_output)
    pdf_output.seek(0)
    return pdf_output

export_format = st.sidebar.radio("Export Format", ["Excel", "PDF"])
if st.sidebar.button("📥 Download Filtered Results"):
    if len(filtered_df) == 0:
        st.sidebar.warning("No data to export.")
    else:
        if export_format == "Excel":
            st.download_button("Download Excel", data=convert_to_excel(filtered_df), file_name="disaster_news.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        elif export_format == "PDF":
            st.download_button("Download PDF", data=convert_to_pdf(filtered_df), file_name="disaster_news.pdf", mime="application/pdf")
