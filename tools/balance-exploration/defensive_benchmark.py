#!/usr/bin/env python3
"""
Captures the current performance of the full defensive suite (Shields, Dampeners, Armor)
against the standard sqrt-based weapons.
"""
import sys, os, math
sys.path.insert(0, os.path.dirname(__file__))
from weapon_sim_matrix import roll_ew, WEAPONS

class Shield:
    def __init__(self, name, flat, r_scale):
        self.name = name
        self.flat = flat
        self.r_scale = r_scale
        self.active = True
        
    def reduce_damage(self, dmg):
        if not self.active: return dmg
        roll = roll_ew([2, 2]) # Standard config roll
        reduction = self.flat + roll * self.r_scale
        if reduction < dmg:
            self.active = False # Shield overwhelmed
        return max(0, dmg - reduction)

class Dampener:
    def __init__(self, name, base, config_mult):
        self.name = name
        self.base = base
        self.config_mult = config_mult
        self.config = 3 # Average thresholds reached

    def reduce_damage(self, dmg, is_ballistic):
        if not is_ballistic: return dmg
        reduction = self.base + (self.config * self.config_mult)
        return max(0, dmg - reduction)

class ArmorLayer:
    def __init__(self, wt):
        self.wt = wt
        self.degradation = 0

    def reduce_damage(self, incoming_dmg, is_ap=False):
        scale = math.sqrt(self.wt)
        roll = roll_ew([2, 2])
        # Unmodified wiki formula
        base_reduction = (2 * scale) + roll * (1.0 + 0.15 * scale)
        reduction = max(0, base_reduction - self.degradation)
        if is_ap:
            reduction = math.ceil(reduction / 2)
        remaining_dmg = incoming_dmg - reduction
        if remaining_dmg > 0:
            self.degradation += 1
        return max(0, remaining_dmg)

def sim_full_defense(weapon_name, is_ballistic, iterations=1000):
    wpn = WEAPONS[weapon_name]
    kills = 0
    total_turns = 0
    
    for _ in range(iterations):
        shield = Shield("Standard Shield", 4, 1.5)
        dampener = Dampener("Heavy Dampener", 10, 2)
        armor = ArmorLayer(4.0) # 4t Metal Plating
        stress = 0
        
        for turn in range(1, 201):
            dmg = wpn["dmg"]
            
            # 1. Shields
            dmg = shield.reduce_damage(dmg)
            
            # 2. Dampeners (Armor acts after, wait: Dampeners help armor/shields. "subtracts from enemy damage... helping armor and shields.")
            # Ah, "Dampeners subtract from enemy damage, helping armor and shields." So Dampener first!
            # I will apply dampener first.
            pass # See below
            
        pass

def true_sim(weapon_name, is_ballistic, iterations=1000):
    wpn = WEAPONS[weapon_name]
    kills = 0
    total_turns = 0
    
    for _ in range(iterations):
        shield = Shield("Standard Shield", 4, 1.5)
        dampener = Dampener("Heavy Dampener", 10, 2)
        armor = ArmorLayer(4.0)
        stress = 0
        
        for turn in range(1, 201):
            dmg = wpn["dmg"]
            
            # 1. Dampener
            dmg = dampener.reduce_damage(dmg, is_ballistic)
            
            # 2. Shield
            dmg = shield.reduce_damage(dmg)
            
            # 3. Armor
            dmg = armor.reduce_damage(dmg, wpn["ap"])
            
            if dmg > 0:
                stress += dmg
            if stress >= 35:
                kills += 1
                total_turns += turn
                break
                
    return (total_turns / kills) if kills > 0 else float('inf')

print("=== CURRENT DEFENSIVE PERFORMANCE ===")
print("Target: Heavy Dampener (1t) -> Standard Shield (1t) -> 4.0t Metal Plating")
print("-" * 70)
for w, is_b in [("Medium Cannon", True), ("Heavy Artillery", True), ("Medium Laser", False), ("Heavy Laser", False)]:
    ttk = true_sim(w, is_b)
    print(f"{w:<18} | {ttk:.1f} turns to kill")

