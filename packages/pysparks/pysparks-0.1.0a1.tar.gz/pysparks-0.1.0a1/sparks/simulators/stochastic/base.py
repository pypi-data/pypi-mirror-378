from typing import Type
from pathlib import Path
from dataclasses import dataclass

import numpy as np
from runkmc.simulation import RunKMC, SimulationConfig, SimulationResult

from sparks.models import (
    RateType,
    StateType,
    SimulationData,
    SupportsStochasticSimulation,
)
from sparks.simulators import Simulator


@dataclass
class KMCConfig:

    num_particles: int
    termination_time: float
    analysis_time: float


class StochasticSimulator(Simulator):
    """Kinetic Monte Carlo Simulator (using RunKMC)"""

    def __init__(
        self, model: SupportsStochasticSimulation, k: RateType, data_dir: Path | str
    ):

        super().__init__(model, k)
        self.model = model

        self.model_state_class: Type[StateType] = self.model.StateClass
        self.run_kmc = RunKMC(model.name, data_dir, force_compile=False)

    def get_simulation_config(self, model_name: str, **kwargs) -> SimulationConfig:

        kmc_config = KMCConfig(
            num_particles=self.num_particles,
            termination_time=self.t_eval[-1],
            analysis_time=self.t_eval[1] - self.t_eval[0],
        )
        kmc_inputs = self.model.get_kmc_inputs(
            self.k, self.y0, kmc_config, model_name=model_name, **kwargs
        )

        return SimulationConfig(model_name, kmc_inputs, **kwargs)

    def simulate(
        self,
        t_eval: np.ndarray,
        init_state: StateType,
        num_particles: int,
        model_name: str,
        **kwargs,
    ) -> SimulationData[StateType]:

        overwrite = kwargs.pop("overwrite", False)

        self.y0 = init_state
        self.t_eval = t_eval
        self.num_particles = num_particles
        self.model_name = model_name

        config = self.get_simulation_config(self.model_name, **kwargs)

        self.result: SimulationResult = self.run_kmc.run_or_retrieve(config, overwrite)

        data, mdata = self.model.parse_kmc_outputs(self.result, self.model_name)
        self.mdata = mdata

        return data
