from abc import ABC
from dataclasses import dataclass, fields, field
from typing import Generic, Type, TypeVar, List, Optional, Callable, Any
from functools import cached_property

import numpy as np

from sparks.core import NDArrayType


def state_field(default: float = 0.0):
    return field(default_factory=lambda: np.array(default))


StateType = TypeVar("StateType", bound="State")


@dataclass
class State(ABC):

    t: NDArrayType = state_field()

    def __post_init__(self):

        for name in self.get_species_names():
            value = np.array(getattr(self, name))
            setattr(self, name, np.array(value))

    @classmethod
    def get_species_names(cls) -> List[str]:
        """Get all species field names (excluding time)"""
        # Cache the result to avoid repeated fields() calls
        if not hasattr(cls, "_cached_species_names"):
            cls._cached_species_names = [f.name for f in fields(cls) if f.name != "t"]
        return cls._cached_species_names

    @property
    def is_trajectory(self) -> bool:
        """Check if the state is a trajectory"""
        return self.t.ndim > 0 and len(self.t) > 1

    def to_array(self) -> NDArrayType:
        """Convert state to numpy array (excluding time)"""
        return np.array([getattr(self, name) for name in self.get_species_names()])

    @classmethod
    def from_array(
        cls: Type[StateType],
        arr: NDArrayType,
        t: Optional[NDArrayType] = None,
    ) -> StateType:
        """Create a state from a numpy array"""
        arr = np.asarray(arr)
        species_names = cls.get_species_names()

        if t is None:
            t = np.array(0.0) if arr.ndim == 1 else np.zeros(arr.shape[-1])

        kwargs = {"t": t}
        if arr.ndim == 1:
            for i, name in enumerate(species_names):
                kwargs[name] = arr[i]  # Skip np.array(), let __post_init__ handle it
        else:
            # Trajectory
            for i, name in enumerate(species_names):
                kwargs[name] = arr[i]

        return cls(**kwargs)

    def get_init_state(self) -> "State":
        return self.from_array(self.to_array()[:, 0], t=np.array(0.0))


@dataclass
class SimulationData(Generic[StateType]):
    trajectory: StateType
    init_state: StateType

    @staticmethod
    def from_trajectory(traj: StateType) -> "SimulationData":
        init_state = traj.get_init_state()
        return SimulationData(trajectory=traj, init_state=init_state)


def interpolate_at_time(traj: StateType, target_times: NDArrayType) -> StateType:

    t = traj.t
    target_times = np.asarray(target_times)

    if np.any(target_times < t[0]) or np.any(target_times > t[-1]):
        raise ValueError("Target times are out of bounds.")

    species_names = traj.get_species_names()
    kwargs = {"t": target_times}

    for name in species_names:
        species_values = getattr(traj, name)
        interp_values = np.interp(target_times, t, species_values)
        kwargs[name] = interp_values

    return type(traj)(**kwargs)


def interpolate_by(traj: StateType, x: NDArrayType, xp: NDArrayType) -> StateType:

    x = np.asarray(x)
    xp = np.asarray(xp)

    t_at_x = np.interp(x, xp, traj.t)
    return interpolate_at_time(traj, t_at_x)


def get_midpoint_values(traj: StateType) -> StateType:

    t = traj.t
    t_mid = 0.5 * (t[:-1] + t[1:])

    return interpolate_at_time(traj, t_mid)


def derived(fn: Callable[..., Any] = None, *, cache: bool = True):
    """
    Use on implementation of State to make a property (optionally cached) that
    is also visible to the RHS view builder as a derived relationship.
    """

    if fn is None:
        # allow @derived_property() with kwargs
        return lambda f: derived(f, cache=cache)

    prop = cached_property(fn) if cache else property(fn)
    setattr(prop, "__is_derived__", True)
    return prop
