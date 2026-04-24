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
approxSpace = util.CreateApproximationSpace(dom, dict(fct = "u", type = "Lagrange", order = 1))
ufield = ug4.GridFunction2dCPU1(approxSpace)


############################################
# Read ESRI-ASC
############################################

try:
    myRaster = ug4.NumberRaster2d()
    myRaster.load_from_asc("images/example.asc")
    # myRaster.blur(desc.blurAlpha, desc.blurIterations)
except Exception as inst:
    print ("Error loading raster from ASC:")
    print(type(inst))    # the exception type
    print(inst.args)     # arguments stored in .args
    print(inst)          #

try:
    rasterNumberData = ug4.RasterNumberData2d(myRaster)
    rasterNumberData.set_order(2)
    rasterNumberData.set_scale(1.0)
except Exception as inst:
    print ("Error creating RasterNumberData2d:")
    print(type(inst))    # the exception type
    print(inst.args)     # arguments stored in .args
    print(inst)          #

try:
    # Interpolate the raster data onto the finite element grid,
    # write to VTK for visualization.
    ug4.Interpolate(rasterNumberData, ufield, "u")
    ug4.WriteGridFunctionToVTK(ufield, f"vtk/Field_RasterASC")
except Exception as inst:
    print ("Error writing grid function to VTK:")
    print(type(inst))    # the exception type
    print(inst.args)     # arguments stored in .args
    print(inst)     
