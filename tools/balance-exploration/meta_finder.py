#!/usr/bin/env python3
"""
Exhaustive Meta Finder.
Reads component stats from `meta_config.json`.
Generates all valid combinations of Armor and Weapons within given budgets.
Runs a full cross-matrix Monte Carlo simulation to discover the Meta
(highest- TTK defense, lowest-TTK offense).

Usage:
    uv run python meta_finder.py --armor-budget 4.0 --weapon-mass 6.0 --weapon-e 300 --weapon-heat 30
    uv run python meta_finder.py --armor-budget 4.0 --weapon-mass 6.0 --weapon-e 300 --weapon-heat 30 --iterations 500 --jobs 8
"""
import sys, os, json, math, random, argparse
from multiprocessing import Pool, cpu_count
import itertools

# --- Dice pool ----------------------------------------------------------------
def _build_pool():
    pool = []
    for p in itertools.product(range(1, 11), repeat=5):
        s = sorted(p)
        pool.append(s[1] + s[1])
    return pool

ROLL_POOL = _build_pool()

# --- Armor model --------------------------------------------------------------
class DynamicArmorLayer:
    __slots__ = ("wt", "flat", "rs", "use_one_plus", "degradation")

    def __init__(self, wt, flat, rs, use_one_plus):
        self.wt = wt
        self.flat = flat
        self.rs = rs
        self.use_one_plus = use_one_plus
        self.degradation = 0

    def reduce_damage(self, incoming_dmg, is_ap, roll):
        scale = math.sqrt(self.wt)
        if self.use_one_plus:
            base_red = (self.flat * scale) + roll * (1.0 + self.rs * scale)
        else:
            base_red = (self.flat * scale) + roll * (self.rs * scale)
        reduction = max(0.0, base_red - self.degradation)
        if is_ap:
            reduction = math.ceil(reduction / 2)
        rem = incoming_dmg - reduction
        if rem > 0:
            self.degradation += 1
        return max(0, rem)

# --- Combat simulation --------------------------------------------------------
def sim_combat(w_combo, a_combo, config):
    target_stress = config["settings"]["target_stress"]
    max_turns = config["settings"]["max_turns"]
    atypes = config["armor_types"]
    wtypes = config["weapon_types"]

    layers = [DynamicArmorLayer(wt, atypes[n]["flat"], atypes[n]["rs"],
                                config["settings"]["use_one_plus_roll"])
              for n, wt in a_combo]

    stress = 0
    for turn in range(1, max_turns + 1):
        for w_name, qty in w_combo:
            w = wtypes[w_name]
            for _ in range(qty):
                dmg = w["dmg"]
                is_ap = w["ap"]
                roll = random.choice(ROLL_POOL)
                for layer in layers:
                    dmg = layer.reduce_damage(dmg, is_ap, roll)
                if dmg > 0:
                    stress += dmg
                if stress >= target_stress:
                    return turn
    return float("inf")


def run_mc(w_combo, a_combo, config):
    iters = config["settings"].get("mc_iterations", 200)
    kills = 0
    total_turns = 0.0
    for _ in range(iters):
        t = sim_combat(w_combo, a_combo, config)
        if t != float("inf"):
            kills += 1
            total_turns += t
    if kills == 0:
        return float("inf")
    return total_turns / kills

