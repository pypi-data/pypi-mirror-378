# Multiple Minimum Monte Carlo
[![pypi](https://img.shields.io/pypi/v/multiple-minimum-monte-carlo.svg)](https://pypi.python.org/pypi/multiple-minimum-monte-carlo)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/charliermarsh/ruff/main/assets/badge/v1.json)](https://github.com/charliermarsh/ruff)

This package will help you perform a multiple minumum Monte Carlo conformer search as described in [Chang et al., 1989](https://doi.org/10.1021/ja00194a035). It is built to be used with an ASE calculator and ASE optimization tools but user-defined optimization strategies can be employed as well.

### Installation

This package can be installed with pip

```bash
pip install multiple-minimum-monte-carlo
```

### Tutorial

To run a search, you need to initialize Conformer, Calculation, and ConformerEnsemble objects. Conformer objects require either an input xyz or SMILES string. The default Calculation object is ASEOptimization which requires an ASE optimization routine (like FIRE) and an ASE calculator (the example below uses the xtb calculator which will need to be installed separately from this package). ConformerEnsemble objects require a Conformer and Calculation object.

```python
from ase.optimize.fire import FIRE
from ase.io import write
from xtb.ase.calculator import XTB
from multiple_minimum_monte_carlo.conformer import Conformer
from multiple_minimum_monte_carlo.calculation import ASEOptimization
from multiple_minimum_monte_carlo.conformer_ensemble import ConformerEnsemble

smiles = "CC(=O)Oc1ccccc1C(=O)O"
conformer = Conformer(smiles=smiles)
optimizer = ASEOptimization(calc=XTB(method="gfn2-xtb"), optimizer=FIRE)
conformer_ensemble = ConformerEnsemble(conformer=conformer, calc=optimizer)
```

To run the search, call run_monte_carlo with the ConformerEnsemble object

```python
final_ensemble = conformer_ensemble.run_monte_carlo()
```

final_ensemble will be a list of coordinate arrays that arranged by their energy (lowest energy first). To read out the minimum energy compound, do this

```python
from ase.io import write
conformer.atoms.set_positions(final_ensemble[0])
write("lowest_energy_conformer.xyz", conformer.atoms, format="xyz")
```

### User-Defined Calculation

To define a Calculation object, a class will need three function: init, run, and energy. init initializes the class with whatever information is necessary. run performs an optimization. It takes an ase.Atoms object and a list of atoms to constrain and returns an np array of cartesian coordinates (in angstroms) and a float with the energy of the conformation (in kcal/mol). energy calculates the energy of a conformer. It takes an ase.Atoms object and returns a float the with energy (in kcal/mol)

### Planned future work

Include support for batched optimization 