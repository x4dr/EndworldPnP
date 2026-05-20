import math

def calc_reduction(wt):
    scale = math.sqrt(wt)
    # Using Avg Roll = 9, Roll Scale = 0.9
    return (2 * scale) + 9 * (0.9 * scale)

def test_hit(dmg, layers, spalling=0):
    current_dmg = dmg
    for wt in layers:
        reduction = calc_reduction(wt)
        current_dmg = current_dmg - reduction
        if current_dmg > 0:
            current_dmg += spalling # The penetrated armor becomes shrapnel
        else:
            current_dmg = 0
            break
    return max(0, current_dmg)

print("=== THE SPALLING MECHANIC TEST ===")
print("Comparing 1x 4.0t Plate vs 2x 2.0t Plates against a 25 Dmg Heavy Hit.")
print(f"1x 4.0t Plate Reduction: {calc_reduction(4.0):.1f}")
print(f"1x 2.0t Plate Reduction: {calc_reduction(2.0):.1f}")
print("-" * 65)
print(f"{'Spalling Dmg':<15} | {'Dmg thru 1x 4t':<18} | {'Dmg thru 2x 2t'}")
print("-" * 65)

for spall in [0, 2, 4, 5, 6, 8, 10]:
    dmg_1x = test_hit(25, [4.0], spall)
    dmg_2x = test_hit(25, [2.0, 2.0], spall)
    print(f"+{spall:<14} | {dmg_1x:<18.1f} | {dmg_2x:<18.1f}")

