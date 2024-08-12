from interfazCv import VideoProcessor

def main():
    rtsp_url = "rtsp://admin:admin123@192.168.31.108:554/cam/realmonitor?channel=5&subtype=0"
    processor = VideoProcessor(rtsp_url=rtsp_url)

    processor.roi = (1228, 6, 1020, 1434)  # Coordenadas y dimensiones de la ROI conocidas

    if processor.conectar_camara():
        processor.iniciar_tkinter()

    processor.liberar_recursos()

if __name__ == "__main__":
    main()
