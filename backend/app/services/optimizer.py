import pandas as pd
import numpy as np
from math import radians, sin, cos, sqrt, atan2
import random

DEPOT = {"lat": 4.1534, "lon": 9.2916, "name": "HYSACAM Depot Buea", "bin_id": "DEPOT"}
TRUCK_CAPACITY = 1000
NUM_TRUCKS = 3

def haversine(lat1, lon1, lat2, lon2):
    R = 6371
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    a = sin((lat2-lat1)/2)**2 + cos(lat1)*cos(lat2)*sin((lon2-lon1)/2)**2
    return R * 2 * atan2(sqrt(a), sqrt(1-a))

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

def run_genetic_algorithm(bins_to_collect):
    if not bins_to_collect:
        return [], 0

    locations = [DEPOT] + bins_to_collect
    demands = [0] + [
        (b["predicted_fill"] / 100) * b["capacity_kg"]
        for b in bins_to_collect
    ]
    dist_matrix = build_distance_matrix(locations)
    bin_indices = list(range(1, len(locations)))
    n_bins = len(bin_indices)

    # Scale population to number of bins
    POP = max(10, min(100, n_bins * 5))
    GENS = 200

    def split_routes(chrom):
        routes, route, load = [], [], 0
        for idx in chrom:
            if load + demands[idx] <= TRUCK_CAPACITY:
                route.append(idx)
                load += demands[idx]
            else:
                if route:
                    routes.append(route)
                route, load = [idx], demands[idx]
        if route:
            routes.append(route)
        return routes

    def route_dist(route):
        if not route:
            return 0
        d = dist_matrix[0][route[0]]
        for i in range(len(route) - 1):
            d += dist_matrix[route[i]][route[i+1]]
        return d + dist_matrix[route[-1]][0]

    def fitness(chrom):
        routes = split_routes(chrom)
        total = sum(route_dist(r) for r in routes)
        penalty = max(0, len(routes) - NUM_TRUCKS) * 1000
        return 1 / (total + penalty + 1e-6)

    def crossover(p1, p2):
        size = len(p1)
        if size < 2:
            return p1[:]
        s, e = sorted(random.sample(range(size), 2))
        child = [None] * size
        child[s:e] = p1[s:e]
        ptr = 0
        for g in p2:
            if g not in child:
                while child[ptr] is not None:
                    ptr += 1
                child[ptr] = g
        return child

    def mutate(ind):
        if len(ind) >= 2 and random.random() < 0.02:
            i, j = random.sample(range(len(ind)), 2)
            ind[i], ind[j] = ind[j], ind[i]
        return ind

    random.seed(42)
    pop = [random.sample(bin_indices, n_bins) for _ in range(POP)]

    best_chrom, best_fit, best_dist = None, -1, float("inf")

    for _ in range(GENS):
        fits = [fitness(ind) for ind in pop]
        idx = int(np.argmax(fits))
        if fits[idx] > best_fit:
            best_fit = fits[idx]
            best_chrom = pop[idx].copy()
            best_dist = 1 / best_fit

        elite_size = min(10, POP)
        elites = [pop[i] for i in np.argsort(fits)[-elite_size:]]
        selected = [pop[random.choices(range(POP), weights=fits)[0]] for _ in range(POP)]
        children = []
        for i in range(0, POP - 1, 2):
            children += [
                mutate(crossover(selected[i], selected[i+1])),
                mutate(crossover(selected[i+1], selected[i]))
            ]
        pop = elites + children[:POP - elite_size]

    best_routes = split_routes(best_chrom)
    output = []
    for i, route in enumerate(best_routes):
        stops = []
        for order, bin_idx in enumerate(route):
            b = locations[bin_idx]
            stops.append({
                "stop_order": order + 1,
                "bin_id": b["bin_id"],
                "name": b["name"],
                "neighborhood": b["neighborhood"],
                "lat": b["lat"],
                "lon": b["lon"],
                "demand_kg": round(demands[bin_idx], 2),
                "fill_percentage": b["predicted_fill"]
            })
        output.append({
            "truck_id": f"TRUCK{i+1:02d}",
            "total_bins": len(route),
            "total_load_kg": round(sum(demands[b] for b in route), 2),
            "distance_km": round(route_dist(route), 2),
            "stops": stops
        })

    return output, round(best_dist, 2)