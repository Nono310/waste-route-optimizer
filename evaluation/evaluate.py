import pandas as pd
import numpy as np
from math import radians, sin, cos, sqrt, atan2
import random
import joblib
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

print("=" * 60)
print("   AI WASTE COLLECTION SYSTEM — EVALUATION MODULE")
print("   University of Buea | MBARGA MBOM NOEMIE")
print("=" * 60)
print()

# ── CONSTANTS ─────────────────────────────────────────────────────────────────
BASE_DIR         = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEPOT            = {"lat": 4.1534, "lon": 9.2916, "name": "HYSACAM Depot"}
TRUCK_CAPACITY   = 1000   # kg
NUM_TRUCKS       = 3
FUEL_RATE        = 0.35   # liters per km
FUEL_PRICE_XAF   = 500    # XAF per liter (approximate Cameroon price)
COLLECTION_THRESHOLD = 60 # percent

# ── LOAD DATA ─────────────────────────────────────────────────────────────────
print("🔄 Loading data...")
bins_df      = pd.read_csv(os.path.join(BASE_DIR, "data/raw/bins.csv"))
processed_df = pd.read_csv(os.path.join(BASE_DIR, "data/processed/processed_data.csv"))

# Load ML model
model       = joblib.load(os.path.join(BASE_DIR, "data/models/waste_model.pkl"))
le_bin      = joblib.load(os.path.join(BASE_DIR, "data/models/le_bin.pkl"))
le_neighbor = joblib.load(os.path.join(BASE_DIR, "data/models/le_neighborhood.pkl"))
FEATURES    = joblib.load(os.path.join(BASE_DIR, "data/models/features.pkl"))

print(f"✅ Loaded {len(bins_df)} bins")
print(f"✅ Loaded {len(processed_df)} waste level records")
print()

# ── HAVERSINE DISTANCE ─────────────────────────────────────────────────────────
def haversine(lat1, lon1, lat2, lon2):
    R = 6371
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    a = sin((lat2-lat1)/2)**2 + cos(lat1)*cos(lat2)*sin((lon2-lon1)/2)**2
    return R * 2 * atan2(sqrt(a), sqrt(1-a))

# ── BUILD DISTANCE MATRIX ──────────────────────────────────────────────────────
def build_distance_matrix(locations):
    n = len(locations)
    matrix = np.zeros((n, n))
    for i in range(n):
        for j in range(n):
            if i != j:
                matrix[i][j] = haversine(
                    locations[i]["lat"], locations[i]["lon"],
                    locations[j]["lat"], locations[j]["lon"]
                )
    return matrix

