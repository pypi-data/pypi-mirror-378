from typing import Any, Dict, List, Tuple

import numpy as np
from runkmc.results import SimulationResult

from sparks.models import SimulationData
from sparks.simulators.stochastic import KMCConfig
from .model import ModelState, RateCoefficients, ChainModelState, SequenceModelState


def get_FRP2_kmc_inputs(
    k: RateCoefficients, s0: ModelState, config: KMCConfig
) -> Dict[str, Any]:

    return {
        "num_units": config.num_units,
        "termination_time": config.termination_time,
        "analysis_time": config.analysis_time,
        "I_c0": float(s0.I),
        "R_c0": float(s0.R),
        "A_c0": float(s0.A),
        "B_c0": float(s0.B),
        "I_FW": 0.0,
        "R_FW": 1.0,
        "A_FW": 100.0,
        "B_FW": 200.0,
        "kd": k.kd,
        "kpAA": k.kpAA,
        "kpAB": k.kpAB,
        "kpBA": k.kpBA,
        "kpBB": k.kpBB,
        "kdAA": k.kdAA,
        "kdAB": k.kdAB,
        "kdBA": k.kdBA,
        "kdBB": k.kdBB,
        "ktcAA": k.ktcAA,
        "ktcAB": k.ktcAB,
        "ktcBB": k.ktcBB,
        "ktdAA": k.ktdAA,
        "ktdAB": k.ktdAB,
        "ktdBB": k.ktdBB,
    }


def get_CRP3_kmc_inputs(
    k: RateCoefficients, s0: ModelState, config: KMCConfig
) -> Dict[str, Any]:

    return {
        "num_units": config.num_units,
        "termination_time": config.termination_time,
        "analysis_time": config.analysis_time,
        "I_c0": float(s0.R),
        "A_c0": float(s0.A),
        "B_c0": float(s0.B),
        "I_FW": 1.0,
        "A_FW": 100.0,
        "B_FW": 200.0,
        "kpAA": k.kpAA,
        "kpAB": k.kpAB,
        "kpBA": k.kpBA,
        "kpBB": k.kpBB,
        "kdAA": k.kdAA,
        "kdAB": k.kdAB,
        "kdBA": k.kdBA,
        "kdBB": k.kdBB,
    }


def get_kmc_inputs(
    k: RateCoefficients, s0: ModelState, config: KMCConfig, model_name: str
) -> Dict[str, Any]:

    if model_name == "CRP3":
        return get_CRP3_kmc_inputs(k, s0, config)
    elif model_name == "FRP2":
        return get_FRP2_kmc_inputs(k, s0, config)
    else:
        raise ValueError(f"Unknown model name: {model_name}")


def build_chain_model_state(
    results: SimulationResult,
) -> SimulationData[ChainModelState]:

    data = results.results
    t = data.kmc_time
    zeros = np.zeros_like(t)

    cms = ChainModelState(
        t=t,
        lam_0=zeros,
        lam_1=zeros,
        lam_2=zeros,
        mu_0=np.ones_like(t),
        mu_1=data.nAvgCL,
        mu_2=data.wAvgCL * data.nAvgCL,
    )

    return SimulationData[ChainModelState].from_trajectory(cms)


def build_sequence_model_state(
    results: SimulationResult,
) -> SimulationData[SequenceModelState]:

    data = results.results
    t = data.kmc_time
    zeros = np.zeros_like(t)

    sms = SequenceModelState(
        t=t,
        aSA0=zeros,
        aSB0=zeros,
        aSA1=zeros,
        aSB1=zeros,
        aSA2=zeros,
        aSB2=zeros,
        iSA0=np.ones_like(t),
        iSB0=np.ones_like(t),
        iSA1=data.nAvgSL["A"],
        iSB1=data.nAvgSL["B"],
        iSA2=data.wAvgSL["A"] * data.nAvgSL["A"],
        iSB2=data.wAvgSL["B"] * data.nAvgSL["B"],
    )

    return SimulationData[SequenceModelState].from_trajectory(sms)


