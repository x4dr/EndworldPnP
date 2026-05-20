#!/usr/bin/env python3
"""
Tests different gun masses against a Size 11 (500t) Mech.
Target Armor: 34.0t facing armor.
"""
import sys, os, math
sys.path.insert(0, os.path.dirname(__file__))
from scaling_ttk_test import monte_carlo

if __name__ == "__main__":
    facing_armor = 34.0
    
    print("=== SIZE 11 (500t) MECH: GUN MASS SCALING TEST ===")
    print(f"Target Stress: 35 | Facing Armor: {facing_armor}t | Formula: 10 + 3*sqrt(mass)")
    print("-" * 75)
    print(f"{'Gun Mass(t)':<12} | {'Gun Dmg':<8} || {'1-Layer TTK (34t)':<18} | {'2-Layer TTK (2x 17t)'}")
    print("-" * 75)
    
    for gun_mass in range(40, 105, 5):
        gun_dmg = round(10 + 3 * math.sqrt(gun_mass))
        
        ttk_1x = monte_carlo(gun_dmg, [facing_armor])
        ttk_2x = monte_carlo(gun_dmg, [facing_armor / 2, facing_armor / 2])
        
        print(f"{gun_mass:<12.1f} | {gun_dmg:<8} || {ttk_1x:<18} | {ttk_2x}")

