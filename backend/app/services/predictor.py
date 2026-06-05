import pandas as pd
import numpy as np
import joblib
import os
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

model       = joblib.load(os.path.join(BASE_DIR, "data/models/waste_model.pkl"))
le_bin      = joblib.load(os.path.join(BASE_DIR, "data/models/le_bin.pkl"))
le_neighbor = joblib.load(os.path.join(BASE_DIR, "data/models/le_neighborhood.pkl"))
FEATURES    = joblib.load(os.path.join(BASE_DIR, "data/models/features.pkl"))

bins_df      = pd.read_csv(os.path.join(BASE_DIR, "data/raw/bins.csv"))
processed_df = pd.read_csv(os.path.join(BASE_DIR, "data/processed/processed_data.csv"))

MARKET_BINS = ["BIN003","BIN006","BIN011","BIN015","BIN021","BIN022","BIN023","BIN027"]

def predict_waste_levels(hour=None, day_of_week=None):
    now = datetime.now()
    hour        = hour        if hour        is not None else now.hour
    day_of_week = day_of_week if day_of_week is not None else now.weekday()
    month       = now.month
    week        = now.isocalendar()[1]
    is_weekend  = int(day_of_week >= 5)
    time_of_day = 0 if hour < 6 else 1 if hour < 12 else 2 if hour < 18 else 3

    hourly_avg = (
        processed_df.groupby(["bin_id", "hour"])["waste_level_kg"]
        .mean().reset_index()
        .rename(columns={"waste_level_kg": "avg_waste_by_hour"})
    )
    daily_avg = (
        processed_df.groupby(["bin_id", "day_of_week"])["waste_level_kg"]
        .mean().reset_index()
        .rename(columns={"waste_level_kg": "avg_waste_by_day"})
    )
    collection_counts = (
        pd.read_csv(os.path.join(BASE_DIR, "data/raw/collection_history.csv"))
        .groupby("bin_id").size().reset_index()
        .rename(columns={0: "total_collections"})
    )

    results = []
    for _, bin_row in bins_df.iterrows():
        bin_id       = bin_row["bin_id"]
        neighborhood = bin_row["neighborhood"]
        is_market    = int(bin_id in MARKET_BINS)

        h_avg = hourly_avg[
            (hourly_avg["bin_id"] == bin_id) &
            (hourly_avg["hour"]   == hour)
        ]["avg_waste_by_hour"]
        avg_by_hour = float(h_avg.values[0]) if len(h_avg) > 0 else 0.5

        d_avg = daily_avg[
            (daily_avg["bin_id"]      == bin_id) &
            (daily_avg["day_of_week"] == day_of_week)
        ]["avg_waste_by_day"]
        avg_by_day = float(d_avg.values[0]) if len(d_avg) > 0 else 0.5

        total_col = collection_counts[
            collection_counts["bin_id"] == bin_id
        ]["total_collections"]
        total_collections = float(total_col.values[0]) if len(total_col) > 0 else 0

        try:
            bin_enc = int(le_bin.transform([bin_id])[0])
        except:
            bin_enc = 0
        try:
            nbr_enc = int(le_neighbor.transform([neighborhood])[0])
        except:
            nbr_enc = 0

        features = {
            "bin_id_encoded"       : bin_enc,
            "neighborhood_encoded" : nbr_enc,
            "lat"                  : float(bin_row["lat"]),
            "lon"                  : float(bin_row["lon"]),
            "capacity_kg"          : float(bin_row["capacity_kg"]),
            "day_of_week"          : day_of_week,
            "hour"                 : hour,
            "month"                : month,
            "week_of_year"         : week,
            "is_weekend"           : is_weekend,
            "time_of_day"          : time_of_day,
            "is_market_area"       : is_market,
            "avg_waste_by_hour"    : avg_by_hour,
            "avg_waste_by_day"     : avg_by_day,
            "total_collections"    : total_collections
        }

        X = pd.DataFrame([features])[FEATURES]
        predicted_fill = float(model.predict(X)[0])
        predicted_fill = max(0, min(predicted_fill, 100))

        results.append({
            "bin_id"          : bin_id,
            "name"            : bin_row["name"],
            "neighborhood"    : neighborhood,
            "lat"             : float(bin_row["lat"]),
            "lon"             : float(bin_row["lon"]),
            "capacity_kg"     : float(bin_row["capacity_kg"]),
            "predicted_fill"  : round(predicted_fill, 1),
            "needs_collection": predicted_fill >= 60,
            "is_market_area"  : bool(is_market)
        })

    return results