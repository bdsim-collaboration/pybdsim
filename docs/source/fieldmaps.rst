==========
Field Maps
==========

The `pybdsim.Field` module has several functions and classes to help create, convert,
and visualise BDSIM-format field maps easier. Various useful workflows are described
below, but every function and class is documented in: :ref:`pybdsim-field-module`.


.. _field-map-loading:

Loading
-------

Existing BDSIM-format field maps can be loaded with: ::

  fm = pybdsim.Field.Load("nameOfFieldMap.dat")

This will automatically detect the number of dimensions in the field map and load
it into a numpy array inside a pybdsim class. The class is one of:


* :code:`pybdsim.Field.Field1D`
* :code:`pybdsim.Field.Field2D`
* :code:`pybdsim.Field.Field3D`
* :code:`pybdsim.Field.Field4D`

These all have member variables such as:

* :code:`data` - the numpy array of the field map data
* :code:`columns` -  a list of column names
* :code:`header` - a dictionary of all information in the header

Writing
-------

Al of the pybdsim classes described in :ref:`field-map-loading` (e.g. `Field3D`) have
a method called :code:`Write`. This will write out the instance of that class (i.e. that
particular field map data) to a BDSIM-format field map file.

Therefore, these classes represent a a very good route for creation and conversion
of field maps. The recommended strategy is to get the information *into* one of those
classes then it can be written out to file, loaded, plotted with ease.

.. _field-map-creation:

Creation
--------

