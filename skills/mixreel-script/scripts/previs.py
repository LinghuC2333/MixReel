#!/usr/bin/env python3
"""Render a spatial previs from a scene file: a top-down plan, start and end
frames for each shot, a numbered storyboard sheet and a review sheet.

  python3 previs.py SCENE.json --out DIR [--shots S01,S07] [--backend auto]

Backends, in the order to try them:
  blender  the Blender application, found on PATH, in $BLENDER or in the usual
           install folders. auto picks it when present.
  bpy      Blender's bpy package from PyPI, run through uv in a throwaway
           environment. It downloads several hundred MB, so ask the user first.
  raster   numpy and Pillow only. Flat shading without shadows or depth of
           field, good enough for positions, occlusion, screen direction and
           framing. Every output is marked as a rough render.
auto never downloads; when Blender is missing it stops and says so.

  python3 previs.py --schema   prints the scene file format.
"""

import argparse
import glob
import json
import math
import os
import shutil
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import previs_scene as ps  # noqa: E402

ROUGH_NOTE = ("rough render: flat shading, no shadows or depth of field; "
              "overlaps between near-touching objects can be off by a few pixels")


def find_blender(explicit=None):
    candidates = [explicit, os.environ.get("BLENDER"), shutil.which("blender"),
                  "/Applications/Blender.app/Contents/MacOS/Blender",
                  os.path.expanduser("~/Applications/Blender.app/Contents/MacOS/Blender"),
                  "/snap/bin/blender"]
    candidates += sorted(glob.glob("/opt/blender*/blender"), reverse=True)
    candidates += sorted(glob.glob("C:/Program Files/Blender Foundation/Blender*/blender.exe"), reverse=True)
    for c in candidates:
        if c and os.path.isfile(c) and os.access(c, os.X_OK):
            return c
    return None


def blender_version(exe):
    try:
        out = subprocess.run([exe, "--version"], capture_output=True, text=True, timeout=60).stdout
        return out.strip().splitlines()[0]
    except Exception:
        return "Blender (version unknown)"


def find_font(explicit=None):
    from PIL import ImageFont
    candidates = [explicit, "/System/Library/Fonts/PingFang.ttc", "/System/Library/Fonts/Hiragino Sans GB.ttc",
                  "/System/Library/Fonts/STHeiti Medium.ttc", "/System/Library/Fonts/Supplemental/Arial Unicode.ttf",
                  "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
                  "/usr/share/fonts/noto-cjk/NotoSansCJK-Regular.ttc", "C:/Windows/Fonts/msyh.ttc",
                  "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"]
    for c in candidates:
        if c and os.path.isfile(c):
            return lambda size, c=c: ImageFont.truetype(c, size)
    return lambda size: ImageFont.load_default(size)


# Frames

def frame_jobs(scene, wanted, out_dir):
    jobs = []
    for shot in scene["shots"]:
        if wanted and shot["id"] not in wanted:
            continue
        for name, t in ps.shot_frames(shot, scene.get("fps", 24)):
            jobs.append({"shot": shot["id"], "frame": name, "t": t,
                         "path": os.path.join(out_dir, "shots", f"{shot['id']}_{name}.png")})
    return jobs


