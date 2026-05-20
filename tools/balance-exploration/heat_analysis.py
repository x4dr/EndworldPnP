#!/usr/bin/env python3
"""
Analyzes generated configurations against low, mid, and high heat bands.
Sorts configurations into Archetypes (Endurance, Cooling, Balanced) and checks design goals.

Usage:
  uv run python gen_configs.py | uv run python heat_analysis.py --low 40 --mid 55 --high 70
"""
import sys, re, os
sys.path.insert(0, os.path.dirname(__file__))
from heat_sim import I, test_sim, summary

CODES = {
    "HE": "Heat Exchanger", "HP": "Heatpipes", "W": "Water Reservoir",
    "V": "Radiator Vent", "PCC": "Phase Change Cell", "PCL": "Phase Change Loop",
    "CD": "Coolant Dump", "ED": "Electrochromic Dissipator", "LML": "Liquid Metal Loop",
    "RB": "Refractory Block", "RW": "Radiator Wings", "TC": "Thermal Capacitor",
    "WC": "Water cooling", "BV": "Blowoff Valve", "ADI": "Anti-Detonant Injector", "ECCS": "ECCS",
}
PER_TON = {"Water Reservoir", "Phase Change Cell", "Refractory Block", "Thermal Capacitor"}

def fmt(r):
    if r is None: return "fx"
    if r == 0: return "inf"
    return str(r)

if __name__ == "__main__":
    low_h, mid_h, high_h = 20.0, 40.0, 60.0
    max_energy = 50
    args = sys.argv[1:]
    i = 0
    while i < len(args):
        if args[i] == "--low" and i + 1 < len(args): low_h = float(args[i+1]); i += 2
        elif args[i] == "--mid" and i + 1 < len(args): mid_h = float(args[i+1]); i += 2
        elif args[i] == "--high" and i + 1 < len(args): high_h = float(args[i+1]); i += 2
        elif args[i] == "--max-energy" and i + 1 < len(args): max_energy = int(args[i+1]); i += 2
        else: i += 1

    pool_a, pool_b, pool_c = [], [], []
    failed, total = 0, 0

    for line in sys.stdin:
        line = line.strip()
        if not line: continue
        total += 1
        parts = []
        for token in line.split():
            m = re.match(r"^([A-Za-z]+)(?:x([\d.]+))?$", token)
            if not m: parts = None; break
            code, raw_qty = m.group(1), m.group(2)
            name = CODES.get(code)
            if not name: parts = None; break
            qty = float(raw_qty) if raw_qty else 1
            if raw_qty is None and name not in PER_TON:
                parts.extend(I(name))
            else:
                parts.extend(I(name, qty))
        if not parts: failed += 1; continue

        rl = test_sim(parts, low_h)
        rm = test_sim(parts, mid_h)
        rh = test_sim(parts, high_h)

        if rl != 0:
            failed += 1
            continue

        e = sum(s.energy_cost() for s in parts)
        if e > max_energy:
            failed += 1
            continue
        flx = sum(s.flux_val() for s in parts)
        cap = sum(s.max_cap() for s in parts)
        act = sum(s.active for s in parts)
        hp = sum(1 for s in parts if s.hardpoint)

        # Type A: sink endurance. Score = high heat turns.
        if rh == 0: sa = 999
        elif rh is None: sa = -1
        else: sa = rh
        pool_a.append((line, sa, rm, rh, e, flx, cap, act, hp))

        # Type B: cooling. Score = (mid, high) turns.
        sb = (rm, rh)
        pool_b.append((line, sb, rm, rh, e, flx, cap, act, hp))

        # Type C: balanced, finite at mid. Score = average of mid + high turns.
        if rm is not None and rm != 0 and rh is not None and rh != 0:
            sc = (rm + rh) / 2
            pool_c.append((line, sc, rm, rh, e, flx, cap, act, hp))

    # Sort A by high heat (descending)
    pool_a.sort(key=lambda x: -x[1])
    
    # Sort B by mid (0 inf -> first), then high (descending)
    pool_b.sort(key=lambda x: (
        x[2] != 0, 
        -(x[2] if x[2] is not None else -1),
        x[3] != 0, 
        -(x[3] if x[3] is not None else -1)
    ))
    
    # Sort C by average (descending)
    pool_c.sort(key=lambda x: -x[1])

    print(f"Configs: {total} | Failed: {failed} | Type A: {len(pool_a)} | Type B: {len(pool_b)} | Type C: {len(pool_c)}")
    print()

    for label, pool in [
        ("TYPE A (Endurance) score=high_turns", pool_a),
        ("TYPE B (Cooling) score=mid,high", pool_b),
        ("TYPE C (Balanced) score=avg_turns", pool_c),
    ]:
        print(f"=== {label} ===")
        print(f"{'score':>8}  {'mid':>6}  {'high':>6}  {'E':>5}  {'flux':>4}  {'cap':>4}  {'act':>4}  HP  config")
        for cfg, s, rm, rh, e, flx, cap, act, hp in pool[:10]:
            score_str = f"{s[0]},{s[1]}" if isinstance(s, tuple) else f"{s:.1f}"
            print(f"{score_str:>8}  {fmt(rm):>6}  {fmt(rh):>6}  {e:>5}  {flx:>4}  {cap:>4}  {act:>4}  {hp:>2}  {cfg}")
        print()

    # --- Design Goals Check ---
    print("=== DESIGN GOALS CHECK ===")
    has_inf_a = any(rm == 0 for _, _, rm, _, _, _, _, _, _ in pool_a[:10])
    print(f"1. A has infinite mid: {'YES (Average cooling too high)' if has_inf_a else 'NO'}")

    high_a = [rh for _, _, _, rh, _, _, _, _, _ in pool_a[:10] if rh is not None and rh != 0]
    high_b = [rh for _, _, _, rh, _, _, _, _, _ in pool_b[:10] if rh is not None and rh != 0]
    avg_ha = sum(high_a) / len(high_a) if high_a else 0
    avg_hb = sum(high_b) / len(high_b) if high_b else 0
    print(f"2. A high heat ({avg_ha:.1f}) > B high heat ({avg_hb:.1f}): {'YES' if avg_ha > avg_hb else 'NO (Capacities too low)'}")

    avg_a_score = sum(s for _, s, _, _, _, _, _, _, _ in pool_a[:10]) / len(pool_a[:10]) if pool_a[:10] else 0
    avg_b_score = sum(s[1] for _, s, _, _, _, _, _, _, _ in pool_b[:10] if s[1] is not None and s[1] != 0) / len(pool_b[:10]) if pool_b[:10] else 0
    avg_c_score = sum(s for _, s, _, _, _, _, _, _, _ in pool_c[:10]) / len(pool_c[:10]) if pool_c[:10] else 0
    
    print(f"3. Strategy differentiation (B:{avg_b_score:.1f} < C:{avg_c_score:.1f} < A:{avg_a_score:.1f}): {'YES' if avg_b_score < avg_c_score < avg_a_score else 'NO'}")