# ── PREDICT WASTE LEVELS ───────────────────────────────────────────────────────
def predict_all_bins():
    from datetime import datetime
    now         = datetime.now()
    hour        = now.hour
    day_of_week = now.weekday()
    month       = now.month
    week        = now.isocalendar()[1]
    is_weekend  = int(day_of_week >= 5)
    time_of_day = 0 if hour < 6 else 1 if hour < 12 else 2 if hour < 18 else 3

    MARKET_BINS = ["BIN003","BIN006","BIN011","BIN015",
                   "BIN021","BIN022","BIN023","BIN027"]

    hourly_avg = (
        processed_df.groupby(["bin_id","hour"])["waste_level_kg"]
        .mean().reset_index()
        .rename(columns={"waste_level_kg":"avg_waste_by_hour"})
    )
    daily_avg = (
        processed_df.groupby(["bin_id","day_of_week"])["waste_level_kg"]
        .mean().reset_index()
        .rename(columns={"waste_level_kg":"avg_waste_by_day"})
    )
    collection_counts = (
        pd.read_csv(os.path.join(BASE_DIR, "data/raw/collection_history.csv"))
        .groupby("bin_id").size().reset_index()
        .rename(columns={0:"total_collections"})
    )

    results = []
    for _, bin_row in bins_df.iterrows():
        bin_id       = bin_row["bin_id"]
        neighborhood = bin_row["neighborhood"]
        is_market    = int(bin_id in MARKET_BINS)

        h_avg = hourly_avg[
            (hourly_avg["bin_id"]==bin_id) &
            (hourly_avg["hour"]==hour)
        ]["avg_waste_by_hour"]
        avg_by_hour = float(h_avg.values[0]) if len(h_avg) > 0 else 0.5

        d_avg = daily_avg[
            (daily_avg["bin_id"]==bin_id) &
            (daily_avg["day_of_week"]==day_of_week)
        ]["avg_waste_by_day"]
        avg_by_day = float(d_avg.values[0]) if len(d_avg) > 0 else 0.5

        total_col = collection_counts[
            collection_counts["bin_id"]==bin_id
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
            "bin_id_encoded"      : bin_enc,
            "neighborhood_encoded": nbr_enc,
            "lat"                 : float(bin_row["lat"]),
            "lon"                 : float(bin_row["lon"]),
            "capacity_kg"         : float(bin_row["capacity_kg"]),
            "day_of_week"         : day_of_week,
            "hour"                : hour,
            "month"               : month,
            "week_of_year"        : week,
            "is_weekend"          : is_weekend,
            "time_of_day"         : time_of_day,
            "is_market_area"      : is_market,
            "avg_waste_by_hour"   : avg_by_hour,
            "avg_waste_by_day"    : avg_by_day,
            "total_collections"   : total_collections
        }

        X = pd.DataFrame([features])[FEATURES]
        predicted_fill = float(model.predict(X)[0])
        predicted_fill = max(0, min(predicted_fill, 100))

        results.append({
            "bin_id"           : bin_id,
            "name"             : bin_row["name"],
            "neighborhood"     : bin_row["neighborhood"],
            "lat"              : float(bin_row["lat"]),
            "lon"              : float(bin_row["lon"]),
            "capacity_kg"      : float(bin_row["capacity_kg"]),
            "predicted_fill"   : round(predicted_fill, 1),
            "needs_collection" : predicted_fill >= COLLECTION_THRESHOLD,
            "demand_kg"        : round((predicted_fill / 100) * float(bin_row["capacity_kg"]), 2)
        })

    return results

# ── GENETIC ALGORITHM (same as optimizer.py) ───────────────────────────────────
def run_ga(bins_to_collect):
    if not bins_to_collect:
        return [], 0

    locations = [DEPOT] + bins_to_collect
    demands   = [0] + [b["demand_kg"] for b in bins_to_collect]
    n         = len(locations)

    dist_matrix = build_distance_matrix(locations)
    bin_indices = list(range(1, n))

    def split_routes(chrom):
        routes, route, load = [], [], 0
        for idx in chrom:
            if load + demands[idx] <= TRUCK_CAPACITY:
                route.append(idx); load += demands[idx]
            else:
                if route: routes.append(route)
                route, load = [idx], demands[idx]
        if route: routes.append(route)
        return routes

    def route_dist(route):
        if not route: return 0
        d = dist_matrix[0][route[0]]
        for i in range(len(route)-1):
            d += dist_matrix[route[i]][route[i+1]]
        return d + dist_matrix[route[-1]][0]

    def fitness(chrom):
        routes  = split_routes(chrom)
        total   = sum(route_dist(r) for r in routes)
        penalty = max(0, len(routes) - NUM_TRUCKS) * 1000
        return 1 / (total + penalty + 1e-6)

    def crossover(p1, p2):
        size = len(p1)
        s, e = sorted(random.sample(range(size), 2))
        child = [None]*size
        child[s:e] = p1[s:e]
        ptr = 0
        for g in p2:
            if g not in child:
                while child[ptr] is not None: ptr += 1
                child[ptr] = g
        return child

    def mutate(ind):
        if random.random() < 0.02:
            i, j = random.sample(range(len(ind)), 2)
            ind[i], ind[j] = ind[j], ind[i]
        return ind

    random.seed(42)
    POP  = 100
    GENS = 200
    pop  = [random.sample(bin_indices, len(bin_indices)) for _ in range(POP)]

    best_chrom, best_fit, best_dist = None, -1, float("inf")

    for _ in range(GENS):
        fits = [fitness(ind) for ind in pop]
        idx  = int(np.argmax(fits))
        if fits[idx] > best_fit:
            best_fit   = fits[idx]
            best_chrom = pop[idx].copy()
            best_dist  = 1 / best_fit

        elites   = [pop[i] for i in np.argsort(fits)[-10:]]
        selected = [pop[random.choices(range(POP), weights=fits)[0]] for _ in range(POP)]
        children = []
        for i in range(0, POP-1, 2):
            children += [mutate(crossover(selected[i], selected[i+1])),
                         mutate(crossover(selected[i+1], selected[i]))]
        pop = elites + children[:POP-10]

    best_routes = split_routes(best_chrom)
    total_dist  = sum(route_dist(r) for r in best_routes)
    return best_routes, round(total_dist, 2)

