import cv2
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import json
import time

# Ruta del video
video_path = "C:\\Users\\56975\\Desktop\\Contador_Video.mp4"

# Coordenadas de la región de interés
x, y, w, h = 125, 661, 231, 28

# Función para cargar credenciales del archivo JSON
def load_credentials():
    with open('config.json') as f:
        return json.load(f)

# Función para enviar correos 
def send_email(subject, body, to_email):
    creds = load_credentials()
    
    smtp_server = creds['smtp_server']
    smtp_port = creds['smtp_port']
    smtp_username = creds['smtp_username']
    smtp_password = creds['smtp_password']
    
    msg = MIMEMultipart()
    msg['From'] = smtp_username
    msg['To'] = to_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))
    
    try:
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(smtp_username, smtp_password)
        server.send_message(msg)
        server.quit()
        print(f"Correo enviado exitosamente: {subject}")
    except Exception as e:
        print(f"Error al enviar el correo: {e}")

# Inicializar el video
cap = cv2.VideoCapture(video_path)

# Inicializar el sustractor de fondo
fgbg = cv2.createBackgroundSubtractorMOG2(history=500, varThreshold=16, detectShadows=True)

# Inicializar el contador de objetos
object_count = 0
object_in_roi = False

# Parámetros para la detección de contornos
min_contour_area = 1200

# Email destinatario
destinatario = 'sanmaglass@gmail.com'

while True:
    # Leer un cuadro del video
    ret, frame = cap.read()
    if not ret:
        # Si se llega al final del video, reiniciar desde el inicio
        cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
        ret, frame = cap.read()

    # Recortar la región de interés (ROI)
    roi = frame[y:y+h, x:x+w]

    # Aplicar el sustractor de fondo a la ROI
    fgmask = fgbg.apply(roi)

    # Mejorar la máscara
    fgmask = cv2.morphologyEx(fgmask, cv2.MORPH_OPEN, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3,3)))
    fgmask = cv2.dilate(fgmask, None, iterations=2)

    # Encontrar contornos en la ROI
    contours, _ = cv2.findContours(fgmask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Detectar objetos en la ROI
    detected_objects = 0
    for contour in contours:
        if cv2.contourArea(contour) > min_contour_area:  # Filtrar pequeños contornos
            (cx, cy, cw, ch) = cv2.boundingRect(contour)
            cv2.rectangle(roi, (cx, cy), (cx+cw, cy+ch), (0, 255, 0), 2)
            detected_objects += 1

    # Si se detecta al menos un objeto en la ROI
    if detected_objects > 0:
        if not object_in_roi:
            object_in_roi = True
            object_count += 1
            
            # Enviar alerta cada 10 objetos detectados
            if object_count % 10 == 0:
                subject = f"Alerta: Se han contado {object_count} paquetes"
                body = f"Se han detectado {object_count} paquetes en la región de interés."
                send_email(subject, body, destinatario)
    else:
        object_in_roi = False

    # Mostrar el contador en el cuadro
    cv2.putText(frame, f"Count: {object_count}", (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
    
    # Dibujar la ROI en el cuadro completo
    cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)
    cv2.imshow("Video with ROI", frame)

    # Salir del bucle si se presiona la tecla 'q'
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Liberar el video y cerrar todas las ventanas
cap.release()
cv2.destroyAllWindows()

# Mostrar el conteo total
print(f"Total objects counted: {object_count}")
