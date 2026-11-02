from collections import deque
from datetime import datetime
import matplotlib.animation as animation
import matplotlib.pyplot as plt
import serial

# ==========================================
# CONFIGURATION
# ==========================================
SERIAL_PORT = "COM5"  # Windows: 'COM3', 'COM4' | Mac/Linux: '/dev/ttyUSB0'
BAUD_RATE = 230400
DISPLAY_WINDOW_SEC = 15.0  # Shows the most recent 15 seconds on screen
SAMPLE_RATE_HZ = 200.0
BUFFER_SIZE = int(DISPLAY_WINDOW_SEC * SAMPLE_RATE_HZ)

# Generate timestamped filename for every test run
filename = f"mixing_run_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
csv_file = open(filename, "w", buffering=1)  # Line-buffered writing
csv_file.write("elapsed_time_s,raw_adc,voltage_v\n")

# Connect to Arduino
ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=0.1)
ser.reset_input_buffer()

# Discard bootloader header line
try:
  ser.readline()
except Exception:
  pass

# Rolling display deques
time_deque = deque(maxlen=BUFFER_SIZE)
voltage_deque = deque(maxlen=BUFFER_SIZE)

# Plot Configuration
fig, ax = plt.subplots(figsize=(10, 5))
(line,) = ax.plot([], [], color="#0055A5", lw=1.5, label="Sensor Voltage V(t)")
ax.set_ylim(-0.2, 5.2)
ax.set_xlabel("Time Elapsed [s]", fontsize=11)
ax.set_ylabel("Voltage [V]", fontsize=11)
ax.set_title("Live Crucible Conductivity Response", fontsize=12, fontweight="bold")
ax.grid(True, linestyle="--", alpha=0.5)
ax.legend(loc="upper right")

t_zero_us = None


def update(frame):
  global t_zero_us

  # Process all pending bytes in the serial buffer
  while ser.in_waiting > 0:
    try:
      raw_bytes = ser.readline().decode("utf-8", errors="ignore").strip()
      if not raw_bytes or "," not in raw_bytes:
        continue

      parts = raw_bytes.split(",")
      t_us = int(parts[0])
      adc = int(parts[1])

      if t_zero_us is None:
        t_zero_us = t_us

      # Compute physical metrics
      t_sec = (t_us - t_zero_us) / 1e6
      voltage = adc * (5.0 / 1023.0)

      # 1. Immediately log to CSV on disk
      csv_file.write(f"{t_sec:.6f},{adc},{voltage:.4f}\n")

      # 2. Append to rolling display memory
      time_deque.append(t_sec)
      voltage_deque.append(voltage)

    except (ValueError, IndexError):
      continue

  # Update the graph line
  if time_deque:
    line.set_data(time_deque, voltage_deque)
    t_now = time_deque[-1]
    ax.set_xlim(
        max(0.0, t_now - DISPLAY_WINDOW_SEC), max(DISPLAY_WINDOW_SEC, t_now)
    )

  return (line,)


ani = animation.FuncAnimation(fig, update, interval=33, blit=False)

print(f"Logging data to: {filename}")
print("Close the graph window to stop the run.")

try:
  plt.show()
finally:
  ser.close()
  csv_file.close()
  print(f"Run completed. File safely written: {filename}")