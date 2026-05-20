#!/usr/bin/env python3
"""
Benchmarks the 'Dummy Weapon' formula against the different armor types in Endworld.
Tests Single Layer armor configurations across multiple mech sizes.

Usage:
    uv run python armor_benchmark.py
"""
import math

# --- ARMOR TYPES ---
# Format: "Name": (Flat Reduction, Roll Scaling, Scales With Weight)
ARMOR_TYPES = {
    "Sheetmetal (TL 2)":          (0.0, 0.05, True),
    "Composite Plating (TL 2)":   (1.0, 0.25, True),
    "Metal Plating (TL 1)":       (2.0, 0.15, True),
    "UHDC (TL 1)":                (3.0, 0.08, True),
    "Active Plating - Pass (TL 3)": (1.0, 0.30, True),
    "Active Plating - Act (TL 3)":  (0.5, 0.40, True),
    "SpeedShell (TL 3)":          (1.0, 0.15, True),
    "Ion Armor (TL 4)":           (2.0, 0.40, True),
    "Hardlight Armor (TL 5)":     (10.0, 0.00, False), # Does not scale with weight
}

def calc_reduction(armor_type, wt, roll=9):
    flat, roll_scale, scales = ARMOR_TYPES[armor_type]
    
    if not scales:
        return flat + roll * roll_scale # Hardlight is flat 10
        
    scale = math.sqrt(wt)
    # Using the unmodified formula: Flat*Scale + Roll*(1 + Roll_Scale*Scale)
    # The user asked to look at the unmodified armor stuff against single layers.
    return (flat * scale) + roll * (1 + roll_scale * scale)

def benchmark_mechs():
    test_sizes = [
        (4, 4.0),     # Very Light
        (7, 40.0),    # Light/Medium
        (9, 150.0),   # Medium/Heavy
        (11, 500.0)   # Ultra
    ]
    
    print("=== ARMOR BENCHMARK: DUMMY WEAPONS VS SINGLE LAYER ARMOR ===")
    print("Formula: Damage = 10 + 3 * sqrt(gun mass)")
    print("Armor Formula: Flat*Scale + Roll*(1 + Roll_Scale*Scale) | Avg Roll = 9")
    print("-" * 110)
    
    for size, mass in test_sizes:
        # Calculate Facing Armor (Single Layer)
        total_armor = mass * 0.5
        avg_sector = total_armor / size
        facing_armor = round(avg_sector * 1.5, 1)
        
        # Calculate Peer Gun
        gun_mass = round(mass * 0.15, 1)
        gun_dmg = round(10 + 3 * math.sqrt(gun_mass))
        
        print(f"\n--- Mech Mass: {mass}t (Size {size}) | Facing Armor: {facing_armor}t | Peer Gun: {gun_mass}t (Dmg: {gun_dmg}) ---")
        print(f"{'Armor Type':<30} | {'Avg Reduction':<15} | {'Dmg Taken/Hit':<15} | {'Est. TTK (35 Stress)'}")
        print("-" * 110)
        
        # Sort armor types by reduction power
        results = []
        for a_type in ARMOR_TYPES:
            red = calc_reduction(a_type, facing_armor)
            dmg_taken = max(0, gun_dmg - red)
            ttk = 35 / dmg_taken if dmg_taken > 0 else float('inf')
            results.append((a_type, red, dmg_taken, ttk))
            
        results.sort(key=lambda x: x[1]) # Sort by lowest reduction first
        
        for a_type, red, dmg_taken, ttk in results:
            ttk_str = f"{ttk:.1f} turns" if ttk != float('inf') else "INVINCIBLE"
            print(f"{a_type:<30} | {red:>5.1f} blocked   | {dmg_taken:>5.1f} dmg       | {ttk_str:>15}")

if __name__ == "__main__":
    benchmark_mechs()
