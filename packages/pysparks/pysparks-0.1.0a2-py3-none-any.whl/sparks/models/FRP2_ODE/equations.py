from sparks.core import NDArrayType
from .model import RateCoefficients, ModelState, SequenceModelState, ChainModelState


def kinetic_odes(
    dydt: ModelState,
    k: RateCoefficients,
    t: NDArrayType,
    s: ModelState,
) -> ModelState:
    """Defines the ODEs for the full FRP2 model."""

    dydt.t = t

    kp = (
        # i=A, j=A
        (k.kpAA * s.pA * s.fA - k.kdAA * s.pAA * s.pA / s.M)
        # i=A, j=B
        + (k.kpAB * s.pA * s.fB - k.kdAB * s.pAB * s.pB / s.M)
        # i=B, j=A
        + (k.kpBA * s.pB * s.fA - k.kdBA * s.pBA * s.pA / s.M)
        # i=B, j=B
        + (k.kpBB * s.pB * s.fB - k.kdBB * s.pBB * s.pB / s.M)
    )

    """ Moles of Initiator """
    dydt.I = -k.kd * s.I

    """ Moles of Free Radical, R """
    dydt.R = (
        # Formation by initiation
        +2 * k.f * k.kd * s.I
        # Consumption by propagation
        - k.kpAA * s.R * s.A
        - k.kpBB * s.R * s.B
    )

    """ Moles of A Monomer """
    dydt.A = (
        # Consumption by propagation
        -k.kpAA * (s.R + s.RA) * s.A
        - k.kpBA * s.RB * s.A
        - k.kpAA * s.PA * s.A
        - k.kpBA * s.PB * s.A
        # Formation by depropagation
        + k.kdAA * s.PAA
        + k.kdBA * s.PBA
    )

    """ Moles of B Monomer """
    dydt.B = (
        # Consumption by propagation
        -k.kpBB * (s.R + s.RB) * s.B
        - k.kpAB * s.RA * s.B
        - k.kpAB * s.PA * s.B
        - k.kpBB * s.PB * s.B
        # Formation by depropagation
        + k.kdAB * s.PAB
        + k.kdBB * s.PBB
    )

    """ Moles of R-A dyad"""
    dydt.RA = (
        # Formation by propagation (R + A -> RA)
        +k.kpAA * s.R * s.A
        # Consumption by propagation (RA + A -> PAA, RA + B -> PAB)
        - k.kpAA * s.RA * s.A
        - k.kpAB * s.RA * s.B
    )

    """ Total moles of R-B dyad """
    dydt.RB = (
        # Formation by propagation (R + B -> RB)
        +k.kpBB * s.R * s.B
        # Consumption by propagation (RB + A -> PBA, RB + B -> PBB)
        - k.kpBA * s.RB * s.A
        - k.kpBB * s.RB * s.B
    )

    c_tAA = c_tBB = 1
    c_tAB = 1

    """ Total moles of ~~AA* polymer """
    dydt.PAA = (
        # Formation by propagation (RA + A -> PAA)
        +k.kpAA * s.RA * s.A
        # Formation by propagation (PBA + A -> PAA)
        + k.kpAA * s.PBA * s.A
        # Consumption by propagation (PAA + B -> PAB)
        - k.kpAB * s.PAA * s.B
        # Formation by depropagation (PAAB -> PAA + B)
        + k.kdAB * s.pAA * s.PAB
        # Consumption by depropagation (PBAA -> PBA + A)
        - k.kdAA * s.pBA * s.PAA
        # Consumption by termination (PAA + PA -> (2)PD, PAA + PB -> (2)PD)
        - c_tAA * k.ktAA * s.PAA * s.PA
        - c_tAB * k.ktAB * s.PAA * s.PB
    )

    """ Total moles of ~~AB* polymer """
    dydt.PAB = (
        # Formation by propagation (RA + B -> PAB)
        +k.kpAB * s.RA * s.B
        # Formation by propagation (PA + B -> PAB)
        + k.kpAB * s.PA * s.B
        # Consumption by propagation (PAB + A -> PBA)
        - k.kpBA * s.PAB * s.A
        # Consumption by propagation (PAB + B -> PBB)
        - k.kpBB * s.PAB * s.B
        # Formation by depropagation (PABA -> PAB + A)
        + k.kdBA * s.pAB * s.PBA
        # Formation by depropagation (PABB -> PAB + B)
        + k.kdBB * s.pAB * s.PBB
        # Consumption by depropagation (PAB -> PA + B)
        - k.kdAB * s.PAB
        # Consumption by termination (PAB + PA -> (2)PD, PAB + PB -> (2)PD)
        - c_tAB * k.ktAB * s.PAB * s.PA
        - c_tBB * k.ktBB * s.PAB * s.PB
    )

    """ Total moles of ~~BA* polymer """
    dydt.PBA = (
        # Formation by propagation (RB + A -> PBA)
        +k.kpBA * s.RB * s.A
        # Formation by propagation (PB + A -> PBA)
        + k.kpBA * s.PB * s.A
        # Consumption by propagation (PBA + A -> PAA)
        - k.kpAA * s.PBA * s.A
        # Consumption by propagation (PBA + B -> PBB)
        - k.kpAB * s.PBA * s.B
        # Formation by depropagation (PBAA -> PBA + A)
        + k.kdAA * s.pBA * s.PAA
        # Formation by depropagation (PBAB -> PBA + B)
        + k.kdAB * s.pBA * s.PAB
        # Consumption by depropagation (PBA -> PB + A)
        - k.kdBA * s.PBA
        # Consumption by termination (PBA + PA -> (2)PD, PBA + PB -> (2)PD)
        - c_tAA * k.ktAA * s.PBA * s.PA
        - c_tAB * k.ktAB * s.PBA * s.PB
    )

    """ Total moles of ~~BB* polymer """
    dydt.PBB = (
        # Formation by propagation (RB + B -> PBB)
        +k.kpBB * s.RB * s.B
        # Formation by propagation (PAB + B -> PBB)
        + k.kpBB * s.PAB * s.B
        # Consumption by propagation (PBB + A -> PBA)
        - k.kpBA * s.PBB * s.A
        # Formation by depropagation (PBBA -> PBB + A)
        + k.kdBA * s.pBB * s.PBA
        # Consumption by depropagation (PABB -> PAB + B)
        - k.kdBB * s.pAB * s.PBB
        # Consumption by termination (PBB + PA -> (2)PD, PBB + PB -> (2)PD)
        - c_tBB * k.ktBB * s.PBB * s.PB
        - c_tAB * k.ktAB * s.PBB * s.PA
    )

    return dydt


