import numpy as np
from scipy.spatial.distance import pdist, squareform
from scipy.linalg import svd

def tps_interp(x, y, z, xi, yi):
    # Compute the distances between each pair of data points
    d = squareform(pdist(np.column_stack([x, y])))
    # Construct the system matrix
    rbf = d**2 * np.log(d + (d == 0))
    A = np.column_stack([rbf, x, y, np.ones_like(x)])
    U, S, Vh = svd(A, full_matrices=False)
    # Solve for the weights
    rhs = np.dot(U.T, z)
    weights = np.dot(np.linalg.inv(np.diag(S)), rhs[:,np.newaxis])
    # Evaluate the TPS surface
    dxi = squareform(pdist(np.column_stack([xi.flatten(), yi.flatten()])))
    rbf_eval = dxi**2 * np.log(dxi + (dxi == 0))
    surface = np.dot(rbf_eval, weights[:-3]) + weights[-3]*xi.flatten() + weights[-2]*yi.flatten() + weights[-1]
    return surface.reshape(xi.shape)

# Define the data points
x = np.array([0, 1, 2, 3, 4, 5])
y = np.array([0, 1, 2, 3, 4, 5])
z = np.array([0, 1, 4, 9, 16, 25])
# Define the grid for the TPS surface
xi, yi = np.meshgrid(np.linspace(0, 5, 100), np.linspace(0, 5, 100))
# Perform the TPS interpolation
surface = tps_interp(x, y, z, xi, yi)