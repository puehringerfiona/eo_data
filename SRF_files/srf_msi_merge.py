from pathlib import Path

import pandas as pd
import numpy as np

SRF_DIR = Path(r"C:\Users\puehrifi\Documents\eo_data\SRF_files")

# Define wavelength range and band center wavelengths
wvl_range = np.arange(400, 950)
band_centers = [443, 492, 559, 665, 704, 740, 783, 842, 865]


# Load S2A and S2B spectral response functions
file_path = SRF_DIR / "S2-SRF_COPE-GSEG-EOPG-TN-15-0007_3.2.xlsx"

srf_s2a = pd.read_excel(file_path, sheet_name='Spectral Responses (S2A)', index_col=0)
srf_s2b = pd.read_excel(file_path, sheet_name='Spectral Responses (S2B)', index_col=0)

# Trim to desired wavelength range and select first 7 bands
srf_s2a = srf_s2a.loc[wvl_range[0]:wvl_range[-1]].iloc[:, 0:9]
srf_s2b = srf_s2b.loc[wvl_range[0]:wvl_range[-1]].iloc[:, 0:9]

# Rename columns to match desired band center names
srf_s2a.columns = band_centers
srf_s2b.columns = band_centers

# Compute average SRF
srf_avg = 0.5 * (srf_s2a + srf_s2b)

# Ensure the output contains all wavelengths in range, fill missing with 0
srf_output = pd.DataFrame(index=wvl_range, columns=band_centers, dtype=float)
srf_output.update(srf_avg)
srf_output.fillna(0, inplace=True)

# Reset index to include 'SR_WL' as first column
srf_output.reset_index(inplace=True)
srf_output.rename(columns={'index': 'SR_WL'}, inplace=True)

# Rename columns to match desired output format
srf_output.columns = ['SR_WL'] + [f'S2A_SR_AV_B{i+1}' for i in range(9)]

# Save to CSV
srf_output.to_csv(SRF_DIR / "S2A_S2B_Merged_SRF.csv", index=False)
