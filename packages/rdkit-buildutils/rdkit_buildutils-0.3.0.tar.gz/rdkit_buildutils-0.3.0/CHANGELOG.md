# Changelog
All notable changes to this project will be documented in this file.

## [0.3.0] - 2025-08-30
### Added
- New modules: `logging_utils`, `standardize`, `helm`, `query_variants`,
  `rgroup_extract`, `filters`, `matching`, `rgd_assign`, `datatypes`.
- High-level helpers to reproduce pipelines: filtering, matching variants,
  R-group decomposition & code assignment, site-aware mapping, unknown allocator.

### Changed
- `__init__` exposes a stable API for pipeline integration.
- README updated with new examples.

### Fixed
- More robust query variant generation and fragment normalization.

---

## [0.2.0] - 2025-08-21
### Added
- R-group decomposition utilities (`rgroup_core.py`): `to_core`, `normalize_rgroup_smiles`, `to_peptidic_scaffold`, `anchored_smiles`, `build_code_map`, `decompose_with_cores`, `decompose_for_monomer`.
- Scaffold normalization utilities (`scaffold_normalize.py`): `canonical_ranks`, `r_to_atommap`, `relabel_dummies_canonically`, `normalize_scaffold_chiral`.
- Duplicate detection with pandas (`duplicates_pandas.py`): `find_duplicate_monomers_chiral_df`.
- Optional extras: `[pandas]`, `[db]`.

### Changed
- Expanded README with examples.
- Updated `__init__.py` to expose new API.
- Improved packaging metadata in `pyproject.toml`.

### Fixed
- Deterministic relabeling of dummy atoms improves scaffold comparisons.

---

## [0.1.0] - 2025-06-01
### Added
- Initial release with `convert_r_to_atom_map` and `build_molecule_final`.
