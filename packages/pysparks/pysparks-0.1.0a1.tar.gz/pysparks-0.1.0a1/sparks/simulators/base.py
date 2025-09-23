from abc import ABC, abstractmethod

import numpy as np

from sparks.models import BaseModelProtocol, RateType, StateType, SimulationData


class Simulator(ABC):
    """Base class for polymerization simulators"""

    def __init__(self, model: BaseModelProtocol, k: RateType):
        self.model = model
        self.k = k

    @abstractmethod
    def simulate(
        self, t_eval: np.ndarray, init_state: StateType, **kwargs
    ) -> SimulationData[StateType]:
        """Run simulation and return time points and final state"""
        pass
