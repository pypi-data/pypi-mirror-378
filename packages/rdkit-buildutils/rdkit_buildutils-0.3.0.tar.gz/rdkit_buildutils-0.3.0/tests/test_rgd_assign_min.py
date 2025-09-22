from rdkit import Chem
from rdkit_buildutils.rgd_assign import assign_rgroups_for_matches, InMemoryUnknownAllocator

def test_assign_rgroups_minimal():
    monomers = {"Ser": "[R1]NCC(=O)[R2]"}
    target = Chem.MolFromSmiles("CC(C)(C)OC(=O)NCC(=O)OC")
    matches = [{
        "target_id": "t1",
        "monomer_symbol": "Ser",
        "structure_smiles": Chem.MolToSmiles(target, isomericSmiles=True),
    }]
    rgroups = [
        {"code": "BOC", "smiles": "-C(=O)OC(C)(C)C"},
        {"code": "OME", "smiles": "-OC"},
    ]
    out = assign_rgroups_for_matches(matches, monomers, rgroups, allocator=InMemoryUnknownAllocator())
    assert len(out) == 1
    a = out[0]
    codes = set(v for v in a.r_codes.values() if v)
    assert ("BOC" in codes) or ("OME" in codes)
    assert a.core_used is not None
    assert a.score is not None
