#!/usr/bin/env python3
"""
Tests how weapon damage and armor reduction scale across different mech sizes.
Shows the mathematical discrepancy between weapon damage scaling and armor scaling.

Usage:
    uv run python scale_test.py
"""
import math

sizes = [
    (2, 1.0), (3, 2.0), (4, 4.0), (5, 10.0), (6, 18.0), 
    (7, 40.0), (8, 70.0), (9, 150.0), (10, 300.0), (11, 500.0), (12, 700.0)
]

def calc_reduction(wt, roll_scale=0.9, roll=9):
    if wt <= 0: return 0
    scale = math.sqrt(wt)
    return (2 * scale) + roll * (roll_scale * scale)

print("=== ENDWORLD SCALING TEST (Peer vs Peer) ===")
print("Assumptions:")
print("- Facing Armor = (Mech Mass * 50% Budget) / Sectors * 1.5 front-load multiplier")
print("- Peer Gun Mass = Mech Mass * 15% (Roughly 2 big guns on the remaining budget)")
print("- Damage Formula = 10 + 3 * sqrt(Gun Mass)")
print("- Armor Formula = 2*sqrt(wt) + Roll*(0.9*sqrt(wt))  [Average Roll = 9]")
print("-" * 115)
print(f"{'Size':<5} | {'Mass(t)':<8} | {'Facing Armor':<15} | {'1x Plate Reduc':<15} | {'2x Plate Reduc':<15} | {'Peer Gun':<10} | {'Gun Dmg'}")
print("-" * 115)

for size, mass in sizes:
    # Armor Math
    total_armor = mass * 0.5
    avg_sector = total_armor / size
    facing_armor = avg_sector * 1.5
    
    # Round to nearest 0.1t for realism
    facing_armor = round(facing_armor, 1)
    
    if facing_armor > 0:
        half_armor = facing_armor / 2
        # Calculate reductions (assuming average roll of 9)
        red_1x = calc_reduction(facing_armor)
        red_2x = calc_reduction(half_armor) * 2 # Shows combined blocking power if hit didn't penetrate
    else:
        red_1x = 0
        red_2x = 0
        
    # Weapon Math
    gun_mass = round(mass * 0.15, 1)
    if gun_mass > 0:
        gun_dmg = 10 + 3 * math.sqrt(gun_mass)
    else:
        gun_dmg = 0
        
    print(f"{size:<5} | {mass:<8.1f} | {facing_armor:>5.1f}t          | {red_1x:>5.1f} dmg         | {red_2x:>5.1f} dmg         | {gun_mass:>4.1f}t      | {gun_dmg:>5.1f}")
