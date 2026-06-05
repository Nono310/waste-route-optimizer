import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os

np.random.seed(42)

# ── 1. BIN LOCATIONS ACROSS BUEA ──────────────────────────────────────────────
bins_data = [
    {"bin_id": "BIN001", "name": "Molyko Junction",        "lat": 4.1527, "lon": 9.2916, "capacity_kg": 100, "neighborhood": "Molyko"},
    {"bin_id": "BIN002", "name": "UB Main Gate",           "lat": 4.1545, "lon": 9.2933, "capacity_kg": 120, "neighborhood": "Molyko"},
    {"bin_id": "BIN003", "name": "Molyko Market",          "lat": 4.1511, "lon": 9.2901, "capacity_kg": 150, "neighborhood": "Molyko"},
    {"bin_id": "BIN004", "name": "Bonduma Center",         "lat": 4.1476, "lon": 9.2856, "capacity_kg": 100, "neighborhood": "Bonduma"},
    {"bin_id": "BIN005", "name": "Bonduma Health Center",  "lat": 4.1489, "lon": 9.2871, "capacity_kg": 80,  "neighborhood": "Bonduma"},
    {"bin_id": "BIN006", "name": "Great Soppo Market",     "lat": 4.1432, "lon": 9.2801, "capacity_kg": 150, "neighborhood": "Great Soppo"},
    {"bin_id": "BIN007", "name": "Great Soppo Junction",   "lat": 4.1418, "lon": 9.2789, "capacity_kg": 100, "neighborhood": "Great Soppo"},
    {"bin_id": "BIN008", "name": "Small Soppo Center",     "lat": 4.1398, "lon": 9.2754, "capacity_kg": 80,  "neighborhood": "Small Soppo"},
    {"bin_id": "BIN009", "name": "Small Soppo School",     "lat": 4.1411, "lon": 9.2768, "capacity_kg": 80,  "neighborhood": "Small Soppo"},
    {"bin_id": "BIN010", "name": "Mile 16 Junction",       "lat": 4.1601, "lon": 9.2698, "capacity_kg": 120, "neighborhood": "Mile 16"},
    {"bin_id": "BIN011", "name": "Mile 16 Market",         "lat": 4.1589, "lon": 9.2712, "capacity_kg": 150, "neighborhood": "Mile 16"},
    {"bin_id": "BIN012", "name": "Bokwango Road",          "lat": 4.1367, "lon": 9.2845, "capacity_kg": 80,  "neighborhood": "Bokwango"},
    {"bin_id": "BIN013", "name": "Bokwango Village",       "lat": 4.1351, "lon": 9.2832, "capacity_kg": 80,  "neighborhood": "Bokwango"},
    {"bin_id": "BIN014", "name": "Clerks Quarter",         "lat": 4.1556, "lon": 9.2978, "capacity_kg": 100, "neighborhood": "Clerks Quarter"},
    {"bin_id": "BIN015", "name": "Clerks Quarter Market",  "lat": 4.1567, "lon": 9.2991, "capacity_kg": 120, "neighborhood": "Clerks Quarter"},
    {"bin_id": "BIN016", "name": "Federal Quarter",        "lat": 4.1623, "lon": 9.3012, "capacity_kg": 100, "neighborhood": "Federal Quarter"},
    {"bin_id": "BIN017", "name": "Federal Quarter Park",   "lat": 4.1638, "lon": 9.3028, "capacity_kg": 80,  "neighborhood": "Federal Quarter"},
    {"bin_id": "BIN018", "name": "GRA Junction",           "lat": 4.1578, "lon": 9.3045, "capacity_kg": 120, "neighborhood": "GRA"},
    {"bin_id": "BIN019", "name": "GRA Market",             "lat": 4.1591, "lon": 9.3061, "capacity_kg": 100, "neighborhood": "GRA"},
    {"bin_id": "BIN020", "name": "Sandpit Junction",       "lat": 4.1445, "lon": 9.3089, "capacity_kg": 80,  "neighborhood": "Sandpit"},
    {"bin_id": "BIN021", "name": "Sandpit Market",         "lat": 4.1458, "lon": 9.3102, "capacity_kg": 100, "neighborhood": "Sandpit"},
    {"bin_id": "BIN022", "name": "Buea Town Hall",         "lat": 4.1534, "lon": 9.3134, "capacity_kg": 150, "neighborhood": "Buea Town"},
    {"bin_id": "BIN023", "name": "Buea Town Market",       "lat": 4.1521, "lon": 9.3118, "capacity_kg": 150, "neighborhood": "Buea Town"},
    {"bin_id": "BIN024", "name": "Wokoko Junction",        "lat": 4.1489, "lon": 9.3156, "capacity_kg": 100, "neighborhood": "Wokoko"},
    {"bin_id": "BIN025", "name": "Wokoko Center",          "lat": 4.1501, "lon": 9.3171, "capacity_kg": 80,  "neighborhood": "Wokoko"},
    {"bin_id": "BIN026", "name": "Lysoka Junction",        "lat": 4.1712, "lon": 9.2823, "capacity_kg": 100, "neighborhood": "Lysoka"},
    {"bin_id": "BIN027", "name": "Lysoka Market",          "lat": 4.1698, "lon": 9.2809, "capacity_kg": 120, "neighborhood": "Lysoka"},
    {"bin_id": "BIN028", "name": "Tole Junction",          "lat": 4.1334, "lon": 9.2712, "capacity_kg": 80,  "neighborhood": "Tole"},
    {"bin_id": "BIN029", "name": "Tole Tea Estate",        "lat": 4.1318, "lon": 9.2698, "capacity_kg": 80,  "neighborhood": "Tole"},
    {"bin_id": "BIN030", "name": "Camp Sic Junction",      "lat": 4.1623, "lon": 9.2945, "capacity_kg": 100, "neighborhood": "Camp Sic"},
]

