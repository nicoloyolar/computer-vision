import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import random
import time
import json

class CorreoReporte:
    def __init__(self, config_path='config.json', destinatario='sanmaglass@gmail.com'):
        self.config_path = config_path
        self.destinatario = destinatario
        self.conteo_total = 0
        self.creds = self.load_credentials()

    def load_credentials(self):
        with open(self.config_path) as f:
            return json.load(f)
    
    def enviar_correos(self):
        h_inicio = 8
        h_fin = 18

        for hora in range(h_inicio, h_fin + 1):
            subject, body, conteo = self.reportes(hora)
            self.conteo_total += conteo
            self.send_email(subject, body)
            if hora < h_fin:  
                time.sleep(5) 

        final_subject = "Reporte final turno diurno 8 AM-18 PM"
        final_body = f"Cantidad total de paquetes contabilizados en el turno diurno: {self.conteo_total}"
        self.send_email(final_subject, final_body)

