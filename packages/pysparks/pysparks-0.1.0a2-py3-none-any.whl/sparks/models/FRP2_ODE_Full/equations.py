from dataclasses import dataclass

import numpy as np

from sparks.core import NDArrayType
from sparks.utils import okprint, errprint, warnprint
from sparks.data import MonomerType

from .model import RateCoefficients, ModelState, SequenceModelState


def get_kt_from_Cheong_2003(s: ModelState, k: RateCoefficients):

    T_C = k.T_C
    if T_C == 115:
        ka = 0.23e14  # L/mol/min
    elif T_C == 140:
        ka = 0.8e14  # L/mol/min
    else:
        raise ValueError(f"Unsupported temperature: {T_C} C")

    ktBB = k.mpropsB.kt
    ktAA = (np.sqrt(ka) - s.beta * np.sqrt(ktBB)) ** 2
    ktAB = np.sqrt(ktAA * ktBB)

    return ktAA, ktAB, ktBB


@dataclass
class Context:

    # Parameters
    use_diffusion_control: bool = False
    const_volume: bool = False
    const_temperature: bool = True

    # Initial state
    init_state: ModelState | None = None

    # Gel Effect
    triggered: bool = False
    t_event: NDArrayType | None = None
    Vf_cr1: float | None = None
    kt_cr: float | None = None
    Mw_cr: float | None = None

    debug_counter: int = 0
    debug_interval: int = 100

    # times = [10, 20, 30, 40, 50, 60, 70, 80, 90]
    times = [100, 200, 300, 400, 500, 600, 700, 800, 900]
    # times = []
    time_idx: int = 0


