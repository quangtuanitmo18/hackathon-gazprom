# Task 1 verification evidence (2026-10-30)

**Scope:** Ingestion contracts, canonical ticket schema and provenance manifest only.

**Isolated run location:** /mnt/data/gazprom-task1 (ephemeral evaluation environment). The GitHub branch `feat/public-dataset-ingestion-task1` contains the same implementation and test source.

**RED:** before production modules existed, executed `PYTHONPATH=src python -m pytest tests/data/test_adapters.py tests/data/test_manifest.py -v`; exit code **2**, collection errors `ModuleNotFoundError: productpulse.data.adapters` and `...manifest`.

**GREEN:** after minimal implementation, executed the same command; **8 passed in 0.09s**. Follow-up `PYTHONPATH=src python -m pytest tests/ -q` returned **8 passed in 0.03s**. Python was 3.13.5, pytest 9.0.2.

**Covered:** join labels by stable ID rather than row order, mismatched labels, blank and duplicate IDs, missing vs naive timezone timestamps, SHA-256 provenance and nonexistent files.

**Important limitations:** no real Zenodo or Mendeley source was downloaded or profiled, and the CSV field mappings are provisional until checked against the actual source release. No live APIs or Gazprom Neft data used. No ML benchmark or business outcome measured.

**Pending next checks:** verify original dataset archive schema, real license metadata, download SHA-256, schema mapping and anonymization before task 2. The local CLI cannot reach GitHub directly; files were published using the connected GitHub API after local tests.

**Ruling:** use standard-library dataclass instead of Pydantic for this offline minimal schema; reduces dependencies. Replace or validate against Pydantic at the API boundary if the team chooses FastAPI.
