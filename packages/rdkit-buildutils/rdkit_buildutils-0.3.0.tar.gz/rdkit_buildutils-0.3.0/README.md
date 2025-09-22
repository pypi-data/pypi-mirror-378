# rdkit_buildutils

Utilities built on top of [RDKit](https://www.rdkit.org/) for constructing, normalizing and decomposing molecules with placeholder substitution.

The package supports workflows involving **monomers**, **R-group decomposition**, **query matching**, and **scaffold normalization**. All helpers are **general-purpose** and RDKit-only.

> ⚠️ Developed in a personal context for scientific support. Not affiliated with RDKit or any specific organization.

---

## ✨ Features

### Core (`rdkit_buildutils/core.py`)
- `convert_r_to_atom_map(smiles_r)`: `[R1]` → `[*:1]`.
- `build_molecule_final(base_smiles, **substituents)`: substitute placeholders (`r1="CC"`, …).

### R-group (`rdkit_buildutils/rgroup_core.py`)
- `to_core`, `normalize_rgroup_smiles`, `to_peptidic_scaffold`.
- `anchored_smiles`, `build_code_map`.
- `decompose_with_cores`, `decompose_for_monomer`.

### Scaffold normalization (`rdkit_buildutils/scaffold_normalize.py`)
- `canonical_ranks`, `r_to_atommap`, `relabel_dummies_canonically`.
- `normalize_scaffold_chiral` (D/L preserving).

### New in **0.3**
- **Logging**: `silence_rdkit`, `silence_rdkit_all`
- **Standardization**: `standardize_for_matching`
- **HELM**: `helm_to_query_mol`
- **Query variants**: `make_scaffold_variants` (strict/nostereo/kekule/dropR/peptidic*)
- **R-group extraction**: `extract_rgroup_smiles`
- **Filters**: `is_aminoacid_like_scaffold`, `keep_targets_with_single_aa_core`
- **Matching**: `prepare_targets`, `find_monomer_matches`
- **RGD assign**: `assign_rgroups_for_matches`, `build_code_map_from_table`
- **Datatypes**: `MonomerScaffold`, `MatchRecord`, `RAssignment`

---

## 📦 Installation

```bash
# pip-only (uses rdkit-pypi)
pip install rdkit_buildutils
# or, if you install RDKit via conda-forge, install rdkit separately and then:
pip install rdkit_buildutils
```

Optional extras:
```bash
pip install rdkit_buildutils[pandas]   # pandas helpers
pip install rdkit_buildutils[db]       # adapters you may write externally
```

---

## 🔬 Examples

```python
from rdkit_buildutils import convert_r_to_atom_map, build_molecule_final
from rdkit import Chem

scaffold = "[R1]NCC(=O)[R2]"
core = convert_r_to_atom_map(scaffold)  # -> [*:1]NCC(=O)[*:2]
mol = build_molecule_final(core, r1="C", r2="OC")
print(Chem.MolToSmiles(mol))
```

R-group assignment with matching (sketch):
```python
from rdkit_buildutils import (
  helm_to_query_mol, MonomerScaffold, prepare_targets, find_monomer_matches,
  assign_rgroups_for_matches
)
# build MonomerScaffold list...
# prepare targets...
# matches = find_monomer_matches(...)
# assignments = assign_rgroups_for_matches(...)
```

---

## ✅ License
MIT © 2025 Fabio Nelli
