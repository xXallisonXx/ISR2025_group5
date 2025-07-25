import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator, FuncFormatter
from netCDF4 import Dataset

# === Load the dataset ===
data_path = "/scratch/prakasp/2023/aur_emp_e_empx1.25x0.125_20250722_new.nc"
data = Dataset(data_path)

# === Extract variables ===
lat = data["lat"][:].filled()  # 1D (lat,)
lon = data["lon"][:].filled()  # 1D (lon,)
time = data["time"][:].filled() / 3600  # Convert from seconds to hours
NE = data["NE"][:].filled() * 1e6  # Convert to m⁻³ → shape: (time, height, lat, lon)
TEC = data["TEC"][:].filled()  # TEC already in TECU → shape: (time, lat, lon)
ZG = data["ZG"][:].filled()  # Height in meters → shape: (time, height, lat, lon)

# === Select location: lat = 66.5°, lon = -147° ===
lat_idx = np.abs(lat - 66.5).argmin()
lon_idx = np.abs(lon + 147).argmin()

# === Filter time: 4 to 6 UT ===
time_filter = (time >= 4) & (time <= 6)
time_hours_filtered = time[time_filter]

# === Extract data at selected location and time ===
NE_profile = NE[time_filter, :, lat_idx, lon_idx]  # (time, height)
z_profile = ZG[0, :, lat_idx, lon_idx] / 100000  # in km, shape: (height,)
TEC_profile = TEC[time_filter, lat_idx, lon_idx]  # (time,)

# === Convert NE to log10 ===
log_NE = np.log10(NE_profile)

# === Plotting ===
fig, axs = plt.subplots(2, 1, figsize=(10, 10))

# --- 1. Electron density (log₁₀) vs time and height ---
time_mesh, height_mesh = np.meshgrid(time_hours_filtered, z_profile)
cf1 = axs[0].contourf(
    time_mesh, height_mesh, log_NE.T, levels=50, cmap="jet", vmin=10, vmax=12
)
cbar1 = fig.colorbar(cf1, ax=axs[0], orientation="vertical", pad=0.01)
cbar1.set_label("log$_{10}$(NE) (m$^{-3}$)", fontsize=14)
axs[0].set_title("Electron Density", fontsize=16)
axs[0].set_ylabel("Altitude (km)", fontsize=12)
axs[0].set_xlim(4, 6)
axs[0].set_ylim(150, 500)
axs[0].xaxis.set_major_locator(MultipleLocator(0.25))
axs[0].xaxis.set_major_formatter(
    FuncFormatter(lambda x, _: f"{int(x)}:{int((x % 1) * 60):02d}")
)
axs[0].tick_params(labelsize=12)

# --- 2. TEC vs time ---
axs[1].plot(time_hours_filtered, TEC_profile, color="red", linewidth=2)
axs[1].set_title("TEC at 66.5°N, -147°E", fontsize=14)
axs[1].set_ylabel("TEC (TECU)", fontsize=14)
axs[1].set_xlabel("UT (hours)", fontsize=14)
axs[1].set_xlim(4, 6)
axs[1].grid(True)
axs[1].set_ylim(0, 14)
axs[1].xaxis.set_major_locator(MultipleLocator(0.25))
axs[1].xaxis.set_major_formatter(
    FuncFormatter(lambda x, _: f"{int(x)}:{int((x % 1) * 60):02d}")
)
axs[1].tick_params(labelsize=14)

plt.tight_layout()
plt.show()
