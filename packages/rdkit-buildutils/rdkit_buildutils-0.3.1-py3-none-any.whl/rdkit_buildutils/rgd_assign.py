from __future__ import annotations
from typing import Dict, List, Tuple, Optional, Iterable
from dataclasses import dataclass
from rdkit import Chem
from rdkit.Chem import rdRGroupDecomposition as RGD, rdMolDescriptors as Descr
import re
from .rgroup_core import to_core as _to_core, normalize_rgroup_smiles, to_peptidic_scaffold
from .datatypes import RAssignment

class UnknownCodeAllocator:
    def get_or_create(self, smiles_anchored: str) -> str:
        raise NotImplementedError

class InMemoryUnknownAllocator(UnknownCodeAllocator):
    def __init__(self, start_from: int = 1):
        self.map: Dict[str,str]={}
        self.n=start_from
    def get_or_create(self, smiles_anchored: str) -> str:
        if smiles_anchored in self.map: return self.map[smiles_anchored]
        code=f"RX{self.n:05d}"; self.map[smiles_anchored]=code; self.n+=1; return code

def _site_atom_symbol(core_mol: Chem.Mol | None, r_label: str) -> Optional[str]:
    if core_mol is None: return None
    try: n=int(r_label[1:])
    except Exception: return None
    for a in core_mol.GetAtoms():
        if a.GetAtomicNum()==0 and a.GetAtomMapNum()==n:
            nbr=list(a.GetNeighbors()); return nbr[0].GetSymbol() if nbr else None
    return None

def _map_with_site(frag_smi: str | None, site_symbol: str | None, code_map: Dict[str,str]) -> Optional[str]:
    if not frag_smi: return None
    if frag_smi in code_map: return code_map[frag_smi]
    if site_symbol in ('O','S') and frag_smi.startswith('*'):
        tail=frag_smi[1:]; cand=f"*{site_symbol}{tail}"
        if cand in code_map: return code_map[cand]
    return None

_R_PLACEHOLDER = re.compile(r'\[R(\d+)\]')

def _cleanup_dash_string(s: str) -> str | None:
    s=(s or "").strip()
    if not s: return None
    s=re.sub(r'\s+','',s)
    s=re.sub(r'-{2,}','-',s)
    return s or None

def _to_anchored_smiles(raw: str | None) -> str | None:
    if not isinstance(raw,str): return None
    s=_cleanup_dash_string(raw)
    if not s: return None
    if _R_PLACEHOLDER.search(s):
        return None
    if '*' in s:
        m=Chem.MolFromSmiles(s)
        if not m: return None
        for a in m.GetAtoms():
            if a.GetAtomicNum()==0: a.SetAtomMapNum(0)
        smi=Chem.MolToSmiles(m, canonical=True)
        return re.sub(r'\[\*\:(\d+)\]','[*]',smi)
    left=s.startswith('-'); right=s.endswith('-'); core=s.lstrip('-').rstrip('-')
    if not core: return None
    candidate = f"*{core}*" if (left and right) else (f"*{core}" if left else (f"{core}*" if right else f"*{core}"))
    m=Chem.MolFromSmiles(candidate) or Chem.MolFromSmiles(f"*{core}")
    if not m: return None
    for a in m.GetAtoms():
        if a.GetAtomicNum()==0: a.SetAtomMapNum(0)
    smi=Chem.MolToSmiles(m, canonical=True)
    return re.sub(r'\[\*\:(\d+)\]','[*]',smi)

def build_code_map(rgroups: Iterable[Dict[str,str]], code_key='code', smiles_key='smiles') -> Dict[str,str]:
    cmap={}
    for r in rgroups:
        code=(r.get(code_key) or '').strip()
        raw = r.get(smiles_key)
        if not code: continue
        smi=_to_anchored_smiles(raw)
        if smi: cmap.setdefault(smi, code)
    return cmap

def _mw(m: Optional[Chem.Mol]) -> float:
    return float(Descr.CalcExactMolWt(m)) if m is not None else 0.0

