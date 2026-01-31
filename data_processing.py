######################
#---Import-modules---#
######################
from matplotlib import pyplot as plt

from convert_csv import convert_csv as convert
from matplotlib.pyplot import subplots, show, savefig
import numpy as np
from scipy.signal import find_peaks, savgol_filter
from scipy.constants import Rydberg as Rh

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

    #df['Mean Smooth'] = savgol_filter(df['Mean Curve'], 9, 3 )

x = zero['Wavelength (nm)']

#########################
#---Hydrogen-Spectrum---#
#########################

def Rydberg(n_0, n_1):
    if n_1 > n_0:
        l_inv = Rh * (n_0**-2 - n_1**-2)
        l = l_inv ** -1
        return l

wavelengths = []

for i in range(1,5):
    for j in range(1,20):
        if j > i:
            wavelengths.append(Rydberg(i,j) * 1e9)
        #print(i,j)
print(wavelengths)
wavelengths = np.array(wavelengths)

mask = (wavelengths >= min(x)) & (wavelengths <= max(x))

fig, ax = subplots()

ax.plot(x, zero['Mean Curve'], color='darkslategrey', label='Mean E')
ax.fill_between(x, zero['Mean Curve'] - zero['Std'], zero['Mean Curve'] + zero['Std'], color='darkslategrey', alpha=0.4, label='Error Margin')
ax.vlines(wavelengths[mask], *ax.get_ylim(), color='black', alpha=0.2, label='Model', linestyle='dashed')
ax.grid(alpha=0.5)
ax.set_xlabel('Wavelength (nm)')
ax.set_ylabel('E (s.u.)')
ax.legend()
savefig(r"C:\Users\Gebruiker\Documents\Uni\W&O Labs\Plots\HES.png")
show()



peaks, _ = find_peaks(zero['Mean Curve'], height=5000, distance=1)
maxima = [(wavelength, value, std) for wavelength,value,std in zip(x[peaks], zero['Mean Curve'][peaks], zero['Std'][peaks])]
for i in maxima:
    print(f"{i[0]}, {i[1]:.3g}, {i[2]:.1g}")

######################
#---Motivation-gel---#
######################

fig,axs = subplots(2,1, tight_layout=True)

axs[0].plot(x,zero['Mean Curve'], color='darkslategrey' ,alpha=0.50, label='No Container')
axs[0].plot(x, coated['Mean Curve'], color='darkslategrey', label='Coated')
axs[0].plot(x, empty['Mean Curve'], color='darksalmon', label='Empty')

axs[0].grid(alpha=0.5)
axs[0].set_ylabel('E (s.u.)')
axs[0].set_title('(a)', y=-0.3)
axs[0].legend()

axs[1].plot(x, coated['Mean Curve'] - empty['Mean Curve'], color='darkslategrey', label='Residual; Coated-Empty')
axs[1].grid(alpha=0.5)
axs[1].set_xlabel('Wavelength (nm)')
axs[1].set_ylabel('E (s.u.)')
axs[1].set_title('(b)', y=-0.5)

savefig(r"C:\Users\Gebruiker\Documents\Uni\W&O Labs\Plots\anti-fog_motivation.png")
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
    print(C)
    corrected = C*data
    corrected = np.clip(corrected, None, null)
    return corrected

for df in [liquid, vapour_little, vapour_lot, vapour_dark]:
    df['Mean Corrected'] = corr(zero['Mean Curve'], df['Mean Curve'], C)
    df['Std Corrected'] = C*df['Std']

fig, axs = subplots(2,1, tight_layout=True, figsize=(5,9))

axs[0].plot(x,zero['Mean Curve'], color='darkslategrey', label='No Container', alpha=0.5)
axs[0].plot(x,liquid['Mean Curve'], color='darkslategrey', label='Liquid')
#axs[0].plot(x,vapour_little['Mean Curve'], label='Vapour (Small layer)')
#axs[0].plot(x,vapour_lot['Mean Curve'], label='Vapour (Thick layer)')
axs[0].plot(x,vapour_dark['Mean Curve'], linestyle=':', color='darksalmon', label='Vapour (Dark)')
axs[0].legend()
axs[0].grid(alpha=0.5)
axs[0].set_xlabel('Wavelength (nm)')
axs[0].set_ylabel('E (s.u.)')
axs[0].set_title('(a)', y=-0.2)

axs[1].plot(x,zero['Mean Curve'], color='darkslategrey', label='No Container', alpha=0.5)
axs[1].plot(x,liquid['Mean Corrected'], color='darkslategrey', label='Liquid')
#axs[1].plot(x,vapour_little['Mean Corrected'], label='Vapour (Small layer)')
#axs[1].plot(x,vapour_lot['Mean Corrected'], label='Vapour (Thick layer)')
axs[1].plot(x,vapour_dark['Mean Corrected'], linestyle=':', color='darksalmon', label='Vapour (Dark)')
axs[1].legend()
axs[1].grid(alpha=0.5)
axs[1].set_xlabel('Wavelength (nm)')
axs[1].set_title('(b)', y=-0.2)

#axs[2].plot(x, C, color='darkslategrey', label='Correction Factor')
#axs[2].grid(alpha=0.5)
#axs[2].set_xlabel('Wavelength (nm)')
#axs[2].legend()

savefig(r"C:\Users\Gebruiker\Documents\Uni\W&O Labs\Plots\correction.png")
show()

######################
#-----Absorbance-----#
######################

for df in [liquid, vapour_little, vapour_lot, vapour_dark]:
    df['Transmittance'] = df['Mean Corrected']/zero['Mean Curve']
    df['Std Transmittance'] = (df['Transmittance'] *
                               np.sqrt((df['Std Corrected']/df['Mean Corrected'])**2
                                + (df['Std']/df['Mean Curve'])**2))

    df['Absorbance'] = np.log10(df['Transmittance']**-1)
    df['Std Absorbance'] = (np.log(10))**-1 * df['Std Transmittance'] / df['Transmittance']

