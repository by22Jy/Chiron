from fastapi import FastAPI, UploadFile, File, HTTPException, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from ultralytics import YOLO
from PIL import Image
import io, requests, base64
import numpy as np

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:5173", "http://localhost:5173", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
@app.get("/health")
def health():
    # 避免 IDE 对未安装环境报 "Import could not be resolved"，用动态探测而非直接导入
    import importlib.util
    deepface_ok = importlib.util.find_spec("deepface") is not None
    return {"status": "ok", "deepface": deepface_ok}

# 分别加载检测与姿态模型（可按需替换为 yolov8m*.pt 提升精度）
model_det = YOLO("yolov8m.pt")
model_pose = YOLO("yolov8m-pose.pt")


def run_detect(image: Image.Image):
    # 降低输入尺寸并稍调置信度，提升稳定性与速度
    results = model_det.predict(image, imgsz=320, conf=0.30, verbose=False)
    names = model_det.names
    objects = []
    for r in results:
        for c in r.boxes.cls:
            objects.append(names[int(c)])
    return {"objects": list(set(objects))}


def run_analyze(image: Image.Image):
    # 检测（框）
    det_res = model_det.predict(image, imgsz=480, conf=0.30, verbose=False)
    names = model_det.names
    det_boxes = []  # [{label, score, box:[x1,y1,x2,y2]}]
    for r in det_res:
        if r.boxes is None:
            continue
        for i in range(len(r.boxes)):
            cls_id = int(r.boxes.cls[i])
            score = float(r.boxes.conf[i]) if r.boxes.conf is not None else 0.0
            xyxy = r.boxes.xyxy[i].tolist()  # [x1,y1,x2,y2]
            det_boxes.append({
                "label": names.get(cls_id, str(cls_id)),
                "score": score,
                "box": [float(xyxy[0]), float(xyxy[1]), float(xyxy[2]), float(xyxy[3])]
            })

    # 姿态（关键点）
    pose_res = model_pose.predict(image, imgsz=480, conf=0.30, verbose=False)
    persons = []  # [{id, keypoints:[[x,y,conf]...]}]
    pid = 1
    for r in pose_res:
        if getattr(r, 'keypoints', None) is None or r.keypoints is None:
            continue
        kxy = r.keypoints.xy  # [num, k, 2]
        kconf = r.keypoints.conf  # [num, k] or None
        num = kxy.shape[0]
        for idx in range(num):
            pts_xy = kxy[idx].tolist()
            pts_conf = kconf[idx].tolist() if kconf is not None else [1.0]*len(pts_xy)
            kp = []
            for (x, y), cf in zip(pts_xy, pts_conf):
                kp.append([float(x), float(y), float(cf)])
            persons.append({"id": pid, "keypoints": kp})
            pid += 1

    # 简单空间关系推理：手腕与物体盒包含/近邻
    def wrist_points(kp):
        if not kp:
            return []
        return [kp[-1][:2], kp[-2][:2]] if len(kp) >= 2 else [kp[-1][:2]]

    def box_contains(box, pt):
        x1, y1, x2, y2 = box
        x, y = pt
        return x1 <= x <= x2 and y1 <= y <= y2

    def point_box_distance(box, pt):
        x1, y1, x2, y2 = box
        x, y = pt
        cx = min(max(x, x1), x2)
        cy = min(max(y, y1), y2)
        dx = x - cx
        dy = y - cy
        return (dx*dx + dy*dy) ** 0.5

    actions = []
    for p in persons:
        wrists = wrist_points(p.get("keypoints", []))
        for obj in det_boxes:
            if obj["label"].lower() in ("person",):
                continue
            near = False
            for w in wrists:
                if box_contains(obj["box"], w) or point_box_distance(obj["box"], w) < 50.0:
                    near = True
                    break
            if near:
                actions.append(f"person_{p['id']} holding {obj['label']}")

    return {"detections": det_boxes, "poses": persons, "actions": actions}


@app.post("/detect/file")
async def detect_file(file: UploadFile = File(...)):
    img_bytes = await file.read()
    image = Image.open(io.BytesIO(img_bytes)).convert("RGB")
    return run_detect(image)


