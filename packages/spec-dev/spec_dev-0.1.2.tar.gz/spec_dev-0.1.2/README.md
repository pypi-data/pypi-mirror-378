# spec-dev

A small helper package that bundles the `.spec-dev` workspace template so it can be
installed with `pip` and copied into new projects.

## Installation

```bash
pip install spec-dev
```

If you are working from the repository source, you can install it locally instead:

```bash
pip install .
```

## CLI Usage

```bash
spec-dev init               # copy .spec-dev into the current directory
spec-dev init path/to/app   # copy into a specific directory
spec-dev init --force       # overwrite an existing .spec-dev folder
spec-dev memory T-123       # scaffold .spec-dev/memories/T-123-memory.md
```

The CLI defaults to `init` when you omit the subcommand, so `spec-dev` keeps the
original behaviour.

## Python API

```python
from spec_dev import copy, create_memory

copy("/path/to/project", overwrite=True)
create_memory("T-123", "/path/to/project")
```

Both helpers return a `Path` to the created resources.
