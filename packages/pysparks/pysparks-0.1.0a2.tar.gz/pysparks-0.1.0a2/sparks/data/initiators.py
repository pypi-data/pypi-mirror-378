from enum import Enum
from dataclasses import dataclass
from typing import Dict

from sparks.utils.formulas import arrhenius_eqn
from sparks.core import R_cal
from .monomers import MonomerType

# +-----------------------------------------------------------
# | Initiator Rate Constants and Properties sourced from WATPOLY
# | (https://doi.org/10.1080/10601325.2017.1312678)
# | and other literature sources as noted below
# +-----------------------------------------------------------


class InitiatorType(Enum):
    General = "General"
    AIBN = "AIBN"
    BPO = "BPO"
    dTBPO = "dTBPO"
    TBPA = "TBPA"
    TBPB = "TBPB"


@dataclass
class InitiatorData:

    name: str
    id: InitiatorType

    # Initiator molecular weight (g/mol)
    MW: float

    # Decomposition rate constant (L/min)
    kd: Dict[MonomerType, float]

    # Initiator efficiency
    f: Dict[MonomerType, float]

    # Critical free volume for diffusion-control
    Vf_i: Dict[MonomerType, float]

    # Rate of decrease of f
    C: Dict[MonomerType, float]


def AIBN(T_K: float) -> InitiatorData:
    return InitiatorData(
        name="AIBN",
        id=InitiatorType.AIBN,
        MW=164.21,
        kd={
            MonomerType.Sty: arrhenius_eqn(6.33e16, 3.0719e4, R=R_cal)(T_K),
            MonomerType.EA: arrhenius_eqn(7.7803e16, 3.0704e4, R=R_cal)(T_K),
            MonomerType.General: arrhenius_eqn(6.23e16, 3.0704e4, R=R_cal)(T_K),
        },
        f={
            MonomerType.Sty: 0.6,
            MonomerType.BMA: 0.42,
            MonomerType.General: arrhenius_eqn(0.0247, -2166, R=R_cal)(T_K),
        },
        Vf_i={
            MonomerType.Sty: 0.04,
            MonomerType.BA: 0.15,
            MonomerType.EA: arrhenius_eqn(0.825, 1175, R=R_cal)(T_K),
            MonomerType.BMA: 0.09,
            MonomerType.General: arrhenius_eqn(0.6365, 1368.8, R=R_cal)(T_K),
        },
        C={
            MonomerType.Sty: 0.5,
            MonomerType.BA: 1,
            MonomerType.EA: 1,
            MonomerType.General: 0.685,
        },
    )


def dTBPO(T_K: float) -> InitiatorData:
    return InitiatorData(
        name="di-tert-butyl peroxide",
        id=InitiatorType.dTBPO,
        MW=146.23,
        kd={
            # MonomerType.MMA: arrhenius_eqn(1.68e16, 3.5e4, R=R_cal)(T_K),
            MonomerType.MMA: arrhenius_eqn(7.29e16, 3.56e4, R=R_cal)(T_K),
            MonomerType.General: arrhenius_eqn(7.29e16, 3.56e4, R=R_cal)(T_K),
        },
        f={
            MonomerType.MMA: 0.7,
            MonomerType.BA: 0.3,
            MonomerType.General: 0.5,
        },
        Vf_i={MonomerType.General: 0.15},
        C={MonomerType.General: 0.25},
    )
