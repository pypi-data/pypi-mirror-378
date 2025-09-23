from dataclasses import dataclass

import numpy as np

from sparks.core import NDArrayType, EPS
from sparks.models import State, state_field, derived
from sparks.data import InitiatorData, MonomerData
from sparks.models import SupportsDeterministicODE, ODEFunction


@dataclass
class RateCoefficients:

    mpropsA: MonomerData
    mpropsB: MonomerData
    iprops: InitiatorData
    T_C: float = 0.0

    # Copolymer reactivity
    rA: float = 1.0
    rB: float = 1.0
    KAA: float = 0.0
    KAB: float = 0.0
    KBA: float = 0.0
    KBB: float = 0.0

    def kp(self, f: float = 1.0):
        """Calculate propagation rate coefficients"""
        kpAA = f * self.mpropsA.kp
        kpBB = f * self.mpropsB.kp
        kpAB = kpAA / self.rA
        kpBA = kpBB / self.rB
        return kpAA, kpAB, kpBA, kpBB

    def kd(self, f: float = 1.0):
        """Calculate depropagation rate coefficients"""
        kpAA, kpAB, kpBA, kpBB = self.kp(f=f)
        kdAA = self.KAA * kpAA
        kdAB = self.KAB * kpAB
        kdBA = self.KBA * kpBA
        kdBB = self.KBB * kpBB
        return kdAA, kdAB, kdBA, kdBB

    def kfm(self, f: float = 1.0):
        """Calculate transfer to monomer rate coefficients"""
        kf_mAA = f * self.mpropsA.kf_m
        kf_mBB = f * self.mpropsB.kf_m
        kf_mAB = kf_mAA / self.rB
        kf_mBA = kf_mBB / self.rA
        return kf_mAA, kf_mAB, kf_mBA, kf_mBB


