import serial

def send_sms(phone_number, message):
    try:
        s = serial.Serial('COM1', 9600)  # Configura el puerto COM y la velocidad
        s.write(b'ATZ\r')  # Envía un reset al módem
        s.write(b'AT+CMGF=1\r')  # Configura el modo SMS
        s.write(f'AT+CMGS="{phone_number}"\r'.encode())  # Especifica el número de teléfono
        s.write(f'{message}\x1A'.encode())  # Envía el mensaje (terminado con Ctrl+Z)
        print("Mensaje enviado correctamente")
        s.close()
    except Exception as e:
        print(f"Error al enviar el SMS: {e}")

# Ejemplo de uso
phone_number = "+5491126927297"  # Número de teléfono del destinatario
message = "¡Hola! Esto es un SMS desde Python."
send_sms(phone_number, message)
