# Importing
import sys

# sys.path.append('$HOME/ug4-git/lib/')
# sys.path.append('$HOME/ug4-git/bin/plugins/')
import ug4py.pyugcore  as ug4
import ug4py.pyconvectiondiffusion as cd

sys.path.append('.')
import modsimtools as util
import numpy as np

############################################
# Read UG4 domain.
############################################

# Number of refinements and method (FE or FV) can be set here.
NUM_REFS = 4
METHOD = "FV"

# We read a grid & create a grid function (for storing data)
filename="grids/square.ugx" # "square", "corner-mixed"
dom = util.CreateDomain(filename, NUM_REFS, "")
approxSpaceDesc = dict(fct = "u", type = "Lagrange", order = 1)
approxSpace = util.CreateApproximationSpace(dom, approxSpaceDesc)
ufield = ug4.GridFunction2dCPU1(approxSpace)


############################################
# Python-UserData: Read TIFF image and define callback for sampling raster data in finite element assembly.
############################################
def read_tiff_image(filename):
    from PIL import Image
    
    
    # Open the TIFF file
    img = Image.open(filename)
    
    # Read dimensions MxN (width x height)
    M, N = img.size  # M = width, N = height
    print(f"Dimensions: {M} x {N}")
    
    # Convert to numpy array (2D if grayscale, 3D if RGB)
    data = np.array(img)
    
    # If RGB, convert to grayscale or handle accordingly
    if len(data.shape) == 3:
        data = np.mean(data, axis=2)  # Convert to grayscale by averaging channels
    
    # Map to unit square: normalize coordinates if needed, but for data, perhaps normalize values
    # Assuming data is intensity values, normalize to [0,1] for unit square mapping
    if data.max() > 0:
        data = data / data.max()
    
    return data

tiff_data = read_tiff_image("images/example.tiff")
print(tiff_data)
print(tiff_data.shape)
npixel=np.min(tiff_data.shape)   
print(f"npixel = {npixel}")




# Define a callback function for sampling the raster data in the finite element assembly.
# The parameters be0x, be0y, be1x, be1y define the bounding box of the element in world coordinates. 
# The parameters t and si can be used for time-dependent problems or for selecting a subset, if needed. They are ignored here.
# 
# Here, we compute the corresponding pixel indices for the bounding box, extract the raster values in that box, 
# and return their average.
def raster_box_value_2d(x, y, be0x, be0y, be1x, be1y, t, si):
    """UG-Callback: Mittelwert der Box im simple mode, mit optionaler Overview-Auswahl."""
    import math
    ncells = npixel-1
    ii = math.floor(ncells*(x+1.0)/2.0)
    jj = math.floor(ncells*(y+1.0)/2.0)    
    
    print(f"Sampling at x={x}, y={y} → ii={ii}, jj={jj}")   
  
    print(f"Raster value at (ii, jj): {tiff_data[int(jj), int(ii)]}")
   
  
    ii0 = math.floor(ncells*(be0x+1.0)/2.0)
    jj0 = math.floor(ncells*(be0y+1.0)/2.0)
    ii1 = math.floor(ncells*(be1x+1.0)/2.0)
    jj1 = math.floor(ncells*(be1y+1.0)/2.0)
    print(f"Bounding box: ({be0x}, {be0y}), ({be1x}, {be1y})")
    print(f"Corresponding pixel box: ii [{ii0}, {ii1}], jj [{jj0}, {jj1}]")

    box_data = tiff_data[jj0:jj1, ii0:ii1]
    print(f"Raster values in box: {box_data}")
    avg_value = np.mean(box_data)
    print(f"Average raster value in box: {avg_value}")


    return float(avg_value)    





############################################
# Configure solver.
############################################
# Direct solver (LU) is used here for simplicity, but for larger problems, an iterative solver with preconditioning would be more efficient.
solver = ug4.LUCPU1()

# CG with Gauss-Seidel preconditioning is an alternative for larger systems, but may require tuning for convergence.
jac = ug4.JacobiCPU1(0.5)
sgs = ug4.SymmetricGaussSeidelCPU1()
solver = ug4.CGCPU1(sgs)



# Multigrid solvers can be very efficient for large problems, but require more setup (defining multigrid levels, smoothers, etc.).
gmg = ug4.GeometricMultiGrid2dCPU1(approxSpace)  # Konstruktor
gmg.set_base_solver(ug4.LUCPU1())  
gmg.set_base_level(1)          # Multi-grid

