# integrar base de datos    (cada una hora se envía el conteo a la BD)
# alertas                   (cada una hora se envía un correo con el conteo - evento de estancamiento)

from video_stream import VideoStream
from yolo_detection import YOLODetector
from sort import Sort
from path import MODEL_PATH, VIDEO_PATH
import cv2
import numpy as np
import os

class ObjectCounter:
    """Esta clase permite detectar, identificar, clasificar y contar distintos tipos de productos en una línea de producción mediante un sistema de visión artificial"""
    def __init__(self, model_path, video_path):
        self.model_path             = model_path
        self.video_path             = video_path
        self.scale_factor           = 0.6
        self.counter_line_y         = 1000
        self.product_count_1kg      = 0
        self.product_count_500grs   = 0
        self.stagnation_count       = 0
        self.sort_tracker           = Sort(max_age=3, min_hits=2, iou_threshold=0.3)
        self.counted_ids            = set()
        self.object_classes         = {}
        self.object_scores          = {}

        self.check_files()

    def check_files(self):
        """Este método comprueba la existencia de los archivos especificados y lanza una excepción si alguno falla"""
        if not os.path.exists(self.model_path):
            raise FileNotFoundError(f"El modelo no se encuentra en {self.model_path}")
        if not os.path.exists(self.video_path):
            raise FileNotFoundError(f"El video no se encuentra en {self.video_path}")

    def draw_label(self, frame, text, x, y, color=(0, 255, 255), bg_color=(0, 0, 0, 0.5)):
        """Este método dibuja un cuadro de texto en el marco. Acepta el texto, las coordenadas y los colores de fondo y de texto"""
        font_scale, font_thickness = 1.2, 3
        text_size = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, font_scale, font_thickness)[0]
        box_coords = ((x, y), (x + text_size[0] + 10, y - text_size[1] - 10))
        cv2.rectangle(frame, box_coords[0], box_coords[1], bg_color[:3], -1)
        cv2.putText(frame, text, (x, y - 5), cv2.FONT_HERSHEY_SIMPLEX, font_scale, color, font_thickness)

    def highlight_critical(self, frame, text, x, y):
        """Este método destaca mensajes críticos en rojo"""
        self.draw_label(frame, text, x, y, color=(0, 0, 255), bg_color=(0, 0, 0, 0.7))

    def start_video_from_minute(self, stream, minute):
        """Este método permite comenzar la reproducción el video a partir de un minuto específico"""
        fps = stream.cap.get(cv2.CAP_PROP_FPS)
        start_frame = int(minute * 60 * fps)
        stream.cap.set(cv2.CAP_PROP_POS_FRAMES, start_frame)

    def count_products(self, track_id, label):
        """Este método cuenta la cantidad de productos detectados, asegurándose de que no se cuenten dos veces"""
        if track_id not in self.counted_ids:
            self.counted_ids.add(track_id)
            if label == '1kg':
                self.product_count_1kg += 1
            elif label == '500grs':
                self.product_count_500grs += 1

    def process_frame(self, frame, detector):
        """Este método maneja la detección de objetos, actualiza el seguimiento y llama al método de conteo de productos"""
        results = detector.detect_objects(frame)
        detections = [[*map(int, detection.xyxy[0]), float(detection.conf)] for detection in results[0].boxes if detection.conf >= detector.confidence_threshold]

        for detection in detections:
            x1, y1, x2, y2, score = detection
            label = detector.model.names[int(results[0].boxes[0].cls)]
            display_text = f'{label} ({score * 100:.1f}%)'

            if label == 'estancamiento':
                self.highlight_critical(frame, display_text, x1, y1)
                if label not in self.counted_ids:
                    self.stagnation_count += 1
                    self.counted_ids.add(label)
            else:
                self.draw_label(frame, display_text, x1, y1)

            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)

        detections = np.array(detections) if detections else np.empty((0, 5))
        tracked_objects = self.sort_tracker.update(detections)

        for obj in tracked_objects:
            x1, y1, x2, y2, track_id = map(int, obj)
            if track_id not in self.object_classes:
                self.object_classes[track_id] = label
                self.object_scores[track_id] = score

            self.count_products(track_id, self.object_classes[track_id])

    def display_info(self, frame):
        """Este método dibuja información en el marco, como el conteo de productos y los estancamientos"""
        cv2.line(frame, (0, self.counter_line_y), (frame.shape[1], self.counter_line_y), (0, 0, 255), 2)
        cv2.putText(frame, f'Paquetes de 1kg: {self.product_count_1kg}', (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 255, 255), 3)
        cv2.putText(frame, f'Paquetes de 500grs: {self.product_count_500grs}', (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 255, 255), 3)
        cv2.putText(frame, f'Estancamientos: {self.stagnation_count}', (10, 110), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 0, 255), 3)

    def run(self):
        """Este es el método principal que gestiona el flujo del programa"""
        stream = VideoStream(self.video_path)
        if not stream.cap.isOpened():
            return

        detector = YOLODetector(self.model_path)
        if detector is None:
            return
        
        detector.confidence_threshold = 0.67
        self.start_video_from_minute(stream, 1)

        while stream.cap.isOpened():
            ret, frame = stream.read_frame()
            if not ret:
                break

            self.process_frame(frame, detector)
            self.display_info(frame)

            cv2.imshow('YOLO SORT Real-Time Detection', cv2.resize(frame, None, fx=self.scale_factor, fy=self.scale_factor))
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        stream.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    """Se crea una instancia de la clase principal y se ejecuta el método 'run()'"""
    try:
        counter = ObjectCounter(MODEL_PATH, VIDEO_PATH)
        counter.run()
    except Exception as e:
        print(f"Error: {e}")
