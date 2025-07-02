#py -m pip install customtkinter
#py -m pip install pillow
#py -m pip install opencv-python
#py -m pip install numpy
#py -m pip install opencv-contrib-python
#py -m pip install opencv-python-headless
#py -m pip install scikit-image
#py -m pip install imageio
#py -m pip install matplotlib

import customtkinter as ctk
import tkinter as tk
from PIL import Image, ImageTk
from tkinter import PhotoImage, simpledialog, messagebox, filedialog
import Programacion.base as base
import os
import cv2
import numpy as np
import io
from PIL import Image
from skimage.metrics import structural_similarity as ssim
import cv2
from datetime import datetime
import sqlite3
    
# ---------------------------------------------Configuración básica de la ventana---------------------------------------------
ctk.set_appearance_mode("dark")
root = ctk.CTk()

root.title("Inicio de sesion/Registrarse")

# Ocultar barra de tareas
root.overrideredirect(True)

# Obtener dimensiones de la pantalla
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
print(screen_width,'-',screen_height)

# Calcular factores de escala
scale_width = (screen_width / 1280)  # 1280 es el ancho base
scale_height = (screen_height / 720)  # 720 es la altura base
print(scale_width,'-',scale_height)

# Establecer tamaño de la ventana
root.geometry("%dx%d+0+0" % (screen_width, screen_height))

###############################################################################FUNCIONES###############################################################################

# ----------------------------------------------------Botón de REGISTER---------------------------------------------
def limpiarRegistro():
    #image_label.configure(image='')  # Elimina la imagen mostrada en el label
    for entry in Entradas:  # Entradas es la lista que contiene todas las CTkEntry
        entry.delete(0, 'end')  # Borra el contenido actual del campo de entrada
        entry.configure(fg_color='#343638')  # Restablece el color del texto a gris
    DNI_entry.configure(placeholder_text='DNI - Profesor')
    
    nombre_entry.configure(placeholder_text='Nombre/s')
    apellido_s_entry.configure(placeholder_text='Apellido/s')
    mail_entry.configure(placeholder_text='e-mail')
    password_entry.configure(placeholder_text='Contraseña')
    password_confirm_entry.configure(placeholder_text='Confirmar contraseña')
#-------------------------------------------FUNCIONES DE VALIDACION---------------------------------------------------------------------#
def validarDni(P):
        if P.isdigit() and len(P) == 8:
            DNI_entry.configure(fg_color='#343638',text_color='#909298') 
            return True
        
        else:
            DNI_entry.configure(fg_color="#b74241",text_color='black')
            return True


def validarNombre(P):

    if P.isalpha():
        nombre_entry.configure(fg_color='#343638',text_color='#909298') 
        return True
    else:
        nombre_entry.configure(fg_color="#b74241",text_color='black') 
        return True

def validarApellido(P):

        if P.isalpha():
            apellido_s_entry.configure(fg_color='#343638',text_color='#909298') 
            return True
        else:
            apellido_s_entry.configure(fg_color="#b74241",text_color='black')



def validarMail(P): 

        if "@" in P and "." in P :
            mail_entry.configure(fg_color='#343638',text_color='#909298') 
            return True
        else:
            mail_entry.configure(fg_color="#b74241",text_color='black') 
            return True



def validarContrasena(P):

        if P == "":
            password_entry.configure(fg_color="#b74241",text_color='black') 
            return True
        else:
            password_entry.configure(fg_color='#343638',text_color='#909298') 
            return True

def validarConfirmarContrasena(P,Pass):
       
        if P != Pass or P=='':
           
           password_confirm_entry.configure(fg_color="#b74241",text_color='black') 
           return True
        else:
           password_confirm_entry.configure(fg_color='#343638',text_color='#909298') 
           return True
#-------------------------------------------FUNCIONES DE VALIDACION---------------------------------------------------------------------#

