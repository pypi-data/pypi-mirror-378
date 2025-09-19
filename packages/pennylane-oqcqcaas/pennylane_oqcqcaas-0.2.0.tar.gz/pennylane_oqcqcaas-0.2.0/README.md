# pennylane-oqc
PennyLane plugin for OQC QCaaS devices

## Build and Install

```
poetry build
```

## Developer Setup

```
poetry install
```

### Test Runs

Note tests look for `.env` file from which to source these env variables that are required for the plugin.
Suggest placing this file in the root of the test directory.

* "OQC_URL"
* "OQC_DEVICE"
* "OQC_AUTH_TOKEN"

```
poetry run python -m pytest
```
