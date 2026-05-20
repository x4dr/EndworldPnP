#!/usr/bin/env python3
"""
Calculates the Absolute Maximum Effective Dissipation (Fully Soaked) for mechs.
Can be used to generate the full grid (1-15 tons, 1-4 HP) or calculate autobands
(-30%, -10%, +10%) for a specific budget and hardpoint limit.

Usage:
  # Full grid
  uv run python calc_peak_dissipation.py
  
  # Specific build autobands
  uv run python calc_peak_dissipation.py --budget 10 --max-hp 3
"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from heat_sim import I

def get_stats(sys_name):
    s = I(sys_name)[0]
    pd = s.passive
    if s.passive_div > 0:
        pd += s.max_cap() / s.passive_div
    return {
        'w': int(s.weight * 2),
        'h': 1 if s.hardpoint else 0,
        'f': s.flux_val(),
        'd': s.active + pd,
        'e': s.energy_cost()
    }

components = ["HE", "ED", "V", "W", "PCC", "TC", "LML", "HP", "PCL", "WC", "BV", "ADI", "CD", "ECCS"]
c_map = {
    "HE": "Heat Exchanger", "ED": "Electrochromic Dissipator", "V": "Radiator Vent",
    "W": "Water Reservoir", "PCC": "Phase Change Cell", "TC": "Thermal Capacitor",
    "LML": "Liquid Metal Loop", "HP": "Heatpipes", "PCL": "Phase Change Loop",
    "WC": "Water cooling", "BV": "Blowoff Valve", "ADI": "Anti-Detonant Injector", 
    "CD": "Coolant Dump", "ECCS": "ECCS"
}

c_stats = {c: get_stats(c_map[c]) for c in components}

MAX_T = 15
MAX_W = MAX_T * 2
MAX_H = 4

dp = [[ [] for _ in range(MAX_H + 1)] for _ in range(MAX_W + 1)]
dp[0][0].append((0, 0, 0, {}))

def pareto(lst):
    flt = []
    for i, a in enumerate(lst):
        dom = False
        for j, b in enumerate(lst):
            if i == j: continue
            if b[0] >= a[0] and b[1] >= a[1] and b[2] <= a[2]:
                if b[0] == a[0] and b[1] == a[1] and b[2] == a[2] and j < i:
                    dom = True
                    break
                if b[0] > a[0] or b[1] > a[1] or b[2] < a[2]:
                    dom = True
                    break
        if not dom:
            flt.append(a)
    return flt

for w in range(MAX_W + 1):
    for h in range(MAX_H + 1):
        for c in components:
            st = c_stats[c]
            pw = w - st['w']
            ph = h - st['h']
            if pw >= 0 and ph >= 0:
                for pf, pd, pe, pcfg in dp[pw][ph]:
                    ncfg = dict(pcfg)
                    ncfg[c] = ncfg.get(c, 0) + 1
                    dp[w][h].append((pf + st['f'], pd + st['d'], pe + st['e'], ncfg))
        if dp[w][h]:
            dp[w][h] = pareto(dp[w][h])

def get_peak(t_budget, hp_limit, max_energy, max_tl=5):
    w_limit = int(t_budget * 2)
    best_eff = -1
    best_state = None
    
    # TL mapping
    TL = {"HE": 3, "ED": 4, "V": 2, "W": 2, "PCC": 3, "TC": 4, "LML": 4, "HP": 3, "PCL": 3, "WC": 2, "BV": 1, "ADI": 2, "CD": 3, "ECCS": 4}
    
    for pw in range(w_limit + 1):
        for ph in range(hp_limit + 1):
            for f, d, e, cfg in dp[pw][ph]:
                # Check TL
                valid_tl = True
                for c in cfg:
                    if TL.get(c, 1) > max_tl:
                        valid_tl = False
                        break
                if not valid_tl:
                    continue
                    
                if e <= max_energy:
                    eff = min(f, d)
                    if eff > best_eff:
                        best_eff = eff
                        best_state = (eff, f, d, e, cfg)
    return best_state

if __name__ == "__main__":
    args = sys.argv[1:]
    if "--budget" in args and "--max-hp" in args:
        b = float(args[args.index("--budget")+1])
        h = int(args[args.index("--max-hp")+1])
        max_e = b * 5
        max_tl = int(args[args.index("--max-tl")+1]) if "--max-tl" in args else 5
        
        state = get_peak(b, h, max_e, max_tl)
        if state:
            eff, f, d, e, cfg = state
            bstr = " + ".join([f"{k}x{v}" if v > 1 else k for k,v in cfg.items()])
            print(f"Scenario: {b}t Budget, {h} HP, Max Energy {max_e}")
            print(f"Peak Dissipation: {eff:.2f} ({bstr})")
            print(f"Autobands (-30%, -10%, +10%):")
            print(f"  Low:  {eff * 0.70:.2f}")
            print(f"  Mid:  {eff * 0.90:.2f}")
            print(f"  High: {eff * 1.10:.2f}")
        else:
            print("No valid configurations found.")
    else:
        print("Absolute Maximum Effective Dissipation Grid (Fully Soaked)")
        print("--------------------------------------------------------------------------------")
        print(f"{'Ton':<3} | {'HP':<2} | {'MaxE':<4} || {'Eff_Diss':<8} | {'Flux':<4} | {'Raw_Diss':<8} | {'Build'}")
        print("-" * 80)
        for t in range(1, MAX_T + 1):
            for h in range(1, MAX_H + 1):
                state = get_peak(t, h, t * 5)
                if state and state[0] > 0:
                    eff, f, d, e, cfg = state
                    bstr = " + ".join([f"{k}x{v}" if v > 1 else k for k,v in cfg.items()])
                    print(f"{t:<3} | {h:<2} | {t*5:<4} || {eff:<8.1f} | {f:<4.0f} | {d:<8.1f} | {bstr}")
                else:
                    print(f"{t:<3} | {h:<2} | {t*5:<4} || {'0.0':<8} | {'0':<4} | {'0.0':<8} | None")