def _row_mass_gap(row: Dict[str, Chem.Mol], mol: Chem.Mol) -> float:
    return abs(_mw(mol) - (_mw(row.get('Core')) + sum(_mw(v) for k,v in row.items() if k.startswith('R') and v is not None)))

def _score_row(row: Dict[str, Chem.Mol], code_map: Dict[str,str], core_mol: Chem.Mol) -> tuple[int,int,float,int]:
    known=total=unknowns=0
    for k,frag in row.items():
        if not k.startswith('R'): continue
        total+=1
        if frag is None: continue
        frag_smi = normalize_rgroup_smiles(frag)
        site = _site_atom_symbol(core_mol, k)
        code = _map_with_site(frag_smi, site, code_map) if frag_smi else None
        known += 1 if code is not None else 0
        unknowns += 0 if code is not None else 1
    return (known, total, 0.0, unknowns)

def best_rgd_row_with_scoring(core_entries: List[tuple[str, Chem.Mol, str]],
                              mol: Chem.Mol,
                              code_map: Dict[str,str]):
    params=RGD.RGroupDecompositionParameters()
    params.removeHydrogensPostMatch=True
    params.alignment=RGD.RGroupCoreAlignment.MCS
    best=(None,None,None,(-1,-1,1e9,1e9))
    for core_smi, core, origin in core_entries:
        if core is None: continue
        rgd=RGD.RGroupDecomposition(core, params)
        try:
            rgd.Add(mol); rgd.Process()
        except Exception:
            continue
        rows=rgd.GetRGroupsAsRows()
        if not rows: continue
        row=rows[0]
        known,total,_,unknowns = _score_row(row, code_map, core)
        mgap=_row_mass_gap(row, mol)
        score=(known,total,mgap,unknowns)
        bk,bt,bmg,bu = best[3]
        replace=False
        if (known,total)>(bk,bt): replace=True
        elif (known,total)==(bk,bt):
            if mgap<bmg-1e-6: replace=True
            elif abs(mgap-bmg)<=1e-6 and unknowns<bu: replace=True
        if replace: best=(row, core_smi, origin, score)
    return best

def assign_rgroups_for_matches(matches: Iterable[Dict],
                               monomer_scaffolds: Dict[str,str],
                               rgroups_table: Iterable[Dict[str,str]],
                               allocator: UnknownCodeAllocator | None = None,
                               alt_cores: Dict[str, List[str]] | None = None) -> List[RAssignment]:
    code_map=build_code_map(rgroups_table)
    allocator = allocator or InMemoryUnknownAllocator()
    out: List[RAssignment]=[]
    for rec in matches:
        tid=str(rec["target_id"])
        symbol=rec.get("monomer_symbol")
        smi=rec["structure_smiles"]
        mol=Chem.MolFromSmiles(smi) if smi else None
        if mol is None:
            out.append(RAssignment(tid, symbol, {}, None, None)); continue
        asis=monomer_scaffolds.get(symbol or "")
        if not asis:
            out.append(RAssignment(tid, symbol, {}, None, None)); continue
        pep=to_peptidic_scaffold(asis)
        cores=[(asis, _to_core(asis), "as-is"), (pep, _to_core(pep), "peptidic")]
        if alt_cores and symbol in alt_cores:
            for i,alt in enumerate(alt_cores[symbol], start=1):
                cores.append((alt, _to_core(alt), f"alt#{i}"))
        row, core_used, origin, score = best_rgd_row_with_scoring(cores, mol, code_map)
        r_codes={}
        if row is not None:
            core_mol = _to_core(core_used) if core_used else None
            for i in (1,2,3,4,5):
                label=f"R{i}"
                frag=row.get(label)
                if frag is None:
                    r_codes[label]=None; continue
                frag_smi=normalize_rgroup_smiles(frag)
                site = _site_atom_symbol(core_mol, label) if core_mol else None
                code = _map_with_site(frag_smi, site, code_map) if frag_smi else None
                if code is None and frag_smi:
                    code = allocator.get_or_create(frag_smi)
                r_codes[label]=code
            core_used = Chem.MolToSmiles(core_mol, canonical=True) if core_mol else core_used
        out.append(RAssignment(tid, symbol, r_codes, core_used, score))
    return out
