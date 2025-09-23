from typing import Type
from pathlib import Path

import numpy as np
from runkmc.kmc.config import KMCConfig
from runkmc.kmc import RunKMC, SimulationConfig
from runkmc.results import SimulationResult

from sparks.models import (
    RateType,
    StateType,
    SimulationData,
    SupportsStochasticSimulation,
)
from sparks.simulators import Simulator


class StochasticSimulator(Simulator):
    """Kinetic Monte Carlo Simulator (using RunKMC)"""

    def __init__(
        self, model: SupportsStochasticSimulation, k: RateType, data_dir: Path | str
    ):

        super().__init__(model, k)
        self.model = model

        self.model_state_class: Type[StateType] = self.model.StateClass
        self.run_kmc = RunKMC(data_dir, force_compile=False)

    def simulate(
        self,
        t_eval: np.ndarray,
        init_state: StateType,
        num_units: int,
        model_name: str,
        **kwargs,
    ) -> SimulationData[StateType]:

        self.y0 = init_state
        self.t_eval = t_eval
        self.model_name = model_name

        self.kmc_config = KMCConfig(
            num_units=num_units,
            termination_time=t_eval[-1],
            analysis_time=t_eval[1] - t_eval[0],
        )
        kmc_inputs = self.model.get_kmc_inputs(
            self.k, self.y0, self.kmc_config, model_name=model_name, **kwargs
        )

        self.sim_config = SimulationConfig(model_name, kmc_inputs, **kwargs)

        self.result: SimulationResult = self.run_kmc.run_from_config(self.sim_config)

        data, mdata = self.model.parse_kmc_outputs(self.result, self.model_name)
        self.mdata = mdata

        return data
