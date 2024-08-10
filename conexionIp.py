import cv2

# URL RTSP de la cámara
rtsp_url = "rtsp://admin:admin123@192.168.31.108:554/cam/realmonitor?channel=5&subtype=0"

# Conectar a la cámara
cap = cv2.VideoCapture(rtsp_url)

if not cap.isOpened():
    print("No se pudo conectar a la cámara.")
else:
    print("Conectado a la cámara IP Proyecto St.")

# Bucle para leer frames de la cámara
while True:
    ret, frame = cap.read()
    if not ret:
        print("No se pudo leer el frame.")
        break

    # Redimensionar el frame para que no se vea tan grande
    frame_resized = cv2.resize(frame, (640, 480))

    # Convertir a escala de grises
    gray_frame = cv2.cvtColor(frame_resized, cv2.COLOR_BGR2GRAY)

    # Aplicar umbralización (después de convertir a escala de grises)
    _, thresh_frame = cv2.threshold(gray_frame, 128, 255, cv2.THRESH_BINARY)

    # Mostrar el video en escala de grises y el video umbralizado
    cv2.imshow("Video en Escala de Grises", gray_frame)
    cv2.imshow("Video Umbralizado", thresh_frame)

    # Salir del bucle si se presiona la tecla 'q'
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Liberar los recursos
cap.release()
cv2.destroyAllWindows()
