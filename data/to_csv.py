import pandas as pd
import numpy as np
from uncertainties import unumpy

# Define time filter (4-6 UT on 2025-07-22)
start_time = datetime.datetime(2025,7,22,4,0,0)
end_time = datetime.datetime(2025,7,22,6,0,0)

# List to store all rows
data_rows = []

for bdat in PFISR_data:
    # Apply your filtering
    NeFitted = FilterProfile(bdat['ne'])
    dNeFitted = FilterProfile(bdat['dne'])
    AltValues = bdat['altitude']
    
    # Calculate VTEC with errors
    VTEC = TECIntegralWithErrors(NeFitted, dNeFitted, AltValues)
    tec_vals = unumpy.nominal_values(VTEC)
    dtec_vals = unumpy.std_devs(VTEC)
    
    # Process each time point
    for t_idx, time in enumerate(bdat['time']):
        if not (start_time <= time <= end_time):
            continue
            
        # Get average Ne and dNe across altitudes for this time point
        avg_Ne = np.mean(NeFitted[:, t_idx])
        avg_dNe = np.mean(dNeFitted[:, t_idx])
        
        # Create row for this time point
        row = {
            'time': time,
            'beam_id': bdat['bid'],
            'elevation': bdat['elm'],
            'azimuth': bdat['azm'],
            'TEC': tec_vals[t_idx],
            'dTEC': dtec_vals[t_idx],
            'Ne': avg_Ne,
            'dNe': avg_dNe
        }
        data_rows.append(row)

# Create DataFrame
df = pd.DataFrame(data_rows)

# Sort by time then beam ID
df.sort_values(['time', 'beam_id'], inplace=True)

# Save to CSV
output_filename = 'PFISR_simple_format.csv'
df.to_csv(output_filename, index=False)

print(f"Data saved to {output_filename}")
print("Sample data:")
print(df.head())
