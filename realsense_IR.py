import pyrealsense2 as rs
import numpy as np
import cv2
import json
import os

out_dir = "rs_test_output"
os.makedirs(out_dir, exist_ok=True)

# 1. 配置并启动管线
pipeline = rs.pipeline()
config = rs.config()

# 分辨率可以按需改，后面最好和你算法一致
W, H = 640, 480
config.enable_stream(rs.stream.color, W, H, rs.format.bgr8, 30)
config.enable_stream(rs.stream.depth, W, H, rs.format.z16, 30)
config.enable_stream(rs.stream.infrared, 1, W, H, rs.format.y8, 30)  # 左 IR
config.enable_stream(rs.stream.infrared, 2, W, H, rs.format.y8, 30)  # 右 IR
# 对齐 depth → color
align = rs.align(rs.stream.color)

print("Starting pipeline...")
profile = pipeline.start(config)

# 2. 跳过前面几帧，让自动曝光稳定
for _ in range(30):
    frames = pipeline.wait_for_frames()

frames = pipeline.wait_for_frames()
aligned = align.process(frames)

color_frame = aligned.get_color_frame()
depth_frame = aligned.get_depth_frame()

ir_left_frame  = frames.get_infrared_frame(1)
ir_right_frame = frames.get_infrared_frame(2)

if not color_frame or not depth_frame:
    raise RuntimeError("No frames received")

# 3. 转成 numpy
color = np.asanyarray(color_frame.get_data())
depth = np.asanyarray(depth_frame.get_data())  # uint16
ir_left  = np.asanyarray(ir_left_frame.get_data()) # HxW, uint8
ir_right = np.asanyarray(ir_right_frame.get_data()) # HxW, uint8

# ✅ 灰度 → 伪三通道 RGB (和你 C++ 里的 cv::cvtColor 一样)
ir_left_rgb  = cv2.cvtColor(ir_left,  cv2.COLOR_GRAY2RGB)   # HxWx3
ir_right_rgb = cv2.cvtColor(ir_right, cv2.COLOR_GRAY2RGB)   # HxWx3

print("Color shape:", color.shape)
print("Depth shape:", depth.shape)


# =============================
#  🔥 正确提取 IR stereo 内参 🔥
# =============================

intr_left = ir_left_frame.profile.as_video_stream_profile().intrinsics
intr_right = ir_right_frame.profile.as_video_stream_profile().intrinsics

# stereo baseline (单位：米)
extr = ir_left_frame.profile.get_extrinsics_to(ir_right_frame.profile)
baseline = np.linalg.norm(extr.translation)

K_left = {
    "width": intr_left.width,
    "height": intr_left.height,
    "fx": intr_left.fx,
    "fy": intr_left.fy,
    "cx": intr_left.ppx,
    "cy": intr_left.ppy,
    "baseline_m": baseline
}

print("IR Left K = ", K_left)
print("Baseline = ", baseline)

# 5. 保存结果，方便后面直接作为 demo_data 用
cv2.imwrite(os.path.join(out_dir, "color_0000.png"), color)
cv2.imwrite(os.path.join(out_dir, "depth_0000.png"), depth)
cv2.imwrite(os.path.join(out_dir, "ir_left_0000.png"), ir_left_rgb)
cv2.imwrite(os.path.join(out_dir, "ir_right_0000.png"), ir_right_rgb)


# save intrinsics for stereo
with open(os.path.join(out_dir, "ir_intrinsics.json"), "w") as f:
    json.dump(K_left, f, indent=2)

pipeline.stop()
print("Saved images and intrinsics to:", out_dir)

