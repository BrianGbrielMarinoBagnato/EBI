import sqlite3
from datetime import datetime
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import os
# Conexión a la base de datos
def conectar_base():
    return sqlite3.connect('EBI.db')

# Crear la tabla si no existe, agregando un campo para la fecha y hora de registro
def crear_tabla():
    conn = conectar_base()
    cur = conn.cursor()
    cur.execute("""CREATE TABLE IF NOT EXISTS registrados(
        nombre VARCHAR(60),
        apellido VARCHAR(40),
        email TEXT,
        dni INT PRIMARY KEY,
        contraseña TEXT,
        confirmar_contraseña TEXT,
        fecha_registro TEXT,
        foto TEXT
    )""")
    conn.commit()
    conn.close()

# Función para insertar los datos en la base de datos
def datos_insertados(nombre, apellido, email, dni, contraseña, confirmar_contraseña, fecha_registro, foto):
    try:
        conn = conectar_base()
        cur = conn.cursor()
        cur.execute("""INSERT INTO registrados (nombre, apellido, email, dni, contraseña, confirmar_contraseña, fecha_registro, foto)
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                    (nombre, apellido, email, dni, contraseña, confirmar_contraseña, fecha_registro, foto))
        conn.commit()
        conn.close()
    except sqlite3.IntegrityError as e:
        print(f"Error al insertar los datos: {e}")



# Función para buscar un usuario por su DNI
def buscar(dni):
    conn = sqlite3.connect('EBI.db')  # Abrir la conexión a la base de datos
    conn = conectar_base()
    cur = conn.cursor()
    cur.execute("SELECT nombre FROM registrados WHERE dni = ?", (dni,))
    resultado = cur.fetchone()  # Recupera una sola fila del resultado
    conn.close()  # Cerrar la conexión a la base de datos
    return resultado[0] if resultado else None  # Devuelve el nombre si se encuentra, o None si no se encuentra
    
# Función para mostrar los usuarios registrados en una interfaz gráfica
def mostrar_usuarios():
    conn = conectar_base()
    cur = conn.cursor()
    cur.execute("SELECT * FROM registrados")
    registros = cur.fetchall()

    # Crear ventana
    ventana = tk.Tk()
    ventana.title("Usuarios Registrados")
    # Obtener dimensiones de la pantalla
    screen_width = ventana.winfo_screenwidth()
    screen_height = ventana.winfo_screenheight()
    print(screen_width,'-',screen_height)
    # Calcular factores de escala
    scale_width = (screen_width / 1280)  # 1280 es el ancho base
    scale_height = (screen_height / 720)  # 720 es la altura base
    ventana.geometry("%dx%d+0+0" % (screen_width, screen_height))
    # Crear tabla
    tabla = ttk.Treeview(ventana, columns=('Nombre', 'Apellido', 'Email', 'DNI', 'Contraseña', 'Confirmar Contraseña', 'Fecha Registro', 'Foto'), show='headings')
    for col in tabla["columns"]:
        tabla.heading(col, text=col)

    # Insertar datos en la tabla
    for registro in registros:
        foto_path = registro[7]  # Suponiendo que la foto está en la octava columna
        if os.path.exists(foto_path):
            img = Image.open(foto_path)
            img.thumbnail((100, 100))  # Ajustar tamaño de la imagen
            img_tk = ImageTk.PhotoImage(img)
        else:
            img_tk = None

        # Usar la imagen en la tabla
        tabla.insert('', 'end', values=registro + (img_tk,))

    tabla.pack()

    ventana.mainloop()
    conn.close()

def mostrar_imagen_desde_db(dni):
    # Crear la ventana de tkinter primero
    ventana = tk.Tk()
    ventana.title("Imagen del Usuario")
    # Conectar a la base de datos
    conn = conectar_base()
    cur = conn.cursor()

    # Obtener la ruta de la imagen desde la base de datos
    cur.execute("SELECT foto FROM registrados WHERE dni = ?", (dni,))
    resultado = cur.fetchone()
    

    # Obtener la ruta de la imagen desde la base de datos
    cur.execute("SELECT foto FROM registrados WHERE dni = ?", (dni,))
    resultado = cur.fetchone()
    
    if resultado:
        foto_path = resultado[0]  # La ruta de la imagen está en la primera (y única) columna del resultado

        if os.path.exists(foto_path):
            # Convertir la ruta de la imagen en una imagen que tkinter pueda mostrar
            imagen = Image.open(foto_path)
            imagen_tk = ImageTk.PhotoImage(imagen)

            # Mostrar la imagen en un Label
            img_label = tk.Label(ventana, image=imagen_tk)
            img_label.pack()

            # Necesario para evitar que la imagen sea recolectada por el GC
            img_label.image = imagen_tk
        else:
            print("La ruta de la imagen no existe:", foto_path)
    else:
        print("No se encontró ningún usuario con el DNI proporcionado.")

    # Ejecutar el bucle principal de la ventana
    ventana.mainloop()

    # Cerrar la conexión a la base de datos
    conn.close()
# Muestra la interfaz gráfica con los usuarios registrados

