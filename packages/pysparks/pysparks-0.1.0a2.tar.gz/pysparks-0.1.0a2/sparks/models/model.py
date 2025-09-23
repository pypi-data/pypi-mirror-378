from typing import (
    Dict,
    Tuple,
    Type,
    Generic,
    Protocol,
    Union,
    runtime_checkable,
    Any,
)
from abc import abstractmethod

from runkmc.kmc.config import KMCConfig
from runkmc.results import SimulationResult

from sparks.core import NDArrayType
from .state import StateType, SimulationData
from .reactions import RateType, RxnIDType, ReactionNetworkDef


@runtime_checkable
class BaseModelProtocol(Generic[RateType, StateType], Protocol):
    name: str

    RateClass: Type[RateType]
    StateClass: Type[StateType]


class ODEFunction(Protocol):
    """ODE Function for React models"""

    def __call__(
        self,
        dydt: StateType,
        k: RateType,
        t: NDArrayType,
        state: StateType,
        **kwargs: Any,
    ) -> StateType: ...


@runtime_checkable
class SupportsDeterministicODE(BaseModelProtocol, Protocol):

    @abstractmethod
    def ode_function(self) -> ODEFunction:
        """ODE function for deterministic simulation"""
        raise NotImplementedError


@runtime_checkable
class SupportsReactionNetwork(BaseModelProtocol, Protocol):
    RxnIDClass: Type[RxnIDType]

    @abstractmethod
    def reactions(self) -> ReactionNetworkDef:
        raise NotImplementedError


SupportsDeterministicSimulation = Union[
    SupportsDeterministicODE, SupportsReactionNetwork
]


@runtime_checkable
class SupportsStochasticSimulation(SupportsReactionNetwork, Protocol):

    @abstractmethod
    def get_kmc_inputs(
        self, k: RateType, s0: StateType, config: KMCConfig, model_name: str, **kwargs
    ) -> Dict[str, Any]:
        """Get the inputs for KMC simulation"""
        raise NotImplementedError

    @abstractmethod
    def parse_kmc_outputs(
        self, result: SimulationResult, model_name: str, **kwargs
    ) -> Tuple[SimulationData[StateType], Any]:
        """Parse the outputs from KMC simulation"""
        raise NotImplementedError
