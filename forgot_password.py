import tkinter as tk
from tkinter import messagebox

class ForgotPasswordWindow:
    def __init__(self, parent):
        self.top = tk.Toplevel(parent)
        self.top.title("Forgot Password")
        self.top.geometry("400x220")
        self.top.resizable(False, False)
        label = tk.Label(self.top, text="Forgot Password", font=("Arial", 16, "bold"))
        label.pack(pady=20)
        info = tk.Label(self.top, text="Please contact your administrator to reset your password.", font=("Arial", 12), wraplength=350)
        info.pack(pady=10)
        close_btn = tk.Button(self.top, text="Close", command=self.top.destroy)
        close_btn.pack(pady=20)
