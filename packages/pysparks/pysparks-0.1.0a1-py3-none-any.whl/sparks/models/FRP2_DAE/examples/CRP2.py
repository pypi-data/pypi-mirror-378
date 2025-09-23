from ..model import ModelState, RateCoefficients


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
