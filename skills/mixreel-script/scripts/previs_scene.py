"""Scene file for a spatial previs, shared by every renderer.

The scene file is JSON. Units are metres, Z points up, the floor is z = 0.
Yaw is in degrees seen from above: 0 faces +Y, 90 faces -X.

{
  "name": "Coronation blocking",
  "frame": {"width": 540, "height": 960},        # delivery aspect, default 540 x 960
  "background": "#0e1116",
  "floor": {"center": [0, 1], "size": [14, 21], "color": "#262e38", "grid": 1.0},
  "props": [                                      # sets and plot props
    {"id": "throne", "label": "Throne", "color": "#d49e38",
     "pos": [0, 6.8, 1.2], "yaw": 180,            # or "keys" like an actor, with pos and yaw
     "parts": [{"box": {"center": [0, 0, 0.12], "size": [1.5, 1.25, 0.25]}}]}
  ],
  "actors": [                                     # one proxy per named character
    {"id": "Elvina", "label": "Elvina", "color": "#a661b8",
     "height": 1.98, "dress": true, "long_hair": true,
     "items": [{"at": "right_arm", "color": "#bcc8d4",
                "box": {"center": [0, 0, -0.95], "size": [0.055, 0.035, 0.8]}}],
     "keys": [{"t": 0, "pos": [-0.6, -1, 0], "yaw": 0, "pose": "stand", "arm": 0},
              {"t": 3.8, "look_at": "King"},
              {"t": 10.6, "pos": [-0.6, 0.4, 0]}]}
  ],
  "shots": [
    {"id": "S01", "title": "Ring of guards", "start": 0, "end": 2, "vfov": 50,
     "camera": {"start": {"pos": [0.2, -5.8, 2.6], "look": [0, 2.6, 1.6]},
                "end":   {"pos": [0.2, -5.35, 2.6], "look": [0, 2.6, 1.6]}},
     "pov": "Aiden",                              # optional, hides that actor except the right arm and its items
     "frames": ["start", "end"]}                  # optional, add "mid" for long moves
  ]
}

Parts and items use four shapes, each in the owner's own frame.
  box       {"center": [x, y, z], "size": [w, d, h], "yaw": degrees}
  ellipsoid {"center": [x, y, z], "radii": [rx, ry, rz]}
  rod       {"from": [x, y, z], "to": [x, y, z], "radius": r}
  cone      {"from": [x, y, z], "to": [x, y, z], "r1": r, "r2": r}
A part may carry its own "color".

Colours are display colours, as on screen. An actor whose label is "" gets no
name in the plan, which keeps crowds readable.

Actor keys run on the film's one timeline. A key may set pos, yaw or look_at
(an actor id or an [x, y] point), pose (stand, sit, kneel, lie), seat (hip
height in metres when sitting, default 0.45) and arm (right arm raise in
degrees, 0 hangs down or rests on the lap when sitting, 90 points forward). Fields a key leaves out carry over
from the previous key. Between two keys values ease in and out; a pose changes
when its key is reached.

Actor items are held props. "body" items sit in the actor's frame, feet at
the origin, facing +Y. "right_arm" items sit in the arm's frame, shoulder at
the origin, the arm hanging along -Z with the hand at z = -0.48; they follow
the arm. Body and items are drawn for a 1.98 tall proxy and scale with height.
"""

import json
import math

import numpy as np

REF_HEIGHT = 1.98
POSES = ("stand", "sit", "kneel", "lie")
SHAPES = ("box", "ellipsoid", "rod", "cone")
EYE_COLOR = (0.08, 0.09, 0.11)


class SceneError(ValueError):
    pass


def hex_rgb(value, default=(0.6, 0.6, 0.6)):
    if value is None:
        return default
    if isinstance(value, (list, tuple)):
        return tuple(float(v) for v in value[:3])
    s = str(value).lstrip("#")
    if len(s) != 6:
        raise SceneError(f"colour {value!r} is not #rrggbb")
    return tuple(int(s[i:i + 2], 16) / 255 for i in (0, 2, 4))


def load(path):
    with open(path, encoding="utf-8") as f:
        scene = json.load(f)
    check(scene)
    return scene


