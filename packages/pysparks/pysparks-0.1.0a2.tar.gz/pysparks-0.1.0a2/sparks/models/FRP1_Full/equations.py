from dataclasses import dataclass

import numpy as np

from sparks.core import NDArrayType, NA
from sparks.utils import okprint, errprint
from sparks.data import MonomerType
from .model import RateCoefficients, ModelState


@dataclass
class Context:

    # Parameters
    use_diffusion_control: bool = True
    # use_diffusion_control: bool = False
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
    times = [50, 100, 150, 200, 250, 300, 350, 400, 450, 500, 550, 600]
    time_idx: int = 0


def kinetic_odes(
    k: RateCoefficients, t: NDArrayType, s: ModelState, context: Context = Context()
) -> ModelState:
    """Defines the ODEs for the FRP1 model."""

    T_C = k.T_C
    T_K = T_C + 273.15  # Convert Celsius to Kelvin

    # Extract properties
    iprops = k.iprops
    mprops = k.mprops

    dydt = ModelState()
    dydt.t = t

    # Save initial state
    if not context.init_state and t >= 0:
        context.init_state = s

    nM0 = context.init_state.M  # Initial moles of monomer

    ########################
    ### Molecular Weight ###
    ########################

    MW_eff = mprops.MW
    Mn = MW_eff * s.mu_1 / s.mu_0
    Mw = MW_eff * s.mu_2 / s.mu_1

    mass_m = s.M * MW_eff
    mass_p = s.nPM * MW_eff
    mass_s = 0.0
    total_mass = mass_m + mass_p + mass_s
    wp = mass_p / total_mass

    vol_m = mass_m / mprops.dens_m
    vol_p = mass_p / mprops.dens_p
    vol_s = 0.0

    # Initiation
    kd = iprops.kd.get(mprops.id, iprops.kd[MonomerType.General])
    f = iprops.f.get(mprops.id, iprops.f[MonomerType.General])
    kth = mprops.kth

    # Propagation
    kp = mprops.kp

    # Chain transfer
    kfm = mprops.kf_m
    kfz = 0

    kfs = 0
    kfCTA = 0
    kfp = 0

    # Termination rate constants
    kt = mprops.kt
    ktd_ratio = mprops.ktd_ratio  # ktd / ktc

    kp_factor = 1
    kfm_factor = 1

    if context.use_diffusion_control:

        # Calculate the free volume
        Vf_m = (mprops.Vf_m + mprops.alpha_m * (T_K - mprops.Tg_m)) * vol_m / s.V
        Vf_p = (mprops.Vf_p + mprops.alpha_p * (T_K - mprops.Tg_p)) * vol_p / s.V
        Vf_s = 0.0
        Vf = Vf_m + Vf_p + Vf_s

        if not context.triggered:
            # 1) Segmental diffusion termination
            c = (nM0 - s.M) / s.V / MW_eff  # Mass concentration of accumulated polymer
            kt = kt * (1 + mprops.delta * c)

            K3_test = (Mw**mprops.m) * np.exp(mprops.A / Vf)
            if K3_test >= mprops.K3:
                context.triggered = True
                context.t_event = t
                context.Vf_cr1 = Vf * 1.0
                context.kt_cr = kt
                context.Mw_cr = Mw
                print(
                    f"K3 triggered at t={t:.2f} s: K3_test={K3_test:.2f}, K3={mprops.K3:.2f}"
                )
                print(f"Triggered at t={t:.2f} s, Vf={Vf:.2f} L, Mw={Mw/1e3:.2f} kDa")
        else:
            # print(f"t = {t:.2f} s, Vf = {Vf:.2f} L, Mw = {Mw/1e3:.2f} kDa")
            kt = (
                context.kt_cr
                * (context.Mw_cr / Mw) ** mprops.n
                * np.exp(-mprops.A * (1 / Vf - 1 / context.Vf_cr1))
            )

        # 2) Translational diffusion termination
        Vf_cr2 = mprops.Vf_c
        if Vf < Vf_cr2:
            kp_factor = kfm_factor = np.exp(-mprops.B * (1 / Vf - 1 / Vf_cr2))

        Vf_i = iprops.Vf_i.get(mprops.id, iprops.Vf_i[MonomerType.General])
        C_factor = iprops.C.get(mprops.id, iprops.C[MonomerType.General])
        if Vf < Vf_i:
            f = f * np.exp(-C_factor * (1 / Vf - 1 / Vf_i))

        # 3) Reaction diffusion termination
        D = (
            mprops.n_s * (mprops.l0) ** 2 * kp * s.M_conc / 6.0
        )  # Diffusion coefficient (m^2/s)
        delta = (6 * (vol_m / s.M) / (np.pi * NA)) ** (1 / 3.0)
        # delta = mprops.delta
        kt_rd = 8 * np.pi * NA * delta * D / 1000
        kt += 0.0 * kt_rd

    kp = kp * kp_factor
    kfm = kfm * kfm_factor

    ktc = kt / (1 + ktd_ratio)
    ktd = kt * ktd_ratio / (1 + ktd_ratio)

    kdp = 0
    kp = kp - kdp / s.M_conc if s.M_conc > 0 else kp

    Ri = 2 * f * kd * s.I_conc + 2 * kth * s.M_conc**3
    Rp = kp * s.M_conc * s.R_conc

    # Volume balance
    dydt.V = s.V * (-Rp * MW_eff * (1 / mprops.dens_m - 1 / mprops.dens_p))

    # Initiator balance
    dydt.I = s.V * (-kd * s.I_conc)

    # Monomer balance
    dydt.M = s.V * (
        # Consumption by propagation
        -kp * s.M_conc * s.R_conc
        # Consumption by chain transfer to monomer
        - kfm * s.R_conc * s.M_conc
        # Consumption by thermal initiation
        - 3 * kth * s.M_conc**3
    )

    dydt.nPM = s.V * Rp

    # Polymer radical balance
    dydt.R = s.V * (
        # Formation by initiation
        Ri
        # Consumption by chain transfer to impurity
        - kfz * s.R_conc * s.Z_conc
        # Consumption by termination
        - kt * s.R_conc**2
    )
    # Reactions for propagation and
    # chain transfer to monomer, solvent, and CTA
    # ommitted since they "consume" and "form" radicals

    # Dead polymer balance
    dydt.D = s.V * (
        # Formation by termination (comb.)
        +ktc * s.R_conc**2
        # Formation by termination (disp.)
        + 2 * ktd * s.R_conc**2
        # Formation by chain transfer to monomer
        + kfm * s.R_conc * s.M_conc
        # Formation by chain transfer to solvent
        + kfs * s.R_conc * s.S_conc
        # Formation by chain transfer to CTA
        + kfCTA * s.R_conc * s.CTA_conc
        # Formation by chain transfer to impurity
        + kfz * s.R_conc * s.Z_conc
    )

    # Solvent balance
    dydt.S = s.V * (
        # Consumption by chain transfer to solvent
        -kfs
        * s.R_conc
        * s.S_conc
    )

    # Chain transfer agent balance
    dydt.CTA = s.V * (
        # Consumption by chain transfer to CTA
        -kfCTA
        * s.R_conc
        * s.CTA_conc
    )

    # Impurity balance
    dydt.Z = s.V * (
        # Consumption by chain transfer to impurity
        -kfz
        * s.R_conc
        * s.Z_conc
    )

    # Active radicals (0th order moment)
    dydt.lam_0 = s.V * (
        # Formation by initiation
        Ri
        # Consumption by termination
        - kt * s.lam0_conc**2
        # Consumption from impurity
        - kfz * s.lam0_conc * s.Z_conc
    )

    # Active radicals (1st order moment)
    dydt.lam_1 = s.V * (
        # Formation by initiation
        Ri
        # Formation by propagation
        + kp * s.M_conc * s.lam0_conc
        # Consumption by termination
        - kt * s.lam0_conc * s.lam1_conc
        # Consumption from chain transfer
        - (kfCTA * s.CTA_conc + kfm * s.M_conc + kfs * s.S_conc)
        * (s.lam1_conc - s.lam0_conc)
        # Formation by chain transfer to polymer
        + kfp * (s.lam0_conc * s.mu2_conc - s.lam1_conc * s.mu1_conc)
        # Consumption by chain transfer to impurity
        - kfz * s.lam1_conc * s.Z_conc
    )

    # Active radicals (2nd order moment)
    dydt.lam_2 = s.V * (
        # Formation by initiation
        Ri
        # Formation by propagation
        + kp * s.M_conc * (s.lam0_conc + 2 * s.lam1_conc)
        # Consumption by termination
        - kt * s.lam0_conc * s.lam2_conc
        # Consumption from chain transfer
        - (kfCTA * s.CTA_conc + kfm * s.M_conc + kfs * s.S_conc)
        * (s.lam2_conc - s.lam0_conc)
        # Formation by chain transfer to polymer
        + kfp * (s.lam0_conc * s.mu3_conc - s.lam2_conc * s.mu1_conc)
        # Consumption by chain transfer to impurity
        - kfz * s.lam2_conc * s.Z_conc
    )

    # Dead radicals (0th order moment)
    dydt.mu_0 = s.V * (
        # Formation by termination
        +(0.5 * ktc + ktd) * s.lam0_conc**2
        # Formation by chain transfer
        + (kfm * s.M_conc + kfCTA * s.CTA_conc + kfs * s.S_conc + kfz * s.Z_conc)
        * s.lam0_conc
    )

    # Dead radicals (1st order moment)
    dydt.mu_1 = s.V * (
        # Formation by termination
        +(ktc + ktd) * s.lam0_conc * s.lam1_conc
        # Formation by chain transfer
        + (kfm * s.M_conc + kfCTA * s.CTA_conc + kfs * s.S_conc + kfz * s.Z_conc)
        * s.lam1_conc
        # Chain transfer to polymer
        + kfp * (s.lam1_conc * s.mu1_conc - s.lam0_conc * s.mu2_conc)
    )

    # Dead radicals (2nd order moment)
    dydt.mu_2 = s.V * (
        # Formation by termination (comb.)
        ktc * (s.lam0_conc * s.lam2_conc + s.lam1_conc**2)
        # Formation by termination (disp.)
        + ktd * s.lam0_conc * s.lam2_conc
        # Formation by chain transfer
        + (kfm * s.M_conc + kfCTA * s.CTA_conc + kfs * s.S_conc + kfz * s.Z_conc)
        * s.lam2_conc
        # Chain transfer to polymer
        + kfp * (s.lam2_conc * s.mu1_conc - s.lam0_conc * s.mu3_conc)
    )

    vol_error = 100 * abs((vol_m + vol_p - s.V) / s.V) if s.V > 0 else 0

    mole_error = 100 * abs((s.M + s.nPM - nM0) / (nM0)) if (nM0) > 0 else 0

    lam_0_error = (
        100 * abs((s.lam0_conc - s.R_conc) / s.lam0_conc) if s.lam0_conc > 0 else 0
    )

    # if context.debug_counter % context.debug_interval == 0:
    time = np.inf
    if context.time_idx < len(context.times):
        time = context.times[context.time_idx]

    if t >= time:
        context.time_idx += 1
        vol_error = 100 * abs((vol_m + vol_p + vol_s - s.V) / s.V)
        print(f"Step {context.time_idx}: t={t:.2f}")

        print(f"Time: {t:.2f} s, Volume: {s.V:.3e} L")
        print(
            f"kd: {kd:.3e}, kp: {kp:.3e}, kt: {kt:.3e}, kfm: {kfm:.3e}, kfs: {kfs:.3e}"
        )
        print(f"Vf: {Vf:.3e} L, Mn: {Mn:.3e} g/mol, Mw: {Mw:.3e} g/mol")

        mole_error_str = f"\tMole balance error: {mole_error:.3e}%"
        if mole_error > 1.0:
            errprint(mole_error_str)
        else:
            okprint(mole_error_str)

        vol_error_str = f"\tVolume balance error: {vol_error:.3e}%"
        print(f"\tVolume: {s.V:.3f} L, vol_m: {vol_m:.3f} L, vol_p: {vol_p:.3f} L")
        if vol_error > 1.0:
            errprint(vol_error_str)
        else:
            okprint(vol_error_str)

        lam_0_error_str = f"\tlam_0 error: {lam_0_error:.3e}%"
        if lam_0_error > 1.0:
            errprint(lam_0_error_str)
            errprint(f"\t\tkt: {kt:.3e}, ktd: {ktd:.3e}, ktc: {ktc:.3e}")
            errprint(
                f"\t\tRi: {Ri:.3e}, Rp: {Rp:.3e}, M: {s.M_conc:.3e}, R: {s.R_conc:.3e}"
            )
            errprint(f"\t\tCalculated lam_0: {s.lam_0:.3e}, Expected: {s.R_conc:.3e}")
        else:
            okprint(lam_0_error_str)
        # print(f"lam_0: {s.lam_0.value:.3e}, Ptot: {Ptot:.3e}, Rtot: {Rtot:.3e}")
        active_NACL = (s.lam_1 / s.lam_0) if s.lam_0 > 0 else 0
        print(f"\tActive NACL: {active_NACL:.2f}")

        inactive_NACL = (s.mu_1 / s.mu_0) if s.mu_0 > 0 else 0
        print(f"\tInactive NACL: {inactive_NACL:.2f}")

        print()
    context.debug_counter += 1

    return dydt
