######################
#---Import-modules---#
######################

import pandas as pd
import pathlib
import os

######################
#----Def-Function----#
######################

def convert_csv(filepath, sep="\t", skip_rows=0, units_row=True, save_csv=False, save_path=False, confirm_save=True):
    """
    Convert weirdly formatted txt file to csv.
    Made for data files from 3B Scientific Digital Spectrometer LD.
    Last edited by Sven v/d Bergh @ 22:30 13/01/2026
    Latest version for Python 3.12.

    Parameters]
    filepath : str - full path to csv file
                        Must be Raw!!
    sep : str - delimiter
    skip_rows : int - number of rows to skip
    units_row : bool - whether file has unit row
    save_csv : bool - whether to save csv file
    save_path : str - path and filename to save csv file
    confirm_save : bool - whether to manually confirm save

    Output]
    csv : pandas.DataFrame - converted csv file
    """

    # Get filepath
    tilde_path = os.path.expanduser(fr"{filepath}")
    path = pathlib.Path(tilde_path)

    # Write text file to pandas.DataFrame
    df = pd.read_csv(path, sep=sep, skiprows=skip_rows)
    df.columns = df.columns.str.replace('?', 'Wavelength', regex=False)

    if units_row:
        units = df.iloc[0]          # Define first row as units

        df.columns = [f"{col} ({unit})" if unit != col else col
                        for col, unit in zip(df.columns, units)]         # Integrate units in header

        df = df.iloc[1:].reset_index(drop=True)         # Remove units row

    df[df.columns] = df[df.columns].apply(pd.to_numeric, errors='coerce')        # Convert all values to floats
    df = df[df['Wavelength (nm)'] != 0].reset_index(drop=True)          # Rows for wavelength=0 are excluded

    # Save csv file
    if save_csv:
        if not save_path:       # Give name if not given by user
            save_path = "converted_csv.csv"
        if confirm_save:        # Ask for confirmation before saving
            confirm = input("Confirm saving csv file (True/False): ")
            confirm = eval(confirm)
            if confirm:         # Save file upon confirm
                df.to_csv(save_path, index=False)
                print(f"saved to {save_path}.")
            else:               # Save denied
                print("csv was not saved.")
                return df
        else:
            df.to_csv(save_path, index=False)       # Automatic save
            return df

    return df

