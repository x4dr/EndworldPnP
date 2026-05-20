#!/usr/bin/env python3
import sys, re, os
sys.path.insert(0, os.path.dirname(__file__))
from armor_sim import get_plate, mc_armor

def fmt(r):
    if r == float('inf'): return "inf"
    return f"{r:.1f}"

if __name__ == "__main__":
    low_d, mid_d, high_d = 12, 16, 22
    args = sys.argv[1:]
    i = 0
    while i < len(args):
        if args[i] == "--low" and i + 1 < len(args): low_d = int(args[i+1]); i += 2
        elif args[i] == "--mid" and i + 1 < len(args): mid_d = int(args[i+1]); i += 2
        elif args[i] == "--high" and i + 1 < len(args): high_d = int(args[i+1]); i += 2
        else: i += 1

    results = []
    
    for line in sys.stdin:
        line = line.strip()
        if not line: continue
        
        loadout = []
        for token in line.split():
            m = re.match(r"^([A-Za-z]+)(?:x([\d]+))?$", token)
            if not m: continue
            name, raw_qty = m.group(1), m.group(2)
            qty = int(raw_qty) if raw_qty else 1
            loadout.extend(get_plate(name, qty))
            
        if not loadout: continue
        
        ttk_low = mc_armor(loadout, low_d)
        ttk_mid = mc_armor(loadout, mid_d)
        ttk_high = mc_armor(loadout, high_d, is_ap=True) # High damage band gets AP
        
        # Score is primarily mid-band survival, then high-band
        score = ttk_mid if ttk_mid != float('inf') else 9999
        results.append((line, score, ttk_low, ttk_mid, ttk_high))
        
    results.sort(key=lambda x: -x[1]) # Sort descending by mid-band TTK
    
    print(f"=== DISCRETE ARMOR ANALYSIS ===")
    print(f"Incoming Damage -> Low: {low_d} | Mid: {mid_d} | High: {high_d} (AP)")
    print(f"{'Config':<40} | {'Low TTK':<10} | {'Mid TTK':<10} | {'High TTK (AP)':<15}")
    print("-" * 85)
    
    for cfg, score, tl, tm, th in results:
        print(f"{cfg:<40} | {fmt(tl):<10} | {fmt(tm):<10} | {fmt(th):<15}")

