import pyRecFusionSDK as rf
import numpy as np

# Initialize vectors
v1 = rf.Vec3(1.1, 2.2, 3.3)
v2 = rf.Vec3i(x=1, y=2, z=3)

print(v1, v2)

# Initialize 3x3 matrix from Numpy array or nested lists
arr = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
m1 = rf.Mat3(arr)
m2 = rf.Mat3(np.asarray(arr))

print(m1, m2)

# Matrix multiplication
print(m1 @ m2)