@dataclass
class ModelState(State):

    V: NDArrayType = state_field(1.0)

    I: NDArrayType = state_field()
    R: NDArrayType = state_field()
    A: NDArrayType = state_field()
    B: NDArrayType = state_field()
    RA: NDArrayType = state_field()
    RB: NDArrayType = state_field()
    PAA: NDArrayType = state_field()
    PAB: NDArrayType = state_field()
    PBA: NDArrayType = state_field()
    PBB: NDArrayType = state_field()
    D: NDArrayType = state_field()

    # Moles of monomers converted to polymer
    nPA: NDArrayType = state_field()
    nPB: NDArrayType = state_field()

    CTA: NDArrayType = state_field()
    S: NDArrayType = state_field()
    Z: NDArrayType = state_field()

    # Live Radical Moment Equations
    lam_0: NDArrayType = state_field()
    lam_1: NDArrayType = state_field()
    lam_2: NDArrayType = state_field()

    # Dead Polymer Moment Equations
    mu_0: NDArrayType = state_field()
    mu_1: NDArrayType = state_field()
    mu_2: NDArrayType = state_field()

    ##############################
    ### Species concentrations ###
    ##############################

    @derived
    def I_conc(self) -> NDArrayType:
        """Concentration of initiator"""
        return np.where(self.V > 0, self.I / self.V, 0.0)

    @derived
    def R_conc(self) -> NDArrayType:
        """Concentration of free radicals"""
        return np.where(self.V > 0, self.R / self.V, 0.0)

    @derived
    def RA_conc(self) -> NDArrayType:
        """Concentration of R-A dyads"""
        return np.where(self.V > 0, self.RA / self.V, 0.0)

    @derived
    def RB_conc(self) -> NDArrayType:
        """Concentration of R-B dyads"""
        return np.where(self.V > 0, self.RB / self.V, 0.0)

    @derived
    def A_conc(self) -> NDArrayType:
        """Concentration of monomer A"""
        return np.where(self.V > 0, self.A / self.V, 0.0)

    @derived
    def B_conc(self) -> NDArrayType:
        """Concentration of monomer B"""
        return np.where(self.V > 0, self.B / self.V, 0.0)

    @derived
    def M_conc(self) -> NDArrayType:
        """Concentration of monomers"""
        return np.where(self.V > 0, self.M / self.V, 0.0)

    @derived
    def PAA_conc(self) -> NDArrayType:
        """Concentration of active polymer chains ending in AA"""
        return np.where(self.V > 0, self.PAA / self.V, 0.0)

    @derived
    def PAB_conc(self) -> NDArrayType:
        """Concentration of active polymer chains ending in AB"""
        return np.where(self.V > 0, self.PAB / self.V, 0.0)

    @derived
    def PBA_conc(self) -> NDArrayType:
        """Concentration of active polymer chains ending in BA"""
        return np.where(self.V > 0, self.PBA / self.V, 0.0)

    @derived
    def PBB_conc(self) -> NDArrayType:
        """Concentration of active polymer chains ending in BB"""
        return np.where(self.V > 0, self.PBB / self.V, 0.0)

    @derived
    def PA_conc(self) -> NDArrayType:
        """Concentration of active polymer chains ending in A"""
        return self.PAA_conc + self.PBA_conc

    @derived
    def PB_conc(self) -> NDArrayType:
        """Concentration of active polymer chains ending in B"""
        return self.PAB_conc + self.PBB_conc

    @derived
    def P_conc(self) -> NDArrayType:
        """Total concentration of active polymer chains"""
        return self.PA_conc + self.PB_conc

    @derived
    def S_conc(self) -> NDArrayType:
        """Concentration of solvent"""
        return np.where(self.V > 0, self.S / self.V, 0.0)

    @derived
    def Z_conc(self) -> NDArrayType:
        """Concentration of impurity"""
        return np.where(self.V > 0, self.Z / self.V, 0.0)

    @derived
    def CTA_conc(self) -> NDArrayType:
        """Concentration of chain transfer agent"""
        return np.where(self.V > 0, self.CTA / self.V, 0.0)

    @derived
    def lam_0_conc(self) -> NDArrayType:
        """Concentration of living radical moment 0"""
        return np.where(self.V > 0, self.lam_0 / self.V, 0.0)

    @derived
    def lam_1_conc(self) -> NDArrayType:
        """Concentration of living radical moment 1"""
        return np.where(self.V > 0, self.lam_1 / self.V, 0.0)

    @derived
    def lam_2_conc(self) -> NDArrayType:
        """Concentration of living radical moment 2"""
        return np.where(self.V > 0, self.lam_2 / self.V, 0.0)

    @derived
    def mu_0_conc(self) -> NDArrayType:
        """Concentration of dead polymer moment 0"""
        return np.where(self.V > 0, self.mu_0 / self.V, 0.0)

    @derived
    def mu_1_conc(self) -> NDArrayType:
        """Concentration of dead polymer moment 1"""
        return np.where(self.V > 0, self.mu_1 / self.V, 0.0)

    @derived
    def mu_2_conc(self) -> NDArrayType:
        """Concentration of dead polymer moment 2"""
        return np.where(self.V > 0, self.mu_2 / self.V, 0.0)

    ##########################
    ### Monomer Properties ###
    ##########################

    @derived
    def M(self) -> NDArrayType:
        """Total moles of monomer"""
        return self.A + self.B

    @derived
    def fA(self) -> NDArrayType:
        """Fraction of monomer A"""
        return np.where(self.M > 0, self.A / self.M, 0.0)

    @derived
    def fB(self) -> NDArrayType:
        """Fraction of monomer B"""
        return np.where(self.M > 0, self.B / self.M, 0.0)

    #################################
    ### Active Polymer Properties ###
    #################################

    @derived
    def PA(self) -> NDArrayType:
        """Moles of active polymer chains ending in A"""
        return self.PAA + self.PBA

    @derived
    def PB(self) -> NDArrayType:
        """Moles of active polymer chains ending in B"""
        return self.PAB + self.PBB

    @derived
    def P(self) -> NDArrayType:
        """Total moles of active polymer chains"""
        return self.PA + self.PB

    @derived
    def pA(self) -> NDArrayType:
        """Fraction of active polymer chains ending in A"""
        return self.PA / (self.P + EPS)

    @derived
    def pB(self) -> NDArrayType:
        """Fraction of active polymer chains ending in B"""
        return self.PB / (self.P + EPS)

    @derived
    def pAA(self) -> NDArrayType:
        """Fraction of active ~A chains ending in ~AA"""
        return self.PAA / (self.PA + EPS)

    @derived
    def pAB(self) -> NDArrayType:
        """Fraction of active ~B chains ending in ~AB"""
        return self.PAB / (self.PB + EPS)

    @derived
    def pBA(self) -> NDArrayType:
        """Fraction of active ~A chains ending in ~BA"""
        return self.PBA / (self.PA + EPS)

    @derived
    def pBB(self) -> NDArrayType:
        """Fraction of active ~B chains ending in ~BB"""
        return self.PBB / (self.PB + EPS)

    @derived
    def FA(self) -> NDArrayType:
        """Composition of monomer A in the active polymer"""
        return self.PA / (self.P + EPS)

    @derived
    def FB(self) -> NDArrayType:
        """Composition of monomer B in the active polymer"""
        return self.PB / (self.P + EPS)

    @derived
    def beta(self) -> NDArrayType:
        """Ratio of monomer B to A in the active polymer"""
        return self.PB / (self.PA + EPS)

    #####################################
    ### Cumulative Polymer Properties ###
    #####################################

    @derived
    def nP(self) -> NDArrayType:
        """Total moles of polymer"""
        return self.nPA + self.nPB

    @derived
    def FbarA(self) -> NDArrayType:
        """Cumulative composition of monomer A in the polymer"""
        return self.nPA / (self.nP + EPS)

    @derived
    def FbarB(self) -> NDArrayType:
        """Cumulative composition of monomer B in the polymer"""
        return self.nPB / (self.nP + EPS)

    # def MW_Eff(self, k: RateCoefficients) -> NDArrayType:
    #     """Molecular weight of the polymer"""
    #     return self.FbarA * k.mpropsA.MW + self.FbarB * k.mpropsB.MW

    ###############################
    ### Chain Length Properties ###
    ###############################

    @derived
    def cld_m0(self) -> NDArrayType:
        """0th moment of the chain length distribution"""
        return 0 * self.lam_0 + self.mu_0

    @derived
    def cld_m1(self) -> NDArrayType:
        """1st moment of the chain length distribution"""
        return 0 * self.lam_1 + self.mu_1

    @derived
    def cld_m2(self) -> NDArrayType:
        """2nd moment of the chain length distribution"""
        return 0 * self.lam_2 + self.mu_2

    @derived
    def active_NACL(self) -> NDArrayType:
        """Number average chain length"""
        return np.where(self.lam_0 > 0, self.lam_1 / self.lam_0, 0.0)

    @derived
    def active_WACL(self) -> NDArrayType:
        """Weight average chain length"""
        return np.where(self.lam_1 > 0, self.lam_2 / self.lam_1, 0.0)

    @derived
    def active_PDI(self) -> NDArrayType:
        """Polydispersity index"""
        return np.where(self.active_NACL > 0, self.active_WACL / self.active_NACL, 0.0)

    @derived
    def NACL(self) -> NDArrayType:
        """Number average chain length"""
        return np.where(self.cld_m0 > 0, self.cld_m1 / self.cld_m0, 0.0)

    @derived
    def WACL(self) -> NDArrayType:
        """Weight average chain length"""
        return np.where(self.cld_m1 > 0, self.cld_m2 / self.cld_m1, 0.0)

    @derived
    def PDI(self) -> NDArrayType:
        """Polydispersity index"""
        return np.where(self.NACL > 0, self.WACL / self.NACL, 0.0)

    ###########################
    ### Computed Properties ###
    ###########################

    def xA(self, s0: "ModelState") -> NDArrayType:
        """Conversion of monomer A"""
        return np.where(s0.A > 0, 1 - self.A / s0.A, 0.0)

    def xB(self, s0: "ModelState") -> NDArrayType:
        """Conversion of monomer B"""
        return np.where(s0.B > 0, 1 - self.B / s0.B, 0.0)

    def x(self, s0: "ModelState") -> NDArrayType:
        """Conversion of all monomer"""
        return np.where((s0.A + s0.B) > 0, 1 - (self.A + self.B) / (s0.A + s0.B), 0.0)


