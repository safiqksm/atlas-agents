# Installation

## Supported Python versions

Use **Python 3.10 – 3.13**. Python **3.12** is recommended.

Python 3.14 and newer are **not** supported. Several dependencies, crewai in
particular, publish releases only for `Requires-Python <3.14` or `<3.15`.

## Quick setup (recommended)

This uses [uv](https://docs.astral.sh/uv/). If no Python 3.12 is installed, uv
downloads one for you.

```bash
# from the repo root
uv venv --python 3.12 .venv
uv pip install --python .venv/bin/python -r requirements.txt
source .venv/bin/activate
```

Check that the install works:

```bash
python --version          # Python 3.12.x
python -c "import crewai, langgraph, openai, anthropic, dspy, chromadb, mcp; print('ok')"
```

### Without uv

You need a Python 3.12 interpreter first (e.g. `brew install python@3.12`):

```bash
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Troubleshooting

### `Could not find a version that satisfies the requirement crewai>=0.80.0`

Symptom: `pip install -r requirements.txt` fails with a long list like:

```
ERROR: Ignored the following versions that require a different python version:
  ... 1.15.45 Requires-Python >=3.10,<3.14; ... 1.108.18 Requires-Python >=3.10,<3.15
ERROR: Could not find a version that satisfies the requirement crewai>=0.80.0
  (from versions: 0.1.0, ..., 0.11.2)
```

**Cause:** the virtual environment runs a Python that is too new (for example
Homebrew's default `python3`, which may be 3.15). pip skips every modern crewai
release because of its `Requires-Python` bound. That leaves only ancient 0.x
versions, and none of them meet `>=0.80.0`.

**Fix:**

1. Check which Python the venv uses:
   ```bash
   .venv/bin/python --version
   ```
2. If it's 3.14 or newer, delete the venv and recreate it on 3.12:
   ```bash
   rm -rf .venv
   uv venv --python 3.12 .venv
   uv pip install --python .venv/bin/python -r requirements.txt
   ```
3. Activate it and run the import check above:
   ```bash
   source .venv/bin/activate
   ```

**Notes:**

- uv installs its managed Python under `~/.local/share/uv/python/`. Your system
  and Homebrew Pythons stay as they are. `uv python list --only-installed`
  shows what's installed.
- Always **activate the venv** (or call `.venv/bin/python` directly). Outside
  the venv, a bare `python3` still points at your system default, which may be
  the unsupported version.
