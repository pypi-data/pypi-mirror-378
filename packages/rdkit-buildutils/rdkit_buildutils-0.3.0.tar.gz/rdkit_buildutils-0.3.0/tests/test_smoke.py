import rdkit_buildutils as r

def test_smoke_import():
    assert hasattr(r, "__version__")
    assert "build_molecule_final" in r.__all__
    assert "make_scaffold_variants" in r.__all__
    assert "standardize_for_matching" in r.__all__
