import cv2
from video_stream import VideoStream
from yolo_detection import YOLODetector

MODEL_PATH = "C:\\Users\\FULLUNLOCK\\Desktop\\DEVELOPMENT\\computer-vision\\proyecto_contador\\model_video\\modelofinalcombinado.pt"
VIDEO_PATH = 'C:\\Users\\FULLUNLOCK\\Desktop\\DEVELOPMENT\\computer-vision\\proyecto_contador\\model_video\\Actual.mp4'
SCALE_FACTOR = 0.5
frame_skip = 5 

def main():
    stream = VideoStream(VIDEO_PATH)
    detector = YOLODetector(MODEL_PATH)
    frame_count = 0

    while stream.cap.isOpened():
        ret, frame = stream.read_frame()
        if not ret:
            break

        frame_count += 1
        if frame_count % frame_skip != 0:
            continue  

        results = detector.detect_objects(frame)

        for detection in results[0].boxes:
            if detection.conf >= detector.confidence_threshold:
                x1, y1, x2, y2 = map(int, detection.xyxy[0])
                label = detector.model.names[int(detection.cls)]
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                cv2.putText(frame, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)

        resized_frame = cv2.resize(frame, None, fx=SCALE_FACTOR, fy=SCALE_FACTOR)
        cv2.imshow('YOLO Real-Time Detection', resized_frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    stream.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
