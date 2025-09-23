from functools import cached_property
from typing import Any, List, Tuple
from dataclasses import dataclass

import numpy as np

from sparks.core import NDArrayType, EPS
from sparks.models import (
    State,
    state_field,
    derived,
    SimulationData,
    ReactionNetworkDef,
    SupportsDeterministicODE,
    SupportsReactionNetwork,
    SupportsStochasticSimulation,
)
from sparks.simulators.stochastic import KMCConfig, SimulationResult


from .reactions import RxnID


@dataclass
class RateCoefficients:
    """Rate coefficients for binary uncontrolled free-radical copolymerization kinetics."""

    # Initiation
    kd: float = 0.0
    f: float = 1.0

    # Propagation
    kpAA: float = 0.0
    kpAB: float = 0.0
    kpBA: float = 0.0
    kpBB: float = 0.0

    # Depropagation
    kdAA: float = 0.0
    kdAB: float = 0.0
    kdBA: float = 0.0
    kdBB: float = 0.0

    # Termination
    ktcAA: float = 0.0
    ktcAB: float = 0.0
    ktcBB: float = 0.0

    ktdAA: float = 0.0
    ktdAB: float = 0.0
    ktdBB: float = 0.0

    def __post_init__(self):
        # Cache some commonly used values
        self._ktAA = self.ktcAA + self.ktdAA
        self._ktAB = self.ktcAB + self.ktdAB
        self._ktBB = self.ktcBB + self.ktdBB

    @cached_property
    def ktAA(self) -> float:
        """Total termination rate for AA"""
        return self._ktAA

    @cached_property
    def ktAB(self) -> float:
        """Total termination rate for AB"""
        return self._ktAB

    @cached_property
    def ktBB(self) -> float:
        """Total termination rate for BB"""
        return self._ktBB

    @cached_property
    def rA(self) -> float:
        """Reactivity ratio for monomer A"""
        return self.kpAA / self.kpAB if self.kpAB != 0 else 0

    @cached_property
    def rB(self) -> float:
        """Reactivity ratio for monomer B"""
        return self.kpBB / self.kpBA if self.kpBA != 0 else 0

    @cached_property
    def rX(self) -> float:
        """Cross-propagation ratio"""
        return self.kpAA / self.kpBB if self.kpBB != 0 else 0

    @cached_property
    def KAA(self) -> float:
        """Equilibrium constant for AA"""
        return self.kdAA / self.kpAA if self.kpAA != 0 else 0

    @cached_property
    def KAB(self) -> float:
        """Equilibrium constant for AB"""
        return self.kdAB / self.kpAB if self.kpAB != 0 else 0

    @cached_property
    def KBA(self) -> float:
        """Equilibrium constant for BA"""
        return self.kdBA / self.kpBA if self.kpBA != 0 else 0

    @cached_property
    def KBB(self) -> float:
        """Equilibrium constant for BB"""
        return self.kdBB / self.kpBB if self.kpBB != 0 else 0


@dataclass
class ModelState(State):
    """State for binary uncontrolled free-radical copolymerization kinetics."""

    I: NDArrayType = state_field(0.0)
    R: NDArrayType = state_field(0.0)
    A: NDArrayType = state_field(0.0)
    B: NDArrayType = state_field(0.0)
    RA: NDArrayType = state_field(0.0)
    RB: NDArrayType = state_field(0.0)
    PAA: NDArrayType = state_field(0.0)
    PAB: NDArrayType = state_field(0.0)
    PBA: NDArrayType = state_field(0.0)
    PBB: NDArrayType = state_field(0.0)
    PD: NDArrayType = state_field(0.0)

    def chain_species_ids(self) -> List[str]:
        return ["R", "RA", "RB", "PAA", "PAB", "PBA", "PBB", "PD"]

    @derived
    def M(self) -> NDArrayType:
        """Total monomer concentration"""
        return self.A + self.B

    @derived
    def fA(self) -> NDArrayType:
        """Fraction of monomer A"""
        return self.A / (self.M + EPS)

    @derived
    def fB(self) -> NDArrayType:
        """Fraction of monomer B"""
        return self.B / (self.M + EPS)

    @derived
    def PA(self) -> NDArrayType:
        """Concentration of polymer chains ending in ~~A"""
        return self.PAA + self.PBA

    @derived
    def PB(self) -> NDArrayType:
        """Concentration of polymer chains ending in ~~B"""
        return self.PAB + self.PBB

    @derived
    def P(self) -> NDArrayType:
        """Total polymer concentration"""
        return self.PA + self.PB

    @derived
    def pA(self) -> NDArrayType:
        """Fraction of polymer chains ending in ~~A"""
        return self.PA / (self.P + EPS)

    @derived
    def pB(self) -> NDArrayType:
        """Fraction of polymer chains ending in ~~B"""
        return self.PB / (self.P + EPS)

    @derived
    def pAA(self) -> NDArrayType:
        """Fraction of polymer chains ending in ~~AA"""
        return self.PAA / (self.PA + EPS)

    @derived
    def pAB(self) -> NDArrayType:
        """Fraction of polymer chains ending in ~~AB"""
        return self.PAB / (self.PB + EPS)

    @derived
    def pBA(self) -> NDArrayType:
        """Fraction of polymer chains ending in ~~BA"""
        return self.PBA / (self.PA + EPS)

    @derived
    def pBB(self) -> NDArrayType:
        """Fraction of polymer chains ending in ~~BB"""
        return self.PBB / (self.PB + EPS)

    def xA(self, s0: "ModelState") -> NDArrayType:
        """Conversion of monomer A"""
        return 1 - self.A / (s0.A + EPS)

    def xB(self, s0: "ModelState") -> NDArrayType:
        """Conversion of monomer B"""
        return 1 - self.B / (s0.B + EPS)

    def x(self, s0: "ModelState") -> NDArrayType:
        """Conversion of all monomer"""
        return 1 - (self.A + self.B) / (s0.A + s0.B + EPS)

    def FA(self, s0: "ModelState") -> NDArrayType:
        """Fraction of A monomers in polymer chains (composition)"""
        return (s0.A - self.A) / (s0.M - self.M + EPS)

    def FB(self, s0: "ModelState") -> NDArrayType:
        """Fraction of B monomers in polymer chains (composition)"""
        return (s0.B - self.B) / (s0.M - self.M + EPS)


