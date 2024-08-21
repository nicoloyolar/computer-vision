from config import DB_CONFIG
import mysql.connector

try:
    conn = mysql.connector.connect(
        host=DB_CONFIG['host'],
        port=DB_CONFIG['port'],
        user=DB_CONFIG['user'],
        password=DB_CONFIG['password'],
        database=DB_CONFIG['database']
    )
    if conn.is_connected():
        print("Conexión exitosa a la base de datos")
        
except mysql.connector.Error as err:
    print(f"Error: {err}")