def kinetic_odes(
    dydt: ModelState,
    k: RateCoefficients,
    t: NDArrayType,
    s: ModelState,
    context: Context = Context(),
) -> ModelState:
    """Defines the ODEs for the full FRP2 model."""

    dydt.t = t

    T_C = k.T_C
    T_K = T_C + 273.15  # Convert Celsius to Kelvin

    # Extract properties
    iprops = k.iprops
    mpropsA = k.mpropsA
    mpropsB = k.mpropsB

    # Save initial state
    if not context.init_state and t >= 0:
        context.init_state = s

    # A0, B0 are initial moles for volume balance calculations
    A0 = context.init_state.A
    B0 = context.init_state.B
    M0 = A0 + B0

    ######################
    ### Rate Constants ###
    ######################

    kpAA, kpAB, kpBA, kpBB = k.kp()
    kpRAA, kpRAB, kpRBA, kpRBB = k.kp(f=1e1)
    kdAA, kdAB, kdBA, kdBB = k.kd()

    # Initiation
    kd = iprops.kd[MonomerType.General]
    f = iprops.f[MonomerType.General]

    # Thermal Initiation
    kthA = mpropsA.kth
    kthB = mpropsB.kth

    # Chain Transfer to Monomer
    kf_mAA, kf_mAB, kf_mBA, kf_mBB = k.kfm()
    kfm = kfm_pseudo = (
        kf_mAA * s.pA * s.fA
        + kf_mAB * s.pA * s.fB
        + kf_mBA * s.pB * s.fA
        + kf_mBB * s.pB * s.fB
    )

    kf_mAA = 0
    kf_mBB = 0
    kf_mAB = 0
    kf_mBA = 0

    RpA = (
        s.A_conc
        * (
            kpRAA * (s.R_conc + s.RA_conc)
            + kpRBA * s.RB_conc
            + kpAA * s.PA_conc
            + kpBA * s.PB_conc
        )
        - s.PA_conc * (kdAA * s.pAA + kdBA * s.pBA)
        + s.A_conc * (kf_mAA * s.PA_conc + kf_mBA * s.PB_conc)
        + 2 * kthA * s.A_conc**3
    )
    RpB = (
        s.B_conc
        * (
            kpRBB * (s.R_conc + s.RB_conc)
            + kpRAB * s.RA_conc
            + kpBB * s.PB_conc
            + kpAB * s.PA_conc
        )
        - s.PB_conc * (kdBB * s.pBB + kdAB * s.pAB)
        + s.B_conc * (kf_mAB * s.PA_conc + kf_mBB * s.PB_conc)
        + 2 * kthB * s.B_conc**3
    )
    Rp = RpA + RpB

    # Calculate composition of the polymer
    F_A = RpA / Rp if Rp > 0 else 0.0
    F_B = RpB / Rp if Rp > 0 else 0.0

    ###########################################
    ### Calculate the pseudo rate constants ###
    ###########################################

    # Pseudo rate constant for propagation
    # Mistake in Eq. 52? kdij * Pij * pi / M_conc
    # Should be kdij * Pij * pj / M_conc
    kp = kp_pseudo = (
        # i=A, j=A
        (kpAA * s.pA * s.fA - kdAA * s.pAA * s.pA / s.M_conc)
        # i=A, j=B
        + (kpAB * s.pA * s.fB - kdAB * s.pAB * s.pB / s.M_conc)
        # i=B, j=A
        + (kpBA * s.pB * s.fA - kdBA * s.pBA * s.pA / s.M_conc)
        # i=B, j=B
        + (kpBB * s.pB * s.fB - kdBB * s.pBB * s.pB / s.M_conc)
    )

    ktAA, ktAB, ktBB = get_kt_from_Cheong_2003(s, k)
    kt = kt_pseduo = ktAA * s.pA * s.pA + ktBB * s.pB * s.pB + 2 * ktAB * s.pA * s.pB
    ktd_ratio = mpropsA.ktd_ratio * s.pA + mpropsB.ktd_ratio * s.pB

    # Transfer to impurity, solvent, CTA, or polymer not implemented
    kfz = 0
    kfs = 0
    kfCTA = 0
    kfp = 0

    ########################################
    ### Calculate the overall properties ###
    ########################################

    # Effective molecular weight of monomer/polymer
    MW_eff = s.FbarA * mpropsA.MW + s.FbarB * mpropsB.MW

    # Calculate the mass/volume of monomer
    m_A = s.A * mpropsA.MW
    m_B = s.B * mpropsB.MW
    vol_A = m_A / mpropsA.dens_m
    vol_B = m_B / mpropsB.dens_m
    vol_m = vol_A + vol_B

    # Calculate the mass/volume of polymer
    m_PA = s.nPA * mpropsA.MW
    m_PB = s.nPB * mpropsB.MW
    m_P = m_PA + m_PB
    vol_PA = m_PA / mpropsA.dens_p
    vol_PB = m_PB / mpropsB.dens_p
    vol_P = vol_PA + vol_PB  # Volume of polymer in L

    kt_factor = 1
    kp_factor = 1
    kfm_factor = 1

    if context.use_diffusion_control:

        Mn = MW_eff * s.NACL
        Mw = MW_eff * s.WACL

        Vf_p = mpropsA.Vf_p
        alpha_mP = mpropsA.alpha_p

        wA = m_PA / m_P if m_P > 0 else 0
        wB = m_PB / m_P if m_P > 0 else 0
        Tg_P = 1 / (wA / mpropsA.Tg_p + wB / mpropsB.Tg_p) if m_P > 0 else 0

        # Calculate the free volume
        Vf_A = (mpropsA.Vf_m + mpropsA.alpha_m * (T_K - mpropsA.Tg_m)) * vol_A / s.V
        Vf_B = (mpropsB.Vf_m + mpropsB.alpha_m * (T_K - mpropsB.Tg_m)) * vol_B / s.V
        Vf_P = (Vf_p + alpha_mP * (T_K - Tg_P)) * vol_P / s.V
        Vf = Vf_A + Vf_B + Vf_P

        delta_c = mpropsA.delta * s.pA + mpropsB.delta * s.pB

        K3 = K3_pseudo = np.exp(
            1 / (s.FbarA / np.log(mpropsA.K3) + s.FbarB / np.log(mpropsB.K3))
        )

        A_factor = A_pseudo = (
            1 / (F_A / mpropsA.A + F_B / mpropsB.A) if (F_A + F_B) > 0 else 0
        )
        m = np.where((s.pA + s.pB) > 0, mpropsA.m * s.pA + mpropsB.m * s.pB, 1)
        n = np.where((s.pA + s.pB) > 0, mpropsA.n * s.pA + mpropsB.n * s.pB, 1)

        if not context.triggered:
            # 1) Segmental diffusion termination

            c = m_P / s.V  # Mass concentration of accumulated polymer (g/L)
            # kt = kt * (1 + delta_c * c)

            K3_test = (Mw**m) * np.exp(A_factor / Vf)
            # print(
            #     f"K3_test={K3_test:.2f}, K3={K3:.2f}, K3_A={mpropsA.K3:.2f}, K3_B={mpropsB.K3:.2f}"
            # )
            # warnprint(K3_test)
            # warnprint(K3)
            # warnprint(f"Mw={Mw:.3e} g/mol")
            if not np.isclose(K3, 0) and K3_test >= K3 and t >= 1:
                context.triggered = True
                context.t_event = t
                context.Vf_cr1 = Vf * 1.0
                context.kt_cr = kt
                context.Mw_cr = Mw

                warnprint(
                    f"K3 triggered at t={t:.2f} s: K3_test={K3_test:.3e}, K3={K3:.3e}"
                )
                warnprint(
                    f"A (A factor): {mpropsA.A}, B (A factor): {mpropsB.A}, A_factor: {A_factor}"
                )
                warnprint(f"A (K3): {mpropsA.K3}, B (K3): {mpropsB.K3}, K3: {K3}")
                warnprint(
                    f"F_A: {F_A}, F_B: {F_B}, Fbar_A: {s.FbarA}, Fbar_B: {s.FbarB}"
                )
                warnprint(
                    f"Triggered at t={t:.2f} s, Vf={Vf:.2f} L, Mw={Mw/1e3:.2f} kDa"
                )
        else:

            kt_factor = (context.Mw_cr / Mw) ** n * np.exp(
                -A_factor * (1 / Vf - 1 / context.Vf_cr1)
            )

        # 2) Translational diffusion termination
        Vf_cr2 = mpropsA.Vf_c * s.pA + mpropsB.Vf_c * s.pB
        B_factor = mpropsA.B * s.pA + mpropsB.B * s.pB
        if Vf < Vf_cr2:
            kp_factor = kfm_factor = np.exp(-B_factor * (1 / Vf - 1 / Vf_cr2))
            # kp = kp * np.exp(-B_factor * (1 / Vf - 1 / Vf_cr2))
            # kfm = kfm * np.exp(-B_factor * (1 / Vf - 1 / Vf_cr2))

        Vf_i = iprops.Vf_i[MonomerType.General]
        C_factor = iprops.C[MonomerType.General]
        if Vf < Vf_i:
            f = f * np.exp(-C_factor * (1 / Vf - 1 / Vf_i))

        # 3) Reaction diffusion termination
        # D = (
        #     mprops.n_s * (mprops.l0) ** 2 * kp * M_conc / 6.0
        # )  # Diffusion coefficient (m^2/s)
        # delta = (6 * (vol_m / nM) / (np.pi * NA)) ** (1 / 3.0)
        # # delta = mprops.delta
        # kt_rd = 8 * np.pi * NA * delta * D / 1000
        # kt += 0.0 * kt_rd

    ktAA *= kt_factor
    ktBB *= kt_factor
    ktAB *= kt_factor
    kt *= kt_factor

    kpAA, kpAB, kpBA, kpBB = k.kp(f=kp_factor)
    kdAA, kdAB, kdBA, kdBB = k.kd(f=kp_factor)
    kp *= kp_factor

    kf_mAA, kf_mAB, kf_mBA, kf_mBB = k.kfm(f=kfm_factor)
    kfm_pseudo *= kfm_factor

    ktc = kt / (1 + ktd_ratio)
    ktd = kt * ktd_ratio / (1 + ktd_ratio)
    # ktc = kt
    # ktd = 0
    # ktc = 0
    # ktd = kt

    Ri = 2 * f * kd * s.I_conc + 2 * kthA * s.A_conc**3 + 2 * kthB * s.B_conc**3

    # Rates of Propagation of A and B
    RpA = (
        s.A_conc
        * (
            kpRAA * (s.R_conc + s.RA_conc)
            + kpRBA * s.RB_conc
            + kpAA * s.PA_conc
            + kpBA * s.PB_conc
        )
        - s.PA_conc * (kdAA * s.pAA + kdBA * s.pBA)
        + s.A_conc * (kf_mAA * s.PA_conc + kf_mBA * s.PB_conc)
        + 2 * kthA * s.A_conc**3
    )
    RpB = (
        s.B_conc
        * (
            kpRBB * (s.R_conc + s.RB_conc)
            + kpRAB * s.RA_conc
            + kpBB * s.PB_conc
            + kpAB * s.PA_conc
        )
        - s.PB_conc * (kdBB * s.pBB + kdAB * s.pAB)
        + s.B_conc * (kf_mAB * s.PA_conc + kf_mBB * s.PB_conc)
        + 2 * kthB * s.B_conc**3
    )
    Rp = RpA + RpB

    # Calculate volume change from monomer
    vdelta_mA = RpA * vol_A / s.A if s.A > 0 else 0.0
    vdelta_mB = RpB * vol_B / s.B if s.B > 0 else 0.0
    vdelta_PA = RpA * vol_PA / s.nPA if s.nPA > 0 else 0.0
    vdelta_PB = RpB * vol_PB / s.nPB if s.nPB > 0 else 0.0
    vdelta = vdelta_mA + vdelta_mB - vdelta_PA - vdelta_PB

    if context.const_volume:
        dydt.V = 0 * s.V
    else:
        dydt.V = -s.V * vdelta

    """ Moles of Initiator """
    dydt.I = s.V * (-kd * s.I_conc)

    """ Moles of Free Radical, R """
    dydt.R = s.V * (
        # Formation by initiation
        +2 * f * kd * s.I_conc
        # Consumption by propagation
        - kpRAA * s.R_conc * s.A_conc
        - kpRBB * s.R_conc * s.B_conc
    )

    """ Moles of A Monomer """
    dydt.A = s.V * (
        # Consumption by propagation
        -kpRAA * (s.R_conc + s.RA_conc) * s.A_conc
        - kpRBA * s.RB_conc * s.A_conc
        - kpAA * s.PA_conc * s.A_conc
        - kpBA * s.PB_conc * s.A_conc
        # Formation by depropagation
        + kdAA * s.PAA_conc
        + kdBA * s.PBA_conc
        # Consumption by chain transfer to monomer
        - kf_mAA * s.PA_conc * s.A_conc
        - kf_mBA * s.PB_conc * s.A_conc
        # Consumption by thermal initiation
        - 3 * kthA * s.A_conc**3
    )

    """ Moles of B Monomer """
    dydt.B = s.V * (
        # Consumption by propagation
        -kpRBB * (s.R_conc + s.RB_conc) * s.B_conc
        - kpRAB * s.RA_conc * s.B_conc
        - kpAB * s.PA_conc * s.B_conc
        - kpBB * s.PB_conc * s.B_conc
        # Formation by depropagation
        + kdAB * s.PAB_conc
        + kdBB * s.PBB_conc
        # Consumption by chain transfer to monomer
        - kf_mAB * s.PA_conc * s.B_conc
        - kf_mBB * s.PB_conc * s.B_conc
        # Consumption by thermal initiation
        - 3 * kthB * s.B_conc**3
    )

    """ Moles of R-A dyad"""
    dydt.RA = s.V * (
        # Formation by thermal initiation (3A -> 2RA)
        +2 * kthA * s.A_conc**3
        # Formation by propagation (R + A -> RA)
        + kpRAA * s.R_conc * s.A_conc
        # Consumption by propagation (RA + A -> PAA, RA + B -> PAB)
        - kpRAA * s.RA_conc * s.A_conc
        - kpRAB * s.RA_conc * s.B_conc
        # Formation by chain transfer (PA + A -> PD + RA)
        + kf_mAA * s.PA_conc * s.A_conc
        # Formation by chain transfer (PB + A -> PD + RA)
        + kf_mBA * s.PB_conc * s.A_conc
    )

    """ Total moles of R-B dyad """
    dydt.RB = s.V * (
        # Formation by thermal initiation (3B -> 2RB)
        +2 * kthB * s.B_conc**3
        # Formation by propagation (R + B -> RB)
        + kpRBB * s.R_conc * s.B_conc
        # Consumption by propagation (RB + A -> PBA, RB + B -> PBB)
        - kpRBA * s.RB_conc * s.A_conc
        - kpRBB * s.RB_conc * s.B_conc
        # Formation by chain transfer (PA + B -> PD + RB)
        + kf_mAB * s.PA_conc * s.B_conc
        # Formation by chain transfer (PB + B -> PD + RB)
        + kf_mBB * s.PB_conc * s.B_conc
    )

    c_tAA = c_tBB = 1
    c_tAB = 1

    """ Total moles of ~~AA* polymer """
    dydt.PAA = s.V * (
        # Formation by propagation (RA + A -> PAA)
        +kpRAA * s.RA_conc * s.A_conc
        # Formation by propagation (PBA + A -> PAA)
        + kpAA * s.PBA_conc * s.A_conc
        # Consumption by propagation (PAA + B -> PAB)
        - kpAB * s.PAA_conc * s.B_conc
        # Formation by depropagation (PAAB -> PAA + B)
        + kdAB * s.pAA * s.PAB_conc
        # Consumption by depropagation (PBAA -> PBA + A)
        - kdAA * s.pBA * s.PAA_conc
        # Consumption by chain transfer to monomer (PAA + B -tr-> PD + RB)
        - kf_mAB * s.PAA_conc * s.B_conc
        # Consumption by chain transfer to monomer (PAA + A -tr-> PD + RA)
        - kf_mAA * s.PAA_conc * s.A_conc
        # Consumption by termination (PAA + PA -> (2)PD, PAA + PB -> (2)PD)
        - c_tAA * ktAA * s.PAA_conc * s.PA_conc
        - c_tAB * ktAB * s.PAA_conc * s.PB_conc
    )

    """ Total moles of ~~AB* polymer """
    dydt.PAB = s.V * (
        # Formation by propagation (RA + B -> PAB)
        +kpRAB * s.RA_conc * s.B_conc
        # Formation by propagation (PA + B -> PAB)
        + kpAB * s.PA_conc * s.B_conc
        # Consumption by propagation (PAB + A -> PBA)
        - kpBA * s.PAB_conc * s.A_conc
        # Consumption by propagation (PAB + B -> PBB)
        - kpBB * s.PAB_conc * s.B_conc
        # Formation by depropagation (PABA -> PAB + A)
        + kdBA * s.pAB * s.PBA_conc
        # Formation by depropagation (PABB -> PAB + B)
        + kdBB * s.pAB * s.PBB_conc
        # Consumption by depropagation (PAB -> PA + B)
        - kdAB * s.PAB_conc
        # Consumption by chain transfer to monomer (PAB + A -tr-> PD + RA)
        - kf_mBA * s.PAB_conc * s.A_conc
        # Consumption by chain transfer to monomer (PAB + B -tr-> PD + RB)
        - kf_mBB * s.PAB_conc * s.B_conc
        # Consumption by termination (PAB + PA -> (2)PD, PAB + PB -> (2)PD)
        - c_tAB * ktAB * s.PAB_conc * s.PA_conc
        - c_tBB * ktBB * s.PAB_conc * s.PB_conc
    )

    """ Total moles of ~~BA* polymer """
    dydt.PBA = s.V * (
        # Formation by propagation (RB + A -> PBA)
        +kpRBA * s.RB_conc * s.A_conc
        # Formation by propagation (PB + A -> PBA)
        + kpBA * s.PB_conc * s.A_conc
        # Consumption by propagation (PBA + A -> PAA)
        - kpAA * s.PBA_conc * s.A_conc
        # Consumption by propagation (PBA + B -> PBB)
        - kpAB * s.PBA_conc * s.B_conc
        # Formation by depropagation (PBAA -> PBA + A)
        + kdAA * s.pBA * s.PAA_conc
        # Formation by depropagation (PBAB -> PBA + B)
        + kdAB * s.pBA * s.PAB_conc
        # Consumption by depropagation (PBA -> PB + A)
        - kdBA * s.PBA_conc
        # Consumption by chain transfer to monomer (PBA + A -tr-> PD + RA)
        - kf_mAA * s.PBA_conc * s.A_conc
        # Consumption by chain transfer to monomer (PBA + B -tr-> PD + RB)
        - kf_mAB * s.PBA_conc * s.B_conc
        # Consumption by termination (PBA + PA -> (2)PD, PBA + PB -> (2)PD)
        - c_tAA * ktAA * s.PBA_conc * s.PA_conc
        - c_tAB * ktAB * s.PBA_conc * s.PB_conc
    )

    """ Total moles of ~~BB* polymer """
    dydt.PBB = s.V * (
        # Formation by propagation (RB + B -> PBB)
        +kpRBB * s.RB_conc * s.B_conc
        # Formation by propagation (PAB + B -> PBB)
        + kpBB * s.PAB_conc * s.B_conc
        # Consumption by propagation (PBB + A -> PBA)
        - kpBA * s.PBB_conc * s.A_conc
        # Formation by depropagation (PBBA -> PBB + A)
        + kdBA * s.pBB * s.PBA_conc
        # Consumption by depropagation (PABB -> PAB + B)
        - kdBB * s.pAB * s.PBB_conc
        # Consumption by chain transfer to monomer (PBB + A -tr-> PD + RA)
        - kf_mBA * s.PBB_conc * s.A_conc
        # Consumption by chain transfer to monomer (PBB + B -tr-> PD + RB)
        - kf_mBB * s.PBB_conc * s.B_conc
        # Consumption by termination (PBB + PA -> (2)PD, PBB + PB -> (2)PD)
        - c_tBB * ktBB * s.PBB_conc * s.PB_conc
        - c_tAB * ktAB * s.PBB_conc * s.PA_conc
    )

    """ Total moles of A and B monomer in polymer"""
    dydt.nPA = s.V * RpA
    dydt.nPB = s.V * RpB

    # Formation of polymer from active radicals
    poly_form = (
        kpRAA * s.R_conc * s.A_conc
        + kpRBB * s.R_conc * s.B_conc
        + 2 * kthA * s.A_conc**3
        + 2 * kthB * s.B_conc**3
    )

    mu_3_conc = np.where(
        (s.mu_0_conc * s.mu_1_conc) > 0,
        s.mu_2_conc
        / (s.mu_0_conc * s.mu_1_conc)
        * (2 * s.mu_0_conc * s.mu_2_conc - s.mu_2_conc),
        0,
    )  # Could be misprint (potentially s.mu_1^2)

    """ Active radicals (0th order moment) """
    dydt.lam_0 = s.V * (
        # Formation by propagation
        poly_form
        # Consumption by termination
        - kt * s.lam_0_conc**2
        # Consumption from impurity
        - kfz * s.lam_0_conc * s.Z_conc
    )

    """ Active radicals (1st order moment) """
    dydt.lam_1 = s.V * (
        # Formation by propagation
        poly_form
        # Formation by propagation
        + kp * s.M_conc * s.lam_0_conc
        # Consumption by termination
        - kt * s.lam_0_conc * s.lam_1_conc
        # Consumption from chain transfer
        - (kfCTA * s.CTA_conc + kfm * s.M_conc + kfs * s.S_conc)
        * (s.lam_1_conc - s.lam_0_conc)
        # Formation by chain transfer to polymer
        + kfp * (s.lam_0_conc * mu_3_conc - s.lam_1_conc * s.mu_1_conc)
        # Consumption by chain transfer to impurity
        - kfz * s.lam_1_conc * s.Z_conc
    )

    """Active radicals (2nd order moment)"""
    dydt.lam_2 = s.V * (
        # Formation by propagation
        poly_form
        # Formation by propagation
        + kp * s.M_conc * (s.lam_0_conc + 2 * s.lam_1_conc)
        # Consumption by termination
        - kt * s.lam_0_conc * s.lam_2_conc
        # Consumption from chain transfer
        - (kfCTA * s.CTA_conc + kfm * s.M_conc + kfs * s.S_conc)
        * (s.lam_2_conc - s.lam_0_conc)
        # Formation by chain transfer to polymer
        + kfp * (s.lam_0_conc * mu_3_conc - s.lam_2_conc * s.mu_1_conc)
        # Consumption by chain transfer to impurity
        - kfz * s.lam_2_conc * s.Z_conc
    )

    """Dead radicals (0th order moment)"""
    dydt.mu_0 = s.V * (
        # Formation by termination
        +(0.5 * ktc + ktd) * s.lam_0_conc**2
        # Formation by chain transfer
        + (kfm * s.M_conc + kfCTA * s.CTA_conc + kfs * s.S_conc + kfz * s.Z_conc)
        * s.lam_0_conc
    )

    """Dead radicals (1st order moment)"""
    dydt.mu_1 = s.V * (
        # Formation by termination
        +(ktc + ktd) * s.lam_0_conc * s.lam_1_conc
        # Formation by chain transfer
        + (kfm * s.M_conc + kfCTA * s.CTA_conc + kfs * s.S_conc + kfz * s.Z_conc)
        * s.lam_1_conc
        # Chain transfer to polymer
        + kfp * (s.lam_1_conc * s.mu_1_conc - s.lam_0_conc * s.mu_2_conc)
    )

    """Dead radicals (2nd order moment)"""
    dydt.mu_2 = s.V * (
        # Formation by termination (comb.)
        +ktc * (s.lam_0_conc * s.lam_2_conc + s.lam_1_conc**2)
        # Formation by termination (disp.)
        + ktd * s.lam_0_conc * s.lam_2_conc
        # Formation by chain transfer
        + (kfm * s.M_conc + kfCTA * s.CTA_conc + kfs * s.S_conc + kfz * s.Z_conc)
        * s.lam_2_conc
        # Chain transfer to polymer
        + kfp * (s.lam_2_conc * s.mu_1_conc - s.lam_0_conc * mu_3_conc)
    )

    vol_error = np.where(s.V > 0, 100 * abs((vol_m + vol_P - s.V) / s.V), 0)
    mole_error = np.where(M0 > 0, 100 * abs((s.A + s.B + s.nPA + s.nPB - M0) / M0), 0)

    dRtotdt = dydt.R + dydt.RA + dydt.RB + dydt.PAA + dydt.PAB + dydt.PBA + dydt.PBB
    dRtotdt_ = s.V * (Ri - kt * s.P_conc**2)
    dRtotdt_error = np.where(dRtotdt > 0, 100 * abs((dRtotdt - dRtotdt_) / dRtotdt), 0)

    lam_0_error = np.where(
        s.lam_0_conc > 0, 100 * abs((s.lam_0_conc - s.P_conc) / s.lam_0_conc), 0
    )

    time = np.inf
    if context.time_idx < len(context.times):
        time = context.times[context.time_idx]

    if t >= time:
        # if True:
        context.time_idx += 1
        vol_error = 100 * abs((vol_m + vol_P - s.V) / s.V)
        print(f"Step {context.time_idx}: t={t:.2f}")

        print(f"Time: {t:.2f}, Volume: {s.V:.3e} L")
        print(f"kd: {kd:.3e}, kp: {kp:.3e}, kt: {kt:.3e}, kfm: {kfm:.3e}")
        print(
            f"kfm_factor: {kfm_factor:.3e}, kp_factor: {kp_factor:.3e}, kt_factor: {kt_factor:.3e}"
        )
        print(
            f"pA: {s.pA:.3f}, pB: {s.pB:.3f}, pAA: {s.pAA:.3f}, pAB: {s.pAB:.3f}, pBA: {s.pBA:.3f}, pBB: {s.pBB:.3f}"
        )
        print(f"A_conc: {s.A_conc:.3e}, B_conc: {s.B_conc:.3e} ")

        mole_error_str = f"\tMole balance error: {mole_error:.3e}% (moles = {M0:.3e})"
        if mole_error > 1.0:
            errprint(mole_error_str)
        else:
            okprint(mole_error_str)

        vol_error_str = f"\tVolume balance error: {vol_error:.3e}% (vol = {s.V:.3e} L)"
        if vol_error > 1.0:
            errprint(vol_error_str)
        else:
            okprint(vol_error_str)

        dRtotdt_error_str = f"\tRadical balance error: {dRtotdt_error:.3e}%"
        if dRtotdt_error > 1.0:
            errprint(dRtotdt_error_str)
            errprint(f"\t\tCalculated dRtotdt: {dRtotdt:.3e}, Expected: {dRtotdt_:.3e}")
        else:
            okprint(dRtotdt_error_str)

        lam_0_error_str = f"\tlam_0 error: {lam_0_error:.3e}%"
        if lam_0_error > 1.0:
            errprint(lam_0_error_str)
            errprint(
                f"\t\tCalculated lam_0: {s.lam_0_conc:.3e}, Expected: {s.P_conc:.3e}"
            )
        else:
            okprint(lam_0_error_str)

        print(f"\tActive NACL: {s.active_NACL:.2f}")
        print(f"\tInactive NACL: {s.NACL:.2f}")
        print(f"\t mu0: {s.mu_0:.3e} mu1: {s.mu_1:.3e} mu2: {s.mu_2:.3e}")
        print()

    return dydt