#----------------------------------------Función para cambiar entre Sign In y Register--------------------------------------------
def show_frame(frame):
    button_frame.configure(fg_color=sign_in_button_main.cget('fg_color'))
    if frame == sign_in_frame:
        sign_in_button.configure(fg_color=sign_in_frame.cget('fg_color'), corner_radius=20)
        register_button.configure(fg_color=register_button_main.cget('fg_color'), corner_radius=0)
        frame.tkraise()
        
    else:
        contraseña = simpledialog.askstring("Ingresar Contraseña", 
                                            "Por favor, ingrese la contraseña:", 
                                            show='*',
                                            parent=frame)  # Añadir 'parent' para centrar en 'frame'
        if contraseña is None:  # Si se presionó "Cancelar"
            return 
        if contraseña != 'admin':
            messagebox.showinfo("-- Error --", "Contraseña Incorrecta", parent=frame)
            return
        register_button.configure(fg_color=sign_in_frame.cget('fg_color'), corner_radius=20)
        sign_in_button.configure(fg_color=sign_in_button_main.cget('fg_color'), corner_radius=0)
        frame.tkraise()
        global colorBase
        colorBase=nombre_entry.cget('bg_color')
#----------------------------------------Función para cambiar entre Sign In y Register--------------------------------------------#

#-------------------------------------FUNCIONES DE COMPARACIÓN DE IMÁGENES-------------------------------------


def comparar_imagenes(img_bytes_guardada, img_bytes_capturada):
    # Convertir bytes a imágenes
    img_guardada = cv2.imdecode(np.frombuffer(img_bytes_guardada, np.uint8), cv2.IMREAD_COLOR)
    img_capturada = cv2.imdecode(np.frombuffer(img_bytes_capturada, np.uint8), cv2.IMREAD_COLOR)
    
    if img_guardada is None or img_capturada is None:
        return False

    # Crear el detector de características LBPH (Local Binary Patterns Histograms)
    face_recognizer = cv2.face.LBPHFaceRecognizer_create()
    
    # Entrenar el recognizer con la imagen guardada
    face_recognizer.train([cv2.cvtColor(img_guardada, cv2.COLOR_BGR2GRAY)], np.array([0]))

    # Comparar la imagen capturada con la imagen guardada
    label, confidence = face_recognizer.predict(cv2.cvtColor(img_capturada, cv2.COLOR_BGR2GRAY))
    
    print(f'Confianza: {confidence}')  # Para depuración
    umbral_confianza = 61.0
    
    # Retorna True si la confianza es menor que el umbral, indicando que la identidad es verificada
    return confidence < umbral_confianza

#-------------------------------------FUNCIONES PARA CARGAR IMAGEN EN LA CARPETA-------------------------------------
def cargar_imagen_guardada(nombre, dni):
    ruta_carpeta_usuario = os.path.join('usuarios', f"{nombre}_{dni}")
    ruta_imagen_guardada = os.path.join(ruta_carpeta_usuario, 'imagen.jpg')
    
    if not os.path.exists(ruta_imagen_guardada):
        return None
    
    with open(ruta_imagen_guardada, 'rb') as file:
        return file.read()

