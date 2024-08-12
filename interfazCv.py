import os
import cv2
from PyQt5.QtWidgets import QMainWindow, QLabel, QPushButton, QComboBox, QVBoxLayout, QWidget, QHBoxLayout
from PyQt5.QtGui import QImage, QPixmap, QIcon, QPainter, QPainterPath
from PyQt5.QtCore import QTimer, Qt, QRectF

class VideoProcessor(QMainWindow):
    def __init__(self, rtsp_url, roi=None):
        super().__init__()
        self.rtsp_url = rtsp_url
        self.roi = roi
        self.desired_width = 640
        self.desired_height = 480
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('Conteo productos/Control calidad')
        self.setWindowIcon(QIcon(self.get_icon_path()))
        self.setGeometry(100, 100, 800, 700)

        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)

        main_layout = QHBoxLayout()
        control_layout = QVBoxLayout()

        logo_label = QLabel(self)
        pixmap = self.get_pixmap(self.get_icon_path(), 150, 75)
        if pixmap:
            logo_label.setPixmap(pixmap)
            logo_label.setAlignment(Qt.AlignCenter)
        else:
            logo_label.setText("Logo no encontrado")
            logo_label.setAlignment(Qt.AlignCenter)
        control_layout.addWidget(logo_label)

        control_label = QLabel("Control Panel", self)
        control_label.setStyleSheet("""
            font-size: 16px;
            font-weight: bold;
            color: #34495e;
            background-color: #ecf0f1;
            padding: 5px;
            margin-bottom: 20px;
            border-radius: 5px;
        """)
        control_label.setAlignment(Qt.AlignCenter)
        control_layout.addWidget(control_label)

        buttons = [
            ('Alertas', '#E8D5C4'),
            ('Cambiar Horarios', '#E8D5C4'),
            ('Análisis Contador', '#E8D5C4'),
            ('Bases de datos', '#E8D5C4')
        ]

        for text, color in buttons:
            button = QPushButton(text, self)
            button.setStyleSheet(f"""
                background-color: {color};
                font-size: 12px;
                font-weight: bold;
                padding: 10px;
                border-radius: 10px;
                border: 2px solid #34495e;
                margin-bottom: 10px;
            """)
            button.setCursor(Qt.PointingHandCursor)
            control_layout.addWidget(button)

        control_layout.addStretch()

        
        mode_label = QLabel("Modo de Visualización:", self)
        mode_label.setStyleSheet("font-size: 14px; font-weight: bold;")
        control_layout.addWidget(mode_label)

        self.mode_combo = QComboBox(self)
        self.mode_combo.addItems(["Normal", "Escala de Grises", "Umbralización"])
        control_layout.addWidget(self.mode_combo)

        main_layout.addLayout(control_layout)

    
        self.video_label = QLabel(self)
        self.video_label.setFixedSize(self.desired_width, self.desired_height)
        self.video_label.setStyleSheet("background-color: black; border-radius: 15px; border: 2px solid #34495e;")
        main_layout.addWidget(self.video_label)

        central_widget.setLayout(main_layout)

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)

        self.conectar_camara()

    def get_icon_path(self):
        return os.path.join("assets", "logoStpng.png")

    def get_pixmap(self, path, width, height):
        if os.path.exists(path):
            return QPixmap(path).scaled(width, height, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        return None

    def conectar_camara(self):
        self.cap = cv2.VideoCapture(self.rtsp_url)
        if self.cap.isOpened():
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
            self.cap.set(cv2.CAP_PROP_FPS, 24)
            self.timer.start(30)

    def update_frame(self):
        ret, frame = self.cap.read()
        if ret:
            frame = self.procesar_frame(frame)
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame_resized = cv2.resize(frame, (self.desired_width, self.desired_height), interpolation=cv2.INTER_AREA)
            qt_image = QImage(frame_resized.data, frame_resized.shape[1], frame_resized.shape[0], QImage.Format_RGB888)
            rounded_pixmap = self.apply_rounded_corners(QPixmap.fromImage(qt_image), 15)
            self.video_label.setPixmap(rounded_pixmap)

    def procesar_frame(self, frame):
        if self.roi:
            x, y, w, h = self.roi
            x, y = max(0, min(x, frame.shape[1] - 1)), max(0, min(y, frame.shape[0] - 1))
            w, h = min(w, frame.shape[1] - x), min(h, frame.shape[0] - y)
            roi = frame[y:y+h, x:x+w]

            if self.mode_combo.currentText() == "Escala de Grises":
                processed = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
                processed = cv2.cvtColor(processed, cv2.COLOR_GRAY2BGR)
            elif self.mode_combo.currentText() == "Umbralización":
                gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
                _, processed = cv2.threshold(gray, 128, 255, cv2.THRESH_BINARY)
                processed = cv2.cvtColor(processed, cv2.COLOR_GRAY2BGR)
            else:
                processed = roi

            frame[y:y+h, x:x+w] = processed
        return frame

    def apply_rounded_corners(self, pixmap, radius):
        rounded = QPixmap(pixmap.size())
        rounded.fill(Qt.transparent)

        painter = QPainter(rounded)
        painter.setRenderHint(QPainter.Antialiasing)
        path = QPainterPath()
        path.addRoundedRect(QRectF(pixmap.rect()), radius, radius)
        painter.setClipPath(path)
        painter.drawPixmap(0, 0, pixmap)
        painter.end()

        return rounded

    def closeEvent(self, event):
        if self.cap:
            self.cap.release()
        event.accept()