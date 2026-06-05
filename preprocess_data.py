import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
import os

print("🔄 Starting data preprocessing...\n")

# ── 1. LOAD RAW DATA ──────────────────────────────────────────────────────────
bins_df = pd.read_csv("data/raw/bins.csv")
waste_df = pd.read_csv("data/raw/waste_levels.csv")
collections_df = pd.read_csv("data/raw/collection_history.csv")

print(f"✅ Loaded bins.csv        — {len(bins_df)} rows")
print(f"✅ Loaded waste_levels.csv — {len(waste_df)} rows")
print(f"✅ Loaded collection_history.csv — {len(collections_df)} rows")

# ── 2. CLEAN WASTE LEVELS ─────────────────────────────────────────────────────
# Convert timestamp to datetime
waste_df["timestamp"] = pd.to_datetime(waste_df["timestamp"])

# Drop duplicates
waste_df.drop_duplicates(inplace=True)

# Drop rows with missing values
waste_df.dropna(inplace=True)

# Remove impossible values (negative or above capacity)
waste_df = waste_df[waste_df["waste_level_kg"] >= 0]
waste_df = waste_df[waste_df["fill_percentage"] <= 100]

print(f"\n✅ After cleaning — {len(waste_df)} waste level records remain")

# ── 3. FEATURE ENGINEERING ────────────────────────────────────────────────────
print("\n🔧 Engineering features...")

# Time-based features
waste_df["day_of_week"]   = waste_df["timestamp"].dt.dayofweek
waste_df["hour"]          = waste_df["timestamp"].dt.hour
waste_df["month"]         = waste_df["timestamp"].dt.month
waste_df["week_of_year"]  = waste_df["timestamp"].dt.isocalendar().week.astype(int)
waste_df["is_weekend"]    = (waste_df["day_of_week"] >= 5).astype(int)

# Time of day category
def time_of_day(hour):
    if hour < 6:
        return 0   # night
    elif hour < 12:
        return 1   # morning
    elif hour < 18:
        return 2   # afternoon
    else:
        return 3   # evening

waste_df["time_of_day"] = waste_df["hour"].apply(time_of_day)

# ── 4. HISTORICAL AVERAGES ────────────────────────────────────────────────────
print("🔧 Computing historical averages...")

# Average waste level per bin per hour
hourly_avg = (
    waste_df.groupby(["bin_id", "hour"])["waste_level_kg"]
    .mean()
    .reset_index()
    .rename(columns={"waste_level_kg": "avg_waste_by_hour"})
)

# Average waste level per bin per day of week
daily_avg = (
    waste_df.groupby(["bin_id", "day_of_week"])["waste_level_kg"]
    .mean()
    .reset_index()
    .rename(columns={"waste_level_kg": "avg_waste_by_day"})
)

# Merge averages back into main dataframe
waste_df = waste_df.merge(hourly_avg, on=["bin_id", "hour"], how="left")
waste_df = waste_df.merge(daily_avg,  on=["bin_id", "day_of_week"], how="left")

# ── 5. MERGE WITH BIN INFO ────────────────────────────────────────────────────
print("🔧 Merging with bin metadata...")

waste_df = waste_df.merge(
    bins_df[["bin_id", "lat", "lon", "capacity_kg", "neighborhood"]],
    on="bin_id",
    how="left",
    suffixes=("", "_bin")
)

# Drop duplicate is_market_area column if exists
if "is_market_area_bin" in waste_df.columns:
    waste_df.drop(columns=["is_market_area_bin"], inplace=True)

# ── 6. COLLECTION FREQUENCY PER BIN ──────────────────────────────────────────
print("🔧 Computing collection frequency...")

collection_counts = (
    collections_df.groupby("bin_id")
    .size()
    .reset_index()
    .rename(columns={0: "total_collections"})
)

waste_df = waste_df.merge(collection_counts, on="bin_id", how="left")
waste_df["total_collections"].fillna(0, inplace=True)

# ── 7. NORMALIZE NUMERICAL FEATURES ──────────────────────────────────────────
print("🔧 Normalizing features...")

scaler = MinMaxScaler()
cols_to_scale = [
    "waste_level_kg",
    "avg_waste_by_hour",
    "avg_waste_by_day",
    "lat",
    "lon",
    "total_collections"
]

waste_df[cols_to_scale] = scaler.fit_transform(waste_df[cols_to_scale])

# ── 8. SELECT FINAL FEATURES ──────────────────────────────────────────────────
final_columns = [
    "bin_id",
    "timestamp",
    "neighborhood",
    "lat",
    "lon",
    "capacity_kg",
    "waste_level_kg",
    "fill_percentage",
    "day_of_week",
    "hour",
    "month",
    "week_of_year",
    "is_weekend",
    "time_of_day",
    "is_market_area",
    "avg_waste_by_hour",
    "avg_waste_by_day",
    "total_collections"
]

processed_df = waste_df[final_columns].copy()

# ── 9. SAVE OUTPUT ────────────────────────────────────────────────────────────
os.makedirs("data/processed", exist_ok=True)
processed_df.to_csv("data/processed/processed_data.csv", index=False)

print(f"\n✅ processed_data.csv saved — {len(processed_df)} rows")
print(f"   Features: {len(final_columns)} columns")

# ── 10. SUMMARY REPORT ────────────────────────────────────────────────────────
print("\n📊 PREPROCESSING SUMMARY")
print(f"   Total records     : {len(processed_df)}")
print(f"   Unique bins       : {processed_df['bin_id'].nunique()}")
print(f"   Neighborhoods     : {processed_df['neighborhood'].nunique()}")
print(f"   Date range        : {processed_df['timestamp'].min()} → {processed_df['timestamp'].max()}")
print(f"   Avg fill level    : {processed_df['fill_percentage'].mean():.1f}%")
print(f"   Market area bins  : {processed_df[processed_df['is_market_area']==1]['bin_id'].nunique()}")
print("\n✅ Preprocessing complete!")