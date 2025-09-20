import pyRecFusionSDK as rf
import numpy as np
# import psutil
from time import time_ns
a = np.array([[1,2,3], [4,5,6], [7,8,9]])
m3 = rf.Mat3(a.copy())
print(m3.data)
m3.data = np.array([[1,1,1],[2,2,2],[3,3,3]])
print(m3.data)
m3[1,1] = 55
print(m3.data)
# m3.data = a
# print(m3.data)
exit()

img_color = rf.ColorImage(5, 10, 3, None)

print(img_color)
print(img_color.data)
print(img_color.data_ref)

exit()
print(f"Version: {rf.version()}")

rf.init()
mgr = rf.SensorManager()
sensor = mgr.open_any()
img_color = rf.ColorImage.for_sensor(sensor)
img_depth = rf.DepthImage.for_sensor(sensor)

NUM_FRAMES = 3
frames = []
sums_before = []
t0 = time_ns()
for i in range(NUM_FRAMES):
    mem = psutil.virtual_memory()
    print("Used memory:", mem.used / 1024 / 1024)
    if sensor.read_image(img_depth, img_color):
        # sums_before.append(sum(sum(img_color.data)))
        d = img_color.data
        print(d)
        # img_color.data.fill(1)
        print(d)
        frames.append(d)
t1 = time_ns()
print("Took:", (t1-t0) / 1e6, "ms")
print("fps:", NUM_FRAMES / ((t1 - t0) / 1e9))  

sums_after = []
for frame in frames:
    sums_after.append(frame.max().max())
print(sums_before)
print(sums_after)

rf.deinit()
