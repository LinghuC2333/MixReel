"""Software renderer for previs scenes, using only numpy and Pillow.

It draws flat-shaded proxies with a depth buffer and object outlines. It has
no shadows, depth of field or anti-aliasing, so near-touching overlaps can be
off by a few pixels. It also draws the top-down plan base for every backend.
"""

import math

import numpy as np
from PIL import Image

import previs_scene as ps

NEAR = 0.03
LIGHT = np.array([0.35, -0.45, 0.82]) / np.linalg.norm([0.35, -0.45, 0.82])


def _clip_near(tri):
    """Clip one camera-space triangle against z = NEAR; returns 0, 1 or 2 triangles."""
    out = []
    for i in range(3):
        a, b = tri[i], tri[(i + 1) % 3]
        if a[2] >= NEAR:
            out.append(a)
        if (a[2] >= NEAR) != (b[2] >= NEAR):
            u = (NEAR - a[2]) / (b[2] - a[2])
            out.append(a + (b - a) * u)
    return [np.array([out[0], out[k], out[k + 1]]) for k in range(1, len(out) - 1)]


def render(meshes, cam_pos, cam_look, width, height, vfov=None, ortho_height=None, background=(0.055, 0.065, 0.08)):
    """Render meshes from a camera. Give vfov in degrees, or ortho_height in metres for a straight orthographic view."""
    tris, cols, oids = ps.triangles(meshes)
    right, up, fwd = ps.camera_basis(cam_pos, cam_look)
    normals = np.cross(tris[:, 1] - tris[:, 0], tris[:, 2] - tris[:, 0])
    lens = np.linalg.norm(normals, axis=1)
    keep = lens > 1e-12
    tris, cols, oids, normals = tris[keep], cols[keep], oids[keep], normals[keep] / lens[keep, None]
    rel = tris - np.array(cam_pos, float)
    cs = np.stack([rel @ right, rel @ up, rel @ fwd], axis=-1)
    view = np.abs(normals @ fwd)
    shade = 0.30 + 0.45 * np.clip(np.abs(normals @ LIGHT), 0, 1) + 0.15 * view
    rgb = np.clip(cols * shade[:, None], 0, 1)

    if ortho_height is None:
        f = (height / 2) / math.tan(math.radians(vfov) / 2)
        work = []
        for i in range(len(cs)):
            z = cs[i, :, 2]
            if (z >= NEAR).all():
                work.append((cs[i], i))
            elif (z >= NEAR).any():
                work += [(t, i) for t in _clip_near(cs[i])]
    else:
        f = height / ortho_height
        work = [(cs[i], i) for i in range(len(cs))]

    color = np.empty((height, width, 3))
    color[:] = background
    depth = np.full((height, width), -np.inf)
    ident = np.full((height, width), -1)
    for tri, i in work:
        if ortho_height is None:
            sx = width / 2 + f * tri[:, 0] / tri[:, 2]
            sy = height / 2 - f * tri[:, 1] / tri[:, 2]
            key = 1.0 / tri[:, 2]
        else:
            sx = width / 2 + f * tri[:, 0]
            sy = height / 2 - f * tri[:, 1]
            key = -tri[:, 2]
        x0, x1 = max(0, int(math.floor(sx.min()))), min(width - 1, int(math.ceil(sx.max())))
        y0, y1 = max(0, int(math.floor(sy.min()))), min(height - 1, int(math.ceil(sy.max())))
        if x0 > x1 or y0 > y1:
            continue
        area = (sx[1] - sx[0]) * (sy[2] - sy[0]) - (sx[2] - sx[0]) * (sy[1] - sy[0])
        if abs(area) < 1e-9:
            continue
        px, py = np.meshgrid(np.arange(x0, x1 + 1) + 0.5, np.arange(y0, y1 + 1) + 0.5)
        w0 = ((sx[1] - px) * (sy[2] - py) - (sx[2] - px) * (sy[1] - py)) / area
        w1 = ((sx[2] - px) * (sy[0] - py) - (sx[0] - px) * (sy[2] - py)) / area
        w2 = 1 - w0 - w1
        inside = (w0 >= 0) & (w1 >= 0) & (w2 >= 0)
        if not inside.any():
            continue
        k = w0 * key[0] + w1 * key[1] + w2 * key[2]
        region = depth[y0:y1 + 1, x0:x1 + 1]
        # Coplanar faces keep whichever was drawn first instead of flickering.
        win = inside & (k > region + 1e-6 * np.abs(k))
        region[win] = k[win]
        color[y0:y1 + 1, x0:x1 + 1][win] = rgb[i]
        ident[y0:y1 + 1, x0:x1 + 1][win] = oids[i]

    # Outline where one object meets another or the background.
    edge = np.zeros_like(ident, bool)
    edge[:, 1:] |= ident[:, 1:] != ident[:, :-1]
    edge[1:, :] |= ident[1:, :] != ident[:-1, :]
    floor_ids = {j for j, m in enumerate(meshes) if m[0] == "floor"}
    if floor_ids:
        on_floor = np.isin(ident, list(floor_ids))
        both_floor = np.zeros_like(edge)
        both_floor[:, 1:] |= on_floor[:, 1:] & on_floor[:, :-1]
        both_floor[1:, :] |= on_floor[1:, :] & on_floor[:-1, :]
        edge &= ~both_floor
    color[edge] *= 0.55
    return Image.fromarray((color * 255).round().astype(np.uint8))


def render_shot(scene, shot, t, width, height):
    cam = ps.camera_at(shot, t)
    meshes = ps.scene_meshes(scene, t, pov=shot.get("pov"))
    bg = ps.hex_rgb(scene.get("background"), (0.055, 0.065, 0.08))
    return render(meshes, cam["pos"], cam["look"], width, height, vfov=cam["vfov"], background=bg)


def render_plan(scene, t, bounds, width, height):
    """Straight-down view of the scene at time t over bounds (xmin, xmax, ymin, ymax)."""
    xmin, xmax, ymin, ymax = bounds
    cx, cy = (xmin + xmax) / 2, (ymin + ymax) / 2
    meshes = ps.scene_meshes(scene, t)
    bg = ps.hex_rgb(scene.get("background"), (0.055, 0.065, 0.08))
    return render(meshes, [cx, cy, 200.0], [cx, cy, 0.0], width, height,
                  ortho_height=ymax - ymin, background=bg)