def check(scene):
    ids = set()
    for group in ("props", "actors"):
        for obj in scene.get(group, []):
            if "id" not in obj:
                raise SceneError(f"an entry in {group} has no id")
            if obj["id"] in ids:
                raise SceneError(f"id {obj['id']!r} is used twice")
            ids.add(obj["id"])
            for part in obj.get("parts", []) + obj.get("items", []):
                if not any(k in part for k in SHAPES):
                    raise SceneError(f"{obj['id']}: a part needs one of {', '.join(SHAPES)}")
    for actor in scene.get("actors", []):
        if not actor.get("keys"):
            raise SceneError(f"actor {actor['id']!r} needs at least one key")
        if "pos" not in sorted(actor["keys"], key=lambda k: k.get("t", 0))[0]:
            raise SceneError(f"actor {actor['id']!r}: the first key needs pos")
        for k in actor["keys"]:
            if k.get("pose", "stand") not in POSES:
                raise SceneError(f"actor {actor['id']!r}: pose must be one of {', '.join(POSES)}")
    shot_ids = set()
    for shot in scene.get("shots", []):
        for field in ("id", "start", "end", "vfov", "camera"):
            if field not in shot:
                raise SceneError(f"shot {shot.get('id', '?')}: missing {field}")
        if shot["id"] in shot_ids:
            raise SceneError(f"shot id {shot['id']!r} is used twice")
        shot_ids.add(shot["id"])
        if shot["end"] <= shot["start"]:
            raise SceneError(f"shot {shot['id']}: end must be after start")
        if shot.get("pov") and shot["pov"] not in ids:
            raise SceneError(f"shot {shot['id']}: pov {shot['pov']!r} is not an actor")


def frame_size(scene):
    fr = scene.get("frame", {})
    return int(fr.get("width", 540)), int(fr.get("height", 960))


# Timeline

def smooth(u):
    u = min(1.0, max(0.0, u))
    return u * u * (3 - 2 * u)


def _filled_keys(obj):
    keys = sorted(obj.get("keys") or [{"t": 0, "pos": obj.get("pos", [0, 0, 0]), "yaw": obj.get("yaw", 0)}],
                  key=lambda k: k.get("t", 0))
    out, prev = [], {"pos": [0, 0, 0], "yaw": 0, "pose": "stand", "arm": 0, "seat": 0.45, "look_at": None}
    for k in keys:
        cur = dict(prev)
        cur.update(k)
        if "yaw" in k:
            cur["look_at"] = None
        cur.setdefault("t", 0)
        out.append(cur)
        prev = cur
    return out


def _yaw_toward(src, target):
    dx, dy = target[0] - src[0], target[1] - src[1]
    if abs(dx) < 1e-9 and abs(dy) < 1e-9:
        return None
    return math.degrees(math.atan2(-dx, dy))


def _angle_lerp(a, b, u):
    d = (b - a + 180) % 360 - 180
    return a + d * u


def raw_state(obj, t):
    keys = _filled_keys(obj)
    if t <= keys[0]["t"]:
        a, b, u = keys[0], keys[0], 0.0
    elif t >= keys[-1]["t"]:
        a, b, u = keys[-1], keys[-1], 0.0
    else:
        i = max(j for j, k in enumerate(keys) if k["t"] <= t)
        a, b = keys[i], keys[i + 1]
        u = smooth((t - a["t"]) / (b["t"] - a["t"]))
    return a, b, u


def states(scene, t):
    """Resolved pos, yaw (degrees), pose, arm and seat of every actor and prop at time t."""
    out, pending = {}, []
    for group in ("props", "actors"):
        for obj in scene.get(group, []):
            a, b, u = raw_state(obj, t)
            pos = [a["pos"][i] + (b["pos"][i] - a["pos"][i]) * u for i in range(3)]
            st = {"pos": pos, "yaw": None, "pose": a["pose"], "arm": a["arm"] + (b["arm"] - a["arm"]) * u,
                  "seat": a["seat"] + (b["seat"] - a["seat"]) * u}
            out[obj["id"]] = st
            pending.append((obj["id"], a, b, u))
    # Gaze targets need every position first.
    for oid, a, b, u in pending:
        def yaw_of(k):
            if k["look_at"] is None:
                return k["yaw"]
            tgt = k["look_at"]
            tgt = out[tgt]["pos"] if isinstance(tgt, str) else tgt
            y = _yaw_toward(out[oid]["pos"], tgt)
            return k["yaw"] if y is None else y
        out[oid]["yaw"] = _angle_lerp(yaw_of(a), yaw_of(b), u)
    return out


def shot_frames(shot, fps=24):
    names = shot.get("frames", ["start", "end"])
    times = {"start": shot["start"], "mid": (shot["start"] + shot["end"]) / 2,
             "end": max(shot["start"], shot["end"] - 1 / fps)}
    return [(n, times[n]) for n in names]


