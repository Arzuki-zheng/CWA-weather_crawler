import streamlit as st
import sqlite3
import pandas as pd

st.title("🌤️ 台灣各地天氣預報 (SQLite Demo)")

# 讀 SQLite
conn = sqlite3.connect("data.db")
df = pd.read_sql("SELECT location, datatime, temperature, humidity, weather_desc FROM weather", conn)
conn.close()

# 顯示原始表格
st.subheader("📋 天氣資料表")
st.dataframe(df, use_container_width=True)

# 把溫度轉成數值才能算最大/最小
df_num = df.copy()
df_num["temperature"] = pd.to_numeric(df_num["temperature"], errors="coerce")

col1, col2 = st.columns(2)
col1.metric("最高溫", f"{df_num['temperature'].max()} ℃")
col2.metric("最低溫", f"{df_num['temperature'].min()} ℃")

st.markdown("資料來源: 中央氣象局開放資料平臺（F-D0047-073）")
