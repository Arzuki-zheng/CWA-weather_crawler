import requests
import sqlite3

URL = "https://opendata.cwa.gov.tw/api/v1/rest/datastore/F-D0047-073?Authorization=CWA-1F9282FA-261E-43EB-BEF0-B06D9F66AD23&format=JSON"

# === 1. 抓 API JSON ===
res = requests.get(URL)
data = res.json()

# records -> Locations(list) -> [0] -> Location(list)
locations_block_list = data["records"]["Locations"]
first_block = locations_block_list[0]
location_list = first_block["Location"]

print("地點數量:", len(location_list))

rows = []  # 要寫進 SQLite 的所有列

# === 2. 解析每個地點的所有時間點 ===
for loc in location_list:
    loc_name = loc["LocationName"]              # 例如「中區」
    weather_elements = loc["WeatherElement"]    # 溫度、濕度、天氣 等

    elem_map = {e["ElementName"]: e for e in weather_elements}

    temp_elem = elem_map.get("溫度")
    rh_elem   = elem_map.get("相對濕度")
    wx_elem   = elem_map.get("天氣描述") or elem_map.get("天氣") or elem_map.get("天氣現象")

    if not temp_elem:
        continue  # 沒有溫度就跳過

    # 以「溫度」的 Time 當主時間軸
    for t in temp_elem.get("Time", []):
        datatime = t["DataTime"]

        # 溫度：ElementValue[0]["Temperature"]
        temperature = None
        tev = t.get("ElementValue", [])
        if isinstance(tev, list) and tev:
            temperature = tev[0].get("Temperature")

        # 濕度：找相同 DataTime
        humidity = None
        if rh_elem:
            for ht in rh_elem.get("Time", []):
                if ht.get("DataTime") == datatime:
                    hev = ht.get("ElementValue", [])
                    if isinstance(hev, list) and hev:
                        humidity = hev[0].get("RelativeHumidity")
                    break

        # 天氣描述
        weather_desc = None
        if wx_elem:
            for wt in wx_elem.get("Time", []):
                if wt.get("DataTime") == datatime:
                    wv = wt.get("ElementValue", [])
                    if isinstance(wv, list) and wv:
                        weather_desc = (
                            wv[0].get("WeatherDescription")
                            or wv[0].get("Weather")
                        )
                    break

        rows.append((loc_name, datatime, temperature, humidity, weather_desc))

print("解析完成，準備寫入 SQLite，總列數:", len(rows))

# === 3. 砍舊表 + 重建正確 schema + 寫入 ===
conn = sqlite3.connect("data.db")
cur = conn.cursor()

# 直接砍掉舊的 weather 表，避免舊欄位影響
cur.execute("DROP TABLE IF EXISTS weather")

cur.execute("""
CREATE TABLE weather (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    location TEXT,
    datatime TEXT,
    temperature TEXT,
    humidity TEXT,
    weather_desc TEXT
)
""")

cur.executemany(
    "INSERT INTO weather (location, datatime, temperature, humidity, weather_desc) VALUES (?, ?, ?, ?, ?)",
    rows
)

conn.commit()
conn.close()

print("寫入完成！")
