from pathlib import Path

import pandas as pd
import numpy as np

SRF_DIR = Path(r"C:\Users\puehrifi\Documents\eo_data\SRF_files")

def convert_oli_srf_to_wide(xls_path, sensor_prefix="L8"):
    """
    Converts Landsat OLI SRF Excel file (one sheet per band) to wide Sentinel-style format.
    Skips sheets that do not contain valid SRF columns.
    """
    xls = pd.ExcelFile(xls_path)
    sheet_names = xls.sheet_names
    srf_dict = {}
    valid_band_count = 1

    print(f"📘 Found {len(sheet_names)} sheets. Processing valid ones...")

    for sheet in sheet_names:
        if sheet.strip().lower() in ["pan", "panchromatic"]:
            print(f"Skipping PAN sheet: '{sheet}'")
            continue

        try:
            df = pd.read_excel(xls, sheet_name=sheet)
            print(f"\n🔍 Checking sheet: '{sheet}'")

            # Try to find wavelength and RSR columns
            wl_candidates = [col for col in df.columns if 'wave' in col.lower()]
            rsr_candidates = [col for col in df.columns if 'rsr' in col.lower()]

            if not wl_candidates or not rsr_candidates:
                print(f"⚠️ Skipping sheet '{sheet}' (missing 'wave' or 'rsr' column)")
                continue

            wl_col = wl_candidates[0]
            rsr_col = rsr_candidates[0]

            df = df[[wl_col, rsr_col]].dropna()
            df.columns = ['SR_WL', f'{sensor_prefix}_B{valid_band_count}']
            df = df.astype({'SR_WL': float, f'{sensor_prefix}_B{valid_band_count}': float})

            srf_dict[f'{sensor_prefix}_B{valid_band_count}'] = df
            valid_band_count += 1

        except Exception as e:
            print(f"❌ Error reading sheet '{sheet}': {e}")
            continue

    if not srf_dict:
        raise ValueError("No valid SRF data found in any sheet.")

    # Combine into one DataFrame
    all_wls = sorted(set(np.concatenate([df['SR_WL'].values for df in srf_dict.values()])))
    master_df = pd.DataFrame({'SR_WL': all_wls})

    for band_name, band_df in srf_dict.items():
        master_df = master_df.merge(band_df, on='SR_WL', how='left')

    master_df = master_df.fillna(0)
    return master_df


# --- Example usage ---
# Adjust sensor_prefix to "L9" for Landsat 9
input_xlsx = SRF_DIR / "Ball_BA_RSR.v1.2.xls"
output_csv = SRF_DIR / "OLI_SRF.csv"

wide_srf_df = convert_oli_srf_to_wide(input_xlsx, sensor_prefix="L8")
wide_srf_df.to_csv(output_csv, index=False)
