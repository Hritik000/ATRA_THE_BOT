Act as a principal engineer reviewing the proposed ATRA changes.

Review:
- correctness
- architecture
- test coverage
- security
- leakage
- time-series validation
- error handling
- observability
- performance
- maintainability
- dependency bloat
- agent permissions
- reproducibility

For ML/backtesting inspect:
- chronological splits
- target alignment
- future-data access
- preprocessing leakage
- realistic cost assumptions
- dataset/model/strategy versioning

Return:
1. blocking issues
2. important issues
3. minor issues
4. missing tests
5. missing docs

Do not rewrite the project.