@app.post("/detect/url")
async def detect_url(url: str):
    try:
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        image = Image.open(io.BytesIO(resp.content)).convert("RGB")
        return run_detect(image)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/analyze/file")
async def analyze_file(file: UploadFile = File(...)):
    img_bytes = await file.read()
    image = Image.open(io.BytesIO(img_bytes)).convert("RGB")
    return run_analyze(image)


@app.post("/analyze/url")
async def analyze_url(url: str):
    try:
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        image = Image.open(io.BytesIO(resp.content)).convert("RGB")
        return run_analyze(image)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/emotion/file")
async def emotion_file(file: UploadFile = File(...)):
    try:
        from deepface import DeepFace  # type: ignore
    except ImportError:
        raise HTTPException(status_code=503, detail="DeepFace 未安装，请先 pip install deepface")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"DeepFace 导入失败: {e}")
    img_bytes = await file.read()
    image = Image.open(io.BytesIO(img_bytes)).convert("RGB")
    # DeepFace 接受 ndarray 或路径（BGR）
    np_img = np.array(image)[:, :, ::-1]
    try:
        # 使用更快的 detector_backend，并关闭对齐，加快速度
        result = DeepFace.analyze(
            np_img,
            actions=['emotion'],
            enforce_detection=False,
            detector_backend='opencv',
            align=False
        )
        # DeepFace 可能返回 list 或 dict
        if isinstance(result, list) and len(result) > 0:
            result = result[0]
        emotion = result.get('dominant_emotion')
        scores = result.get('emotion') or {}
        def to_py(x):
            if isinstance(x, (np.floating,)):
                return float(x)
            if isinstance(x, (np.integer,)):
                return int(x)
            if isinstance(x, np.ndarray):
                return x.tolist()
            if isinstance(x, dict):
                return {k: to_py(v) for k, v in x.items()}
            if isinstance(x, (list, tuple)):
                return [to_py(v) for v in x]
            return x
        return {"emotion": str(emotion) if emotion is not None else "", "raw": to_py(scores)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/emotion/url")
async def emotion_url(url: str):
    try:
        from deepface import DeepFace  # type: ignore
    except ImportError:
        raise HTTPException(status_code=503, detail="DeepFace 未安装，请先 pip install deepface")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"DeepFace 导入失败: {e}")
    try:
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        image = Image.open(io.BytesIO(resp.content)).convert("RGB")
        np_img = np.array(image)[:, :, ::-1]
        result = DeepFace.analyze(
            np_img,
            actions=['emotion'],
            enforce_detection=False,
            detector_backend='opencv',
            align=False
        )
        if isinstance(result, list) and len(result) > 0:
            result = result[0]
        emotion = result.get('dominant_emotion')
        scores = result.get('emotion') or {}
        def to_py(x):
            if isinstance(x, (np.floating,)):
                return float(x)
            if isinstance(x, (np.integer,)):
                return int(x)
            if isinstance(x, np.ndarray):
                return x.tolist()
            if isinstance(x, dict):
                return {k: to_py(v) for k, v in x.items()}
            if isinstance(x, (list, tuple)):
                return [to_py(v) for v in x]
            return x
        return {"emotion": str(emotion) if emotion is not None else "", "raw": to_py(scores)}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.websocket("/ws/detect")
async def ws_detect(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            # 前端发送 base64 图像字符串；也支持 dataURL 形式
            data = await websocket.receive_text()
            if data.startswith("data:image") and "," in data:
                data = data.split(",", 1)[1]
            img_bytes = base64.b64decode(data)
            image = Image.open(io.BytesIO(img_bytes)).convert("RGB")
            result = run_detect(image)
            await websocket.send_json(result)
    except Exception as e:
        try:
            await websocket.send_json({"error": str(e)})
        except Exception:
            pass



@app.websocket("/ws/analyze")
async def ws_analyze(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            if data.startswith("data:image") and "," in data:
                data = data.split(",", 1)[1]
            img_bytes = base64.b64decode(data)
            image = Image.open(io.BytesIO(img_bytes)).convert("RGB")
            result = run_analyze(image)
            await websocket.send_json(result)
    except Exception as e:
        try:
            await websocket.send_json({"error": str(e)})
        except Exception:
            pass

