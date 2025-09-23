from typing import Any, Dict, List, Tuple

import numpy as np
import pandas as pd
from runkmc.simulation import SimulationResult

from sparks.models import SimulationData
from sparks.simulators.stochastic import KMCConfig
from .model import ModelState, RateCoefficients, ChainModelState, SequenceModelState


def get_FRP2_kmc_inputs(
    k: RateCoefficients, s0: ModelState, config: KMCConfig
) -> Dict[str, Any]:

    return {
        "num_units": config.num_particles,
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
        "num_units": config.num_particles,
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


def build_chain_model_state(df: pd.DataFrame) -> SimulationData[ChainModelState]:

    t = df["KMC Time"].values
    zeros = np.zeros_like(t)
    NACL = df["nAvgChainLength"].values
    WACL = df["wAvgChainLength"].values

    cms = ChainModelState(
        t=t,
        lam_0=zeros,
        lam_1=zeros,
        lam_2=zeros,
        mu_0=np.ones_like(t),
        mu_1=NACL,
        mu_2=WACL * NACL,
    )
    return SimulationData[ChainModelState].from_trajectory(cms)


def build_sequence_model_state(df: pd.DataFrame) -> SimulationData[SequenceModelState]:

    t = df["KMC Time"].values
    zeros = np.zeros_like(t)
    NASL_A = df["nAvgSequenceLength_A"].values
    NASL_B = df["nAvgSequenceLength_B"].values
    WASL_A = df["wAvgSequenceLength_A"].values
    WASL_B = df["wAvgSequenceLength_B"].values

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
        iSA1=NASL_A,
        iSB1=NASL_B,
        iSA2=WASL_A * NASL_A,
        iSB2=WASL_B * NASL_B,
    )

    return SimulationData[SequenceModelState].from_trajectory(sms)


def build_pos_sequence_model_state(
    df: pd.DataFrame,
) -> List[SimulationData[SequenceModelState]]:

    pos_sms = []
    for pos, group_df in df.groupby("Bucket"):

        group_df = group_df.sort_values("KMC Time")

        t = np.insert(group_df["KMC Time"].values, 0, 0)
        zeros = np.zeros_like(t)
        mc_A = np.insert(group_df["MonomerCount_A"].values, 0, 0)
        mc_B = np.insert(group_df["MonomerCount_B"].values, 0, 0)
        sc_A = np.insert(group_df["SequenceCount_A"].values, 0, 0)
        sc_B = np.insert(group_df["SequenceCount_B"].values, 0, 0)
        sl2_A = np.insert(group_df["SequenceLengths2_A"].values, 0, 0)
        sl2_B = np.insert(group_df["SequenceLengths2_B"].values, 0, 0)

        NASL_A = np.divide(mc_A, sc_A, where=sc_A != 0)
        NASL_B = np.divide(mc_B, sc_B, where=sc_B != 0)
        WASL_A = np.divide(sl2_A, sc_A, where=sc_A != 0)
        WASL_B = np.divide(sl2_B, sc_B, where=sc_B != 0)

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
            iSA1=NASL_A,
            iSB1=NASL_B,
            iSA2=WASL_A * NASL_A,
            iSB2=WASL_B * NASL_B,
        )
        sms_data = SimulationData[SequenceModelState].from_trajectory(sms)
        pos_sms.append(sms_data)

    return pos_sms


def build_FRP2_model_state(df: pd.DataFrame) -> SimulationData[ModelState]:

    NAV = df["NAV"].values
    t = df["KMC Time"].values
    I = df["I Count"].values / NAV
    R = df["R Count"].values / NAV
    A = df["A Count"].values / NAV
    B = df["B Count"].values / NAV
    RA = df["P[R.A] Count"].values / NAV
    RB = df["P[R.B] Count"].values / NAV
    PAA = df["P[A.A] Count"].values / NAV
    PAB = df["P[A.B] Count"].values / NAV
    PBA = df["P[B.A] Count"].values / NAV
    PBB = df["P[B.B] Count"].values / NAV
    P = PAA + PAB + PBA + PBB
    PD = df["D Count"].values / NAV

    state = ModelState(t, I, R, A, B, RA, RB, PAA, PAB, PBA, PBB, PD)
    init_state = ModelState(
        t=t[0],
        I=I[0],
        R=R[0],
        A=A[0],
        B=B[0],
        RA=RA[0],
        RB=RB[0],
        PAA=PAA[0],
        PAB=PAB[0],
        PBA=PBA[0],
        PBB=PBB[0],
        PD=PD[0],
    )
    return SimulationData[ModelState].from_trajectory(state)
    # return SimulationData[ModelState](trajectory=state, init_state=init_state)


def build_CRP3_model_state(df: pd.DataFrame) -> SimulationData[ModelState]:

    NAV = df["NAV"].values
    t = df["KMC Time"].values
    I = np.zeros_like(t)
    R = df["I Count"].values / NAV
    A = df["A Count"].values / NAV
    B = df["B Count"].values / NAV
    RA = df["P[I.A] Count"].values / NAV
    RB = df["P[I.B] Count"].values / NAV
    PAA = df["P[-.A.A] Count"].values / NAV
    PAB = df["P[-.A.B] Count"].values / NAV
    PBA = df["P[-.B.A] Count"].values / NAV
    PBB = df["P[-.B.B] Count"].values / NAV
    PD = df["D Count"].values / NAV

    state = ModelState(t, I, R, A, B, RA, RB, PAA, PAB, PBA, PBB, PD)
    init_state = ModelState(
        t=t[0],
        I=0,
        R=R[0],
        A=A[0],
        B=B[0],
        RA=RA[0],
        RB=RB[0],
        PAA=PAA[0],
        PAB=PAB[0],
        PBA=PBA[0],
        PBB=PBB[0],
        PD=PD[0],
    )
    return SimulationData[ModelState].from_trajectory(state)
    # return SimulationData[ModelState](trajectory=state, init_state=init_state)


def parse_kmc_outputs(
    result: SimulationResult, model_name: str
) -> Tuple[SimulationData[ModelState], Any]:

    df = result.load_results()

    model_data = None
    if model_name == "FRP2":
        model_data = build_FRP2_model_state(df)
    elif model_name == "CRP3":
        model_data = build_CRP3_model_state(df)
    else:
        raise ValueError(f"Unknown model name: {model_name}")

    cms = build_chain_model_state(df)
    sms = build_sequence_model_state(df)

    seq_df = result.load_sequence_data()
    pos_sms = None
    if seq_df is not None and not seq_df.empty:
        pos_sms = build_pos_sequence_model_state(seq_df)

    mdata = {"cms": cms, "sms": sms, "pos_sms": pos_sms}

    return model_data, mdata
