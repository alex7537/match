import trimesh

# 原始带纹理的 ply 路径
mesh_path = "/home/match/test-bild/obj_000002.ply"   # ← 把这里改成你的真实路径

# 读取 mesh（不做额外处理）
mesh = trimesh.load(mesh_path, process=False)

# 给它一个简单的单色材质（避免引用外部 png）
mesh.visual = trimesh.visual.ColorVisuals(
    mesh,
    vertex_colors=[200, 200, 200, 255]  # 灰白色，RGBA
)

# 导出为新的无纹理 ply
out_path = "/home/match/test-bild/obj_000002_notex.ply"  # ← 输出路径，也改成你方便的地方
mesh.export(out_path)

print("Exported:", out_path)
