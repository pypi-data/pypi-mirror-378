# Hadeel

A simple Python package for defining search problems.

## Installation

```bash
pip install Hadeel
```

## Usage

```python
from Hadeel import SearchProblem

problem = SearchProblem("start", "goal")
print(problem.get_initial_state())  # start
print(problem.is_goal("goal"))      # True
```
