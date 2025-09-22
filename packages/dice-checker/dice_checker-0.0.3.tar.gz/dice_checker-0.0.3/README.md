# dice-checker

[![Release](https://img.shields.io/github/v/release/rguillon/dice-checker)](https://img.shields.io/github/v/release/rguillon/dice-checker)
[![Build status](https://img.shields.io/github/actions/workflow/status/rguillon/dice-checker/ci.yml?branch=main)](https://github.com/rguillon/dice-checker/actions/workflows/ci.yml?query=branch%3Amain)
[![codecov](https://codecov.io/gh/rguillon/dice-checker/branch/main/graph/badge.svg)](https://codecov.io/gh/rguillon/dice-checker)
[![Commit activity](https://img.shields.io/github/commit-activity/m/rguillon/dice-checker)](https://img.shields.io/github/commit-activity/m/rguillon/dice-checker)
[![License](https://img.shields.io/github/license/rguillon/dice-checker)](https://img.shields.io/github/license/rguillon/dice-checker)

A simple library to compute probabilities with dice rolls.


Dice objects can be created from a simple RPG-like string expression:

```python

from dice_checker import Dice

Dice("D6")          # One 6 faced dice
Dice("2D8+1")       # Two 8 faces dices plus 1
Dice("5D10-1D6-1")  # Five 10 sided dices minus one 6 sided dice minus 1
Dice("1")           # A constant value of 1

```

Dices can also be build from a custom map of value/probability

```python

from dice_checker import Dice

# Using a 6 faces dice where 1 to 4 gives 0 points, a 5 gives 1 point, a 6 gives 2 points
dice = Dice({0:4, 1:1, 2:1})


```


And Dices can be built on the fly

```python

from dice_checker import Dice

dice = Dice()

dice.add_event(event=1, probability=1)
dice.add_event(event=2, probability=1)

```

Dices have attributes:
* `distribution` returns a map of value/chances.
* `expected_value` returns the average value of the roll.

```python

>>> from dice_checker import Dice
>>> roll = Dice("2D6+1")
>>> print(roll.distribution)
{3.0: 1.0, 4.0: 2.0, 5.0: 3.0, 6.0: 4.0, 7.0: 5.0, 8.0: 6.0, 9.0: 5.0, 10.0: 4.0, 11.0: 3.0, 12.0: 2.0, 13.0: 1.0}
>>> print(roll.expected_value)
8.0

```

Dices can be added and subtracted

```python

>>> from dice_checker import Dice
>>> assert Dice("3D6") == Dice("2D6") +Dice("1D6")
>>> assert Dice("2D6-D6") == Dice("2D6") - Dice("1D6")

```

And Dices implement comparison operators that will return the probability of the True/False events:


```python

>>> from dice_checker import Dice
>>> (Dice("1D10") >= Dice("1D6")).distribution
{1.0: 45.0, 0.0: 15.0}

>>> (Dice("2D6") < Dice("2D6")).distribution
{0.0: 721.0, 1.0: 575.0}

```
