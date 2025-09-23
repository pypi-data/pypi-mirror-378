from enum import Enum
from dataclasses import dataclass

from sparks.utils.formulas import arrhenius_eqn, kcal_to_J, C_to_K, get_arrhenius_const
from sparks.core import R_cal

# +-----------------------------------------------------------
# | Monomer Rate Constants and Properties sourced from WATPOLY
# | (https://doi.org/10.1080/10601325.2017.1312678)
# | and other literature sources as noted below
# +-----------------------------------------------------------


class MonomerType(Enum):
    General = "General"
    AMS = "AMS"
    MMA = "MMA"
    BA = "BA"
    Sty = "Sty"
    AN = "AN"
    HEA = "HEA"
    BMA = "BMA"
    AA = "AA"
    EA = "EA"


@dataclass
class MonomerData:

    name: str
    id: MonomerType
    # id: str

    # Molecular weight of the monomer (g/mol)
    MW: float

    # Glass transition temperature of the monomer (K)
    Tg_m: float

    # Glass transition temperature of the polymer (K)
    Tg_p: float

    # Heat capacity of the monomer (cal/kg/K)
    Cp_m: float

    # Heat capacity of the polymer (cal/kg/K)
    Cp_p: float

    # Heat of reaction (cal/mol)
    deltaH: float

    # Density of monomer (g/L)
    dens_m: float

    # Density of polymer (g/L)
    dens_p: float

    # Rate of propagation (L/mol/min)
    kp: float

    # Rate of termination (L/mol/min)
    kt: float

    # Disproportionation to combination ratio
    ktd_ratio: float

    # Transfer to monomer rate (L/mol/min)
    kf_m: float

    # Transfer to polymer rate (L/mol/min)
    kf_p: float

    # Internal double bond rate of propagation (L/mol/min)
    kp_in: float

    # Terminal double bond rate of propagation (L/mol/min)
    kp_te: float

    # Reaction radius for segmental diffusion (L/g)
    delta: float

    # Critical free volume (L)
    Vf_c: float

    # Free volume of the monomer (L)
    Vf_m: float

    # Thermal expansion coefficient of the monomer (L/K)
    alpha_m: float

    # Free volume of the polymer (L)
    Vf_p: float

    # Thermal expansion coefficient of the polymer (L/K)
    alpha_p: float

    # Rate of decrease of kp
    B: float

    # Gel-effect model parameter
    m: float
    n: float

    # Rate of decrease of kt
    A: float

    # Onset pt. of translational diffusion-control
    K3: float

    # Avg. number of monomer units per chain
    n_s: float

    # Length of monomer unit per chain (cm)
    l0: float

    # Thermal (/self) initiation rate (L^2/mol^2/min)
    kth: float


# S. I. Cheong & A. Penlidis (2003)
# Modeling of the Copolymerization, with Depropagation, of α-Methyl Styrene
# and Methyl Methacrylate at an Elevated Temperature
# Table 1
kp_AMS_100C = 390 * 60  # L/mol/min
Ea_kp_AMS = kcal_to_J(13)  # J/mol
A_kp_AMS = get_arrhenius_const(Ea_kp_AMS, kp_AMS_100C, C_to_K(100))
kp_AMS = arrhenius_eqn(A_kp_AMS, Ea_kp_AMS)

kt_AMS_100C = 8.3e11  # L/mol/min
Ea_kt_AMS = kcal_to_J(2)
A_kt_AMS = get_arrhenius_const(Ea_kt_AMS, kt_AMS_100C, C_to_K(100))
kt_AMS = arrhenius_eqn(A_kt_AMS, Ea_kt_AMS)


def alpha_methyl_styrene(T_K: float) -> MonomerData:
    return MonomerData(
        name="alpha-methyl styrene",
        id=MonomerType.AMS,
        MW=118.16,
        Tg_m=150.15,
        Tg_p=449.15,
        Cp_m=400,
        Cp_p=400,
        deltaH=-1.7e4,
        dens_m=(0.875 - 0.000918 * (T_K - 273.15)) * 1000,
        dens_p=(1.15 - 0.000918 * (T_K - 273.15)) * 1000,
        kp=kp_AMS(T_K),
        kt=kt_AMS(T_K),
        ktd_ratio=0.07,
        kf_m=arrhenius_eqn(3.3615e9, 15177, R=R_cal)(T_K),
        kf_p=0.0,
        kp_in=0.0,
        kp_te=0.0,
        delta=0.001,
        Vf_c=arrhenius_eqn(1.2, 2220, R=R_cal)(T_K),
        Vf_m=0.025,
        alpha_m=0.001,
        Vf_p=0.025,
        alpha_p=0.00048,
        B=0.5,
        m=0.5,
        n=1.75,
        A=0.55,
        K3=1e10,
        n_s=120,
        l0=5.0e-8,
        kth=2.5e-9 * 60,  # Cheong 2003
    )


# kp/kt from Nising P., & Meyer T. Ind. Eng. Chem. Res., Vol. 43, No. 23, 2004
# - Ref: Brandup & Immergut, Polymer Handbook, 4th ed. (II-84)
# - - Ref: H. K. Mahabadi, K. F. O'Driscoll, J. Macromol. Sci. A: Chem., 11, 967 (1977).
def methyl_methacrylate(T_K: float) -> MonomerData:
    return MonomerData(
        name="methyl methacrylate",
        id=MonomerType.MMA,
        MW=100.12,
        Tg_m=167.1,
        Tg_p=378,
        Cp_m=411.1,
        Cp_p=400,
        deltaH=-1.381e4,
        dens_m=(0.9665 - 0.001164 * (T_K - 273.15)) * 1e3,
        dens_p=(1.195 - 0.00033 * (T_K - 273.15)) * 1e3,
        kp=arrhenius_eqn(2.952e7, 4353, R=R_cal)(T_K),
        kt=arrhenius_eqn(5.88e9, 701, R=R_cal)(T_K),
        ktd_ratio=arrhenius_eqn(1.6093, -440.12, R=R_cal)(T_K),
        kf_m=arrhenius_eqn(9.3435e4, 7475, R=R_cal)(T_K),
        kf_p=0.0,
        kp_in=0.0,
        kp_te=0.0,
        delta=0.001,
        Vf_c=arrhenius_eqn(0.7408, 1589.6, R=R_cal)(T_K),
        Vf_m=0.025,
        alpha_m=0.001,
        Vf_p=0.025,
        alpha_p=0.00048,
        B=1.0,
        m=0.5,
        n=1.75,
        A=1.11,
        K3=arrhenius_eqn(0.563, -8900, R=R_cal)(T_K),
        n_s=47,
        l0=6.9e-8,
        kth=arrhenius_eqn(2.26e-6, 6578, R=R_cal)(T_K),
    )