bins_df = pd.DataFrame(bins_data)
bins_df.to_csv("data/raw/bins.csv", index=False)
print(f"✅ bins.csv created — {len(bins_df)} bins across Buea")

# ── 2. WASTE LEVELS ───────────────────────────────────────────────────────────
# Readings every 6 hours for 90 days
start_date = datetime(2024, 1, 1)
records = []

# Bins near markets fill faster
market_bins = ["BIN003", "BIN006", "BIN011", "BIN015", "BIN021", "BIN022", "BIN023", "BIN027"]

for bin_info in bins_data:
    bin_id = bin_info["bin_id"]
    capacity = bin_info["capacity_kg"]
    is_market = bin_id in market_bins

    current_level = np.random.uniform(10, 30)  # starting level

    for day in range(90):
        for hour in [0, 6, 12, 18]:
            timestamp = start_date + timedelta(days=day, hours=hour)
            day_of_week = timestamp.weekday()  # 0=Monday, 6=Sunday
            is_weekend = day_of_week >= 5

            # Fill rate depends on time of day, day of week, bin type
            base_fill = np.random.uniform(2, 6)
            if is_market:
                base_fill *= 1.6
            if is_weekend:
                base_fill *= 1.3
            if hour == 12:  # midday peak
                base_fill *= 1.4
            if hour == 18:  # evening peak
                base_fill *= 1.2

            current_level = min(current_level + base_fill, capacity)

            # Add some noise
            noise = np.random.normal(0, 1.5)
            reported_level = max(0, min(current_level + noise, capacity))

            records.append({
                "bin_id": bin_id,
                "timestamp": timestamp.strftime("%Y-%m-%d %H:%M:%S"),
                "waste_level_kg": round(reported_level, 2),
                "capacity_kg": capacity,
                "fill_percentage": round((reported_level / capacity) * 100, 1),
                "day_of_week": day_of_week,
                "hour": hour,
                "is_weekend": int(is_weekend),
                "is_market_area": int(is_market)
            })

            # Reset level after collection (if > 80% full, collection likely)
            if current_level >= capacity * 0.80:
                current_level = np.random.uniform(5, 15)

waste_df = pd.DataFrame(records)
waste_df.to_csv("data/raw/waste_levels.csv", index=False)
print(f"✅ waste_levels.csv created — {len(waste_df)} records")

# ── 3. COLLECTION HISTORY ─────────────────────────────────────────────────────
collections = []
collection_id = 1

for bin_id in [b["bin_id"] for b in bins_data]:
    bin_waste = waste_df[waste_df["bin_id"] == bin_id]

    # Find timestamps where fill % was high (simulating collection events)
    high_fill = bin_waste[bin_waste["fill_percentage"] >= 78].copy()

    for _, row in high_fill.iterrows():
        collections.append({
            "collection_id": f"COL{collection_id:04d}",
            "bin_id": bin_id,
            "collection_time": row["timestamp"],
            "waste_collected_kg": round(row["waste_level_kg"], 2),
            "truck_id": f"TRUCK{np.random.randint(1, 5):02d}",
            "driver": np.random.choice(["Emmanuel", "Paul", "Grace", "Peter", "Mary"]),
            "status": "completed"
        })
        collection_id += 1

collections_df = pd.DataFrame(collections)
collections_df.to_csv("data/raw/collection_history.csv", index=False)
print(f"✅ collection_history.csv created — {len(collections_df)} collection events")

print("\n📊 DATASET SUMMARY")
print(f"   Bins: {len(bins_df)}")
print(f"   Waste level readings: {len(waste_df)}")
print(f"   Collection events: {len(collections_df)}")
print(f"\n   Neighborhoods covered:")
for n in sorted(bins_df['neighborhood'].unique()):
    count = len(bins_df[bins_df['neighborhood'] == n])
    print(f"   - {n}: {count} bin(s)")