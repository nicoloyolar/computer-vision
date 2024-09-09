"""Este es el punto de entrada principal de la aplicación de Control de Calidad de choritos"""

from PyQt5.QtWidgets import QApplication
from main_gui import VideoProcessor
from config import roi, url
import sys

### SE DEBE OPTIMIZAR ###

def main():
    """Este es el punto de entrada de la aplicación de Control de Calidad"""
    app = QApplication(sys.argv)
    rtsp_url = url
    processor = VideoProcessor(rtsp_url, roi = roi)
    processor.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
