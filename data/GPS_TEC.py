import numpy as np
import matplotlib.pyplot as plt
import h5py
from scipy.stats import binned_statistic

fname = 'site_203_2025_isr.h5'
ylmv = [0, 30]
az_range = [-160, -130]  # Azimuth range to filter
ele_range = [0, 90]     # Elevation range to filter
ut_range = [4, 6]       # UT hours range to filter (4-6 UT)
ut0 = 202

# Open the HDF5 file
f = h5py.File(fname)
ct = f['data']

# Function to filter and bin data
def process_site_data(site_name, ct_data):
    site_mask = ct_data['site'] == site_name
    site_data = ct_data[site_mask]
    
    # Calculate UT hours
    utdoy = site_data['time']
    uthr = (utdoy - ut0) * 24
    
    # Apply filters
    az = site_data['az']
    elev = site_data['el']
    mask = ((az >= az_range[0]) & (az <= az_range[1]) & 
            (elev >= ele_range[0]) & (elev <= ele_range[1]) &
            (uthr >= ut_range[0]) & (uthr <= ut_range[1]))
    
    uthr_filtered = uthr[mask]
    vtec_filtered = site_data['vtec'][mask]
    
    # Bin and average data (1-minute bins)
    bin_edges = np.linspace(ut_range[0], ut_range[1], 121)  # 1-min bins for 2-hour window
    bin_centers = 0.5 * (bin_edges[:-1] + bin_edges[1:])
    vtec_mean, _, _ = binned_statistic(uthr_filtered, vtec_filtered, 
                                      statistic='mean', bins=bin_edges)
    vtec_std, _, _ = binned_statistic(uthr_filtered, vtec_filtered,
                                     statistic='std', bins=bin_edges)
    
   #remove with no data
    valid_mask = ~np.isnan(vtec_mean)
    return bin_centers[valid_mask], vtec_mean[valid_mask], vtec_std[valid_mask]

# Process data for each site
ut_m05c, vtec_m05c, std_m05c = process_site_data(b'm05c', ct)
ut_m16c, vtec_m16c, std_m16c = process_site_data(b'm16c', ct)
ut_m28c, vtec_m28c, std_m28c = process_site_data(b'm28c', ct)

# Create figure with subplots
fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(8, 10), sharex=True)

# Common plot settings
plot_kwargs = {
    'linewidth': 2,

    'capsize': 3,
    'capthick': 1
}

# Plot for m05c
ax1.errorbar(ut_m05c, vtec_m05c, yerr=std_m05c, color='C0', **plot_kwargs)
ax1.set_title('(66.56°N, 145.2°W)', fontsize=14)
ax1.set_ylabel('TECu', fontsize=14)
ax1.grid(True, linestyle=':', alpha=0.7)
ax1.set_ylim(ylmv)

# Plot for m16c
ax2.errorbar(ut_m16c, vtec_m16c, yerr=std_m16c, color='C1', **plot_kwargs)
ax2.set_title('(63.88°N, 145.8°W)', fontsize=11)
ax2.set_ylabel('TECu', fontsize=14)
ax2.grid(True, linestyle=':', alpha=0.7)
ax2.set_ylim(ylmv)

# Plot for m28c
ax3.errorbar(ut_m28c, vtec_m28c, yerr=std_m28c, color='C2', **plot_kwargs)
ax3.set_title('(70.13°N, 143.6°W)', fontsize=11)
ax3.set_ylabel('TECu', fontsize=14)
ax3.set_xlabel('UT Hours', fontsize=14)
ax3.grid(True, linestyle=':', alpha=0.7)
ax3.set_ylim(ylmv)

# Common x-axis 
for ax in [ax1, ax2, ax3]:
    ax.set_xlim(ut_range)
    ax.set_xticks(np.arange(ut_range[0], ut_range[1]+0.1, 0.5))
    ax.tick_params(axis='both', which='major', labelsize=14)

# Add main title
fig.suptitle(f'Azimuth: {az_range[0]}° to {az_range[1]}° | '
            f'Elevation: {ele_range[0]}° to {ele_range[1]}°',
            fontsize=14, y=0.98)

plt.tight_layout()
plt.show()
