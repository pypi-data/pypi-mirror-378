from typing import Tuple

import numpy as np

from sparks.utils import dbgprint
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
