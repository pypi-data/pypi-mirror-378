import numpy as np

T0 = 303.15
muMixLiq = 2.414e-5 * np.power(10, 247.8 / (T0 - 140.0))
CpMixLiq = 4181
kThermLiq = 0.62
rho0MixLiq = 1000
sigmaLiq = 0.07

Mw_CO2 = 0.044
Mw_CO = 0.028
Mw_H2 = 0.002

# Wilke-Chang params for diffusion coefficient of a given solute in water (solvent)
WC_psi = 2.6
WC_M = 18
# kg/kmol
WC_V_O2 = 25.6e-3
# m3/kmol molar volume at normal boiling temperature (Treybal 1968)
WC_V_H2 = 14.3e-3
WC_V_CO2 = 34e-3
WC_V_CO = 30.7e-3
WC_V_CH4 = 35e-3
# ****** diffusion coeff ***********
D_H2 = (
    1.173e-16
    * np.power(WC_psi * WC_M, 0.5)
    * T0
    / muMixLiq
    / np.power(WC_V_H2, 0.6)
)
D_CO2 = (
    1.173e-16
    * np.power(WC_psi * WC_M, 0.5)
    * T0
    / muMixLiq
    / np.power(WC_V_CO2, 0.6)
)
D_CO = (
    1.173e-16
    * np.power(WC_psi * WC_M, 0.5)
    * T0
    / muMixLiq
    / np.power(WC_V_CO, 0.6)
)
D_CH4 = (
    1.173e-16
    * np.power(WC_psi * WC_M, 0.5)
    * T0
    / muMixLiq
    / np.power(WC_V_CH4, 0.6)
)
# D_H2=3.4e-9, D_CO2=2e-9, D_CO=2.16e-9 at 25C
# Looks like the H2 diffusion is less than litr reported values ~ 4.5e-9
# *******inlet gas frac*************
f_H2 = 0.07
f_CO2 = 0.70
f_CO = 0.23
# *********************************
LeLiqH2 = kThermLiq / rho0MixLiq / D_H2 / CpMixLiq
LeLiqCO = kThermLiq / rho0MixLiq / D_CO / CpMixLiq
LeLiqCO2 = kThermLiq / rho0MixLiq / D_CO2 / CpMixLiq
LeLiqCH4 = kThermLiq / rho0MixLiq / D_CH4 / CpMixLiq

LeLiqMix = f_H2 * LeLiqH2 + f_CO2 * LeLiqCO2 + f_CO * LeLiqCO
PrMixLiq = CpMixLiq * muMixLiq / kThermLiq
# Pr number is ~ 7 for water and ~ 0.7 for air
# *********************************
kH2 = D_H2 * rho0MixLiq * CpMixLiq * LeLiqMix
PrH2 = muMixLiq * CpMixLiq / kH2

kCO = D_CO * rho0MixLiq * CpMixLiq * LeLiqMix
PrCO = muMixLiq * CpMixLiq / kCO

kCO2 = D_CO2 * rho0MixLiq * CpMixLiq * LeLiqMix
PrCO2 = muMixLiq * CpMixLiq / kCO2

kCH4 = D_CH4 * rho0MixLiq * CpMixLiq * LeLiqMix
PrCH4 = muMixLiq * CpMixLiq / kCH4

H_O2_298 = 0.032
DH_O2 = 1700
H_CO2_298 = 0.83
DH_CO2 = 2400
H_CO_298 = 0.023
DH_CO = 1300
H_H2_298 = 0.019
DH_H2 = 500
H_CH4_298 = 0.032
DH_CH4 = 1900

He_H2 = H_H2_298 * np.exp(DH_H2 * (1.0 / T0 - 1.0 / 298.15))
He_CO = H_CO_298 * np.exp(DH_CO * (1.0 / T0 - 1.0 / 298.15))
He_CO2 = H_CO2_298 * np.exp(DH_CO2 * (1.0 / T0 - 1.0 / 298.15))
He_CH4 = H_CH4_298 * np.exp(DH_CH4 * (1.0 / T0 - 1.0 / 298.15))

print("D_H2:", D_H2)
print("D_CO2:", D_CO2)
print("D_CO:", D_CO)
print("He_H2:", He_H2)
print("He_CO2:", He_CO2)
print("He_CO:", He_CO)
