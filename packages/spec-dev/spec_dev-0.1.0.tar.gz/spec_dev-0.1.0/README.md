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

## Usage

After installing the package, run the CLI helper to copy the `.spec-dev` folder
into the current directory. The command overwrites existing files only when you
pass `--force`.

```bash
spec-dev            # copies into the current working directory
spec-dev path/to/project --force
```

From Python you can call the helper directly:

```python
from spec_dev import copy

copy("/path/to/project", overwrite=True)
```

The function returns the path to the copied `.spec-dev` directory.