#-------------------------------------FUNCIONES PARA AUTENTICAR USUARIO-------------------------------------
def autenticar_usuario(nombre, dni):
    global cap
    cap = cv2.VideoCapture(0)
    
    if not cap.isOpened():
        messagebox.showerror("Error", "No se puede abrir la cámara.")
        return False
    
    img_bytes_guardada = cargar_imagen_guardada(nombre, dni)
    
    if img_bytes_guardada is None:
        messagebox.showerror("Error", "No se encontró la imagen guardada.")
        cap.release()
        cv2.destroyAllWindows()
        return False
    
    while cap.isOpened():
        ret, frame = cap.read()
        if ret:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))
            
            if faces:
                # Extraer el primer rostro encontrado
                x, y, w, h = faces[0]
                face_image = gray[y:y+h, x:x+w]
                
                # Convertir el rostro a bytes
                _, img_bytes_capturada = cv2.imencode('.jpg', face_image)
                img_bytes_capturada = img_bytes_capturada.tobytes()
                
                similitud = comparar_imagenes(img_bytes_guardada, img_bytes_capturada)

                if similitud:
                    messagebox.showinfo('Autenticación exitosa', 'Usuario autenticado correctamente.')
                    break
                else:
                    messagebox.showwarning('Autenticación fallida', 'El rostro capturado no coincide con el guardado.')
                    break

            cv2.imshow('Autenticación', frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
    
    cap.release()
    cv2.destroyAllWindows()


#-------------------------------------------FUNCION PARA ABRIR CAMARA-----------------------------------------------#
def abrir_camara():
    global img_bytes
    cap = cv2.VideoCapture(0)  # Intenta abrir la cámara
    
    # Verificar si la cámara se abrió correctamente
    if not cap.isOpened():
        messagebox.showerror("Error", "No se encontró ninguna cámara.")
        return  # Salir de la función si no se puede abrir la cámara
    
    # Cargar el clasificador en cascada para detección de rostros
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    
    if face_cascade.empty():
        raise IOError("No se pudo cargar el clasificador en cascada.")
    
    while cap.isOpened():
        ret, frame = cap.read()
        if ret:
            # Detectar rostros en el marco en color
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

            for (x, y, w, h) in faces:
                cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
                face_image = frame[y:y+h, x:x+w]  # Extraer el rostro en color

                # Convertir el rostro a bytes
                _, img_bytes_capturada = cv2.imencode('.jpg', face_image)
                img_bytes = img_bytes_capturada.tobytes()
                break  # Salir del bucle si detecta al menos un rostro

            cv2.imshow('Camara', frame)

            if cv2.waitKey(1) & 0xFF == ord("q"):  # Presionar 'q' para guardar la imagen
                if img_bytes:
                    messagebox.showinfo('Foto capturada', 'Foto del rostro capturada correctamente')
                else:
                    messagebox.showwarning('Advertencia', 'No se detectó ningún rostro.')
                break
        
    cap.release()
    cv2.destroyAllWindows()
#--------------------------------------FUNCION QUE MUESTRA IMAGEGN--------------------------


def mostrar_imagen(ruta_imagen):

    if not os.path.exists(ruta_imagen):
        print(f"Error: El archivo no se encuentra en la ruta: {ruta_imagen}")
        return

    ventana = tk.Tk()
    ventana.title("Mostrar Imagen")
    
    try:
        imagen = Image.open(ruta_imagen)
        imagen_tk = ImageTk.PhotoImage(imagen)
        
        etiqueta_imagen = tk.Label(ventana, image=imagen_tk)
        etiqueta_imagen.pack()
        
        etiqueta_imagen.image = imagen_tk  # Mantener una referencia a la imagen
        
        ventana.mainloop()
    except Exception as e:
        print(f"Error al mostrar la imagen: {e}")




#-------------------------------------FUNCIONES DE REGISTRO Y INICIO DE SESION-------------------------------------

def registro():
    global fecha_registro, img_bytes  # Asegúrate de que img_bytes esté disponible
    
    # Validar los campos de entrada
    try:
        validarDni(DNI_entry.get())
        validarNombre(nombre_entry.get())
        validarApellido(apellido_s_entry.get())
        validarMail(mail_entry.get())
        validarContrasena(password_entry.get())
        validarConfirmarContrasena(password_confirm_entry.get(), password_entry.get())
    except ValueError as e:
        messagebox.showwarning("Error de Validación", str(e))
        return
    
    # Contar entradas válidas
    contador = 0
    for entrada in Entradas:
        if entrada.cget("fg_color").lower() == "#343638":
            contador += 1
    
    if contador == 6:
        nombre = nombre_entry.get()
        apellido = apellido_s_entry.get()
        mail = mail_entry.get()
        dni = DNI_entry.get()
        contraseña = password_entry.get()
        confirmar_contraseña = password_confirm_entry.get()
        fecha_registro = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        # Crear carpeta para el usuario
        carpeta_usuario = os.path.join('usuarios', f"{nombre}_{dni}")
        os.makedirs(carpeta_usuario, exist_ok=True)
        
        # Llamar a la función de abrir la cámara y tomar una foto
        abrir_camara()

        # Definir la ruta de la imagen
        ruta_imagen = os.path.join(carpeta_usuario, 'imagen.jpg')
        
        # Guardar la imagen en la carpeta
        if img_bytes:
            with open(ruta_imagen, 'wb') as img_file:
                img_file.write(img_bytes)
        else:
            messagebox.showwarning("Error", "No se capturó ninguna imagen.")
            return
        
        # Insertar datos en la base de datos
        base.datos_insertados(nombre, apellido, mail, dni, contraseña, confirmar_contraseña, fecha_registro, ruta_imagen)
        messagebox.showinfo('', 'Alumno cargado correctamente')
        
        start_frame.tkraise()
    else:
        messagebox.showwarning("Error de Validación", "No todos los campos son válidos.")


def inicioSesion():
    global nombre  # Hacer la variable nombre global
    dni = DNI_inicio_entry.get()
    nombre = base.buscar(dni)  # Buscar el nombre usando el DNI
    
    if nombre:
        messagebox.showinfo("Bienvenido", f"Bienvenido {nombre}")
        start_frame.tkraise()
        
        # Abrir la cámara y capturar la imagen
        abrir_camara()
        
        # Leer la imagen guardada en la carpeta del usuario
        carpeta_usuario = os.path.join('usuarios', f"{nombre}_{dni}")
        imagen_guardada_path = os.path.join(carpeta_usuario, 'imagen.jpg')
        
        # Verificar que la imagen guardada existe
        if os.path.exists(imagen_guardada_path):
            with open(imagen_guardada_path, 'rb') as file:
                img_bytes_guardada = file.read()
            
            # Comparar las imágenes
            if img_bytes and img_bytes_guardada:
                if comparar_imagenes(img_bytes_guardada, img_bytes):
                    messagebox.showinfo("Acceso concedido", "La identidad ha sido verificada")
                    base.mostrar_usuarios()
                else:
                    messagebox.showwarning("Acceso denegado", "No se pudo verificar la identidad")
            else:
                messagebox.showwarning("Error", "No se pudo capturar la imagen o la imagen guardada no está disponible.")
        else:
            messagebox.showwarning("Error", "La imagen guardada no está disponible.")
    
    else:
        messagebox.showwarning("Error", "DNI no encontrado. Verifique los datos e intente nuevamente.")




#-------------------------------------FUNCIONES DE REGISTRO Y INICIO DE SESION-------------------------------------
#------------------------------------------------boton inicial--------------------------------------------
def botonIniciar():
    limpiarRegistro()
    DNI_inicio_entry.delete(0, 'end')  # Borra el contenido actual del campo de entrada
    DNI_inicio_entry.configure(fg_color='#343638')  # Restablece el color del texto a gris
    DNI_inicio_entry.configure(placeholder_text='DNI - Profesor')
    button_frame.tkraise()
    show_frame(sign_in_frame)
###############################################################################FUNCIONES###############################################################################



# Cargar el clasificador en cascada para detección de rostros
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

# Verificar si el clasificador se cargó corre   ctamente
if face_cascade.empty():
    raise IOError("No se pudo cargar el clasificador en cascada.")


# ---------------------------------------------Crear un contenedor para centrar los frames---------------------------------------------
container = ctk.CTkFrame(root)
container.place(relx=0.5, rely=0.5, anchor=tk.CENTER)


#800 y 600
# ---------------------------------------------Frame principal para contener Sign In y Register---------------------------------------------
main_frame = ctk.CTkFrame(master=container, width=screen_width * 0.85 , height=screen_height * 0.8,fg_color=container.cget('fg_color'))
main_frame.pack(padx=20, pady=20)

#--------------------------------------------- Botones de alternancia en la parte superior---------------------------------------------
button_frame = ctk.CTkFrame(master=main_frame, width=int(round(850*scale_width)), height=int(round(50*scale_height)), corner_radius=0, fg_color='blue')
button_frame.place(relx=0.5, rely=0.05, anchor=tk.CENTER)

#---------------------------------------------BOTONES DE ARRIBA---------------------------------------------
#BOTON SIGN IN
sign_in_button = ctk.CTkButton(master=button_frame, text="Iniciar Sesion", width=screen_width * 0.44, height=screen_height * 0.1,font=('arial',20), corner_radius=0, command=lambda: show_frame(sign_in_frame))
sign_in_button.grid(row=0, column=0)

#BOTON REGISTER
register_button = ctk.CTkButton(master=button_frame, text="Registrarse", width=screen_width * 0.44, height=screen_height * 0.1,font=('arial',20), corner_radius=0, command=lambda: show_frame(register_frame),)
register_button.grid(row=0, column=1)
#---------------------------------------------BOTONES DE ARRIBA---------------------------------------------



#---------------------------------------------Frame para Sign In---------------------------------------------
sign_in_frame = ctk.CTkFrame(master=main_frame, width=screen_width * 0.85,height=screen_height * 0.75, corner_radius=0)
sign_in_frame.place(relx=0.5, rely=0.55, anchor=tk.CENTER)
# Botón para salir
exit_button = ctk.CTkButton(
    master=sign_in_frame, 
    text="Salir", 
    font=('Arial', 30), 
    width=screen_width * 0.090, 
    height=screen_height * 0.0450, 
    fg_color="red", 
    command=root.quit
)
exit_button.place(relx=0.765, rely=0.85, anchor=tk.SE)  # Ubicación en la parte inferior derecha
#---------------------------------------------Título de Sign In---------------------------------------------
sign_in_label = ctk.CTkLabel(master=sign_in_frame, text="Iniciar Sesion", font=("Arial", 30))
sign_in_label.place(relx=0.5, rely=0.48, anchor=tk.CENTER)


image_path = 'Icono_Usuario.png' 
pil_image = Image.open(image_path)

# Convertir la imagen de PIL a un objeto PhotoImage compatible con Tkinter
pil_image = pil_image.resize((int(round(300*scale_width)),int(round(300*scale_height))), Image.LANCZOS)

tk_image = ImageTk.PhotoImage(pil_image)


# Imagen de usuario (placeholder)
user_image = ctk.CTkLabel(master=sign_in_frame,text='', image=tk_image, width=int(round(100*scale_width)), height=int(round(100*scale_height)), corner_radius=50)
user_image.place(relx=0.5, rely=0.285, anchor=tk.CENTER)



# Campo de Username or Email
DNI_inicio_entry = ctk.CTkEntry(master=sign_in_frame, placeholder_text="DNI - Profesor", width=screen_width * 0.45, height=screen_height * 0.05)
DNI_inicio_entry.place(relx=0.5, rely=0.6, anchor=tk.CENTER)


# ---------------------------------------------FREAME SIGN IN---------------------------------------------
#BOTON SIGN IN
sign_in_button_main = ctk.CTkButton(master=sign_in_frame, text="Iniciar Sesion", width=screen_width * 0.45, height=screen_height * 0.07, font=("Arial", 30),command=lambda: inicioSesion())
sign_in_button_main.place(relx=0.5, rely=0.715, anchor=tk.CENTER)


# Frame para Sign In
register_frame = ctk.CTkFrame(master=main_frame, width=screen_width * 0.85,height=screen_height * 0.75, corner_radius=0)
register_frame.place(relx=0.5, rely=0.55, anchor=tk.CENTER)
# Botón para salir
exit_button = ctk.CTkButton(
    master=register_frame, 
    text="Salir", 
    font=('Arial', 30), 
    width=screen_width * 0.090, 
    height=screen_height * 0.0450, 
    fg_color="red", 
    command=root.quit
)
exit_button.place(relx=0.8650, rely=0.9370, anchor=tk.SE)  # Ubicación en la parte inferior derecha

#Nombre
nombre_entry = ctk.CTkEntry(master=register_frame, placeholder_text="Nombre/s",  width=screen_width * 0.45, height=screen_height * 0.05)
nombre_entry.place(relx=0.6, rely=0.2, anchor=tk.CENTER)

#Apellido
apellido_s_entry = ctk.CTkEntry(master=register_frame, placeholder_text="Apellido/s",  width=screen_width * 0.45, height=screen_height * 0.05)
apellido_s_entry.place(relx=0.6, rely=0.3, anchor=tk.CENTER)


# Campo de Username or Email
mail_entry = ctk.CTkEntry(master=register_frame, placeholder_text="e-mail", width=screen_width * 0.45, height=screen_height * 0.05)
mail_entry.place(relx=0.6, rely=0.4, anchor=tk.CENTER)

#DNI
DNI_entry = ctk.CTkEntry(master=register_frame, placeholder_text="DNI",  width=screen_width * 0.45, height=screen_height * 0.05)
DNI_entry.place(relx=0.6, rely=0.5, anchor=tk.CENTER)

# Campo de Password
password_entry = ctk.CTkEntry(master=register_frame, placeholder_text="Contraseña", show="*", width=screen_width * 0.45, height=screen_height * 0.05)
password_entry.place(relx=0.6, rely=0.6, anchor=tk.CENTER)

#Confirmar Contraseña
password_confirm_entry = ctk.CTkEntry(master=register_frame, placeholder_text="Confirmar Constraseña", show="*", width=screen_width * 0.45, height=screen_height * 0.05)
password_confirm_entry.place(relx=0.6, rely=0.7, anchor=tk.CENTER)

Entradas=[DNI_entry,nombre_entry,apellido_s_entry,mail_entry,password_confirm_entry,password_entry]
#-----------------------------------ENTRYS PARA EL REGISTER-----------------------------------
# --------------------------Botón de REGISTER---------------------------
register_button_main = ctk.CTkButton(master=register_frame, text="Registrarse", width=screen_width * 0.45, height=screen_height * 0.075, font=("Arial", 30),command=lambda: registro())
register_button_main.place(relx=0.6, rely=0.8, anchor=tk.CENTER)

user_image2 = ctk.CTkLabel(master=register_frame,text='', image=tk_image, width=int(round(50*scale_width)), height=int(round(50*scale_height)), corner_radius=50)
user_image2.place(relx=0.17, rely=0.50, anchor=tk.CENTER)


###############################################################################FRAME VISUALIZAR DATOS###############################################################################


def crear_frame_visualizar_datos(root):
    # Crear un frame para mostrar la base de datos
    frame_datos = tk.Frame(root)
    frame_datos.pack(fill=tk.BOTH, expand=True)

    # Conexión a la base de datos
    conn = sqlite3.connect('EBI.db')
    cur = conn.cursor()

    # Consulta para obtener todos los registros
    cur.execute("SELECT * FROM registrados")
    registros = cur.fetchall()

    # Crear tabla
    tabla = tk.Treeview(frame_datos, columns=('Nombre', 'Apellido', 'Email', 'DNI', 'Contraseña', 'Confirmar Contraseña', 'Fecha Registro'), show='headings')
    tabla.heading('Nombre', text='Nombre')
    tabla.heading('Apellido', text='Apellido')
    tabla.heading('Email', text='Email')
    tabla.heading('DNI', text='DNI')
    tabla.heading('Contraseña', text='Contraseña')
    tabla.heading('Confirmar Contraseña', text='Confirmar Contraseña')
    tabla.heading('Fecha Registro', text='Fecha Registro')

    # Insertar datos en la tabla
    for registro in registros:
        tabla.insert('', 'end', values=registro)

    tabla.pack(fill=tk.BOTH, expand=True)

    # Cerrar la conexión a la base de datos
    conn.close()

    # Crear botón "Salir"
    salir_button = tk.Button(frame_datos, text="Salir", command=root.quit)
    salir_button.place(relx=0.50, rely=0.40,anchor=tk.CENTER)

###############################################################################FRAME VISUALIZAR DATOS###############################################################################


###############################################################################INICIO FRAME-BOTON-TODOO###############################################################################

start_frame = ctk.CTkFrame(master=main_frame, width=screen_width * 0.85,height=screen_height * 0.8, corner_radius=0)
start_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)