def camera_at(shot, t):
    cam = shot["camera"]
    a = cam["start"]
    b = cam.get("end", a)
    u = smooth((t - shot["start"]) / max(1e-6, shot["end"] - shot["start"]))
    pos = [a["pos"][i] + (b["pos"][i] - a["pos"][i]) * u for i in range(3)]
    look = [a["look"][i] + (b["look"][i] - a["look"][i]) * u for i in range(3)]
    return {"pos": pos, "look": look, "vfov": shot["vfov"]}


def camera_basis(pos, look):
    fwd = np.array(look, float) - np.array(pos, float)
    fwd /= np.linalg.norm(fwd)
    hint = np.array([0, 0, 1.0]) if abs(fwd[2]) < 0.999 else np.array([0, 1.0, 0])
    right = np.cross(fwd, hint)
    right /= np.linalg.norm(right)
    up = np.cross(right, fwd)
    return right, up, fwd


# Geometry

def _rot_x(deg):
    a = math.radians(deg)
    c, s = math.cos(a), math.sin(a)
    return np.array([[1, 0, 0], [0, c, -s], [0, s, c]])


def _rot_z(deg):
    a = math.radians(deg)
    c, s = math.cos(a), math.sin(a)
    return np.array([[c, -s, 0], [s, c, 0], [0, 0, 1]])


def _box(p):
    c, (w, d, h) = np.array(p["center"], float), p["size"]
    v = np.array([[x, y, z] for z in (-.5, .5) for y in (-.5, .5) for x in (-.5, .5)]) * [w, d, h]
    v = v @ _rot_z(p.get("yaw", 0)).T + c
    f = [(0, 2, 3, 1), (4, 5, 7, 6), (0, 1, 5, 4), (2, 6, 7, 3), (0, 4, 6, 2), (1, 3, 7, 5)]
    return v, f


def _ellipsoid(p, seg=12, rings=8):
    c, r = np.array(p["center"], float), np.array(p["radii"], float)
    v = [[0, 0, -1]]
    for i in range(1, rings):
        th = math.pi * i / rings - math.pi / 2
        for j in range(seg):
            ph = 2 * math.pi * j / seg
            v.append([math.cos(th) * math.cos(ph), math.cos(th) * math.sin(ph), math.sin(th)])
    v.append([0, 0, 1])
    v = np.array(v) * r + c
    f, top = [], len(v) - 1
    for j in range(seg):
        f.append((0, 1 + (j + 1) % seg, 1 + j))
    for i in range(rings - 2):
        for j in range(seg):
            a, b = 1 + i * seg + j, 1 + i * seg + (j + 1) % seg
            f.append((a, b, b + seg, a + seg))
    base = 1 + (rings - 2) * seg
    for j in range(seg):
        f.append((base + j, base + (j + 1) % seg, top))
    return v, f


def _cone(a, b, r1, r2, seg=12):
    a, b = np.array(a, float), np.array(b, float)
    axis = b - a
    length = np.linalg.norm(axis)
    if length < 1e-9:
        return np.zeros((0, 3)), []
    w = axis / length
    hint = np.array([1.0, 0, 0]) if abs(w[0]) < 0.9 else np.array([0, 1.0, 0])
    u = np.cross(w, hint)
    u /= np.linalg.norm(u)
    v2 = np.cross(w, u)
    ring = [math.cos(2 * math.pi * j / seg) * u + math.sin(2 * math.pi * j / seg) * v2 for j in range(seg)]
    # A pointed end is one vertex, so no zero-area faces reach the renderer.
    ends = []
    for centre, r in ((a, r1), (b, r2)):
        ends.append([centre] if r <= 1e-6 else [centre + r * d for d in ring])
    verts = ends[0] + ends[1]
    lo = lambda j: 0 if len(ends[0]) == 1 else j % seg
    hi = lambda j: len(ends[0]) + (0 if len(ends[1]) == 1 else j % seg)
    f = []
    for j in range(seg):
        quad = [lo(j), lo(j + 1), hi(j + 1), hi(j)]
        f.append(tuple(dict.fromkeys(quad)))
    if len(ends[0]) > 1:
        verts.append(a)
        f += [(len(verts) - 1, (j + 1) % seg, j) for j in range(seg)]
    if len(ends[1]) > 1:
        verts.append(b)
        f += [(len(verts) - 1, hi(j), hi(j + 1)) for j in range(seg)]
    return np.array(verts), f


def primitive(part):
    if "box" in part:
        return _box(part["box"])
    if "ellipsoid" in part:
        return _ellipsoid(part["ellipsoid"])
    if "rod" in part:
        p = part["rod"]
        return _cone(p["from"], p["to"], p["radius"], p["radius"])
    p = part["cone"]
    return _cone(p["from"], p["to"], p["r1"], p["r2"])