def chain_odes(
    dydt: ChainModelState,
    k: RateCoefficients,
    t: NDArrayType,
    cms: ChainModelState,
    s: ModelState,
) -> ChainModelState:

    dydt.t = t
    # s = static_state
    # ode_sol: OdeSolution,
    # s = ModelState.from_array(ode_sol(t))

    ###########################################
    ### Calculate the pseudo rate constants ###
    ###########################################

    # Pseudo rate constant for propagation
    # Mistake in Eq. 52? kdij * Pij * pi / M
    # Should be kdij * Pij * pj / M
    kp = (
        # i=A, j=A
        (k.kpAA * s.pA * s.fA - k.kdAA * s.pAA * s.pA / s.M)
        # i=A, j=B
        + (k.kpAB * s.pA * s.fB - k.kdAB * s.pAB * s.pB / s.M)
        # i=B, j=A
        + (k.kpBA * s.pB * s.fA - k.kdBA * s.pBA * s.pA / s.M)
        # i=B, j=B
        + (k.kpBB * s.pB * s.fB - k.kdBB * s.pBB * s.pB / s.M)
    )

    kt = k.ktAA * s.pA * s.pA + k.ktBB * s.pB * s.pB + 2 * k.ktAB * s.pA * s.pB
    ktc = k.ktcAA * s.pA * s.pA + k.ktcBB * s.pB * s.pB + 2 * k.ktcAB * s.pA * s.pB
    ktd = k.ktdAA * s.pA * s.pA + k.ktdBB * s.pB * s.pB + 2 * k.ktdAB * s.pA * s.pB

    # Formation of polymer from active radicals
    poly_form = k.kpAA * s.R * s.A + k.kpBB * s.R * s.B

    """ Active radicals (0th order moment) """
    dydt.lam_0 = (
        # Formation by propagation
        poly_form
        # Consumption by termination
        - kt * cms.lam_0**2
    )

    """ Active radicals (1st order moment) """
    dydt.lam_1 = (
        # Formation by propagation
        poly_form
        # Formation by propagation
        + kp * s.M * cms.lam_0
        # Consumption by termination
        - kt * cms.lam_0 * cms.lam_1
    )

    """Active radicals (2nd order moment)"""
    dydt.lam_2 = (
        # Formation by propagation
        poly_form
        # Formation by propagation
        + kp * s.M * (cms.lam_0 + 2 * cms.lam_1)
        # Consumption by termination
        - kt * cms.lam_0 * cms.lam_2
    )

    """Dead radicals (0th order moment)"""
    dydt.mu_0 = (
        # Formation by termination
        +(0.5 * ktc + ktd)
        * cms.lam_0**2
    )

    """Dead radicals (1st order moment)"""
    dydt.mu_1 = (
        # Formation by termination
        +(ktc + ktd)
        * cms.lam_0
        * cms.lam_1
    )

    """Dead radicals (2nd order moment)"""
    dydt.mu_2 = (
        # Formation by termination (comb.)
        +ktc * (cms.lam_0 * cms.lam_2 + cms.lam_1**2)
        # Formation by termination (disp.)
        + ktd * cms.lam_0 * cms.lam_2
    )

    return dydt


