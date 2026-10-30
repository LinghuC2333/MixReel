"""Render previs shots with Blender's Workbench engine.

Run through previs.py, which starts it either inside the Blender application
(blender -b --python previs_blender.py -- JOB) or with the bpy Python package
(python previs_blender.py -- JOB). JOB is a JSON file naming the scene, the
output folder and the frames to render.
"""

import json
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import bpy  # noqa: E402
from mathutils import Vector  # noqa: E402

import previs_scene as ps  # noqa: E402


def reset():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    if scene.world is None:
        scene.world = bpy.data.worlds.new("World")
    return scene


def setup(scene, width, height, background):
    scene.render.engine = "BLENDER_WORKBENCH"
    scene.render.resolution_x, scene.render.resolution_y = width, height
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.view_settings.view_transform = "Standard"
    scene.world.color = background
    sh = scene.display.shading
    sh.light = "STUDIO"
    sh.color_type = "MATERIAL"
    sh.background_type = "WORLD"
    sh.show_object_outline = True
    sh.show_cavity = True
    sh.cavity_type = "BOTH"
    sh.show_shadows = True


_materials = {}


def linear(rgb):
    # Scene colours are display colours; Blender expects linear values.
    return tuple(c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4 for c in rgb)


def material(rgb):
    key = tuple(round(c, 4) for c in linear(rgb))
    if key not in _materials:
        m = bpy.data.materials.new("c%02x%02x%02x" % tuple(int(c * 255) for c in key))
        m.diffuse_color = (*key, 1)
        _materials[key] = m
    return _materials[key]


def build(scene, meshes):
    """One Blender object per mesh, rebuilt for each rendered moment."""
    for o in list(bpy.data.objects):
        if o.type == "MESH":
            bpy.data.objects.remove(o, do_unlink=True)
    for i, (oid, v, f, rgb) in enumerate(meshes):
        me = bpy.data.meshes.new(f"{oid}_{i}")
        me.from_pydata([tuple(p) for p in v], [], [tuple(x) for x in f])
        # Round shapes shade smoothly; box edges stay sharp.
        for poly in me.polygons:
            poly.use_smooth = True
        if hasattr(me, "set_sharp_from_angle"):
            me.set_sharp_from_angle(angle=math.radians(40))
        me.materials.append(material(rgb))
        ob = bpy.data.objects.new(f"{oid}_{i}", me)
        scene.collection.objects.link(ob)


def camera(scene, cam):
    data = bpy.data.cameras.get("previs") or bpy.data.cameras.new("previs")
    ob = bpy.data.objects.get("previs") or bpy.data.objects.new("previs", data)
    if ob.name not in scene.collection.objects:
        scene.collection.objects.link(ob)
    data.sensor_fit = "VERTICAL"
    data.sensor_height = 24
    data.lens = 12 / math.tan(math.radians(cam["vfov"]) / 2)
    data.clip_start, data.clip_end = 0.03, 500
    ob.location = cam["pos"]
    ob.rotation_euler = (Vector(cam["look"]) - Vector(cam["pos"])).to_track_quat("-Z", "Y").to_euler()
    scene.camera = ob


def main():
    args = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else sys.argv[1:]
    with open(args[0], encoding="utf-8") as f:
        job = json.load(f)
    scene_data = ps.load(job["scene"])
    width, height = ps.frame_size(scene_data)
    scene = reset()
    setup(scene, width, height, linear(ps.hex_rgb(scene_data.get("background"), (0.055, 0.065, 0.08))))
    shots = {s["id"]: s for s in scene_data["shots"]}
    for item in job["frames"]:
        shot = shots[item["shot"]]
        build(scene, ps.scene_meshes(scene_data, item["t"], pov=shot.get("pov")))
        camera(scene, ps.camera_at(shot, item["t"]))
        scene.render.filepath = item["path"]
        bpy.ops.render.render(write_still=True)
    if job.get("blend"):
        bpy.ops.wm.save_as_mainfile(filepath=job["blend"])
    print("PREVIS_BLENDER_DONE", bpy.app.version_string)


if __name__ == "__main__":
    main()
