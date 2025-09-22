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
spec-dev memory T-123       # scaffold .spec-dev/active-memories/T-123-memory.md
# template lives at .spec-dev/templates/memories/task-memory-template.md
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

## Templates

All starter files live under `.spec-dev/templates/`. Use `templates/active/` for
phase artifacts (copy into `.spec-dev/active-dev/` and rename), and `templates/memories/`
for archival notes. Fill templates out before advancing gates; refer to the included
example for memory expectations.
Task memories live under `.spec-dev/active-memories/` and follow a lightweight playbook—why it mattered, what changed, how it shipped, validation, artifacts, ripple effects, and any lessons learned—trim sections that do not apply.
