"""
extract data, using Paraview-python modules, to numpy arrays

This script is for probing the superificial velocity of the gas (air)

"""

import os
from sys import argv

import numpy as np
import vtk.numpy_interface.dataset_adapter as dsa
from paraview import simple as pv

D_H2 = 1.2097e-8
D_CO2 = 5.3765e-9
D_CO = 3.9518e-9
He_H2 = 0.02
He_CO = 0.018
He_CO2 = 0.64
Mw_CO2 = 0.044
Mw_CO = 0.028
Mw_H2 = 0.002

nskip = 1
if len(argv) > 1:
    nskip = int(argv[1])
ofreader = pv.OpenFOAMReader(FileName=".")  # just need to provide folder
ofreader.CaseType = "Reconstructed Case"
ofreader.MeshRegions = ["internalMesh"]
ofreader.SkipZeroTime = 0  # dont know why this is not working
t = np.array(ofreader.TimestepValues)[::nskip]
N = t.size
print(t)

# set time to something other than zero to avoid errors about unset fields
# pv.UpdatePipeline(time = t[-1])

liqthreshold = pv.Threshold(
    Input=ofreader,
    Scalars=["CELLS", "alpha.gas"],
    LowerThreshold=0,
    UpperThreshold=0.6,
    ThresholdMethod="Between",
)

calc1 = pv.Calculator(
    Input=liqthreshold,
    AttributeType="Cell Data",
    ResultArrayName="Re",
    Function='"thermo:rho.liquid"*mag("U.gas"-"U.liquid")*"d.gas"/"thermo:mu.liquid"',
)

calc2 = pv.Calculator(
    Input=calc1,
    AttributeType="Cell Data",
    ResultArrayName="klaco2",
    Function='1.13*("Re"^0.5)*(("thermo:mu.liquid"/"thermo:rho.liquid"/%e)^0.5)*(%e/"d.gas")\
                         *(6.0/"d.gas")*"alpha.gas"*3600'
    % (D_CO2, D_CO2),
)

calc3 = pv.Calculator(
    Input=calc2,
    AttributeType="Cell Data",
    ResultArrayName="klah2",
    Function='1.13*("Re"^0.5)*(("thermo:mu.liquid"/"thermo:rho.liquid"/%e)^0.5)*(%e/"d.gas")\
                         *(6.0/"d.gas")*"alpha.gas"*3600'
    % (D_H2, D_H2),
)

calc4 = pv.Calculator(
    Input=calc3,
    AttributeType="Cell Data",
    ResultArrayName="klaco",
    Function='1.13*("Re"^0.5)*(("thermo:mu.liquid"/"thermo:rho.liquid"/%e)^0.5)*(%e/"d.gas")\
                         *(6.0/"d.gas")*"alpha.gas"*3600'
    % (D_CO, D_CO),
)

calc5 = pv.Calculator(
    Input=calc4,
    AttributeType="Cell Data",
    ResultArrayName="co2_star",
    Function='"thermo:rho.gas"*"CO2.gas"/%e*%e' % (Mw_CO2, He_CO2),
)

calc6 = pv.Calculator(
    Input=calc5,
    AttributeType="Cell Data",
    ResultArrayName="co_star",
    Function='"thermo:rho.gas"*"CO.gas"/%e*%e' % (Mw_CO, He_CO),
)

calc7 = pv.Calculator(
    Input=calc6,
    AttributeType="Cell Data",
    ResultArrayName="h2_star",
    Function='"thermo:rho.gas"*"H2.gas"/%e*%e' % (Mw_H2, He_H2),
)

# integrate all variables
int1 = pv.IntegrateVariables(Input=calc7)
int1.DivideCellDataByVolume = 1

klaco2 = np.zeros(N)  # hour^-1
klaco = np.zeros(N)  # hour^-1
klah2 = np.zeros(N)  # hour^-1
co2sat = np.zeros(N)
cosat = np.zeros(N)
h2sat = np.zeros(N)

for i in range(N):
    print("processing time = %g" % t[i])
    pv.UpdatePipeline(time=t[i], proxy=int1)
    idat = dsa.WrapDataObject(pv.servermanager.Fetch(int1))
    klaco2[i] = idat.CellData["klaco2"].item()
    klaco[i] = idat.CellData["klaco"].item()
    klah2[i] = idat.CellData["klah2"].item()
    co2sat[i] = idat.CellData["co2_star"].item()
    cosat[i] = idat.CellData["co_star"].item()
    h2sat[i] = idat.CellData["h2_star"].item()

print(klaco2)
print(klaco)
print(klah2)
print(co2sat)
print(cosat)
print(h2sat)

np.savetxt(
    "volumetric_cstar_kla.dat",
    np.transpose(np.vstack((t, klaco2, klaco, klah2, co2sat, cosat, h2sat))),
    delimiter="  ",
)
