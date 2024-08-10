import cv2

# URL RTSP de la cámara
rtsp_url = "rtsp://admin:admin123@192.168.31.108:554/cam/realmonitor?channel=5&subtype=0"
cap = cv2.VideoCapture(rtsp_url)

if not cap.isOpened():
    print("Acceso denegado.")
else:
    print("Conectado a la cámara IP")

while True:
    ret, frame = cap.read()
    if not ret:
        print("No se pudo leer el frame.")
        break

    # dimensiones frame
    frame_resized = cv2.resize(frame, (640, 480))

    # Convertir a escala de grises
    gray_frame = cv2.cvtColor(frame_resized, cv2.COLOR_BGR2GRAY)

    # unmbralizacion)
    _, thresh_frame = cv2.threshold(gray_frame, 128, 255, cv2.THRESH_BINARY)

    cv2.imshow("Video en Escala de Grises", gray_frame)
    cv2.imshow("Video Umbralizado", thresh_frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Liberar los recursos
cap.release()
cv2.destroyAllWindows()
