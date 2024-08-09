from computervission_2 import CorreoReporte

def main():
    reporte = CorreoReporte(destinatario='sanmaglass@gmail.com')
    reporte.enviar_correos()

if __name__ == "__main__":
    main()