fig, ax = subplots(2,1, tight_layout=True)
ax[1].plot(x,vapour_dark['Absorbance'], color='darkslategrey', linestyle='-', label='Vapour')
ax[1].fill_between(x, vapour_dark['Absorbance'] + vapour_dark['Std Absorbance'], vapour_dark['Absorbance'] - vapour_dark['Std Absorbance'], color='darkslategrey', alpha=0.5, label='Error Margin')
#ax[1].plot(x,liquid['Absorbance'], color='darkslategrey', label='Liquid')
#ax[1].fill_between(x, liquid['Absorbance'] + liquid['Std Absorbance'], liquid['Absorbance'] - liquid['Std Absorbance'], color='darkslategrey', alpha=0.5)
ax[1].grid(alpha=0.5)
ax[1].set_ylim([-1.5,2.3])
ax[1].set_xlabel('Wavelength (nm)')
ax[1].set_ylabel('Absorbance')
ax[1].set_title('(b)', y=-0.5)
ax[1].legend(loc=1)

ax[0].plot(x,vapour_dark['Transmittance'], color='darkslategrey', linestyle='-', label='Vapour')
ax[0].fill_between(x, vapour_dark['Transmittance'] + vapour_dark['Std Transmittance'], vapour_dark['Transmittance'] - vapour_dark['Std Transmittance'], color='darkslategrey', alpha=0.5, label='Error Margin')
#ax[0].plot(x,liquid['Transmittance'], color='darkslategrey', label='Liquid')
#ax[0].fill_between(x, liquid['Transmittance'] + liquid['Std Transmittance'], liquid['Transmittance'] - liquid['Std Transmittance'], color='darkslategrey', alpha=0.5)
ax[0].grid(alpha=0.5)
ax[0].set_ylim([0,1])
ax[0].set_ylabel('Transmittance')
ax[0].set_title('(a)', y=-0.4)
savefig(r"C:\Users\Gebruiker\Documents\Uni\W&O Labs\Plots\absorb_trans_vp.png")
show()



fig, ax = subplots(2,1, tight_layout=True)
#ax[1].plot(x,vapour_dark['Absorbance'], color='#B2997F', linestyle='--', label='Vapour')
#ax[1].fill_between(x, vapour_dark['Absorbance'] + vapour_dark['Std Absorbance'], vapour_dark['Absorbance'] - vapour_dark['Std Absorbance'], color='#B2997F', alpha=0.5)
ax[1].plot(x,liquid['Absorbance'], color='darkslategrey', label='Liquid')
ax[1].fill_between(x, liquid['Absorbance'] + liquid['Std Absorbance'], liquid['Absorbance'] - liquid['Std Absorbance'], color='darkslategrey', alpha=0.5, label='Error Margin')
ax[1].grid(alpha=0.5)
ax[1].set_ylim([-1.5,2.3])
ax[1].set_xlabel('Wavelength (nm)')
ax[1].set_ylabel('Absorbance')
ax[1].set_title('(b)', y=-0.5)
ax[1].legend(loc=1)

#ax[0].plot(x,vapour_dark['Transmittance'], color='darksalmon', linestyle='--', label='Vapour')
#ax[0].fill_between(x, vapour_dark['Transmittance'] + vapour_dark['Std Transmittance'], vapour_dark['Transmittance'] - vapour_dark['Std Transmittance'], color='#B2997F', alpha=0.5)
ax[0].plot(x,liquid['Transmittance'], color='darkslategrey', label='Liquid')
ax[0].fill_between(x, liquid['Transmittance'] + liquid['Std Transmittance'], liquid['Transmittance'] - liquid['Std Transmittance'], color='darkslategrey', alpha=0.5, label='Error Margin')
ax[0].grid(alpha=0.5)
ax[0].set_ylim([0,1])
ax[0].set_ylabel('Transmittance')
ax[0].set_title('(a)', y=-0.4)

savefig(r"C:\Users\Gebruiker\Documents\Uni\W&O Labs\Plots\absorb_trans_lq.png")
show()




smooth_trans_vp = savgol_filter(vapour_dark['Transmittance'], 27, 3 )
smooth_trans_lq = savgol_filter(liquid['Transmittance'], 27, 3 )

smooth_abs_vp = savgol_filter(vapour_dark['Absorbance'], 27, 3 )
smooth_abs_lq = savgol_filter(liquid['Absorbance'], 27, 3 )

fig, ax = subplots(2,1, tight_layout=True)

ax[1].plot(x,smooth_abs_vp, color='darksalmon', label='Vapour')
ax[1].plot(x,smooth_abs_lq, color='darkslategrey', label='Liquid')
ax[1].grid(alpha=0.5)
ax[1].set_ylim([-1.5,2.3])
ax[1].set_xlabel('Wavelength (nm)')
ax[1].set_ylabel('Absorbance')
ax[1].set_title('(b)', y=-0.5)
ax[1].legend(loc=1)

ax[0].plot(x,smooth_trans_vp, color='darksalmon', label='Vapour')
ax[0].plot(x,smooth_trans_lq, color='darkslategrey', label='Liquid')
ax[0].grid(alpha=0.5)
ax[0].set_ylim([0,1])
ax[0].set_ylabel('Transmittance')
ax[0].set_title('(a)', y=-0.4)
savefig(r"C:\Users\Gebruiker\Documents\Uni\W&O Labs\Plots\absorb_trans.png")
show()

######################
#----Saving--data----#
######################



