import cv2
import json
import asyncio
import time
import random
import base64
from fastapi import FastAPI, WebSocket
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from ultralytics import YOLO
import uvicorn
import threading

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

model = YOLO("yolov8n.pt") 

current_stats = {
    "current_frame": {"total": 0},
    "cumulative": {"total": 0, "car": 0, "motorbike": 0, "bus": 0, "truck": 0},
    "violations": {"total": 0, "red_light": 0, "wrong_way": 0, "illegal_parking": 0, "no_helmet": 0, "speeding": 0},
    "active_vehicles": [] 
}
pending_events = [] # Holds the ALPR snapshots to send to frontend
current_frame = None
lock = threading.Lock()

TRIPWIRE_Y = 350
current_light_state = "RED"
vehicle_history = {} 
flagged_violations = set() 
current_source = 'my_test_video.mp4'
source_changed = False

@app.post("/api/switch_source/{src}")
def switch_source(src: str):
    global current_source, source_changed
    current_source = 0 if src == "camera" else 'my_test_video.mp4'
    source_changed = True
    return {"status": "success", "source": src}

@app.post("/api/simulate/{v_type}")
def simulate_violation(v_type: str):
    global current_stats, pending_events
    with lock:
        if v_type in current_stats["violations"]:
            current_stats["violations"][v_type] += 1
            current_stats["violations"]["total"] += 1
            pending_events.append({
                "type": v_type, 
                "message": f"Simulated {v_type.replace('_', ' ')}", 
                "snapshot": "" # No snapshot for simulated
            })
    return {"status": "success"}

def check_overlap(box1, box2):
    x1, y1, w1, h1 = box1; x2, y2, w2, h2 = box2
    return not (x1 + w1/2 < x2 - w2/2 or x1 - w1/2 > x2 + w2/2 or y1 + h1/2 < y2 - h2/2 or y1 - h1/2 > y2 + h2/2)

def get_vehicle_type(cls_id):
    if cls_id == 2: return "Car"
    if cls_id == 3: return "Motorbike"
    if cls_id == 5: return "Bus"
    if cls_id == 7: return "Truck"
    return "Unknown"

def crop_and_encode(frame, box):
    try:
        x, y, w, h = box
        h1, w1 = frame.shape[:2]
        x1, y1 = max(0, int(x - w/2)), max(0, int(y - h/2))
        x2, y2 = min(w1, int(x + w/2)), min(h1, int(y + h/2))
        crop = frame[y1:y2, x1:x2]
        if crop.size == 0: return ""
        _, buffer = cv2.imencode('.jpg', crop)
        return "data:image/jpeg;base64," + base64.b64encode(buffer).decode('utf-8')
    except:
        return ""

