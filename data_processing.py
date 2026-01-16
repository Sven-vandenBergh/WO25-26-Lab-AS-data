######################
#---Import-modules---#
######################
from matplotlib import pyplot as plt

from convert_csv import convert_csv as convert
from matplotlib.pyplot import subplots, show
import numpy as np
from scipy.signal import find_peaks

######################
#----Import--Data----#
######################

zero = convert(r"C:\Users\Gebruiker\Documents\Uni\W&O Labs\raw_data_txt\nothing2.txt",
                save_path=r"C:\Users\Gebruiker\Documents\Uni\W&O Labs\raw_data_csv\zero.csv", save_csv=False)       # Data purely from Hydrogen lamp, no container
empty = convert(r"C:\Users\Gebruiker\Documents\Uni\W&O Labs\raw_data_txt\emptycontainer2.txt",
                save_path=r"C:\Users\Gebruiker\Documents\Uni\W&O Labs\raw_data_csv\empty.csv", save_csv=False)      # Data with container inserted, no coating of anti-fog
coated = convert(r"C:\Users\Gebruiker\Documents\Uni\W&O Labs\raw_data_txt\containerwithgel2.txt",
                save_path=r"C:\Users\Gebruiker\Documents\Uni\W&O Labs\raw_data_csv\coated.csv", save_csv=False)     # Data from container coated in anti-fog gel
liquid = convert(r"C:\Users\Gebruiker\Documents\Uni\W&O Labs\raw_data_txt\onlywater2.txt",
                save_path=r"C:\Users\Gebruiker\Documents\Uni\W&O Labs\raw_data_csv\liquid.csv", save_csv=False)     # Data from container filled with water, no gel applied
vapour_little = convert(r"C:\Users\Gebruiker\Documents\Uni\W&O Labs\raw_data_txt\vapour_some_water2.txt",
                save_path=r"C:\Users\Gebruiker\Documents\Uni\W&O Labs\raw_data_csv\vapour_little.csv", save_csv=False)  # Data from container with anti-fog, small layer of water
vapour_lot = convert(r"C:\Users\Gebruiker\Documents\Uni\W&O Labs\raw_data_txt\vapour_more_water2.txt",
                save_path=r"C:\Users\Gebruiker\Documents\Uni\W&O Labs\raw_data_csv\vapour_lot.csv", save_csv=False) # Data from container with anti-fog, thick layer of water
vapour_dark = convert(r"C:\Users\Gebruiker\Documents\Uni\W&O Labs\raw_data_txt\vapour_different_more_water3.txt",
                save_path=r"C:\Users\Gebruiker\Documents\Uni\W&O Labs\raw_data_csv\vapour_dark.csv", save_csv=False)    # Thick layer of water with anti-fog, darker room

######################
#-----Mean--Data-----#
######################

for df in [zero, empty, coated, liquid, vapour_little, vapour_lot, vapour_dark]:
    df['Mean Curve'] = df.iloc[:, 1:].mean(axis=1)
    df['Std'] = df.iloc[:, 1:].std(axis=1)
    #print(df[0:1])

x = zero['Wavelength (nm)']

#########################
#---Hydrogen-Spectrum---#
#########################

fig, ax = subplots()
ax.plot(x, zero['Mean Curve'], color='darkslategrey')
ax.grid(alpha=0.5)
ax.set_xlabel('Wavelength (nm)')
show()

#peaks, _ = find_peaks(y, height=10000)
#print(x[peaks], y[peaks])

######################
#---Motivation-gel---#
######################

fig,axs = subplots(2,1, tight_layout=True)

axs[0].plot(x,zero['Mean Curve'], color='darkslategrey' ,alpha=0.35, label='Zero')
axs[0].plot(x, coated['Mean Curve'], color='darkslategrey', label='Coated')
axs[0].plot(x, empty['Mean Curve'], color='cadetblue', label='Empty')

axs[0].grid(alpha=0.5)
axs[0].legend()

axs[1].plot(x, coated['Mean Curve'] - empty['Mean Curve'], color='darkslategrey', label='Residual; Coated-Empty')
axs[1].grid(alpha=0.5)
axs[1].legend()
axs[1].set_xlabel('Wavelength (nm)')
show()

######################
#---Correction-gel---#
######################

C = zero['Mean Curve']/coated['Mean Curve']

def corr(null, data, C):
    """
    It does not make sense for wavelengths scattered and absorbed by the vapour to
    suddenly have higher intensity than our spectrum without; Hence we cap corrected
    values at the initial measurements, and recognise that in cases where correction
    exceeds these initial values, there simply is absorption simply has not much of
    an effect;

    Parameters]
    null : array-like - measurements without absorption or scattering
    data : array-like - measurements with absorption or scattering
    C : array-like - correction factor

    Output]
    corrected: array-like - corrected data
    """

    corrected = C*data
    corrected = np.clip(corrected, None, null)
    return corrected


liquid_corr = corr(zero['Mean Curve'], liquid['Mean Curve'], C)
vapour_little_corr = corr(zero['Mean Curve'], vapour_little['Mean Curve'], C)
vapour_lot_corr = corr(zero['Mean Curve'], vapour_lot['Mean Curve'], C)
vapour_dark_corr = corr(zero['Mean Curve'], vapour_dark['Mean Curve'], C)

fig, axs = subplots(1,2, tight_layout=True, figsize=(10,5))

axs[0].plot(x,zero['Mean Curve'], color='darkslategrey', label='Zero', alpha=0.35)
axs[0].plot(x,liquid['Mean Curve'], label='Liquid')
#axs[0].plot(x,vapour_little['Mean Curve'], label='Vapour (Small layer)')
#axs[0].plot(x,vapour_lot['Mean Curve'], label='Vapour (Thick layer)')
axs[0].plot(x,vapour_dark['Mean Curve'], label='Vapour (Dark)')
axs[0].legend()
axs[0].grid(alpha=0.5)
axs[0].set_xlabel('Wavelength (nm)')

axs[1].plot(x,zero['Mean Curve'], color='darkslategrey', label='Zero', alpha=0.35)
axs[1].plot(x,liquid_corr, label='Liquid')
#axs[1].plot(x,vapour_little_corr, label='Vapour (Small layer)')
#axs[1].plot(x,vapour_lot_corr, label='Vapour (Thick layer)')
axs[1].plot(x,vapour_dark_corr, label='Vapour (Dark)')
axs[1].legend()
axs[1].grid(alpha=0.5)
axs[1].set_xlabel('Wavelength (nm)')

#axs[2].plot(x, C, color='darkslategrey', label='Correction Factor')
#axs[2].grid(alpha=0.5)
#axs[2].set_xlabel('Wavelength (nm)')
#axs[2].legend()

show()

