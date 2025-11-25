import json
import numpy as np

pose_path = "/home/match/test-bild/pose.json"  # 换成你的真实路径

with open(pose_path, "r") as f:
    data = json.load(f)

# 原始是 [[[...],[...],[...],[...]]]
# 这里直接取第 0 个元素，变成 4x4
T = np.array(data["transformation_matrix"][0], dtype=float)

print("T shape:", T.shape)
print("T =\n", T)

tx, ty, tz = T[0, 3], T[1, 3], T[2, 3]
print("\n3D position in camera frame:")
print("tx =", tx)
print("ty =", ty)
print("tz =", tz, "(depth in meters)")