@dataclass
class SequenceModelState(State):
    """Represents the state variables for the sequence distribution model."""

    aSA0: NDArrayType = state_field()
    aSB0: NDArrayType = state_field()
    aSA1: NDArrayType = state_field()
    aSB1: NDArrayType = state_field()
    aSA2: NDArrayType = state_field()
    aSB2: NDArrayType = state_field()

    iSA0: NDArrayType = state_field()
    iSB0: NDArrayType = state_field()
    iSA1: NDArrayType = state_field()
    iSB1: NDArrayType = state_field()
    iSA2: NDArrayType = state_field()
    iSB2: NDArrayType = state_field()

    ###################################################
    ### Moments of the sequence length distribution ###
    ###################################################

    @derived
    def SA0(self) -> NDArrayType:
        """0th moment of the sequence length distribution"""
        return self.aSA0 + self.iSA0

    @derived
    def SB0(self) -> NDArrayType:
        """0th moment of the sequence length distribution"""
        return self.aSB0 + self.iSB0

    @derived
    def SA1(self) -> NDArrayType:
        """1st moment of the sequence length distribution"""
        return self.aSA1 + self.iSA1

    @derived
    def SB1(self) -> NDArrayType:
        """1st moment of the sequence length distribution"""
        return self.aSB1 + self.iSB1

    @derived
    def SA2(self) -> NDArrayType:
        """2nd moment of the sequence length distribution"""
        return self.aSA2 + self.iSA2

    @derived
    def SB2(self) -> NDArrayType:
        """2nd moment of the sequence length distribution"""
        return self.aSB2 + self.iSB2

    ##################################
    ### Active Sequence Statistics ###
    ##################################

    @derived
    def active_NASL_A(self) -> NDArrayType:
        """Number average sequence length of active A sequences"""
        return np.where(self.aSA0 > 0, self.aSA1 / self.aSA0, 0.0)

    @derived
    def active_NASL_B(self) -> NDArrayType:
        """Number average sequence length of active B sequences"""
        return np.where(self.aSB0 > 0, self.aSB1 / self.aSB0, 0.0)

    @derived
    def active_WASL_A(self) -> NDArrayType:
        """Weight average sequence length of active A sequences"""
        return np.where(self.aSA1 > 0, self.aSA2 / self.aSA1, 0.0)

    @derived
    def active_WASL_B(self) -> NDArrayType:
        """Weight average sequence length of active B sequences"""
        return np.where(self.aSB1 > 0, self.aSB2 / self.aSB1, 0.0)

    @derived
    def active_SDI_A(self) -> NDArrayType:
        """Sequence dispersity of active A sequences"""
        return np.where(
            self.active_NASL_A > 0, self.active_WASL_A / self.active_NASL_A, 0.0
        )

    @derived
    def active_SDI_B(self) -> NDArrayType:
        """Sequence dispersity of active B sequences"""
        return np.where(
            self.active_NASL_B > 0, self.active_WASL_B / self.active_NASL_B, 0.0
        )

    ####################################
    ### Inactive Sequence Statistics ###
    ####################################

    @derived
    def inactive_NASL_A(self) -> NDArrayType:
        """Number average sequence length of inactive A sequences"""
        return np.where(self.iSA0 > 0, self.iSA1 / self.iSA0, 0.0)

    @derived
    def inactive_NASL_B(self) -> NDArrayType:
        """Number average sequence length of inactive B sequences"""
        return np.where(self.iSB0 > 0, self.iSB1 / self.iSB0, 0.0)

    @derived
    def inactive_WASL_A(self) -> NDArrayType:
        """Weight average sequence length of inactive A sequences"""
        return np.where(self.iSA1 > 0, self.iSA2 / self.iSA1, 0.0)

    @derived
    def inactive_WASL_B(self) -> NDArrayType:
        """Weight average sequence length of inactive B sequences"""
        return np.where(self.iSB1 > 0, self.iSB2 / self.iSB1, 0.0)

    @derived
    def inactive_SDI_A(self) -> NDArrayType:
        """Sequence dispersity of inactive A sequences"""
        return np.where(
            self.inactive_NASL_A > 0, self.inactive_WASL_A / self.inactive_NASL_A, 0.0
        )

    @derived
    def inactive_SDI_B(self) -> NDArrayType:
        """Sequence dispersity of inactive B sequences"""
        return np.where(
            self.inactive_NASL_B > 0, self.inactive_WASL_B / self.inactive_NASL_B, 0.0
        )

    #################################
    ### Total Sequence Statistics ###
    #################################

    @derived
    def NASL_A(self) -> NDArrayType:
        """Number average sequence length of total A sequences (active + inactive)"""
        return np.where(self.SA0 > 0, self.SA1 / self.SA0, 0.0)

    @derived
    def NASL_B(self) -> NDArrayType:
        """Number average sequence length of total B sequences (active + inactive)"""
        return np.where(self.SB0 > 0, self.SB1 / self.SB0, 0.0)

    @derived
    def WASL_A(self) -> NDArrayType:
        """Weight average sequence length of total A sequences (active + inactive)"""
        return np.where(self.SA1 > 0, self.SA2 / self.SA1, 0.0)

    @derived
    def WASL_B(self) -> NDArrayType:
        """Weight average sequence length of total B sequences (active + inactive)"""
        return np.where(self.SB1 > 0, self.SB2 / self.SB1, 0.0)

    @derived
    def SDI_A(self) -> NDArrayType:
        """Sequence dispersity of total A sequences (active + inactive)"""
        return np.where(self.WASL_A > 0, self.NASL_A / self.WASL_A, 0.0)

    @derived
    def SDI_B(self) -> NDArrayType:
        """Sequence dispersity of total B sequences (active + inactive)"""
        return np.where(self.WASL_B > 0, self.NASL_B / self.WASL_B, 0.0)


