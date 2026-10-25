"""Find every face a picture shows and flag any the player or the page cuts.

    .venv/bin/python pipeline/facecrop.py <samples.json> <public dir>
        [--out <dir>] [--accept <file>]

<samples.json> is the episode's picture export: a list with one entry per
picture per sample (five a second), written by a small script beside the
episode that reads its shots and pages: {"kind", "i": its index, "frame",
"src": the file under <public dir>, "rect": [x, y, w, h] on the frame,
"t": seconds into a video (null for a still), then either "size": [w, h],
"k": screen pixels per source pixel and "mx", "my": the source point at
the rect's centre, or "layer": {"crop": [W, H, x, y, w, h] or null,
"fit": "cover" or "contain", "pos": "50% 50%", "zoom"}; and "caption":
the page on screen as {"x", "w", "y" (its centre), "h", "text"} or null}.

Each sample says where a picture's source pixels land on the 1080x1920
frame at one frame of the film (the shot's crop, push and rect, the page
camera, or for a layer its rect and its crop or fit, placed here once
the file's size is known). Pictures laid over one another are
each checked alone: a face covered by the picture on top is not seen as
covered. The faces are found on the uncut source, where they are
whole (OpenCV's YuNet, models/face_detection_yunet_2023mar.onnx from
opencv/opencv_zoo, MIT licence, SHA-256 8f2383e4…, with its
five points: the eyes, the nose, the mouth's corners), and mapped onto the
frame, so a face half out of frame is still found. A face at least 150 px
wide on the frame (a subject, not the crowd behind it) is flagged when:

  SIDE     an eye, the nose or a mouth corner lies under the player's side
           crop (52 px each side, measured on a posted Reel),
  EDGE     one of them lies outside the picture (the frame or a band's
           edge); an extreme close-up whose cheek or ear leaves the frame
           is framing, not a fault,
  TOP      an eye lies under the player's top bar (y < 245),
  CAPTION  the caption page on screen crosses the mouth or the chin (from
           the nose down) across a third of the face's width.

One film cut a face with the side crop in three renders (a profile, four
film shots, a night shot), each judged by eye on stills without the crop
drawn; that night shot at its first crop is this check's counterfactual
(it fails it, and passes the crop that fixed it). Flags are grouped
by shot (first and last time). A group shorter than 0.25 s, timed frame
by frame (a face drifting to an edge in a shot's last frames), is printed
as brief and does not fail. A flag the owner has chosen to keep is listed
in the episode's accept file, one line each, named by the picture's file
so an inserted shot cannot move it: "<src> <FLAG>: <the reason, with who
chose it>"; it is printed as accepted and does not fail. With --out,
the first sample of each group is drawn there (the picture as the frame
shows it, the covered bands darkened, the face boxed). Exits 1 when
anything else is flagged.
"""

import json
import subprocess
import sys
from pathlib import Path

import cv2
import numpy as np

MODEL = Path(__file__).parent / "models" / "face_detection_yunet_2023mar.onnx"
W, H = 1080, 1920
SIDE, TOPBAR = 52, 245
MIN_FACE = 150
DETECT_W = 1920  # sources are detected at most this wide


def video_size(path):
    out = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=width,height",
                          "-of", "csv=p=0", str(path)], capture_output=True, text=True, check=True).stdout
    return [int(v) for v in out.strip().split(",")[:2]]


def place_layer(s, size):
    """A layer (a picture in a rect): its rect, then a crop, or the
    file fitted to cover or contain the rect at its object position and
    zoom; sets the sample's scale and centre as a shot's."""
    x, y, w, h = s["rect"]
    lay = s["layer"]
    if lay["crop"]:
        _, _, cx, cy, cw, ch = lay["crop"]
        k, mx, my = max(w / cw, h / ch), cx + cw / 2, cy + ch / 2
    else:
        W, H = size
        k0 = (max if lay["fit"] == "cover" else min)(w / W, h / H)
        px, py = (float(v.rstrip("%")) / 100 for v in lay["pos"].split())
        ox, oy = (w - W * k0) * px, (h - H * k0) * py
        k, mx, my = k0, (w / 2 - ox) / k0, (h / 2 - oy) / k0
    z = lay["zoom"]
    s.update(size=size, k=k * z, mx=mx, my=my)


