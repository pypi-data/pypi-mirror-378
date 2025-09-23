from typing import Optional, Tuple, Dict

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.axes import Axes

from sparks.core import okprint, warnprint, dbgprint
from sparks.models import SimulationData
from sparks.simulators import DeterministicSimulator
from sparks.data.initiators import dTBPO
from sparks.data.monomers import alpha_methyl_styrene, methyl_methacrylate
from sparks.utils.formulas import C_to_K

from ..model import (
    Model,
    ModelState,
    RateCoefficients,
    SequenceModel,
    SequenceModelState,
)

##################################################
### HIGH TEMPERATURE AMS-MMA (115 C and 140 C) ###
##################################################

COLOR_115 = "#009ADE"
COLOR_140 = "#FF1F5B"


# ---- Experimental and model validation data ----

CONDS = {
    "T_115C": {"T_C": 115, "wAMS": 0.45, "wDTBPO": 0.02, "t_end_min": 1450},
    "T_140C": {"T_C": 140, "wAMS": 0.45, "wDTBPO": 0.02, "t_end_min": 1080},
}

# ---- Example Conditions ----


def k_AMS_MMA(temp_C: float) -> RateCoefficients:
    """Return the rate coefficients for the AMS MMA model at a given temperature in Celsius."""

    temp_K = C_to_K(temp_C)

    iprops = dTBPO(temp_K)
    mpropsA = alpha_methyl_styrene(temp_K)
    mpropsB = methyl_methacrylate(temp_K)

    kpAA = mpropsA.kp
    kpBB = mpropsB.kp

    dbgprint(f"Rate coefficients at {temp_C} C:")
    dbgprint(f"kp AMS: {kpAA/1e4:.4f}, kp MMA: {kpBB/1e4:.4f}")
    dbgprint(f"kt AMS: {mpropsA.kt/1e10:.4f}, kt MMA: {mpropsB.kt/1e10:.4f}")
    print()

    rA = 0.16
    rB = 0.41
    kpAB = kpAA / rA
    kpBA = kpBB / rB

    if temp_C == 115:
        KAA = 35
        KBB = 0.22
        qA = 8.2
        qB = 0.0
        kdBA = qA * kpAB
        kdAB = qB * kpBA
        KAB = kdAB / kpAB
        KBA = kdBA / kpBA
    elif temp_C == 140:
        KAA = 54
        KBB = 0.45
        qA = 19.1
        qB = 1.27
        kdBA = qA * kpAB
        kdAB = qB * kpBA
        KAB = kdAB / kpAB
        KBA = kdBA / kpBA
    else:
        raise ValueError(
            f"Unsupported temperature: {temp_C} C. Supported temperatures are 115 C and 140 C."
        )
    dbgprint(f"rA: {rA:.4f}, rB: {rB:.4f}")
    dbgprint(f"KAA: {KAA:.4f}, KAB: {KAB:.4f}, KBA: {KBA:.4f}, KBB: {KBB:.4f}")
    print()

    return RateCoefficients(
        T_C=temp_C,
        iprops=iprops,
        mpropsA=mpropsA,
        mpropsB=mpropsB,
        rA=rA,
        rB=rB,
        KAA=KAA,
        KAB=KAB,
        KBA=KBA,
        KBB=KBB,
    )


