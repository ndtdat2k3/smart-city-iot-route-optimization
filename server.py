# ================================================================
#  Flask server – nhan anh tu WROOM, chay YOLOv8, tra ket qua JSON
#  Cai dat: pip install flask ultralytics pillow
#  Chay:    python server.py
#  Sau do:  ngrok http 5000  ->  lay URL dan vao WROOM
# ================================================================

from flask import Flask, request, jsonify, send_file, Response
from ultralytics import YOLO
from PIL import Image, ImageDraw, ImageFont
import io, time, os, threading

app = Flask(__name__)

# ---- Load model khi khoi dong ----
MODEL_PATH = "best.pt"
print(f"[SERVER] Dang load model: {MODEL_PATH}")
model = YOLO(MODEL_PATH)
print("[SERVER] Model san sang!")

# ---- Cac class can dem ----
VEHICLE_CLASSES = {"car", "motorbike", "truck", "bus", "bicycle"}
LANE_CLASSES    = {"lane"}

# ---- Luu anh preview (thread-safe) ----
_preview_lock     = threading.Lock()
_last_annotated   = None   # bytes JPEG da ve bbox
_last_raw         = None   # bytes JPEG goc tu CAM
_last_meta        = {}     # vehicle_count, lane_count, inference_ms, timestamp

# Mau bbox
COLOR_VEHICLE = (255, 80,  80)   # do
COLOR_LANE    = (80,  200, 80)   # xanh la
COLOR_OTHER   = (200, 200, 80)   # vang

