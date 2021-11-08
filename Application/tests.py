import numpy as np
import matplotlib.pyplot as plt



monde = np.ones((3, 3), dtype=np.float64)
monde[0, 0] = 3
monde[0, 1] = 5
monde[1, 0] = 8

print("monde 1")
print(monde)
print("monde 2")
print(np.roll(monde, 1, 1))
print("monde 3")
print(np.roll(monde, -1, axis=0))


