import json
import numpy as np
import os

scene_dir = "my_demo_d435"

with open(os.path.join(scene_dir, "intrinsics.json"), "r") as f:
    intr = json.load(f)

fx = intr["fx"]
fy = intr["fy"]
cx = intr["cx"]
cy = intr["cy"]

K = np.array([
    [fx, 0,  cx],
    [0,  fy, cy],
    [0,  0,  1]
], dtype=float)

print("K =\n", K)

out_path = os.path.join(scene_dir, "cam_K.txt")
np.savetxt(out_path, K)
print("saved to", out_path)
