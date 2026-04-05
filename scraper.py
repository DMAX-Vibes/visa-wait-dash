#!/usr/bin/env python3
"""
Scrapes U.S. State Department Global Visa Wait Times and outputs data.json.
Run: python scraper.py
"""

import json, re, sys
from datetime import datetime, timezone
import requests
from bs4 import BeautifulSoup

URL = "https://travel.state.gov/content/travel/en/us-visas/visa-information-resources/global-visa-wait-times.html"

# Coordinates for every embassy / consulate post
COORDS = {
    "Abidjan": [5.3544, -4.0080], "Abu Dhabi": [24.4539, 54.3773],
    "Abuja": [9.0765, 7.3986], "Accra": [5.6037, -0.1870],
    "Adana": [37.0000, 35.3213], "Addis Ababa": [9.0300, 38.7400],
    "Algiers": [36.7538, 3.0588], "Almaty": [43.2220, 76.8512],
    "Amman": [31.9454, 35.9284], "Amsterdam": [52.3676, 4.9041],
    "Ankara": [39.9334, 32.8597], "Antananarivo": [-18.9137, 47.5361],
    "Apia": [-13.8333, -171.8333], "Ashgabat": [37.9601, 58.3261],
    "Asmara": [15.3229, 38.9251], "Astana": [51.1801, 71.4460],
    "Asuncion": [-25.2867, -57.6470], "Athens": [37.9838, 23.7275],
    "Auckland": [-36.8485, 174.7633], "Baghdad": [33.3152, 44.3661],
    "Baku": [40.4093, 49.8671], "Bamako": [12.6392, -8.0029],
    "Bandar Seri Begawan": [4.9031, 114.9398], "Bangkok": [13.7563, 100.5018],
    "Bangui": [4.3612, 18.5550], "Banjul": [13.4549, -16.5790],
    "Barcelona": [41.3851, 2.1734], "Beijing": [39.9042, 116.4074],
    "Beirut": [33.8938, 35.5018], "Belfast": [54.5973, -5.9301],
    "Belgrade": [44.8176, 20.4569], "Belmopan": [17.2500, -88.7667],
    "Berlin": [52.5200, 13.4050], "Bern": [46.9481, 7.4474],
    "Bishkek": [42.8746, 74.5698], "Bogota": [4.7110, -74.0721],
    "Brasilia": [-15.7801, -47.9292], "Bratislava": [48.1486, 17.1077],
    "Brazzaville": [-4.2694, 15.2712], "Bridgetown": [13.1132, -59.5988],
    "Brussels": [50.8503, 4.3517], "Bucharest": [44.4268, 26.1025],
    "Budapest": [47.4979, 19.0402], "Buenos Aires": [-34.6037, -58.3816],
    "Bujumbura": [-3.3822, 29.3644], "Cairo": [30.0444, 31.2357],
    "Calgary": [51.0447, -114.0719], "Canberra": [-35.2809, 149.1300],
    "Cape Town": [-33.9249, 18.4241], "Caracas": [10.4806, -66.9036],
    "Casablanca": [33.5731, -7.5898], "Chengdu": [30.5728, 104.0668],
    "Chennai (Madras)": [13.0827, 80.2707], "Chiang Mai": [18.7883, 98.9853],
    "Chisinau": [47.0105, 28.8638], "Ciudad Juarez": [31.7400, -106.4870],
    "Colombo": [6.9271, 79.8612], "Conakry": [9.5370, -13.6773],
    "Copenhagen": [55.6761, 12.5683], "Cotonou": [6.3654, 2.4183],
    "Curacao": [12.1696, -68.9900], "Dakar": [14.7167, -17.4677],
    "Damascus": [33.5138, 36.2765], "Dar Es Salaam": [-6.7924, 39.2083],
    "Department": [38.8951, -77.0364], "Dhahran": [26.2978, 50.1545],
    "Dhaka": [23.8103, 90.4125], "Dili": [-8.5569, 125.5789],
    "Djibouti": [11.5720, 43.1451], "Doha": [25.2854, 51.5310],
    "Dubai": [25.2048, 55.2708], "Dublin": [53.3498, -6.2603],
    "Durban": [-29.8587, 31.0218], "Dushanbe": [38.5598, 68.7870],
    "Edinburgh": [55.9533, -3.1883], "Erbil": [36.1901, 44.0091],
    "Florence": [43.7696, 11.2558], "Frankfurt": [50.1109, 8.6821],
    "Freetown": [8.4657, -13.2317], "Fukuoka": [33.5904, 130.4017],
    "Gaborone": [-24.6282, 25.9231], "Georgetown": [6.8013, -58.1551],
    "Guadalajara": [20.6597, -103.3496], "Guangzhou": [23.1291, 113.2644],
    "Guatemala City": [14.6349, -90.5069], "Guayaquil": [-2.1700, -79.9224],
    "Halifax": [44.6488, -63.5752], "Hamilton": [32.2942, -64.7839],
    "Hanoi": [21.0285, 105.8542], "Harare": [-17.8252, 31.0335],
    "Havana": [23.1136, -82.3666], "Helsinki": [60.1699, 24.9384],
    "Hermosillo": [29.0729, -110.9559], "Ho Chi Minh City": [10.8231, 106.6297],
    "Hong Kong": [22.3193, 114.1694], "Hyderabad": [17.3850, 78.4867],
    "Islamabad": [33.7294, 73.0931], "Istanbul": [41.0082, 28.9784],
    "Jakarta": [-6.2088, 106.8456], "Jeddah": [21.5433, 39.1728],
    "Jerusalem": [31.7683, 35.2137], "Johannesburg": [-26.2041, 28.0473],
    "Juba": [4.8594, 31.5713], "Kabul": [34.5553, 69.2075],
    "Kampala": [0.3476, 32.5825], "Kaohsiung": [22.6273, 120.3014],
    "Karachi": [24.8607, 67.0011], "Kathmandu": [27.7172, 85.3240],
    "Khartoum": [15.5007, 32.5599], "Kigali": [-1.9441, 30.0619],
    "Kingston": [17.9714, -76.7920], "Kinshasa": [-4.4419, 15.2663],
    "Kolkata": [22.5726, 88.3639], "Kolonia": [6.9647, 158.2085],
    "Koror": [7.3419, 134.4792], "Krakow": [50.0647, 19.9450],
    "Kuala Lumpur": [3.1390, 101.6869], "Kuwait": [29.3759, 47.9774],
    "Kyiv": [50.4501, 30.5234], "La Paz": [-16.5000, -68.1500],
    "Lagos": [6.5244, 3.3792], "Lahore": [31.5497, 74.3436],
    "Libreville": [0.4162, 9.4673], "Lilongwe": [-13.9626, 33.7741],
    "Lima": [-12.0464, -77.0428], "Lisbon": [38.7223, -9.1393],
    "Ljubljana": [46.0569, 14.5058], "Lome": [6.1375, 1.2123],
    "London": [51.5074, -0.1278], "Luanda": [-8.8368, 13.2343],
    "Lusaka": [-15.3875, 28.3228], "Luxembourg": [49.6116, 6.1319],
    "Madrid": [40.4168, -3.7038], "Majuro": [7.0897, 171.3803],
    "Malabo": [3.7500, 8.7833], "Managua": [12.1364, -86.2514],
    "Manama": [26.2235, 50.5876], "Manila": [14.5995, 120.9842],
    "Maputo": [-25.9692, 32.5732], "Marseille": [43.2965, 5.3698],
    "Maseru": [-29.3142, 27.4833], "Matamoros": [25.8694, -97.5027],
    "Mbabane": [-26.3054, 31.1367], "Melbourne": [-37.8136, 144.9631],
    "Merida": [20.9674, -89.5926], "Mexicali Tpf": [32.6245, -115.4523],
    "Mexico City": [19.4326, -99.1332], "Milan": [45.4654, 9.1859],
    "Minsk": [53.9045, 27.5615], "Monrovia": [6.3106, -10.8047],
    "Monterrey": [25.6866, -100.3161], "Montevideo": [-34.9011, -56.1645],
    "Montreal": [45.5017, -73.5673], "Moscow": [55.7558, 37.6173],
    "Mumbai (Bombay)": [19.0760, 72.8777], "Munich": [48.1351, 11.5820],
    "Muscat": [23.5880, 58.3829], "N`Djamena": [12.1048, 15.0440],
    "Naha": [26.2124, 127.6792], "Nairobi": [-1.2921, 36.8219],
    "Naples": [40.8518, 14.2681], "Nassau": [25.0443, -77.3504],
    "New Delhi": [28.6139, 77.2090], "Niamey": [13.5137, 2.1098],
    "Nicosia": [35.1856, 33.3823], "Nogales": [31.3000, -110.9400],
    "Nouakchott": [18.0858, -15.9785], "Nuevo Laredo": [27.4863, -99.5182],
    "Osaka/Kobe": [34.6937, 135.5022], "Oslo": [59.9139, 10.7522],
    "Ottawa": [45.4215, -75.6972], "Ouagadougou": [12.3642, -1.5330],
    "Panama City": [8.9936, -79.5197], "Paramaribo": [5.8664, -55.1668],
    "Paris": [48.8566, 2.3522], "Perth": [-31.9505, 115.8605],
    "Phnom Penh": [11.5564, 104.9282], "Podgorica": [42.4304, 19.2594],
    "Ponta Delgada": [37.7412, -25.6756], "Port Au Prince": [18.5432, -72.3388],
    "Port Louis": [-20.1654, 57.4896], "Port Moresby": [-9.4438, 147.1803],
    "Port Of Spain": [10.6549, -61.5019], "Porto Alegre": [-30.0346, -51.2177],
    "Prague": [50.0755, 14.4378], "Praia": [14.9315, -23.5136],
    "Pretoria": [-25.7479, 28.2293], "Pristina": [42.6629, 21.1655],
    "Quebec": [46.8139, -71.2082], "Quito": [-0.1807, -78.4678],
    "Rangoon": [16.8661, 96.1951], "Recife": [-8.0476, -34.8770],
    "Reykjavik": [64.1355, -21.8954], "Riga": [56.9460, 24.1059],
    "Rio De Janeiro": [-22.9068, -43.1729], "Riyadh": [24.7136, 46.6753],
    "Rome": [41.9028, 12.4964], "San Jose": [9.9281, -84.0907],
    "San Salvador": [13.6929, -89.2182], "Sanaa": [15.3694, 44.1910],
    "Santiago": [-33.4489, -70.6693], "Santo Domingo": [18.4861, -69.9312],
    "Sao Paulo": [-23.5505, -46.6333], "Sapporo": [43.0618, 141.3545],
    "Seoul": [37.5665, 126.9780], "Shanghai": [31.2304, 121.4737],
    "Singapore": [1.3521, 103.8198], "Skopje": [41.9973, 21.4280],
    "Sofia": [42.6977, 23.3219], "St. Petersburg": [59.9311, 30.3609],
    "Stockholm": [59.3293, 18.0686], "Surabaya": [-7.2575, 112.7521],
    "Suva": [-18.1248, 178.4501], "Sydney": [-33.8688, 151.2093],
    "Taipei": [25.0330, 121.5654], "Tallinn": [59.4370, 24.7536],
    "Tashkent": [41.2995, 69.2401], "Tbilisi": [41.6938, 44.8015],
    "Tegucigalpa": [14.0723, -87.2020], "Tehran": [35.6892, 51.3890],
    "Tel Aviv": [32.0853, 34.7818], "Tirana": [41.3275, 19.8187],
    "Tokyo": [35.6762, 139.6503], "Toronto": [43.6532, -79.3832],
    "Tripoli": [32.9022, 13.1800], "Tunis": [36.8065, 10.1815],
    "Ulaanbaatar": [47.8864, 106.9057], "Vancouver": [49.2827, -123.1207],
    "Vienna": [48.2082, 16.3738], "Vientiane": [17.9757, 102.6331],
    "Vilnius": [54.6872, 25.2797], "Warsaw": [52.2297, 21.0122],
    "Wellington": [-41.2866, 174.7756], "Windhoek": [-22.5597, 17.0832],
    "Yaounde": [3.8480, 11.5021], "Yerevan": [40.1872, 44.5152],
    "Zagreb": [45.8150, 15.9819], "Zurich": [47.3769, 8.5417],
}

