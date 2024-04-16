import vtk
import pybdsim

def Plot3DXYZVtk(filename):

    d = pybdsim.Field.Load(filename)

    [glyph3D, streamline] = _fieldToVtkStructuredGrid(d)

    colors = vtk.vtkNamedColors()

    mapper = vtk.vtkPolyDataMapper()
    mapper.SetInputConnection(glyph3D.GetOutputPort())

    actor = vtk.vtkActor()
    actor.SetMapper(mapper)
    actor.GetProperty().SetColor([0,0,0])

    actor2 = vtk.vtkActor()
    actor2.SetMapper(streamline.GetOutputPort())
    actor2.VisibilityOn()

    renderer = vtk.vtkRenderer()
    renderWindow = vtk.vtkRenderWindow()
    renderWindow.AddRenderer(renderer)
    renderWindow.SetWindowName('OrientedGlyphs')

    renderWindowInteractor = vtk.vtkRenderWindowInteractor()
    renderWindowInteractor.SetRenderWindow(renderWindow)

    axes = vtk.vtkAxesActor()
    axes.SetTotalLength(50,50,50)

    #renderer.AddActor(actor)
    renderer.AddActor(actor2)
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
    glyph3D.SetScaleFactor(0.1)
    glyph3D.Update()

    seeds = vtk.vtkPlaneSource()
    seeds.SetXResolution(10)
    seeds.SetYResolution(10)
    seeds.SetOrigin(0, 0, 0)
    seeds.SetPoint1(10, 0, 0)
    seeds.SetPoint2(0, 10, 0)
    seeds.Update()

    streamline = vtk.vtkStreamTracer()
    streamline.SetInputData(strucGrid)
    streamline.SetSourceConnection(seeds.GetOutputPort())
    streamline.SetMaximumPropagation(50)
    streamline.SetInitialIntegrationStep(.2)
    streamline.SetIntegrationDirectionToForward()
    streamline.Update()

    streamline_mapper = vtk.vtkPolyDataMapper()
    streamline_mapper.SetInputConnection(streamline.GetOutputPort())
    streamline_actor = vtk.vtkActor()
    streamline_actor.SetMapper(streamline_mapper)
    streamline_actor.VisibilityOn()

    return [glyph3D, streamline_mapper]
