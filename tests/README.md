# Tests

Planned coverage includes legal-ball counting, delivery ordering, innings segmentation, target construction, temporal feature leakage, bowler attribution rules, split isolation by match, probability bounds, and NWC reconciliation.

Phase 01 uses the standard-library test runner so the critical ingestion rules
can be checked before the project environment is locked:

```bash
PYTHONPATH=src python -m unittest discover -s tests -v
```
