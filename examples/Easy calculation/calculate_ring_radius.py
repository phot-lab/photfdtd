import numpy as np

neff = 2.388915
lam = 1550e-9
N = 100
print("radius = %f um" % (lam * N * 1e6 / neff / (2 * np.pi)))

