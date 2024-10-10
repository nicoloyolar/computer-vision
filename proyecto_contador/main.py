import cv2
from video_stream import VideoStream
from yolo_detection import YOLODetector

MODEL_PATH = "C:\\Users\\FULLUNLOCK\\Desktop\\DEVELOPMENT\\computer-vision\\proyecto_contador\\model_video\\modelofinalcombinado.pt"
VIDEO_PATH = 'C:\\Users\\FULLUNLOCK\\Desktop\\DEVELOPMENT\\computer-vision\\proyecto_contador\\model_video\\Actual.mp4'
SCALE_FACTOR = 0.5
frame_skip = 5

COUNTER_LINE_Y = 1100  # Ajusta esto según tu video
product_count = 0
products_passed = {}  # Usar un diccionario para rastrear los IDs de productos detectados

def main():
    global product_count  
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
                
                center_y = (y1 + y2) // 2 
                product_id = f"{label}_{frame_count}"  # Crear un ID único basado en el label y el frame

                # Inicializar el producto en el diccionario si no existe
                if product_id not in products_passed:
                    products_passed[product_id] = {'counted': False, 'crossed': False}  # Usar un flag para rastrear el estado

                # Comprobar si el producto ha cruzado la línea de conteo
                if center_y > COUNTER_LINE_Y and not products_passed[product_id]['crossed']:
                    product_count += 1
                    products_passed[product_id]['counted'] = True  # Marcar como contado
                    products_passed[product_id]['crossed'] = True  # Marcar que ha cruzado
                    print(f'Producto contado: {label}, Total: {product_count}')

                # Resetear el estado cuando el objeto está por encima de la línea
                if center_y < COUNTER_LINE_Y and products_passed[product_id]['crossed']:
                    products_passed[product_id]['crossed'] = False  # Permitir que se cuente de nuevo al cruzar hacia arriba
                    products_passed[product_id]['counted'] = False  # Resetear el conteo

                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                cv2.putText(frame, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)

        # Dibujar la línea de conteo
        cv2.line(frame, (0, COUNTER_LINE_Y), (frame.shape[1], COUNTER_LINE_Y), (0, 0, 255), 2)

        resized_frame = cv2.resize(frame, None, fx=SCALE_FACTOR, fy=SCALE_FACTOR)
        cv2.imshow('YOLO Real-Time Detection', resized_frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    print(f'Total de productos contados: {product_count}')
    
    stream.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
