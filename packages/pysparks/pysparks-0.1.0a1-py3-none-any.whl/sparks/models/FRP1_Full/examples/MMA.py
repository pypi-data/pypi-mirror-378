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


def plot_conv_validation(
    data_50: SimulationData[ModelState],
    data_70: SimulationData[ModelState],
    data_90: SimulationData[ModelState],
):
    fig, ax = plt.subplots(figsize=(4, 3.5), dpi=150)
    ax.tick_params(axis="both", direction="in", top=True, right=True)

    import pandas as pd

    true_data_50C = pd.read_csv(
        "/home/devon/Documents/Github/React/Manuscript/data/MMA/MMA_50C_Conv_Model.csv"
    )
    true_data_70C = pd.read_csv(
        "/home/devon/Documents/Github/React/Manuscript/data/MMA/MMA_70C_Conv_Model.csv"
    )
    true_data_90C = pd.read_csv(
        "/home/devon/Documents/Github/React/Manuscript/data/MMA/MMA_90C_Conv_Model.csv"
    )

    plt.plot(
        data_50.trajectory.t,
        data_50.trajectory.x(data_50.init_state),
        label="50 C",
        color="tab:blue",
    )
    plt.plot(
        data_70.trajectory.t,
        data_70.trajectory.x(data_70.init_state),
        label="70 C",
        color="tab:green",
    )
    plt.plot(
        data_90.trajectory.t,
        data_90.trajectory.x(data_90.init_state),
        label="90 C",
        color="tab:orange",
    )

    plt.plot(
        true_data_50C["Time (min)"],
        true_data_50C["Conversion (%)"],
        "o",
        color="tab:blue",
        alpha=0.25,
    )

    plt.plot(
        true_data_70C["Time (min)"],
        true_data_70C["Conversion (%)"],
        "o",
        color="tab:green",
        alpha=0.25,
    )

    plt.plot(
        true_data_90C["Time (min)"],
        true_data_90C["Conversion (%)"],
        "o",
        color="tab:orange",
        alpha=0.25,
    )

    plt.xticks(
        [0, 50, 100, 150, 200, 250, 300, 350, 400],
    )
    plt.xlim(0, 400)
    plt.ylim(0, 1)
    plt.xlabel("Time (min)")
    plt.ylabel("Monomer conversion")
    plt.legend()
    plt.show()


def plot_mw_validation(
    data_50: SimulationData[ModelState],
    data_70: SimulationData[ModelState],
    data_90: SimulationData[ModelState],
):

    MW = methyl_methacrylate(1).MW

    t_50 = data_50.trajectory.t
    t_70 = data_70.trajectory.t
    t_90 = data_90.trajectory.t
    x_50 = data_50.trajectory.x(data_50.init_state)
    x_70 = data_70.trajectory.x(data_70.init_state)
    x_90 = data_90.trajectory.x(data_90.init_state)
    Mn_50 = MW * data_50.trajectory.mu_1 / data_50.trajectory.mu_0
    Mw_50 = MW * data_50.trajectory.mu_2 / data_50.trajectory.mu_1
    Mn_70 = MW * data_70.trajectory.mu_1 / data_70.trajectory.mu_0
    Mw_70 = MW * data_70.trajectory.mu_2 / data_70.trajectory.mu_1
    Mn_90 = MW * data_90.trajectory.mu_1 / data_90.trajectory.mu_0
    Mw_90 = MW * data_90.trajectory.mu_2 / data_90.trajectory.mu_1

    fig, axs = plt.subplots(1, 3, figsize=(11, 3.5), dpi=150)
    axs[0].plot(
        x_50,
        Mn_50 / 1e5,
        label="50 C",
        color="tab:blue",
    )
    axs[0].plot(
        x_50,
        Mw_50 / 1e5,
        label="50 C",
        color="tab:blue",
        linestyle="--",
    )
    axs[1].plot(
        x_70,
        Mn_70 / 1e5,
        label="70 C",
        color="tab:green",
    )
    axs[1].plot(
        x_70,
        Mw_70 / 1e5,
        label="Mw 70 C",
        color="tab:green",
        linestyle="--",
    )
    axs[2].plot(
        x_90,
        Mn_90 / 1e5,
        label="90 C",
        color="tab:orange",
    )
    axs[2].plot(
        x_90,
        Mw_90 / 1e5,
        label="Mw 90 C",
        color="tab:orange",
        linestyle="--",
    )

    true_Mn_70C = pd.read_csv(
        "/home/devon/Documents/Github/React/Manuscript/data/MMA/MMA_70C_Mn_Model.csv"
    )
    true_Mw_70C = pd.read_csv(
        "/home/devon/Documents/Github/React/Manuscript/data/MMA/MMA_70C_Mw_Model.csv"
    )
    true_Mn_90C = pd.read_csv(
        "/home/devon/Documents/Github/React/Manuscript/data/MMA/MMA_90C_Mn_Model.csv"
    )
    true_Mw_90C = pd.read_csv(
        "/home/devon/Documents/Github/React/Manuscript/data/MMA/MMA_90C_Mw_Model.csv"
    )

    axs[1].plot(
        true_Mn_70C["Conversion (%)"],
        true_Mn_70C["Mn (Da)"] / 1e5,
        "o",
        color="tab:green",
        alpha=0.25,
    )
    axs[1].plot(
        true_Mw_70C["Conversion (%)"],
        true_Mw_70C["Mw (Da)"] / 1e5,
        "o",
        color="tab:green",
        alpha=0.25,
    )
    axs[2].plot(
        true_Mn_90C["Conversion (%)"],
        true_Mn_90C["Mn (Da)"] / 1e5,
        "o",
        color="tab:orange",
        alpha=0.25,
    )
    axs[2].plot(
        true_Mw_90C["Conversion (%)"],
        true_Mw_90C["Mw (Da)"] / 1e5,
        "o",
        color="tab:orange",
        alpha=0.25,
    )

    for ax in axs:
        ax.set_xlabel("Monomer conversion")
        ax.set_ylabel("Mn or Mw (10$^5$ Da)")
        ax.tick_params(axis="both", direction="in", top=True, right=True)
    plt.tight_layout()
    plt.show()
