import os
import cv2
import tkinter as tk
from tkinter import Label, Button, OptionMenu, StringVar
from PIL import Image, ImageTk

class VideoProcessor:
    """Procesa el video en tiempo real desde una cámara IP con diferentes modos de visualización."""

    def __init__(self, rtsp_url, roi=None):
        self.rtsp_url = rtsp_url
        self.cap = None
        self.roi = roi  # (x, y, width, height)
        self.window = None
        self.canvas = None
        self.mode = None

    def conectar_camara(self):
        """Conecta a la cámara IP."""
        self.cap = cv2.VideoCapture(self.rtsp_url)
        return self.cap.isOpened()

    def procesar_frame(self, frame):
        """Aplica el procesamiento según el modo seleccionado."""
        if self.roi:
            x, y, w, h = self.roi
            roi = frame[y:y+h, x:x+w]

            if self.mode.get() == "Escala de Grises":
                processed = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
            elif self.mode.get() == "Umbralización":
                gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
                _, processed = cv2.threshold(gray, 128, 255, cv2.THRESH_BINARY)
            else:  # Modo Normal
                processed = roi

            frame[y:y+h, x:x+w] = cv2.cvtColor(processed, cv2.COLOR_GRAY2BGR) if self.mode.get() != "Normal" else processed
        return frame

    def iniciar_tkinter(self):
        """Inicia la interfaz gráfica de usuario."""
        self.window = tk.Tk()
        self.window.title("Procesamiento de Video")
        self.window.geometry("1280x720")
        self.window.minsize(1280, 720)  # Tamaño mínimo para evitar agrandamiento no deseado
        self.window.maxsize(1280, 720)  # Tamaño máximo fijo para evitar el color beige

        # Fondo y configuración del panel de control
        control_frame = tk.Frame(self.window, bg="#F4F4F4", width=250, height=720)
        control_frame.pack(side=tk.LEFT, fill=tk.Y)

        # Agrega el logo de la empresa
        logo_path = os.path.join("assets", "pngEmpresa.png")  # Asegúrate de que esta ruta es correcta
        logo = Image.open(logo_path).resize((200, 100), Image.ANTIALIAS)
        logo = ImageTk.PhotoImage(logo)
        tk.Label(control_frame, image=logo, bg="#F4F4F4").pack(pady=10)

        # Botón de título del panel de control
        Label(control_frame, text="Control Panel", bg="#34495e", fg="#ecf0f1", font=("Segoe UI", 18, "bold"),
              relief="raised", bd=4, padx=10, pady=5).pack(pady=10)

        # Botones de control
        Button(control_frame, text="Alertas", bg="#A3D2CA", fg="#333333", font=("Segoe UI", 14, "bold"),
               width=20, height=2, relief="raised", bd=3).pack(pady=10)
        Button(control_frame, text="Cambiar Horarios", bg="#E8A87C", fg="#333333", font=("Segoe UI", 14, "bold"),
               width=20, height=2, relief="raised", bd=3).pack(pady=10)
        Button(control_frame, text="Análisis Contador", bg="#C38D9E", fg="#333333", font=("Segoe UI", 14, "bold"),
               width=20, height=2, relief="raised", bd=3).pack(pady=10)

        # Selector de modo de procesamientos
        Label(control_frame, text="Modo de Visualización", bg="#F4F4F4", fg="#333333", font=("Segoe UI", 12, "bold")).pack(pady=10)
        self.mode = StringVar(value="Umbralización")
        mode_menu = OptionMenu(control_frame, self.mode, "Normal", "Escala de Grises", "Umbralización")
        mode_menu.config(bg="#bdc3c7", fg="#333333", font=("Segoe UI", 12), relief="raised", bd=2, width=15)
        mode_menu.pack(pady=10)

        # Canvas para video
        self.canvas = tk.Canvas(self.window, width=1024, height=720, bg="#FAF3E0")
        self.canvas.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        self.actualizar_frame()
        self.window.mainloop()

    def actualizar_frame(self):
        """Actualiza y muestra el siguiente frame del video."""
        ret, frame = self.cap.read()
        if ret:
            frame = self.procesar_frame(frame)
            image = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            image = image.resize((1024, 720), Image.ANTIALIAS)
            photo = ImageTk.PhotoImage(image=image)
            self.canvas.create_image(0, 0, image=photo, anchor=tk.NW)
            self.canvas.image = photo

        self.window.after(30, self.actualizar_frame)

    def iniciar(self):
        """Inicia el procesamiento de video."""
        if self.conectar_camara():
            self.iniciar_tkinter()
        self.cap.release()

def main():
    rtsp_url = "rtsp://admin:admin123@192.168.31.108:554/cam/realmonitor?channel=5&subtype=0"
    processor = VideoProcessor(rtsp_url, roi=(1228, 6, 1020, 1434))
    processor.iniciar()

if __name__ == "__main__":
    main()
