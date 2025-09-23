from typing import Dict, List, Tuple

import numpy as np

from sparks.models import StateType, SimulationData
from sparks.simulators import DeterministicSimulator, StochasticSimulator
from ..model import (
    Model,
    ModelState,
    RateCoefficients,
    SequenceModel,
    SequenceModelState,
)


def k_CRP2_from_ratios(
    rA: float,
    rB: float,
    rX: float = 1.0,
    KAA: float = 0.0,
    KAB: float = 0.0,
    KBA: float = 0.0,
    KBB: float = 0.0,
    kpAA: float = 1.0,
) -> RateCoefficients:

    # rX = kpAA / kpBB
    kpBB = kpAA / rX

    kpAB = kpAA / rA
    kpBA = kpBB / rB

    kdAA = KAA * kpAA
    kdAB = KAB * kpAB
    kdBA = KBA * kpBA
    kdBB = KBB * kpBB

    return RateCoefficients(
        kpAA=kpAA,
        kpAB=kpAB,
        kpBA=kpBA,
        kpBB=kpBB,
        kdAA=kdAA,
        kdAB=kdAB,
        kdBA=kdBA,
        kdBB=kdBB,
    )


def k_CRP2_equal_from_ratio(
    rA: float,
    rB: float,
    K: float,
    **kwargs,
) -> RateCoefficients:

    return k_CRP2_from_ratios(rA=rA, rB=rB, KAA=K, KAB=K, KBA=K, KBB=K, **kwargs)


def c0_CRP2(
    fA0: float = 0.50, M0: float = 1.0, M0_I0_ratio: float = 1000.0
) -> ModelState:

    A0 = fA0 * M0
    B0 = (1 - fA0) * M0
    R0 = M0 / M0_I0_ratio

    return ModelState(R=R0, A=A0, B=B0)


def get_ode_model(
    T_C: float,
    fA0: float,
    M0: float,
    M2Iratio: float = 1000,
    rA: float = 15.0,
    rB: float = 0.5,
    KAA: float = 0.0,
    **kwargs,
) -> Tuple[SimulationData[ModelState], SimulationData[SequenceModelState]]:

    A0, B0 = fA0 * M0, (1 - fA0) * M0
    k = k_CRP2_from_ratios(rA, rB, KAA=KAA)
    init_state = ModelState(
        R=M0 / M2Iratio,
        A=A0,
        B=B0,
    )
    print(f"rA: {rA}, rB: {rB}, KAA: {KAA}")

    t_eval = np.linspace(0, 5e4, 10000)
    t_eval = kwargs.pop("t_eval", t_eval)

    ds = DeterministicSimulator(Model(), k)
    data = ds.simulate(
        t_eval=t_eval,
        init_state=init_state,
    )

    ds_seq = DeterministicSimulator(SequenceModel(), k)
    seq_data = ds_seq.simulate(
        t_eval=t_eval, init_state=SequenceModelState(), s=ds.ode_sol
    )

    return data, seq_data


def get_kmc_model(
    T_C: float,
    fA0: float,
    M0: float,
    M2Iratio: float = 1000,
    rA: float = 15.0,
    rB: float = 0.5,
    KAA: float = 0.0,
    **kwargs,
) -> Tuple[
    SimulationData[ModelState],
    Dict[str, SimulationData[StateType] | List[SimulationData[StateType]]],
]:

    A0, B0 = fA0 * M0, (1 - fA0) * M0
    k = k_CRP2_from_ratios(rA, rB, KAA=KAA)
    init_state = ModelState(
        R=M0 / M2Iratio,
        A=A0,
        B=B0,
    )
    print(f"rA: {rA}, rB: {rB}, KAA: {KAA}")

    ss = StochasticSimulator(Model(), k, data_dir="./simulations")

    data = ss.simulate(
        t_eval=kwargs.pop("t_eval", np.linspace(0, 5e4, 1000)),
        init_state=init_state,
        num_particles=kwargs.pop("num_particles", 1e7),
        model_name="CRP3",
        report_polymers=kwargs.pop("report_polymers", False),
        report_sequences=kwargs.pop("report_sequences", False),
        overwrite=kwargs.pop("overwrite", False),
        **kwargs,
    )

    return data, ss.mdata
