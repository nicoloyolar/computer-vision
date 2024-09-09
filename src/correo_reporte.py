from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib
import random
import time
import json

class correoReporte:
    """Esta clase permite el envío de mensajería mediante correo electrónico"""
    def __init__(self, config_path='config.json'):
        self.config_path    = config_path
        self.creds          = self.load_credentials()
        self.destinatarios  = self.creds.get('destinatarios', [])
        self.cc             = self.creds.get('cc', [])
        self.conteo_total   = 0

    def load_credentials(self):
        """Esta método trae las credenciales desde el archivo de configuración para enviar mensajería por correo"""
        try:
            with open(self.config_path) as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"Error: El archivo de configuración '{self.config_path}' no se encontró.")
            raise
        except json.JSONDecodeError:
            print(f"Error: El archivo de configuración '{self.config_path}' no se puede parsear.")
            raise

    def send_email(self, subject, body):
        """Esta función permite enviar correos mediante un servidor y configuración smtp previamente establecida"""
        smtp_server     = self.creds['smtp_server']
        smtp_port       = self.creds['smtp_port']
        smtp_username   = self.creds['smtp_username']
        smtp_password   = self.creds['smtp_password']

        msg = MIMEMultipart()
        msg['From']     = smtp_username
        msg['To']       = ', '.join(self.destinatarios)
        msg['Cc']       = ', '.join(self.cc)
        msg['Subject']  = subject

        msg.attach(MIMEText(body, 'plain'))

        try:
            with smtplib.SMTP(smtp_server, smtp_port) as server:
                server.starttls()
                server.login(smtp_username, smtp_password)
                server.send_message(msg)
            print(f"Correo enviado: {subject} a {msg['To']} con CC a {msg['Cc']}")
        
        except smtplib.SMTPAuthenticationError:
            print(f"Error: Fallo en la autenticación con el servidor SMTP. Verifica el usuario y la contraseña.")
        
        except smtplib.SMTPConnectError:
            print(f"Error: No se pudo conectar al servidor SMTP. Verifica la configuración del servidor.")
        
        except smtplib.SMTPException as e:
            print(f"Error general al enviar el correo: {e}")
        
        except Exception as e:
            print(f"Error inesperado: {e}")

    def reportes(self, hora):
        """Genera un reporte mediante correo electrónico para notificar cuantos paquetes han sido contabilizados en cierto horario"""
        try:
            conteo = random.randint(50, 200)
            subject = f"Reporte conteo {hora} AM" if hora < 12 else f"Reporte conteo {hora % 12} PM"
            body = f"Cantidad de paquetes contabilizados horario {hora} AM: {conteo}" if hora < 12 else f"Cantidad de paquetes contabilizados horario {hora % 12} PM: {conteo}"
            return subject, body, conteo
        except Exception as e:
            print(f"Error al generar el reporte: {e}")
            return "Error", "No se pudo generar el reporte", 0

    def enviar_correos(self):
        """Esta función sirve para simulación de envío de correos"""
        h_inicio = 8
        h_fin = 18

        for hora in range(h_inicio, h_fin + 1):
            subject, body, conteo = self.reportes(hora)
            self.conteo_total += conteo
            self.send_email(subject, body)
            if hora < h_fin:
                time.sleep(5)

        final_subject   = "Reporte final turno diurno 8 AM-18 PM"
        final_body      = f"Cantidad total de paquetes contabilizados en el turno diurno: {self.conteo_total}"
        
        self.send_email(final_subject, final_body)

if __name__ == "__main__":
    try:
        reporte = correoReporte()
        reporte.enviar_correos()
    except Exception as e:
        print(f"Error en la ejecución del programa: {e}")