A field map can be created from scratch in Python from knowledge of a field, such as
an equation. A numpy array of the right shape should be created, then an instance
of :code:`pybdsim.Field.Field[N]D` created (where N is one of (1,2,3,4).

Creating the array is entirely up to the user as this depends on how they get the
information. However, a small example script is shown below here (in Python language): ::


  import numpy as np
  import pybdsim

  fx, fy, fz = 0.0, 1.0, 0.0
  xmax = 30  # cm is the default units for bdsim field maps
  ymax = 30
  data = []
  # loop over and build up 3d lists of lists of lists
  for yi in [-ymax, ymax]:
     v = []
     for xi in [-xmax, xmax]:
         # here, fx,fy,fz could be from a function
         v.append([xi, yi, fx, fy, fz])
         data.append(v)

  # convert to numpy array
  data = np.array(data)
    
  # construct a BDSIM format field object and write it out
  f = pybdsim.Field.Field2D(data)
  f.Write("box-field-map.dat')


.. note:: BDSIM's default convention for a field map is to loop over the lowest
	  dimension first, i.e. x. Therefore, the loop above is written y, then x.
	  See below for purposely handling the other order of looping.

This minimal example creates a 2D 'box' of 4 points in space each with the same field
value of [0,1,0] (unit Y direction with magnitude 1). The box is :math:`\pm 30 cm` in
size. Units aren't used explicitly - just numbers - but the units of BDSIM field map
files are cm and s.

.. note:: The file written out by the class at the end can be loaded again with
	  :code:`pybdsim.Field.Load` to get a (new) object with the same contents
	  as the original Field2D instance.

The array should be structured to contain the coordinates and field components at each
point. So for a 2D field map, this would be: :math:`(x, y, F_x, F_y, F_z)`. The array would
then have 2 dimensions representing its structure. So if the field map had 10 points in `x`
and 20 in `y`, it would ultimately be a numpy array with the shape :code:`(10,20,5)`.

Generally, the :code:`numpy.shape(array)` would look like:

* 1D: :code:`(N_x, 4)`
* 2D: :code:`(N_x, N_y, 5)`
* 3D: :code:`(N_x, N_y, N_z, 6)`
* 4D: :code:`(N_x, N_y, N_z, N_t, 7)`

.. warning:: A key check is looking at the field map, the higher dimension coordinates
	     (e.g. Y, not X) should change first. So for a given X value we should see
	     the Y values cycle through a range, then the X should increment then the Y
	     values cycle again. If this is not the case, then the loop order of dimensions
	     is backwards. You can use "loopOrder" in the header or rewrite the field map
	     correctly.

Alternative Dimensions
**********************

In the case of alternative dimension (e.g. a 2D field map with `x` and `z` dimensions but
no `y`), the construction is the same but we can label the dimensions differently. The dimensions
must be in order (e.g. `x`, `y`, `z`, then `t` for whichever ones are used).

Example: ::

  fm = pybdsim.Field.Field2D(arrayData, firstColumn='X', secondColumn='Z')

Alternative Loop Order
**********************

It is possible for BDSIM to read a file where the right-most coordinate column varies first.
However, for each value, the coordinate columns must still be in x,y,z,t order left to right.
Below is an example similar to above but writing out the file the other way (note the write function).
This will also write the line :code:`loopOrder> tzyx` in the header so BDSIM can load
the field map equivalently. ::

  import numpy as np
  import pybdsim

  fx, fy, fz = 0.0, 1.0, 0.0
  xmax = 30  # cm is the default units for bdsim field maps
  ymax = 30
  data = []
  # loop over and build up 3d lists of lists of lists
  for yi in [-ymax, ymax]:
     v = []
     for xi in [-xmax, xmax]:
         # here, fx,fy,fz could be from a function
         v.append([xi, yi, fx, fy, fz])
         data.append(v)

  # convert to numpy array
  data = np.array(data)
    
  # construct a BDSIM format field object and write it out
  f = pybdsim.Field.Field2D(data, writeLoopOrderReversed=True)
  f.Write("box-field-map.dat')

Below is a script included with bdsim (:code:`bdsim/examples/features/maps_bdsim/Generate2DLoopOrder.py`)
that shows 4 ways to write a field map with the same information. Ultimately, they convey the exact
same field map to BDSIM although the file contents differ (2 sets of possible contents). ::


    import numpy as _np
    import pybdsim
    
    # LOOP METHOD 1
    data = []
    # loop over and build up 3d lists of lists of lists
    for x in [-1,0,1]:
        v = []
        for z in [3,4]:
            v.append([x, z, B*x, B*x*z, B*z])
        data.append(v)

    # convert to numpy array
    data = _np.array(data)

    # loop order is actually z, then x - ie z varies first, so tzyx, so flip=True
    f = pybdsim.Field.Field2D(data, flip=True, secondColumn='Z')
    # we do this so the order is always written out in the default bdsim way
    f.Write('2dexample_loopOrder_for_xz.dat')
    # but we can purposively write it out the other loop way for testing
    # note the header keys are still the same apart from loopOrder> tzyx
    f.Write('2dexample_loopOrder_for_xz_tzyx.dat', writeLoopOrderReversed=True)


    # LOOP METHOD 2
    data2 = []
    # loop over other way
    for z in [3,4]:
        v = []
        for x in [-1,0,1]:
            v.append([x, z, B*x, B*x*z, B*z]) # values must still be in xyzt order
        data2.append(v)

    # convert to numpy array
    data2 = _np.array(data2)

    # loop order is actually x, then z - ie x varies first, so xyzt, so flip=False
    g = pybdsim.Field.Field2D(data2, flip=False, secondColumn='Z')
    # this will write out a file identical to the first one
    g.Write('2dexample_loopOrder_for_zx.dat')
    # this will write out a file identical to the second one
    g.Write('2dexample_loopOrder_for_zx_tzyx.dat', writeLoopOrderReversed=True)



Visualisation and Plotting
--------------------------

To visualise a field map, it is possible to do so in BDSIM / Geant4. See the BDSIM manual
for this information. This draws a selection of arrows in the 3D model and gives a rough
indication that the field map is as intended.

An alternative way is to load the data in pybdsim in Python and plot it, either fully
or in slices (for 3D or 4D maps).

Any library desired can be used in Python and the classes described above in :ref:`field-map-loading`
provide an excellent way to get a numpy array, that is ubiquitous in Python programming
and libraries.

pybdsim provides a variety of small plotting functions mostly for 1D and 2D field maps
using Matplotlib. These functions are inside the :code:`pybdsim.Field` module and all
start with :code:`Plot`. A list is:

* :code:`pybdsim.Field.Plot1DFxFyFz`
* :code:`pybdsim.Field.Plot2DXYConnectionOrder`
* :code:`pybdsim.Field.Plot2DXY`
* :code:`pybdsim.Field.Plot2DXYFxFyFz`
* :code:`pybdsim.Field.Plot2DXYBz`
* :code:`pybdsim.Field.Plot2DXYStream`
* :code:`pybdsim.Field.Plot3DXY`
* :code:`pybdsim.Field.Plot3DXZ`

A (guaranteed) complete list can be found in :ref:`pybdsim-field-module`.

Each can be inspected (in IPython, which is recommended) with a question mark to see its description: ::

  >>> import pybdsim
  >>> pybdsim.Field.Plot2DXY?
  Signature: pybdsim.Field.Plot2DXY(filename, scale=None)
  Docstring:
  Plot a bdsim field map file using the X,Y plane.

  :param filename: name of field map file or object
  :type filename: str, pybdsim.Field._Field.Field2D instance
  :param scale: numerical scaling for quiver plot arrow lengths.
  :type scale: float
  >>>


Conversion
----------

To convert a field map, you should first write a loader from your own format
to the field map into a numpy array with a structure described in :ref:`field-map-creation`.
Then, this array can be *wrapped* in an instance of one of the pybdsim Field classes. This
class can then be used to write out the field map in BDSIM's format. This would look something
like: ::

  def LoadMyFormatFieldMap(filename):
      # ... some implementation...
      # assume variable 'data' of type numpy.array
      return data

  def Convert(inputfilename, outputfilename):
      d = LoadMyFormatFieldMap(inputfilename)
      # assume here it's a 2D field map... need to know which class to use
      bd = pybdsim.Field2D(d)
      bd.Write(outputfilename)


