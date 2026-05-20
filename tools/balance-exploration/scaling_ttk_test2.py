#!/usr/bin/env python3
import math
import random

def roll_ew(selectors):
    dice = sorted([random.randint(1, 10) for _ in range(5)])
    return sum(dice[min(s, 5) - 1] for s in selectors if s > 0)

class ArmorLayer:
    def __init__(self, wt, roll_scale=0.9, grade=2, structure=2):
        self.wt = wt
        self.grade = grade
        self.structure = structure
        self.roll_scale = roll_scale
        self.degradation = 0

    def reduce_damage(self, incoming_dmg):
        scale = math.sqrt(self.wt)
        roll = roll_ew([self.grade, self.structure])
        base_reduction = (2 * scale) + roll * (self.roll_scale * scale)
        reduction = max(0, base_reduction - self.degradation)
        remaining_dmg = incoming_dmg - reduction
        if remaining_dmg > 0:
            self.degradation += 1
        return max(0, remaining_dmg)

def simulate_combat(dmg, layers_wt, target_stress=35, turns_limit=200):
    layers = [ArmorLayer(w) for w in layers_wt]
    stress = 0
    for turn in range(turns_limit):
        current_dmg = dmg
        for layer in layers:
            current_dmg = layer.reduce_damage(current_dmg)
        if current_dmg > 0:
            stress += current_dmg
        if stress >= target_stress:
            return turn + 1
    return float('inf')

def monte_carlo(dmg, layers_wt, iterations=500):
    kills = 0
    total_turns = 0
    for _ in range(iterations):
        turns = simulate_combat(dmg, layers_wt)
        if turns != float('inf'):
            kills += 1
            total_turns += turns
    if kills == 0: return "inf"
    return f"{total_turns / kills:.1f}"

print("=== SCALING TTK TEST: 10 + 6*sqrt(mass) ===")
print(f"{'Size':<5} | {'Mass':<6} | {'Armor':<6} | {'Gun':<6} | {'Dmg':<4} || {'1-Layer TTK':<12} | {'2-Layer TTK':<12}")
print("-" * 75)

test_sizes = [(5, 10.0, 1.5), (7, 40.0, 4.0), (9, 150.0, 12.5), (11, 500.0, 33.5)]

for size, mass, facing_armor in test_sizes:
    gun_mass = mass * 0.15
    gun_dmg = round(10 + 6 * math.sqrt(gun_mass))
    ttk_1x = monte_carlo(gun_dmg, [facing_armor])
    ttk_2x = monte_carlo(gun_dmg, [facing_armor / 2, facing_armor / 2])
    print(f"{size:<5} | {mass:<5.0f}t | {facing_armor:<5.1f}t | {gun_mass:<5.1f}t | {gun_dmg:<4} || {ttk_1x:<12} | {ttk_2x:<12}")

print("\n=== SCALING TTK TEST: 5 + 8*sqrt(mass) ===")
for size, mass, facing_armor in test_sizes:
    gun_mass = mass * 0.15
    gun_dmg = round(5 + 8 * math.sqrt(gun_mass))
    ttk_1x = monte_carlo(gun_dmg, [facing_armor])
    ttk_2x = monte_carlo(gun_dmg, [facing_armor / 2, facing_armor / 2])
    print(f"{size:<5} | {mass:<5.0f}t | {facing_armor:<5.1f}t | {gun_mass:<5.1f}t | {gun_dmg:<4} || {ttk_1x:<12} | {ttk_2x:<12}")
