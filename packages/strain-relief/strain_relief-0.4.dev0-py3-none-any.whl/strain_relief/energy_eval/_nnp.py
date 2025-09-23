import tempfile
from typing import Literal

import ase
from loguru import logger as logging
from rdkit import Chem

from strain_relief.calculators import CALCULATORS_DICT
from strain_relief.constants import EV_TO_KCAL_PER_MOL, HARTREE_TO_KCAL_PER_MOL
from strain_relief.io import rdkit_to_ase
from strain_relief.io.utils_s3 import copy_from_s3


def NNP_energy(
    mols: dict[str : Chem.Mol],
    method: Literal["MACE", "FAIRChem"],
    calculator_kwargs: dict,
    model_paths: str,
    energy_units: Literal["eV", "Hartrees", "kcal/mol"] = "eV",
) -> dict[dict]:
    """Calculate the NNP energy for all conformers of all molecules.

    Parameters
    ----------
    mols : dict[str:Chem.Mol]
        A dictionary of molecules.
    method : Literal["MACE", "FAIRChem"]
        The NNP to use for energy calculation.
    calculator_kwargs : dict
        Additional keyword arguments to pass to the NNP calculator.
        For example, for MACE, this should include `model_path`, `device` and `default_dtype`.
    model_paths : str
        Path to the NNP model to use for energy calculation.
    energy_units : Literal["eV", "Hartrees", "kcal/mol"]
        The units output from the energy calculation.

    Returns
    -------
    dict[str: dict[int: float]]
        A dictionary of dictionaries of conformer energies for each molecule.

        mol_energies = {
            "mol_id": {
                "conf_id": energy
            }
        }
    """
    # Check if model_paths is an S3 path and copy to local if so
    if model_paths.startswith("s3://"):
        local_path = tempfile.mktemp(suffix=".model")
        copy_from_s3(model_paths, local_path)
        model_paths = local_path

    # Set up conversion factor based on energy units
    if energy_units == "eV":
        conversion_factor = EV_TO_KCAL_PER_MOL
        logging.info(f"{method} model outputs energies in eV. Converting to kcal/mol.")
    elif energy_units == "Hartrees":
        conversion_factor = HARTREE_TO_KCAL_PER_MOL
        logging.info(f"{method} model outputs energies in Hartrees. Converting to kcal/mol.")
    elif energy_units == "kcal/mol":
        conversion_factor = 1
        logging.info(f"{method} model outputs energies in kcal/mol. No conversion needed.")

    # Initialise the calculator
    if method not in CALCULATORS_DICT:
        raise ValueError(f"method must be in {CALCULATORS_DICT.keys()}")
    calculator = CALCULATORS_DICT[method](**calculator_kwargs)

    # Calculate energies for each molecule
    mol_energies = {}
    for id, mol in mols.items():
        mol_energies[id] = _NNP_energy(mol, id, calculator, conversion_factor)
    return mol_energies


def _NNP_energy(
    mol: Chem.Mol,
    id: str,
    calculator: ase.calculators,
    conversion_factor: float,
) -> dict[int:float]:
    """Calculate the NNP energy for all conformers of a molecule.

    Parameters
    ----------
    mol : Chem.Mol
        A molecule.
    id : str
        ID of the molecule. Used for logging
    calculator : ase.calculators
        The ASE calculator to use for energy calculation.
    conversion_factor : float
        The conversion factor to use for energy calculation.

    Returns
    -------
    dict[int: float]
        A dictionary of conformer energies.

        conf_energies = {
            "conf_id": energy
        }
    """
    confs_and_ids = rdkit_to_ase(mol)
    for _, atoms in confs_and_ids:
        atoms.calc = calculator
    conf_energies = {
        conf_id: atoms.get_potential_energy() * conversion_factor
        for conf_id, atoms in confs_and_ids
    }
    for conf_id, energy in conf_energies.items():
        logging.debug(f"{id}: Minimised conformer {conf_id} energy = {energy} kcal/mol")

    return conf_energies
