#!/usr/bin/env python3
"""
Login window for Student Performance Monitoring System
"""

import tkinter as tk
from tkinter import ttk, messagebox
from database import db
import admin
import teacher
import student
import io
import random
import string
from PIL import Image, ImageTk
try:
    # Optional dependency; present in requirements.txt
    from captcha.image import ImageCaptcha
except Exception:
    ImageCaptcha = None
try:
    from tktooltip import ToolTip as Tooltip
except Exception:
    Tooltip = None

class LoginWindow:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Student Performance Monitoring System - Login")
        self.root.geometry("900x600")
        self.root.resizable(False, False)
        
        # Center the window
        self.center_window()
        
        # Configure grid weights
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_columnconfigure(1, weight=1)
        self.root.grid_rowconfigure(0, weight=1)
        
        # Create left panel (illustration)
        self.create_left_panel()
        
        # Create right panel (login form)
        self.create_right_panel()
        
        # Bind Enter key to login
        self.root.bind('<Return>', lambda e: self.login())
        
        # Focus on username entry
        self.username_entry.focus()
    
    def create_left_panel(self):
        """Create left panel with illustration"""
        left_frame = tk.Frame(self.root, bg="#f8f9fa")
        left_frame.grid(row=0, column=0, sticky="nsew", padx=0, pady=0)
        
        # Create illustration frame
        illustration_frame = tk.Frame(left_frame, bg="#f8f9fa")
        illustration_frame.pack(expand=True, fill="both", padx=40, pady=40)
        
        # Title for left panel
        title_label = tk.Label(illustration_frame, 
                              text="Student Performance\nMonitoring System",
                              font=("Arial", 24, "bold"),
                              fg="#2c3e50",
                              bg="#f8f9fa",
                              justify="center")
        title_label.pack(pady=(50, 30))
        
        # Subtitle
        subtitle_label = tk.Label(illustration_frame,
                                 text="Track, Analyze, and Improve\nAcademic Performance",
                                 font=("Arial", 14),
                                 fg="#7f8c8d",
                                 bg="#f8f9fa",
                                 justify="center")
        subtitle_label.pack(pady=(0, 50))
        
        # Create a simple illustration using shapes
        canvas = tk.Canvas(illustration_frame, width=300, height=200, 
                          bg="#f8f9fa", highlightthickness=0)
        canvas.pack(pady=20)
        
        # Draw a simple desk illustration
        # Desk
        canvas.create_rectangle(50, 120, 250, 140, fill="#8b4513", outline="")
        # Chair
        canvas.create_rectangle(60, 100, 90, 120, fill="#654321", outline="")
        canvas.create_rectangle(70, 80, 80, 100, fill="#654321", outline="")
        # Laptop
        canvas.create_rectangle(80, 90, 180, 110, fill="#2c3e50", outline="")
        canvas.create_rectangle(85, 95, 175, 105, fill="#ecf0f1", outline="")
        # Lamp
        canvas.create_oval(200, 70, 220, 90, fill="#f39c12", outline="")
        canvas.create_line(210, 90, 210, 120, fill="#95a5a6", width=3)
        # Plant
        canvas.create_oval(240, 100, 260, 120, fill="#27ae60", outline="")
        canvas.create_rectangle(245, 120, 255, 130, fill="#8b4513", outline="")
        
        # Features list
        features_frame = tk.Frame(illustration_frame, bg="#f8f9fa")
        features_frame.pack(pady=30)
        
        features = [
            "📊 Real-time Performance Tracking",
            "📈 Interactive Analytics & Charts", 
            "👥 Multi-role Access (Admin/Teacher/Student)",
            "🔒 Secure Authentication System"
        ]
        
        for feature in features:
            feature_label = tk.Label(features_frame,
                                   text=feature,
                                   font=("Arial", 12),
                                   fg="#34495e",
                                   bg="#f8f9fa",
                                   anchor="w")
            feature_label.pack(pady=5, anchor="w")
    
    def create_right_panel(self):
        """Create right panel with login form"""
        right_frame = tk.Frame(self.root, bg="white")
        right_frame.grid(row=0, column=1, sticky="nsew", padx=0, pady=0)
        
        # Main login container
        login_container = tk.Frame(right_frame, bg="white")
        login_container.pack(expand=True, fill="both", padx=60, pady=40)
        
        # Login title
        login_title = tk.Label(login_container,
                              text="Login",
                              font=("Arial", 28, "bold"),
                              fg="#2c3e50",
                              bg="white")
        login_title.pack(pady=(0, 40))
        
        # Username field
        username_frame = tk.Frame(login_container, bg="white")
        username_frame.pack(fill="x", pady=10)
        
        username_label = tk.Label(username_frame,
                                 text="username",
                                 font=("Arial", 12, "bold"),
                                 fg="#2c3e50",
                                 bg="white",
                                 anchor="w")
        username_label.pack(anchor="w", pady=(0, 5))
        
        # Username entry with icon
        username_entry_frame = tk.Frame(username_frame, bg="white", relief="solid", bd=1)
        username_entry_frame.pack(fill="x", pady=(0, 10))
        
        # User icon (simple text representation)
        user_icon = tk.Label(username_entry_frame,
                            text="👤",
                            font=("Arial", 14),
                            bg="white",
                            fg="#7f8c8d")
        user_icon.pack(side="left", padx=10)
        
        self.username_var = tk.StringVar()
        self.username_entry = tk.Entry(username_entry_frame,
                                      textvariable=self.username_var,
                                      font=("Arial", 12),
                                      relief="flat",
                                      bg="white",
                                      fg="#2c3e50",
                                      insertbackground="#2c3e50")
        self.username_entry.pack(side="left", fill="x", expand=True, padx=(0, 10), pady=10)
        
        # Password field
        password_frame = tk.Frame(login_container, bg="white")
        password_frame.pack(fill="x", pady=10)
        
        password_label = tk.Label(password_frame,
                                 text="Password",
                                 font=("Arial", 12, "bold"),
                                 fg="#2c3e50",
                                 bg="white",
                                 anchor="w")
        password_label.pack(anchor="w", pady=(0, 5))
        
        # Password entry with icon
        password_entry_frame = tk.Frame(password_frame, bg="white", relief="solid", bd=1)
        password_entry_frame.pack(fill="x", pady=(0, 10))
        
        # Lock icon
        lock_icon = tk.Label(password_entry_frame,
                            text="🔒",
                            font=("Arial", 14),
                            bg="white",
                            fg="#7f8c8d")
        lock_icon.pack(side="left", padx=10)
        
        self.password_var = tk.StringVar()
        self.password_entry = tk.Entry(password_entry_frame,
                                      textvariable=self.password_var,
                                      font=("Arial", 12),
                                      relief="flat",
                                      bg="white",
                                      fg="#2c3e50",
                                      show="•",
                                      insertbackground="#2c3e50")
        self.password_entry.pack(side="left", fill="x", expand=True, padx=(0, 10), pady=10)
        
        # Eye icon for password visibility
        self.show_password = tk.BooleanVar()
        eye_icon = tk.Label(password_entry_frame,
                           text="👁️",
                           font=("Arial", 12),
                           bg="white",
                           fg="#7f8c8d",
                           cursor="hand2")
        eye_icon.pack(side="right", padx=10)
        eye_icon.bind("<Button-1>", self.toggle_password_visibility)
        
        # CAPTCHA
        captcha_frame = tk.Frame(login_container, bg="white")
        captcha_frame.pack(fill="x", pady=10)
        captcha_label = tk.Label(captcha_frame, text="Captcha", font=("Arial", 12, "bold"), fg="#2c3e50", bg="white", anchor="w")
        captcha_label.pack(anchor="w", pady=(0,5))
        captcha_row = tk.Frame(captcha_frame, bg="white")
        captcha_row.pack(fill="x")
        
        self.captcha_var = tk.StringVar()
        self.captcha_entry = tk.Entry(captcha_row, textvariable=self.captcha_var, font=("Arial", 12), relief="solid", bd=1, width=22)
        self.captcha_entry.pack(side="left", padx=(0,10))
        
        self.captcha_image_label = tk.Label(captcha_row, bg="white")
        self.captcha_image_label.pack(side="left")
        self.captcha_image_label.bind("<Button-1>", lambda e: self.refresh_captcha())
        refresh_btn = tk.Button(captcha_row,
                                text="⟳",
                                command=self.refresh_captcha,
                                relief="raised",
                                bg="#ecf0f1",
                                fg="#2c3e50",
                                width=4,
                                height=2,
                                font=("Arial", 14, "bold"),
                                cursor="hand2",
                                bd=1)
        refresh_btn.pack(side="right", padx=10, pady=2)
        if Tooltip is not None:
            Tooltip(refresh_btn, "Refresh Captcha (Alt+R)")
        # Keyboard shortcut
        self.root.bind_all("<Alt-r>", lambda e: self.refresh_captcha())
        
        self.refresh_captcha()
        
        # Forgot password link
        forgot_frame = tk.Frame(login_container, bg="white")
        forgot_frame.pack(fill="x", pady=5)
        
        forgot_link = tk.Label(forgot_frame,
                              text="Forgot Password?",
                              font=("Arial", 11),
                              fg="#3498db",
                              bg="white",
                              cursor="hand2")
        forgot_link.pack(anchor="e")
        try:
            import forgot_password  # local module; loaded on demand
            forgot_link.bind("<Button-1>", lambda e: forgot_password.ForgotPasswordWindow(self.root))
        except Exception:
            forgot_link.bind("<Button-1>", lambda e: messagebox.showinfo("Info", "Contact your administrator to reset your password."))
        
        # Rounded Login button (full width)
        self.create_rounded_button(login_container, text="Login", command=self.login)
        
        # Demo credentials
        demo_frame = tk.Frame(login_container, bg="white")
        demo_frame.pack(fill="x", pady=20)
        
        demo_title = tk.Label(demo_frame,
                             text="Demo Credentials",
                             font=("Arial", 12, "bold"),
                             fg="#2c3e50",
                             bg="white")
        demo_title.pack(pady=(0, 10))
        
        demo_credentials = [
            "👨‍💼 Admin: admin / admin123",
            "👩‍🏫 Teacher: teacher1 / teacher123", 
            "👨‍🎓 Student: student1 / student123"
        ]
        
        for credential in demo_credentials:
            cred_label = tk.Label(demo_frame,
                                 text=credential,
                                 font=("Arial", 10),
                                 fg="#7f8c8d",
                                 bg="white",
                                 anchor="w")
            cred_label.pack(anchor="w", pady=2)
        
        # Get started link
        get_started_frame = tk.Frame(login_container, bg="white")
        get_started_frame.pack(fill="x", pady=20)
        
        get_started_text = tk.Label(get_started_frame,
                                   text="Don't have an account? ",
                                   font=("Arial", 11),
                                   fg="#7f8c8d",
                                   bg="white")
        get_started_text.pack(side="left")
        
        get_started_link = tk.Label(get_started_frame,
                                   text="Get Started For Free",
                                   font=("Arial", 11, "bold"),
                                   fg="#3498db",
                                   bg="white",
                                   cursor="hand2")
        get_started_link.pack(side="left")
        get_started_link.bind("<Button-1>", lambda e: messagebox.showinfo("Info", "Contact your administrator to create a new account."))
    
    def create_rounded_button(self, parent, text, command):
        """Create a full-width rounded gold button similar to the screenshot."""
        button_height = 72
        radius = 30
        bg_color = "#c88f05"  # gold-like
        bg_hover = "#d9a31a"
        text_color = "#111111"
        
        canvas = tk.Canvas(parent, height=button_height, bg="white", highlightthickness=0)
        canvas.pack(fill="x", pady=5, side="bottom")
        
        def draw(width):
            canvas.delete("all")
            pad = 80
            x1, y1 = pad, 8
            x2, y2 = width - pad, button_height - 8
            r = radius
            # rounded rectangle using polygons + arcs
            canvas.create_arc(x1, y1, x1+2*r, y1+2*r, start=90, extent=180, fill=bg_color, outline=bg_color)
            canvas.create_arc(x2-2*r, y1, x2, y1+2*r, start=270, extent=180, fill=bg_color, outline=bg_color)
            canvas.create_rectangle(x1+r, y1, x2-r, y2, fill=bg_color, outline=bg_color)
            canvas.create_rectangle(x1, y1+r, x2, y2-r, fill=bg_color, outline=bg_color)
            canvas.create_text((width)//2, button_height//2, text=text, font=("Arial", 20, "bold"), fill=text_color)
        
        # Force initial draw after Canvas is realized
        canvas.after(50, lambda: draw(canvas.winfo_width()))
        
        def on_resize(event):
            draw(event.width)
        
        def on_click(_):
            if callable(command):
                command()
        
        def on_enter(_):
            nonlocal bg_color
            old = bg_color
            bg_color = bg_hover
            draw(canvas.winfo_width())
            bg_color = old
        
        def on_leave(_):
            draw(canvas.winfo_width())
        
        canvas.bind("<Configure>", on_resize)
        canvas.bind("<Button-1>", on_click)
        canvas.bind("<Enter>", on_enter)
        canvas.bind("<Leave>", on_leave)
    
    def _generate_captcha_text(self, length=5):
        alphabet = string.ascii_uppercase + string.digits
        return ''.join(random.choice(alphabet) for _ in range(length))
    
    def refresh_captcha(self):
        """Generate and display a new captcha image"""
        self.captcha_answer = self._generate_captcha_text()
        if ImageCaptcha is not None:
            generator = ImageCaptcha(width=160, height=60)
            image = generator.generate_image(self.captcha_answer)
        else:
            # Fallback: render plain text with Pillow
            image = Image.new('RGB', (160, 60), color=(255, 255, 255))
            from PIL import ImageDraw
            draw = ImageDraw.Draw(image)
            draw.text((10, 15), self.captcha_answer, fill=(0, 0, 0))
        buffer = io.BytesIO()
        image.save(buffer, format='PNG')
        buffer.seek(0)
        pil_img = Image.open(buffer)
        # Bind the image to this window's Tk instance and keep strong references
        self._tk_captcha = ImageTk.PhotoImage(pil_img, master=self.root)
        try:
            self.captcha_image_label.configure(image=self._tk_captcha)
            # Prevent garbage collection by storing on the label as well
            self.captcha_image_label.image = self._tk_captcha
        except tk.TclError:
            # Window might be closing; safely ignore
            return
        self.captcha_var.set("")
    
    def toggle_password_visibility(self, event):
        """Toggle password visibility"""
        if self.password_entry.cget('show') == '•':
            self.password_entry.config(show='')
        else:
            self.password_entry.config(show='•')
    
    def center_window(self):
        """Center the window on screen"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
    
    def login(self):
        """Handle login authentication"""
        username = self.username_var.get().strip()
        password = self.password_var.get().strip()
        captcha_input = self.captcha_var.get().strip().upper()
        
        if not username or not password:
            messagebox.showerror("Error", "Please enter both username and password")
            return
        
        if not captcha_input:
            messagebox.showerror("Error", "Please enter the captcha")
            return
        if captcha_input != getattr(self, 'captcha_answer', ''):
            messagebox.showerror("Error", "Incorrect captcha. Please try again.")
            self.refresh_captcha()
            return
        
        # Authenticate user
        user = db.verify_login(username, password)
        
        if user:
            self.root.withdraw()  # Hide login window
            try:
                # Open appropriate dashboard based on role
                if user['role'] == 'admin':
                    admin.AdminDashboard(user).run()
                elif user['role'] == 'teacher':
                    teacher_profile = db.get_teacher_by_user_id(user['user_id'])
                    if teacher_profile:
                        teacher.TeacherDashboard(user, teacher_profile)
                    else:
                        messagebox.showerror("Error", "Teacher profile not found")
                        self.root.deiconify()
                elif user['role'] == 'student':
                    student_profile = db.get_student_by_user_id(user['user_id'])
                    if student_profile:
                        student.StudentDashboard(user, student_profile)
                    else:
                        messagebox.showerror("Error", "Student profile not found")
                        self.root.deiconify()
            except Exception as e:
                # Surface dashboard errors gracefully and return to login
                messagebox.showerror("Dashboard Error", f"Failed to open dashboard:\n{e}")
                self.root.deiconify()
        else:
            messagebox.showerror("Error", "Invalid username or password")
            self.password_var.set("")
            self.password_entry.focus()
            self.refresh_captcha()
    
    def run(self):
        """Start the login window"""
        self.root.mainloop()

if __name__ == "__main__":
    login_window = LoginWindow()
    login_window.run()
