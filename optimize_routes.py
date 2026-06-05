import pandas as pd
import numpy as np
from math import radians, sin, cos, sqrt, atan2
import random
import joblib

print("🧬 Starting Route Optimization...\n")

# ── 1. LOAD DATA ──────────────────────────────────────────────────────────────
bins_df = pd.read_csv("data/raw/bins.csv")
processed_df = pd.read_csv("data/processed/processed_data.csv")

# Get latest fill percentage per bin
latest = (
    processed_df.sort_values("timestamp")
    .groupby("bin_id")
    .last()
    .reset_index()[["bin_id", "fill_percentage"]]
)

bins_df = bins_df.merge(latest, on="bin_id", how="left")
bins_df["fill_percentage"] = bins_df["fill_percentage"].fillna(50.0)

# Only collect bins that are at least 60% full
bins_to_collect = bins_df[bins_df["fill_percentage"] >= 60].copy()
bins_to_collect = bins_to_collect.reset_index(drop=True)

print(f"✅ Total bins         : {len(bins_df)}")
print(f"✅ Bins needing collection (>=60%): {len(bins_to_collect)}")

# ── 2. DEPOT LOCATION (HYSACAM Buea depot) ────────────────────────────────────
DEPOT = {"lat": 4.1534, "lon": 9.2916, "name": "HYSACAM Depot Buea"}

# ── 3. DISTANCE MATRIX ────────────────────────────────────────────────────────
def haversine(lat1, lon1, lat2, lon2):
    """Calculate distance in km between two GPS points."""
    R = 6371
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = sin(dlat/2)**2 + cos(lat1)*cos(lat2)*sin(dlon/2)**2
    return R * 2 * atan2(sqrt(a), sqrt(1-a))

# Build locations list: depot + bins
locations = [DEPOT] + bins_to_collect.to_dict("records")
n = len(locations)

print(f"\n🔧 Building {n}x{n} distance matrix...")

dist_matrix = np.zeros((n, n))
for i in range(n):
    for j in range(n):
        if i != j:
            dist_matrix[i][j] = haversine(
                locations[i]["lat"], locations[i]["lon"],
                locations[j]["lat"], locations[j]["lon"]
            )

print("✅ Distance matrix built!")

# ── 4. CVRP SETUP ─────────────────────────────────────────────────────────────
TRUCK_CAPACITY   = 1000   # kg per truck
NUM_TRUCKS       = 3
DEPOT_INDEX      = 0

# Demand = waste collected (kg) for each bin
demands = [0]  # depot has 0 demand
for _, row in bins_to_collect.iterrows():
    demand = (row["fill_percentage"] / 100) * row["capacity_kg"]
    demands.append(round(demand, 2))

print(f"\n✅ Truck capacity : {TRUCK_CAPACITY} kg")
print(f"✅ Number of trucks: {NUM_TRUCKS}")
print(f"✅ Total demand   : {sum(demands):.1f} kg")

# ── 5. GENETIC ALGORITHM ──────────────────────────────────────────────────────
BIN_INDICES = list(range(1, n))  # exclude depot

POPULATION_SIZE = 100
GENERATIONS     = 200
MUTATION_RATE   = 0.02
ELITE_SIZE      = 10

def split_into_routes(chromosome):
    """Split chromosome into truck routes respecting capacity."""
    routes = []
    current_route = []
    current_load  = 0

    for bin_idx in chromosome:
        bin_demand = demands[bin_idx]
        if current_load + bin_demand <= TRUCK_CAPACITY:
            current_route.append(bin_idx)
            current_load += bin_demand
        else:
            if current_route:
                routes.append(current_route)
            current_route = [bin_idx]
            current_load  = bin_demand

    if current_route:
        routes.append(current_route)

    return routes

def route_distance(route):
    """Total distance for one truck route (depot → bins → depot)."""
    if not route:
        return 0
    total = dist_matrix[DEPOT_INDEX][route[0]]
    for i in range(len(route) - 1):
        total += dist_matrix[route[i]][route[i+1]]
    total += dist_matrix[route[-1]][DEPOT_INDEX]
    return total

def fitness(chromosome):
    """Lower total distance = higher fitness."""
    routes = split_into_routes(chromosome)
    total_dist = sum(route_distance(r) for r in routes)
    # Penalize if more trucks needed than available
    penalty = max(0, len(routes) - NUM_TRUCKS) * 1000
    return 1 / (total_dist + penalty + 1e-6)

