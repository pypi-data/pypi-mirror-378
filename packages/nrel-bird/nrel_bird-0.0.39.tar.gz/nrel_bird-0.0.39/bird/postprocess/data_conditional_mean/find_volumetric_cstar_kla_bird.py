from bird import logger
from bird.postprocess.post_quantities import *
from bird.utilities.ofio import *

# logger.setLevel("DEBUG")

case_folder = "."
globalVars_dict = read_global_vars(case_folder)
print("D_H2:", globalVars_dict["D_H2"])
print("D_CO2:", globalVars_dict["D_CO2"])
print("D_CO:", globalVars_dict["D_CO"])
print("He_H2:", globalVars_dict["He_H2"])
print("He_CO2:", globalVars_dict["He_CO2"])
print("He_CO:", globalVars_dict["He_CO"])

time_float, time_str = get_case_times(case_folder)
N = len(time_float)
klaco2 = np.zeros(N)  # hour^-1
klaco = np.zeros(N)  # hour^-1
klah2 = np.zeros(N)  # hour^-1
co2sat = np.zeros(N)
cosat = np.zeros(N)
h2sat = np.zeros(N)

for itime, time_val in enumerate(time_str):
    kla_spec, cstar_spec, _ = compute_instantaneous_kla(
        case_folder, time_folder=time_val, species_names=["CO2", "CO", "H2"]
    )
    klaco2[itime] = kla_spec["CO2"]
    klaco[itime] = kla_spec["CO"]
    klah2[itime] = kla_spec["H2"]
    co2sat[itime] = cstar_spec["CO2"]
    cosat[itime] = cstar_spec["CO"]
    h2sat[itime] = cstar_spec["H2"]

print(klaco2)
print(klaco)
print(klah2)
print(co2sat)
print(cosat)
print(h2sat)
