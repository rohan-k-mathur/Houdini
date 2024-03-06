# Navigate to the /obj context
obj_context = hou.node('/obj')

# Create a new geometry container node
geo_node = obj_context.createNode('geo', 'GeneratedGeometry')

# Create a Python SOP node within the geometry container
python_sop = geo_node.createNode('python', 'CreateCassinianOvoid')

# Python code to generate a shape inspired by Cassinian Ovoids
python_code = """
import hou
import numpy as np

# Function to  calculate the square root of a value, ensuring non-negative input
def safe_sqrt(value):
    return np.sqrt(np.maximum(value, 0))

# Access the current frame to interpolate parameters 
frame = hou.frame()

# Parameters for the shape, including starting and ending values for 'a' to animate transformation
a_start = 0.5001  
a_end = 2.0       
c = 0.5           # Controls shape distortion
# Linear interpolation of 'a' from a_start to a_end over frames 1 to 250, for dynamic animation
t = (frame - 1) / (249)  # Normalize frame number to range [0, 1]
a = (a_end - a_start) * t + a_start  # Interpolated value of 'a'

# Define parametric ranges for the shape's geometry
u = np.linspace(0, 2 * np.pi, 100)  # Azimuthal angle
v = np.linspace(0, np.pi, 100)      # Polar angle

# Generate a meshgrid for (u, v) to compute points in bulk for efficiency
U, V = np.meshgrid(u, v)

# Calculate radial distance R using an approximation of the Cassinian Ovoid 
R = safe_sqrt(np.abs(np.cos(2 * V) + safe_sqrt(a**4 - c**4)))
x = R * np.sin(V) * np.cos(U)
y = R * np.sin(V) * np.sin(U)
z = R * np.cos(V)

# Clear existing geometry to prepare for new points generation
geo = hou.pwd().geometry()
geo.clear()

# Iterate over flattened arrays of coordinates to create and position points in the geometry
for xi, yi, zi in zip(x.flatten(), y.flatten(), z.flatten()):
    point = geo.createPoint()
    point.setPosition((xi, yi, zi))
"""

# Set the Python SOP's script parameter to the python_code
python_sop.parm('python').set(python_code)

# Layout nodes for a cleaner look
geo_node.layoutChildren()
