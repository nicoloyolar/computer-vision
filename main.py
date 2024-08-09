from correoReporte import correoReporte

email_test = ['nicolas.iloyolar@gmail.com', 'sanmaglass@gmail.com']

def main():
    reporte = correoReporte(destinatario=email_test)
    reporte.enviar_correos()

if __name__ == "__main__":
    main()
