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
# Read MultiLayerRaster
############################################

try:
    import ug4py.pyijkdata as ijk
    myRasterData = ijk.MultilevelRasterData2d()

    # This function uses StdUserData::operator()
    #ug4.Interpolate(myRasterData, ufield, "u")



    elemDisc=cd.ConvectionDiffusionFE2d("u", "Inner")
    elemDisc.set_source(myRasterData)
    elemDisc.set_diffusion(0.0)
    elemDisc.set_reaction_rate(1.0)
    
    dirichletBND = ug4.DirichletBoundary2dCPU1()
    dirichletBND.add(0.0, "u", "Boundary")

    domainDisc = ug4.DomainDiscretization2dCPU1(approxSpace)
    domainDisc.add(elemDisc)
    domainDisc.add(dirichletBND)

    A = ug4.AssembledLinearOperatorCPU1(domainDisc)
    b = ug4.GridFunction2dCPU1(approxSpace)

    domainDisc.assemble_linear(A, b)
 
    domainDisc.adjust_solution(ufield)

    lu = ug4.LUCPU1()
    lu.init(A)
    lu.apply(ufield,b)
    ug4.WriteGridFunctionToVTK(ufield, "Field_MultiLayerRaster")

except Exception as inst:
    print(type(inst))    # the exception type
    print(inst.args)     # arguments stored in .args
    print(inst)          #

# Write data.
# ug4.WriteGridFunctionToVTK(ufield, "Field_RasterASC")
