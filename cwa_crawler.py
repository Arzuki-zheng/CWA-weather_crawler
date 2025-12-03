import requests
import sqlite3

# === 1. 抓 CWA API JSON ===
URL = "https://opendata.cwa.gov.tw/api/v1/rest/datastore/F-D0047-073?Authorization=CWA-1F9282FA-261E-43EB-BEF0-B06D9F66AD23&format=JSON"

res = requests.get(URL)
data = res.json()

# 檢查基本結構
records = data["records"]
locations_root = records["Locations"]          # 這是 list
first_block = locations_root[0]                # 只有一個 block，裡面有很多 Location
loc_list = first_block["Location"]             # 這才是每個地點的 list

print("地點數量:", len(loc_list))

# === 2. 工具函式：取「第一個有值」的 ElementValue ===
def get_first_nonempty_value(elem_dict):
    """從某個 WeatherElement 裡面，找第一個有值的時間區間"""
    if not elem_dict:
        return None
    times = elem_dict.get("Time", [])
    for t in times:
        v = t.get("ElementValue", [])
        if isinstance(v, list):
            if not v:
                continue
            value = v[0].get("Value")
        else:
            value = v.get("Value")
        if value not in (None, "", " "):
            return value
    return None

rows = []

# === 3. 解析每個地點，整理要寫進 SQLite 的欄位 ===
for loc in loc_list:
    location_name = loc["LocationName"]          # 地點名稱（中文）
    elements = loc["WeatherElement"]             # 各種氣象元素 list

    # 轉成 dict，方便用 ElementName 查
    elem_map = {e["ElementName"]: e for e in elements}

    min_temp = get_first_nonempty_value(elem_map.get("MinT"))
    max_temp = get_first_nonempty_value(elem_map.get("MaxT"))
    description = get_first_nonempty_value(elem_map.get("WeatherDescription"))

    rows.append((location_name, min_temp, max_temp, description))

print("準備寫入 SQLite，筆數:", len(rows))

# === 4. 寫入 SQLite data.db ===
conn = sqlite3.connect("data.db")
cur = conn.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS weather (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    location TEXT,
    min_temp TEXT,
    max_temp TEXT,
    description TEXT
)
""")

# 清空舊資料，避免重複
cur.execute("DELETE FROM weather")

# 批次寫入
cur.executemany(
    "INSERT INTO weather (location, min_temp, max_temp, description) VALUES (?, ?, ?, ?)",
    rows
)

conn.commit()
conn.close()

print("寫入完成！")
