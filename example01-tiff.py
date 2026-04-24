# Importing
import sys

# sys.path.append('$HOME/ug4-git/lib/')
# sys.path.append('$HOME/ug4-git/bin/plugins/')
import ug4py.pyugcore  as ug4
import ug4py.pyconvectiondiffusion as cd

sys.path.append('.')
import modsimtools as util


############################################
# Read UG4 domain.
############################################
# We read a grid & create a grid function (for storing data)
filename="grids/square.ugx" # "square", "corner-mixed"
dom = util.CreateDomain(filename, 6, "")
approxSpaceDesc = dict(fct = "u", type = "Lagrange", order = 1)
approxSpace = util.CreateApproximationSpace(dom, approxSpaceDesc)
ufield = ug4.GridFunction2dCPU1(approxSpace)



############################################
# Read Tiff-Image.
############################################

if True:
    # import ug4py.pyijkdata as ijk
    import ug4py.pyijkdata as ijk

    # Read image.
    tiffImageData = ijk.TiffImageDataNumber2d()
    tiffImageData.init("images/example.tiff")
    nx=tiffImageData.get_size_x()
    ny=tiffImageData.get_size_y()
    print("nx =" + str (nx) + ", ny="+ str(ny))

    # Set dimensions of bounding box. All points will be mapped into this.
    x0 = ug4.Vec2d(); x0.set_coord(0, -1.0);  x0.set_coord(1, -1.0)
    x1= ug4.Vec2d();  x1.set_coord(0, 1.0);  x1.set_coord(1, 1.0)
    tiffImageData.set_corners(x0,x1)

    # Write data.
    ug4.Interpolate(tiffImageData, ufield, "u")
    ug4.WriteGridFunctionToVTK(ufield, "vtk/Field_Tiff")
