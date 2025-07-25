import h5py
import numpy as np
import matplotlib.pyplot as plt

import matplotlib

matplotlib.use("tkagg")

with h5py.File("data/sri/20250722.014_lp_5min-fitcal.h5", "r") as h5:
    beamcodes = h5["BeamCodes"][:]

az = beamcodes[:, 1]
el = beamcodes[:, 2]

# set up plot
fig = plt.figure(figsize=(5, 5))
ax = fig.add_subplot(111, projection="polar")
ax.set_theta_direction(-1)
ax.set_theta_offset(np.pi / 2.0)
ax.set_rlabel_position(100.0)
elticks = np.arange(20.0, 90.0, 10.0)
ax.set_rticks(np.cos(elticks * np.pi / 180.0))
ax.set_yticklabels([str(int(el)) + "\N{DEGREE SIGN}" for el in elticks])

ax.scatter(az * np.pi / 180.0, np.cos(el * np.pi / 180.0), s=75)

plt.savefig("figs/beam_plot.png", dpi=300)
