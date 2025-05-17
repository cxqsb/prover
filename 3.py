import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import pandas as pd

MINIMUM_BID = 100
MAX_TOTAL_POOL = 22000
STAR_MULTIPLIER = 5

def get_base_stars_v2(p_total):
    if p_total <= 0:
        return 0
    elif p_total <= 5000:
        return 1
    elif p_total <= 7500:
        return 2
    elif p_total <= 16000:
        return 3
    elif p_total <= 17000:
        return 4
    elif p_total <= 18000:
        return 5
    elif p_total <= 19000:
        return 6
    elif p_total <= 22000: 
        return 7
    else: 
        return 0 

def calculate_efficiency_no_rakeback(your_bid_b, others_bid_p_others):
    if your_bid_b < MINIMUM_BID:
        return 0.0

    p_total = your_bid_b + others_bid_p_others

    if p_total <= 0:
        return 0.0
    
    if p_total > MAX_TOTAL_POOL:
        return 0.0 

    base_stars = get_base_stars_v2(p_total)
    if base_stars == 0 and p_total > 0 : 
        return 0.0

    star_prize = base_stars * STAR_MULTIPLIER
    
    # Check for p_total being zero before division, though already handled by earlier check
    if p_total == 0: # Should not be reached if B >= 100 and p_others >= 0
        return 0.0
        
    efficiency = star_prize / p_total 
    return efficiency

# Define ranges for P_others and B
# Increased density for smoother plot surfaces
p_others_plot_range = np.linspace(0, MAX_TOTAL_POOL - MINIMUM_BID, 50) # 50 points
b_plot_range = np.unique(np.concatenate(([MINIMUM_BID, 5000], 
                                          np.logspace(np.log10(MINIMUM_BID), np.log10(5000), 50).astype(int)))) # 50 points for B
b_plot_range = b_plot_range[b_plot_range >= MINIMUM_BID]
b_plot_range.sort()

X_P_others, Y_B = np.meshgrid(p_others_plot_range, b_plot_range)
Z_Efficiency_no_rakeback = np.zeros_like(X_P_others)

for i in range(X_P_others.shape[0]): 
    for j in range(X_P_others.shape[1]): 
        b_val = Y_B[i, j]
        p_o_val = X_P_others[i, j]
        Z_Efficiency_no_rakeback[i, j] = calculate_efficiency_no_rakeback(b_val, p_o_val)
        
# --- Generate Table (Code from previous response, can be kept or removed if only plot is needed now) ---
p_others_table_samples = [0, 1000, 4900, 5000, 7400, 15000, 20000, 21900]
b_table_samples_single_bid = [100, 500, 1000, 2000, 3000, 5000] 

table_output_eff_v2 = [f"--- Efficiency Table (No Rakeback, P_total <= {MAX_TOTAL_POOL}) ---"]
header_eff_v2 = f"{'P_others':<10} | {'Your Bid B':<12} | {'Total Pool P':<12} | {'Star Prize':<12} | {'Efficiency':<20}"
table_output_eff_v2.append(header_eff_v2)
table_output_eff_v2.append("-" * len(header_eff_v2))

for p_o_val in p_others_table_samples:
    for b_val in b_table_samples_single_bid:
        p_tot_val = b_val + p_o_val
        eff_val_str = "0.00000" 
        prize_val = 0

        if b_val >= MINIMUM_BID and p_tot_val <= MAX_TOTAL_POOL and p_tot_val > 0 :
            base_s = get_base_stars_v2(p_tot_val)
            prize_val = base_s * STAR_MULTIPLIER
            eff_s = prize_val / p_tot_val
            eff_val_str = f"{eff_s:.5f}"
        elif b_val < MINIMUM_BID:
            eff_val_str = "Invalid Bid"
        
        table_output_eff_v2.append(f"{p_o_val:<10.0f} | {b_val:<12.0f} | {p_tot_val:<12.0f} | {prize_val:<12} | {eff_val_str:<20}")
    if p_o_val != p_others_table_samples[-1]:
        table_output_eff_v2.append("." * (len(header_eff_v2) - 30))

print("\n".join(table_output_eff_v2))

# --- Generate 3D Plot ---
fig = plt.figure(figsize=(14, 10))
ax = fig.add_subplot(111, projection='3d')

surf = ax.plot_surface(X_P_others, Y_B, Z_Efficiency_no_rakeback, cmap='viridis', edgecolor='none', alpha=0.85)

# --- Adjust Z-axis limits to "zoom in" ---
valid_Z_values = Z_Efficiency_no_rakeback[Z_Efficiency_no_rakeback > 0] # Exclude 0 for limit calculation
if valid_Z_values.size > 0:
    z_min_eff = np.min(valid_Z_values)
    z_max_eff = np.max(valid_Z_values)
    padding = (z_max_eff - z_min_eff) * 0.05 # Add 5% padding
    
    # Ensure z_min_eff is not unreasonably high if all efficiencies are very low
    # And ensure plot_z_min is not negative if z_min_eff - padding becomes so.
    plot_z_min = max(0, z_min_eff - padding) 
    plot_z_max = z_max_eff + padding

    # Handle case where z_min and z_max are very close or equal
    if np.isclose(plot_z_min, plot_z_max):
        plot_z_min = max(0, plot_z_min - 0.0001) # Add a small range
        plot_z_max = plot_z_max + 0.0001
    if plot_z_min < plot_z_max : # Only set if valid range
        ax.set_zlim(plot_z_min, plot_z_max)
    else: # Fallback if something went wrong or all values are the same
        ax.set_zlim(0, max(0.001, z_max_eff * 1.1 if valid_Z_values.size > 0 else 0.001) ) # Default if all values are zero or very close
else:
    ax.set_zlim(0.001, 0.002) # 手动设置一个更集中的范围

fig.colorbar(surf, shrink=0.5, aspect=10, label='Efficiency (Star_Prize / P_total)')
ax.set_xlabel("Sum of Others' Bids (P_others)")
ax.set_ylabel('Your Bid (B)')
ax.set_zlabel('Cost-Effectiveness (Efficiency)')
ax.set_title(f'Efficiency (No Rakeback, P_total <= {MAX_TOTAL_POOL}) - Zoomed Z-axis')
ax.view_init(elev=30, azim=-130) # Experiment with view angle (e.g. elev=30, azim=-130 or elev=40, azim=-110)

plt.tight_layout()
plt.show()

print("\n--- How to Interpret This Efficiency Plot (No Rakeback, Zoomed Z-axis) ---")
print("This plot shows the 'Cost-Effectiveness' (Efficiency) of your single bid.")
print(f"- Z-axis range has been adjusted to better show variations in positive efficiency values.")
print("  (Values of 0 for invalid/out-of-bound bids might be clipped from the bottom if they make the range too large).")
print("- Higher Z-values are better. Look for where the surface peaks or forms plateaus.")
print("- The '断层' (jumps) where Star Prize changes should be more visible as steps in the surface.")
print("  These jumps occur when (Your Bid + P_others) crosses 5000, 7500, 16000, etc.")