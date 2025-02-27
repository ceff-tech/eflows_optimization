# Belleflopt - An Environmental Flows Optimization Platform
A tool to allocate unimpaired flows optimally for environmental purposes. Developed for Python 3.6 and Django 2.1.

Build and Testing Status: [![Build Status](https://dev.azure.com/nickrsantos/belleflopt/_apis/build/status/ceff-tech.belleflopt?branchName=master)](https://dev.azure.com/nickrsantos/belleflopt/_build/latest?definitionId=2&branchName=master)

## What's with the name?
It's prounounced like "belly flopped", and can be broken down as:
* _bell_ - just a support for the rest of it
* _e_ - "environment"
* _flo_ - "flow"
* _opt_ - "optimization"

And belly flops are a silly thing that happens in water sometimes. This codebase uses an
evolutionary algorithm to find optimal environmental flow and economic tradeoffs,
so it might perform a few bellyflops of its own.

## Setup
To use, first rename `eflows_optimization/local_settings_template.py` to
`eflows_optimization/local_settings.py`. Inside that file, change the value
of `SECRET_KEY` to a cryptographically secure value.

Next, install dependencies:
```
python -m pip install -r requirements.txt
```

Then set up the database. First, create it,

```
python manage.py migrate
python manage.py shell 
```

## Running the prototype
In the shell, run the following to load species, watershed, and flow data and set up the
hydrologic network
```python
from belleflopt import load
load.load_fresh()
```

If you want to actually run optimization now, you can then:
```python
from belleflopt import support
support.run_optimize()
```

That function's signature looks like the following:
```
"""
    Runs a single optimization run, defaulting to 1000 NFE using NSGAII. Won't output plots to screen
    by default. Outputs tables and figures to the data/results folder.
	:param algorithm: a platypus Algorithm object (not the instance, but the actual item imported from platypus)
						defaults to NSGAII.
	:param NFE: How many times should the objective function be run?
	:param popsize: The size of hte population to use
	:param seed: Random seed to start
	:param show_plots: Whether plots should be output to the screen
	:return: None
	"""
```

If you want to take a look at the optimization innards, they're in
`eflows.optimize` as a subclass of Platypus's `Problem` class.

Currently, there is no web component to this project, despite being
developed in Django. That's just futureproofing - it's all console
access now. Unittests are available for data loading functions, but
not for other functionality.

If you want to do some testing, you can use `support.run_optimize_many()` (takes no
arguments - tweak the code if you want it to be different) or use Platypus' Experimenter class.
Note that currently, due to the way the model is constructed, you can't use parallel
expirementers - the database will lock and prevent multiple accesses.

## Extension Points
The codebase is being designed to be a reusable package that encompasses as much as
possible, to allow for this code to be a research platform that encourages exploration of outcomes
as opposed to something that runs once and gives an answer. To extend or change behavior, there
are two major locations as of this writing:
1. Changing the settings. In `local_settings.py`, defaults are set that determine how belleflopt
loads and processes data for flow metrics and components. Changing these values would alter
results and can be used to explore different scenarios, especially when paired with input
data for different objectives or geographies.
2. Providing different functions for base benefit calculation and loading. Belleflopt establishes
surfaces that it uses to determine the benefit of a given flow of water on a given date
for a given segment. It handles this with `BenefitBox` objects located in `benefit.py`, but you
can create your own benefit class. These classes are paired with a function (located in
`flow_components.py` that attaches them to belleflopt's core data structures. When initializing
belleflopt's components, you can build a different function that extracts values from belleflopt's
data structures and builds your own `BenefitBox`-like class. That class must have a method
`single_flow_benefit(self, flow, day_of_year)` that returns the base benefit of that flow on that
day of the water year for that stream segment - at least in order to run the model. For full
compatibility, copying the other interfaces of `BenefitBox` is advised.

This "base benefit" is then used in conjunction with present species (those who stand to benefit
from it) in establishing the total benefit of a given flow/day/segment. More documentation
on extension points will be forthcoming as the package is fleshed out further.

## Model Runs
Model runs are handled in unit tests. While the main `eflows.tests` package holds standard
unit tests, the `eflows.tests.model_runs` package is special in that each test class in a file
in that package describes a discrete model run. Upon each commit, these runs will be re-evaluated
with results uploaded to comet.ml so that performance of the results can be tracked over time,
even as the code changes, allowing us to see if a model run that previously performed poorly is
better after certain bugfixes, etc.

The actual utilization of the model_runs package is not yet determined, but will be included here.
 
## Results
Sample results are included below:
![Sample Results](maps/maps_layout.png)

## Performance
This model is slow right now, sorry. It's built into Django, which makes data management
and network traversal nice, but also slows everything down and prevents parallelization
while using a SQLite backend. One function evaluation takes about a second or more on
modest hardware, so plan accordingly. Most runs converged in less than 4000 NFE, but
it's possible you'd want to go further for testing.