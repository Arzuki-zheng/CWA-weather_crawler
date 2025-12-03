import streamlit as st
import sqlite3
import pandas as pd

st.title("🌤️ 台灣各地天氣預報 (SQLite Demo)")

# 讀 SQLite
conn = sqlite3.connect("data.db")
df = pd.read_sql("SELECT * FROM weather LIMIT 20", conn)
conn.close()

st.dataframe(df, use_container_width=True)

col1, col2 = st.columns(2)
col1.metric("最高溫", df['max_temp'].dropna().max())
col2.metric("最低溫", df['min_temp'].dropna().min())
st.markdown("資料來源: [中央氣象局開放資料平臺](https://opendata.cwa.gov.tw/dataset/forecast)")
