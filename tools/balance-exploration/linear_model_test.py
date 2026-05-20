#!/usr/bin/env python3
import math

sizes = [(4, 4.0), (5, 10.0), (7, 40.0), (9, 150.0), (11, 500.0)]

def test_linear(weapon_mult, armor_roll_scale):
    print(f"\n--- Testing Linear Model: Wpn Multiplier={weapon_mult}, Armor Roll Scale={armor_roll_scale} ---")
    print(f"{'Size':<5} | {'Mass':<5} | {'Armor':<6} | {'Gun':<5} || {'Armor Reduc':<12} | {'Gun Dmg':<8} | {'Net Dmg':<8}")
    print("-" * 80)
    for size, mass in sizes:
        total_armor = mass * 0.5
        avg_sector = total_armor / size
        facing_armor = round(avg_sector * 1.5, 1)
        if facing_armor == 0: continue
        
        gun_mass = round(mass * 0.15, 1)
        
        # Linear Armor: Flat*Wt + Roll*(1 + RollScale*Wt)
        # Using Metal Plating (Flat=2)
        armor_reduc = (2 * facing_armor) + 9 * (1.0 + armor_roll_scale * facing_armor)
        
        # Linear Weapon: 10 + Mult * Wt
        gun_dmg = 10 + weapon_mult * gun_mass
        
        net = max(0, gun_dmg - armor_reduc)
        print(f"{size:<5} | {mass:<5.0f} | {facing_armor:<6.1f} | {gun_mass:<5.1f} || {armor_reduc:<12.1f} | {gun_dmg:<8.1f} | {net:<8.1f}")

test_linear(1.5, 0.10)
test_linear(1.0, 0.15)
test_linear(2.0, 0.15)

