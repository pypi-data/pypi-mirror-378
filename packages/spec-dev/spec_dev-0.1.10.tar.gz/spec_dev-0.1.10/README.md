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
# Initialise a project (default destination is the current directory)
spec-dev init
spec-dev init path/to/app
spec-dev init --force                  # overwrite an existing .spec-dev folder

# Create a task memory scaffold from the bundled template
spec-dev memory T-123

# Archive the current cycle and reset active templates
spec-dev cycle --label fal-ai-image-gen
```

Run `spec-dev --help` for the full command list and examples.

## Python API

```python
from spec_dev import copy, create_memory, complete_cycle

root = copy("/path/to/project", overwrite=True)
memory = create_memory("T-123", root)
archive = complete_cycle(root, label="fal-ai-image-gen")
```

Each helper returns the `Path` it creates (the `.spec-dev` directory, the new
memory file, or the archived history folder).

## Workflow Primer

The bundled instructions under `.spec-dev/*.md` walk you through the
Specify → Plan → Tasks → Implementation phases. Highlights:

- `.spec-dev/templates/active/` contains fresh templates for each phase, ready
  to copy into `.spec-dev/active-dev/`.
- Task memories live under `.spec-dev/active-memories/`; use
  `spec-dev memory T-XXX` to scaffold an entry and capture why/what/how plus
  validation evidence.
- After delivering a cycle, run `spec-dev cycle [--label <name>]` to move the
  finished spec/plan/tasks/implementation log into `.spec-dev/history/` and reset
  `active-dev/` with clean templates for the next iteration.
