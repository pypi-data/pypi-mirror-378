from typing import Any, Callable, Dict, Generic, Optional, Tuple, Type, TypeAlias, cast
from functools import cached_property

import numpy as np
from scipy.integrate._ivp.ivp import OdeSolution

from sparks.core import NDArrayType
from sparks.models import StateType, ODEFunction, RateType

# SciPy RHS: f(t, y) -> ydot
ScipyODEFun: TypeAlias = Callable[[float, NDArrayType], NDArrayType]

# Sparks model: (dydt, k, t, s) -> dydt
ODEFun: TypeAlias = Callable[[StateType, RateType, float, StateType], StateType]

ODEStaticSolution: TypeAlias = Optional[Tuple[StateType, OdeSolution]]


# --------------------------------------------------------------------------------------
# Functions to compile a State class for fast evaluation in an ODE solver
# --------------------------------------------------------------------------------------


class _ViewBase:
    """
    Optimized read-only view of a State for fast ODE evaluation.
    """

    __slots__ = ("_y", "_t", "_memo")

    def __init__(self):
        self._y = None
        self._t = 0.0
        self._memo = {}

    @property
    def t(self) -> float:
        return self._t

    @t.setter
    def t(self, value: float) -> None:
        self._t = float(value)

    def __setattr__(self, name: str, value: float) -> None:
        if name in _ViewBase.__slots__:
            return object.__setattr__(self, name, value)
        if name == "t":
            return type(self).t.__set__(self, float(value))
        raise AttributeError("Input state is read-only.")


class _WriterBase:
    """
    Optimized writable view of a State for fast ODE evaluation.
    """

    __slots__ = ("_buf", "_t")

    def __init__(self):
        self._buf: Optional[NDArrayType] = None
        self._t: float = 0.0

    @property
    def t(self) -> float:
        return self._t

    @t.setter
    def t(self, value: float) -> None:
        self._t = float(value)


"""Cache for state view and writer types"""
_VIEW_CACHE: Dict[Tuple[Type[StateType], bool], Type[_ViewBase]] = {}
_WRITER_CACHE: Dict[Type[StateType], Type[_WriterBase]] = {}


def compile_state_to_view(
    state_cls: Type[StateType], *, with_derived: bool
) -> Type[_ViewBase]:
    key = (state_cls, bool(with_derived))
    View = _VIEW_CACHE.get(key)

    if View is not None:
        return View

    names = state_cls.get_species_names()

    class View(_ViewBase):
        pass

    # Fast fixed-index properties
    for i, name in enumerate(names):

        def _make_state_var(ix=i, n=name):

            def get(self: _ViewBase):
                return self._y[ix]

            get.__name__ = f"get_{n}"
            return property(get)

        setattr(View, name, _make_state_var())

    # bind @derived getters (memoized per call)
    if with_derived:
        species_set = set(names)

        for attr_name, attr in vars(state_cls).items():

            if attr_name in species_set:
                continue

            if getattr(attr, "__is_derived__", False):

                if isinstance(attr, property):
                    fn = attr.fget
                elif isinstance(attr, cached_property):
                    fn = attr.func
                else:
                    fn = attr

                if attr_name in species_set:
                    raise ValueError(
                        f"Derived name '{attr_name}' conflicts with species."
                    )

                def _make_derived(_n=attr_name, _f=fn):

                    def get(self: _ViewBase):
                        m = self._memo
                        if _n in m:
                            return m[_n]
                        val = _f(self)
                        m[_n] = val
                        return val

                    get.__name__ = f"get_derived_{_n}"
                    return property(get)

                setattr(View, attr_name, _make_derived())

    def __getattr__(self, name: str):
        raise AttributeError(f"Unknown field '{name}'. Valid: {names}")

    View.__getattr__ = __getattr__
    View.__name__ = f"View_{state_cls.__name__}"
    _VIEW_CACHE[key] = View
    return View


def compile_state_to_writer(state_cls: Type[StateType]) -> Type[_WriterBase]:

    Writer = _WRITER_CACHE.get(state_cls)
    if Writer is not None:
        return Writer

    names = state_cls.get_species_names()

    class Writer(_WriterBase):
        pass

    for i, name in enumerate(names):

        def _make_state_var(ix=i, n=name):

            def get(self: _WriterBase) -> float:
                return self._buf[ix]

            def set(self: _WriterBase, value: float) -> None:
                self._buf[ix] = float(value)

            get.__name__ = f"get_{n}"
            set.__name__ = f"set_{n}"
            return property(get, set)

        setattr(Writer, name, _make_state_var())

    def __getattr__(self, name: str):
        raise AttributeError(f"Unknown field '{name}'. Valid: {names}")

    Writer.__getattr__ = __getattr__
    Writer.__name__ = f"Writer_{state_cls.__name__}"
    _WRITER_CACHE[state_cls] = Writer
    return Writer


