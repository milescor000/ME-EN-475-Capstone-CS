#---Libraries-------------------------------------------------------------------------------------#
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
#-------------------------------------------------------------------------------------------------#

#---Read CSV--------------------------------------------------------------------------------------#
df = pd.read_csv(r"C:\Users\corey\OneDrive\Documents\School\Fall 2026\ME EN 475 - Capstone (CS)\CS DAQ\DAQ_Experimental_Code\1k_Ohm_Resistor_Test.csv")
#-------------------------------------------------------------------------------------------------#

#---Unpack Data-----------------------------------------------------------------------------------#
t = df["elapsed_time_s"].to_numpy()
adc = df["raw_adc"].to_numpy()
V = df["voltage_v"].to_numpy()
#-------------------------------------------------------------------------------------------------#

#---Concentration Conversion----------------------------------------------------------------------#
G = (1023 - adc)/adc

G_0 = np.min(G)
G_infinity = np.max(G)

C_star = (G - G_0)/(G_infinity - G_0)
#-------------------------------------------------------------------------------------------------#

#---Identify 95% Concentration Point--------------------------------------------------------------#
indices_95 = np.where(C_star >= 0.95)[0]

if len(indices_95) > 0:
  idx_95 = indices_95[0]
  t_95 = t[idx_95]
  c_95 = C_star[idx_95]
else:
  t_95 = None
  print("Threshold not reached.")
#-------------------------------------------------------------------------------------------------#

#---Plot Data-------------------------------------------------------------------------------------#
plt.figure(1)
plt.plot(t,V)
plt.xlabel("Time (s)", fontsize=14)
plt.ylabel("Voltage (V)", fontsize=14)

plt.figure(2)
plt.plot(t,adc)
plt.xlabel("Time (s)", fontsize=14)
plt.ylabel("Raw ADC", fontsize=14)

plt.figure(3)
plt.plot(t,C_star)
plt.plot(t_95, c_95, color="red", label=f"t_95 = {t_95} s", marker='o')
plt.xlabel("Time (s)", fontsize=14)
plt.ylabel("Normalized Concentration", fontsize=14)
plt.legend()

plt.show()
#-------------------------------------------------------------------------------------------------#
