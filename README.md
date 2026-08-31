# zlocket-nyan

`zlocket-nyan` is a bounded, offline simulator for the workflow found in the
historical zLocket source. The current build is intended for refactoring,
contract testing, and future integration with an authorized staging
environment.

It does **not** connect to Locket, Firebase, Thanh Dieu's token service, proxy
providers, or any other external host.

## Requirements
    
- Python 3.12 or newer
- No third-party runtime dependencies

Creating an isolated environment is still recommended:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

## Run

The default execution is an offline dry-run:

```powershell
python locket.py --dry-run
```

Simulate two accounts, three requests per account, and two workers:

```powershell
python locket.py --dry-run --accounts 2 --repeat 3 --threads 2 --target owned_test_uid
```

The historical `51`-request behavior can be exercised entirely in memory:

```powershell
python locket.py --dry-run --accounts 1 --repeat 51 --threads 1
```

Machine-readable summary:

```powershell
python locket.py --dry-run --json
```

## Test

```powershell
python -m unittest discover -s tests -v
```

The test suite includes a network guard assertion and bounded workflow checks.

## Architecture

```text
CLI
 `- WorkflowRunner
     |- AppCheckProvider
     |- AuthAdapter
     `- LocketApiAdapter
```

Only mock implementations are included. A future staging adapter must use a
Firebase project and API environment controlled by the developer, keep secrets
outside Git, verify TLS, apply explicit request limits, and provide cleanup for
test data.

## Historical source

The original implementation remains available in Git history before version
`2.0.0`. It is not kept as an executable entrypoint because it depended on a
retired third-party token broker, disabled TLS verification, and performed
unbounded network actions.
