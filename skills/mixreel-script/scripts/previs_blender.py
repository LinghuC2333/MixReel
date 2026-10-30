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
from mathutils import Matrix, Vector  # noqa: E402

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


def lens(data, vfov):
    data.sensor_fit = "VERTICAL"
    data.sensor_height = 24
    data.lens = 12 / math.tan(math.radians(vfov) / 2)
    data.clip_start, data.clip_end = 0.03, 500


def aim(cam):
    return (Vector(cam["look"]) - Vector(cam["pos"])).to_track_quat("-Z", "Y").to_euler()


def camera(scene, cam):
    data = bpy.data.cameras.get("previs") or bpy.data.cameras.new("previs")
    ob = bpy.data.objects.get("previs") or bpy.data.objects.new("previs", data)
    if ob.name not in scene.collection.objects:
        scene.collection.objects.link(ob)
    lens(data, cam["vfov"])
    ob.location = cam["pos"]
    ob.rotation_euler = aim(cam)
    scene.camera = ob


# Scrubbable scene file

def _fcurves(ob):
    """F-curves of an object's action, before and after Blender 4.4 moved them into slots."""
    act = ob.animation_data.action
    if hasattr(act, "layers") and act.layers:
        from bpy_extras import anim_utils
        return anim_utils.action_get_channelbag_for_slot(act, ob.animation_data.action_slot).fcurves
    return act.fcurves


def _key(ob, path, values, frames):
    """Key a property on many frames at once; values holds one tuple per frame."""
    ob.keyframe_insert(path, frame=frames[0])
    for fc in _fcurves(ob):
        if fc.data_path != path:
            continue
        fc.keyframe_points.clear()
        fc.keyframe_points.add(len(frames))
        co = [x for f, v in zip(frames, values) for x in (f, v[fc.array_index])]
        fc.keyframe_points.foreach_set("co", co)
        for kp in fc.keyframe_points:
            kp.interpolation = "LINEAR"
        fc.update()


def _animate(ob, samples):
    """samples: (frame, location, rotation) with only the frames where something changes."""
    frames = [f for f, _, _ in samples]
    _key(ob, "location", [tuple(l) for _, l, _ in samples], frames)
    _key(ob, "rotation_euler", [tuple(r) for _, _, r in samples], frames)


def _changes(values, same):
    """Indices where a value differs from its neighbour, so holds need only their two ends."""
    keep = [0]
    for k in range(1, len(values)):
        if not same(values[k], values[k - 1]) or (k + 1 < len(values) and not same(values[k], values[k + 1])):
            keep.append(k)
    if keep[-1] != len(values) - 1:
        keep.append(len(values) - 1)
    return keep


def _collection(scene, name):
    col = bpy.data.collections.get(name)
    if col is None:
        col = bpy.data.collections.new(name)
        scene.collection.children.link(col)
    return col


def build_film(scene, scene_data):
    """Rebuild the scene as the whole film: every piece keyed once a frame where it moves, every
    shot's camera keyed over its shot and a timeline marker at each cut bound to that camera."""
    for o in list(bpy.data.objects):
        bpy.data.objects.remove(o, do_unlink=True)
    fps, count, pieces, cameras = ps.film(scene_data)
    scene.render.fps = round(fps)
    scene.frame_start, scene.frame_end = 1, count

    for key, p in pieces.items():
        name = ".".join(str(k) for k in key)
        me = bpy.data.meshes.new(name)
        me.from_pydata([tuple(v) for v in p["vertices"]], [], [tuple(x) for x in p["faces"]])
        for poly in me.polygons:
            poly.use_smooth = True
        if hasattr(me, "set_sharp_from_angle"):
            me.set_sharp_from_angle(angle=math.radians(40))
        me.materials.append(material(p["rgb"]))
        ob = bpy.data.objects.new(name, me)
        _collection(scene, p["owner"]).objects.link(ob)

        mats = p["matrices"]
        shown = [m is not None for m in mats]
        # A hidden piece holds its last placement so the curves stay calm.
        held, last = [], next(m for m in mats if m is not None)
        for m in mats:
            last = m if m is not None else last
            held.append(last)
        loc_rot, prev = [], None
        for m in held:
            loc, quat, scale = Matrix(m.tolist()).decompose()
            prev = quat.to_euler("XYZ", prev) if prev else quat.to_euler("XYZ")
            loc_rot.append((loc, prev))
        ob.scale = scale
        same = lambda a, b: (abs(a - b) < 1e-7).all()
        if all(same(m, held[0]) for m in held):
            ob.location, ob.rotation_euler = loc_rot[0]
        else:
            _animate(ob, [(k + 1, *loc_rot[k]) for k in _changes(held, same)])
        if not all(shown):
            flips = [k for k in range(count) if k == 0 or shown[k] != shown[k - 1]]
            for k in flips:
                ob.hide_viewport = ob.hide_render = not shown[k]
                ob.keyframe_insert("hide_viewport", frame=k + 1)
                ob.keyframe_insert("hide_render", frame=k + 1)

    col = _collection(scene, "cameras")
    scene.timeline_markers.clear()
    for shot in scene_data.get("shots", []):
        data = bpy.data.cameras.new(shot["id"])
        lens(data, shot["vfov"])
        ob = bpy.data.objects.new(shot["id"], data)
        col.objects.link(ob)
        samples = cameras[shot["id"]]
        poses = [(Vector(c["pos"]), aim(c)) for _, c in samples]
        same = lambda a, b: (a[0] - b[0]).length < 1e-7 and (Vector(a[1]) - Vector(b[1])).length < 1e-7
        if all(same(p, poses[0]) for p in poses):
            ob.location, ob.rotation_euler = poses[0]
        else:
            _animate(ob, [(samples[k][0] + 1, *poses[k]) for k in _changes(poses, same)])
        frame = samples[0][0] + 1
        if not any(m.frame == frame for m in scene.timeline_markers):
            scene.timeline_markers.new(shot["id"], frame=frame).camera = ob
        if scene.camera is None:
            scene.camera = ob

    # Open on the first shot, looking through its camera with the render's look.
    scene.frame_set(1)
    for screen in bpy.data.screens:
        for area in screen.areas:
            if area.type != "VIEW_3D":
                continue
            for space in area.spaces:
                if space.type == "VIEW_3D":
                    sh = space.shading
                    sh.type, sh.light, sh.color_type = "SOLID", "STUDIO", "MATERIAL"
                    sh.show_object_outline, sh.show_cavity, sh.show_shadows = True, True, True
                    space.overlay.show_floor = False
                    space.region_3d.view_perspective = "CAMERA"


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
        build_film(scene, scene_data)
        bpy.ops.wm.save_as_mainfile(filepath=job["blend"])
    print("PREVIS_BLENDER_DONE", bpy.app.version_string)


if __name__ == "__main__":
    main()
