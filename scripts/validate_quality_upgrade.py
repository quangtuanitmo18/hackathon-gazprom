#!/usr/bin/env python3
"""Reproducible *design* regressions, not claims of observed model success."""
from __future__ import annotations
import json
import math
from pathlib import Path

root=Path(__file__).resolve().parents[1]
main=(root/"submissions/main-solution.ru.md").read_text(encoding="utf-8")
metrics=(root/"submissions/05-effect-metrics.ru.md").read_text(encoding="utf-8")
fin=(root/"docs/business/financial-assumptions.md").read_text(encoding="utf-8")
slides=(root/"submissions/presentation-outline.ru.md").read_text(encoding="utf-8")
plan=(root/"docs/evaluation/paired-baseline-benchmark.ru.md").read_text(encoding="utf-8")
scenario=json.loads((root/"docs/business/scenario-inputs.json").read_text(encoding="utf-8"))

assert len(main)<=15000, f"main over limit: {len(main)}"
assert all(x in main for x in ("1 532 277", "1 603 331", "Wilson", "BM25"))
assert all(x in metrics for x in ("246", "Wilson", "BM25", "включая не просмотренные"))
assert all(x in slides for x in ("14%", "6,35%", "Wilson", "BM25"))
assert all(x in fin for x in ("14,00%", "6,35%", "5,04%", "1 532 277", "1 603 331"))
assert "Вебнефть" in main and "не" in main

base=next(x for x in scenario["scenarios"] if x["id"]=="base")
b=base["expected_gross_annual_rub"]*base["realizable_fraction"]
for inp_r,inp_g,value in [(0.10,0.00,1641322),(0.14,0.00,1532277),(0.14,0.05,1603331)]:
    pv=sum(b*((1+inp_g)**(year-1))/(1+inp_r)**year for year in (1,2,3))
    assert round(pv)==value, (inp_r,inp_g,pv)
    assert any(x["nominal_discount_rate"]==inp_r and x["nominal_hourly_value_growth"]==inp_g and x["expected_rub"]==value for x in scenario["sensitivity"]["expected_pv_base_rub"])

def wilson_lcb(successes:int,n:int,z:float=1.96)->float:
    p=successes/n
    return (p+z*z/(2*n)-z*math.sqrt(p*(1-p)/n+z*z/(4*n*n)))/(1+z*z/n)

assert math.ceil(1.96**2*0.8*0.2/0.05**2)==246
assert round(wilson_lcb(200,250),3)==0.746
assert round(wilson_lcb(213,250),3)==0.803
assert wilson_lcb(200,250)<0.8<wilson_lcb(213,250)
for term in ("A —", "B —", "C —", "95%", "false-merge", "NOT VERIFIED"):
    assert term in plan, term
print("PASS: quality upgrade regressions —",len(main),"main chars; 3 PV scenarios; Wilson examples; A/B/C protocol")