def source_frame(public, s):
    path = public / s["src"]
    if s["t"] is None:
        im = cv2.imread(str(path), cv2.IMREAD_COLOR)
        if im is None:
            raise SystemExit(f"cannot read {path}")
        return im
    w, h = s.get("size") or video_size(path)
    # The last sample of a stretch can fall a frame past the file's end.
    for back in (0, 0.04, 0.08, 0.12):
        raw = subprocess.run(["ffmpeg", "-loglevel", "error", "-ss", f"{max(0, s['t'] - back):.3f}", "-i", str(path), "-frames:v", "1",
                              "-f", "rawvideo", "-pix_fmt", "bgr24", "-"], capture_output=True, check=True).stdout
        if raw:
            return np.frombuffer(raw, np.uint8).reshape(h, w, 3)
    raise SystemExit(f"cannot read {path} at {s['t']:.3f}")


def faces(det, im):
    """Each face as (x, y, w, h, [(x, y) of the eyes, the nose and the mouth corners])."""
    h, w = im.shape[:2]
    f = min(1.0, DETECT_W / w)
    small = cv2.resize(im, (round(w * f), round(h * f))) if f < 1 else im
    det.setInputSize((small.shape[1], small.shape[0]))
    _, found = det.detect(small)
    if found is None:
        return []
    return [(r[0] / f, r[1] / f, r[2] / f, r[3] / f, [(r[4 + 2 * j] / f, r[5 + 2 * j] / f) for j in range(5)]) for r in found]


def to_frame(s, x, y):
    rx, ry, rw, rh = s["rect"]
    return rx + rw / 2 + (x - s["mx"]) * s["k"], ry + rh / 2 + (y - s["my"]) * s["k"]


def check(s, face):
    x0, y0 = to_frame(s, face[0], face[1])
    x1, y1 = to_frame(s, face[0] + face[2], face[1] + face[3])
    points = [to_frame(s, *p) for p in face[4]]
    if x1 - x0 < MIN_FACE:
        return []
    rx, ry, rw, rh = s["rect"]
    left, right = max(rx, 0), min(rx + rw, W)
    top, bottom = max(ry, 0), min(ry + rh, H)
    inside = [left <= x < right and top <= y < bottom for x, y in points]
    if not any(inside):
        return []  # the face is not on the frame at all
    out = []
    if not all(inside):
        out.append(("EDGE", "an eye, the nose or the mouth outside the picture"))
    if any(ok and not SIDE <= x < W - SIDE for (x, _), ok in zip(points, inside)):
        out.append(("SIDE", "an eye, the nose or the mouth under the player's side crop"))
    if any(ok and y < TOPBAR for (_, y), ok in zip(points[:2], inside)):
        out.append(("TOP", "an eye under the player's top bar"))
    c = s.get("caption")
    if c:
        cy0, cy1 = c["y"] - c["h"] / 2, c["y"] + c["h"] / 2
        over_y = min(y1, cy1) - max(points[2][1], cy0)
        over_x = min(x1, c["x"] + c["w"]) - max(x0, c["x"])
        if over_y > 0 and over_x > (x1 - x0) / 3:
            out.append(("CAPTION", f"the page \"{c['text']}\" across the mouth or the chin"))
    return [(kind, why, (round(x0), round(y0), round(x1), round(y1))) for kind, why in out]


def draw(s, im, box, path):
    rx, ry, rw, rh = s["rect"]
    m = np.float32([[s["k"], 0, rx + rw / 2 - s["mx"] * s["k"]], [0, s["k"], ry + rh / 2 - s["my"] * s["k"]]])
    frame = cv2.warpAffine(im, m, (W, H))
    mask = np.zeros((H, W), np.uint8)
    mask[max(ry, 0):min(ry + rh, H), max(rx, 0):min(rx + rw, W)] = 1
    frame[mask == 0] = 0
    shade = frame.copy()
    shade[:, :SIDE] //= 3
    shade[:, W - SIDE:] //= 3
    shade[:TOPBAR] //= 3
    cv2.rectangle(shade, box[:2], box[2:], (0, 0, 255), 4)
    cv2.imwrite(str(path), shade)


