import cv2
from video_stream import VideoStream
from yolo_detection import YOLODetector

MODEL_PATH      = "C:\\Users\\Administrador\\Desktop\\proyecto_contador\\modelo\\modelofinalcombinado.pt" # modelo direccon ruta
VIDEO_PATH      = 'C:\\Users\\Administrador\\Downloads\\Actual.mp4'  # poner ruta actual pc 
SCALE_FACTOR    = 0.5

stream      = VideoStream(VIDEO_PATH)
detector    = YOLODetector(MODEL_PATH)

product_count   = 0
unique_ids      = set()

while stream.cap.isOpened():
    ret, frame = stream.read_frame()
    if not ret:
        stream.release()
        stream = VideoStream(VIDEO_PATH)
        continue

    results = detector.detect_objects(frame)

    for detection in results[0].boxes:
        if detection.conf >= detector.confidence_threshold:
            x1, y1, x2, y2 = map(int, detection.xyxy[0])
            label = detector.model.names[int(detection.cls)]
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.putText(frame, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
            product_id = f'{x1}-{y1}-{x2}-{y2}'
            if product_id not in unique_ids:
                unique_ids.add(product_id)
                product_count += 1

    cv2.putText(frame, f'Total Count: {product_count}', (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)
    resized_frame = cv2.resize(frame, None, fx=SCALE_FACTOR, fy=SCALE_FACTOR)
    cv2.imshow('YOLO Real-Time Detection', resized_frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

stream.release()
cv2.destroyAllWindows()
