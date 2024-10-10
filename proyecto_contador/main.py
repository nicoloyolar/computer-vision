import cv2
import numpy as np
from video_stream import VideoStream
from yolo_detection import YOLODetector
from sort import Sort
import time

MODEL_PATH = "C:\\Users\\56975\\OneDrive\\Escritorio\\vision_computer_project\\models\\modelofinalcombinado.pt" # poner link como corresponde 
VIDEO_PATH = "C:\\Users\\56975\\Videos\\videosdechoritos\\ok.mp4" # poner link como corresponde 
SCALE_FACTOR = 0.6
frame_skip = 1

COUNTER_LINE_Y = 1000
product_count_1kg = 0
product_count_500grs = 0
stagnation_count = 0
sort_tracker = Sort(max_age=3, min_hits=2, iou_threshold=0.3)
counted_ids = set()
object_classes = {}
object_scores = {}

def draw_label(frame, text, x, y, color=(0, 255, 255), bg_color=(0, 0, 0, 0.5)):
    font_scale, font_thickness = 1.2, 3
    (text_width, text_height), _ = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, font_scale, font_thickness)
    overlay = frame.copy()
    box_coords = ((x, y), (x + text_width + 10, y - text_height - 10))
    cv2.rectangle(overlay, box_coords[0], box_coords[1], bg_color[:3], -1)
    cv2.addWeighted(overlay, bg_color[3], frame, 1 - bg_color[3], 0, frame)
    cv2.putText(frame, text, (x, y - 5), cv2.FONT_HERSHEY_SIMPLEX, font_scale, color, font_thickness)

def highlight_critical(frame, text, x, y):
    draw_label(frame, text, x, y, color=(0, 0, 255), bg_color=(0, 0, 0, 0.7))

def start_video_from_minute(stream, minute):
    fps = stream.cap.get(cv2.CAP_PROP_FPS)
    start_frame = int(minute * 60 * fps)
    stream.cap.set(cv2.CAP_PROP_POS_FRAMES, start_frame)

def main():
    global product_count_1kg, product_count_500grs, stagnation_count
    stream = VideoStream(VIDEO_PATH)
    if not stream.cap.isOpened():
        return

    detector = YOLODetector(MODEL_PATH)
    detector.confidence_threshold = 0.67
    start_video_from_minute(stream, 30)

    fps = 20
    last_time = time.time()

    while stream.cap.isOpened():
        ret, frame = stream.read_frame()
        if not ret: break

        current_time = time.time()
        elapsed_time = current_time - last_time

        if elapsed_time < 1.0 / fps:
            continue

        last_time = current_time

        results = detector.detect_objects(frame)
        detections = [[*map(int, detection.xyxy[0]), float(detection.conf)] for detection in results[0].boxes if detection.conf >= detector.confidence_threshold]

        for detection in detections:
            x1, y1, x2, y2, score = detection
            label = detector.model.names[int(results[0].boxes[0].cls)]
            display_text = f'{label} ({score * 100:.1f}%)'
            if label == 'estancamiento':
                highlight_critical(frame, display_text, x1, y1)
                if label not in counted_ids:
                    stagnation_count += 1
                    counted_ids.add(label)
            else:
                draw_label(frame, display_text, x1, y1, color=(0, 255, 0), bg_color=(0, 0, 0, 0.5))
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)

        detections = np.array(detections) if detections else np.empty((0, 5))
        tracked_objects = sort_tracker.update(detections)

        for obj in tracked_objects:
            x1, y1, x2, y2, track_id = map(int, obj)
            if track_id not in object_classes:
                object_classes[track_id], object_scores[track_id] = label, score
            fixed_label, fixed_score = object_classes[track_id], object_scores[track_id]
            display_text = f'{fixed_label} ({fixed_score * 100:.1f}%)'
            draw_label(frame, display_text, x1, y1)
            if (y1 + y2) // 2 > COUNTER_LINE_Y and track_id not in counted_ids:
                counted_ids.add(track_id)
                if fixed_label == '1kg':
                    product_count_1kg += 1
                elif fixed_label == '500grs':
                    product_count_500grs += 1

        cv2.line(frame, (0, COUNTER_LINE_Y), (frame.shape[1], COUNTER_LINE_Y), (0, 0, 255), 2)
        cv2.putText(frame, f'Paquetes de 1kg: {product_count_1kg}', (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 255, 255), 3)
        cv2.putText(frame, f'Paquetes de 500grs: {product_count_500grs}', (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 255, 255), 3)
        cv2.putText(frame, f'Estancamientos: {stagnation_count}', (10, 110), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 0, 255), 3)

        cv2.imshow('YOLO SORT Real-Time Detection', cv2.resize(frame, None, fx=SCALE_FACTOR, fy=SCALE_FACTOR))
        if cv2.waitKey(1) & 0xFF == ord('q'): break

    print(f'Total de productos contados: {product_count}')
    
    stream.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