image_path = 'Logo_e.b.i.png'  
pil_image = Image.open(image_path)

# Ajustar el tamaño de la imagen (opcional)
pil_image = pil_image.resize((int(round(300*scale_width)),int(round(300*scale_height))), Image.LANCZOS)

# Convertir la imagen de PIL a un objeto PhotoImage compatible con Tkinter
tk_image = ImageTk.PhotoImage(pil_image)


# Imagen de usuario (placeholder)
user_image = ctk.CTkLabel(master=start_frame,text='', image=tk_image, width=200, height=200, corner_radius=50)
user_image.place(relx=0.5, rely=0.25, anchor=tk.CENTER)

start_label = ctk.CTkLabel(master=start_frame, text="E.B.I.", font=("Arial", 40))
start_label.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

linea_label = ctk.CTkLabel(master=start_frame, text="______________________________", font=("Arial", 20))
linea_label.place(relx=0.5, rely=0.55, anchor=tk.CENTER)

slogan_label = ctk.CTkLabel(master=start_frame, text="Escaner Biometrico Inteligente", font=("Arial", 20))
slogan_label.place(relx=0.5, rely=0.62, anchor=tk.CENTER)

start_button_main = ctk.CTkButton(master=start_frame, text="Iniciar",font=('Arial',30), width=screen_width * 0.5, height=screen_height * 0.1,command=lambda: botonIniciar())
start_button_main.place(relx=0.5, rely=0.8, anchor=tk.CENTER)