def between(a, b, f):
    """The sample of a picture at frame f, between its samples a and b: a
    shot's push and its video time are linear in the frame; a page's eased
    camera is close to it over six frames."""
    u = (f - a["frame"]) / (b["frame"] - a["frame"])
    mid = dict(a, frame=f, caption=a["caption"] if u < 0.5 else b["caption"])
    for key in ("k", "mx", "my") + (("t",) if a["t"] is not None else ()):
        mid[key] = a[key] + (b[key] - a[key]) * u
    return mid


def main():
    args = sys.argv[1:]
    opts = {k: args[args.index(k) + 1] for k in ("--out", "--accept") if k in args}
    samples = json.loads(Path(args[0]).read_text())
    public = Path(args[1])
    out = Path(opts["--out"]) if "--out" in opts else None
    if out:
        out.mkdir(parents=True, exist_ok=True)
    # Kept flags are named by the picture's file, which inserting a shot
    # does not move: "<src> <FLAG>: <reason, with who chose it>".
    accepted = {}
    if "--accept" in opts:
        for line in Path(opts["--accept"]).read_text().splitlines():
            if line.strip() and not line.startswith("#"):
                head, why = line.split(":", 1)
                src, kind = head.split()
                accepted[(src, kind)] = why.strip()
    det = cv2.FaceDetectorYN.create(str(MODEL), "", (320, 320), 0.7, 0.3, 5000)
    stills = {}  # a still's faces are found once; a video frame is read per sample

    def look(s):
        if s["t"] is None:
            if s["src"] not in stills:
                im = source_frame(public, s)
                stills[s["src"]] = (im, faces(det, im))
            return stills[s["src"]]
        im = source_frame(public, s)
        return im, faces(det, im)

    groups = {}  # (picture, flag) -> {first, last, count, whys, box, image}
    seen = 0  # subject-sized faces on the frame, so a clean run is known to have looked
    by_picture = {}
    for s in samples:
        im, found = look(s)
        if "layer" in s:
            place_layer(s, [im.shape[1], im.shape[0]])
        by_picture.setdefault((s["kind"], s["i"]), []).append(s)
        for face in found:
            x0, _ = to_frame(s, face[0], face[1])
            x1, _ = to_frame(s, face[0] + face[2], face[1])
            seen += x1 - x0 >= MIN_FACE
            for kind, why, box in check(s, face):
                g = groups.setdefault((s["kind"], s["i"], kind), {"first": s, "last": s, "count": 0, "whys": [], "box": box, "im": im})
                g["last"] = s
                g["count"] += 1
                if why not in g["whys"]:
                    g["whys"].append(why)
    failed = 0
    for (pk, i, kind), g in sorted(groups.items(), key=lambda kv: kv[1]["first"]["frame"]):
        first, last = g["first"], g["last"]
        span = (last["frame"] - first["frame"] + 1) / 30
        if span < 0.25:
            # Samples are six frames apart, so one flagged sample can stand
            # for up to 0.37 s: look at every frame from the sample before
            # to the sample after, and time the flag exactly.
            run = by_picture[(pk, i)]
            j0, j1 = run.index(first), run.index(last)
            a, b = run[max(0, j0 - 1)], run[min(len(run) - 1, j1 + 1)]
            hit = []
            for f in range(a["frame"], b["frame"] + 1):
                lo = max((x for x in run if x["frame"] <= f), key=lambda x: x["frame"])
                hi = min((x for x in run if x["frame"] >= f), key=lambda x: x["frame"])
                m = lo if lo is hi else between(lo, hi, f)
                _, found = look(m)
                if any(k == kind for face in found for k, _, _ in check(m, face)):
                    hit.append(f)
            span = (max(hit) - min(hit) + 1) / 30 if hit else span
        where = first["src"] if first["t"] is None else f"{first['src']} @ {first['t']:.2f}"
        if (first["src"], kind) in accepted:
            status = f"accepted: {accepted[(first['src'], kind)]}"
        elif span < 0.25:
            status = f"brief, {round(span * 30)} frames"
        else:
            status, failed = "FAIL", failed + 1
        print(f"{kind:8} {first['frame'] / 30:6.2f} to {last['frame'] / 30:6.2f} s ({g['count']} samples)  {pk} {i}  {where}: {'; '.join(g['whys'])}  [{status}]")
        if out:
            draw(first, g["im"], g["box"], out / f"{kind.lower()}-{first['frame']:05}.jpg")
    print(f"{len(samples)} samples, {seen} subject faces seen, {len(groups)} flagged, {failed} failing")
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
