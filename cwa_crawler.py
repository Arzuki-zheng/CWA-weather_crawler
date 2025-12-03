import requests, sqlite3

URL="https://opendata.cwa.gov.tw/api/v1/rest/datastore/F-D0047-073?Authorization=CWA-1F9282FA-261E-43EB-BEF0-B06D9F66AD23&format=JSON"
data=requests.get(URL).json()

loc_list=data["records"]["Locations"][0]["Location"]

def first_value(elem):  # 取第一個時間區間的值
    t=elem.get("Time",[])
    if not t: return None
    v=t[0]["ElementValue"]
    return v[0]["Value"] if isinstance(v,list) else v["Value"]

rows=[]
for loc in loc_list:
    name=loc["LocationName"]
    elems={e["ElementName"]:e for e in loc["WeatherElement"]}
    minT=first_value(elems.get("MinT",{}))
    maxT=first_value(elems.get("MaxT",{}))
    desc=first_value(elems.get("WeatherDescription",{}))
    rows.append((name,minT,maxT,desc))

conn=sqlite3.connect("data.db")
cur=conn.cursor()
cur.execute("""CREATE TABLE IF NOT EXISTS weather(
 id INTEGER PRIMARY KEY AUTOINCREMENT,
 location TEXT, min_temp TEXT, max_temp TEXT, description TEXT)""")
cur.execute("DELETE FROM weather")
cur.executemany("INSERT INTO weather(location,min_temp,max_temp,description) VALUES (?,?,?,?)", rows)
conn.commit(); conn.close()
print(f"Inserted {len(rows)} rows.")