def run_blender(cmd, job, out_dir):
    path = os.path.join(out_dir, ".previs_job.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(job, f, ensure_ascii=False)
    try:
        res = subprocess.run(cmd + [path], capture_output=True, text=True)
    finally:
        os.remove(path)
    if res.returncode != 0 or "PREVIS_BLENDER_DONE" not in res.stdout:
        sys.stderr.write(res.stdout[-3000:] + res.stderr[-3000:])
        raise SystemExit("Blender rendering failed; see the log above.")
    return res.stdout


def render_frames(scene_path, scene, jobs, args, out_dir):
    backend = args.backend
    exe = find_blender(args.blender) if backend in ("auto", "blender") else None
    if backend == "auto":
        if not exe:
            sys.stderr.write(
                "Blender was not found on PATH, in $BLENDER or in the usual install folders.\n"
                "Ask the user to install Blender (free, blender.org) and rerun, or with their consent\n"
                "rerun with --backend bpy (downloads the bpy package through uv), or --backend raster.\n")
            raise SystemExit(3)
        backend = "blender"
    if backend == "blender" and not exe:
        raise SystemExit("Blender was not found; pass --blender PATH.")

    job = {"scene": os.path.abspath(scene_path), "frames": jobs,
           "blend": os.path.join(out_dir, "previs.blend") if args.save_blend else None}
    if backend == "blender":
        run_blender([exe, "-b", "--factory-startup", "--python", os.path.join(HERE, "previs_blender.py"), "--"], job, out_dir)
        return {"backend": "blender", "renderer": blender_version(exe), "rough": False}
    if backend == "bpy":
        uv = shutil.which("uv")
        if not uv:
            raise SystemExit("--backend bpy needs uv (https://docs.astral.sh/uv/); otherwise use --backend raster.")
        cmd = [uv, "run", "--no-project", "--python", args.bpy_python, "--with", f"bpy{args.bpy_version}",
               "--with", "numpy", "python", os.path.join(HERE, "previs_blender.py"), "--"]
        log = run_blender(cmd, job, out_dir)
        version = log.split("PREVIS_BLENDER_DONE", 1)[1].strip().splitlines()[0]
        return {"backend": "bpy", "renderer": f"bpy {version}", "rough": False}

    import previs_raster as pr
    width, height = ps.frame_size(scene)
    shots = {s["id"]: s for s in scene["shots"]}
    for j in jobs:
        pr.render_shot(scene, shots[j["shot"]], j["t"], width, height).save(j["path"])
    return {"backend": "raster", "renderer": "previs_raster (numpy + Pillow)", "rough": True}


# Plan

def plan_bounds(scene, t, pad=0.8):
    fl = scene.get("floor")
    xs, ys = [], []
    if fl:
        cx, cy = fl.get("center", [0, 0])
        w, d = fl.get("size", [20, 20])
        xs += [cx - w / 2, cx + w / 2]
        ys += [cy - d / 2, cy + d / 2]
    else:
        for _, v, _, _ in ps.scene_meshes(scene, t):
            xs += [v[:, 0].min(), v[:, 0].max()]
            ys += [v[:, 1].min(), v[:, 1].max()]
    for shot in scene["shots"]:
        p = shot["camera"]["start"]["pos"]
        xs.append(p[0])
        ys.append(p[1])
    return min(xs) - pad, max(xs) + pad, min(ys) - pad, max(ys) + pad


def draw_plan(scene, t, font, path, rough):
    import previs_raster as pr
    from PIL import ImageDraw
    xmin, xmax, ymin, ymax = plan_bounds(scene, t)
    k = 1400 / max(xmax - xmin, ymax - ymin)
    width, height = int((xmax - xmin) * k), int((ymax - ymin) * k)
    img = pr.render_plan(scene, t, (xmin, xmax, ymin, ymax), width, height)
    draw = ImageDraw.Draw(img)
    to_px = lambda x, y: ((x - xmin) * k, (ymax - y) * k)
    st = ps.states(scene, t)
    boxes = []
    big, small = font(max(16, int(k * 0.32))), font(max(14, int(k * 0.26)))

    def place(text, anchor, fill, f, r=None):
        r = r if r is not None else k * 0.45
        bb = f.getbbox(text)
        tw, th = bb[2] - bb[0], bb[3] - bb[1]
        ax, ay = anchor
        spots = [(0, -1), (0, 1), (1, 0), (-1, 0), (1, -1), (-1, -1), (1, 1), (-1, 1)]
        for dx, dy in [(x * r * m, y * r * m) for m in (1, 2, 3) for x, y in spots]:
            x, y = ax + dx - tw / 2, ay + dy - th / 2
            box = (x - 3, y - 3, x + tw + 3, y + th + 3)
            inside = box[0] >= 0 and box[1] >= 0 and box[2] <= width and box[3] <= height
            if inside and not any(not (box[2] < b[0] or box[0] > b[2] or box[3] < b[1] or box[1] > b[3]) for b in boxes):
                break
        boxes.append(box)
        draw.text((x - bb[0], y - bb[1]), text, font=f, fill=fill, stroke_width=3, stroke_fill=(10, 10, 12))

    def arrow(points, rgb, w):
        if len(points) < 2:
            return
        draw.line(points, fill=rgb, width=w, joint="curve")
        (x0, y0), (x1, y1) = points[-2], points[-1]
        a = math.atan2(y1 - y0, x1 - x0)
        s = w * 4
        draw.polygon([(x1, y1), (x1 - s * math.cos(a - .45), y1 - s * math.sin(a - .45)),
                      (x1 - s * math.cos(a + .45), y1 - s * math.sin(a + .45))], fill=rgb)

    # Movement over the whole film, from each actor's keys.
    for actor in scene.get("actors", []):
        rgb = tuple(int(c * 255) for c in ps.hex_rgb(actor.get("color")))
        times = sorted({t} | {kk.get("t", 0) for kk in actor["keys"]})
        pts = []
        for tt in times:
            p = ps.states(scene, tt)[actor["id"]]["pos"]
            if not pts or math.dist(p[:2], pts[-1]) > 0.05:
                pts.append(p[:2])
        if len(pts) > 1 and sum(math.dist(a, b) for a, b in zip(pts, pts[1:])) > 0.3:
            arrow([to_px(*p) for p in pts], rgb, max(3, int(k * 0.05)))

    amber = (250, 214, 64)
    # Shots that share a camera position share one marker.
    names = {}
    for shot in scene["shots"]:
        p = tuple(round(v, 2) for v in shot["camera"]["start"]["pos"])
        names.setdefault(p, []).append(shot["id"])
    for shot in scene["shots"]:
        cam = shot["camera"]
        p0, l0 = cam["start"]["pos"], cam["start"]["look"]
        p1 = cam.get("end", cam["start"])["pos"]
        if math.dist(p0[:2], p1[:2]) > 0.2:
            draw.line([to_px(*p0[:2]), to_px(*p1[:2])], fill=amber, width=2)
        a = math.atan2(l0[1] - p0[1], l0[0] - p0[0])
        half = math.radians(shot["vfov"]) * 0.5 * ps.frame_size(scene)[0] / ps.frame_size(scene)[1]
        reach = 1.6
        cx, cy = to_px(*p0[:2])
        tips = [to_px(p0[0] + reach * math.cos(a + d), p0[1] + reach * math.sin(a + d)) for d in (-half, half)]
        draw.polygon([(cx, cy)] + tips, outline=amber, width=2)
        draw.ellipse((cx - 6, cy - 6, cx + 6, cy + 6), fill=amber)
        same = names[tuple(round(v, 2) for v in p0)]
        if shot["id"] == same[0]:
            place(" ".join(same), (cx, cy), amber, small, r=k * 0.3)

    for prop in scene.get("props", []):
        if prop.get("label"):
            meshes = ps.prop_meshes(prop, st[prop["id"]])
            if meshes:
                pts = [v for v, _, _ in meshes]
                lo = min(v[:, :2].min(axis=0)[0] for v in pts), min(v[:, :2].min(axis=0)[1] for v in pts)
                hi = max(v[:, :2].max(axis=0)[0] for v in pts), max(v[:, :2].max(axis=0)[1] for v in pts)
                at = ((lo[0] + hi[0]) / 2, (lo[1] + hi[1]) / 2)
            else:
                at = st[prop["id"]]["pos"][:2]
            place(prop["label"], to_px(*at), tuple(int(c * 255) for c in ps.hex_rgb(prop.get("color"))), small)
    for actor in scene.get("actors", []):
        label = actor.get("label", actor["id"])
        if label:
            p = st[actor["id"]]["pos"]
            place(label, to_px(*p[:2]), tuple(int(c * 255) for c in ps.hex_rgb(actor.get("color"))), big)

    head = f"{scene.get('name', 'previs')}  t = {t:g} s  grid 1 m" + ("  rough render" if rough else "")
    draw.text((16, 12), head, font=small, fill=(235, 235, 240), stroke_width=3, stroke_fill=(10, 10, 12))
    img.save(path)


# Sheets

def sheets(scene, jobs, out_dir, font):
    from PIL import Image, ImageDraw
    order = [s["id"] for s in scene["shots"]]
    by_shot = {}
    for j in jobs:
        by_shot.setdefault(j["shot"], []).append(j)
    shots = [s for s in order if s in by_shot]
    width, height = ps.frame_size(scene)

    # Storyboard for a model: playback order, one frame per shot, a panel number and nothing else.
    pw, ph = width // 2, height // 2
    cols, gap = min(5, len(shots)), 8
    rows = math.ceil(len(shots) / cols)
    sheet = Image.new("RGB", (cols * pw + (cols + 1) * gap, rows * ph + (rows + 1) * gap), (0, 0, 0))
    draw = ImageDraw.Draw(sheet)
    f = font(22)
    for n, sid in enumerate(shots):
        first = by_shot[sid][0]
        im = Image.open(first["path"]).convert("RGB").resize((pw, ph))
        x, y = gap + (n % cols) * (pw + gap), gap + (n // cols) * (ph + gap)
        sheet.paste(im, (x, y))
        label = str(order.index(sid) + 1)
        draw.rectangle((x, y, x + 34, y + 30), fill=(0, 0, 0))
        draw.text((x + 8, y + 2), label, font=f, fill=(255, 255, 255))
    sheet.save(os.path.join(out_dir, "storyboard.png"))

    # Review sheet for people: every rendered frame of each shot with its id.
    titles = {s["id"]: s.get("title", "") for s in scene["shots"]}
    fw, fh = int(width * 0.4), int(height * 0.4)
    cell_w = max(len(v) for v in by_shot.values()) * (fw + 4) + 12
    cell_h, cols = fh + 44, min(3, len(shots))
    rows = math.ceil(len(shots) / cols)
    review = Image.new("RGB", (cols * cell_w, rows * cell_h), (22, 24, 28))
    draw = ImageDraw.Draw(review)
    f = font(20)
    for n, sid in enumerate(shots):
        x, y = (n % cols) * cell_w + 6, (n // cols) * cell_h
        draw.text((x, y + 8), f"{sid}  {titles[sid]}", font=f, fill=(235, 235, 240))
        for m, j in enumerate(by_shot[sid]):
            im = Image.open(j["path"]).convert("RGB").resize((fw, fh))
            review.paste(im, (x + m * (fw + 4), y + 40))
            draw.text((x + m * (fw + 4) + 6, y + 44), j["frame"], font=font(16), fill=(255, 255, 255),
                      stroke_width=2, stroke_fill=(0, 0, 0))
    review.save(os.path.join(out_dir, "review.png"))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("scene", nargs="?")
    ap.add_argument("--out", help="output folder")
    ap.add_argument("--shots", default="all", help="comma-separated shot ids, or all")
    ap.add_argument("--backend", choices=["auto", "blender", "bpy", "raster"], default="auto")
    ap.add_argument("--blender", help="path to the Blender executable")
    ap.add_argument("--bpy-python", default="3.11", help="Python version uv uses for the bpy package")
    ap.add_argument("--bpy-version", default="", help="pip version spec for bpy, such as ==4.5.*")
    ap.add_argument("--plan-time", type=float, default=0.0, help="moment drawn in the plan, in seconds")
    ap.add_argument("--save-blend", action="store_true", help="also save a .blend of the last rendered moment")
    ap.add_argument("--font", help="font file for plan and sheet labels")
    ap.add_argument("--schema", action="store_true", help="print the scene file format and exit")
    args = ap.parse_args()
    if args.schema:
        print(ps.__doc__)
        return
    if not args.scene or not args.out:
        ap.error("SCENE and --out are required")

    scene = ps.load(args.scene)
    out_dir = os.path.abspath(args.out)
    os.makedirs(os.path.join(out_dir, "shots"), exist_ok=True)
    wanted = None if args.shots == "all" else set(args.shots.split(","))
    unknown = (wanted or set()) - {s["id"] for s in scene["shots"]}
    if unknown:
        raise SystemExit(f"unknown shot ids: {', '.join(sorted(unknown))}")
    jobs = frame_jobs(scene, wanted, out_dir)
    font = find_font(args.font)

    started = time.time()
    info = render_frames(args.scene, scene, jobs, args, out_dir)
    draw_plan(scene, args.plan_time, font, os.path.join(out_dir, "plan.png"), info["rough"])
    if jobs:
        sheets(scene, jobs, out_dir, font)

    manifest = dict(info, scene=os.path.abspath(args.scene), seconds=round(time.time() - started, 1),
                    plan="plan.png", storyboard="storyboard.png" if jobs else None,
                    review="review.png" if jobs else None, note=ROUGH_NOTE if info["rough"] else None,
                    frames=[{"shot": j["shot"], "frame": j["frame"], "t": round(j["t"], 3),
                             "file": os.path.relpath(j["path"], out_dir),
                             "camera": ps.camera_at(next(s for s in scene["shots"] if s["id"] == j["shot"]), j["t"]),
                             "actors": {k: {"pos": [round(x, 3) for x in v["pos"]], "yaw": round(v["yaw"], 1),
                                            "pose": v["pose"]}
                                        for k, v in ps.states(scene, j["t"]).items()
                                        if k in {a["id"] for a in scene.get("actors", [])}}}
                            for j in jobs])
    with open(os.path.join(out_dir, "previs.json"), "w", encoding="utf-8") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)
    print(f"{info['backend']}: {len(jobs)} frames, plan and sheets in {out_dir}")


if __name__ == "__main__":
    main()
