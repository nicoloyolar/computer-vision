from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib
import random
import time
import json

class correoReporte:
    """Esta clase permite el envío de mensajería mediante correo electrónico"""
    def __init__(self, config_path='config.json'):
        self.config_path = config_path
        self.creds = self.load_credentials()
        self.destinatarios = self.creds.get('destinatarios', [])
        self.cc = self.creds.get('cc', [])
        self.conteo_total = 0

    def load_credentials(self):
        with open(self.config_path) as f:
            return json.load(f)

    def send_email(self, subject, body):
        smtp_server = self.creds['smtp_server']
        smtp_port = self.creds['smtp_port']
        smtp_username = self.creds['smtp_username']
        smtp_password = self.creds['smtp_password']

        msg = MIMEMultipart()
        msg['From'] = smtp_username
        msg['To'] = ', '.join(self.destinatarios)
        msg['Cc'] = ', '.join(self.cc)
        msg['Subject'] = subject

        msg.attach(MIMEText(body, 'plain'))

        try:
            server = smtplib.SMTP(smtp_server, smtp_port)
            server.starttls()
            server.login(smtp_username, smtp_password)
            server.send_message(msg)
            server.quit()
            print(f"Correo enviado: {subject} a {msg['To']} con CC a {msg['Cc']}")
        except Exception as e:
            print(f"Error al enviar el correo: {e}")

    def reportes(self, hora):
        conteo = random.randint(50, 200)
        subject = f"Reporte conteo {hora} AM" if hora < 12 else f"Reporte conteo {hora % 12} PM"
        body = f"Cantidad de paquetes contabilizados horario {hora} AM: {conteo}" if hora < 12 else f"Cantidad de paquetes contabilizados horario {hora % 12} PM: {conteo}"
        return subject, body, conteo

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

if __name__ == "__main__":
    
    reporte = correoReporte()

    reporte.enviar_correos()
