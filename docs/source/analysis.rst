========
Analysis
========

There are many potential ways to perform analysis of BDSIM output. There is no standard way to perform
analysis (e.g. pure ROOT, ROOT via python, uproot, etc). This module gathers useful algorithms for users
to perform standard analysis. These analyses are also very useful for testing of BDSIM output.

Trajectory
----------

In general it is complex to navigate and use trajectory data structures. They mainly form a connected
tree data structure, although they are stored as flat tables (``std::vector``) and trajectories are linked
with indicies (``std::vector`` and ``std::map``)

Finding the primary trajectory
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The order in which trajectories are stored is not the same between runs of BDSIM/Geant4. The
primary track could appear anywhere is the trajectory data structures. ``BDSIM_OUTPUT.root`` need to have trajectories
stored and specifically: ::

    option, storeTrajectory=1,
            storeTrajectoryDepth=-1,
            storeTrajectoryAllVariables=1;

To find the primary trajectory

.. code-block:: python

    import pybdsim
    d = pybdsim.Data.Load("./BDSIM_OUTPUT.root")
    et = d.GetEventTree()   # get event tree
    e = d.GetEvent()        # get event root event data structure
    et.GetEntry(0)          # get first event

    iprimary = pybdsim.Analysis.Trajectory.find_primary_index(e.Trajectory)


Hashing a event trajectories
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Example to load a file and hash the trajectories.

.. code-block:: python

    import pybdsim
    d = pybdsim.Data.Load("./BDSIM_OUTPUT.root")
    et = d.GetEventTree()   # get event tree
    e = d.GetEvent()        # get event root event data structure
    et.GetEntry(0)          # get first event

    v, h = pybdsim.Analysis.Trajectory.traverse_trajectories(e.Trajectory,"test.dat")

The ``test.dat`` output file is optional and it very useful to find divergances in trajectory tree
structure. ``traverse_trajectories`` returns a list of the visited trajectory indices and a hash of
the entire tree. The hash is a ``bytes`` object and the easiest way to view is ``h.hex()``


Energy loss
-----------