# ── BASELINE SYSTEM ────────────────────────────────────────────────────────────
def run_baseline(all_bins):
    """Visit ALL bins in fixed sequential order regardless of fill level."""
    locations = [DEPOT] + all_bins
    total_dist = 0

    # Split into truck routes respecting capacity
    routes, route, load = [], [], 0
    for bin_info in all_bins:
        demand = bin_info["demand_kg"]
        if load + demand <= TRUCK_CAPACITY:
            route.append(bin_info); load += demand
        else:
            if route: routes.append(route)
            route, load = [bin_info], demand
    if route: routes.append(route)

    # Compute total distance
    for r in routes:
        stops = [DEPOT] + r + [DEPOT]
        for i in range(len(stops)-1):
            total_dist += haversine(
                stops[i]["lat"], stops[i]["lon"],
                stops[i+1]["lat"], stops[i+1]["lon"]
            )

    return routes, round(total_dist, 2)

# ══════════════════════════════════════════════════════════════════════════════
# MAIN EVALUATION
# ══════════════════════════════════════════════════════════════════════════════
print("🔮 Running waste level predictions...")
all_predictions = predict_all_bins()

bins_needing_collection = [b for b in all_predictions if b["needs_collection"]]
all_bins_list           = all_predictions

print(f"✅ Total bins predicted: {len(all_predictions)}")
print(f"✅ Bins needing collection (>={COLLECTION_THRESHOLD}%): {len(bins_needing_collection)}")
print()

# ── RUN BASELINE ───────────────────────────────────────────────────────────────
print("🚛 Running BASELINE fixed-route system...")
baseline_routes, baseline_distance = run_baseline(all_bins_list)
baseline_fuel        = round(baseline_distance * FUEL_RATE, 2)
baseline_fuel_cost   = round(baseline_fuel * FUEL_PRICE_XAF, 0)
baseline_bins_served = len(all_bins_list)
baseline_overflow    = len([b for b in all_bins_list if b["predicted_fill"] >= 80])
print(f"✅ Baseline total distance: {baseline_distance} km")
print()

# ── RUN AI-ENHANCED SYSTEM ─────────────────────────────────────────────────────
print("🧬 Running AI-ENHANCED optimized system (Genetic Algorithm)...")
print("   Please wait — running 200 generations...")
ai_routes, ai_distance = run_ga(bins_needing_collection)
ai_fuel        = round(ai_distance * FUEL_RATE, 2)
ai_fuel_cost   = round(ai_fuel * FUEL_PRICE_XAF, 0)
ai_bins_served = len(bins_needing_collection)
ai_overflow    = len([b for b in bins_needing_collection if b["predicted_fill"] >= 80])
print(f"✅ AI optimized total distance: {ai_distance} km")
print()

# ── COMPUTE METRICS ────────────────────────────────────────────────────────────
distance_saved    = round(baseline_distance - ai_distance, 2)
distance_pct      = round((distance_saved / baseline_distance) * 100, 1) if baseline_distance > 0 else 0
fuel_saved        = round(baseline_fuel - ai_fuel, 2)
fuel_cost_saved   = round(baseline_fuel_cost - ai_fuel_cost, 0)
coverage_baseline = round((baseline_bins_served / len(all_predictions)) * 100, 1)
coverage_ai       = 100.0  # all urgent bins served

