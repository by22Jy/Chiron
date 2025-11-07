from fastapi import FastAPI, UploadFile, File, HTTPException, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from ultralytics import YOLO
from PIL import Image
import io, requests, base64
import numpy as np
from collections import deque

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:5173", "http://localhost:5173", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Gesture Recognizer ---
# 简单手势识别器，用于检测挥手
class SimpleGestureRecognizer:
    def __init__(self):
        # 用 deque 存储最近 N 帧的手腕 x 坐标
        self.wrist_history = deque(maxlen=10)  # 跟踪最近10帧
        self.last_action = ""
        self.cooldown = 0  # 冷却时间，防止重复触发

    def recognize(self, keypoints):
        if self.cooldown > 0:
            self.cooldown -= 1
            return None

        # YOLOv8-pose 的关键点索引: 9 (左腕), 10 (右腕)
        # 我们只用右腕来简化
        right_wrist_kp = None
        if keypoints and len(keypoints) > 10:
            right_wrist_kp = keypoints[10] # [x, y, conf]

        if right_wrist_kp and right_wrist_kp[2] > 0.4:  # 置信度足够
            current_x = right_wrist_kp[0]
            self.wrist_history.append(current_x)

            if len(self.wrist_history) < 5: # 需要足够历史数据
                return None

            # 计算位移
            start_x = self.wrist_history[0]
            end_x = self.wrist_history[-1]
            displacement = end_x - start_x
            
            # 定义阈值 (可根据摄像头分辨率和距离调整)
            SWIPE_THRESHOLD = 80 

            if displacement > SWIPE_THRESHOLD:
                self.wrist_history.clear()
                self.cooldown = 15 # 冷却15帧
                return "swipe_right"
            elif displacement < -SWIPE_THRESHOLD:
                self.wrist_history.clear()
                self.cooldown = 15 # 冷却15帧
                return "swipe_left"
        return None

# 为每个 WebSocket 连接维护一个手势识别器实例
gesture_recognizers = {}


@app.get("/health")
def health():
    import importlib.util
    deepface_ok = importlib.util.find_spec("deepface") is not None
    return {"status": "ok", "deepface": deepface_ok}

model_det = YOLO("yolov8m.pt")
model_pose = YOLO("yolov8m-pose.pt")

def run_detect(image: Image.Image):
    results = model_det.predict(image, imgsz=320, conf=0.30, verbose=False)
    names = model_det.names
    objects = []
    for r in results:
        for c in r.boxes.cls:
            objects.append(names[int(c)])
    return {"objects": list(set(objects))}


def run_analyze(image: Image.Image, recognizer: SimpleGestureRecognizer = None):
    # 检测
    det_res = model_det.predict(image, imgsz=480, conf=0.30, verbose=False)
    names = model_det.names
    det_boxes = []
    for r in det_res:
        if r.boxes is None: continue
        for i in range(len(r.boxes)):
            cls_id = int(r.boxes.cls[i])
            score = float(r.boxes.conf[i]) if r.boxes.conf is not None else 0.0
            xyxy = r.boxes.xyxy[i].tolist()
            det_boxes.append({"label": names.get(cls_id, str(cls_id)), "score": score, "box": [float(v) for v in xyxy]})

    # 姿态
    pose_res = model_pose.predict(image, imgsz=480, conf=0.30, verbose=False)
    persons = []
    pid = 1
    all_keypoints = []
    for r in pose_res:
        if getattr(r, 'keypoints', None) is None or r.keypoints is None: continue
        kxy = r.keypoints.xy
        kconf = r.keypoints.conf
        num = kxy.shape[0]
        for idx in range(num):
            pts_xy = kxy[idx].tolist()
            pts_conf = kconf[idx].tolist() if kconf is not None else [1.0]*len(pts_xy)
            kp = [[float(x), float(y), float(cf)] for (x, y), cf in zip(pts_xy, pts_conf)]
            persons.append({"id": pid, "keypoints": kp})
            all_keypoints.append(kp) # 收集所有人的关键点
            pid += 1

    # --- 手势识别 & 关系推断 ---
    actions = []
    # 1. 挥手手势
    if recognizer and persons:
        # 简单起见，我们只基于画面中的第一个人做手势识别
        gesture = recognizer.recognize(all_keypoints[0])
        if gesture:
            actions.append(gesture)

    # 2. 空间关系: 手腕与物体
    def wrist_points(kp):
        if not kp: return []
        # 9: left_wrist, 10: right_wrist
        return [kp[9][:2], kp[10][:2]] if len(kp) > 10 else []

    def box_contains(box, pt):
        x1, y1, x2, y2 = box; x, y = pt
        return x1 <= x <= x2 and y1 <= y <= y2

    def point_box_distance(box, pt):
        x1, y1, x2, y2 = box; x, y = pt
        cx = min(max(x, x1), x2); cy = min(max(y, y1), y2)
        return ((x - cx)**2 + (y - cy)**2)**0.5

    for p in persons:
        wrists = wrist_points(p.get("keypoints", []))
        for obj in det_boxes:
            if obj["label"].lower() in ("person",): continue
            for w in wrists:
                if box_contains(obj["box"], w) or point_box_distance(obj["box"], w) < 50.0:
                    actions.append(f"person_{p['id']} holding {obj['label']}")
                    break 

    return {"detections": det_boxes, "poses": persons, "actions": list(set(actions))}


