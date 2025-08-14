# py -m pip install customtkinter
# py -m pip install pillow
# py -m pip install opencv-python
# py -m pip install numpy
# py -m pip install scikit-image
# py -m pip install imageio
# py -m pip install matplotlib

import customtkinter as ctk
import tkinter as tk
from PIL import Image, ImageTk
from tkinter import simpledialog, messagebox
import os
import cv2
import numpy as np
import sqlite3
from datetime import datetime
from skimage.metrics import structural_similarity as ssim
import Programacion.base as base

# ================================================ MAIN APPLICATION CLASS ================================================
class FacialRecognitionApp:
    def __init__(self):
        self.root = ctk.CTk()
        self.setup_window()
        self.initialize_variables()
        self.create_widgets()
        self.root.mainloop()
    
    def setup_window(self):
        """Configure the main application window"""
        ctk.set_appearance_mode("dark")
        self.root.title("Sistema de Reconocimiento Facial - EBI")
        self.root.overrideredirect(True)  # Hide title bar
        
        # Get screen dimensions
        self.screen_width = self.root.winfo_screenwidth()
        self.screen_height = self.root.winfo_screenheight()
        
        # Set window size to full screen
        self.root.geometry(f"{self.screen_width}x{self.screen_height}+0+0")
        
        # Calculate scale factors
        self.scale_width = self.screen_width / 1280
        self.scale_height = self.screen_height / 720
        
        # Load face cascade
        self.face_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        )
        if self.face_cascade.empty():
            raise RuntimeError("Error loading face detection model")
    
    def initialize_variables(self):
        """Initialize application variables"""
        self.img_bytes = None
        self.current_user = None
        self.cap = None
        self.user_image_cache = {}
        
        # Create users directory if not exists
        os.makedirs('usuarios', exist_ok=True)
        
        # Initialize database
        base.initialize_database()
    
    def create_widgets(self):
        """Create all GUI components"""
        self.create_container()
        self.create_main_frame()
        self.create_start_frame()
        self.create_sign_in_frame()
        self.create_register_frame()
        self.create_dashboard_frame()
        self.start_frame.tkraise()
    
    # ================================================ UI COMPONENTS ================================================
    def create_container(self):
        """Create main container"""
        self.container = ctk.CTkFrame(self.root)
        self.container.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
    
    def create_main_frame(self):
        """Create main application frame"""
        self.main_frame = ctk.CTkFrame(
            master=self.container, 
            width=self.screen_width * 0.85, 
            height=self.screen_height * 0.8,
            fg_color=self.container.cget('fg_color')
        )
        self.main_frame.pack(padx=20, pady=20)
    
    def create_start_frame(self):
        """Create welcome screen"""
        self.start_frame = ctk.CTkFrame(
            master=self.main_frame, 
            width=self.screen_width * 0.85,
            height=self.screen_height * 0.8
        )
        self.start_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
        
        # Load and display logo
        logo_img = self.load_and_resize_image('Logo_e.b.i.png', 300, 300)
        logo_label = ctk.CTkLabel(
            master=self.start_frame, 
            text='', 
            image=logo_img, 
            width=200, 
            height=200
        )
        logo_label.place(relx=0.5, rely=0.25, anchor=tk.CENTER)
        
        # Application title
        title_label = ctk.CTkLabel(
            master=self.start_frame, 
            text="E.B.I.", 
            font=("Arial", 40)
        )
        title_label.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
        
        # Separator line
        separator = ctk.CTkLabel(
            master=self.start_frame, 
            text="______________________________", 
            font=("Arial", 20)
        )
        separator.place(relx=0.5, rely=0.55, anchor=tk.CENTER)
        
        # Slogan
        slogan = ctk.CTkLabel(
            master=self.start_frame, 
            text="Escaner Biométrico Inteligente", 
            font=("Arial", 20)
        )
        slogan.place(relx=0.5, rely=0.62, anchor=tk.CENTER)
        
        # Start button
        start_btn = ctk.CTkButton(
            master=self.start_frame, 
            text="Iniciar",
            font=('Arial', 30), 
            width=self.screen_width * 0.5, 
            height=self.screen_height * 0.1,
            command=self.show_login
        )
        start_btn.place(relx=0.5, rely=0.8, anchor=tk.CENTER)
        
        # Exit button
        exit_btn = ctk.CTkButton(
            master=self.start_frame, 
            text="Salir", 
            font=('Arial', 30), 
            width=self.screen_width * 0.09, 
            height=self.screen_height * 0.045, 
            fg_color="red", 
            command=self.root.quit
        )
        exit_btn.place(relx=0.795, rely=0.95, anchor=tk.SE)
    
    def create_sign_in_frame(self):
        """Create login frame"""
        self.sign_in_frame = ctk.CTkFrame(
            master=self.main_frame, 
            width=self.screen_width * 0.85,
            height=self.screen_height * 0.75
        )
        self.sign_in_frame.place(relx=0.5, rely=0.55, anchor=tk.CENTER)
        
        # Title
        title = ctk.CTkLabel(
            master=self.sign_in_frame, 
            text="Iniciar Sesión", 
            font=("Arial", 30)
        )
        title.place(relx=0.5, rely=0.48, anchor=tk.CENTER)
        
        # User icon
        user_icon = self.load_and_resize_image('Icono_Usuario.png', 300, 300)
        user_img = ctk.CTkLabel(
            master=self.sign_in_frame,
            text='', 
            image=user_icon, 
            width=int(round(100 * self.scale_width)), 
            height=int(round(100 * self.scale_height))
        )
        user_img.place(relx=0.5, rely=0.285, anchor=tk.CENTER)
        
        # DNI input
        self.DNI_inicio_entry = ctk.CTkEntry(
            master=self.sign_in_frame, 
            placeholder_text="DNI - Profesor", 
            width=self.screen_width * 0.45, 
            height=self.screen_height * 0.05
        )
        self.DNI_inicio_entry.place(relx=0.5, rely=0.6, anchor=tk.CENTER)
        
        # Login button
        login_btn = ctk.CTkButton(
            master=self.sign_in_frame, 
            text="Iniciar Sesión", 
            width=self.screen_width * 0.45, 
            height=self.screen_height * 0.07, 
            font=("Arial", 30),
            command=self.login
        )
        login_btn.place(relx=0.5, rely=0.715, anchor=tk.CENTER)
        
        # Back button
        back_btn = ctk.CTkButton(
            master=self.sign_in_frame, 
            text="Volver", 
            width=self.screen_width * 0.1, 
            height=self.screen_height * 0.05,
            command=self.show_start
        )
        back_btn.place(relx=0.1, rely=0.9, anchor=tk.CENTER)
        
        # Exit button
        exit_btn = ctk.CTkButton(
            master=self.sign_in_frame, 
            text="Salir", 
            font=('Arial', 30), 
            width=self.screen_width * 0.09, 
            height=self.screen_height * 0.045, 
            fg_color="red", 
            command=self.root.quit
        )
        exit_btn.place(relx=0.765, rely=0.85, anchor=tk.SE)
    
    def create_register_frame(self):
        """Create registration frame"""
        self.register_frame = ctk.CTkFrame(
            master=self.main_frame, 
            width=self.screen_width * 0.85,
            height=self.screen_height * 0.75
        )
        self.register_frame.place(relx=0.5, rely=0.55, anchor=tk.CENTER)
        
        # User icon
        user_icon = self.load_and_resize_image('Icono_Usuario.png', 300, 300)
        user_img = ctk.CTkLabel(
            master=self.register_frame,
            text='', 
            image=user_icon, 
            width=int(round(50 * self.scale_width)), 
            height=int(round(50 * self.scale_height))
        )
        user_img.place(relx=0.17, rely=0.50, anchor=tk.CENTER)
        
        # Form fields
        fields = [
            ("Nombre/s", 0.6, 0.2, "nombre_entry"),
            ("Apellido/s", 0.6, 0.3, "apellido_entry"),
            ("e-mail", 0.6, 0.4, "email_entry"),
            ("DNI", 0.6, 0.5, "dni_entry"),
            ("Contraseña", 0.6, 0.6, "password_entry"),
            ("Confirmar Contraseña", 0.6, 0.7, "confirm_password_entry")
        ]
        
        self.entries = {}
        for text, relx, rely, name in fields:
            entry = ctk.CTkEntry(
                master=self.register_frame, 
                placeholder_text=text,
                width=self.screen_width * 0.45, 
                height=self.screen_height * 0.05
            )
            entry.place(relx=relx, rely=rely, anchor=tk.CENTER)
            self.entries[name] = entry
            
            # Set validation based on field type
            if name == "dni_entry":
                entry.configure(validate="key", validatecommand=(self.root.register(self.validate_dni), '%P'))
            elif name == "nombre_entry" or name == "apellido_entry":
                entry.configure(validate="key", validatecommand=(self.root.register(self.validate_name), '%P', name))
            elif name == "email_entry":
                entry.configure(validate="key", validatecommand=(self.root.register(self.validate_email), '%P'))
            elif "password" in name:
                entry.configure(show="*")
                if name == "password_entry":
                    entry.configure(validate="key", validatecommand=(self.root.register(self.validate_password), '%P'))
                else:
                    entry.configure(validate="key", validatecommand=(self.root.register(self.validate_confirm_password), '%P', self.entries["password_entry"].get()))
        
        # Camera button
        camera_btn = ctk.CTkButton(
            master=self.register_frame, 
            text="Tomar Foto", 
            width=self.screen_width * 0.2, 
            height=self.screen_height * 0.05,
            command=self.capture_face_image
        )
        camera_btn.place(relx=0.18, rely=0.65, anchor=tk.CENTER)
        
        # Register button
        register_btn = ctk.CTkButton(
            master=self.register_frame, 
            text="Registrarse", 
            width=self.screen_width * 0.45, 
            height=self.screen_height * 0.075, 
            font=("Arial", 30),
            command=self.register_user
        )
        register_btn.place(relx=0.6, rely=0.8, anchor=tk.CENTER)
        
        # Back button
        back_btn = ctk.CTkButton(
            master=self.register_frame, 
            text="Volver", 
            width=self.screen_width * 0.1, 
            height=self.screen_height * 0.05,
            command=self.show_login
        )
        back_btn.place(relx=0.1, rely=0.9, anchor=tk.CENTER)
        
        # Exit button
        exit_btn = ctk.CTkButton(
            master=self.register_frame, 
            text="Salir", 
            font=('Arial', 30), 
            width=self.screen_width * 0.09, 
            height=self.screen_height * 0.045, 
            fg_color="red", 
            command=self.root.quit
        )
        exit_btn.place(relx=0.8650, rely=0.9370, anchor=tk.SE)
    
    def create_dashboard_frame(self):
        """Create user dashboard frame"""
        self.dashboard_frame = ctk.CTkFrame(
            master=self.main_frame, 
            width=self.screen_width * 0.85,
            height=self.screen_height * 0.75
        )
        self.dashboard_frame.place(relx=0.5, rely=0.55, anchor=tk.CENTER)
        
        # Welcome message
        self.welcome_label = ctk.CTkLabel(
            master=self.dashboard_frame, 
            text="", 
            font=("Arial", 30)
        )
        self.welcome_label.place(relx=0.5, rely=0.1, anchor=tk.CENTER)
        
        # User actions
        actions = [
            ("Ver Registros", self.show_records),
            ("Tomar Asistencia", self.take_attendance),
            ("Ver Reportes", self.show_reports),
            ("Administrar Usuarios", self.manage_users),
            ("Cerrar Sesión", self.logout)
        ]
        
        for i, (text, command) in enumerate(actions):
            btn = ctk.CTkButton(
                master=self.dashboard_frame,
                text=text,
                width=self.screen_width * 0.3,
                height=self.screen_height * 0.1,
                font=("Arial", 20),
                command=command
            )
            btn.place(relx=0.3 + (i % 2) * 0.4, rely=0.3 + (i // 2) * 0.2, anchor=tk.CENTER)
    
    # ================================================ UTILITY METHODS ================================================
    def load_and_resize_image(self, path, width, height):
        """Load and resize an image with caching"""
        if path in self.user_image_cache:
            return self.user_image_cache[path]
        
        try:
            img = Image.open(path)
            img = img.resize(
                (int(round(width * self.scale_width)), 
                 int(round(height * self.scale_height))), 
                Image.LANCZOS
            )
            tk_img = ImageTk.PhotoImage(img)
            self.user_image_cache[path] = tk_img
            return tk_img
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo cargar la imagen: {str(e)}")
            return None
    
    # ================================================ VALIDATION METHODS ================================================
    def validate_dni(self, value):
        """Validate DNI input"""
        if value.isdigit() and len(value) == 8:
            self.entries["dni_entry"].configure(fg_color='#343638', text_color='#909298') 
            return True
        self.entries["dni_entry"].configure(fg_color="#b74241", text_color='black')
        return True
    
    def validate_name(self, value, field_name):
        """Validate name input"""
        if value.replace(" ", "").isalpha():
            self.entries[field_name].configure(fg_color='#343638', text_color='#909298') 
            return True
        self.entries[field_name].configure(fg_color="#b74241", text_color='black') 
        return True
    
    def validate_email(self, value):
        """Validate email input"""
        if "@" in value and "." in value and len(value) > 5:
            self.entries["email_entry"].configure(fg_color='#343638', text_color='#909298') 
            return True
        self.entries["email_entry"].configure(fg_color="#b74241", text_color='black') 
        return True
    
    def validate_password(self, value):
        """Validate password input"""
        if len(value) >= 6:
            self.entries["password_entry"].configure(fg_color='#343638', text_color='#909298') 
            return True
        self.entries["password_entry"].configure(fg_color="#b74241", text_color='black') 
        return True
    
    def validate_confirm_password(self, value, password):
        """Validate password confirmation"""
        if value == password and value != "":
            self.entries["confirm_password_entry"].configure(fg_color='#343638', text_color='#909298') 
            return True
        self.entries["confirm_password_entry"].configure(fg_color="#b74241", text_color='black') 
        return True
    
    def is_form_valid(self):
        """Check if all form fields are valid"""
        return all(entry.cget("fg_color") == "#343638" for entry in self.entries.values())
    
    # ================================================ NAVIGATION METHODS ================================================
    def show_frame(self, frame):
        """Show the specified frame"""
        frame.tkraise()
    
    def show_start(self):
        """Show start screen"""
        self.show_frame(self.start_frame)
    
    def show_login(self):
        """Show login screen"""
        self.clear_form()
        self.show_frame(self.sign_in_frame)
    
    def show_register(self):
        """Show registration screen"""
        password = simpledialog.askstring(
            "Acceso Administrativo", 
            "Ingrese contraseña de administrador:", 
            show='*',
            parent=self.root
        )
        
        if password is None:
            return  # User canceled
        
        if password != 'admin':
            messagebox.showwarning("Error", "Contraseña incorrecta")
            return
        
        self.clear_form()
        self.show_frame(self.register_frame)
    
    def show_dashboard(self):
        """Show user dashboard"""
        if self.current_user:
            self.welcome_label.configure(text=f"Bienvenido, {self.current_user}")
            self.show_frame(self.dashboard_frame)
    
    # ================================================ CORE FUNCTIONALITY ================================================
    def clear_form(self):
        """Clear all form fields"""
        for entry in self.entries.values():
            entry.delete(0, 'end')
            entry.configure(fg_color='#343638')
    
    def capture_face_image(self):
        """Capture face image using camera"""
        self.cap = cv2.VideoCapture(0)
        
        if not self.cap.isOpened():
            messagebox.showerror("Error", "No se puede acceder a la cámara")
            return
        
        self.img_bytes = None
        
        while self.cap.isOpened():
            ret, frame = self.cap.read()
            if not ret:
                break
            
            # Convert to grayscale for face detection
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = self.face_cascade.detectMultiScale(
                gray, 
                scaleFactor=1.1, 
                minNeighbors=5, 
                minSize=(30, 30)
            )
            
            # Draw rectangles around detected faces
            for (x, y, w, h) in faces:
                cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
                face_img = frame[y:y+h, x:x+w]
                
                # Convert face image to bytes
                _, buffer = cv2.imencode('.jpg', face_img)
                self.img_bytes = buffer.tobytes()
            
            cv2.imshow('Captura de Rostro - Presione "q" para capturar', frame)
            
            # Press 'q' to capture and exit
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        
        self.cap.release()
        cv2.destroyAllWindows()
        
        if self.img_bytes:
            messagebox.showinfo("Éxito", "Rostro capturado correctamente")
        else:
            messagebox.showwarning("Advertencia", "No se detectó ningún rostro")
    
    def compare_faces(self, img1_bytes, img2_bytes):
        """Compare two face images using SSIM and LBPH"""
        # Convert bytes to images
        img1 = cv2.imdecode(np.frombuffer(img1_bytes, np.uint8), cv2.IMREAD_COLOR)
        img2 = cv2.imdecode(np.frombuffer(img2_bytes, np.uint8), cv2.IMREAD_COLOR)
        
        if img1 is None or img2 is None:
            return False
        
        # Resize images to same dimensions
        img1 = cv2.resize(img1, (100, 100))
        img2 = cv2.resize(img2, (100, 100))
        
        # Convert to grayscale
        gray1 = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY)
        gray2 = cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY)
        
        # Calculate SSIM
        ssim_score, _ = ssim(gray1, gray2, full=True)
        
        # LBPH face recognizer
        recognizer = cv2.face.LBPHFaceRecognizer_create()
        recognizer.train([gray1], np.array([0]))
        _, confidence = recognizer.predict(gray2)
        
        # Combined threshold (adjust as needed)
        return ssim_score > 0.5 and confidence < 60
    
    def register_user(self):
        """Register a new user"""
        if not self.is_form_valid():
            messagebox.showwarning("Error", "Por favor complete todos los campos correctamente")
            return
        
        if not self.img_bytes:
            messagebox.showwarning("Error", "Debe capturar una imagen de rostro")
            return
        
        # Get form data
        data = {name: entry.get() for name, entry in self.entries.items()}
        
        # Create user directory
        user_dir = os.path.join('usuarios', f"{data['nombre_entry']}_{data['dni_entry']}")
        os.makedirs(user_dir, exist_ok=True)
        
        # Save face image
        img_path = os.path.join(user_dir, 'imagen.jpg')
        with open(img_path, 'wb') as f:
            f.write(self.img_bytes)
        
        # Save to database
        registration_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        base.insert_user(
            data['nombre_entry'], 
            data['apellido_entry'], 
            data['email_entry'], 
            data['dni_entry'], 
            data['password_entry'],
            registration_date,
            img_path
        )
        
        messagebox.showinfo("Éxito", "Usuario registrado correctamente")
        self.clear_form()
        self.show_login()
    
    def login(self):
        """Authenticate user"""
        dni = self.DNI_inicio_entry.get()
        if not dni.isdigit() or len(dni) != 8:
            messagebox.showwarning("Error", "DNI inválido")
            return
        
        user = base.get_user_by_dni(dni)
        if not user:
            messagebox.showwarning("Error", "Usuario no encontrado")
            return
        
        # Capture face for authentication
        self.capture_face_image()
        if not self.img_bytes:
            return
        
        # Load registered face image
        try:
            with open(user['face_image_path'], 'rb') as f:
                registered_img = f.read()
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo cargar la imagen registrada: {str(e)}")
            return
        
        # Compare faces
        if self.compare_faces(registered_img, self.img_bytes):
            self.current_user = user['nombre']
            messagebox.showinfo("Éxito", f"Bienvenido {self.current_user}")
            self.show_dashboard()
        else:
            messagebox.showwarning("Error", "Autenticación fallida: Rostro no coincide")
    
    def show_records(self):
        """Show user records"""
        conn = sqlite3.connect('EBI.db')
        cursor = conn.cursor()
        
        try:
            cursor.execute("SELECT * FROM registrados")
            records = cursor.fetchall()
            
            # Create a new window to display records
            records_window = ctk.CTkToplevel(self.root)
            records_window.title("Registros de Usuarios")
            records_window.geometry("900x500")
            
            # Create treeview
            columns = ("ID", "Nombre", "Apellido", "Email", "DNI", "Fecha Registro")
            tree = tk.ttk.Treeview(records_window, columns=columns, show="headings")
            
            # Configure columns
            for col in columns:
                tree.heading(col, text=col)
                tree.column(col, width=150)
            
            # Add data
            for record in records:
                tree.insert("", "end", values=record[:6])  # Exclude password and image path
            
            # Add scrollbar
            scrollbar = tk.Scrollbar(records_window, orient="vertical", command=tree.yview)
            tree.configure(yscrollcommand=scrollbar.set)
            
            # Layout
            tree.pack(side="left", fill="both", expand=True)
            scrollbar.pack(side="right", fill="y")
            
        except sqlite3.Error as e:
            messagebox.showerror("Error de Base de Datos", str(e))
        finally:
            conn.close()
    
    def take_attendance(self):
        """Take attendance using facial recognition"""
        # Implement your attendance logic here
        messagebox.showinfo("Asistencia", "Funcionalidad de toma de asistencia en desarrollo")
    
    def show_reports(self):
        """Show attendance reports"""
        # Implement your reporting logic here
        messagebox.showinfo("Reportes", "Funcionalidad de reportes en desarrollo")
    
    def manage_users(self):
        """Manage users (admin only)"""
        password = simpledialog.askstring(
            "Acceso Administrativo", 
            "Ingrese contraseña de administrador:", 
            show='*',
            parent=self.root
        )
        
        if password != 'admin':
            messagebox.showwarning("Error", "Acceso denegado")
            return
        
        # Implement user management functionality
        messagebox.showinfo("Administración", "Funcionalidad de administración de usuarios en desarrollo")
    
    def logout(self):
        """Logout current user"""
        self.current_user = None
        self.DNI_inicio_entry.delete(0, tk.END)
        self.show_login()

# ================================================ RUN APPLICATION ================================================
if __name__ == "__main__":
    app = FacialRecognitionApp()
    # End of file   