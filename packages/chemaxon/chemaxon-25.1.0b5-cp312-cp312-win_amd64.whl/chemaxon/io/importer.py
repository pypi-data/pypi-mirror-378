import ctypes

from .._isolate_handler import _cxn, _isolate_handler, _Opaque
from ..molecule import Molecule, _CMolecule, _init_mol
from .exporter import export_mol
from .._exception_util import _CExceptionData, _checkException


def _to_svg(mrv: str):
    """:meta private:"""
    cxn_mol = import_mol(mrv)
    return export_mol(cxn_mol, "svg:headless,nosource,w300")

def import_mol(mol: str, options: str = "") -> Molecule:
    """Molecule import

    You can find more information about file formats and options on the following link: https://docs.chemaxon.com/display/docs/formats_index.md

    Here you can find the supported formats: https://docs.chemaxon.com/display/docs/python-api_limitations.md

    Parameters
    ----------
    mol : `str`
       Input molecule string
    options : `str`
       This option is to specify the input format and options for the import
    Raises
    ------
    RuntimeError
        If the molecule contains more than 800 atoms / bonds
    Returns
    -------
    molecule : `Molecule`
       The imported molecule
    """
    thread = _isolate_handler.get_isolate_thread()

    _cxn.import_mol.restype = ctypes.c_void_p
    try:
        cmolecule = _CMolecule.from_address(_cxn.import_mol(thread, mol.encode("utf-8"), options.encode("utf-8")))
        molecule = _init_mol(_to_svg, cmolecule)
    finally:
        _cxn.free_import_mol_result(thread)
        _isolate_handler.cleanup_isolate_thread(thread)
    return molecule


class _CMolImporter(ctypes.Structure):
    """:meta private:"""
    _fields_ = [
        ("exception_data", ctypes.POINTER(_CExceptionData)),
        ("native_handle", ctypes.c_longlong)
    ]

class MolImporter:
    """Class for importing molecules from a file.
    More info about file formats and options: https://docs.chemaxon.com/display/docs/formats_index.md
    Here you can find the supported formats: https://docs.chemaxon.com/display/docs/python

    Attributes
    ----------
    _file_path: `str`
        For internal use only, path of the file to be imported
    _native_handle: `ctypes.c_longlong`
        For internal use only, native handle of the molecule importer

    """

    _file_path: str
    _native_handle: ctypes.c_longlong

    def __init__(self, file_path):
        self._file_path = file_path
        thread = _isolate_handler.get_isolate_thread()
        _cxn.open_mol_importer.argtypes = [ctypes.POINTER(_Opaque), ctypes.c_char_p]
        _cxn.open_mol_importer.restype = ctypes.c_void_p
        try:
            c_molecule_importer = _CMolImporter.from_address(
                _cxn.open_mol_importer(thread, self._file_path.encode("utf-8")))
            self._native_handle = c_molecule_importer.native_handle
            _checkException(c_molecule_importer)
        finally:
            _isolate_handler.cleanup_isolate_thread(thread)

    def _to_c_molimporter(self):
        """:meta private:"""
        c_molecule_importer = _CMolImporter()
        if (self._file_path is not None):
            c_molecule_importer.file_path = self._file_path.encode("utf-8")
        if self._native_handle is not None:
            c_molecule_importer.native_handle = self._native_handle
        return c_molecule_importer

    def read(self) -> Molecule:
        """Read next molecule with the importer. Doesn't need to be called if using iterator.

        Returns
        -------
        molecule : `Molecule` or `None`
            The next molecule in the file, or None if there are no more molecules.
        """
        thread = _isolate_handler.get_isolate_thread()
        _cxn.read_mol.argtypes = [ctypes.POINTER(_Opaque), ctypes.POINTER(_CMolImporter)]
        _cxn.read_mol.restype = ctypes.c_void_p
        try:
            c_molecule = _CMolecule.from_address(_cxn.read_mol(thread, ctypes.byref(self._to_c_molimporter())))
            next_molecule = _init_mol(_to_svg, cmolecule=c_molecule)
        finally:
            _cxn.free_read_molecule(thread)
            _isolate_handler.cleanup_isolate_thread(thread)
        return next_molecule

    def close(self):
        """Close the importer and free resources. Doesn't need to be called if using the context manager."""

        thread = _isolate_handler.get_isolate_thread()
        _cxn.close_mol_importer.argtypes = [ctypes.POINTER(_Opaque)]
        _cxn.close_mol_importer.restype = ctypes.c_void_p
        try:
            _cxn.close_mol_importer(thread)
        finally:
            _isolate_handler.cleanup_isolate_thread(thread)

    def __iter__(self):
        return self

    def __next__(self) -> Molecule:
        next_molecule = self.read()
        if next_molecule is None:
            raise StopIteration
        return next_molecule

    def __enter__(self):
        return self

    def __exit__(self, type, value, tb):
        self.close()