# Mostrar el frame de Sign In al inicio
start_frame.tkraise()

# Botón para salir
exit_button = ctk.CTkButton(
    master=start_frame, 
    text="Salir", 
    font=('Arial', 30), 
    width=screen_width * 0.090, 
    height=screen_height * 0.0450, 
    fg_color="red", 
    command=root.quit
)
exit_button.place(relx=0.795, rely=0.95, anchor=tk.SE)  # Ubicación en la parte inferior derecha

root.mainloop()

###############################################################################INICIO FRAME-BOTON-TODOO###############################################################################




'''
botonCargarImagen = ctk.CTkButton(master=register_frame, text="Abrir camara",fg_color="#1A93A6", command = abrir_camara)
botonCargarImagen.place(relx=0.18,rely=0.75, anchor=tk.CENTER)
comentarios

        ## Guardar los valores globalmente para el archivo principal
        #global nombre, apellido, mail, dni, contraseña, confirmar_contraseña
        #nombre = nombre_entry.get()
        #apellido = apellido_s_entry.get()
        #mail = mail_entry.get()
        #dni = DNI_entry.get()
        #contraseña = password_entry.get()
        #confirmar_contraseña = password_confirm_entry.get()
        # 
        # # Funciones.insertar_persona(entradaDni.get(),entradaNombre.get(),entradaApellido.get(),entradaDomicilio.get(),entradaMail.get(),entradaTelefono.get(),entradaUsuario.get(),entradaContrasena.get(),img_bytes)
        # 

        # 
# image_path = 'Icono_Usuario.png'  
# pil_image = Image.open(image_path)

# # Ajustar el tamaño de la imagen (opcional)
# pil_image = pil_image.resize((int(round(300*scale_width)),int(round(300*scale_height))), Image.LANCZOS)

# # Convertir la imagen de PIL a un objeto PhotoImage compatible con Tkinter
# tk_image = ImageTk.PhotoImage(pil_image)


# # Imagen de usuario (placeholder)
# user_image = ctk.CTkLabel(master=register_frame,text='', image=tk_image, width=100, height=100, corner_radius=50)
# user_image.place(relx=0.18, rely=0.5, anchor=tk.CENTER)

        # 
        # 
        
        def load_image():
    global img_bytes
    file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.jpg *.jpeg")])
    if file_path:
        img = Image.open(file_path)
        img.thumbnail((int(round(288*scale_height)),int(round(288*scale_width))))
        img_tk = ImageTk.PhotoImage(img)
        image_label.configure(image=img_tk)
        image_label.image = img_tk

        # Convertir imagen a bytes
        with open(file_path, 'rb') as file:
            img_bytes = file.read()

        # # Campo de Password
# password_entry = ctk.CTkEntry(master=sign_in_frame, placeholder_text="Password", show="*", width=screen_width * 0.45, height=screen_height * 0.05)
# password_entry.place(relx=0.6, rely=0.5, anchor=tk.CENTER)
# password_label = ctk.CTkLabel(master=sign_in_frame, text="Password", font=("Arial", 15))
# password_label.place(relx=0.396, rely=0.45, anchor=tk.CENTER)
# 

# '''
'''
s# TITULO DE REGISTER
register_label = ctk.CTkLabel(master=register_frame, text=".", font=("Arial", 35))
register_label.place(relx=0.18, rely=0.23, anchor=tk.CENTER)'''

'''
image_frame = ctk.CTkFrame(master=register_frame, height=200,width=200,border_color='gray',border_width=2)
image_frame.place(relx=0.18,rely=0.5, anchor=tk.CENTER)

image_label = ctk.CTkLabel(master=image_frame, text="")
image_label.place(relx=0.02,rely=0.02)'''


'''User_label = ctk.CTkLabel(master=sign_in_frame, text="DNI - Profesor", font=("Arial", 15))
User_label.place(relx=0.282, rely=0.54, anchor=tk.CENTER)'''