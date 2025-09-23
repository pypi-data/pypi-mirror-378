import ctypes
from dataclasses import dataclass
from collections.abc import Callable
import traceback

from ._util import _customresize
from ._exception_util import _CExceptionData, _checkException
from ._isolate_handler import _cxn, _isolate_handler, _Opaque


class _CMolecule(ctypes.Structure):
    """:meta private:"""
    MAX_ATOM_OR_BOND_COUNT = 800  # must be the same as the value in the corresponding java file

    _fields_ = [
        ("orig_source", ctypes.c_char_p),
        ("orig_format", ctypes.c_char_p),
        ("atom_count", ctypes.c_int),
        ("atom_symbols", ctypes.c_char_p),
        ("atom_numbers", ctypes.c_int * MAX_ATOM_OR_BOND_COUNT),
        ("atom_mass_numbers", ctypes.c_int * MAX_ATOM_OR_BOND_COUNT),
        ("bond_count", ctypes.c_int),
        ("bond_types", ctypes.c_int * MAX_ATOM_OR_BOND_COUNT),
        ("bond_atoms_1", ctypes.c_int * MAX_ATOM_OR_BOND_COUNT),
        ("bond_atoms_2", ctypes.c_int * MAX_ATOM_OR_BOND_COUNT),
        ("exception_data", ctypes.POINTER(_CExceptionData)),
        ("native_handle", ctypes.c_longlong),
        ("is_null_mol", ctypes.c_bool)
    ]


@dataclass(frozen=True)
class Molecule:
    """
    You can create Molecule by importing with `chemaxon.io.importer.import_mol` function.

    Attributes
    ----------
    _source: `str`
        Source of the molecule. If cmolecule is specified it's not considered.
    _format: `str`
        Input format of the molecule.
    to_svg:
        svg converter function
    cmolecule: _CMolecule
        Optional parameter, native cxn library call's result object
    """
    _source: str
    _format: str
    _to_svg: Callable
    bonds: tuple
    atoms: tuple
    native_handle: ctypes.c_longlong

    def _to_cmol(self):
        """:meta private:"""
        c_molecule = _CMolecule(self._source.encode("utf-8"))
        if (self._format is not None):
            c_molecule.orig_format = self._format.encode("utf-8")
        if self.native_handle is not None:  # some test mols (see import_for_test...) may have None value
            c_molecule.native_handle = self.native_handle
        return c_molecule

    def _repr_svg_(self):
        """
        Returns
        -------
        svg: `str`
            SVG representation of the molecule
        """
        return self._to_svg(self._source)

    def __del__(self):
        thread = _isolate_handler.get_isolate_thread()
        _cxn.free_mol_handle.argtypes = [ctypes.POINTER(_Opaque), ctypes.POINTER(_CMolecule)]
        _cxn.check.restype = ctypes.c_void_p
        try:
            if self.native_handle is not None and not _isolate_handler.isolate_torn_down:
                # some test mols (see import_for_test...) may have None value
                #
                # module level molecule's destructor may be called after isolate tear down, in this case
                # we can't call destroy
                _cxn.free_mol_handle(thread, self._to_cmol())
        finally:
            _isolate_handler.cleanup_isolate_thread(thread)


def _init_mol(to_svg: Callable, cmolecule: _CMolecule = None) -> Molecule:
    """:meta private:"""
    _checkException(cmolecule)

    if cmolecule.is_null_mol:
        return None

    c_bond_types = _customresize(cmolecule.bond_types, cmolecule.bond_count)
    c_bond_atoms_1 = _customresize(cmolecule.bond_atoms_1, cmolecule.bond_count)
    c_bond_atoms_2 = _customresize(cmolecule.bond_atoms_2, cmolecule.bond_count)

    _bonds = []
    for i in range(cmolecule.bond_count):
        _bonds.append(Bond(c_bond_types[i], (c_bond_atoms_1[i], c_bond_atoms_2[i])))

    bond_per_atoms = {a_ind: [] for a_ind in range(cmolecule.atom_count)}
    for b in _bonds:
        for a_ind in b.atoms:
            bond_per_atoms[a_ind].append(b)

    c_atom_symbols = cmolecule.atom_symbols.decode("utf-8").split(";")
    c_atom_numbers = _customresize(cmolecule.atom_numbers, cmolecule.atom_count)
    c_atom_mass_numbers = _customresize(cmolecule.atom_mass_numbers, cmolecule.atom_count)

    _atoms = []
    for i in range(cmolecule.atom_count):
        _atoms.append(Atom(c_atom_symbols[i], c_atom_numbers[i], c_atom_mass_numbers[i],
                           tuple(bond_per_atoms[i])))
    return Molecule(cmolecule.orig_source.decode("utf-8"), cmolecule.orig_format.decode("utf-8"), to_svg, tuple(_bonds),
                    tuple(_atoms), cmolecule.native_handle)

def _init_empty_mol(to_svg: Callable, cmolecule: _CMolecule = None) -> Molecule:
    """:meta private:"""

    c_bond_types = []
    c_bond_atoms_1 = []
    c_bond_atoms_2 = []

    _bonds = []
    bond_per_atoms = {a_ind: [] for a_ind in range(cmolecule.atom_count)}

    c_atom_symbols = []

    c_atom_numbers = []
    c_atom_mass_numbers = []

    _atoms = []

    return Molecule("", "", to_svg, tuple(_bonds),
                    tuple(_atoms), cmolecule.native_handle)

@dataclass(frozen=True)
class Atom:
    """
    Class representing atoms in a molecule.

    Attributes:
    -----------
    symbol : str
        Atom symbol.
    atom_number : int
        Atomic number.
    mass_number: int
        Mass number of the atom. 0 - if mixture of isotopes.
    bond: tuple
        Bonds of the atom.
    """

    symbol: str
    atom_number: int
    mass_number: int
    bonds: tuple


@dataclass(frozen=True)
class Bond:
    """
    Class representing bonds in a molecule.

    Attributes:
    -----------
    type : str
        The bond type.
    atoms : tuple
        Indexes of the two atoms connected by this bond.
    """

    type: int
    atoms: tuple
