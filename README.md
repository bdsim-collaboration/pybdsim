#pyBDSIM#

A python package containing both utilities for preparing and analysing BDSIM input and output as well as controlling BDSIM.

## Authors ##

L. Nevay
S. Boogert

## Setup ##
The module currently requires no setup and can be used by adding the pybdsim directory to your python path.

-> edit your terminal (perhaps bash) profile


```
#!csh

$PYTHONPATH=$PYTHONPATH:/path/to/where/you/put/pybdsim

```


```
#!python

$>python
$>>> import pybdsim
$>>> a = pybdsim.Data.Load("run1_output.txt")
$>>> hist(a.Xp())
```

# Dependencies #
Where possible, all attempt has been made to only use built in python types.  However, matplotlib is required for plotting.  Numpy and pyRoot are required for root output analysis.

In future, conventional python setup scripts will be implemented along with dynamic import based on available dependencies.

* python2.7
* ipython
* numpy
* scipy
* matplotlib 
* pyroot (build root with python extensions)
* [pymad8](https://bitbucket.org/jairhul/pymad8)
* [pymadx](https://bitbucket.org/jairhul/pymadx)
* [robdsim](https://bitbucket.org/jairhul/robdsim)