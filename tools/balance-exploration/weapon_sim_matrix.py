#!/usr/bin/env python3
import random
import math

def roll_ew(selectors):
    dice = sorted([random.randint(1, 10) for _ in range(5)])
    total = 0
    for s in selectors:
        if s <= 0: continue
        idx = min(s, 5) - 1
        total += dice[idx]
    return total

WEAPONS = {
    "Medium Laser":   {"wt": 3.0, "dmg": 15, "e": 150, "heat": 15, "ammo": 0, "ap": False},
    "Heavy Laser":    {"wt": 6.0, "dmg": 18, "e": 300, "heat": 30, "ammo": 0, "ap": True},
    "Medium Cannon":  {"wt": 3.0, "dmg": 16, "e": 10,  "heat": 6,  "ammo": 25,"ap": False},
    "Heavy Artillery":{"wt": 6.0, "dmg": 22, "e": 15,  "heat": 10, "ammo": 50,"ap": True},
    "Medium Missile": {"wt": 3.0, "dmg": 17, "e": 20,  "heat": 2,  "ammo": 40,"ap": False},
    "Heavy Silo":     {"wt": 6.0, "dmg": 25, "e": 30,  "heat": 3,  "ammo": 100,"ap": False},
}

class ArmorLayer:
    def __init__(self, wt, grade=2, structure=2):
        self.wt = wt
        self.grade = grade
        self.structure = structure
        self.degradation = 0

    def reduce_damage(self, incoming_dmg, is_ap=False):
        scale = math.sqrt(self.wt)
        selectors = [self.grade, self.structure]
        roll = roll_ew(selectors)
        
        # User proposed formula: Removed the "1 +"
        base_reduction = (2 * scale) + roll * (0.15 * scale)
        reduction = max(0, base_reduction - self.degradation)
        
        if is_ap:
            reduction = math.ceil(reduction / 2)
            
        remaining_dmg = incoming_dmg - reduction
        if remaining_dmg > 0:
            self.degradation += 1
                
        return max(0, remaining_dmg)

def simulate_combat(weapon_name, armor_setup, target_stress=35, turns_limit=100):
    wpn = WEAPONS[weapon_name]
    # Create fresh armor layers for this run
    layers = [ArmorLayer(wt=w) for w in armor_setup]
    
    stress = 0
    # Assuming infinite ammo/cooling for a pure TTK test, as requested
    
    for turn in range(turns_limit):
        dmg = wpn["dmg"]
        for layer in layers:
            dmg = layer.reduce_damage(dmg, wpn["ap"])
            
        if dmg > 0:
            stress += dmg
            
        if stress >= target_stress:
            return True, turn + 1
            
    return False, turns_limit

def monte_carlo(weapon_name, armor_setup, iterations=2000):
    kills = 0
    total_ttk = 0
    
    for _ in range(iterations):
        killed, turns = simulate_combat(weapon_name, armor_setup)
        if killed:
            kills += 1
            total_ttk += turns
            
    kill_pct = (kills / iterations) * 100
    avg_ttk = (total_ttk / kills) if kills > 0 else 0
    return kill_pct, avg_ttk

print("=== SCENARIO 1: Two Layers of 2.0t (4.0t Total) ===")
print(f"{'Weapon':<16} | {'Kill%':<6} | {'Avg TTK':<7}")
print("-" * 35)
for w in WEAPONS:
    pct, ttk = monte_carlo(w, [2.0, 2.0])
    print(f"{w:<16} | {pct:>5.1f}% | {ttk:>7.1f}")

print("\n=== SCENARIO 2: One Layer of 4.0t (4.0t Total) ===")
print(f"{'Weapon':<16} | {'Kill%':<6} | {'Avg TTK':<7}")
print("-" * 35)
for w in WEAPONS:
    pct, ttk = monte_carlo(w, [4.0])
    print(f"{w:<16} | {pct:>5.1f}% | {ttk:>7.1f}")
