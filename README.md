#pybdsim#

A python package containing both utilities for preparing and analysing BDSIM input and output as well as controlling BDSIM.

## Authors ##

L. Nevay
A. Abramov
S. Boogert
W. Shields
J. Snuverink
S. Walker


## Setup ##

From within the pybdsim root directory:

$ make install

or for development:

$ make develop


```
#!python

$>python
$>>> import pybdsim
$>>> a = pybdsim.Data.Load("run1_output.txt")
$>>> import matplotlib.pyplot as plt
$>>> plt.hist(a.Xp())
```
