from time import time
import logging
from typing import Tuple, List, Union

import numpy as np
from pyscf.gto.mole import Mole
from pyscf.scf import RHF

from .ucc import UCC as _UCCBase
from openfermion.transforms import jordan_wigner
from tyxonq.libs.hamiltonian_encoding.pauli_io import reverse_qop_idx
from tyxonq.applications.chem.chem_libs.hamiltonians_chem_library.hamiltonian_builders import (
    get_hop_from_integral,
)
from tyxonq.applications.chem.chem_libs.circuit_chem_library.ansatz_kupccgsd import (
    generate_kupccgsd_ex1_ops,
    generate_kupccgsd_ex2_ops,
    generate_kupccgsd_ex_ops,
)

logger = logging.getLogger(__name__)


class KUPCCGSD(_UCCBase):
    """
    Run :math:`k`-UpCCGSD calculation.
    The interfaces are similar to :class:`UCCSD <tencirchem.UCCSD>`.
    """

    def __init__(
        self,
        mol: Union[Mole, RHF],
        active_space: Tuple[int, int] = None,
        aslst: List[int] = None,
        mo_coeff: np.ndarray = None,
        k: int = 3,
        n_tries: int = 1,
        runtime: str = None,
        run_hf: bool = True,
        run_fci: bool = True,
    ):
        r"""
        Initialize the class with molecular input.

        Parameters
        ----------
        mol: Mole or RHF
            The molecule as PySCF ``Mole`` object or the PySCF ``RHF`` object
        active_space: Tuple[int, int], optional
            Active space approximation. The first integer is the number of electrons and the second integer is
            the number or spatial-orbitals. Defaults to None.
        aslst: List[int], optional
            Pick orbitals for the active space. Defaults to None which means the orbitals are sorted by energy.
            The orbital index is 0-based.

            .. note::
                See `PySCF document <https://pyscf.org/user/mcscf.html#picking-an-active-space>`_
                for choosing the active space orbitals. Here orbital index is 0-based, whereas in PySCF by default it
                is 1-based.

        mo_coeff: np.ndarray, optional
            Molecule coefficients. If provided then RHF is skipped.
            Can be used in combination with the ``init_state`` attribute.
            Defaults to None which means RHF orbitals are used.
        k: int, optional
            The number of layers in the ansatz. Defaults to 3
        n_tries: int, optional
            The number of different initial points used for VQE calculation.
            For large circuits usually a lot of runs are required for good accuracy.
            Defaults to 1.
        runtime: str, optional
            The runtime to run the calculation (e.g., 'device').
        run_hf: bool, optional
            Whether run HF for molecule orbitals. Defaults to ``True``.
        run_mp2: bool, optional
            Whether run MP2 for energy reference. Defaults to ``True``.
        run_ccsd: bool, optional
            Whether run CCSD for energy reference. Defaults to ``True``.
        run_fci: bool, optional
            Whether run FCI for energy reference. Defaults to ``True``.

        See Also
        --------
        tencirchem.UCCSD
        tencirchem.PUCCD
        tencirchem.UCC
        """
        # ---- RHF setup ----
        if hasattr(mol, "mol") and hasattr(mol, "kernel"):
            hf = mol
        else:
            hf = RHF(mol)
        if mo_coeff is not None:
            hf.mo_coeff = np.asarray(mo_coeff)
        hf.chkfile = None
        hf.verbose = 0
        if run_hf:
            hf.kernel()

        # ---- Integrals and core energy ----
        from tyxonq.applications.chem.chem_libs.hamiltonians_chem_library.hamiltonian_builders import (
            get_integral_from_hf,
        )
        int1e, int2e, e_core = get_integral_from_hf(hf, active_space=active_space, aslst=aslst)

        # Active space size and electrons
        if active_space is None:
            n_elec = int(getattr(hf.mol, "nelectron"))
            n_cas = int(getattr(hf.mol, "nao"))
        else:
            n_elec, n_cas = int(active_space[0]), int(active_space[1])

        no = n_elec // 2
        nv = n_cas - no

        # Build qubit Hamiltonian
        n_qubits = 2 * n_cas
        fop = get_hop_from_integral(int1e, int2e)
        hq = reverse_qop_idx(jordan_wigner(fop), n_qubits)

        # ---- Initialize UCC base ----
        _UCCBase.__init__(
            self,
            n_qubits=n_qubits,
            n_elec_s=(no, n_elec - no),
            h_qubit_op=hq,
            runtime=(runtime or "device"),
            mode="fermion",
            ex_ops=None,
            param_ids=None,
            init_state=None,
            decompose_multicontrol=False,
            trotter=False,
        )
        # the number of layers
        self.k = k
        # the number of different initialization
        self.n_tries = n_tries
        # For generalized k-UpCCGSD, generate ex-ops independent of CC amplitudes
        ex_ops, param_ids, init_guess = generate_kupccgsd_ex_ops(no, nv, self.k)
        # param ids are contiguous starting at 0; init_guess sized accordingly
        self.ex_ops = ex_ops
        self.param_ids = param_ids
        self.init_guess = np.asarray(init_guess, dtype=np.float64)
        self.init_guess_list = [self.init_guess]
        for _ in range(self.n_tries - 1):
            self.init_guess_list.append(np.random.rand(self.n_params) - 0.5)
        self.e_tries_list = []
        self.opt_res_list = []
        self.staging_time = self.opt_time = None
        self.e_core = float(e_core)
        if run_fci:
            try:
                from pyscf.fci import direct_spin1 as _fci_ds1  # type: ignore
                self.e_fci = float(_fci_ds1.FCI().kernel(int1e, int2e, n_cas, (no, n_elec - no))[0] + self.e_core)
            except Exception:
                self.e_fci = float("nan")

    def kernel(self, **opts):
        _, stating_time = self.get_opt_function(with_time=True)

        time1 = time()
        for i in range(self.n_tries):
            logger.info(f"k-UpCCGSD try {i}")
            if self.n_tries == 1:
                if not np.allclose(self.init_guess, self.init_guess_list[0]):
                    logger.info("Inconsistent `self.init_guess` and `self.init_guess_list`.  Use `self.init_guess`.")
            else:
                self.init_guess = self.init_guess_list[i]
            # Forward runtime options; rely on UCCSD.kernel implementation
            e_try = super().kernel(**opts)
            # Prefer optimizer result stored by base class; fallback to simple namespace
            r = self.opt_res
            self.opt_res_list.append(r)
            logger.info(f"k-UpCCGSD try {i} energy {float(r.fun)}")
        self.opt_res_list.sort(key=lambda x: x.fun)
        self.e_tries_list = [float(res.fun) for res in self.opt_res_list]
        time2 = time()

        self.staging_time = stating_time
        self.opt_time = time2 - time1
        self.opt_res = self.opt_res_list[0]
        self.opt_res.e_tries = self.e_tries_list

        if not self.opt_res.success:
            logger.warning("Optimization failed. See `.opt_res` for details.")

        self.init_guess = self.opt_res.init_guess
        return float(self.opt_res.fun)

    def get_ex_ops(self, t1: np.ndarray = None, t2: np.ndarray = None) -> Tuple[List[Tuple], List[int], np.ndarray]:
        """
        Get one-body and two-body excitation operators for :math:`k`-UpCCGSD ansatz.
        The excitations are generalized and two-body excitations are restricted to paired ones.
        Initial guesses are generated randomly.

        Parameters
        ----------
        t1: np.ndarray, optional
            Not used. Kept for consistency with the parent method.
        t2: np.ndarray, optional
            Not used. Kept for consistency with the parent method.

        Returns
        -------
        ex_op: List[Tuple]
            The excitation operators. Each operator is represented by a tuple of ints.
        param_ids: List[int]
            The mapping from excitations to parameters.
        init_guess: np.ndarray
            The initial guess for the parameters.

        See Also
        --------
        get_ex1_ops: Get generalized one-body excitation operators.
        get_ex2_ops: Get generalized paired two-body excitation operators.

        Examples
        --------
        >>> from tencirchem import KUPCCGSD
        >>> from tencirchem.molecule import h2
        >>> kupccgsd = KUPCCGSD(h2)
        >>> ex_op, param_ids, init_guess = kupccgsd.get_ex_ops()
        >>> ex_op
        [(1, 3, 2, 0), (3, 2), (1, 0), (1, 3, 2, 0), (3, 2), (1, 0), (1, 3, 2, 0), (3, 2), (1, 0)]
        >>> param_ids
        [0, 1, 1, 2, 3, 3, 4, 5, 5]
        >>> init_guess  # doctest:+ELLIPSIS
        array([...])
        """
        ex_op, param_ids, init_guess = generate_kupccgsd_ex_ops(self.no, self.nv, self.k)
        return ex_op, param_ids, init_guess

    def get_ex1_ops(self, t1: np.ndarray = None) -> Tuple[List[Tuple], List[int], np.ndarray]:
        """
        Get generalized one-body excitation operators.

        Parameters
        ----------
        t1: np.ndarray, optional
            Not used. Kept for consistency with the parent method.

        Returns
        -------
        ex_op: List[Tuple]
            The excitation operators. Each operator is represented by a tuple of ints.
        param_ids: List[int]
            The mapping from excitations to parameters.
        init_guess: np.ndarray
            The initial guess for the parameters.

        See Also
        --------
        get_ex2_ops: Get generalized paired two-body excitation operators.
        get_ex_ops: Get one-body and two-body excitation operators for :math:`k`-UpCCGSD ansatz.
        """
        assert t1 is None
        return generate_kupccgsd_ex1_ops(self.no, self.nv)

    def get_ex2_ops(self, t2: np.ndarray = None) -> Tuple[List[Tuple], List[int], np.ndarray]:
        """
        Get generalized paired two-body excitation operators.

        Parameters
        ----------
        t2: np.ndarray, optional
            Not used. Kept for consistency with the parent method.

        Returns
        -------
        ex_op: List[Tuple]
            The excitation operators. Each operator is represented by a tuple of ints.
        param_ids: List[int]
            The mapping from excitations to parameters.
        init_guess: np.ndarray
            The initial guess for the parameters.

        See Also
        --------
        get_ex1_ops: Get one-body excitation operators.
        get_ex_ops: Get one-body and two-body excitation operators for :math:`k`-UpCCGSD ansatz.
        """

        assert t2 is None
        return generate_kupccgsd_ex2_ops(self.no, self.nv)

    @property
    def e_kupccgsd(self):
        """
        Returns :math:`k`-UpCCGSD energy
        """
        return self.energy()

    @classmethod
    def from_integral(
        cls,
        int1e: np.ndarray,
        int2e: np.ndarray,
        n_elec: Union[int, Tuple[int, int]],
        e_core: float | None = None,
        ovlp: np.ndarray | None = None,
        *,
        mode: str = "fermion",
        runtime: str = "device",
        k: int = 3,
        n_tries: int = 1,
        **kwargs,
    ) -> "KUPCCGSD":
        # Build qubit Hamiltonian from integrals
        if isinstance(n_elec, int):
            assert n_elec % 2 == 0
            n_elec_s = (n_elec // 2, n_elec // 2)
        else:
            n_elec_s = (int(n_elec[0]), int(n_elec[1]))
        n_cas = int(len(int1e))
        n_qubits = 2 * n_cas
        fop = get_hop_from_integral(int1e, int2e)
        hq = reverse_qop_idx(jordan_wigner(fop), n_qubits)

        # Manually construct instance without requiring a Mole object
        inst = cls.__new__(cls)
        # Initialize via UCCSD constructor path to ensure UCCSD helpers exist
        # Use base UCC constructor (numeric/molecule-independent)
        _UCCBase.__init__(
            inst,
            n_qubits=n_qubits,
            n_elec_s=n_elec_s,
            h_qubit_op=hq,
            runtime=runtime,
            mode=mode,
            ex_ops=None,
            param_ids=None,
            init_state=None,
            decompose_multicontrol=False,
            trotter=False,
        )
        # Record minimal CAS metadata used by KUPCCGSD helpers
        no = int(sum(n_elec_s)) // 2
        nv = int(n_cas) - no
        inst.no = no
        inst.nv = nv
        inst.active_space = (int(sum(n_elec_s)), int(n_cas))
        # Set algorithm-specific knobs
        inst.k = int(k)
        inst.n_tries = int(n_tries)
        # Generate generalized UpCCGSD excitations and init guess
        ex_op, param_ids, _init_guess = generate_kupccgsd_ex_ops(inst.no, inst.nv, inst.k)
        # Normalize ids to contiguous range and set zero init guess of correct size
        import numpy as _np
        max_id = max(param_ids) if len(param_ids) > 0 else -1
        id_map = {old: idx for idx, old in enumerate(range(max_id + 1))}
        param_ids = [id_map[int(i)] for i in param_ids]
        init_vec = _np.zeros((max_id + 1,), dtype=_np.float64)
        inst.ex_ops = ex_op
        inst.param_ids = param_ids
        inst.init_guess = _np.asarray(init_vec, dtype=_np.float64)
        # Core energy if provided
        try:
            inst.e_core = float(e_core) if e_core is not None else 0.0
        except Exception:
            inst.e_core = 0.0
        # init_guess_list
        inst.init_guess_list = [inst.init_guess]
        for _ in range(inst.n_tries - 1):
            inst.init_guess_list.append(_np.random.rand(inst.init_guess.size) - 0.5)
        # Initialize optimization bookkeeping like TCC
        inst.e_tries_list = []
        inst.opt_res_list = []
        inst.staging_time = None
        inst.opt_time = None
        # Reference FCI energy for assertions (optional)
        try:
            from pyscf.fci import direct_spin1 as _fci_ds1  # type: ignore
            na, nb = n_elec_s
            inst.e_fci = float(_fci_ds1.FCI().kernel(int1e, int2e, n_cas, (na, nb))[0] + (float(e_core) if e_core is not None else 0.0))
        except Exception:
            inst.e_fci = float('nan')
        return inst
