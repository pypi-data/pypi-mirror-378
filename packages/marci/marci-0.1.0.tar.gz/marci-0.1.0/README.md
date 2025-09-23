# marci

Marci: Marketing Science utilities for campaign analysis and simulation

A comprehensive Python package for marketing campaign modeling, including elasticity curves, seasonality patterns, conversion delays, and campaign simulation tools.

## Installation

```bash
pip install marci
```

## Quickstart

```python
import pandas as pd
from marci import Campaign, Elasticity, Seasonality

# Create a campaign simulation
campaign = Campaign()
results = campaign.sim_outcomes()

# Analyze elasticity curves
elasticity = Elasticity(elasticity_coef=0.5, saturation_rate=0.8)
roas = elasticity.roas([0.5, 1.0, 1.5])

# Generate seasonal patterns
seasonality = Seasonality(seed=42)
values = seasonality.values(pd.date_range("2023-01-01", periods=365, freq="D"))
```

## Development

- Create and activate a virtual environment
- Install dev tools

```bash
python -m venv .venv
# Windows PowerShell
. .venv/Scripts/Activate.ps1

pip install -U pip build pytest
pip install -e .
pytest -q
```

## Release

1. Bump version in `src/marci/_version.py`
2. Commit and tag

```bash
git commit -am "chore: release v0.1.0"
git tag v0.1.0
```

3. Push tags to GitHub; the publish workflow will upload to PyPI when a release is created (or manually run the workflow).

Alternatively, publish locally:

```bash
python -m build
python -m twine upload dist/*
```

## License

MIT

