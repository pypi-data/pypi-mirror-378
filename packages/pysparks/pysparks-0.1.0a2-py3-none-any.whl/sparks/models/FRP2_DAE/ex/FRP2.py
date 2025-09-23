from sparks.models import ReactionNetworkDef
from ..model import RateCoefficients, ModelState
from ..reactions import (
    initiator_decomposition_rxn,
    propagation_rxn,
    depropagation_rxn,
    termination_rxn,
)


def k_FRP2_equal() -> RateCoefficients:

    kp = 1.0e03
    f_kd = 0.5
    ktd = 1.0e07

    return RateCoefficients(
        kd=3.0e-06,
        f=0.5,
        kpAA=kp,
        kpAB=kp,
        kpBA=kp,
        kpBB=kp,
        kdAA=f_kd * kp,
        kdAB=f_kd * kp,
        kdBA=f_kd * kp,
        kdBB=f_kd * kp,
        ktcAA=0,
        ktcAB=0,
        ktcBB=0,
        ktdAA=ktd,
        ktdAB=ktd,
        ktdBB=ktd,
    )


def k_FRP2_from_ratios(
    rA: float,
    rB: float,
    rX: float = 1.0,
    KAA: float = 0.0,
    KAB: float = 0.0,
    KBA: float = 0.0,
    KBB: float = 0.0,
    kpAA: float = 1.0,
    kd: float = 3.0e-06,
    kt: float = 1.0e7,
    ktd_frac: float = 1.0,
) -> RateCoefficients:

    # rX = kpAA / kpBB
    kpBB = kpAA / rX

    kpAB = kpAA / rA
    kpBA = kpBB / rB

    kdAA = KAA * kpAA
    kdAB = KAB * kpAB
    kdBA = KBA * kpBA
    kdBB = KBB * kpBB

    ktdAA = ktd_frac * kt
    ktdAB = ktd_frac * kt
    ktdBB = ktd_frac * kt
    ktcAA = (1 - ktd_frac) * kt
    ktcAB = (1 - ktd_frac) * kt
    ktcBB = (1 - ktd_frac) * kt

    return RateCoefficients(
        kd=kd,
        f=0.5,
        kpAA=kpAA,
        kpAB=kpAB,
        kpBA=kpBA,
        kpBB=kpBB,
        kdAA=kdAA,
        kdAB=kdAB,
        kdBA=kdBA,
        kdBB=kdBB,
        ktcAA=ktcAA,
        ktcAB=ktcAB,
        ktcBB=ktcBB,
        ktdAA=ktdAA,
        ktdAB=ktdAB,
        ktdBB=ktdBB,
    )


def k_FRP2_equal_from_ratio(
    rA: float,
    rB: float,
    K: float,
    **kwargs,
) -> RateCoefficients:

    return k_FRP2_from_ratios(
        rA=rA,
        rB=rB,
        KAA=K,
        KAB=K,
        KBA=K,
        KBB=K,
        **kwargs,
    )


def c0_FRP2(
    fA0: float = 0.50, M0: float = 1.0, M0_I0_ratio: float = 1000.0
) -> ModelState:

    A0 = fA0 * M0
    B0 = (1 - fA0) * M0
    I0 = M0 / M0_I0_ratio

    return ModelState(I=I0, A=A0, B=B0)


def FRP2_Reactions() -> ReactionNetworkDef:

    reactions = {}
    reactions.update(initiator_decomposition_rxn())
    reactions.update(propagation_rxn())
    reactions.update(depropagation_rxn())
    reactions.update(termination_rxn())
    return reactions