def _person_parts(actor, st):
    """Proxy body as (part dict, frame) pairs; frame is 'body' or 'right_arm'."""
    E = lambda c, r, **k: dict(ellipsoid={"center": c, "radii": r}, **k)
    R = lambda a, b, r, **k: dict(rod={"from": a, "to": b, "radius": r}, **k)
    C = lambda a, b, r1, r2, **k: dict(cone={"from": a, "to": b, "r1": r1, "r2": r2}, **k)
    s = actor.get("height", REF_HEIGHT) / REF_HEIGHT
    pose = st["pose"]
    dz = {"stand": 0.0, "lie": 0.0, "sit": st["seat"] / s - 0.88, "kneel": -0.42}[pose]
    up = lambda p: [p[0], p[1], p[2] + dz]
    parts = [E(up([0, 0, 1.25]), [.28, .17, .38]), E(up([0, 0, .93]), [.23, .16, .19]),
             R(up([0, 0, 1.5]), up([0, 0, 1.65]), .085), dict(E(up([0, 0, 1.77]), [.15, .14, .21]), group="head"),
             E(up([0, .145, 1.78]), [.045, .055, .05])]
    parts += [E(up([x, .124, 1.83]), [.022, .024, .018], color=EYE_COLOR) for x in (-.06, .06)]
    if actor.get("long_hair"):
        parts.append(E(up([0, -.08, 1.60]), [.17, .12, .30]))
    for x in (-.14, .14):
        if pose == "sit":
            hip = .88 + dz
            parts += [R([x, 0, hip], [x, .5, hip], .095), R([x, .5, hip], [x, .55, .2], .085), E([x, .62, .12], [.11, .2, .09])]
        elif pose == "kneel":
            parts += [R([x, 0, .48], [x, .12, .09], .09), R([x, .12, .09], [x, -.4, .09], .085), E([x, -.45, .08], [.11, .16, .08])]
        else:
            parts += [R([x, 0, .9], [x, .02, .15], .09), E([x, .08, .09], [.11, .2, .09])]
    if actor.get("dress"):
        hem = {"sit": max(.1, .55 + dz), "kneel": .06}.get(pose, .04)
        parts.append(C([0, .15 if pose == "sit" else 0, hem], up([0, 0, .92]), .40, .19))
    if pose == "sit":
        parts += [R(up([-.3, 0, 1.45]), up([-.2, .35, .95]), .065), E(up([-.2, .37, .95]), [.07, .09, .07])]
    else:
        parts += [R(up([-.3, 0, 1.45]), up([-.34, .08, 1.0]), .065), E(up([-.34, .08, 1.0]), [.07, .07, .085])]
    out = [(p, "body") for p in parts]
    out += [(dict(R([0, 0, 0], [0, 0, -.48], .07), group="right_arm"), "right_arm"),
            (dict(E([0, 0, -.48], [.075, .075, .09]), group="right_arm"), "right_arm")]
    for item in actor.get("items", []):
        frame = item.get("at", "body")
        out.append((dict(item, group="right_arm" if frame == "right_arm" else "item"), frame))
    return out, s, dz


def _affine(rot, move):
    m = np.eye(4)
    m[:3, :3], m[:3, 3] = rot, move
    return m


def actor_parts(actor, st, hide_body=False):
    """Body pieces as (key, vertices, faces, rgb, matrix). Vertices sit in the piece's own frame and the
    4x4 matrix places them in the world; the key stays the same while the pose's shape does."""
    color = hex_rgb(actor.get("color"))
    parts, s, dz = _person_parts(actor, st)
    body = _affine(_rot_z(st["yaw"]) * s, st["pos"])
    if st["pose"] == "lie":
        body = body @ _affine(_rot_x(90), [0, 0, .17])
    # Seated, the arm at 0 rests the hand on the lap like the left one.
    arm = body @ _affine(_rot_x(st["arm"] + (40 if st["pose"] == "sit" else 0)), [.30, 0, 1.45 + dz])
    shape = st["pose"] + (f"{st['seat']:.3f}" if st["pose"] == "sit" else "")
    out = []
    for i, (part, frame) in enumerate(parts):
        if hide_body and part.get("group") != "right_arm":
            continue
        v, f = primitive(part)
        if len(v):
            out.append(((shape, i), v, f, hex_rgb(part.get("color"), color), arm if frame == "right_arm" else body))
    return out