def make_scipy_rhs(
    state_cls: Type[StateType],
    k: RateType,
    *,
    attach_derived: bool = True,
    debug: bool = False,
    **bound_kwargs: Any,
) -> Callable[[ODEFun], ScipyODEFun]:
    """Optimization of State"""

    names = state_cls.get_species_names()  # Single source of truth
    if "t" in names:
        raise ValueError("State class should not have 't' as a species name.")

    View = compile_state_to_view(state_cls, with_derived=attach_derived)
    Writer = compile_state_to_writer(state_cls)

    view = View()
    writer = Writer()
    buf: Optional[NDArrayType] = None

    # ----------------- Decorator that returns SciPy's f(t,y) -----------------
    def decorator(model_fun: ODEFun) -> ScipyODEFun:

        # Guard against double wrapping
        if getattr(model_fun, "__is_scipy_rhs__", False):
            raise TypeError(
                "make_scipy_rhs received a SciPy (t,y)->ydot function; "
                "pass a dydt-first model `(dydt, k, t, s)` instead."
            )

        def rhs(t: float, y: NDArrayType) -> NDArrayType:
            nonlocal buf

            # Allocate or resize output buffer as needed
            if (buf is None) or (buf.shape != y.shape) or (buf.dtype != y.dtype):
                buf = np.empty_like(y)

            # Wire the view/writer to current arrays and time
            view._y = y
            view.t = t
            view._memo.clear()  # Fresh deriveds each call

            writer._buf = buf
            writer.t = t

            if debug:
                # Help catch missing assignments quickly
                buf[...] = np.nan
            else:
                buf.fill(0.0)

            # Give IDEs/types a hint; at runtime these are view/writer
            s = cast(StateType, view)
            dydt = cast(StateType, writer)

            extra = {}
            for key, val in bound_kwargs.items():
                if getattr(val, "_is_state_provider", False):
                    extra[key] = val(t)
                else:
                    extra[key] = val

            # Run the user's equations
            model_fun(dydt, k, t, s, **extra)

            # Ensure all outputs were written this call
            if debug and np.isnan(buf).any():
                missing = [names[i] for i, v in enumerate(buf) if np.isnan(v)]
                raise RuntimeError(f"RHS did not set all outputs: {missing}")

            return buf

        rhs.__is_scipy_rhs__ = True
        rhs.__wrapped_model__ = model_fun
        return rhs

    return decorator


def compile_odes(
    state_cls: Type[StateType],
    ode_fun: ODEFunction,
    k: RateType,
    # static_state: Optional[OdeSolution] = None,
    **kwargs: Any,
) -> ScipyODEFun:

    return make_scipy_rhs(state_cls, k, **kwargs)(ode_fun)


class OdeSolutionState(Generic[StateType]):
    """
    Wrap an OdeSolution and present it as a read-only State view at time t.
    """

    __slots__ = ("_sol", "_view", "_state_cls", "_debug")
    _is_state_provider = True

    def __init__(
        self,
        state_cls: Type[StateType],
        ode_sol: OdeSolution,
        *,
        attach_derived: bool = True,
        debug: bool = False,
    ):
        self._state_cls = state_cls
        self._sol = ode_sol

        View = compile_state_to_view(state_cls, with_derived=attach_derived)
        self._view = View()
        self._debug = debug

    def __call__(self, t: float) -> StateType:
        y = np.asarray(self._sol(t), dtype=float)

        # SciPy returns (n,) for scalar t, or (n, m) for vector t – handle scalar only here
        if y.ndim == 2:
            if y.shape[1] == 1:
                y = y[:, 0]
            else:
                raise ValueError(
                    "OdeSolutionState: OdeSolution returned multiple time points; expected scalar t."
                )

        if self._debug:
            expected = len(self._state_cls.get_species_names())
            if y.ndim != 1 or y.shape[0] != expected:
                raise ValueError(
                    f"OdeSolutionState: expected length {expected} for {self._state_cls.__name__}, got {y.shape}."
                )

        v = self._view
        v._y = y
        v.t = t
        v._memo.clear()
        return cast(StateType, v)