@dataclass
class ChainModelState(State):
    """Represents the state variables for the chain length distribution model."""

    lam_0: NDArrayType = state_field(0.0)
    lam_1: NDArrayType = state_field(0.0)
    lam_2: NDArrayType = state_field(0.0)
    mu_0: NDArrayType = state_field(0.0)
    mu_1: NDArrayType = state_field(0.0)
    mu_2: NDArrayType = state_field(0.0)

    @derived
    def NACL(self) -> NDArrayType:
        """Number average chain length"""
        return (self.lam_1 + self.mu_1) / (self.lam_0 + self.mu_0 + EPS)

    @derived
    def WACL(self) -> NDArrayType:
        """Weight average chain length"""
        return (self.lam_2 + self.mu_2) / (self.lam_1 + self.mu_1 + EPS)

    @derived
    def PDI(self) -> NDArrayType:
        """Dispersity"""
        return self.WACL / self.NACL

    # @cached_property
    # def aP_1(self) -> StateVariable:
    #     """1st moment of the active CLD (excluding dead chains)"""
    #     return StateVariable("aP_1", (self.PA1 + self.PB1).value)

    # @cached_property
    # def P_1(self) -> StateVariable:
    #     """1st moment of the total CLD (active and dead chains)"""
    #     return StateVariable("P_1", (self.aP_1 + self.PD1).value)

    # @cached_property
    # def aP_2(self) -> StateVariable:
    #     """2nd moment of the active CLD (excluding dead chains)"""
    #     return StateVariable("aP_2", (self.PA2 + self.PB2).value)

    # @cached_property
    # def P_2(self) -> StateVariable:
    #     """2nd moment of the total CLD (active and dead chains)"""
    #     return StateVariable("P_2", (self.aP_2 + self.PD2).value)

    # @cached_property
    # def NACL(self) -> StateVariable:
    #     """Number average chain length"""
    #     return StateVariable("NACL", (self.P_1 / self.P_0).value)

    # @cached_property
    # def WACL(self) -> StateVariable:
    #     """Weight average chain length"""
    #     return StateVariable("WACL", (self.P_2 / self.P_1).value)

    # @cached_property
    # def PDI(self) -> StateVariable:
    #     """Dispersity"""
    #     return StateVariable("PDI", (self.WACL / self.NACL).value)


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


class Model(
    SupportsDeterministicODE,
    SupportsStochasticSimulation,
    SupportsReactionNetwork,
):

    name = "FRP2"
    RateClass = RateCoefficients
    StateClass = ModelState
    RxnIDClass = RxnID

    def ode_function(self):
        from .equations import kinetic_odes

        return kinetic_odes

    def reactions(self) -> ReactionNetworkDef:
        from .reactions import reactions

        return reactions

    def get_kmc_inputs(
        self,
        k: RateCoefficients,
        state: ModelState,
        config: KMCConfig,
        model_name: str,
        **kwargs,
    ) -> dict[str, Any]:
        """Get KMC simulation inputs"""
        from .kmc import get_kmc_inputs

        return get_kmc_inputs(k, state, config, model_name)

    def parse_kmc_outputs(
        self, result: SimulationResult, model_name: str, **kwargs
    ) -> Tuple[SimulationData[ModelState], Any]:
        """Parse KMC simulation results"""
        from .kmc import parse_kmc_outputs

        return parse_kmc_outputs(result, model_name)


class ChainModel(SupportsDeterministicODE):

    name = "FRP2 Chain Model"
    RateClass = RateCoefficients
    StateClass = ChainModelState

    def ode_function(self):
        from .equations import chain_odes

        return chain_odes


class SequenceModel(SupportsDeterministicODE):

    name = "FRP2 Sequence Model"
    RateClass = RateCoefficients
    StateClass = SequenceModelState

    def ode_function(self):
        from .equations import sequence_odes

        return sequence_odes
