#!/usr/bin/env python3
"""
Tests different Roll Scaling multipliers for the Armor formula.
Compares Time-To-Kill (TTK) between Layered (2x 2t) and Single-Plate (1x 4t) armor setups.

Usage:
    uv run python armor_scaling_test.py
"""
import sys, os, math
import argparse
sys.path.insert(0, os.path.dirname(__file__))
from weapon_sim_matrix import roll_ew, WEAPONS

class DynamicArmorLayer:
    def __init__(self, wt, roll_scale, grade=2, structure=2):
        self.wt = wt
        self.grade = grade
        self.structure = structure
        self.roll_scale = roll_scale
        self.degradation = 0

    def reduce_damage(self, incoming_dmg, is_ap=False):
        scale = math.sqrt(self.wt)
        selectors = [self.grade, self.structure]
        roll = roll_ew(selectors)
        
        # New formula without 1+
        base_reduction = (2 * scale) + roll * (self.roll_scale * scale)
        reduction = max(0, base_reduction - self.degradation)
        
        if is_ap:
            reduction = math.ceil(reduction / 2)
            
        remaining_dmg = incoming_dmg - reduction
        if remaining_dmg > 0:
            self.degradation += 1
                
        return max(0, remaining_dmg)

def sim_dynamic(weapon_name, roll_scale, armor_setup, target_stress=35, turns_limit=100):
    wpn = WEAPONS[weapon_name]
    layers = [DynamicArmorLayer(w, roll_scale) for w in armor_setup]
    
    stress = 0
    for turn in range(turns_limit):
        dmg = wpn["dmg"]
        for layer in layers:
            dmg = layer.reduce_damage(dmg, wpn["ap"])
        if dmg > 0:
            stress += dmg
        if stress >= target_stress:
            return True, turn + 1
    return False, turns_limit

def mc_dynamic(weapon_name, roll_scale, armor_setup, iterations=1000):
    kills = 0
    total_ttk = 0
    for _ in range(iterations):
        killed, turns = sim_dynamic(weapon_name, roll_scale, armor_setup)
        if killed:
            kills += 1
            total_ttk += turns
            
    kill_pct = (kills / iterations) * 100
    avg_ttk = (total_ttk / kills) if kills > 0 else 0
    return kill_pct, avg_ttk

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Test armor scaling.")
    parser.add_argument("--scale", type=float, default=0.9, help="Roll Scaling Multiplier")
    args = parser.parse_args()

    scale_val = args.scale
    print(f"=== TESTING ROLL SCALE: {scale_val} ===")
    
    print("\n--- SCENARIO 1: Two Layers of 2.0t (4.0t Total) ---")
    print(f"{'Weapon':<16} | {'Kill%':<6} | {'Avg TTK'}")
    print("-" * 35)
    for w in ["Medium Laser", "Medium Cannon", "Heavy Laser", "Heavy Artillery"]:
        pct, ttk = mc_dynamic(w, scale_val, [2.0, 2.0])
        print(f"{w:<16} | {pct:>5.1f}% | {ttk:>7.1f}")
        
    print("\n--- SCENARIO 2: One Layer of 4.0t (4.0t Total) ---")
    print(f"{'Weapon':<16} | {'Kill%':<6} | {'Avg TTK'}")
    print("-" * 35)
    for w in ["Medium Laser", "Medium Cannon", "Heavy Laser", "Heavy Artillery"]:
        pct, ttk = mc_dynamic(w, scale_val, [4.0])
        print(f"{w:<16} | {pct:>5.1f}% | {ttk:>7.1f}")
