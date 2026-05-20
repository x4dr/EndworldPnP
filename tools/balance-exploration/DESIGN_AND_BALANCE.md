# Endworld Heat System: Design & Balance

This document outlines the mechanical levers (knobs), balancing methodology, and tier-defining components for the Endworld Mecha Heat System. It is the result of extensive algorithmic simulation of over 100,000 potential loadouts to ensure mathematical integrity and archetype separation.

## 1. The Core Knobs (Mechanical Levers)

The heat system relies on balancing four primary resources against a strict Tonnage and Hardpoint budget.

*   **Total Flux (The Throughput Tax)**: Before heat can be stored or dissipated, it must enter the flux pool. Sinks like the `Water Reservoir` have massive capacity but terrible flux. If a mech generates 70 heat but only has 30 flux, it is immediately *Flux Capped* and takes damage. To utilize heavy sinks, players are forced to pay the "Flux Tax" by dedicating tonnage to pipe systems like `Liquid Metal Loops` or `Heatpipes`.
*   **Capacity (The Soak)**: Determines how much raw heat a mech can store before failing. High capacity defines the **Type A (Endurance)** archetype.
*   **Active Cooling**: Flat heat removal per turn. Highly restricted by Hardpoints and Energy. Scaling this up is the only way to achieve **Type B (Cooling)** status (infinite equilibrium at medium heat loads).
*   **Fractional Bleed (Passive Division)**: Sinks passively bleed a fraction of their stored heat (e.g., 1/25th of stored heat per turn). This prevents mechs from permanently holding heat but is intentionally kept low so it doesn't accidentally provide "infinite" cooling without active dissipators.

## 2. The Archetypes

The simulation categorizes mechs into three distinct tactical roles:

1.  **Type A (Endurance)**: Focuses on massive Capacity and Flux. They can survive extreme heat spikes (High Heat) for a long, finite duration. However, because they lack Active Cooling, they will eventually overheat even at Medium Heat.
2.  **Type B (Cooling)**: Focuses on Active Cooling and Hardpoint optimization. They can sustain Medium Heat indefinitely (`inf`). However, they sacrifice Capacity to do so, meaning severe heat spikes (High Heat) will overwhelm them rapidly.
3.  **Type C (Balanced)**: The middle ground. Finite at both Medium and High heat, utilizing a blend of active vents and buffer sinks to stay versatile.

## 3. Tier-Defining Components

As mechs progress through Tech Levels (TL) and Chassis Weights (Tonnage / HP), specific components define the meta for that bracket.

### Lowtech (TL 2)
*Lowtech is characterized by extreme bulk, flux starvation, and reliance on brute force.*
*   **Water Reservoir**: The absolute king of raw capacity (80/t). It is the only way for Lowtech mechs to survive heat spikes, but its terrible flux (5) means it requires extensive pipe networks to function at higher loads.
*   **Radiator Vent**: The baseline active cooler (10 Act / 0.5t / 1 HP). Efficient per ton, but eats up precious hardpoints.

### Midtech (TL 3)
*Midtech introduces the "plumbing" that makes heavy mechs viable, and the "anchor" that saves hardpoints.*
*   **Heat Exchanger (HE)**: The ultimate Heavy Mech anchor. At 5 tons and 1 HP, it provides a massive 35 Active Cooling. It is terrible per-ton, but incredibly efficient per-hardpoint, making it mandatory for Heavy mechs that only have 2 or 3 Hardpoints available for heat management.
*   **Phase Change Cell (PCC)**: A balanced sink that trades raw capacity (50) for better built-in flux (10), reducing the "Flux Tax".
*   **Heatpipes / Phase Change Loop**: Essential mid-game throughput enablers (15 Flux/ton).

### Hightech (TL 4)
*Hightech is defined by extreme density, allowing for specialized min-maxing.*
*   **Electrochromic Dissipator (ED)**: A glass cannon. Provides 11 Active Cooling and 11 Capacity for just 0.5t and 1 HP. It has 0 Flux and costs 5 Energy. It is the most dense cooling system in the game (22 cooling/ton), perfect for pushing Type B builds into "infinite" territory.
*   **Liquid Metal Loop (LML)**: The ultimate throughput solution (30 Flux/ton). Completely eliminates the Flux Tax for a single ton.
*   **Thermal Capacitor (TC)**: The ultimate dense buffer (60 Cap / 8 Flux).