def prop_parts(prop, st):
    color = hex_rgb(prop.get("color"))
    m = _affine(_rot_z(st["yaw"]), st["pos"])
    return [(i, *primitive(part), hex_rgb(part.get("color"), color), m) for i, part in enumerate(prop.get("parts", []))]


def _placed(pieces):
    return [(v @ m[:3, :3].T + m[:3, 3], f, c) for _, v, f, c, m in pieces]


def actor_meshes(actor, st, hide_body=False):
    return _placed(actor_parts(actor, st, hide_body))


def prop_meshes(prop, st):
    return _placed(prop_parts(prop, st))


def floor_meshes(scene):
    fl = scene.get("floor")
    if not fl:
        return []
    cx, cy = fl.get("center", [0, 0])
    w, d = fl.get("size", [20, 20])
    base = hex_rgb(fl.get("color"), (.15, .18, .22))
    out = [(*_box({"center": [cx, cy, -.05], "size": [w, d, .1]}), base)]
    step = fl.get("grid", 1.0)
    if step:
        line = tuple(min(1, c * 1.7 + .03) for c in base)
        x = math.ceil((cx - w / 2) / step) * step
        while x <= cx + w / 2 + 1e-6:
            out.append((*_box({"center": [x, cy, .003], "size": [.015, d, .006]}), line))
            x += step
        y = math.ceil((cy - d / 2) / step) * step
        while y <= cy + d / 2 + 1e-6:
            out.append((*_box({"center": [cx, y, .004], "size": [w, .015, .006]}), line))
            y += step
    return out


def scene_meshes(scene, t, pov=None):
    """Every mesh at time t as (object id, vertices, faces, rgb)."""
    st = states(scene, t)
    out = [("floor", v, f, c) for v, f, c in floor_meshes(scene)]
    for prop in scene.get("props", []):
        out += [(prop["id"], v, f, c) for v, f, c in prop_meshes(prop, st[prop["id"]])]
    for actor in scene.get("actors", []):
        out += [(actor["id"], v, f, c) for v, f, c in actor_meshes(actor, st[actor["id"]], hide_body=actor["id"] == pov)]
    return out


def film(scene):
    """The whole film sampled once a frame, for a scene file people can scrub.

    Returns (fps, frame count, pieces, cameras). pieces maps a stable key to its owner, vertices
    in its own frame, faces, rgb and one 4x4 world matrix per frame, None while hidden; a pose
    change hides one set of pieces and shows another. cameras maps each shot id to its
    (frame index, camera) samples from the shot's start to its end."""
    fps = scene.get("fps", 24)
    shots = scene.get("shots", [])
    count = max(1, round(max([s["end"] for s in shots] + [0]) * fps))
    pieces = {}

    def put(key, owner, v, f, c, m, k):
        if key not in pieces:
            pieces[key] = {"owner": owner, "vertices": v, "faces": f, "rgb": c, "matrices": [None] * count}
        pieces[key]["matrices"][k] = m

    first = {s["id"]: round(s["start"] * fps) for s in shots}
    for k in range(count):
        t = k / fps
        # On screen is the latest shot to have started, as the cut markers give.
        shot = max((s for s in shots if first[s["id"]] <= k), key=lambda s: first[s["id"]], default=None)
        st = states(scene, t)
        for prop in scene.get("props", []):
            for i, v, f, c, m in prop_parts(prop, st[prop["id"]]):
                put((prop["id"], i), prop["id"], v, f, c, m, k)
        for actor in scene.get("actors", []):
            pov = shot is not None and shot.get("pov") == actor["id"]
            for key, v, f, c, m in actor_parts(actor, st[actor["id"]], hide_body=pov):
                put((actor["id"],) + key, actor["id"], v, f, c, m, k)
    for i, (v, f, c) in enumerate(floor_meshes(scene)):
        pieces[("floor", i)] = {"owner": "floor", "vertices": v, "faces": f, "rgb": c,
                                "matrices": [np.eye(4)] * count}
    cameras = {}
    for shot in shots:
        a, b = first[shot["id"]], min(count, round(shot["end"] * fps))
        cameras[shot["id"]] = [(k, camera_at(shot, k / fps)) for k in range(a, max(a + 1, b))]
    return fps, count, pieces, cameras


def triangles(meshes):
    tris, cols, oids = [], [], []
    for i, (oid, v, f, c) in enumerate(meshes):
        for face in f:
            for k in range(1, len(face) - 1):
                tris.append([v[face[0]], v[face[k]], v[face[k + 1]]])
                cols.append(c)
                oids.append(i)
    return np.array(tris, float).reshape(-1, 3, 3), np.array(cols, float).reshape(-1, 3), np.array(oids, int)
