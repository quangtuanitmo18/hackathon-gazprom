"""Probe English-vs-Russian default pain point categories in pinned Rereflect.

Only synthetic test sentences. No network, no imports from optional LLM stack.
No statistical language evaluation claims.
"""
from __future__ import annotations
import importlib.util, json
from pathlib import Path
from datetime import datetime, timezone

path=Path("upstream/services/analysis-engine/src/analyzer/categorizer.py")
spec=importlib.util.spec_from_file_location("rereflect_categorizer_probe",path)
if spec is None or spec.loader is None: raise RuntimeError("cannot import source module")
import sys
module=importlib.util.module_from_spec(spec)
sys.modules[spec.name]=module
spec.loader.exec_module(module)
model=module.PainPointCategorizer()
examples=[
("en_auth","I cannot login to my account"),
("ru_auth","Не могу войти в аккаунт"),
("en_slowness","The app is slow and freezes constantly"),
("ru_slowness","Приложение тормозит и постоянно зависает"),
("en_data","My data is lost after the update"),
("ru_data","После обновления пропали все данные"),
]
results=[]
for label,t in examples:
    v=model.categorize(t)
    results.append({"fixture":label,"category":v.category,"severity":v.level,
                    "confidence":v.confidence})
    print(label+": "+v.category+" ("+v.level+")")
target=Path("docs/spikes/evidence/rereflect-language.json")
target.parent.mkdir(parents=True,exist_ok=True)
target.write_text(json.dumps({
    "generated_utc":datetime.now(timezone.utc).isoformat(),
    "upstream_commit":"987dd9f0611c693524ec0cfba880517fa4d5ec57",
    "method":"single synthetic en/ru pairs through default PainPointCategorizer",
    "results":results,
    "disclaimer":"Tiny synthetic smoke samples; not a real Russian accuracy benchmark."
},indent=2)+"\n")