## 4. Special Interactions: Radiator Wings

`Radiator Wings` fill a highly specific tactical niche: **Out-of-combat / Vulnerable Cooling**.
*   **Stats**: 1t, 50 Capacity, 1/4 Fractional Bleed (Active).
*   **Mechanic**: When deployed, they act as massive radiators, bleeding up to ~12.5 heat per turn. They require 0 Energy and 0 Hardpoints.
*   **Balance**: If used safely (behind shields or cover), they provide unparalleled mathematical value—a single ton gives more cooling than an `ED`, while also providing 50 capacity. They are intentionally "overpowered" in a spreadsheet, balanced entirely by the narrative/combat risk that they are outside of armor and vulnerable to being instantly destroyed if the mech takes a hit while they are deployed.

## 5. Consumable Cooling (Cargo as Heat Sink)
Consumable cooling offers a distinct progression path across tech levels. It trades away long-term logistical stamina (by rapidly burning through Cargo capacity with water/coolant) to instantly solve heat problems without relying on a bulky internal sink network.

*   **TL 1: Blowoff Valve** (0.5t, 1 HP, 0 E). *Boot 0 / Shutoff 0.*
    Provides 15 Active Cooling, consuming 15kg/turn. The ultimate zero-energy panic button. It eats a Hardpoint and screams your location, but provides massive burst cooling.
*   **TL 2: Anti-Detonant Injector (ADI)** (2.0t, 0 HP, 5 E). *Boot 1 / Shutoff 0.*
    Provides 15 Active Cooling, consuming 15kg/turn. Frees up the hardpoint but requires bulky industrial piping (2.0t) and constant power to run.
*   **TL 3: Coolant Dump** (1.0t, 0 HP, 25 E). *Boot 1 / Shutoff 1.*
    Provides 25 Active Cooling, consuming 25kg/turn. Highly efficient for its weight, but requires a heavy energy toll (25 E), forcing pilots to juggle their power budgets to trigger the high-pressure flush.
*   **TL 4: Evaporative Cooling System (ECCS)** (0.5t, 0 HP, 20 E). *Boot 0 / Shutoff 2.*
    Provides an astounding 40 Active Cooling, consuming 40kg/turn. It is mathematically terrifying, but the **Shutoff 2** timer means it is an absolute commitment. Toggling it on guarantees at least 3 turns of operation (120 cooling, 120kg cargo). If used recklessly for a minor heat spike, it bleeds logistical reserves dry instantly.

## 6. Weapon Keywords & Tactical Niches

Weapon keywords are designed to bypass or interact with the defensive mechanics in specific ways. 

*   **Armor Piercing (AP)**: Mathematically cuts armor effectiveness in half. Because thick armor plates provide exponential protection (blocking 15-20 damage), AP is the only way to reliably core heavy mechs. AP weapons should be balanced by having lower raw damage than peer non-AP weapons, or relying on rare/expensive ammo.
*   **Rapid Fire**: Doubling the fire rate is excellent for chewing through Shields (which drop when overwhelmed) or ablative armor (which degrades per hit). However, because the raw damage is split into two weaker hits, it is mathematically terrible against thick, intact armor plates due to the square root damage reduction.
*   **Blast X**: Punishes mechs that front-load all their armor on the facing sector by bleeding damage into the lightly armored adjacent/internal sectors. Blast weapons should have slightly lower main-target damage to compensate for the splash.
*   **Overcharge X**: Provides a dual-mode weapon. It allows a weapon to fire efficiently (low heat, moderate damage) for sustained combat, but allows the pilot to spike the damage to penetrate heavy armor at the cost of a massive, pre-defined heat penalty. Because the 'X' is fixed by the designer, it prevents players from using their total Flux Pool as an infinite thermal battery to create 'Death Rays'.
