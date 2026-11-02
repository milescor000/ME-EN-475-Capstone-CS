#---Libraries-------------------------------------------------------------------------------------#
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
#-------------------------------------------------------------------------------------------------#

#---Configuration---------------------------------------------------------------------------------#
# Adjust this to match when the salt was added during this specific recording
injection_time_s = 10.0

# Adjust this to the name of the test .csv file to by processed
csv_filename = "1k_Ohm_Resistor_Test.csv"
#-------------------------------------------------------------------------------------------------#

#---Read CSV--------------------------------------------------------------------------------------#
data_folder = r"C:\Users\corey\OneDrive\Documents\School\Fall 2026\ME EN 475 - Capstone (CS)\CS DAQ\DAQ_Experimental_Code"
file_path = os.path.join(data_folder, csv_filename)
df = pd.read_csv(file_path)
#-------------------------------------------------------------------------------------------------#

#---Unpack Data-----------------------------------------------------------------------------------#
t = df["elapsed_time_s"].to_numpy()
adc = df["raw_adc"].to_numpy()
V = df["voltage_v"].to_numpy()

# Shift time array so t=0 is the exact moment of injection
t_shifted = t - injection_time_s
#-------------------------------------------------------------------------------------------------#

#---Concentration Conversion----------------------------------------------------------------------#
G = (1023 - adc) / adc

# Use time-window averaging to prevent single noise spikes from ruining the bounds
pre_inject_mask = t < injection_time_s
plateau_mask = t > (t[-1] - 5.0) # Last 5 seconds of the run

G_0 = np.mean(G[pre_inject_mask]) if np.any(pre_inject_mask) else np.min(G)
G_infinity = np.mean(G[plateau_mask])

C_star = (G - G_0) / (G_infinity - G_0)

# Apply a 0.5-second rolling average (assuming 200 Hz DAQ = 100 samples) to reject sloshing
C_star_filt = pd.Series(C_star).rolling(window=100, center=True, min_periods=1).mean().to_numpy()
#-------------------------------------------------------------------------------------------------#

#---Identify 95% Concentration Point--------------------------------------------------------------#
# Only look for 95% crossings AFTER the tracer has been injected
post_inject = t >= injection_time_s
indices_95 = np.where((C_star_filt >= 0.95) & post_inject)[0]

if len(indices_95) > 0:
    idx_95 = indices_95[0]
    
    # Absolute timestamp in the CSV
    t_crossing_raw = t[idx_95]
    
    # Actual mixing duration (Performance Metric)
    t_95_duration = t_crossing_raw - injection_time_s
    c_95 = C_star_filt[idx_95]
    
    print(f"True Mixing Duration (t_95): {t_95_duration:.2f} seconds")
else:
    t_95_duration = None
    print("Threshold not reached.")
#-------------------------------------------------------------------------------------------------#

#---Plot Data-------------------------------------------------------------------------------------#
# Plot against t_shifted so the graph makes physical sense (injection at x=0)
plt.figure(3, figsize=(8, 5))
plt.plot(t_shifted, C_star, color="lightgray", label="Raw $C^*$")
plt.plot(t_shifted, C_star_filt, color="#0055A5", lw=2, label="Filtered Bulk $C^*$")
plt.axhline(0.95, color="black", linestyle="--", alpha=0.7, label="95% Threshold")

if t_95_duration is not None:
    plt.plot(t_95_duration, c_95, marker="o", markersize=8, color="red", label=f"$t_{{95}} = {t_95_duration:.2f}$ s")
    plt.axvline(t_95_duration, color="red", linestyle=":", alpha=0.7)

plt.xlabel("Time Since Injection (s)", fontsize=13)
plt.ylabel("Normalized Concentration $C^*$", fontsize=13)
plt.title("Mixing Performance Curve", fontsize=14, fontweight="bold")
plt.xlim(-5, t_shifted[-1]) # Show 5 seconds before injection for baseline context
plt.ylim(-0.05, 1.15)
plt.legend(loc="lower right")
plt.tight_layout()

plt.show()
#-------------------------------------------------------------------------------------------------#