@app.post("/detect/file")
async def detect_file(file: UploadFile = File(...)):
    img_bytes = await file.read()
    image = Image.open(io.BytesIO(img_bytes)).convert("RGB")
    return run_detect(image)

@app.post("/analyze/file")
async def analyze_file(file: UploadFile = File(...)):
    img_bytes = await file.read()
    image = Image.open(io.BytesIO(img_bytes)).convert("RGB")
    # HTTP 调用是无状态的，所以每次都创建新的识别器
    return run_analyze(image, SimpleGestureRecognizer())

# ... (emotion and url endpoints remain the same)
@app.post("/detect/url")
async def detect_url(url: str):
    try:
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        image = Image.open(io.BytesIO(resp.content)).convert("RGB")
        return run_detect(image)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/analyze/url")
async def analyze_url(url: str):
    try:
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        image = Image.open(io.BytesIO(resp.content)).convert("RGB")
        return run_analyze(image, SimpleGestureRecognizer())
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/emotion/file")
async def emotion_file(file: UploadFile = File(...)):
    try:
        from deepface import DeepFace
    except ImportError:
        raise HTTPException(status_code=503, detail="DeepFace 未安装，请先 pip install deepface")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"DeepFace 导入失败: {e}")
    img_bytes = await file.read()
    np_img = np.array(Image.open(io.BytesIO(img_bytes)).convert("RGB"))[:, :, ::-1]
    try:
        result = DeepFace.analyze(np_img, actions=['emotion'], enforce_detection=False, detector_backend='opencv', align=False)
        if isinstance(result, list) and len(result) > 0: result = result[0]
        emotion = result.get('dominant_emotion')
        scores = result.get('emotion') or {}
        def to_py(x):
            if isinstance(x, np.generic): return x.item()
            if isinstance(x, np.ndarray): return x.tolist()
            if isinstance(x, dict): return {k: to_py(v) for k, v in x.items()}
            if isinstance(x, list): return [to_py(v) for v in x]
            return x
        return {"emotion": str(emotion) if emotion is not None else "", "raw": to_py(scores)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/emotion/url")
async def emotion_url(url: str):
    try:
        from deepface import DeepFace
    except ImportError:
        raise HTTPException(status_code=503, detail="DeepFace 未安装，请先 pip install deepface")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"DeepFace 导入失败: {e}")
    try:
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        np_img = np.array(Image.open(io.BytesIO(resp.content)).convert("RGB"))[:, :, ::-1]
        result = DeepFace.analyze(np_img, actions=['emotion'], enforce_detection=False, detector_backend='opencv', align=False)
        if isinstance(result, list) and len(result) > 0: result = result[0]
        emotion = result.get('dominant_emotion')
        scores = result.get('emotion') or {}
        def to_py(x):
            if isinstance(x, np.generic): return x.item()
            if isinstance(x, np.ndarray): return x.tolist()
            if isinstance(x, dict): return {k: to_py(v) for k, v in x.items()}
            if isinstance(x, list): return [to_py(v) for v in x]
            return x
        return {"emotion": str(emotion) if emotion is not None else "", "raw": to_py(scores)}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.websocket("/ws/detect")
async def ws_detect(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            if data.startswith("data:image") and "," in data: data = data.split(",", 1)[1]
            img_bytes = base64.b64decode(data)
            image = Image.open(io.BytesIO(img_bytes)).convert("RGB")
            result = run_detect(image)
            await websocket.send_json(result)
    except Exception as e:
        try: await websocket.send_json({"error": str(e)})
        except: pass

@app.websocket("/ws/analyze")
async def ws_analyze(websocket: WebSocket):
    client_id = f"{websocket.client.host}:{websocket.client.port}"
    gesture_recognizers[client_id] = SimpleGestureRecognizer()
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            if data.startswith("data:image") and "," in data: data = data.split(",", 1)[1]
            img_bytes = base64.b64decode(data)
            image = Image.open(io.BytesIO(img_bytes)).convert("RGB")
            
            recognizer = gesture_recognizers.get(client_id)
            result = run_analyze(image, recognizer)
            await websocket.send_json(result)
    except Exception as e:
        try: await websocket.send_json({"error": str(e)})
        except: pass
    finally:
        if client_id in gesture_recognizers:
            del gesture_recognizers[client_id]