def create_individual():
    individual = BIN_INDICES.copy()
    random.shuffle(individual)
    return individual

def create_population():
    return [create_individual() for _ in range(POPULATION_SIZE)]

def selection(population, fitnesses):
    """Tournament selection."""
    selected = []
    for _ in range(len(population)):
        a, b = random.sample(range(len(population)), 2)
        selected.append(population[a] if fitnesses[a] > fitnesses[b] else population[b])
    return selected

def crossover(parent1, parent2):
    """Order crossover (OX)."""
    size = len(parent1)
    start, end = sorted(random.sample(range(size), 2))
    child = [None] * size
    child[start:end] = parent1[start:end]
    pointer = 0
    for gene in parent2:
        if gene not in child:
            while child[pointer] is not None:
                pointer += 1
            child[pointer] = gene
    return child

def mutate(individual):
    """Swap mutation."""
    if random.random() < MUTATION_RATE:
        i, j = random.sample(range(len(individual)), 2)
        individual[i], individual[j] = individual[j], individual[i]
    return individual

# ── 6. RUN GENETIC ALGORITHM ──────────────────────────────────────────────────
print("\n🧬 Running Genetic Algorithm...")
print(f"   Population: {POPULATION_SIZE} | Generations: {GENERATIONS}")

random.seed(42)
population  = create_population()
best_chromosome = None
best_fitness    = -1
best_distance   = float("inf")

for generation in range(GENERATIONS):
    fitnesses = [fitness(ind) for ind in population]

    # Track best
    gen_best_idx = np.argmax(fitnesses)
    if fitnesses[gen_best_idx] > best_fitness:
        best_fitness    = fitnesses[gen_best_idx]
        best_chromosome = population[gen_best_idx].copy()
        best_distance   = 1 / best_fitness

    if generation % 50 == 0:
        print(f"   Generation {generation:3d} | Best distance: {best_distance:.2f} km")

    # Elite preservation
    elite_indices = np.argsort(fitnesses)[-ELITE_SIZE:]
    elites = [population[i] for i in elite_indices]

    # Selection + crossover + mutation
    selected   = selection(population, fitnesses)
    children   = []
    for i in range(0, len(selected) - 1, 2):
        child1 = crossover(selected[i], selected[i+1])
        child2 = crossover(selected[i+1], selected[i])
        children.extend([mutate(child1), mutate(child2)])

    population = elites + children[:POPULATION_SIZE - ELITE_SIZE]

print(f"\n✅ Optimization complete!")
print(f"   Best total distance: {best_distance:.2f} km")

# ── 7. OUTPUT OPTIMIZED ROUTES ────────────────────────────────────────────────
best_routes = split_into_routes(best_chromosome)

print(f"\n🚛 OPTIMIZED ROUTES ({len(best_routes)} trucks needed):")
print("=" * 60)

route_results = []

for i, route in enumerate(best_routes):
    truck_id    = f"TRUCK{i+1:02d}"
    dist        = route_distance(route)
    load        = sum(demands[b] for b in route)
    bin_names   = [locations[b]["name"] for b in route]

    print(f"\n  {truck_id} — {len(route)} bins | {load:.1f} kg | {dist:.2f} km")
    print(f"  Depot → ", end="")
    print(" → ".join(bin_names))
    print(f"  → Depot")

    for stop, bin_idx in enumerate(route):
        route_results.append({
            "truck_id"      : truck_id,
            "stop_order"    : stop + 1,
            "bin_id"        : locations[bin_idx]["bin_id"],
            "bin_name"      : locations[bin_idx]["name"],
            "neighborhood"  : locations[bin_idx]["neighborhood"],
            "lat"           : locations[bin_idx]["lat"],
            "lon"           : locations[bin_idx]["lon"],
            "demand_kg"     : demands[bin_idx],
            "fill_percentage": locations[bin_idx]["fill_percentage"],
            "route_distance_km": round(dist, 2)
        })

# ── 8. SAVE ROUTES ────────────────────────────────────────────────────────────
routes_df = pd.DataFrame(route_results)
routes_df.to_csv("data/processed/optimized_routes.csv", index=False)

print("\n" + "=" * 60)
print(f"✅ Optimized routes saved: data/processed/optimized_routes.csv")
print(f"   Total bins served : {len(route_results)}")
print(f"   Total distance    : {best_distance:.2f} km")
print(f"   Trucks used       : {len(best_routes)}")
print("\n🎉 Route optimization complete!")