def parse_wait(text):
    text = (text or "").strip()
    if not text or text.upper() in ("NA", "N/A"):
        return None
    if text.startswith("<"):
        return 0.25   # displayed as "< 0.5 mo"
    m = re.search(r"(\d+(?:\.\d+)?)", text)
    return float(m.group(1)) if m else None

def scrape():
    resp = requests.get(URL, headers={"User-Agent": "Mozilla/5.0"}, timeout=30)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")

    table = soup.find("table")
    if not table:
        print("ERROR: table not found", file=sys.stderr); sys.exit(1)

    # Extract "Last updated" date from page text
    m = re.search(r"Last updated:\s*([^\n<]+)", soup.get_text(), re.I)
    last_updated = m.group(1).strip() if m else "Unknown"

    posts = []
    missing_coords = []
    for row in table.find_all("tr")[1:]:
        cells = row.find_all("td")
        if len(cells) < 5:
            continue
        name = cells[0].get_text(strip=True)
        coords = COORDS.get(name)
        if not coords:
            missing_coords.append(name)
            coords = [0, 0]

        posts.append({
            "name":      name,
            "lat":       coords[0],
            "lng":       coords[1],
            "b1b2_avg":  parse_wait(cells[1].get_text(strip=True)),
            "b1b2_next": parse_wait(cells[2].get_text(strip=True)),
            "fmj_next":  parse_wait(cells[3].get_text(strip=True)),
            "hlopq_next":parse_wait(cells[4].get_text(strip=True)),
            "cd_next":   parse_wait(cells[5].get_text(strip=True)) if len(cells) > 5 else None,
        })

    if missing_coords:
        print(f"WARNING: no coords for: {', '.join(missing_coords)}", file=sys.stderr)

    return {
        "last_updated": last_updated,
        "scraped_at":   datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "posts":        posts,
    }

if __name__ == "__main__":
    result = scrape()
    with open("data.json", "w") as f:
        json.dump(result, f, indent=2)
    print(f"✓ {len(result['posts'])} posts → data.json  |  Source last updated: {result['last_updated']}")