gmg.set_smoother(sgs)
gmg.set_cycle_type("V")     # Select cycle type "V,W,F".                  
gmg.set_num_presmooth(3)
gmg.set_num_postsmooth(3)      
gmg.set_rap(True)           # Galerkin produkt  A_H=RAP

# Use CG with MG as preconditioner.
solver = ug4.CGCPU1(gmg)
# solver = ug4.LinearSolverCPU1(gmg)


print(solver.config_string())

############################################
# Read MultiLayerRaster + Python-UserData
############################################
if True:
    try:
        import ug4py.pyijkdata as ijk

     

        # Create finite element discretizations for two cases: 
        # A) Interpolation, B) Diffusion problem with spatially varying K(x).

        if METHOD == "FE":
            elemDiscA = cd.ConvectionDiffusionFE2d("u", "Inner")
            elemDiscB = cd.ConvectionDiffusionFE2d("u", "Inner")
        else:
            elemDiscA = cd.ConvectionDiffusionFV12d("u", "Inner")
            elemDiscB = cd.ConvectionDiffusionFV12d("u", "Inner")
      
       
        b = ug4.GridFunction2dCPU1(approxSpace)
    
        # Python-Funktion als UserData binden 
        py_ud = ijk.PyElementUserData2d(raster_box_value_2d) 


        # Case A : Compute L2-Interpolation. 
        # FV : \Int_{B} u dV = \Int_{B} py_ud dV
        elemDiscA.set_source(py_ud)
        elemDiscA.set_diffusion(0.0)
        elemDiscA.set_reaction_rate(1.0)

        domainDiscA = ug4.DomainDiscretization2dCPU1(approxSpace)
        domainDiscA.add(elemDiscA)

        A = ug4.AssembledLinearOperatorCPU1(domainDiscA)
        domainDiscA.assemble_linear(A, b)
        domainDiscA.adjust_solution(ufield)

        gmg.set_discretization(domainDiscA)
        solver.init(A)
        solver.apply(ufield, b)
        ug4.WriteGridFunctionToVTK(ufield, f"vtk/Field_K_{NUM_REFS}_refs_{METHOD}")
        print(f"Wrote Field_K_{NUM_REFS}_refs_{METHOD} VTK file.")

        #k.add(py_ud, ug4.ConstUserMatrix2d())


        # Case B : Diffusion problem with spatially varying K(x):   
        #   \nabla \cdot (-K(x) \nabla u) = 0
        #  with K(x) = 0.001 + 1000*(1-py_ud)
       
        k = ug4.ScaleAddLinkerNumber2d() # k = k0 + 1000*(1-pyud)
        k0= 0.001
        k.add(k0+1, 10.0)
        k.add(py_ud, -10.0)

        K = ug4.ScaleAddLinkerMatrix2d()
        K.add(k, ug4.ConstUserMatrix2d())


        # def MyExp (v): return 10**(-v)
        # def MyExp_v (v): return -math.log(10.0) * (10**(-v))
        # pyExp=ug4.PythonUserFunction2d(MyExp, 1)
        # pyExp.set_input_and_deriv(0,k, MyExp_v)

        elemDiscB.set_diffusion(K)
        elemDiscB.set_source(0.0)
        elemDiscB.set_reaction_rate(0.0)  

        # Gradient from WEST to EAST (noflux on NORTH/SOUTH).
        dirichletBND = ug4.DirichletBoundary2dCPU1()
        dirichletBND.add(0.0, "u", "EAST")
        dirichletBND.add(1.0, "u", "WEST")

        # Collect all discretization components and assemble the system.
        domainDiscB = ug4.DomainDiscretization2dCPU1(approxSpace)
        A = ug4.AssembledLinearOperatorCPU1(domainDiscB)

        domainDiscB.add(elemDiscB)
        domainDiscB.add(dirichletBND)
        domainDiscB.assemble_linear(A, b)
        domainDiscB.adjust_solution(ufield)
        
        # Solve the system and write results to VTK for visualization.
        gmg.set_discretization(domainDiscB)
        solver.init(A)
        solver.apply(ufield, b)

        ug4.WriteGridFunctionToVTK(ufield, f"vtk/Field_u_{NUM_REFS}_refs_{METHOD}")
        print(f"Wrote Field_u_{NUM_REFS}_refs_{METHOD} VTK file.")
        print("Done.")


    except Exception as inst:
        print(type(inst))    # the exception type
        print(inst.args)     # arguments stored in .args
        print(inst)          #


