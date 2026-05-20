#!/usr/bin/env python3
import math
import random
import time
from multiprocessing import Pool, cpu_count
from collections import Counter
import itertools

ARMOR_TYPES = {
    "Sheetmetal (TL 2)":          (0.0, 0.05, True),
    "Composite Plating (TL 2)":   (1.0, 0.25, True),
    "Metal Plating (TL 1)":       (2.0, 0.15, True),
    "UHDC (TL 1)":                (3.0, 0.08, True),
    "Active Plating - Pass (TL 3)": (1.0, 0.30, True),
    "Active Plating - Act (TL 3)":  (0.5, 0.40, True),
    "SpeedShell (TL 3)":          (1.0, 0.15, True),
    "Ion Armor (TL 4)":           (2.0, 0.40, True),
    "Hardlight Armor (TL 5)":     (10.0, 0.00, False),
}

# Precompute the dice distribution for [2, 2] selectors (Grade 2, Structure 2)
# To make sampling O(1) and ultra-fast.
def build_dice_pool(selectors=[2, 2]):
    outcomes = []
    # 5d10 has 10^5 = 100,000 combinations
    for p in itertools.product(range(1, 11), repeat=5):
        s = sorted(p)
        tot = sum(s[min(sel, 5) - 1] for sel in selectors if sel > 0)
        outcomes.append(tot)
    return outcomes

DICE_POOL = build_dice_pool()

def run_mc_scenario(args):
    a_type, flat, roll_scale, scales, wt, gun_dmg, iterations = args
    
    scale_factor = math.sqrt(wt) if scales else 1.0
    base_flat = (flat * scale_factor) if scales else flat
    r_scale_factor = roll_scale * scale_factor if scales else 0.0
    
    kills = 0
    total_turns = 0
    
    # Localizing globals for speed
    pool = DICE_POOL
    choice = random.choice
    
    for _ in range(iterations):
        degradation = 0
        stress = 0
        
        for turn in range(1, 501): # 500 turns max
            roll = choice(pool)
            
            # Base reduction using the EXACT wiki-as-written formula
            base_red = base_flat + roll * (1.0 + r_scale_factor) if scales else base_flat + roll * r_scale_factor
            
            # Hardlight has Flat 10, Roll 0, Scales False.
            if not scales:
                base_red = flat + roll * roll_scale
                
            reduction = max(0.0, base_red - degradation)
            
            dmg_taken = gun_dmg - reduction
            
            if dmg_taken > 0:
                stress += dmg_taken
                degradation += 1 # Armor drops by 1 protection per penetration
                
            if stress >= 35:
                kills += 1
                total_turns += turn
                break
                
    kill_pct = (kills / iterations) * 100
    avg_ttk = (total_turns / kills) if kills > 0 else float('inf')
    return (a_type, wt, gun_dmg, kill_pct, avg_ttk)

if __name__ == "__main__":
    test_sizes = [
        (4, 4.0),     # Very Light
        (7, 40.0),    # Light/Medium
        (9, 150.0),   # Medium/Heavy
        (11, 500.0)   # Ultra
    ]
    
    ITERATIONS = 100000
    
    tasks = []
    for size, mass in test_sizes:
        facing_armor = round(((mass * 0.5) / size) * 1.5, 1)
        gun_mass = round(mass * 0.15, 1)
        gun_dmg = round(10 + 3 * math.sqrt(gun_mass))
        
        for a_type, (flat, rs, scales) in ARMOR_TYPES.items():
            tasks.append((a_type, flat, rs, scales, facing_armor, gun_dmg, ITERATIONS))

    print(f"Starting Monte Carlo Benchmark ({ITERATIONS:,} iterations per scenario)...")
    print(f"Using {cpu_count()} CPU cores. This should take a few seconds.")
    
    start_time = time.time()
    
    with Pool(processes=cpu_count()) as p:
        results = p.map(run_mc_scenario, tasks)
        
    end_time = time.time()
    print(f"Simulation completed in {end_time - start_time:.2f} seconds.\n")
    
    # Group results by Mech Size/Mass
    grouped = {}
    for res in results:
        a_type, wt, dmg, pct, ttk = res
        key = (wt, dmg)
        if key not in grouped:
            grouped[key] = []
        grouped[key].append((a_type, pct, ttk))
        
    for (wt, dmg), armors in grouped.items():
        print(f"--- Facing Armor: {wt}t | Peer Gun Dmg: {dmg} ---")
        print(f"{'Armor Type':<30} | {'Kill %':<10} | {'Avg TTK (35 Stress)'}")
        print("-" * 75)
        
        # Sort by TTK descending
        armors.sort(key=lambda x: x[2], reverse=True)
        for a_type, pct, ttk in armors:
            ttk_str = f"{ttk:.1f} turns" if ttk != float('inf') else "INVINCIBLE"
            print(f"{a_type:<30} | {pct:>5.1f}%     | {ttk_str:>15}")
        print()