def sequence_odes(
    dydt: SequenceModelState,
    k: RateCoefficients,
    t: NDArrayType,
    sms: SequenceModelState,
    s: ModelState,
) -> SequenceModelState:

    dydt.t = t

    kpAA, kpAB, kpBA, kpBB = k.kp()
    kdAA, kdAB, kdBA, kdBB = k.kd()
    ktAA, ktAB, ktBB = get_kt_from_Cheong_2003(s, k)

    c_tAA = c_tBB = 1
    c_tAB = 1

    kf_mAA, kf_mAB, kf_mBA, kf_mBB = k.kfm()

    aSA0_conc = sms.aSA0 / s.V
    aSB0_conc = sms.aSB0 / s.V
    aSA1_conc = sms.aSA1 / s.V
    aSB1_conc = sms.aSB1 / s.V
    aSA2_conc = sms.aSA2 / s.V
    aSB2_conc = sms.aSB2 / s.V

    # print(f"aSA0_conc: {aSA0_conc:.3e}, aSB0_conc: {aSB0_conc:.3e}")
    # print(f"aSA1_conc: {aSA1_conc:.3e}, aSB1_conc: {aSB1_conc:.3e}")
    # print(f"aSA2_conc: {aSA2_conc:.3e}, aSB2_conc: {aSB2_conc:.3e}")

    # Rates of termination and chain transfer to monomer
    # Ctrij_x = c_tij * ktij * sms.aSijx * sms.aSij0 + c_tij * kf_mij * sms.aSijx * s.j
    RtAA_0 = ktAA * aSA0_conc * aSA0_conc + 0 * kf_mAA * aSA0_conc * s.A_conc
    RtAB_0 = ktAB * aSA0_conc * aSB0_conc + 0 * kf_mAB * aSA0_conc * s.B_conc
    RtBA_0 = ktAB * aSB0_conc * aSA0_conc + 0 * kf_mBA * aSB0_conc * s.A_conc
    RtBB_0 = ktBB * aSB0_conc * aSB0_conc + 0 * kf_mBB * aSB0_conc * s.B_conc
    RtAA_1 = ktAA * aSA1_conc * aSA0_conc + 0 * kf_mAA * aSA1_conc * s.A_conc
    RtAB_1 = ktAB * aSA1_conc * aSB0_conc + 0 * kf_mAB * aSA1_conc * s.B_conc
    RtBA_1 = ktAB * aSB1_conc * aSA0_conc + 0 * kf_mBA * aSB1_conc * s.A_conc
    RtBB_1 = ktBB * aSB1_conc * aSB0_conc + 0 * kf_mBB * aSB1_conc * s.B_conc
    RtAA_2 = ktAA * aSA2_conc * aSA0_conc + 0 * kf_mAA * aSA2_conc * s.A_conc
    RtAB_2 = ktAB * aSA2_conc * aSB0_conc + 0 * kf_mAB * aSA2_conc * s.B_conc
    RtBA_2 = ktAB * aSB2_conc * aSA0_conc + 0 * kf_mBA * aSB2_conc * s.A_conc
    RtBB_2 = ktBB * aSB2_conc * aSB0_conc + 0 * kf_mBB * aSB2_conc * s.B_conc

    a10_frac = aSA1_conc / aSA0_conc if aSA0_conc > 0 else 0
    b10_frac = aSB1_conc / aSB0_conc if aSB0_conc > 0 else 0
    a20_frac = aSA2_conc / aSA0_conc if aSA0_conc > 0 else 0
    b20_frac = aSB2_conc / aSB0_conc if aSB0_conc > 0 else 0

    # Active A sequences (0th order moment)
    dydt.aSA0 = s.V * (
        # Formation by propagation (PA + A -> PA, PB + A -> PA)
        +kpAA * s.A_conc * (s.R_conc + aSA0_conc)
        + kpBA * s.A_conc * (s.RB_conc + aSB0_conc)
        # Consumption by propagation (PA + A -> PA, PA + B -> PB)
        - kpAA * s.A_conc * aSA0_conc
        - kpAB * s.B_conc * (s.RA_conc + aSA0_conc)
        # Formation by depropagation (PAA -> PA + A, PAB -> PA + B)
        + kdAA * s.pAA * aSA0_conc
        + kdAB * s.pAB * aSB0_conc
        # Consumption by depropagation (PAA -> PA + A, PBA -> PB + A)
        - kdAA * s.pAA * aSA0_conc
        - kdBA * s.pBA * aSA0_conc
        # Consumption by termination (PA + PA -> D, PA + PB -> D)
        - RtAA_0
        - RtAB_0
    )

    # Active B sequences (0th order moment)
    dydt.aSB0 = s.V * (
        # Formation by propagation (PB + B -> PB, PA + B -> PB)
        +kpBB * s.B_conc * (s.R_conc + aSB0_conc)
        + kpAB * s.B_conc * (s.RA_conc + aSA0_conc)
        # Consumption by propagation (PB + B -> PB, PB + A -> PA)
        - kpBB * s.B_conc * aSB0_conc
        - kpBA * s.A_conc * (s.RB_conc + aSB0_conc)
        # Formation by depropagation (PBB -> PB + B, PBA -> PB + A)
        + kdBB * s.pBB * aSB0_conc
        + kdBA * s.pBA * aSA0_conc
        # Consumption by depropagation (PBB -> PB + B, PAB -> PA + B)
        - kdBB * s.pBB * aSB0_conc
        - kdAB * s.pAB * aSB0_conc
        # Consumption by termination (PB + PB -> D, PB + PA -> D)
        - RtBB_0
        - RtBA_0
    )

    # Active A sequences (1st order moment)
    dydt.aSA1 = s.V * (
        # Formation by propagation (PA + A -> PA, PB + A -> PA)
        +kpAA * s.A_conc * (s.R_conc + aSA0_conc + aSA1_conc)
        + kpBA * s.A_conc * (s.RB_conc + aSB0_conc)
        # Consumption by propagation (PA + A -> PA, PA + B -> PB)
        - kpAA * s.A_conc * aSA1_conc
        - kpAB * s.B_conc * (s.RA_conc + aSA1_conc)
        # Formation by depropagation (PAA -> PA + A, PAB -> PA + B)
        + kdAA * s.pAA * (aSA1_conc - aSA0_conc)
        + kdAB * s.pAB * a10_frac * aSB0_conc
        # Consumption by depropagation (PAA -> PA + A, PBA -> PB + A)
        - kdAA * s.pAA * aSA1_conc
        - kdBA * s.pBA * aSA0_conc
        # Consumption by termination (PA + PA -> D, PA + PB -> D)
        - RtAA_1
        - RtAB_1
    )

    # Active B sequences (1st order moment)
    dydt.aSB1 = s.V * (
        # Formation by propagation (PB + B -> PB, PA + B -> PB)
        +kpBB * s.B_conc * (s.R_conc + aSB0_conc + aSB1_conc)
        + kpAB * s.B_conc * (s.RA_conc + aSA0_conc)
        # Consumption by propagation (PB + B -> PB, PB + A -> PA)
        - kpBB * s.B_conc * aSB1_conc
        - kpBA * s.A_conc * (s.RB_conc + aSB1_conc)
        # Formation by depropagation (PBB -> PB + B, PBA -> PB + A)
        + kdBB * s.pBB * (aSB1_conc - aSB0_conc)
        + kdBA * s.pBA * b10_frac * aSA0_conc
        # Consumption by depropagation (PBB -> PB + B, PAB -> PA + B)
        - kdBB * s.pBB * aSB1_conc
        - kdAB * s.pAB * aSB0_conc
        # Consumption by termination (PB + PB -> D, PB + PA -> D)
        - RtBB_1
        - RtBA_1
    )

    # Active A sequences (2nd order moment)
    dydt.aSA2 = s.V * (
        # Formation by propagation (PA + A -> PA, PB + A -> PA)
        +kpAA * s.A_conc * (s.R_conc + aSA0_conc + 2 * aSA1_conc + aSA2_conc)
        + kpBA * s.A_conc * (s.RB_conc + aSB0_conc)
        # Consumption by propagation (PA + A -> PA, PA + B -> PB)
        - kpAA * s.A_conc * aSA2_conc
        - kpAB * s.B_conc * (s.RA_conc + aSA2_conc)
        # Formation by depropagation (PAA -> PA + A, PAB -> PA + B)
        + kdAA * s.pAA * (aSA2_conc - 2 * aSA1_conc + aSA0_conc)
        + kdAB * s.pAB * a20_frac * aSB0_conc
        # Consumption by depropagation (PAA -> PA + A, PBA -> PB + A)
        - kdAA * s.pAA * aSA2_conc
        - kdBA * s.pBA * aSA0_conc
        # Consumption by termination (PA + PA -> D, PA + PB -> D)
        - RtAA_2
        - RtAB_2
    )

    # Active B sequences (2nd order moment)
    dydt.aSB2 = s.V * (
        # Formation by propagation (PB + B -> PB, PA + B -> PB)
        +kpBB * s.B_conc * (s.R_conc + aSB0_conc + 2 * aSB1_conc + aSB2_conc)
        + kpAB * s.B_conc * (s.RA_conc + aSA0_conc)
        # Consumption by propagation (PB + B -> PB, PB + A -> PA)
        - kpBB * s.B_conc * aSB2_conc
        - kpBA * s.A_conc * (s.RB_conc + aSB2_conc)
        # Formation by depropagation (PBB -> PB + B, PBA -> PB + A)
        + kdBB * s.pBB * (aSB2_conc - 2 * aSB1_conc + aSB0_conc)
        + kdBA * s.pBA * b20_frac * aSA0_conc
        # Consumption by depropagation (PBB -> PB + B, PAB -> PA + B)
        - kdBB * s.pBB * aSB2_conc
        - kdAB * s.pAB * aSB0_conc
        # Consumption by termination (PB + PB -> D, PB + PA -> D)
        - RtBB_2
        - RtBA_2
    )

    # Inactive A sequences (0th order moment)
    dydt.iSA0 = s.V * (
        # Formation by cross-propagation (PA + B -> PB)
        +kpAB * s.B_conc * (s.RA_conc + aSA0_conc)
        # Consumption by depropagation (PAB -> PA + B)
        - kdAB * s.pAB * aSB0_conc
        # Formation by termination (PA + PA -> D, PA + PB -> D)
        + RtAA_0
        + RtAB_0
    )

    # Inactive B sequences (0th order moment)
    dydt.iSB0 = s.V * (
        # Formation by cross-propagation (PB + A -> PA)
        +kpBA * s.A_conc * (s.RB_conc + aSB0_conc)
        # Consumption by depropagation (PBA -> PB + A)
        - kdBA * s.pBA * aSA0_conc
        # Formation by termination (PB + PB -> D, PB + PA -> D)
        + RtBB_0
        + RtBA_0
    )

    # Inactive A sequences (1st order moment)
    dydt.iSA1 = s.V * (
        # Formation by cross-propagation (PA + B -> PB)
        +kpAB * s.B_conc * (s.RA_conc + aSA1_conc)
        # Consumption by depropagation (PAB -> PA + B)
        - kdAB * s.pAB * a10_frac * aSB0_conc
        # Formation by termination (PA + PA -> D, PA + PB -> D)
        + RtAA_1
        + RtAB_1
    )

    # Inactive B sequences (1st order moment)
    dydt.iSB1 = s.V * (
        # Formation by cross-propagation (PB + A -> PA)
        +kpBA * s.A_conc * (s.RB_conc + aSB1_conc)
        # Consumption by depropagation (PBA -> PB + A)
        - kdBA * s.pBA * b10_frac * aSA0_conc
        # Formation by termination (PB + PB -> D, PB + PA -> D)
        + RtBB_1
        + RtBA_1
    )

    # Inactive A sequences (2nd order moment)
    dydt.iSA2 = s.V * (
        # Formation by cross-propagation (PA + B -> PB)
        +kpAB * s.B_conc * (s.RA_conc + aSA2_conc)
        # Consumption by depropagation (PAB -> PA + B)
        - kdAB * s.pAB * a20_frac * aSB0_conc
        # Formation by termination (PA + PA -> D, PA + PB -> D)
        + RtAA_2
        + RtAB_2
    )

    # Inactive B sequences (2nd order moment)
    dydt.iSB2 = s.V * (
        # Formation by cross-propagation (PB + A -> PA)
        +kpBA * s.A_conc * (s.RB_conc + aSB2_conc)
        # Consumption by depropagation (PBA -> PB + A)
        - kdBA * s.pBA * b20_frac * aSA0_conc
        # Formation by termination (PB + PB -> D, PB + PA -> D)
        + RtBB_2
        + RtBA_2
    )

    return dydt
