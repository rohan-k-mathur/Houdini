# Navigate to the /obj context
obj_context = hou.node('/obj')

# Create a new geometry container node
geo_node = obj_context.createNode('geo', 'GeneratedGeometry')

# Create a Python SOP node within the geometry container
python_sop = geo_node.createNode('python', 'Structured_Topological_Mappings_of_Invariant_Grids')

python_code = """
import hou
import numpy as np

# Define the size of the grid and mega grid
grid_size = 5
mega_grid_size = 7

t = hou.frame() 

def apply_rules_test(i, j, k):

    return np.cos(i*j*k), np.sin(i*j*k), np.cos(i*j*k)* np.sin(i*j*k)
    
def apply_rules(i, j, k):

    return (i-j+k),(k/(4+2*abs(np.sin(j)))),(i*j*k)/(abs(i+j)+1)


    
def create_surface(coefficients, megacoefficients, geo, t):

    u = np.linspace(0, 2 * np.pi, 34)
    v = np.linspace(0,  2 * np.pi, 34)
    U, V = np.meshgrid(u, v)
    
    pointIndexOffset = 0


    for mi in range(mega_grid_size):
        for mj in range(mega_grid_size):
            for mk in range(mega_grid_size):
                a, b, c = megacoefficients[mi, mj, mk]
                

                cv_positions = []
                
                px = (a + np.cos(a*U + b*V)) * ((a+b-c) + np.cos(U/25))
                x = (a + np.sin(px*U + V)) * (a + np.cos(U))
                y = (b + np.cos(x*V - U)) *(b + np.sin(V))
                z = x*y * np.sin(x-y)

                # Create a local coordinate system for each mega grid cell
                local_coords = np.stack((x, y, z), axis=-1)

                # Apply a rotation matrix to the local coordinates
                rotation_matrix = np.array([
                    [np.cos(a/20), -np.sin(b/20), 0],
                    [np.sin(c/20), np.cos(-a/20), 0],
                    [0, 0, 1]
                ])
                rotated_coords = np.dot(local_coords, rotation_matrix.T)
                # List to store point references for polygon creation
                pointsRefs = []

                for xi, yi, zi in zip(rotated_coords[:, :, 0].flatten(), rotated_coords[:, :, 1].flatten(), rotated_coords[:, :, 2].flatten()):
                    point = geo.createPoint()
                    point.setPosition((xi + mi * (grid_size*4), yi + mj* (grid_size*4), zi + mk* (grid_size*4)))  # Offset for visualization
                    pointsRefs.append(point)
                    cv_positions.append(point) 
                  

# Initialize coefficients for the grid
coefficients = np.zeros((mega_grid_size, mega_grid_size, mega_grid_size, grid_size, grid_size, grid_size, 3))

# Access the geometry of the Python SOP node
geo = hou.pwd().geometry()
geo.clear() # Clear existing geometry

# Initialize megacoefficients based on grid coefficients
megacoefficients = np.zeros((mega_grid_size, mega_grid_size, mega_grid_size, 3))

for mi in range(mega_grid_size):
    for mj in range(mega_grid_size):
        for mk in range(mega_grid_size):

            megacoefficients[mi, mj, mk] = apply_rules(mi, mj, mk)

            # Apply rules to the grid coefficients within each mega grid cell
            for i in range(grid_size):
                for j in range(grid_size):
                    for k in range(grid_size):
                        coefficients[mi, mj, mk, i, j, k] = apply_rules(i+mi, j+mj, k+mk)

# Generate the points on the surfaces
create_surface(coefficients, megacoefficients, geo, t)

"""

# Set the Python SOP's script parameter to the python_code
python_sop.parm('python').set(python_code)

# Layout nodes for a cleaner look
geo_node.layoutChildren()
