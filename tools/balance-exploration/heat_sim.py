#!/usr/bin/env python3
"""
Core simulation logic and component database for the Endworld heat system.

Provides the `System` dataclass, the component database (`I`), and the
`test_sim` function to evaluate a given configuration against a specific heat load.
"""
from dataclasses import dataclass

@dataclass
class System:
    name: str
    per_ton: bool
    half_flux: bool
    capacity: int
    flux: int
    active: int
    passive: int
    passive_div: int
    energy: int
    hardpoint: bool
    weight: float
    qty: float = 1

    def max_cap(self) -> int:
        return int(self.capacity * self.qty) if self.per_ton else self.capacity
    def flux_val(self) -> int:
        if self.half_flux: return int(self.qty) // 2
        return int(self.flux * self.qty) if self.per_ton else self.flux
    def energy_cost(self) -> int:
        return int(self.energy * self.qty) if self.per_ton else self.energy
    def total_weight(self) -> float:
        return self.weight * self.qty

def I(name: str, qty: float = 1) -> list[System]:
    """Retrieves component stats from the database."""
    db = {
        "Refractory Block":       (True,  True,  30, 0,  0, 0, 25, 0, False, 1),
        "Radiator Vent":          (False, False, 10, 5, 10, 1, 0,  5, True,  0.5),
        "Water Reservoir":        (True,  False, 80, 5,  0, 0, 25, 0, False, 1),
        "Water cooling":          (False, False, 5, 5, 0, 0, 0, 3, False, 0.5),
        "Phase Change Cell":      (True,  False, 50, 10, 0, 0, 30, 4, False, 1),
        "Phase Change Loop":      (False, False, 5, 15, 0, 0, 0,  5, False, 1),
        "Heatpipes":              (False, False, 0, 15, 0, 0, 0,  0, False, 1),
        "Blowoff Valve":          (False, False, 15, 15, 15, 0, 0, 0, True, 0.5),
        "Anti-Detonant Injector": (False, False, 15, 15, 15, 0, 0, 5, False, 2.0),
        "Coolant Dump":           (False, False, 25, 25, 25, 0, 0, 25, False, 1.0),
        "ECCS":                   (False, False, 40, 40, 40, 0, 0, 20, False, 0.5),
        "Heat Exchanger":         (False, False, 160,15, 35,0, 0,  50, True,  5),
        "Radiator Wings":         (False, False, 50, 5,  0, 0, 4,  10, False, 1),
        "Thermal Capacitor":      (True,  False, 60, 8,  0, 0, 30, 8, False, 1),
        "Liquid Metal Loop":      (False, False, 10, 30, 0, 0, 0,  15, False, 1),
        "Electrochromic Dissipator":(False,False, 11, 0, 11, 0, 0,  20, True,  0.5),
    }
    pt, hf, cap, flx, act, pas, pdiv, enr, hp, w = db[name]
    data = []
    if pt: data.append(System(name, True, hf, cap, flx, act, pas, pdiv, enr, hp, w, qty))
    else:
        for _ in range(int(qty)): data.append(System(name, False, hf, cap, flx, act, pas, pdiv, enr, hp, w, 1))
    return data

def test_sim(installs, heat_per_turn, max_turns=200):
    """
    Simulates heat load on a configuration over time.
    Returns:
        0 if infinite (equilibrium reached),
        None if flux capped,
        Integer turns until failure.
    """
    total_flux = sum(s.flux_val() for s in installs)
    if heat_per_turn > total_flux: return None
    pool = 0
    stored = [0 for _ in installs]
    for turn in range(1, max_turns + 1):
        can_accept = max(0, total_flux - pool)
        incoming = min(heat_per_turn, can_accept)
        pool += incoming
        residual = heat_per_turn - incoming
        if residual > 0: return turn
        moved = 0
        for i in range(len(installs)):
            if moved >= total_flux: break
            free = max(0, installs[i].max_cap() - stored[i])
            if free <= 0: continue
            take = min(pool, free, total_flux - moved)
            stored[i] += take
            pool -= take
            moved += take
        for i, s in enumerate(installs):
            if s.active > 0: stored[i] = max(0, stored[i] - min(stored[i], s.active))
            if s.passive > 0: stored[i] = max(0, stored[i] - min(stored[i], s.passive))
            if s.passive_div > 0: stored[i] = max(0, stored[i] - stored[i] // s.passive_div)
        pool = max(0, pool)
    return 0

def summary(installs):
    """Generates a text summary of a configuration's stats."""
    t = sum(s.total_weight() for s in installs); f = sum(s.flux_val() for s in installs)
    c = sum(s.max_cap() for s in installs); e = sum(s.energy_cost() for s in installs)
    h = sum(1 for s in installs if s.hardpoint); a = sum(s.active for s in installs)
    b = " + ".join(s.name for s in installs)
    return f"{b} | {t:.1f}t E={e} flux={f} cap={c} active={a} HP={h}"
