from __future__ import annotations
from typing import Dict, Type, Any

import numpy as np
from scipy.integrate import solve_ivp

from sparks.models import (
    RateType,
    StateType,
    SimulationData,
    ODEFunction,
    SupportsDeterministicODE,
    SupportsDeterministicSimulation,
    SupportsReactionNetwork,
)
from sparks.simulators import Simulator

from .compile import compile_odes, OdeSolutionState, OdeSolution
from .reactions import optimized_reaction_odes


def get_ode_function(
    model: SupportsDeterministicSimulation,
    prefer_reactions: bool = False,
) -> ODEFunction:

    has_custom_ode = isinstance(model, SupportsDeterministicODE)
    has_reactions = isinstance(model, SupportsReactionNetwork)

    if prefer_reactions and has_reactions:
        # Use reaction-generated ODE
        return optimized_reaction_odes(model.StateClass, model.reactions())
    elif has_custom_ode:
        # Use custom ODE function
        return model.ode_function()
    elif has_reactions:
        # Fallback to reaction-based ODE if no custom ODE is defined
        return optimized_reaction_odes(model.StateClass, model.reactions())
    else:
        raise ValueError(
            "Model must implement either SupportsDeterministicODE or SupportsReactionNetwork."
        )


def default_solver_params():
    return {"method": "LSODA", "rtol": 1e-6, "atol": 1e-6}


class DeterministicSimulator(Simulator):
    """Simulator for deterministic systems of differential equations."""

    def __init__(
        self,
        model: SupportsDeterministicSimulation,
        k: RateType,
        prefer_reactions: bool = False,
    ):
        """
        Initialize the deterministic simulator with a model and rate constants.
        """
        super().__init__(model, k)
        self.model = model

        self.model_state_class: Type[StateType] = self.model.StateClass
        self.ode_fun = get_ode_function(self.model, prefer_reactions)

    def simulate(
        self,
        t_eval: np.ndarray,
        init_state: StateType,
        *,
        solver_kwargs: Dict[str, Any] = default_solver_params(),
        **model_kwargs: Any,
    ) -> SimulationData[StateType]:

        self.y0 = init_state
        y0_np = init_state.to_array()
        self.t_eval = t_eval

        ode_fun = compile_odes(
            self.model_state_class, self.ode_fun, self.k, **model_kwargs
        )

        self.sol = solve_ivp(
            fun=ode_fun,
            y0=y0_np,
            t_span=(t_eval[0], t_eval[-1]),
            t_eval=t_eval,
            dense_output=True,
            **solver_kwargs,
        )

        ode_sol: OdeSolution = self.sol.sol
        assert isinstance(
            ode_sol, OdeSolution
        ), "solve_ivp did not return a valid OdeSolution."
        self.ode_sol = OdeSolutionState(self.model_state_class, ode_sol)

        self.t = np.array(self.sol.t)
        self.y_np = np.array(self.sol.y)

        self.trajectory = self.model_state_class.from_array(self.y_np, t=self.t)

        self.data = SimulationData(trajectory=self.trajectory, init_state=init_state)

        return self.data