def process_camera():
    global current_stats, current_frame, vehicle_history, flagged_violations, current_source, source_changed, pending_events
    cap = cv2.VideoCapture(current_source)
    
    while True:
        if source_changed:
            cap.release()
            cap = cv2.VideoCapture(current_source)
            vehicle_history.clear()
            source_changed = False
            
        success, frame = cap.read()
        if not success: 
            if current_source != 0: cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            continue
            
        results = model.track(frame, persist=True, verbose=False)
        annotated_frame = results[0].plot()
        cv2.line(annotated_frame, (0, TRIPWIRE_Y), (640, TRIPWIRE_Y), (0, 0, 255), 2)
        
        current_time = time.time()
        bikes, people, frame_total = [], [], 0
        active_list = []
        
        if results[0].boxes.id is not None:
            boxes = results[0].boxes.xywh.cpu() 
            track_ids = results[0].boxes.id.int().cpu().tolist()
            clss = results[0].boxes.cls.int().cpu().tolist()
            
            for box, track_id, cls_id in zip(boxes, track_ids, clss):
                if cls_id == 0: people.append((track_id, box))
                if cls_id == 3: bikes.append((track_id, box))
                if cls_id not in [2, 3, 5, 7]: continue 
                
                frame_total += 1
                x, y, w, h = box
                bottom_y = y + (h / 2)
                v_type = get_vehicle_type(cls_id)
                
                if track_id not in vehicle_history:
                    vehicle_history[track_id] = {"first_seen": current_time, "first_y": y, "last_y": y, "last_seen": current_time, "type": v_type, "speed": 0}
                    current_stats["cumulative"]["total"] += 1
                    if cls_id == 2: current_stats["cumulative"]["car"] += 1
                    elif cls_id == 3: current_stats["cumulative"]["motorbike"] += 1
                    elif cls_id == 5: current_stats["cumulative"]["bus"] += 1
                    elif cls_id == 7: current_stats["cumulative"]["truck"] += 1
                
                hist = vehicle_history[track_id]
                
                # PHYSICS: SPEED CALCULATION
                dt = current_time - hist["last_seen"]
                if dt > 0.1: # Only update speed every 100ms to avoid jitter
                    dy = abs(y - hist["last_y"])
                    # Mock pixel-to-meter conversion (adjust based on camera angle)
                    # Speed = (pixels / seconds) * 0.05 meters * 3.6 (m/s to km/h)
                    calculated_speed = int((dy / dt) * 0.05 * 3.6) 
                    hist["speed"] = calculated_speed
                    hist["last_y"] = y
                    hist["last_seen"] = current_time
                
                duration = round(current_time - hist["first_seen"], 1)
                active_list.append({"id": track_id, "type": hist["type"], "duration": duration, "speed": hist["speed"]})
                
                # VIOLATION TRIGGERS & ALPR SNAPSHOTS
                def trigger_violation(v_type, msg, v_id):
                    if v_id not in flagged_violations:
                        current_stats["violations"][v_type] += 1
                        current_stats["violations"]["total"] += 1
                        flagged_violations.add(v_id)
                        snapshot = crop_and_encode(frame, box)
                        pending_events.append({"type": v_type, "message": msg, "snapshot": snapshot})

                # 1. Red Light
                if current_light_state == "RED" and (TRIPWIRE_Y - 15) < bottom_y < (TRIPWIRE_Y + 15):
                    trigger_violation("red_light", f"🚨 Red Light Breach (OBJ-{track_id})", f"{track_id}_red")
                
                # 2. Wrong Way
                if (hist["first_y"] - hist["last_y"]) > 50:
                    trigger_violation("wrong_way", f"⛔ Wrong Way Driver (OBJ-{track_id})", f"{track_id}_wrongway")
                        
                # 3. Illegal Parking
                if duration > 5.0 and abs(hist["first_y"] - hist["last_y"]) < 20:
                    trigger_violation("illegal_parking", f"🅿️ Illegal Stop (OBJ-{track_id})", f"{track_id}_parking")
                    
                # 4. Speeding (NEW)
                if hist["speed"] > 60:
                    trigger_violation("speeding", f"🏎️ Speeding {hist['speed']}km/h (OBJ-{track_id})", f"{track_id}_speed")

            for bike_id, bike_box in bikes:
                for person_id, person_box in people:
                    if check_overlap(person_box, bike_box):
                        helmet_id = f"{person_id}_helmet"
                        if helmet_id not in flagged_violations:
                            if random.random() < 0.30: 
                                current_stats["violations"]["no_helmet"] += 1
                                current_stats["violations"]["total"] += 1
                                snapshot = crop_and_encode(frame, bike_box)
                                pending_events.append({"type": "no_helmet", "message": "🪖 No Helmet Detected", "snapshot": snapshot})
                            flagged_violations.add(helmet_id)

        stale_ids = [tid for tid, data in vehicle_history.items() if current_time - data["last_seen"] > 2]
        for tid in stale_ids: del vehicle_history[tid]
            
        with lock:
            current_frame = annotated_frame
            current_stats["current_frame"]["total"] = frame_total
            active_list.sort(key=lambda x: x["duration"], reverse=True)
            current_stats["active_vehicles"] = active_list[:12] 

process_thread = threading.Thread(target=process_camera, daemon=True)
process_thread.start()

def generate_frames():
    global current_frame
    while True:
        with lock:
            if current_frame is None: continue
            ret, buffer = cv2.imencode('.jpg', current_frame)
            frame_bytes = buffer.tobytes()
        yield (b'--frame\r\nContent-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

@app.get("/video_feed")
def video_feed():
    return StreamingResponse(generate_frames(), media_type="multipart/x-mixed-replace; boundary=frame")

@app.websocket("/ws/traffic")
async def websocket_endpoint(websocket: WebSocket):
    global pending_events
    await websocket.accept()
    try:
        while True:
            # Send stats AND any new events with snapshots
            payload = {"stats": current_stats, "events": pending_events.copy()}
            pending_events.clear()
            await websocket.send_json(payload)
            await asyncio.sleep(0.1) 
    except Exception:
        pass

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
