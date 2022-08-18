import vtk
import pybdsim

def Plot3DXYZVtk(filename):

    d = pybdsim.Field.Load(filename)

    glyph3D = _fieldToVtkStructuredGrid(d)

    colors = vtk.vtkNamedColors()

    mapper = vtk.vtkPolyDataMapper()
    mapper.SetInputConnection(glyph3D.GetOutputPort())

    actor = vtk.vtkActor()
    actor.SetMapper(mapper)
    actor.GetProperty().SetColor([0,0,0])

    renderer = vtk.vtkRenderer()
    renderWindow = vtk.vtkRenderWindow()
    renderWindow.AddRenderer(renderer)
    renderWindow.SetWindowName('OrientedGlyphs')

    renderWindowInteractor = vtk.vtkRenderWindowInteractor()
    renderWindowInteractor.SetRenderWindow(renderWindow)

    axes = vtk.vtkAxesActor()
    axes.SetTotalLength(50,50,50)

    renderer.AddActor(actor)
    renderer.AddActor(axes)
    renderer.SetBackground([1,1,1])

    renderWindow.Render()
    renderWindowInteractor.Start()

def _fieldToVtkStructuredGrid(inputData) :

    nx = inputData.header['nx']
    minx = inputData.header['xmin']
    maxx = inputData.header['xmax']
    ny = inputData.header['ny']
    miny = inputData.header['ymin']
    maxy = inputData.header['ymax']
    nz = inputData.header['nz']
    minz = inputData.header['zmin']
    maxz = inputData.header['zmax']
    strucGrid = vtk.vtkStructuredGrid()

    strucGrid.SetDimensions(nx,ny,nz)

    points = vtk.vtkPoints()
    pointValues = vtk.vtkDoubleArray()
    pointValues.SetNumberOfComponents(3)
    pointValues.SetNumberOfTuples(nx*ny*nz)

    iPoint = 0
    for i in range(0,nx) :
        for j in range(0,ny) :
            for k in range(0,nz) :
                points.InsertNextPoint(inputData.data[i,j,k,0],
                                       inputData.data[i,j,k,1],
                                       inputData.data[i,j,k,2])
                pointValues.SetTuple(iPoint,
                                     [inputData.data[i,j,k,3],
                                     inputData.data[i,j,k,4],
                                     inputData.data[i,j,k,5]])
                iPoint += 1

    strucGrid.SetPoints(points)
    strucGrid.GetPointData().SetVectors(pointValues)

    arrowSource = vtk.vtkArrowSource()

    glyph3D = vtk.vtkGlyph3D()
    glyph3D.SetSourceConnection(arrowSource.GetOutputPort())
    # glyph3D.SetVectorModeToUseVector()
    glyph3D.SetScaleModeToScaleByVector()
    glyph3D.SetInputData(strucGrid)
    glyph3D.SetScaleFactor(5)
    glyph3D.Update()

    return glyph3D
