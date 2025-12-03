CWA Weather Crawler + SQLite + Streamlit
目的：從中央氣象署 API 抓取 JSON，解析欄位，寫入 SQLite，並用 Streamlit 顯示結果。

專案結構
cwa_crawler.py：抓取與寫入 SQLite

app.py：Streamlit 讀取 SQLite 並顯示

data.db：SQLite 資料庫（執行後產生）

使用步驟
建立環境

Python 3.11

pip install requests pandas streamlit

抓取與寫入 SQLite

python cwa_crawler.py

終端會顯示 Inserted N rows（預期約 29 筆）

檢查資料

可用 DB Browser 或:

python -c "import sqlite3; c=sqlite3.connect('data.db'); print(c.execute('select count(*) from weather').fetchone()); c.close()"

啟動 Streamlit

streamlit run app.py

瀏覽器查看表格與簡單統計並截圖

主要程式說明
API：F-D0047-073（36 小時區域天氣）

JSON 路徑：records → Locations → Location (list)

取用欄位：

location: LocationName

min_temp: WeatherElement["MinT"] 第 1 筆時間區間的 Value

max_temp: WeatherElement["MaxT"] 第 1 筆時間區間的 Value

description: WeatherElement["WeatherDescription"] 第 1 筆 Value

資料表結構
CREATE TABLE IF NOT EXISTS weather (
id INTEGER PRIMARY KEY AUTOINCREMENT,
location TEXT,
min_temp TEXT,
max_temp TEXT,
description TEXT
);

備註：官方 JSON 中 ElementValue 可能為 list 或單一物件，程式已處理取第一筆時間區間值。

交付內容

weather crawler 原始碼（cwa_crawler.py）

SQLite DB（data.db）

Streamlit 原始碼（app.py）

Streamlit 截圖（顯示資料表）