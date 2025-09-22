from __future__ import annotations

# Version
__version__ = "0.3.1"

# Public API re-exports (back-compat)
from .core import convert_r_to_atom_map, build_molecule_final
from .rgroup_core import (
    to_core, normalize_rgroup_smiles, to_peptidic_scaffold,
    anchored_smiles, build_code_map, decompose_with_cores, decompose_for_monomer,
)
from .scaffold_normalize import (
    canonical_ranks, r_to_atommap, relabel_dummies_canonically, normalize_scaffold_chiral,
)

# New modules (v0.3)
from .logging_utils import silence_rdkit, silence_rdkit_all
from .standardize import standardize_for_matching
from .helm import helm_to_query_mol
from .query_variants import make_scaffold_variants
from .rgroup_extract import extract_rgroup_smiles
from .filters import is_aminoacid_like_scaffold, keep_targets_with_single_aa_core
from .matching import prepare_targets, find_monomer_matches
from .rgd_assign import (
    UnknownCodeAllocator, InMemoryUnknownAllocator,
    build_code_map as build_code_map_from_table,
    assign_rgroups_for_matches,
)
from .datatypes import MonomerScaffold, MatchRecord, RAssignment

__all__ = [
    # v0.2
    "convert_r_to_atom_map", "build_molecule_final",
    "to_core", "normalize_rgroup_smiles", "to_peptidic_scaffold",
    "anchored_smiles", "build_code_map", "decompose_with_cores", "decompose_for_monomer",
    "canonical_ranks", "r_to_atommap", "relabel_dummies_canonically", "normalize_scaffold_chiral",
    # v0.3 new
    "silence_rdkit", "silence_rdkit_all", "standardize_for_matching",
    "helm_to_query_mol", "make_scaffold_variants", "extract_rgroup_smiles",
    "is_aminoacid_like_scaffold", "keep_targets_with_single_aa_core",
    "prepare_targets", "find_monomer_matches",
    "UnknownCodeAllocator", "InMemoryUnknownAllocator",
    "build_code_map_from_table", "assign_rgroups_for_matches",
    "MonomerScaffold", "MatchRecord", "RAssignment",
]
