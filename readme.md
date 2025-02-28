# Greedy Tests

All test cases from the bachelors thesis "Greedy-kernel algorithms for data mapping in multiphysics simulations".

- Modified ASTE version:    https://github.com/FabioTucciarone/aste
- Modified preCICE version: https://github.com/FabioTucciarone/precice

## Folder structure

The default folder structure assumed is:
```
..
 |- aste
 |- greedy_tests
```
The ASTE path can be changed in the run.sh file of each test case.

## Running and showing a test

From the root folder ``greedy_tests`` run
```
./test/<test-name>/run.sh
./test/<test-name>/show.py
```
Each test has its own folder.
To show a specific plot from the thesis, run

```
./test/<test-name>/show.py <plot-name>
```
The ``<plot-name>`` is the name of the folder containing the test results, that is, ``/test/<test-name>/data/<plot-name>``

## A list of plots from the thesis:
```
./test/adaptive-f-greedy/show.py thesis-all-adaptive
./test/adaptive-f-greedy/show.py thesis-all-rbf
./test/adaptive-f-greedy/show.py thesis-removal-size

./test/cholesky-vs-cut/show.py thesis

./test/shape-param/show.py thesis

./test/polynomial/show.py thesis

./test/overview/show.py thesis
```