def get_sms(s: ModelState, k: RateCoefficients) -> SequenceModelState:

    kpAA, kpAB, kpBA, kpBB = k.kp()
    kdAA, kdAB, kdBA, kdBB = k.kd()

    RpAA = kpAA * s.PA_conc * s.A_conc - kdAA * s.PAA_conc
    RpAB = kpAB * s.PA_conc * s.B_conc - kdAB * s.PAB_conc
    RpBA = kpBA * s.PB_conc * s.A_conc - kdBA * s.PBA_conc
    RpBB = kpBB * s.PB_conc * s.B_conc - kdBB * s.PBB_conc

    Rp = RpAA + RpAB + RpBA + RpBB
    RpA = RpAA + RpAB
    RpB = RpBA + RpBB

    paa = RpAA / RpA
    pbb = RpBB / RpB

    # print(f"RpAA: {RpAA}, RpAB: {RpAB}, RpA: {RpA}")
    # print(f"RpBA: {RpBA}, RpBB: {RpBB}, RpB: {RpB}")
    # print(f"paa: {paa}, pbb: {pbb}")

    sms = SequenceModelState(t=s.t)

    sms.aSA0 = np.ones_like(paa)
    sms.aSB0 = np.ones_like(pbb)
    sms.aSA1 = 1 / (1 - paa)
    sms.aSB1 = 1 / (1 - pbb)
    sms.aSA2 = (1 + paa) / (1 - paa) ** 2
    sms.aSB2 = (1 + pbb) / (1 - pbb) ** 2

    return sms


class Model(SupportsDeterministicODE):

    name = "FRP2 ODE"
    RateClass = RateCoefficients
    StateClass = ModelState

    _state = ModelState()

    def ode_function(self) -> ODEFunction:
        from .equations import kinetic_odes

        return kinetic_odes


class SequenceModel(SupportsDeterministicODE):

    name = "FRP2 ODE Sequence"
    RateClass = RateCoefficients
    StateClass = SequenceModelState

    _state = SequenceModelState()

    def ode_function(self) -> ODEFunction:
        from .equations import sequence_odes

        return sequence_odes
