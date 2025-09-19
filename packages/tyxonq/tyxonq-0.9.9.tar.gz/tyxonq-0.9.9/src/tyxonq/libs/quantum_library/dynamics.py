from __future__ import annotations

"""Quantum dynamics utilities.

This module provides small, dependency-light helpers for:
- Representing a Pauli-sum Hamiltonian as COO-like sparse data (for small systems)
- Evolving a statevector under a (time-dependent) Hamiltonian via a basic ODE stepper
- Computing dense expectation values ⟨ψ|H|ψ⟩

Naming policy:
- Prefer concise, domain-native names: "dynamics", "evolve_state", "expectation".
- Backwards-compatibility aliases are provided for prior names:
  - PauliStringSum2COO  -> PauliSumCOO
  - evolve_state_numeric -> evolve_state
  - expval_dense -> expectation
"""

from typing import Optional, Sequence, Tuple, Callable, Any
import numpy as np
from ...numerics import NumericBackend as nb
from ...numerics.api import ArrayBackend

from .kernels.pauli import pauli_string_sum_dense, pauli_string_sum_coo


class PauliSumCOO:
    """Lightweight adapter for a Pauli-sum Hamiltonian.

    Parameters
    ----------
    terms:
        Iterable of Pauli term encodings, each length-n with entries in {0,1,2,3} denoting I,X,Y,Z.
    weights:
        Optional coefficients w_j. If omitted, assumed 1.0 for each term.

    Methods
    -------
    to_dense() -> np.ndarray
        Construct a dense matrix H (2^n by 2^n) for small n.
    to_coo() -> (data, row, col, shape)
        Return a COO-like tuple compatible with simple sparse workflows.
    """

    def __init__(self, terms: Sequence[Sequence[int]], weights: Optional[Sequence[float]] = None):
        self._terms = [list(t) for t in terms]
        self._weights = list(weights) if weights is not None else None

    def to_dense(self):
        return pauli_string_sum_dense(self._terms, self._weights)

    def to_coo(self) -> Tuple[np.ndarray, np.ndarray, np.ndarray, Tuple[int, int]]:
        return pauli_string_sum_coo(self._terms, self._weights)


def evolve_state(
    H_or_terms: Any | Sequence[Sequence[int]] | Callable[[float], Any],
    psi0: Any,
    t: float,
    *,
    steps: int = 128,
    weights: Optional[Sequence[float]] = None,
    method: str = "euler",
    backend: ArrayBackend | None = None,
) -> Any:
    """Integrate Schrödinger dynamics for small statevectors.

    Solves dψ/dt = -i H(t) ψ using a simple fixed-step scheme.

    Parameters
    ----------
    H_or_terms:
        - Dense Hamiltonian matrix H (for small n)
        - Or Pauli-term list ([[p_00,...,p_0n], ...]) with optional weights
        - Or a callable H(t) returning the instantaneous dense Hamiltonian
    psi0:
        Initial statevector of shape (2^n,).
    t:
        Total evolution time.
    steps:
        Number of integration steps (fixed step). More steps -> higher accuracy.
    weights:
        Coefficients for Pauli terms if H_or_terms is a term list.
    method:
        Currently only "euler" is implemented.

    Returns
    -------
    np.ndarray
        The evolved, normalized statevector ψ(t).
    """
    if callable(H_or_terms):
        H_fun = H_or_terms
    else:
        if isinstance(H_or_terms, (list, tuple)):
            H = pauli_string_sum_dense(H_or_terms, weights)
        else:
            H = nb.asarray(H_or_terms)
        H_fun = lambda _t: H

    K = backend or nb
    n_steps = max(1, int(steps))
    dt = float(t) / float(n_steps)
    dt_b = K.array(dt, dtype=K.float64)
    j = K.array(1j, dtype=K.complex128)
    psi = K.asarray(psi0)
    for i in range(n_steps):
        Hi = K.asarray(H_fun(i * dt))
        rhs = -j * K.matmul(Hi, psi)
        psi = psi + dt_b * rhs
        nrm2 = K.sum(K.abs(psi) ** 2)
        nrm = K.sqrt(nrm2)
        if float(np.asarray(K.to_numpy(nrm))) > 0.0:
            psi = psi / nrm
    return psi


def expectation(psi: Any, H: Any, *, backend: ArrayBackend | None = None) -> Any:
    """Compute the dense expectation value ⟨ψ|H|ψ⟩.

    For small systems where H is explicitly dense.
    """
    K = backend or nb
    psiK = K.asarray(psi)
    HK = K.asarray(H)
    val = K.matmul(K.conj(psiK), K.matmul(HK, psiK))  # type: ignore[arg-type]
    return K.real(val)


# ---- Backwards compatibility aliases ----
PauliStringSum2COO = PauliSumCOO
evolve_state_numeric = evolve_state
expval_dense = expectation


__all__ = [
    "PauliSumCOO",
    "evolve_state",
    "expectation",
    # Compat
    "PauliStringSum2COO",
    "evolve_state_numeric",
    "expval_dense",
]