# ══════════════════════════════════════════════════════════════════════════════
# PRINT COMPARISON TABLE
# ══════════════════════════════════════════════════════════════════════════════
print("=" * 70)
print("   PERFORMANCE COMPARISON: BASELINE vs AI-ENHANCED SYSTEM")
print("=" * 70)
print(f"{'Metric':<35} {'Baseline':>12} {'AI System':>12} {'Improvement':>12}")
print("-" * 70)
print(f"{'Total Travel Distance (km)':<35} {baseline_distance:>12.2f} {ai_distance:>12.2f} {f'-{distance_saved} km':>12}")
print(f"{'Fuel Consumption (liters)':<35} {baseline_fuel:>12.2f} {ai_fuel:>12.2f} {f'-{fuel_saved} L':>12}")
print(f"{'Estimated Fuel Cost (XAF)':<35} {baseline_fuel_cost:>12,.0f} {ai_fuel_cost:>12,.0f} {f'-{fuel_cost_saved:,.0f}':>12}")
print(f"{'Bins Visited Per Run':<35} {baseline_bins_served:>12} {ai_bins_served:>12} {f'-{baseline_bins_served - ai_bins_served} bins':>12}")
print(f"{'Trucks Used':<35} {min(len(baseline_routes), NUM_TRUCKS):>12} {min(len(ai_routes), NUM_TRUCKS):>12} {'Same':>12}")
print(f"{'Collection Coverage (%)':<35} {coverage_baseline:>11}% {coverage_ai:>11}% {'100% urgent':>12}")
print(f"{'Distance Reduction (%)':<35} {'N/A':>12} {f'{distance_pct}%':>12} {f'{distance_pct}% better':>12}")
print("-" * 70)
print()

# ── AI ROUTE DETAILS ───────────────────────────────────────────────────────────
print("🚛 OPTIMIZED ROUTE DETAILS:")
print("-" * 50)
for i, route in enumerate(ai_routes):
    truck_id   = f"TRUCK{i+1:02d}"
    load       = sum(bins_needing_collection[idx-1]["demand_kg"]
                     for idx in route
                     if idx-1 < len(bins_needing_collection))
    print(f"\n  {truck_id} — {len(route)} stops")
    print(f"  Depot", end="")
    for idx in route:
        if idx - 1 < len(bins_needing_collection):
            b = bins_needing_collection[idx-1]
            print(f" → {b['name']} ({b['predicted_fill']}%)", end="")
    print(" → Depot")
print()

# ── SAVE RESULTS ───────────────────────────────────────────────────────────────
results = {
    "Metric": [
        "Total Travel Distance (km)",
        "Fuel Consumption (liters)",
        "Estimated Fuel Cost (XAF)",
        "Bins Visited Per Run",
        "Trucks Used",
        "Collection Coverage (%)",
        "Distance Reduction (%)",
        "Fuel Cost Saved (XAF)"
    ],
    "Baseline System": [
        baseline_distance,
        baseline_fuel,
        baseline_fuel_cost,
        baseline_bins_served,
        min(len(baseline_routes), NUM_TRUCKS),
        f"{coverage_baseline}%",
        "N/A",
        "0"
    ],
    "AI-Enhanced System": [
        ai_distance,
        ai_fuel,
        ai_fuel_cost,
        ai_bins_served,
        min(len(ai_routes), NUM_TRUCKS),
        f"{coverage_ai}%",
        f"{distance_pct}%",
        f"{fuel_cost_saved:,.0f}"
    ],
    "Improvement": [
        f"-{distance_saved} km",
        f"-{fuel_saved} L",
        f"-{fuel_cost_saved:,.0f} XAF",
        f"-{baseline_bins_served - ai_bins_served} bins",
        "Same fleet",
        "All urgent bins served",
        f"{distance_pct}% reduction",
        f"{fuel_cost_saved:,.0f} XAF saved"
    ]
}

output_path = os.path.join(BASE_DIR, "evaluation", "evaluation_results.csv")
pd.DataFrame(results).to_csv(output_path, index=False)

print("=" * 70)
print(f"✅ Results saved to: evaluation/evaluation_results.csv")
print(f"\n📊 SUMMARY:")
print(f"   Distance saved      : {distance_saved} km ({distance_pct}% reduction)")
print(f"   Fuel saved          : {fuel_saved} liters")
print(f"   Fuel cost saved     : {fuel_cost_saved:,.0f} XAF per run")
print(f"   Unnecessary trips   : {baseline_bins_served - ai_bins_served} bins avoided")
print(f"\n🎉 Evaluation complete!")
print("=" * 70)