#!/usr/bin/env python3
import math
import random
import itertools

# Precompute the 5d10 distribution for Grade 2, Structure 2 (Selectors: 2nd lowest, 2nd lowest)
def _build_pool():
    pool = []
    for p in itertools.product(range(1, 11), repeat=5):
        s = sorted(p)
        pool.append(s[1] + s[1]) # Selectors [2, 2]
    return pool

ROLL_POOL = _build_pool()

class ArmorPlate:
    def __init__(self, name, weight, flat, r_scale, grade=2, structure=2):
        self.name = name
        self.weight = weight
        self.flat = flat
        self.r_scale = r_scale
        self.grade = grade
        self.structure = structure
        self.degradation = 0

    def copy(self):
        return ArmorPlate(self.name, self.weight, self.flat, self.r_scale, self.grade, self.structure)

# Discrete Armor Database (Metal Plating variants)
DB = {
    "ScrapPlate":    (0.5,  1.0, 0.10),
    "LightPlate":    (1.0,  2.0, 0.15),
    "StandardPlate": (2.0,  5.0, 0.30),
    "HeavyPlate":    (4.0, 11.0, 0.60),
    "UltraPlate":    (8.0, 25.0, 1.20),
}

def get_plate(name, qty=1):
    w, f, rs = DB[name]
    return [ArmorPlate(name, w, f, rs) for _ in range(qty)]

def reduce_damage(plate, incoming_dmg, is_ap=False, roll=None):
    if roll is None:
        roll = random.choice(ROLL_POOL)
        
    base_reduction = plate.flat + roll * plate.r_scale
    reduction = max(0, base_reduction - plate.degradation)
    
    if is_ap:
        reduction = math.ceil(reduction / 2)
        
    remaining = incoming_dmg - reduction
    
    if remaining > 0:
        plate.degradation += 1
        
    return max(0, remaining)

def sim_combat(loadout, damage, target_stress=35, max_turns=500, is_ap=False):
    # loadout is a list of ArmorPlate objects, ordered outside-in
    plates = [p.copy() for p in loadout]
    stress = 0
    
    for turn in range(1, max_turns + 1):
        dmg = damage
        for p in plates:
            if dmg <= 0: break
            dmg = reduce_damage(p, dmg, is_ap)
            
        if dmg > 0:
            stress += dmg
            if stress >= target_stress:
                return turn
    return float('inf')

def mc_armor(loadout, damage, is_ap=False, iterations=1000):
    total = 0
    kills = 0
    for _ in range(iterations):
        turns = sim_combat(loadout, damage, 35, 500, is_ap)
        if turns != float('inf'):
            total += turns
            kills += 1
    if kills == 0: return float('inf')
    return total / kills
