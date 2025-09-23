import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

from sparks.models import SimulationData
from sparks.simulators import DeterministicSimulator
from sparks.data.initiators import AIBN
from sparks.data.monomers import methyl_methacrylate
from sparks.utils.formulas import C_to_K

from ..model import Model, RateCoefficients, ModelState


def k_MMA(temp_C: float) -> RateCoefficients:

    temp_K = C_to_K(temp_C)
    iprops = AIBN(temp_K)
    mprops = methyl_methacrylate(temp_K)

    return RateCoefficients(
        T_C=temp_C,
        iprops=iprops,
        mprops=mprops,
    )


def c0_MMA(temp_C: float, c_AIBN: float) -> ModelState:

    temp_K = C_to_K(temp_C)
    mprops = methyl_methacrylate(temp_K)

    V_basis = 1.0  # Volume in L for the basis state
    I = c_AIBN * V_basis
    M = mprops.dens_m / mprops.MW * V_basis  # Convert g/L to mol

    return ModelState(V=V_basis, I=I, M=M)


def get_validation_data():

    model = Model()

    c_AIBN = 0.0258  # mol/L

    T_C = 50
    ds = DeterministicSimulator(model, k=k_MMA(T_C))
    data_50 = ds.simulate(
        t_eval=np.linspace(0, 400, 100),
        init_state=c0_MMA(T_C, c_AIBN=c_AIBN),
    )

    T_C = 70
    ds = DeterministicSimulator(model, k=k_MMA(T_C))
    data_70 = ds.simulate(
        t_eval=np.linspace(0, 100, 100),
        init_state=c0_MMA(T_C, c_AIBN=c_AIBN),
    )

    T_C = 90
    ds = DeterministicSimulator(model, k=k_MMA(T_C))
    data_90 = ds.simulate(
        t_eval=np.linspace(0, 50, 100),
        init_state=c0_MMA(T_C, c_AIBN=c_AIBN),
    )

    return data_50, data_70, data_90