def _draw_boxes(img: Image.Image, results) -> Image.Image:
    """Ve bounding box len anh PIL, tra ve anh moi."""
    draw = ImageDraw.Draw(img)
    try:
        # Thu dung font he thong, fallback ve default neu khong co
        font = ImageFont.truetype("arial.ttf", max(12, img.width // 40))
    except Exception:
        font = ImageFont.load_default()

    for box in results.boxes:
        cls_id   = int(box.cls[0])
        cls_name = model.names[cls_id].lower()
        conf     = float(box.conf[0])
        x1, y1, x2, y2 = [int(v) for v in box.xyxy[0]]

        if cls_name in VEHICLE_CLASSES:
            color = COLOR_VEHICLE
        elif cls_name in LANE_CLASSES:
            color = COLOR_LANE
        else:
            color = COLOR_OTHER

        # Ve khung + label
        draw.rectangle([x1, y1, x2, y2], outline=color, width=2)
        label = f"{cls_name} {conf:.2f}"
        # Nen label de de doc
        bbox_txt = draw.textbbox((x1, y1 - 14), label, font=font)
        draw.rectangle(bbox_txt, fill=color)
        draw.text((x1, y1 - 14), label, fill=(0, 0, 0), font=font)

    return img

# ----------------------------------------------------------------
@app.route("/predict", methods=["POST"])
def predict():
    global _last_annotated, _last_raw, _last_meta

    print(f"[DEBUG] Content-Type: {request.content_type}")
    print(f"[DEBUG] Content-Length: {request.content_length}")

    raw = request.get_data()
    print(f"[DEBUG] Nhan duoc {len(raw)} bytes")

    if len(raw) < 4:
        return jsonify({"error": "No data"}), 400

    if raw[0] != 0xFF or raw[1] != 0xD8:
        print(f"[DEBUG] Khong phai JPEG! Header: {raw[:4].hex()}")
        return jsonify({"error": "Not a JPEG"}), 400

    try:
        img = Image.open(io.BytesIO(raw)).convert("RGB")
    except Exception as e:
        return jsonify({"error": str(e)}), 400

    start   = time.time()
    results = model(img, verbose=False)[0]

    vehicle_count = 0
    lane_count    = 0
    for box in results.boxes:
        cls_id   = int(box.cls[0])
        cls_name = model.names[cls_id].lower()
        if cls_name in VEHICLE_CLASSES:
            vehicle_count += 1
        elif cls_name in LANE_CLASSES:
            lane_count += 1

    elapsed = round(time.time() - start, 3)

    # ---- Luu preview (ve bbox tren ban sao) ----
    try:
        annotated_img = _draw_boxes(img.copy(), results)
        buf = io.BytesIO()
        annotated_img.save(buf, format="JPEG", quality=85)
        annotated_bytes = buf.getvalue()

        with _preview_lock:
            _last_annotated = annotated_bytes
            _last_raw       = raw
            _last_meta      = {
                "vehicle_count": vehicle_count,
                "lane_count":    lane_count,
                "inference_ms":  int(elapsed * 1000),
                "timestamp":     time.strftime("%Y-%m-%d %H:%M:%S"),
                "img_size_kb":   round(len(raw) / 1024, 1),
                "img_wh":        f"{img.width}x{img.height}",
            }
    except Exception as e:
        print(f"[PREVIEW] Loi ve bbox: {e}")

    response = {
        "vehicle_count": vehicle_count,
        "lane_count":    lane_count,
        "inference_ms":  int(elapsed * 1000)
    }
    print(f"[SERVER] Ket qua: {response}")
    return jsonify(response), 200

# ----------------------------------------------------------------
@app.route("/preview")
def preview():
    """Trang HTML tu dong lam moi moi 3 giay, hien thi anh + bbox."""
    with _preview_lock:
        meta = dict(_last_meta)
        has_img = _last_annotated is not None

    if not has_img:
        html = """
        <html><head><meta charset='utf-8'>
        <meta http-equiv='refresh' content='2'>
        <style>body{font-family:sans-serif;background:#111;color:#eee;
               display:flex;align-items:center;justify-content:center;height:100vh;margin:0}
               .box{text-align:center;padding:2rem;border:1px solid #444;border-radius:8px}</style>
        </head><body><div class='box'>
        <h2>&#9201; Chua co anh</h2>
        <p>Dang cho ESP32-CAM gui anh len...</p>
        <p style='color:#888;font-size:.85em'>Trang tu dong lam moi moi 2 giay</p>
        </div></body></html>"""
        return Response(html, mimetype="text/html")

    v  = meta.get("vehicle_count", 0)
    l  = meta.get("lane_count",    0)
    ms = meta.get("inference_ms",  0)
    ts = meta.get("timestamp",     "")
    sz = meta.get("img_size_kb",   0)
    wh = meta.get("img_wh",        "")

    html = f"""
    <html><head><meta charset='utf-8'>
    <meta http-equiv='refresh' content='3'>
    <title>ESP32-CAM Preview</title>
    <style>
      body{{margin:0;background:#111;color:#eee;font-family:sans-serif;
           display:flex;flex-direction:column;align-items:center;padding:1rem}}
      h2{{margin:.5rem 0;font-size:1.1rem;color:#adf}}
      img{{max-width:min(640px,95vw);border:2px solid #444;border-radius:6px;margin:.5rem 0}}
      .stats{{display:flex;gap:1.5rem;flex-wrap:wrap;justify-content:center;
              margin:.4rem 0;font-size:.9rem}}
      .chip{{background:#1e1e2e;border:1px solid #444;border-radius:20px;
             padding:.3rem .9rem}}
      .red{{border-color:#f55;color:#f88}}
      .grn{{border-color:#5d5;color:#8f8}}
      .blu{{border-color:#55f;color:#88f}}
      .yel{{border-color:#dd5;color:#ee8}}
      small{{color:#555;font-size:.75rem;margin-top:.3rem}}
    </style>
    </head>
    <body>
      <h2>&#128247; ESP32-CAM &rarr; YOLOv8 Preview</h2>
      <img src="/preview/image?t={int(time.time())}" alt="annotated">
      <div class='stats'>
        <span class='chip red'>&#128663; Xe: <b>{v}</b></span>
        <span class='chip grn'>&#9135; Lane: <b>{l}</b></span>
        <span class='chip blu'>&#9201; {ms} ms</span>
        <span class='chip yel'>&#128190; {sz} KB &nbsp;|&nbsp; {wh}</span>
      </div>
      <small>Anh cuoi: {ts} &nbsp;|&nbsp; Tu dong lam moi moi 3 giay</small>
    </body></html>"""
    return Response(html, mimetype="text/html")

@app.route("/preview/image")
def preview_image():
    """Tra ve JPEG anh da ve bbox, dung cho <img src=...>."""
    with _preview_lock:
        data = _last_annotated

    if data is None:
        return Response("No image", status=404)

    return Response(data, mimetype="image/jpeg",
                    headers={"Cache-Control": "no-store"})

@app.route("/preview/raw")
def preview_raw():
    """Tra ve JPEG goc tu CAM (khong co bbox)."""
    with _preview_lock:
        data = _last_raw

    if data is None:
        return Response("No image", status=404)

    return Response(data, mimetype="image/jpeg",
                    headers={"Cache-Control": "no-store"})

# ----------------------------------------------------------------
@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"}), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
