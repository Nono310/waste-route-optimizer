import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "backend"))

from app.db.database import engine, SessionLocal
from app.db.models import Base, Bin
import pandas as pd

print("🗄️  Setting up database...\n")

# ── 1. CREATE ALL TABLES ──────────────────────────────────────────────────────
Base.metadata.create_all(bind=engine)
print("✅ Tables created:")
print("   - bins")
print("   - waste_readings")
print("   - community_reports")
print("   - routes")

# ── 2. POPULATE BINS TABLE ────────────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
bins_df  = pd.read_csv(os.path.join(BASE_DIR, "data/raw/bins.csv"))

MARKET_BINS = [
    "BIN003","BIN006","BIN011","BIN015",
    "BIN021","BIN022","BIN023","BIN027"
]

db = SessionLocal()

# Clear existing bins
db.query(Bin).delete()
db.commit()

# Insert bins from CSV
count = 0
for _, row in bins_df.iterrows():
    bin_record = Bin(
        bin_id         = row["bin_id"],
        name           = row["name"],
        neighborhood   = row["neighborhood"],
        lat            = row["lat"],
        lon            = row["lon"],
        capacity_kg    = row["capacity_kg"],
        is_market_area = row["bin_id"] in MARKET_BINS,
        is_active      = True
    )
    db.add(bin_record)
    count += 1

db.commit()
db.close()

print(f"\n✅ Populated bins table — {count} bins inserted")

# ── 3. VERIFY ─────────────────────────────────────────────────────────────────
db = SessionLocal()
total_bins   = db.query(Bin).count()
market_bins  = db.query(Bin).filter(Bin.is_market_area == True).count()
db.close()

print(f"\n📊 DATABASE SUMMARY")
print(f"   Total bins    : {total_bins}")
print(f"   Market bins   : {market_bins}")
print(f"   Database file : waste_optimizer.db")
print(f"\n✅ Database setup complete!")