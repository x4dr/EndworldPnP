#!/usr/bin/env python3
"""
Shooting range Monte-Carlo simulation to test weapon loadouts against armor.
Uses Endworld 5d10 Selector system, Sector Stress, and proper layered armor logic.
"""
import random
import math

# --- DICE SYSTEM ---
def roll_ew(selectors):
    """Rolls 5d10, sorts them, and returns the sum of the selected positions (1-indexed)."""
    dice = sorted([random.randint(1, 10) for _ in range(5)])
    total = 0
    for s in selectors:
        if s <= 0: continue
        idx = min(s, 5) - 1
        total += dice[idx]
    return total

# --- WEAPONS ---
WEAPONS = {
    "Light Laser":    {"wt": 1.0, "dmg": 10, "e": 50,  "heat": 5,  "ammo": 0, "ap": False},
    "Medium Laser":   {"wt": 3.0, "dmg": 15, "e": 150, "heat": 15, "ammo": 0, "ap": False},
    "Heavy Laser":    {"wt": 6.0, "dmg": 18, "e": 300, "heat": 30, "ammo": 0, "ap": True},
    "Light Cannon":   {"wt": 1.0, "dmg": 12, "e": 5,   "heat": 2,  "ammo": 10,"ap": False},
    "Medium Cannon":  {"wt": 3.0, "dmg": 16, "e": 10,  "heat": 6,  "ammo": 25,"ap": False},
    "Heavy Artillery":{"wt": 6.0, "dmg": 22, "e": 15,  "heat": 10, "ammo": 50,"ap": True},
    "Light Missile":  {"wt": 1.0, "dmg": 13, "e": 10,  "heat": 1,  "ammo": 15,"ap": False},
    "Heavy Silo":     {"wt": 6.0, "dmg": 25, "e": 30,  "heat": 3,  "ammo": 100,"ap": False},
}

# --- ARMOR ---
class ArmorLayer:
    def __init__(self, wt=2.0, grade=2, structure=2):
        self.wt = wt
        self.grade = grade
        self.structure = structure
        self.degradation = 0

    def reduce_damage(self, incoming_dmg, is_ap=False):
        scale = math.sqrt(self.wt)
        
        # Roll uses Grade and Structure
        selectors = [self.grade, self.structure]
        roll = roll_ew(selectors)
        
        # Base reduction
        base_reduction = (2 * scale) + roll * (1 + 0.15 * scale)
        
        # Apply degradation penalty (minimum 0)
        reduction = max(0, base_reduction - self.degradation)
        
        if is_ap:
            reduction = math.ceil(reduction / 2)
            
        remaining_dmg = incoming_dmg - reduction
        
        # If damage penetrates (fails to reduce to 0), armor's protection drops by 1 permanently
        if remaining_dmg > 0:
            self.degradation += 1
                
        return max(0, remaining_dmg)

# --- SIMULATION ---
def simulate_combat(weapon_name, cooling_act, cooling_cap, cooling_flux, cargo_kg, target_stress=35, turns_limit=100):
    wpn = WEAPONS[weapon_name]
    
    layer1 = ArmorLayer(wt=2.0, grade=2, structure=2)
    layer2 = ArmorLayer(wt=2.0, grade=2, structure=2)
    
    stress = 0
    heat_pool = 0
    ammo_remaining = cargo_kg
    
    for turn in range(turns_limit):
        if wpn["ammo"] > 0:
            if ammo_remaining < wpn["ammo"]:
                break
            ammo_remaining -= wpn["ammo"]
            
        if wpn["heat"] > cooling_flux:
            break
            
        heat_pool += wpn["heat"]
        heat_pool = max(0, heat_pool - cooling_act)
        
        if heat_pool > cooling_cap:
            break 
            
        dmg = wpn["dmg"]
        dmg = layer1.reduce_damage(dmg, wpn["ap"])
        dmg = layer2.reduce_damage(dmg, wpn["ap"])
            
        if dmg > 0:
            stress += dmg
            
        if stress >= target_stress:
            return True, turn + 1, stress
            
    return False, turns_limit, stress

def monte_carlo(weapon_name, act, cap, flux, cargo, iterations=5000):
    kills = 0
    total_ttk = 0
    total_dmg = 0
    
    for _ in range(iterations):
        killed, turns, stress = simulate_combat(weapon_name, act, cap, flux, cargo)
        if killed:
            kills += 1
            total_ttk += turns
        total_dmg += stress
        
    kill_pct = (kills / iterations) * 100
    avg_ttk = (total_ttk / kills) if kills > 0 else 0
    avg_dmg = total_dmg / iterations
    return kill_pct, avg_ttk, avg_dmg

if __name__ == "__main__":
    print(f"Target: 2x 2.0t Metal Plating | Threshold: 35 Sector Stress")
    print(f"{'Weapon':<16} | {'Kill%':<6} | {'Avg TTK':<7} | {'Avg Stress':<10} | {'AP'}")
    print("-" * 65)
    
    for w in WEAPONS:
        ap = "Yes" if WEAPONS[w]["ap"] else "No"
        pct, ttk, dmg = monte_carlo(w, 30, 200, 30, 2000)
        print(f"{w:<16} | {pct:>5.1f}% | {ttk:>7.1f} | {dmg:>10.1f} | {ap}")

