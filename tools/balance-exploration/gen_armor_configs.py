#!/usr/bin/env python3
import sys

COM = [
    ("UltraPlate", 8.0),
    ("HeavyPlate", 4.0),
    ("StandardPlate", 2.0),
    ("LightPlate", 1.0),
    ("ScrapPlate", 0.5)
]

def generate(budget):
    def dfs(idx, remaining, current):
        if abs(remaining) < 0.1:
            yield current
            return
        if idx >= len(COM) or remaining < 0:
            return
            
        name, wt = COM[idx]
        max_qty = int(remaining // wt)
        
        for q in range(max_qty, -1, -1):
            if q > 0:
                yield from dfs(idx + 1, remaining - (q * wt), current + [(name, q)])
            else:
                yield from dfs(idx + 1, remaining, current)

    for cfg in dfs(0, budget, []):
        parts = []
        for name, q in cfg:
            parts.append(f"{name}x{q}" if q > 1 else name)
        print(" ".join(parts))

if __name__ == "__main__":
    budget = 4.0
    if len(sys.argv) > 1:
        budget = float(sys.argv[1])
    generate(budget)