def sequence_odes(
    dydt: SequenceModelState,
    k: RateCoefficients,
    t: NDArrayType,
    sms: SequenceModelState,
    s: ModelState,
) -> SequenceModelState:

    dydt.t = t

    # sms.aSA0 = sms.aSA0
    # sms.aSB0 = sms.aSB0
    # sms.aSA1 = sms.aSA1
    # sms.aSB1 = sms.aSB1
    # sms.aSA2 = sms.aSA2
    # sms.aSB2 = sms.aSB2

    # Rates of termination
    # Ctrij_x = ktij * sms.aSijx * sms.aSij0
    RtAA_0 = k.ktAA * sms.aSA0 * sms.aSA0
    RtAB_0 = k.ktAB * sms.aSA0 * sms.aSB0
    RtBA_0 = k.ktAB * sms.aSB0 * sms.aSA0
    RtBB_0 = k.ktBB * sms.aSB0 * sms.aSB0
    RtAA_1 = k.ktAA * sms.aSA1 * sms.aSA0
    RtAB_1 = k.ktAB * sms.aSA1 * sms.aSB0
    RtBA_1 = k.ktAB * sms.aSB1 * sms.aSA0
    RtBB_1 = k.ktBB * sms.aSB1 * sms.aSB0
    RtAA_2 = k.ktAA * sms.aSA2 * sms.aSA0
    RtAB_2 = k.ktAB * sms.aSA2 * sms.aSB0
    RtBA_2 = k.ktAB * sms.aSB2 * sms.aSA0
    RtBB_2 = k.ktBB * sms.aSB2 * sms.aSB0

    a10_frac = sms.aSA1 / sms.aSA0 if sms.aSA0 > 0 else 0
    b10_frac = sms.aSB1 / sms.aSB0 if sms.aSB0 > 0 else 0
    a20_frac = sms.aSA2 / sms.aSA0 if sms.aSA0 > 0 else 0
    b20_frac = sms.aSB2 / sms.aSB0 if sms.aSB0 > 0 else 0

    """Active A sequences (0th order moment)"""
    dydt.aSA0 = (
        # Formation by propagation (PA + A -> PA, PB + A -> PA)
        +k.kpAA * s.A * (s.R + sms.aSA0)
        + k.kpBA * s.A * (s.RB + sms.aSB0)
        # Consumption by propagation (PA + A -> PA, PA + B -> PB)
        - k.kpAA * s.A * sms.aSA0
        - k.kpAB * s.B * (s.RA + sms.aSA0)
        # Formation by depropagation (PAA -> PA + A, PAB -> PA + B)
        + k.kdAA * s.pAA * sms.aSA0
        + k.kdAB * s.pAB * sms.aSB0
        # Consumption by depropagation (PAA -> PA + A, PBA -> PB + A)
        - k.kdAA * s.pAA * sms.aSA0
        - k.kdBA * s.pBA * sms.aSA0
        # Consumption by termination (PA + PA -> D, PA + PB -> D)
        - RtAA_0
        - RtAB_0
    )

    """Active B sequences (0th order moment)"""
    dydt.aSB0 = (
        # Formation by propagation (PB + B -> PB, PA + B -> PB)
        +k.kpBB * s.B * (s.R + sms.aSB0)
        + k.kpAB * s.B * (s.RA + sms.aSA0)
        # Consumption by propagation (PB + B -> PB, PB + A -> PA)
        - k.kpBB * s.B * sms.aSB0
        - k.kpBA * s.A * (s.RB + sms.aSB0)
        # Formation by depropagation (PBB -> PB + B, PBA -> PB + A)
        + k.kdBB * s.pBB * sms.aSB0
        + k.kdBA * s.pBA * sms.aSA0
        # Consumption by depropagation (PBB -> PB + B, PAB -> PA + B)
        - k.kdBB * s.pBB * sms.aSB0
        - k.kdAB * s.pAB * sms.aSB0
        # Consumption by termination (PB + PB -> D, PB + PA -> D)
        - RtBB_0
        - RtBA_0
    )

    """Active A sequences (1st order moment)"""
    dydt.aSA1 = (
        # Formation by propagation (PA + A -> PA, PB + A -> PA)
        +k.kpAA * s.A * (s.R + sms.aSA0 + sms.aSA1)
        + k.kpBA * s.A * (s.RB + sms.aSB0)
        # Consumption by propagation (PA + A -> PA, PA + B -> PB)
        - k.kpAA * s.A * sms.aSA1
        - k.kpAB * s.B * (s.RA + sms.aSA1)
        # Formation by depropagation (PAA -> PA + A, PAB -> PA + B)
        + k.kdAA * s.pAA * (sms.aSA1 - sms.aSA0)
        + k.kdAB * s.pAB * a10_frac * sms.aSB0
        # Consumption by depropagation (PAA -> PA + A, PBA -> PB + A)
        - k.kdAA * s.pAA * sms.aSA1
        - k.kdBA * s.pBA * sms.aSA0
        # Consumption by termination (PA + PA -> D, PA + PB -> D)
        - RtAA_1
        - RtAB_1
    )

    """Active B sequences (1st order moment)"""
    dydt.aSB1 = (
        # Formation by propagation (PB + B -> PB, PA + B -> PB)
        +k.kpBB * s.B * (s.R + sms.aSB0 + sms.aSB1)
        + k.kpAB * s.B * (s.RA + sms.aSA0)
        # Consumption by propagation (PB + B -> PB, PB + A -> PA)
        - k.kpBB * s.B * sms.aSB1
        - k.kpBA * s.A * (s.RB + sms.aSB1)
        # Formation by depropagation (PBB -> PB + B, PBA -> PB + A)
        + k.kdBB * s.pBB * (sms.aSB1 - sms.aSB0)
        + k.kdBA * s.pBA * b10_frac * sms.aSA0
        # Consumption by depropagation (PBB -> PB + B, PAB -> PA + B)
        - k.kdBB * s.pBB * sms.aSB1
        - k.kdAB * s.pAB * sms.aSB0
        # Consumption by termination (PB + PB -> D, PB + PA -> D)
        - RtBB_1
        - RtBA_1
    )

    """Active A sequences (2nd order moment)"""
    dydt.aSA2 = (
        # Formation by propagation (PA + A -> PA, PB + A -> PA)
        +k.kpAA * s.A * (s.R + sms.aSA0 + 2 * sms.aSA1 + sms.aSA2)
        + k.kpBA * s.A * (s.RB + sms.aSB0)
        # Consumption by propagation (PA + A -> PA, PA + B -> PB)
        - k.kpAA * s.A * sms.aSA2
        - k.kpAB * s.B * (s.RA + sms.aSA2)
        # Formation by depropagation (PAA -> PA + A, PAB -> PA + B)
        + k.kdAA * s.pAA * (sms.aSA2 - 2 * sms.aSA1 + sms.aSA0)
        + k.kdAB * s.pAB * a20_frac * sms.aSB0
        # Consumption by depropagation (PAA -> PA + A, PBA -> PB + A)
        - k.kdAA * s.pAA * sms.aSA2
        - k.kdBA * s.pBA * sms.aSA0
        # Consumption by termination (PA + PA -> D, PA + PB -> D)
        - RtAA_2
        - RtAB_2
    )

    """Active B sequences (2nd order moment)"""
    dydt.aSB2 = (
        # Formation by propagation (PB + B -> PB, PA + B -> PB)
        +k.kpBB * s.B * (s.R + sms.aSB0 + 2 * sms.aSB1 + sms.aSB2)
        + k.kpAB * s.B * (s.RA + sms.aSA0)
        # Consumption by propagation (PB + B -> PB, PB + A -> PA)
        - k.kpBB * s.B * sms.aSB2
        - k.kpBA * s.A * (s.RB + sms.aSB2)
        # Formation by depropagation (PBB -> PB + B, PBA -> PB + A)
        + k.kdBB * s.pBB * (sms.aSB2 - 2 * sms.aSB1 + sms.aSB0)
        + k.kdBA * s.pBA * b20_frac * sms.aSA0
        # Consumption by depropagation (PBB -> PB + B, PAB -> PA + B)
        - k.kdBB * s.pBB * sms.aSB2
        - k.kdAB * s.pAB * sms.aSB0
        # Consumption by termination (PB + PB -> D, PB + PA -> D)
        - RtBB_2
        - RtBA_2
    )

    """Inactive A sequences (0th order moment)"""
    dydt.iSA0 = (
        # Formation by cross-propagation (PA + B -> PB)
        +k.kpAB * s.B * (s.RA + sms.aSA0)
        # Consumption by depropagation (PAB -> PA + B)
        - k.kdAB * s.pAB * sms.aSB0
        # Formation by termination (PA + PA -> D, PA + PB -> D)
        + RtAA_0
        + RtAB_0
    )

    """Inactive B sequences (0th order moment)"""
    dydt.iSB0 = (
        # Formation by cross-propagation (PB + A -> PA)
        +k.kpBA * s.A * (s.RB + sms.aSB0)
        # Consumption by depropagation (PBA -> PB + A)
        - k.kdBA * s.pBA * sms.aSA0
        # Formation by termination (PB + PB -> D, PB + PA -> D)
        + RtBB_0
        + RtBA_0
    )

    """Inactive A sequences (1st order moment)"""
    dydt.iSA1 = (
        # Formation by cross-propagation (PA + B -> PB)
        +k.kpAB * s.B * (s.RA + sms.aSA1)
        # Consumption by depropagation (PAB -> PA + B)
        - k.kdAB * s.pAB * a10_frac * sms.aSB0
        # Formation by termination (PA + PA -> D, PA + PB -> D)
        + RtAA_1
        + RtAB_1
    )

    """Inactive B sequences (1st order moment)"""
    dydt.iSB1 = (
        # Formation by cross-propagation (PB + A -> PA)
        +k.kpBA * s.A * (s.RB + sms.aSB1)
        # Consumption by depropagation (PBA -> PB + A)
        - k.kdBA * s.pBA * b10_frac * sms.aSA0
        # Formation by termination (PB + PB -> D, PB + PA -> D)
        + RtBB_1
        + RtBA_1
    )

    """Inactive A sequences (2nd order moment)"""
    dydt.iSA2 = (
        # Formation by cross-propagation (PA + B -> PB)
        +k.kpAB * s.B * (s.RA + sms.aSA2)
        # Consumption by depropagation (PAB -> PA + B)
        - k.kdAB * s.pAB * a20_frac * sms.aSB0
        # Formation by termination (PA + PA -> D, PA + PB -> D)
        + RtAA_2
        + RtAB_2
    )

    """Inactive B sequences (2nd order moment)"""
    dydt.iSB2 = (
        # Formation by cross-propagation (PB + A -> PA)
        +k.kpBA * s.A * (s.RB + sms.aSB2)
        # Consumption by depropagation (PBA -> PB + A)
        - k.kdBA * s.pBA * b20_frac * sms.aSA0
        # Formation by termination (PB + PB -> D, PB + PA -> D)
        + RtBB_2
        + RtBA_2
    )

    return dydt