# --- Loadout generators -------------------------------------------------------
def generate_armor_combos(budget, config):
    types = sorted(config["armor_types"])
    step = config["settings"]["min_armor_slice_tons"]
    max_units = int(budget // step)

    combos = []
    def dfs(idx, remaining, current):
        if remaining == 0:
            if current:
                combos.append(tuple(current))
            return
        if idx >= len(types):
            return
        name = types[idx]
        for q in range(remaining + 1):
            cur = current + [(name, q * step)] if q > 0 else current
            dfs(idx + 1, remaining - q, cur)

    dfs(0, max_units, [])
    return combos


def generate_weapon_combos(mass_budget, e_budget, h_budget, config):
    types = sorted(config["weapon_types"])
    combos_set = set()
    combos = []

    def dfs(idx, rem_m, rem_e, rem_h, current):
        if current:
            canonical = tuple(sorted(current))
            if canonical not in combos_set:
                combos_set.add(canonical)
                combos.append(canonical)
        if idx >= len(types):
            return
        name = types[idx]
        w = config["weapon_types"][name]

        max_q = int(min(
            rem_m // w["wt"],
            rem_e // w["e"] if w["e"] > 0 else float("inf"),
            rem_h // w["heat"] if w["heat"] > 0 else float("inf")
        ))

        for q in range(max_q + 1):
            if q > 0:
                dfs(idx + 1,
                    rem_m - q * w["wt"],
                    rem_e - q * w["e"],
                    rem_h - q * w["heat"],
                    current + [(name, q)])
            else:
                dfs(idx + 1, rem_m, rem_e, rem_h, current)

    dfs(0, mass_budget, e_budget, h_budget, [])
    return combos

# --- Multiprocessing ----------------------------------------------------------
_CONFIG_SHARED = None

def _init_worker(config):
    global _CONFIG_SHARED
    _CONFIG_SHARED = config

def worker(args):
    w_combo, a_combo = args
    ttk = run_mc(w_combo, a_combo, _CONFIG_SHARED)
    return w_combo, a_combo, ttk

# --- Display helpers ----------------------------------------------------------
def fmt_weapon(combo, config):
    parts = []
    total_mass = 0.0
    total_e = 0.0
    total_heat = 0.0
    total_dmg = 0
    for name, qty in combo:
        w = config["weapon_types"][name]
        parts.append(f"{name}x{qty}")
        total_mass += w["wt"] * qty
        total_e += w["e"] * qty
        total_heat += w["heat"] * qty
        total_dmg += w["dmg"] * qty
    return (" + ".join(parts),
            total_mass, total_e, total_heat, total_dmg)

def fmt_armor(combo):
    parts = []
    total_wt = 0.0
    for name, wt in combo:
        parts.append(f"{name}@{wt}t")
        total_wt += wt
    return " + ".join(parts), total_wt

# --- Main ---------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(
        description="Exhaustive meta finder for mecha weapon/armor balance")
    parser.add_argument("--armor-budget", type=float, default=4.0,
                        help="Armor mass budget in tons")
    parser.add_argument("--weapon-mass", type=float, default=6.0,
                        help="Weapon mass budget in tons")
    parser.add_argument("--weapon-e", type=float, default=300.0,
                        help="Weapon energy budget")
    parser.add_argument("--weapon-heat", type=float, default=30.0,
                        help="Weapon heat budget")
    parser.add_argument("--iterations", type=int, default=None,
                        help="Override MC iterations in config")
    parser.add_argument("--jobs", type=int, default=None,
                        help="Worker count (default: cpu_count)")
    parser.add_argument("--top-n", type=int, default=5,
                        help="Show top N results (default: 5)")
    parser.add_argument("--config", type=str, default="meta_config.json",
                        help="Config file path (default: meta_config.json)")
    parser.add_argument("--export-csv", type=str, default=None,
                        help="Export full match-up matrix to CSV")
    args = parser.parse_args()

    cfg_path = os.path.join(os.path.dirname(__file__), args.config) \
        if not os.path.isabs(args.config) else args.config
    with open(cfg_path) as f:
        config = json.load(f)

    if args.iterations is not None:
        config["settings"]["mc_iterations"] = args.iterations

    print("Generating loadouts ...")
    a_combos = generate_armor_combos(args.armor_budget, config)
    w_combos = generate_weapon_combos(args.weapon_mass, args.weapon_e,
                                      args.weapon_heat, config)

    matchups = len(w_combos) * len(a_combos)
    print(f"  Weapons: {len(w_combos)}   Armors: {len(a_combos)}   "
          f"Match-ups: {matchups}")

    print("Running cross-matrix Monte Carlo simulation ...")
    tasks = [(w, a) for w in w_combos for a in a_combos]
    n_jobs = args.jobs or cpu_count()
    with Pool(n_jobs, initializer=_init_worker, initargs=(config,)) as p:
        results = p.map(worker, tasks)

    # --- Aggregate by weapon ------------------------------------------------
    w_scores: dict[tuple, list[float]] = {w: [] for w in w_combos}
    a_scores: dict[tuple, list[float]] = {a: [] for a in a_combos}

    for w, a, ttk in results:
        w_scores[w].append(ttk)
        a_scores[a].append(ttk)

    # --- Offensive meta -----------------------------------------------------
    w_avg = []
    for w, ttks in w_scores.items():
        finite = [t for t in ttks if t != float("inf")]
        if not finite:
            avg = float("inf")
        else:
            avg = sum(finite) / len(finite)
        w_avg.append((w, avg, len(ttks) - len(finite)))
    w_avg.sort(key=lambda x: x[1])

    budget_str = (f"mass={args.weapon_mass}t  E={args.weapon_e}  "
                  f"heat={args.weapon_heat}")
    print(f"\n{'=' * 70}")
    print(f"  OFFENSIVE META   ({budget_str})")
    print(f"{'=' * 70}")
    print(f"{'Loadout':<50} {'dmg/t':>6} {'TTK':>6}  {'M':>4} {'E':>5} {'H':>4}")
    print("-" * 80)
    for w, avg, inv in w_avg[:args.top_n]:
        label, mass, e, h, dmg = fmt_weapon(w, config)
        dpt = dmg / mass if mass > 0 else 0
        avg_str = f"{avg:.2f}" if avg != float("inf") else "  inf"
        inv_str = f" *{inv}sk" if inv else ""
        print(f"{label:<48} {dpt:>6.1f} {avg_str:>6}  {mass:>4.0f} {e:>5.0f} {h:>4.0f}{inv_str}")

    # --- Defensive meta -----------------------------------------------------
    a_avg = []
    for a, ttks in a_scores.items():
        finite = [t for t in ttks if t != float("inf")]
        if not finite:
            avg = float("inf")
        else:
            avg = sum(finite) / len(finite)
        a_avg.append((a, avg, len(ttks) - len(finite)))
    a_avg.sort(key=lambda x: (x[2], x[1]), reverse=True)

    print(f"\n{'=' * 70}")
    print(f"  DEFENSIVE META   (armor budget={args.armor_budget}t)")
    print(f"{'=' * 70}")
    print(f"{'Loadout':<48} {'TTK':>6}  {'Wt':>4}")
    print("-" * 60)
    for a, avg, inv in a_avg[:args.top_n]:
        label, wt = fmt_armor(a)
        avg_str = f"{avg:.2f}" if avg != float("inf") else "  inf"
        inv_str = f" *{inv}inv" if inv else ""
        print(f"{label:<46} {avg_str:>6}  {wt:>4.1f}{inv_str}")

    # --- Offensive histogram (TTK distribution across armors) ---------------
    print(f"\n{'─' * 70}")
    print("  TTK Distribution Across Armors (Top 3 weapons)")
    print(f"{'─' * 70}")
    w_hist = w_avg[:min(3, len(w_avg))]
    for w, avg, inv in w_hist:
        ttks = w_scores[w]
        label, *_ = fmt_weapon(w, config)
        buckets = {"< 3": 0, "3-5": 0, "5-10": 0, "> 10": 0, "inf": 0}
        for t in ttks:
            if t == float("inf"):
                buckets["inf"] += 1
            elif t < 3:
                buckets["< 3"] += 1
            elif t < 5:
                buckets["3-5"] += 1
            elif t < 10:
                buckets["5-10"] += 1
            else:
                buckets["> 10"] += 1
        pcts = {k: v / len(ttks) * 100 for k, v in buckets.items()}
        print(f"\n{label}")
        print(f"  Avg TTK: {avg:.2f}")
        for k in ("< 3", "3-5", "5-10", "> 10", "inf"):
            bar = "█" * int(pcts[k] / 5)
            print(f"  {k:>5}: {bar} {pcts[k]:.0f}%")

    # --- Defensive histogram -------------------------------------------------
    print(f"\n{'─' * 70}")
    print("  TTK Distribution Across Weapons (Top 3 armors)")
    print(f"{'─' * 70}")
    a_hist = a_avg[:min(3, len(a_avg))]
    for a, avg, inv in a_hist:
        ttks = a_scores[a]
        label, wt = fmt_armor(a)
        buckets = {"< 3": 0, "3-5": 0, "5-10": 0, "> 10": 0, "inf": 0}
        for t in ttks:
            if t == float("inf"):
                buckets["inf"] += 1
            elif t < 3:
                buckets["< 3"] += 1
            elif t < 5:
                buckets["3-5"] += 1
            elif t < 10:
                buckets["5-10"] += 1
            else:
                buckets["> 10"] += 1
        pcts = {k: v / len(ttks) * 100 for k, v in buckets.items()}
        print(f"\n{label}")
        print(f"  Avg TTK: {avg:.2f}")
        for k in ("< 3", "3-5", "5-10", "> 10", "inf"):
            bar = "█" * int(pcts[k] / 5)
            print(f"  {k:>5}: {bar} {pcts[k]:.0f}%")

    # --- CSV export ------------------------------------------------------------
    if args.export_csv:
        import csv
        csv_path = os.path.join(os.path.dirname(__file__), args.export_csv)
        with open(csv_path, "w", newline="") as f:
            wr = csv.writer(f)
            header = ["weapon", "mass", "e", "heat", "total_dmg",
                      "armor", "armor_wt", "ttk"]
            wr.writerow(header)
            for w, a, ttk in results:
                w_label, wm, we, wh, wd = fmt_weapon(w, config)
                a_label, aw = fmt_armor(a)
                wr.writerow([
                    w_label, f"{wm:.1f}", f"{we:.0f}", f"{wh:.0f}", wd,
                    a_label, f"{aw:.1f}",
                    f"{ttk:.3f}" if ttk != float("inf") else "inf"
                ])
        print(f"\nExported {len(results)} match-ups to {csv_path}")


if __name__ == "__main__":
    main()
