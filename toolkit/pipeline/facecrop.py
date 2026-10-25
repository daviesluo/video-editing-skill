"""Find every face a picture shows and flag any the player or the page cuts.

    .venv/bin/python pipeline/facecrop.py <samples.json> <public dir>
        [--out <dir>] [--accept <file>]

<samples.json> is the episode's picture export: a list with one entry per
picture per sample (five a second), written by a small script beside the
episode that reads its shots and pages: {"kind": "shot" or "page", "i":
its index, "frame", "src": the file under <public dir>, "size": [w, h],
"rect": [x, y, w, h] on the frame, "t": seconds into a video (null for a
still), "k": screen pixels per source pixel, "mx", "my": the source point
at the rect's centre, "caption": the page on screen as {"x", "w", "y" (its
centre), "h", "text"} or null}.

Each sample says where a picture's source pixels land on the 1080x1920
frame at one frame of the film (the shot's crop, push and rect, or the
page camera). The faces are found on the uncut source, where they are
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
by shot (first and last time). A group shorter than 0.25 s (a face
drifting to an edge in a shot's last frames) is printed as brief and does
not fail. A flag the owner has chosen to keep is listed in the episode's
accept file, one line each: "<shot|page> <index> <FLAG>: <the reason, with
who chose it>"; it is printed as accepted and does not fail. With --out,
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


def source_frame(public, s):
    path = public / s["src"]
    if s["t"] is None:
        im = cv2.imread(str(path), cv2.IMREAD_COLOR)
        if im is None:
            raise SystemExit(f"cannot read {path}")
        return im
    w, h = s["size"]
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


def main():
    args = sys.argv[1:]
    opts = {k: args[args.index(k) + 1] for k in ("--out", "--accept") if k in args}
    samples = json.loads(Path(args[0]).read_text())
    public = Path(args[1])
    out = Path(opts["--out"]) if "--out" in opts else None
    if out:
        out.mkdir(parents=True, exist_ok=True)
    accepted = {}
    if "--accept" in opts:
        for line in Path(opts["--accept"]).read_text().splitlines():
            if line.strip() and not line.startswith("#"):
                head, why = line.split(":", 1)
                pk, i, kind = head.split()
                accepted[(pk, int(i), kind)] = why.strip()
    det = cv2.FaceDetectorYN.create(str(MODEL), "", (320, 320), 0.7, 0.3, 5000)
    stills = {}  # a still's faces are found once; a video frame is read per sample
    groups = {}  # (picture, flag) -> [first sample, last sample, count, why, box, image]
    seen = 0  # subject-sized faces on the frame, so a clean run is known to have looked
    for s in samples:
        if s["t"] is None:
            if s["src"] not in stills:
                im = source_frame(public, s)
                stills[s["src"]] = (im, faces(det, im))
            im, found = stills[s["src"]]
        else:
            im = source_frame(public, s)
            found = faces(det, im)
        for face in found:
            x0, _ = to_frame(s, face[0], face[1])
            x1, _ = to_frame(s, face[0] + face[2], face[1])
            seen += x1 - x0 >= MIN_FACE
            for kind, why, box in check(s, face):
                g = groups.setdefault((s["kind"], s["i"], kind), [s, s, 0, why, box, im])
                g[1] = s
                g[2] += 1
    failed = 0
    for (pk, i, kind), (first, last, count, why, box, im) in sorted(groups.items(), key=lambda kv: kv[1][0]["frame"]):
        where = first["src"] if first["t"] is None else f"{first['src']} @ {first['t']:.2f}"
        if (pk, i, kind) in accepted:
            status = f"accepted: {accepted[(pk, i, kind)]}"
        elif (last["frame"] - first["frame"]) / 30 < 0.25:
            status = "brief"
        else:
            status, failed = "FAIL", failed + 1
        print(f"{kind:8} {first['frame'] / 30:6.2f} to {last['frame'] / 30:6.2f} s ({count} samples)  {pk} {i}  {where}: {why}  [{status}]")
        if out:
            draw(first, im, box, out / f"{kind.lower()}-{first['frame']:05}.jpg")
    print(f"{len(samples)} samples, {seen} subject faces seen, {len(groups)} flagged, {failed} failing")
    sys.exit(1 if failed else 0)

if __name__ == "__main__":
    main()
