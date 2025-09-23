from typing import List
from dataclasses import dataclass
from functools import cached_property

from sparks.core import NDArrayType, EPS
from sparks.models import State, state_field, SupportsDeterministicODE
from sparks.data import InitiatorData, MonomerData


@dataclass
class RateCoefficients:
    """Rate constants for homopolymerization kinetics."""

    iprops: InitiatorData  # Initiator properties
    mprops: MonomerData  # Monomer properties
    T_C: float = 0.0  # Temperature in Celsius


@dataclass
class ModelState(State):
    """Represents the state variables for the homopolymer model."""

    V: NDArrayType = state_field(1)

    I: NDArrayType = state_field()
    M: NDArrayType = state_field()
    R: NDArrayType = state_field()
    D: NDArrayType = state_field()

    # Number of moles of monomer in polymer
    nPM: NDArrayType = state_field()

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

    def chain_species_ids(self) -> List[str]:
        return ["R", "D"]

    @cached_property
    def I_conc(self) -> NDArrayType:
        """Initiator concentration"""
        return self.I / (self.V + EPS)

    @cached_property
    def M_conc(self) -> NDArrayType:
        """Monomer concentration"""
        return self.M / (self.V + EPS)

    @cached_property
    def R_conc(self) -> NDArrayType:
        """Radical concentration"""
        return self.R / (self.V + EPS)

    @cached_property
    def D_conc(self) -> NDArrayType:
        """Dead polymer concentration"""
        return self.D / (self.V + EPS)

    @cached_property
    def CTA_conc(self) -> NDArrayType:
        """Chain transfer agent concentration"""
        return self.CTA / (self.V + EPS)

    @cached_property
    def Z_conc(self) -> NDArrayType:
        """Impurity concentration"""
        return self.Z / (self.V + EPS)

    @cached_property
    def S_conc(self) -> NDArrayType:
        """Solvent concentration"""
        return self.S / (self.V + EPS)

    @cached_property
    def lam0_conc(self) -> NDArrayType:
        """Live radical moment 0 concentration"""
        return self.lam_0 / (self.V + EPS)

    @cached_property
    def lam1_conc(self) -> NDArrayType:
        """Live radical moment 1 concentration"""
        return self.lam_1 / (self.V + EPS)

    @cached_property
    def lam2_conc(self) -> NDArrayType:
        """Live radical moment 2 concentration"""
        return self.lam_2 / (self.V + EPS)

    @cached_property
    def mu0_conc(self) -> NDArrayType:
        """Dead polymer moment 0 concentration"""
        return self.mu_0 / (self.V + EPS)

    @cached_property
    def mu1_conc(self) -> NDArrayType:
        """Dead polymer moment 1 concentration"""
        return self.mu_1 / (self.V + EPS)

    @cached_property
    def mu2_conc(self) -> NDArrayType:
        """Dead polymer moment 2 concentration"""
        return self.mu_2 / (self.V + EPS)

    @cached_property
    def mu_3(self) -> NDArrayType:
        """Dead polymer moment 3"""
        return (
            (
                self.mu_2
                / (self.mu_0 * self.mu_1)
                * (2 * self.mu_0 * self.mu_2 - self.mu_2**2)
            )
            if (self.mu_0 * self.mu_1) > 0
            else 0
        )

    @cached_property
    def mu3_conc(self) -> NDArrayType:
        """Dead polymer moment 3 concentration"""
        return self.mu_3 / (self.V + EPS)

    def x(self, s0: "ModelState") -> NDArrayType:
        """Conversion of monomer"""
        return 1 - self.M / (s0.M + EPS)

    @cached_property
    def NACL(self) -> NDArrayType:
        """Number average chain length"""
        return self.mu_1 / (self.mu_0 + EPS)

    @cached_property
    def WACL(self) -> NDArrayType:
        """Weight average chain length"""
        return self.mu_2 / (self.mu_1 + EPS)

    @cached_property
    def PDI(self) -> NDArrayType:
        """Dispersity"""
        return self.WACL / (self.NACL + EPS)


class Model(SupportsDeterministicODE):

    name = "FRP1"
    RateClass = RateCoefficients
    StateClass = ModelState

    def ode_function(self):
        from .equations import kinetic_odes

        return kinetic_odes