def build_pos_sequence_model_state(
    results: SimulationResult,
) -> List[SimulationData[SequenceModelState]]:

    from runkmc.results import SequenceData

    seq_data = results.sequence_data
    if seq_data is None:
        print("No sequence data found in results.")
        return []

    pos_sms = []
    buckets = sorted(np.unique(seq_data.bucket))

    buckets = seq_data.get_buckets()

    for pos in buckets:

        _seq_data = seq_data.get_by_bucket(pos)

        assert isinstance(_seq_data, SequenceData)

        t = _seq_data.kmc_time
        zeros = np.zeros_like(t)
        sms = SequenceModelState(
            t=t,
            aSA0=zeros,
            aSB0=zeros,
            aSA1=zeros,
            aSB1=zeros,
            aSA2=zeros,
            aSB2=zeros,
            iSA0=np.ones_like(t),
            iSB0=np.ones_like(t),
            iSA1=_seq_data.nAvgSL["A"],
            iSB1=_seq_data.nAvgSL["B"],
            iSA2=_seq_data.wAvgSL["A"] * _seq_data.nAvgSL["A"],
            iSB2=_seq_data.wAvgSL["B"] * _seq_data.nAvgSL["B"],
        )
        sms_data = SimulationData[SequenceModelState].from_trajectory(sms)
        pos_sms.append(sms_data)

    return pos_sms


def build_FRP2_state(results: SimulationResult) -> SimulationData[ModelState]:

    data = results.results

    NAV = data.NAV
    state = ModelState(
        t=data.kmc_time,
        I=data.unit_counts["I"] / NAV,
        R=data.unit_counts["R"] / NAV,
        A=data.unit_counts["A"] / NAV,
        B=data.unit_counts["B"] / NAV,
        RA=data.polymer_counts["P[R.A]"] / NAV,
        RB=data.polymer_counts["P[R.B]"] / NAV,
        PAA=data.polymer_counts["P[A.A]"] / NAV,
        PAB=data.polymer_counts["P[A.B]"] / NAV,
        PBA=data.polymer_counts["P[B.A]"] / NAV,
        PBB=data.polymer_counts["P[B.B]"] / NAV,
        PD=data.polymer_counts["D"] / NAV,
    )

    return SimulationData[ModelState].from_trajectory(state)


def build_CRP3_state(results: SimulationResult) -> SimulationData[ModelState]:

    data = results.results

    NAV = data.NAV
    state = ModelState(
        t=data.kmc_time,
        I=np.zeros_like(NAV),
        R=data.unit_counts["R"] / NAV,
        A=data.unit_counts["A"] / NAV,
        B=data.unit_counts["B"] / NAV,
        RA=data.polymer_counts["P[I.A]"] / NAV,
        RB=data.polymer_counts["P[I.B]"] / NAV,
        PAA=data.polymer_counts["P[-.A.A]"] / NAV,
        PAB=data.polymer_counts["P[-.A.B]"] / NAV,
        PBA=data.polymer_counts["P[-.B.A]"] / NAV,
        PBB=data.polymer_counts["P[-.B.B]"] / NAV,
        PD=data.polymer_counts["D"] / NAV,
    )

    return SimulationData[ModelState].from_trajectory(state)


def parse_kmc_outputs(
    result: SimulationResult, model_name: str
) -> Tuple[SimulationData[ModelState], Any]:

    model_data = None
    if model_name == "FRP2":
        model_data = build_FRP2_state(result)
    elif model_name == "CRP3":
        model_data = build_CRP3_state(result)
    else:
        raise ValueError(f"Unknown model name: {model_name}")

    cms = build_chain_model_state(result)
    sms = build_sequence_model_state(result)

    pos_sms = None
    if result.sequence_data is not None:
        pos_sms = build_pos_sequence_model_state(result)

    mdata = {"cms": cms, "sms": sms, "pos_sms": pos_sms}

    return model_data, mdata