def c0_AMS_MMA(T_C: float, wAMS: float, wDTBPO: float) -> ModelState:
    """Create initial state for AMS-MMA simulation with specified weights."""
    temp_K = C_to_K(T_C)

    iprops = dTBPO(temp_K)
    mpropsA = alpha_methyl_styrene(temp_K)
    mpropsB = methyl_methacrylate(temp_K)

    wMMA = 1 - wAMS

    m_basis = 1000  # Basis in grams
    m_AMS = wAMS * (1 - wDTBPO) * m_basis
    m_MMA = wMMA * (1 - wDTBPO) * m_basis
    m_DTBP = wDTBPO * m_basis

    # Calculate moles
    mol_AMS = m_AMS / mpropsA.MW
    mol_MMA = m_MMA / mpropsB.MW
    mol_DTBP = m_DTBP / iprops.MW

    # Calculate volume in L
    v_AMS = m_AMS / mpropsA.dens_m
    v_MMA = m_MMA / mpropsB.dens_m
    v_total = v_AMS + v_MMA

    V_basis = v_total
    I = mol_DTBP
    A = mol_AMS
    B = mol_MMA

    return ModelState(V=V_basis, I=I, A=A, B=B)


# ---- Generate data for validation ----

solver_kwargs = dict(method="BDF", rtol=1e-8, atol=1e-8)


def get_sim_data() -> Tuple[DeterministicSimulator, DeterministicSimulator]:

    T_C = 115
    ds_115 = DeterministicSimulator(Model(), k=k_AMS_MMA(T_C))
    data_115 = ds_115.simulate(
        t_eval=np.linspace(0, 1450, 1000),
        init_state=c0_AMS_MMA(T_C, wAMS=0.45, wDTBPO=0.02),
        solver_kwargs=solver_kwargs,
    )

    T_C = 140
    ds_140 = DeterministicSimulator(Model(), k=k_AMS_MMA(T_C))
    data_140 = ds_140.simulate(
        t_eval=np.linspace(0, 1080, 1000),
        init_state=c0_AMS_MMA(T_C, wAMS=0.45, wDTBPO=0.02),
        solver_kwargs=solver_kwargs,
    )

    return ds_115, ds_140


def get_sim_sequence_data(
    ds_115: DeterministicSimulator, ds_140: DeterministicSimulator
) -> Tuple[DeterministicSimulator, DeterministicSimulator]:

    T_C = 115
    ds_115s = DeterministicSimulator(SequenceModel(), k=k_AMS_MMA(T_C))
    data_115 = ds_115s.simulate(
        t_eval=np.linspace(0, 1450, 1000),
        init_state=SequenceModelState(),
        solver_kwargs=solver_kwargs,
        s=ds_115.ode_sol,
    )

    T_C = 140
    ds_140s = DeterministicSimulator(SequenceModel(), k=k_AMS_MMA(T_C))
    data_140 = ds_140s.simulate(
        t_eval=np.linspace(0, 1080, 1000),
        init_state=SequenceModelState(),
        solver_kwargs=solver_kwargs,
        s=ds_140.ode_sol,
    )

    return ds_115s, ds_140s


# ---- Manuscript figures ----


def plot_conv_validation(
    data: Dict[str, SimulationData[ModelState]],
    exp_data: Optional[Dict[str, pd.DataFrame]] = None,
):
    """Plot conversion validation for all conditions."""

    fig, ax = plt.subplots(1, figsize=(3.5, 3.5), dpi=300)

    for i, (cond_name, sim_data) in enumerate(data.items()):

        condition = CONDS[cond_name]
        color = COLOR_115 if condition["T_C"] == 115 else COLOR_140

        cond_id = f"{int(100 * condition['wAMS'])} wt% AMS, {condition['wDTBPO'] * 100} wt% DTBPO"
        ax.plot(
            sim_data.trajectory.t,
            sim_data.trajectory.x(sim_data.init_state),
            label=cond_id,
            color=color,
        )

        if exp_data is None or cond_name not in exp_data:
            continue

        _exp_data = exp_data.get(cond_name)

        ax.plot(
            _exp_data["Time (min)"],
            _exp_data["Conversion (%)"],
            "^",
            color=color,
            alpha=0.5,
        )

    ax.tick_params(axis="both", direction="in", top=True, right=True)
    ax.set_xlim(0, 1600)
    ax.set_ylim(0, 0.8)
    ax.set_xticks([0, 400, 800, 1200, 1600])
    ax.set_xlabel("Time (min)")
    ax.set_ylabel("Total conversion")

    add_exp_ode_legend(ax, frameon=False, loc="lower right")

    return fig, ax


