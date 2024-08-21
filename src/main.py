"""Este es el punto de entrada principal de la aplicación de Control de Calidad de choritos"""

from PyQt5.QtWidgets import QApplication
from interfazCv import VideoProcessor
import sys

def main():
    app = QApplication(sys.argv)
    rtsp_url = "rtsp://admin:admin123@192.168.31.108:554/cam/realmonitor?channel=5&subtype=0"
    processor = VideoProcessor(rtsp_url, roi=(1228, 6, 1020, 1434))
    processor.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
