import cv2
import numpy as np
from ultralytics import YOLO

def main():
    model = YOLO("yolov8n.onnx")
    cap = cv2.VideoCapture(0)
    roi_polygon = np.array([[100, 400], [500, 400], [600, 600], [50, 600]], np.int32)
    MAX_CAPACITY = 8  
    
    while cap.isOpened():
        success, frame = cap.read()
        if not success:
            break
            
        results = model.track(frame, classes=[2, 3, 5, 7], persist=True, verbose=False)
        vehicles_in_roi = 0
        
        if results[0].boxes.id is not None:
            boxes = results[0].boxes.xyxy.cpu().numpy()
            for box in boxes:
                x1, y1, x2, y2 = map(int, box)
                cx = (x1 + x2) // 2
                cy = (y1 + y2) // 2
                
                is_inside = cv2.pointPolygonTest(roi_polygon, (cx, cy), False)
                if is_inside >= 0:
                    vehicles_in_roi += 1
                    cv2.circle(frame, (cx, cy), 5, (0, 255, 0), -1) 
                else:
                    cv2.circle(frame, (cx, cy), 5, (0, 0, 255), -1) 
                    
        density_score = min(vehicles_in_roi / MAX_CAPACITY, 1.0)
        
        cv2.polylines(frame, [roi_polygon], True, (255, 0, 0), 2)
        cv2.putText(frame, f"Live Density: {density_score:.2f}", (30, 50), 
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA)
                    
        cv2.imshow("Edge-AI Traffic Node", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