def plot_comp_validation(
    data: Dict[str, SimulationData[ModelState]],
    exp_data: Optional[Dict[str, pd.DataFrame]] = None,
):
    """Plot composition validation for all conditions."""
    fig, ax = plt.subplots(1, figsize=(3.5, 3.5), dpi=300)

    for i, (cond_name, sim_data) in enumerate(data.items()):

        condition = CONDS[cond_name]
        color = COLOR_115 if condition["T_C"] == 115 else COLOR_140

        cond_id = f"{int(100 * condition['wAMS'])} wt% AMS, {condition['wDTBPO'] * 100} wt% DTBPO"
        ax.plot(
            sim_data.trajectory.x(sim_data.init_state)[1:],
            sim_data.trajectory.FbarB[1:],
            label=cond_id,
            color=color,
        )

        if exp_data is None or cond_name not in exp_data:
            continue

        _exp_data = exp_data.get(cond_name)

        ax.plot(
            _exp_data["Conversion (%)"],
            1 - _exp_data["Composition (%)"],
            "^",
            color=color,
            alpha=0.5,
        )

    ax.tick_params(axis="both", direction="in", top=True, right=True)
    ax.set_ylim(0.5, 1.0)
    ax.set_xlim(0, 0.8)
    ax.set_xticks([0, 0.2, 0.4, 0.6, 0.8])
    ax.set_xticklabels(["0", "0.2", "0.4", "0.6", "0.8"])
    ax.set_xlabel("Total conversion")
    ax.set_ylabel("Copolymer Composition (MMA)")

    add_exp_ode_legend(ax, frameon=False, loc="lower left")

    return fig, ax


def plot_sequence_data(
    data: Dict[
        str, Tuple[SimulationData[ModelState], SimulationData[SequenceModelState]]
    ],
):
    """Plot composition validation for all conditions."""
    fig, ax = plt.subplots(1, figsize=(3.5, 3.5), dpi=300)

    for i, (cond_name, (sim_data, seq_data)) in enumerate(data.items()):

        condition = CONDS[cond_name]
        color = COLOR_115 if condition["T_C"] == 115 else COLOR_140

        cond_id = f"{int(100 * condition['wAMS'])} wt% AMS, {condition['wDTBPO'] * 100} wt% DTBPO"

        x_vals = sim_data.trajectory.x(sim_data.init_state)
        # end_idx = np.argmax(x_vals >= 0.59) if condition["T_C"] == 140 else None
        end_idx = None
        ax.plot(
            x_vals[1:end_idx],
            seq_data.trajectory.active_NASL_B[1:end_idx],
            label=cond_id,
            color=color,
        )

    ax.plot([0, 0.8], [1, 1], "k--")
    ax.tick_params(axis="both", direction="in", top=True, right=True)
    ax.set_ylim(0.5, 14.5)
    ax.set_xlim(0, 0.8)
    ax.set_xticks([0, 0.2, 0.4, 0.6, 0.8])
    ax.set_xticklabels(["0", "0.2", "0.4", "0.6", "0.8"])
    ax.set_yticks([2, 4, 6, 8, 10, 12, 14])
    ax.set_xlabel("Total conversion")
    ax.set_ylabel("Inst. Avg. Sequence Length (MMA)")

    return fig, ax


def add_exp_ode_legend(axs: Axes, **kwargs):

    markersize = kwargs.pop("markersize", 5)
    exp_dot = axs.plot(
        [], [], "k", label="Experiments", alpha=0.5, markersize=markersize, marker="^"
    )
    ode_line = axs.plot([], [], "k-", label="ODE", alpha=1.0)

    axs.legend(
        handles=[exp_dot[0], ode_line[0]],
        **kwargs,
    )

    return axs
