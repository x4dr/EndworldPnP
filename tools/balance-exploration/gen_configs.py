#!/usr/bin/env python3
"""
Generates valid heat system configurations based on budget and hardpoint limits.

Usage:
  uv run python gen_configs.py --budget 10 --max-hp 3 --max-tl 4
"""
import sys

# (code, weight, max_q, hp_used, flux_per_unit, tech_level)
COM = [
    ("RB", 1, 10, 0, 0.5, 1),
    ("W", 1, 10, 0, 1, 2),
    ("WC", 0.5, 10, 0, 5, 2),
    ("V", 0.5, 20, 1, 5, 2),
    ("PCC", 1, 10, 0, 5, 3),
    ("PCL", 1, 10, 0, 15, 3),
    ("HP", 1, 10, 0, 15, 3),
    ("HE", 5, 1, 1, 15, 3),
    ("TC", 1, 10, 0, 8, 4),
    ("LML", 1, 10, 0, 30, 4),
    ("ED", 0.5, 20, 1, 0, 4),
]

STEP = 0.5

def total_flux(selection):
    f = 0
    for (_, weight, _, _, fpu, _), qty in zip(COM, selection):
        if qty == 0: continue
        f += qty * (fpu // 2 if fpu == 0.5 else fpu)
    return f

def param(selection):
    parts = []
    for (code, _, _, _, _, _), qty in zip(COM, selection):
        if qty > 0:
            parts.append(f"{code}x{qty}" if qty > 1 else code)
    return " ".join(parts)

def generate(budget=10.0, max_hp=3, min_flux=0, max_tl=5):
    max_units = int(budget / STEP)
    def dfs(idx, remaining, selection, hp):
        if hp > max_hp: return
        if idx == len(COM):
            if remaining == 0 and any(q > 0 for q in selection):
                if total_flux(selection) >= min_flux:
                    yield param(selection)
            return

        code, weight, max_q, hp_used, fpu, tl = COM[idx]
        if tl > max_tl: # Skip if TL too high
            yield from dfs(idx + 1, remaining, selection, hp)
            return
        
        w = int(weight / STEP)
        max_possible = min(max_q, remaining // w)
        for qty in range(max_possible + 1):
            selection.append(qty)
            yield from dfs(idx + 1, remaining - qty * w, selection, hp + qty * hp_used)
            selection.pop()
    yield from dfs(0, max_units, [], 0)

if __name__ == "__main__":
    budget = 10.0
    min_flux = 0
    max_hp = 3
    max_tl = 5
    args = sys.argv[1:]
    i = 0
    while i < len(args):
        if args[i] == "--budget": budget = float(args[i+1]); i += 2
        elif args[i] == "--min-flux": min_flux = int(args[i+1]); i += 2
        elif args[i] == "--max-hp": max_hp = int(args[i+1]); i += 2
        elif args[i] == "--max-tl": max_tl = int(args[i+1]); i += 2
        else: i += 1
    for cfg in generate(budget, max_hp, min_flux, max_tl):
        print(cfg)
