#!/usr/bin/env python3
"""
Admin Dashboard for Student Performance Monitoring System
"""

import tkinter as tk
from tkinter import ttk, messagebox
from database import db
import datetime
import sys
import os
import subprocess

class AdminDashboard:
    def __init__(self, user):
        self.user = user
        self.root = tk.Tk()
        self.root.title("Admin Dashboard - Student Performance Monitoring System")
        self.root.geometry("1400x800")
        self.root.state('zoomed')  # Maximize window
        
        # Configure grid weights
        self.root.grid_columnconfigure(1, weight=1)
        self.root.grid_rowconfigure(0, weight=1)
        
        # Create sidebar
        self.create_sidebar()
        
        # Create main content area
        self.create_main_content()
        
        # Load initial data
        self.load_dashboard_data()
        self.load_students()
        self.load_teachers()
        
        # Handle window close
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def create_sidebar(self):
        """Create left sidebar with navigation"""
        sidebar = tk.Frame(self.root, bg="white", width=250)
        sidebar.grid(row=0, column=0, sticky="nsew", padx=0, pady=0)
        sidebar.grid_propagate(False)
        
        # Time and date
        time_frame = tk.Frame(sidebar, bg="white")
        time_frame.pack(fill="x", padx=20, pady=20)
        
        current_time = datetime.datetime.now().strftime("%H:%M:%S")
        current_date = datetime.datetime.now().strftime("%Y/%m/%d")
        
        time_label = tk.Label(time_frame, text=f"🕐 {current_time}", 
                             font=("Arial", 12, "bold"), fg="#2c3e50", bg="white")
        time_label.pack(anchor="w")
        
        date_label = tk.Label(time_frame, text=current_date, 
                             font=("Arial", 10), fg="#7f8c8d", bg="white")
        date_label.pack(anchor="w", pady=(5, 0))
        
        # Profile section
        profile_frame = tk.Frame(sidebar, bg="white")
        profile_frame.pack(fill="x", padx=20, pady=20)
        
        # Profile picture (simple circle)
        profile_canvas = tk.Canvas(profile_frame, width=60, height=60, bg="white", highlightthickness=0)
        profile_canvas.pack(pady=10)
        profile_canvas.create_oval(5, 5, 55, 55, fill="#3498db", outline="")
        profile_canvas.create_text(30, 30, text="👨‍💼", font=("Arial", 20), fill="white")
        
        # Admin name
        admin_name = tk.Label(profile_frame, text="System Administrator", 
                             font=("Arial", 12, "bold"), fg="#2c3e50", bg="white")
        admin_name.pack()
        
        # Navigation menu
        nav_frame = tk.Frame(sidebar, bg="white")
        nav_frame.pack(fill="x", padx=20, pady=20)
        
        # Menu items
        menu_items = [
            ("📊 Dashboard", self.show_dashboard),
            ("👥 Manage Students", self.show_students),
            ("👨‍🏫 Manage Teachers", self.show_teachers),
            ("🤖 Predictions", self.show_predictions),
            ("⚙️ Settings", self.show_settings),
            ("🚪 Exit", self.logout)
        ]
        
        self.menu_buttons = {}
        for text, command in menu_items:
            btn = tk.Button(nav_frame, text=text, font=("Arial", 11), 
                           fg="#2c3e50", bg="white", relief="flat", 
                           anchor="w", command=command, cursor="hand2",
                           activebackground="#ecf0f1", activeforeground="#2c3e50")
            btn.pack(fill="x", pady=2)
            self.menu_buttons[text] = btn
        
        # Highlight dashboard as active
        self.highlight_menu("📊 Dashboard")
    
    def create_main_content(self):
        """Create main content area"""
        self.main_frame = tk.Frame(self.root, bg="#f8f9fa")
        self.main_frame.grid(row=0, column=1, sticky="nsew", padx=0, pady=0)
        
        # Top header
        self.create_header()
        
        # Create scrollable content area
        self.create_scrollable_content()
        
        # Configure the scrollable frame for grid layout
        self.scrollable_frame.grid_columnconfigure(0, weight=1)
        self.scrollable_frame.grid_rowconfigure(0, weight=1)
        
        # Create different content pages
        self.create_dashboard_content()
        self.create_students_content()
        self.create_teachers_content()
        self.create_predictions_content()
        self.create_settings_content()
        
        # Show dashboard by default
        self.show_dashboard()
    
    def create_header(self):
        """Create top header bar"""
        header = tk.Frame(self.main_frame, bg="#3498db", height=60)
        header.pack(fill="x", side="top")
        header.pack_propagate(False)
        
        # Title
        title_label = tk.Label(header, text="System Management Dashboard", 
                              font=("Arial", 18, "bold"), fg="white", bg="#3498db")
        title_label.pack(side="left", padx=20, pady=15)
        
        # Logout button
        logout_btn = tk.Button(header, text="Logout", font=("Arial", 11, "bold"),
                              fg="white", bg="#27ae60", relief="flat", 
                              cursor="hand2", command=self.logout,
                              activebackground="#229954", activeforeground="white")
        logout_btn.pack(side="right", padx=20, pady=15)
    
    def create_scrollable_content(self):
        """Create scrollable content area"""
        # Create canvas and scrollbar for scrolling
        self.canvas = tk.Canvas(self.main_frame, bg="#f8f9fa", highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(self.main_frame, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas, bg="#f8f9fa")
        
        # Configure scrolling
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        
        # Pack canvas and scrollbar
        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")
        
        # Create a container inside the scrollable frame that will hold different pages
        self.content_frame = tk.Frame(self.scrollable_frame, bg="#f8f9fa")
        self.content_frame.grid(row=0, column=0, sticky="nsew")
        self.scrollable_frame.grid_columnconfigure(0, weight=1)
        self.scrollable_frame.grid_rowconfigure(0, weight=1)
        
        # Optional: bind mouse wheel for smoother scrolling
        self.canvas.bind_all("<MouseWheel>", lambda e: self.canvas.yview_scroll(int(-1*(e.delta/120)), "units"))

    def create_dashboard_content(self):
        """Create dashboard content and sections"""
        self.dashboard_content = tk.Frame(self.content_frame, bg="#f8f9fa")
        # Grid weights for dashboard
        self.dashboard_content.grid_columnconfigure(0, weight=1)
        self.dashboard_content.grid_columnconfigure(1, weight=1)
        self.dashboard_content.grid_columnconfigure(2, weight=1)
        self.dashboard_content.grid_rowconfigure(0, weight=0)  # could be future title
        self.dashboard_content.grid_rowconfigure(1, weight=0)  # stats cards
        self.dashboard_content.grid_rowconfigure(2, weight=1)  # charts
        self.dashboard_content.grid_rowconfigure(3, weight=0)  # top students title
        self.dashboard_content.grid_rowconfigure(4, weight=0)  # top students cards
        
        # Build the dashboard sections
        self.create_stats_cards()
        self.create_charts_section()
        self.create_top_students_section()

    def run(self):
        """Start the Tkinter main loop"""
        self.root.mainloop()
    
    def create_stats_cards(self):
        """Create statistics cards using grid layout"""
        # Card 1: Total Students
        card1 = tk.Frame(self.dashboard_content, bg="#1abc9c", relief="flat", bd=0)
        card1.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        card1.grid_columnconfigure(0, weight=1)
        card1.grid_rowconfigure(0, weight=1)
        
        tk.Label(card1, text="Total Students", font=("Arial", 12, "bold"), 
                fg="white", bg="#1abc9c").grid(row=0, column=0, sticky="w", padx=15, pady=(15, 5))
        
        # Icon
        icon_frame = tk.Frame(card1, bg="#1abc9c")
        icon_frame.grid(row=1, column=0, sticky="w", padx=15, pady=5)
        tk.Label(icon_frame, text="👥", font=("Arial", 20), fg="white", bg="#1abc9c").grid(row=0, column=0)
        
        self.students_count_label = tk.Label(card1, text="0", font=("Arial", 24, "bold"), 
                                            fg="white", bg="#1abc9c")
        self.students_count_label.grid(row=2, column=0, sticky="w", padx=15, pady=(0, 15))
        
        # Card 2: Total Teachers
        card2 = tk.Frame(self.dashboard_content, bg="#e74c3c", relief="flat", bd=0)
        card2.grid(row=1, column=1, padx=10, pady=10, sticky="nsew")
        card2.grid_columnconfigure(0, weight=1)
        card2.grid_rowconfigure(0, weight=1)
        
        tk.Label(card2, text="Total Teachers", font=("Arial", 12, "bold"), 
                fg="white", bg="#e74c3c").grid(row=0, column=0, sticky="w", padx=15, pady=(15, 5))
        
        icon_frame2 = tk.Frame(card2, bg="#e74c3c")
        icon_frame2.grid(row=1, column=0, sticky="w", padx=15, pady=5)
        tk.Label(icon_frame2, text="👨‍🏫", font=("Arial", 20), fg="white", bg="#e74c3c").grid(row=0, column=0)
        
        self.teachers_count_label = tk.Label(card2, text="0", font=("Arial", 24, "bold"), 
                                            fg="white", bg="#e74c3c")
        self.teachers_count_label.grid(row=2, column=0, sticky="w", padx=15, pady=(0, 15))
        
        # Card 3: Average Performance
        card3 = tk.Frame(self.dashboard_content, bg="#f39c12", relief="flat", bd=0)
        card3.grid(row=1, column=2, padx=10, pady=10, sticky="nsew")
        card3.grid_columnconfigure(0, weight=1)
        card3.grid_rowconfigure(0, weight=1)
        
        tk.Label(card3, text="Avg Performance", font=("Arial", 12, "bold"), 
                fg="white", bg="#f39c12").grid(row=0, column=0, sticky="w", padx=15, pady=(15, 5))
        
        icon_frame3 = tk.Frame(card3, bg="#f39c12")
        icon_frame3.grid(row=1, column=0, sticky="w", padx=15, pady=5)
        tk.Label(icon_frame3, text="📊", font=("Arial", 20), fg="white", bg="#f39c12").grid(row=0, column=0)
        
        self.avg_performance_label = tk.Label(card3, text="0%", font=("Arial", 24, "bold"), 
                                             fg="white", bg="#f39c12")
        self.avg_performance_label.grid(row=2, column=0, sticky="w", padx=15, pady=(0, 15))
    
    def create_top_students_section(self):
        """Create top 3 students section using grid layout"""
        # Section title
        title_label = tk.Label(self.dashboard_content, text="🏆 Top 3 Students (Les 3 Meilleurs Élèves)", 
                              font=("Arial", 16, "bold"), fg="#2c3e50", bg="#f8f9fa")
        title_label.grid(row=3, column=0, columnspan=3, sticky="w", padx=20, pady=(20, 10))
        
        # Get top students data
        top_students = db.get_top_students(3)
        
        # Medal colors and positions
        medal_colors = ["#FFD700", "#C0C0C0", "#CD7F32"]  # Gold, Silver, Bronze
        medal_emojis = ["🥇", "🥈", "🥉"]
        positions = ["1st", "2nd", "3rd"]
        
        for i, student in enumerate(top_students):
            # Create student card
            card = tk.Frame(self.dashboard_content, bg="white", relief="solid", bd=1)
            card.grid(row=4, column=i, padx=10, pady=5, sticky="nsew")
            card.grid_columnconfigure(0, weight=1)
            card.grid_rowconfigure(0, weight=1)
            
            # Medal and position
            medal_frame = tk.Frame(card, bg="white")
            medal_frame.grid(row=0, column=0, sticky="ew", padx=15, pady=(15, 5))
            
            medal_label = tk.Label(medal_frame, text=medal_emojis[i], font=("Arial", 24), 
                                  bg="white", fg=medal_colors[i])
            medal_label.grid(row=0, column=0)
            
            position_label = tk.Label(medal_frame, text=positions[i], font=("Arial", 12, "bold"), 
                                    bg="white", fg="#7f8c8d")
            position_label.grid(row=0, column=1, padx=(10, 0))
            
            # Student name
            name_label = tk.Label(card, text=student['fullname'], font=("Arial", 14, "bold"), 
                                 bg="white", fg="#2c3e50")
            name_label.grid(row=1, column=0, pady=(0, 5), sticky="ew")
            
            # Student details
            details_frame = tk.Frame(card, bg="white")
            details_frame.grid(row=2, column=0, sticky="ew", padx=15, pady=5)
            details_frame.grid_columnconfigure(0, weight=1)
            details_frame.grid_columnconfigure(1, weight=1)
            
            # CGPA
            cgpa_frame = tk.Frame(details_frame, bg="white")
            cgpa_frame.grid(row=0, column=0, columnspan=2, sticky="ew", pady=2)
            cgpa_frame.grid_columnconfigure(0, weight=1)
            cgpa_frame.grid_columnconfigure(1, weight=1)
            
            tk.Label(cgpa_frame, text="CGPA:", font=("Arial", 10), bg="white", fg="#7f8c8d").grid(row=0, column=0, sticky="w")
            cgpa_value = tk.Label(cgpa_frame, text=f"{student['cgpa']:.2f}", font=("Arial", 12, "bold"), 
                                 bg="white", fg="#27ae60")
            cgpa_value.grid(row=0, column=1, sticky="e")
            
            # Average percentage
            avg_frame = tk.Frame(details_frame, bg="white")
            avg_frame.grid(row=1, column=0, columnspan=2, sticky="ew", pady=2)
            avg_frame.grid_columnconfigure(0, weight=1)
            avg_frame.grid_columnconfigure(1, weight=1)
            
            tk.Label(avg_frame, text="Average:", font=("Arial", 10), bg="white", fg="#7f8c8d").grid(row=0, column=0, sticky="w")
            avg_value = tk.Label(avg_frame, text=f"{student['avg_percentage']:.1f}%", font=("Arial", 12, "bold"), 
                                bg="white", fg="#3498db")
            avg_value.grid(row=0, column=1, sticky="e")
            
            # Total exams
            exams_frame = tk.Frame(details_frame, bg="white")
            exams_frame.grid(row=2, column=0, columnspan=2, sticky="ew", pady=2)
            exams_frame.grid_columnconfigure(0, weight=1)
            exams_frame.grid_columnconfigure(1, weight=1)
            
            tk.Label(exams_frame, text="Exams:", font=("Arial", 10), bg="white", fg="#7f8c8d").grid(row=0, column=0, sticky="w")
            exams_value = tk.Label(exams_frame, text=str(student['total_exams']), font=("Arial", 12, "bold"), 
                                  bg="white", fg="#e74c3c")
            exams_value.grid(row=0, column=1, sticky="e")
            
            # Gender indicator
            gender_frame = tk.Frame(details_frame, bg="white")
            gender_frame.grid(row=3, column=0, columnspan=2, sticky="ew", pady=(5, 10))
            
            gender_emoji = "👨" if student['gender'] == 'Male' else "👩"
            tk.Label(gender_frame, text=gender_emoji, font=("Arial", 12), bg="white").grid(row=0, column=0, sticky="w")
            tk.Label(gender_frame, text=student['gender'], font=("Arial", 10), bg="white", fg="#7f8c8d").grid(row=0, column=1, sticky="w", padx=(5, 0))
        
        # If no students found, show message
        if not top_students:
            no_data_frame = tk.Frame(self.dashboard_content, bg="white", relief="solid", bd=1)
            no_data_frame.grid(row=4, column=0, columnspan=3, padx=10, pady=5, sticky="ew")
            
            tk.Label(no_data_frame, text="No student performance data available", 
                    font=("Arial", 14), fg="#7f8c8d", bg="white").grid(row=0, column=0, pady=20, sticky="nsew")
    
    def create_charts_section(self):
        """Create charts section with 2 columns layout using grid"""
        # Bar chart frame - Left column (Performance by Subject)
        bar_frame = tk.Frame(self.dashboard_content, bg="white", relief="solid", bd=1)
        bar_frame.grid(row=2, column=0, padx=10, pady=10, sticky="nsew")
        bar_frame.grid_columnconfigure(0, weight=1)
        bar_frame.grid_rowconfigure(1, weight=1)
        
        tk.Label(bar_frame, text="Performance by Subject", font=("Arial", 14, "bold"), 
                fg="#2c3e50", bg="white").grid(row=0, column=0, pady=10, sticky="ew")
        
        # Enhanced bar chart using canvas
        self.bar_canvas = tk.Canvas(bar_frame, bg="white", highlightthickness=0)
        self.bar_canvas.grid(row=1, column=0, padx=20, pady=20, sticky="nsew")
        
        # Pie chart frame - Right column (Gender Distribution)
        pie_frame = tk.Frame(self.dashboard_content, bg="white", relief="solid", bd=1)
        pie_frame.grid(row=2, column=1, padx=10, pady=10, sticky="nsew")
        pie_frame.grid_columnconfigure(0, weight=1)
        pie_frame.grid_rowconfigure(1, weight=1)
        
        tk.Label(pie_frame, text="Gender Distribution", font=("Arial", 14, "bold"), 
                fg="#2c3e50", bg="white").grid(row=0, column=0, pady=10, sticky="ew")
        
        # Enhanced pie chart using canvas
        self.pie_canvas = tk.Canvas(pie_frame, bg="white", highlightthickness=0)
        self.pie_canvas.grid(row=1, column=0, padx=20, pady=20, sticky="nsew")
        
        # Performance Trends chart - Bottom Left (spanning both columns)
        trends_frame = tk.Frame(self.dashboard_content, bg="white", relief="solid", bd=1)
        trends_frame.grid(row=2, column=2, padx=10, pady=10, sticky="nsew")
        trends_frame.grid_columnconfigure(0, weight=1)
        trends_frame.grid_rowconfigure(1, weight=1)
        
        tk.Label(trends_frame, text="Performance Trends", font=("Arial", 14, "bold"), 
                fg="#2c3e50", bg="white").grid(row=0, column=0, pady=10, sticky="ew")
        
        # Performance trends chart
        self.trends_canvas = tk.Canvas(trends_frame, bg="white", highlightthickness=0)
        self.trends_canvas.grid(row=1, column=0, padx=20, pady=20, sticky="nsew")
    
    def create_students_content(self):
        """Create students management content using grid layout"""
        self.students_content = tk.Frame(self.content_frame, bg="#f8f9fa")
        
        # Configure grid weights for the students content
        self.students_content.grid_columnconfigure(0, weight=1)
        self.students_content.grid_rowconfigure(0, weight=0)  # Title row
        self.students_content.grid_rowconfigure(1, weight=0)  # Actions row
        self.students_content.grid_rowconfigure(2, weight=1)  # Table row
        
        # Title
        title_label = tk.Label(self.students_content, text="Student Management", 
                              font=("Arial", 24, "bold"), fg="#2c3e50", bg="#f8f9fa")
        title_label.grid(row=0, column=0, sticky="w", padx=20, pady=(20, 10))
        
        # Search and actions frame
        actions_frame = tk.Frame(self.students_content, bg="#f8f9fa")
        actions_frame.grid(row=1, column=0, sticky="ew", padx=20, pady=10)
        actions_frame.grid_columnconfigure(1, weight=1)
        
        # Search
        tk.Label(actions_frame, text="Search:", font=("Arial", 11), 
                fg="#2c3e50", bg="#f8f9fa").grid(row=0, column=0, sticky="w", padx=(0, 10))
        
        self.student_search_var = tk.StringVar()
        search_entry = tk.Entry(actions_frame, textvariable=self.student_search_var, 
                               font=("Arial", 11), width=30)
        search_entry.grid(row=0, column=1, sticky="w", padx=(0, 20))
        search_entry.bind('<KeyRelease>', self.filter_students)
        
        # Action buttons frame
        buttons_frame = tk.Frame(actions_frame, bg="#f8f9fa")
        buttons_frame.grid(row=0, column=2, sticky="e")
        
        # Action buttons
        tk.Button(buttons_frame, text="➕ Add Student", font=("Arial", 11), 
                 fg="white", bg="#27ae60", relief="flat", cursor="hand2",
                 command=self.add_student).grid(row=0, column=0, padx=5, sticky="ew")
        
        tk.Button(buttons_frame, text="✏️ Edit", font=("Arial", 11), 
                 fg="white", bg="#3498db", relief="flat", cursor="hand2",
                 command=self.edit_student).grid(row=0, column=1, padx=5, sticky="ew")
        
        tk.Button(buttons_frame, text="🗑️ Delete", font=("Arial", 11), 
                 fg="white", bg="#e74c3c", relief="flat", cursor="hand2",
                 command=self.delete_student).grid(row=0, column=2, padx=5, sticky="ew")
        
        tk.Button(buttons_frame, text="📊 View Marks", font=("Arial", 11), 
                 fg="white", bg="#9b59b6", relief="flat", cursor="hand2",
                 command=self.view_student_marks).grid(row=0, column=3, padx=5, sticky="ew")
        
        # Students table
        table_frame = tk.Frame(self.students_content, bg="white", relief="solid", bd=1)
        table_frame.grid(row=2, column=0, sticky="nsew", padx=20, pady=10)
        table_frame.grid_columnconfigure(0, weight=1)
        table_frame.grid_rowconfigure(0, weight=1)
        
        # Create Treeview
        columns = ('ID', 'Name', 'Email', 'Phone', 'Gender', 'Status', 'Enrollment Date')
        self.students_tree = ttk.Treeview(table_frame, columns=columns, show='headings', height=15)
        
        # Define headings
        for col in columns:
            self.students_tree.heading(col, text=col)
            self.students_tree.column(col, width=120)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.students_tree.yview)
        self.students_tree.configure(yscrollcommand=scrollbar.set)
        
        self.students_tree.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        scrollbar.grid(row=0, column=1, sticky="ns", pady=10)
    
    def create_teachers_content(self):
        """Create teachers management content using grid layout"""
        self.teachers_content = tk.Frame(self.content_frame, bg="#f8f9fa")
        
        # Configure grid weights for the teachers content
        self.teachers_content.grid_columnconfigure(0, weight=1)
        self.teachers_content.grid_rowconfigure(0, weight=0)  # Title row
        self.teachers_content.grid_rowconfigure(1, weight=0)  # Actions row
        self.teachers_content.grid_rowconfigure(2, weight=1)  # Table row
        
        # Title
        title_label = tk.Label(self.teachers_content, text="Teacher Management", 
                              font=("Arial", 24, "bold"), fg="#2c3e50", bg="#f8f9fa")
        title_label.grid(row=0, column=0, sticky="w", padx=20, pady=(20, 10))
        
        # Search and actions frame
        actions_frame = tk.Frame(self.teachers_content, bg="#f8f9fa")
        actions_frame.grid(row=1, column=0, sticky="ew", padx=20, pady=10)
        actions_frame.grid_columnconfigure(1, weight=1)
        
        # Search
        tk.Label(actions_frame, text="Search:", font=("Arial", 11), 
                fg="#2c3e50", bg="#f8f9fa").grid(row=0, column=0, sticky="w", padx=(0, 10))
        
        self.teacher_search_var = tk.StringVar()
        search_entry = tk.Entry(actions_frame, textvariable=self.teacher_search_var, 
                               font=("Arial", 11), width=30)
        search_entry.grid(row=0, column=1, sticky="w", padx=(0, 20))
        search_entry.bind('<KeyRelease>', self.filter_teachers)
        
        # Action buttons frame
        buttons_frame = tk.Frame(actions_frame, bg="#f8f9fa")
        buttons_frame.grid(row=0, column=2, sticky="e")
        
        # Action buttons
        tk.Button(buttons_frame, text="➕ Add Teacher", font=("Arial", 11), 
                 fg="white", bg="#27ae60", relief="flat", cursor="hand2",
                 command=self.add_teacher).grid(row=0, column=0, padx=5, sticky="ew")
        
        tk.Button(buttons_frame, text="✏️ Edit", font=("Arial", 11), 
                 fg="white", bg="#3498db", relief="flat", cursor="hand2",
                 command=self.edit_teacher).grid(row=0, column=1, padx=5, sticky="ew")
        
        tk.Button(buttons_frame, text="🗑️ Delete", font=("Arial", 11), 
                 fg="white", bg="#e74c3c", relief="flat", cursor="hand2",
                 command=self.delete_teacher).grid(row=0, column=2, padx=5, sticky="ew")
        
        # Teachers table
        table_frame = tk.Frame(self.teachers_content, bg="white", relief="solid", bd=1)
        table_frame.grid(row=2, column=0, sticky="nsew", padx=20, pady=10)
        table_frame.grid_columnconfigure(0, weight=1)
        table_frame.grid_rowconfigure(0, weight=1)
        
        # Create Treeview
        columns = ('ID', 'Name', 'Email', 'Phone', 'Department', 'Qualification', 'Status')
        self.teachers_tree = ttk.Treeview(table_frame, columns=columns, show='headings', height=15)
        
        # Define headings
        for col in columns:
            self.teachers_tree.heading(col, text=col)
            self.teachers_tree.column(col, width=120)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.teachers_tree.yview)
        self.teachers_tree.configure(yscrollcommand=scrollbar.set)
        
        self.teachers_tree.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        scrollbar.grid(row=0, column=1, sticky="ns", pady=10)
    
    def create_settings_content(self):
        """Create settings content using grid layout"""
        self.settings_content = tk.Frame(self.content_frame, bg="#f8f9fa")
        
        # Configure grid weights for the settings content
        self.settings_content.grid_columnconfigure(0, weight=1)
        self.settings_content.grid_rowconfigure(0, weight=0)  # Title row
        self.settings_content.grid_rowconfigure(1, weight=1)  # Content row
        
        # Title
        title_label = tk.Label(self.settings_content, text="System Settings", 
                              font=("Arial", 24, "bold"), fg="#2c3e50", bg="#f8f9fa")
        title_label.grid(row=0, column=0, sticky="w", padx=20, pady=(20, 10))
        
        # Settings content
        settings_frame = tk.Frame(self.settings_content, bg="white", relief="solid", bd=1)
        settings_frame.grid(row=1, column=0, sticky="nsew", padx=20, pady=10)
        settings_frame.grid_columnconfigure(0, weight=1)
        settings_frame.grid_rowconfigure(0, weight=1)
        
        tk.Label(settings_frame, text="Settings functionality will be implemented here", 
                font=("Arial", 14), fg="#7f8c8d", bg="white").grid(row=0, column=0, sticky="nsew")
    
    def highlight_menu(self, active_menu):
        """Highlight active menu item"""
        for text, btn in self.menu_buttons.items():
            if text == active_menu:
                btn.config(bg="#ecf0f1", fg="#2c3e50")
            else:
                btn.config(bg="white", fg="#2c3e50")
    
    def show_dashboard(self):
        """Show dashboard content"""
        self.hide_all_content()
        self.dashboard_content.grid(row=0, column=0, sticky="nsew")
        self.highlight_menu("📊 Dashboard")
    
    def show_students(self):
        """Show students content"""
        self.hide_all_content()
        self.students_content.grid(row=0, column=0, sticky="nsew")
        self.highlight_menu("👥 Manage Students")
    
    def show_teachers(self):
        """Show teachers content"""
        self.hide_all_content()
        self.teachers_content.grid(row=0, column=0, sticky="nsew")
        self.highlight_menu("👨‍🏫 Manage Teachers")
    
    def show_predictions(self):
        """Show predictions content"""
        self.hide_all_content()
        self.predictions_content.grid(row=0, column=0, sticky="nsew")
        self.highlight_menu("🤖 Predictions")

    def show_settings(self):
        """Show settings content"""
        self.hide_all_content()
        self.settings_content.grid(row=0, column=0, sticky="nsew")
        self.highlight_menu("⚙️ Settings")
    
    def hide_all_content(self):
        """Hide all content frames"""
        self.dashboard_content.grid_forget()
        self.students_content.grid_forget()
        self.teachers_content.grid_forget()
        if hasattr(self, 'predictions_content'):
            self.predictions_content.grid_forget()
        self.settings_content.grid_forget()

    def create_predictions_content(self):
        """Create predictions management page"""
        self.predictions_content = tk.Frame(self.content_frame, bg="#f8f9fa")
        self.predictions_content.grid_columnconfigure(0, weight=1)
        self.predictions_content.grid_rowconfigure(0, weight=0)
        self.predictions_content.grid_rowconfigure(1, weight=0)
        self.predictions_content.grid_rowconfigure(2, weight=1)  # students list
        self.predictions_content.grid_rowconfigure(3, weight=1)  # results box

        title_label = tk.Label(self.predictions_content, text="AI Predictions", 
                              font=("Arial", 24, "bold"), fg="#2c3e50", bg="#f8f9fa")
        title_label.grid(row=0, column=0, sticky="w", padx=20, pady=(20, 10))

        actions = tk.Frame(self.predictions_content, bg="#f8f9fa")
        actions.grid(row=1, column=0, sticky="ew", padx=20, pady=10)
        actions.grid_columnconfigure(3, weight=1)

        tk.Button(actions, text="📈 Predict Selected Student", font=("Arial", 11), fg="white", bg="#3498db",
                  relief="flat", cursor="hand2", command=self.predict_selected_student).grid(row=0, column=0, padx=5)
        tk.Button(actions, text="🧹 Clear", font=("Arial", 11), fg="#2c3e50", bg="#ecf0f1",
                  relief="flat", cursor="hand2", command=self.clear_predictions).grid(row=0, column=1, padx=5)

        # Students selector panel
        sel = tk.Frame(self.predictions_content, bg="#f8f9fa")
        sel.grid(row=2, column=0, sticky="nsew", padx=20, pady=(0, 10))
        sel.grid_columnconfigure(0, weight=1)
        sel.grid_rowconfigure(1, weight=1)

        tk.Label(sel, text="Select Student", font=("Arial", 14, "bold"), fg="#2c3e50", bg="#f8f9fa").grid(row=0, column=0, sticky="w", pady=(0, 6))

        table_frame = tk.Frame(sel, bg="white", relief="solid", bd=1)
        table_frame.grid(row=1, column=0, sticky="nsew")
        table_frame.grid_columnconfigure(0, weight=1)
        table_frame.grid_rowconfigure(0, weight=1)

        cols = ("ID", "Name", "Email")
        self.pred_students_tree = ttk.Treeview(table_frame, columns=cols, show='headings', height=8)
        for c in cols:
            self.pred_students_tree.heading(c, text=c)
            self.pred_students_tree.column(c, width=160)
        vs = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.pred_students_tree.yview)
        self.pred_students_tree.configure(yscrollcommand=vs.set)
        self.pred_students_tree.grid(row=0, column=0, sticky="nsew")
        vs.grid(row=0, column=1, sticky="ns")

        # Load students into selector
        try:
            for item in self.pred_students_tree.get_children():
                self.pred_students_tree.delete(item)
            _students = db.get_all_students() or []
            for s in _students:
                self.pred_students_tree.insert('', 'end', values=(s.get('student_id'), s.get('fullname'), s.get('email')))
        except Exception:
            pass

        # Auto-predict on selection
        try:
            self.pred_students_tree.bind('<<TreeviewSelect>>', lambda e: self.predict_selected_student())
        except Exception:
            pass

        # Results and chart area
        # Chart container (matplotlib embedded if available)
        chart_wrap = tk.Frame(self.predictions_content, bg="#f8f9fa")
        chart_wrap.grid(row=3, column=0, sticky="nsew", padx=20, pady=10)
        chart_wrap.grid_columnconfigure(0, weight=1)
        chart_wrap.grid_columnconfigure(1, weight=1)
        chart_wrap.grid_rowconfigure(0, weight=1)

        # Left: bar chart (per-subject predicted %)
        self.pred_bar_frame = tk.Frame(chart_wrap, bg="white", relief="solid", bd=1)
        self.pred_bar_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 5))
        self.pred_bar_frame.grid_columnconfigure(0, weight=1)
        self.pred_bar_frame.grid_rowconfigure(0, weight=1)

        # Right: pie chart (grade distribution)
        self.pred_pie_frame = tk.Frame(chart_wrap, bg="white", relief="solid", bd=1)
        self.pred_pie_frame.grid(row=0, column=1, sticky="nsew", padx=(5, 0))
        self.pred_pie_frame.grid_columnconfigure(0, weight=1)
        self.pred_pie_frame.grid_rowconfigure(0, weight=1)

        # Text results below chart
        self.pred_results = tk.Text(self.predictions_content, height=8, bg="white")
        self.pred_results.grid(row=4, column=0, sticky="nsew", padx=20, pady=(0, 10))

    def clear_predictions(self):
        try:
            self.pred_results.delete('1.0', 'end')
        except Exception:
            pass
        # Clear chart areas
        try:
            for w in getattr(self, 'pred_bar_frame', []).winfo_children():
                w.destroy()
        except Exception:
            pass
        try:
            for w in getattr(self, 'pred_pie_frame', []).winfo_children():
                w.destroy()
        except Exception:
            pass

    def predict_selected_student(self):
        student_id = None
        # Prefer selection from Predictions page student list
        if hasattr(self, 'pred_students_tree'):
            sel = self.pred_students_tree.selection()
            if sel:
                try:
                    student_id = self.pred_students_tree.item(sel[0])['values'][0]
                except Exception:
                    student_id = None
        # Fallback to Students tab selection
        if student_id is None:
            selection = self.students_tree.selection() if hasattr(self, 'students_tree') else []
            if selection:
                item = self.students_tree.item(selection[0])
                student_id = item['values'][0]
        if student_id is None:
            messagebox.showwarning("Warning", "Please select a student (in Predictions or Students tab).")
            return
        try:
            from ml_model import load_model, predict_next_percentage, percentage_to_grade
            model = load_model()
            if not model:
                messagebox.showwarning("Warning", "Model not available. Please train it once from terminal.")
                return
            # Predict for each subject the student has marks in
            marks = db.get_student_marks(student_id) or []
            if not marks:
                messagebox.showinfo("Info", "No marks found for this student.")
                self.clear_predictions()
                return
            # Build subject list (id -> name)
            subj_seen = {}
            for m in marks:
                sid = m.get('subject_id')
                name = m.get('subject_name')
                if sid is not None and name:
                    subj_seen[int(sid)] = str(name)
            preds = []
            for sid, name in subj_seen.items():
                try:
                    p = predict_next_percentage(model, int(student_id), int(sid))
                    if p is not None:
                        preds.append((name, float(p)))
                except Exception:
                    continue
            preds.sort(key=lambda x: x[0])
            # Update text results
            self.pred_results.delete('1.0', 'end')
            if not preds:
                self.pred_results.insert('end', "Not enough data to predict for this student.\n")
            else:
                self.pred_results.insert('end', f"Predictions for student {student_id}:\n")
                for name, p in preds:
                    self.pred_results.insert('end', f" - {name}: {p:.1f}% ({percentage_to_grade(p)})\n")
                self.pred_results.see('end')
            # Render chart
            self.render_pred_charts(preds)
        except Exception as e:
            messagebox.showerror("Error", f"Prediction failed: {e}")

    def render_pred_charts(self, preds):
        # Clear previous charts
        try:
            for w in self.pred_bar_frame.winfo_children():
                w.destroy()
        except Exception:
            pass
        try:
            for w in self.pred_pie_frame.winfo_children():
                w.destroy()
        except Exception:
            pass
        # Empty state
        if not preds:
            for frame in (self.pred_bar_frame, self.pred_pie_frame):
                try:
                    tk.Label(frame, text="No predictions to display", bg="white", fg="#7f8c8d", font=("Arial", 12)).grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
                except Exception:
                    pass
            return
        # Try to render charts
        try:
            import matplotlib.pyplot as plt
            from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
        except ImportError:
            for frame in (self.pred_bar_frame, self.pred_pie_frame):
                tk.Label(frame, text="Matplotlib not available", bg="white", fg="#7f8c8d", font=("Arial", 12)).grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
            return

        # Bar chart (left)
        try:
            fig_bar, ax = plt.subplots(figsize=(6.5, 3.2))
            fig_bar.patch.set_facecolor('white')
            names = [n for n, _ in preds]
            values = [v for _, v in preds]
            xs = range(len(names))
            bars = ax.bar(xs, values, color='#3498db')
            ax.set_ylim(0, 100)
            ax.set_ylabel('Predicted %')
            ax.set_title('Predicted Next Performance by Subject')
            ax.set_xticks(list(xs))
            ax.set_xticklabels(names, rotation=20, ha='right')
            for b, v in zip(bars, values):
                ax.text(b.get_x() + b.get_width()/2, b.get_height()+1, f"{v:.1f}%", ha='center', va='bottom', fontsize=9)
            plt.tight_layout()
            canvas_bar = FigureCanvasTkAgg(fig_bar, master=self.pred_bar_frame)
            canvas_bar.draw()
            canvas_bar.get_tk_widget().grid(row=0, column=0, sticky="nsew")
        except Exception:
            tk.Label(self.pred_bar_frame, text="Failed to render bar chart", bg="white", fg="#e74c3c", font=("Arial", 12)).grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

        # Pie chart (right): grade distribution
        try:
            from ml_model import percentage_to_grade
            grades = [percentage_to_grade(v) for _, v in preds]
            order = ['A+', 'A', 'B', 'C', 'D', 'F']
            counts = [grades.count(g) for g in order]
            if sum(counts) == 0:
                tk.Label(self.pred_pie_frame, text="No data for grade distribution", bg="white", fg="#7f8c8d", font=("Arial", 12)).grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
            else:
                fig_pie, axp = plt.subplots(figsize=(6.5, 3.2))
                fig_pie.patch.set_facecolor('white')
                colors = ['#2ecc71', '#27ae60', '#3498db', '#f1c40f', '#e67e22', '#e74c3c']
                wedges, texts, autotexts = axp.pie(counts, labels=order, autopct='%1.0f%%', startangle=90, colors=colors, pctdistance=0.8)
                centre_circle = plt.Circle((0,0), 0.55, fc='white')
                axp.add_artist(centre_circle)
                axp.set_title('Predicted Grade Distribution')
                plt.tight_layout()
                canvas_pie = FigureCanvasTkAgg(fig_pie, master=self.pred_pie_frame)
                canvas_pie.draw()
                canvas_pie.get_tk_widget().grid(row=0, column=0, sticky="nsew")
        except Exception:
            tk.Label(self.pred_pie_frame, text="Failed to render pie chart", bg="white", fg="#e74c3c", font=("Arial", 12)).grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

    def predict_student_subject_dialog(self):
        # Deprecated in simplified UI; keep no-op for compatibility
        messagebox.showinfo("Info", "Use the student list to select and predict.")
    
    def load_dashboard_data(self):
        """Load dashboard statistics"""
        stats = db.get_system_stats()
        # Update visible labels (no undefined stats_cards)
        self.students_count_label.config(text=str(stats.get('active_students', 0)))
        self.teachers_count_label.config(text=str(stats.get('active_teachers', 0)))
        self.avg_performance_label.config(text=f"{stats.get('average_marks', 0)}%")
        # Refresh all charts
        self.create_bar_chart()
        self.create_pie_chart()
        self.create_trends_chart()
        # Refresh top students section
        self.refresh_top_students()
    
    def create_bar_chart(self):
        """Create bar chart using subject average percentages from DB"""
        self.bar_canvas.delete("all")
        
        # Get canvas dimensions
        canvas_width = self.bar_canvas.winfo_width()
        canvas_height = self.bar_canvas.winfo_height()
        
        if canvas_width <= 1 or canvas_height <= 1:
            # Canvas not yet rendered, schedule for later
            self.root.after(100, self.create_bar_chart)
            return
        
        # Real data: subject average percentages
        rows = db.get_subject_average_percentages(limit=8)
        subjects = [r['subject_name'] for r in rows] or ["No Data"]
        values = [round(r['avg_pct'] or 0, 1) for r in rows] or [0]
        colors = ["#3498db", "#e74c3c", "#f39c12", "#27ae60", "#9b59b6", "#16a085", "#d35400", "#2ecc71"]
        
        # Calculate dimensions
        margin = 40
        chart_width = canvas_width - 2 * margin
        chart_height = canvas_height - 2 * margin
        bar_width = (chart_width - (len(subjects) - 1) * 20) // len(subjects)
        
        # Draw bars
        for i, (subject, value, color) in enumerate(zip(subjects, values, colors)):
            x = margin + i * (bar_width + 20)
            bar_height = (value / 100) * chart_height
            y = margin + chart_height - bar_height
            
            # Bar with gradient effect
            self.bar_canvas.create_rectangle(x, y, x + bar_width, margin + chart_height, 
                                           fill=color, outline="", width=0)
            
            # Value label on top
            self.bar_canvas.create_text(x + bar_width/2, y - 15, 
                                       text=f"{value}%", font=("Arial", 11, "bold"), 
                                       fill="#2c3e50")
            
            # Subject label at bottom
            self.bar_canvas.create_text(x + bar_width/2, margin + chart_height + 20, 
                                       text=subject, font=("Arial", 10, "bold"), 
                                       fill="#2c3e50")
        
        # Add grid lines
        for i in range(0, 101, 20):
            y = margin + chart_height - (i / 100) * chart_height
            self.bar_canvas.create_line(margin, y, margin + chart_width, y, 
                                       fill="#ecf0f1", width=1)
    
    def create_pie_chart(self):
        """Create gender distribution donut chart from DB"""
        self.pie_canvas.delete("all")
        
        # Get canvas dimensions
        canvas_width = self.pie_canvas.winfo_width()
        canvas_height = self.pie_canvas.winfo_height()
        
        if canvas_width <= 1 or canvas_height <= 1:
            # Canvas not yet rendered, schedule for later
            self.root.after(100, self.create_pie_chart)
            return
        
        # Real gender distribution
        gd = db.get_gender_distribution()
        male_count = gd.get('Male', 0)
        female_count = gd.get('Female', 0)
        total = male_count + female_count
        
        center_x = canvas_width // 2
        center_y = canvas_height // 2
        radius = min(canvas_width, canvas_height) // 4
        
        # Draw pie chart
        if total > 0:
            male_angle = (male_count / total) * 360
            female_angle = (female_count / total) * 360
            
            # Male slice
            self.pie_canvas.create_arc(center_x - radius, center_y - radius,
                                     center_x + radius, center_y + radius,
                                     start=0, extent=male_angle, fill="#3498db", outline="white", width=2)
            
            # Female slice
            self.pie_canvas.create_arc(center_x - radius, center_y - radius,
                                     center_x + radius, center_y + radius,
                                     start=male_angle, extent=female_angle, fill="#e74c3c", outline="white", width=2)
            
            # Center circle for donut effect
            self.pie_canvas.create_oval(center_x - radius//2, center_y - radius//2,
                                      center_x + radius//2, center_y + radius//2,
                                      fill="white", outline="")
        
        # Enhanced legend
        legend_x = 20
        legend_y = 20
        
        # Male legend
        self.pie_canvas.create_rectangle(legend_x, legend_y, legend_x + 15, legend_y + 15, 
                                        fill="#3498db", outline="")
        self.pie_canvas.create_text(legend_x + 25, legend_y + 8, text=f"Male: {male_count}", 
                                   font=("Arial", 10, "bold"), fill="#2c3e50")
        
        # Female legend
        self.pie_canvas.create_rectangle(legend_x, legend_y + 25, legend_x + 15, legend_y + 40, 
                                        fill="#e74c3c", outline="")
        self.pie_canvas.create_text(legend_x + 25, legend_y + 33, text=f"Female: {female_count}", 
                                   font=("Arial", 10, "bold"), fill="#2c3e50")
        
        # Total in center
        self.pie_canvas.create_text(center_x, center_y, text=f"Total\n{total}", 
                                   font=("Arial", 12, "bold"), fill="#2c3e50", justify="center")
    
    def create_trends_chart(self):
        """Create performance trends line chart from DB monthly averages"""
        self.trends_canvas.delete("all")
        
        # Get canvas dimensions
        canvas_width = self.trends_canvas.winfo_width()
        canvas_height = self.trends_canvas.winfo_height()
        
        if canvas_width <= 1 or canvas_height <= 1:
            # Canvas not yet rendered, schedule for later
            self.root.after(100, self.create_trends_chart)
            return
        
        # Real monthly averages (last 6 months)
        rows = db.get_monthly_trends_average(months=6)
        months = [r['ym'] for r in rows] or ["N/A"]
        values = [round(r['avg_pct'] or 0, 1) for r in rows] or [0]
        
        margin = 40
        chart_width = canvas_width - 2 * margin
        chart_height = canvas_height - 2 * margin
        
        # Draw grid lines
        for i in range(0, 101, 20):
            y = margin + chart_height - (i / 100) * chart_height
            self.trends_canvas.create_line(margin, y, margin + chart_width, y, 
                                          fill="#ecf0f1", width=1)
        
        # Draw trend line
        points = []
        for i, (month, value) in enumerate(zip(months, values)):
            x = margin + (i / (len(months) - 1)) * chart_width
            y = margin + chart_height - (value / 100) * chart_height
            points.extend([x, y])
            
            # Draw data points
            self.trends_canvas.create_oval(x - 4, y - 4, x + 4, y + 4, 
                                          fill="#3498db", outline="white", width=2)
            
            # Month labels
            self.trends_canvas.create_text(x, margin + chart_height + 20, 
                                          text=month, font=("Arial", 9), fill="#2c3e50")
        
        # Draw trend line
        if len(points) >= 4:
            self.trends_canvas.create_line(points, fill="#3498db", width=3, smooth=True)
        
        # Y-axis labels
        for i in range(0, 101, 20):
            y = margin + chart_height - (i / 100) * chart_height
            self.trends_canvas.create_text(margin - 10, y, text=f"{i}%", 
                                          font=("Arial", 9), fill="#7f8c8d", anchor="e")
    
    
    def refresh_top_students(self):
        """Refresh the top students section with updated data"""
        # Find and destroy existing top students widgets
        for widget in self.dashboard_content.winfo_children():
            if isinstance(widget, tk.Label) and "Top 3 Students" in widget.cget("text"):
                # Destroy the title and all student cards
                widget.destroy()
                # Find and destroy all student cards in row 4
                for child in self.dashboard_content.winfo_children():
                    if isinstance(child, tk.Frame) and child.grid_info().get('row') == 4:
                        child.destroy()
                break
        
        # Recreate the top students section
        self.create_top_students_section()
    
    def load_students(self):
        """Load students data"""
        # Clear existing items
        for item in self.students_tree.get_children():
            self.students_tree.delete(item)
        
        students = db.get_all_students()
        for student in students:
            self.students_tree.insert('', 'end', values=(
                student['student_id'],
                student['fullname'],
                student['email'],
                student['phone'],
                student['gender'],
                student['status']
            ))
    
    def load_teachers(self):
        """Load teachers data"""
        # Clear existing items
        for item in self.teachers_tree.get_children():
            self.teachers_tree.delete(item)
        
        teachers = db.get_all_teachers()
        for teacher in teachers:
            self.teachers_tree.insert('', 'end', values=(
                teacher['teacher_id'],
                teacher['fullname'],
                teacher['email'],
                teacher['phone'],
                teacher['department'],
                teacher['status']
            ))
    
    def filter_students(self, *args):
        """Filter students based on search"""
        search_term = self.student_search_var.get().lower()
        
        # Clear existing items
        for item in self.students_tree.get_children():
            self.students_tree.delete(item)
        
        students = db.get_all_students()
        for student in students:
            if (search_term in student['fullname'].lower() or 
                search_term in student['email'].lower() or
                search_term in str(student['student_id'])):
                self.students_tree.insert('', 'end', values=(
                    student['student_id'],
                    student['fullname'],
                    student['email'],
                    student['phone'],
                    student['gender'],
                    student['status']
                ))
    
    def filter_teachers(self, *args):
        """Filter teachers based on search"""
        search_term = self.teacher_search_var.get().lower()
        
        # Clear existing items
        for item in self.teachers_tree.get_children():
            self.teachers_tree.delete(item)
        
        teachers = db.get_all_teachers()
        for teacher in teachers:
            if (search_term in teacher['fullname'].lower() or 
                search_term in teacher['email'].lower() or
                search_term in str(teacher['teacher_id'])):
                self.teachers_tree.insert('', 'end', values=(
                    teacher['teacher_id'],
                    teacher['fullname'],
                    teacher['email'],
                    teacher['phone'],
                    teacher['department'],
                    teacher['status']
                ))
    
    def add_student(self):
        """Add new student - persists to DB and refreshes table"""
        form = tk.Toplevel(self.root)
        form.title("Add New Student")
        form.geometry("480x560")
        form.resizable(False, False)

        # Form variables
        username_var = tk.StringVar()
        password_var = tk.StringVar()
        fullname_var = tk.StringVar()
        email_var = tk.StringVar()
        phone_var = tk.StringVar()
        dob_var = tk.StringVar()
        gender_var = tk.StringVar(value="Male")
        address_var = tk.StringVar()
        status_var = tk.StringVar(value="Active")

        row = 0
        def add_row(label_text, widget):
            tk.Label(form, text=label_text, font=("Arial", 11)).grid(row=row, column=0, padx=20, pady=8, sticky="w")
            widget.grid(row=row, column=1, padx=20, pady=8, sticky="w")
            return 1

        username_entry = tk.Entry(form, textvariable=username_var, font=("Arial", 11))
        password_entry = tk.Entry(form, textvariable=password_var, font=("Arial", 11), show='*')
        fullname_entry = tk.Entry(form, textvariable=fullname_var, font=("Arial", 11))
        email_entry = tk.Entry(form, textvariable=email_var, font=("Arial", 11))
        phone_entry = tk.Entry(form, textvariable=phone_var, font=("Arial", 11))
        dob_entry = tk.Entry(form, textvariable=dob_var, font=("Arial", 11))

        row += add_row("Username", username_entry)
        row += add_row("Password", password_entry)
        row += add_row("Full Name", fullname_entry)
        row += add_row("Email", email_entry)
        row += add_row("Phone", phone_entry)
        row += add_row("Date of Birth (YYYY-MM-DD)", dob_entry)

        # Gender radios
        tk.Label(form, text="Gender", font=("Arial", 11)).grid(row=row, column=0, padx=20, pady=8, sticky="w")
        gender_frame = tk.Frame(form)
        gender_frame.grid(row=row, column=1, padx=20, pady=8, sticky="w")
        tk.Radiobutton(gender_frame, text="Male", variable=gender_var, value="Male").pack(side="left")
        tk.Radiobutton(gender_frame, text="Female", variable=gender_var, value="Female").pack(side="left")
        row += 1

        address_entry = tk.Entry(form, textvariable=address_var, font=("Arial", 11))
        row += add_row("Address", address_entry)

        # Status combobox
        tk.Label(form, text="Status", font=("Arial", 11)).grid(row=row, column=0, padx=20, pady=8, sticky="w")
        status_combo = ttk.Combobox(form, textvariable=status_var, values=["Active", "Inactive"], state="readonly", width=18)
        status_combo.grid(row=row, column=1, padx=20, pady=8, sticky="w")
        row += 1

        def submit():
            username = username_entry.get().strip()
            password = password_entry.get().strip()
            fullname = fullname_entry.get().strip()
            email = email_entry.get().strip()
            phone = phone_entry.get().strip()
            dob = dob_entry.get().strip()
            gender = gender_var.get().strip() or "Male"
            address = address_entry.get().strip()
            status = status_var.get().strip()

            # Core required fields only
            required_map = {
                "username": username,
                "password": password,
                "full name": fullname,
                "email": email,
            }
            missing = [field for field, value in required_map.items() if not value]
            if missing:
                messagebox.showerror("Error", f"Please fill: {', '.join(missing)}.", parent=form)
                return

            # Normalize optional fields
            phone = phone or None
            address = address or None

            # Normalize date of birth: accept DD-MM-YYYY and convert; allow empty -> NULL
            if dob:
                if len(dob) == 10 and dob[2] == '-' and dob[5] == '-':
                    # DD-MM-YYYY -> YYYY-MM-DD
                    try:
                        d, m, y = dob.split('-')
                        int(d); int(m); int(y)
                        dob = f"{y}-{m.zfill(2)}-{d.zfill(2)}"
                    except Exception:
                        messagebox.showerror("Error", "Invalid date of birth. Use YYYY-MM-DD or DD-MM-YYYY.", parent=form)
                        return
                elif len(dob) == 10 and dob[4] == '-' and dob[7] == '-':
                    # Looks like YYYY-MM-DD, accept as is
                    pass
                else:
                    messagebox.showerror("Error", "Invalid date of birth. Use YYYY-MM-DD or DD-MM-YYYY.", parent=form)
                    return
            else:
                dob = None

            # Duplicate checks aligned with DB constraints (users.username UNIQUE, students.email UNIQUE)
            try:
                existing_user = db.check_username_exists(username)
            except Exception:
                existing_user = db.execute_query("SELECT user_id FROM users WHERE username = %s", (username,))
            if existing_user:
                messagebox.showerror("Error", "Username already exists. Please choose another username.", parent=form)
                return

            if email:
                existing_email = db.execute_query("SELECT student_id FROM students WHERE email = %s", (email,))
                if existing_email:
                    messagebox.showerror("Error", "Email already exists. Please use a different email.", parent=form)
                    return

            # Persist to DB
            ok = db.add_student(username, password, fullname, email, phone, dob, gender, address, status)
            if ok:
                messagebox.showinfo("Success", "Student added successfully.", parent=form)
                # refresh table and dashboard
                self.load_students()
                self.load_dashboard_data()
                form.destroy()
            else:
                messagebox.showerror("Error", "Failed to add student. Username or email may already exist.", parent=form)

        tk.Button(form, text="Add Student", font=("Arial", 12, "bold"), bg="#27ae60", fg="white", command=submit).grid(row=row, column=0, columnspan=2, pady=20)

        form.transient(self.root)
        form.grab_set()
        self.root.wait_window(form)
    
    def edit_student(self):
        """Edit selected student"""
        selection = self.students_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a student to edit")
            return
        item = self.students_tree.item(selection[0])
        values = item['values']
        form = tk.Toplevel(self.root)
        form.title("Edit Student")
        form.geometry("520x520")
        form.resizable(False, False)

        # Fetch additional fields not in the table
        student_id = values[0]
        current = db.execute_query(
            "SELECT fullname, email, phone, date_of_birth, gender, address, status FROM students WHERE student_id = %s",
            (student_id,)
        )
        cur = current[0] if current else {}

        fullname_value = cur.get('fullname', values[1])
        email_value = cur.get('email', values[2])
        phone_value = cur.get('phone', values[3])
        # Format DOB to YYYY-MM-DD if it's a date object
        dob_value = cur.get('date_of_birth')
        if hasattr(dob_value, 'strftime'):
            dob_value = dob_value.strftime('%Y-%m-%d')
        dob_value = dob_value or ''
        gender_var = tk.StringVar(value=cur.get('gender', values[4]))
        address_value = cur.get('address', '') or ''
        status_var = tk.StringVar(value=cur.get('status', values[5]))

        row = 0
        def add_row(label_text, widget):
            tk.Label(form, text=label_text, font=("Arial", 11)).grid(row=row, column=0, padx=20, pady=8, sticky="w")
            widget.grid(row=row, column=1, padx=20, pady=8, sticky="w")
            return 1

        fullname_entry = tk.Entry(form, font=("Arial", 11))
        fullname_entry.insert(0, str(fullname_value or ""))
        row += add_row("Full Name", fullname_entry)
        email_entry = tk.Entry(form, font=("Arial", 11))
        email_entry.insert(0, str(email_value or ""))
        row += add_row("Email", email_entry)
        phone_entry = tk.Entry(form, font=("Arial", 11))
        phone_entry.insert(0, str(phone_value or ""))
        row += add_row("Phone", phone_entry)
        dob_entry = tk.Entry(form, font=("Arial", 11))
        dob_entry.insert(0, str(dob_value))
        row += add_row("Date of Birth (YYYY-MM-DD)", dob_entry)

        # Gender radios
        tk.Label(form, text="Gender", font=("Arial", 11)).grid(row=row, column=0, padx=20, pady=8, sticky="w")
        gender_frame = tk.Frame(form)
        gender_frame.grid(row=row, column=1, padx=20, pady=8, sticky="w")
        tk.Radiobutton(gender_frame, text="Male", variable=gender_var, value="Male").pack(side="left")
        tk.Radiobutton(gender_frame, text="Female", variable=gender_var, value="Female").pack(side="left")
        tk.Radiobutton(gender_frame, text="Other", variable=gender_var, value="Other").pack(side="left")
        row += 1

        address_entry = tk.Entry(form, font=("Arial", 11))
        address_entry.insert(0, str(address_value))
        row += add_row("Address", address_entry)

        # Status combobox
        tk.Label(form, text="Status", font=("Arial", 11)).grid(row=row, column=0, padx=20, pady=8, sticky="w")
        status_combo = ttk.Combobox(form, textvariable=status_var, values=["Active", "Inactive", "Graduated"], state="readonly", width=18)
        status_combo.grid(row=row, column=1, padx=20, pady=8, sticky="w")
        row += 1

        def submit():
            full_name = fullname_entry.get().strip()
            email = email_entry.get().strip()
            phone = phone_entry.get().strip()
            dob = dob_entry.get().strip()
            gender = gender_var.get().strip() or "Male"
            address = address_entry.get().strip() or None
            status = status_var.get().strip()

            if not full_name or not email:
                messagebox.showerror("Error", "Full name and email are required.", parent=form)
                return

            # Normalize date input
            if dob:
                if len(dob) == 10 and dob[2] == '-' and dob[5] == '-':
                    try:
                        d, m, y = dob.split('-')
                        int(d); int(m); int(y)
                        dob = f"{y}-{m.zfill(2)}-{d.zfill(2)}"
                    except Exception:
                        messagebox.showerror("Error", "Invalid date of birth. Use YYYY-MM-DD or DD-MM-YYYY.", parent=form)
                        return
                elif len(dob) == 10 and dob[4] == '-' and dob[7] == '-':
                    pass
                else:
                    messagebox.showerror("Error", "Invalid date of birth. Use YYYY-MM-DD or DD-MM-YYYY.", parent=form)
                    return
            else:
                dob = None

            if db.update_student(student_id, full_name, email, phone or None, dob, gender, address, status):
                messagebox.showinfo("Success", "Student updated successfully.", parent=form)
                self.load_students()
                form.destroy()
            else:
                messagebox.showerror("Error", "Failed to update student.", parent=form)

        tk.Button(form, text="Update Student", font=("Arial", 12, "bold"), bg="#3498db", fg="white", command=submit).grid(row=row, column=0, columnspan=2, pady=20)

        form.transient(self.root)
        form.grab_set()
        self.root.wait_window(form)
    
    def delete_student(self):
        """Delete selected student"""
        selection = self.students_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a student to delete")
            return
        
        if messagebox.askyesno("Confirm", "Are you sure you want to delete this student?"):
            item = self.students_tree.item(selection[0])
            student_id = item['values'][0]
            
            if db.delete_student(student_id):
                messagebox.showinfo("Success", "Student deleted successfully")
                self.load_students()
                self.load_dashboard_data()
            else:
                messagebox.showerror("Error", "Failed to delete student")
    
    def view_student_marks(self):
        """View marks for selected student in a modal table"""
        selection = self.students_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a student to view marks")
            return
        item = self.students_tree.item(selection[0])
        values = item['values']
        student_id = values[0]
        student_name = values[1]

        # Fetch marks
        marks = db.get_student_marks(student_id) or []

        dialog = tk.Toplevel(self.root)
        dialog.title(f"Marks - {student_name}")
        dialog.geometry("850x500")
        dialog.resizable(True, True)

        container = tk.Frame(dialog, bg="white")
        container.pack(fill="both", expand=True, padx=10, pady=10)

        cols = ("Exam Date", "Subject", "Subject Code", "Teacher", "Marks Obtained", "Total", "Percent")
        tree = ttk.Treeview(container, columns=cols, show='headings', height=16)
        for col in cols:
            tree.heading(col, text=col)
            tree.column(col, width=120)

        vs = ttk.Scrollbar(container, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscrollcommand=vs.set)
        tree.grid(row=0, column=0, sticky="nsew")
        vs.grid(row=0, column=1, sticky="ns")
        container.grid_columnconfigure(0, weight=1)
        container.grid_rowconfigure(0, weight=1)

        # Populate
        for m in marks:
            exam_date = m.get('exam_date')
            if hasattr(exam_date, 'strftime'):
                exam_date = exam_date.strftime('%Y-%m-%d')
            percent = 0
            try:
                if m.get('total_marks'):
                    percent = round((m.get('marks_obtained', 0) / m.get('total_marks')) * 100, 2)
            except Exception:
                percent = 0
            tree.insert('', 'end', values=(
                exam_date or '',
                m.get('subject_name', ''),
                m.get('subject_code', ''),
                m.get('teacher_name', ''),
                m.get('marks_obtained', ''),
                m.get('total_marks', ''),
                f"{percent}%"
            ))

        # Close button
        tk.Button(dialog, text="Close", command=dialog.destroy, bg="#e0e0e0").pack(pady=8)

        dialog.transient(self.root)
        dialog.grab_set()
        self.root.wait_window(dialog)
    
    def add_teacher(self):
        """Add new teacher - persists to DB and refreshes table"""
        form = tk.Toplevel(self.root)
        form.title("Add New Teacher")
        form.geometry("520x520")
        form.resizable(False, False)

        # Form variables
        username_var = tk.StringVar()
        password_var = tk.StringVar()
        fullname_var = tk.StringVar()
        email_var = tk.StringVar()
        phone_var = tk.StringVar()
        department_var = tk.StringVar()
        qualification_var = tk.StringVar()
        status_var = tk.StringVar(value="Active")

        row = 0
        def add_row(label_text, widget):
            tk.Label(form, text=label_text, font=("Arial", 11)).grid(row=row, column=0, padx=20, pady=8, sticky="w")
            widget.grid(row=row, column=1, padx=20, pady=8, sticky="w")
            return 1

        # Keep Entry refs
        username_entry = tk.Entry(form, textvariable=username_var, font=("Arial", 11))
        password_entry = tk.Entry(form, textvariable=password_var, font=("Arial", 11), show='*')
        fullname_entry = tk.Entry(form, textvariable=fullname_var, font=("Arial", 11))
        email_entry = tk.Entry(form, textvariable=email_var, font=("Arial", 11))
        phone_entry = tk.Entry(form, textvariable=phone_var, font=("Arial", 11))
        department_entry = tk.Entry(form, textvariable=department_var, font=("Arial", 11))
        qualification_entry = tk.Entry(form, textvariable=qualification_var, font=("Arial", 11))

        row += add_row("Username", username_entry)
        row += add_row("Password", password_entry)
        row += add_row("Full Name", fullname_entry)
        row += add_row("Email", email_entry)
        row += add_row("Phone", phone_entry)
        row += add_row("Department", department_entry)
        row += add_row("Qualification", qualification_entry)

        # Status combobox
        tk.Label(form, text="Status", font=("Arial", 11)).grid(row=row, column=0, padx=20, pady=8, sticky="w")
        status_combo = ttk.Combobox(form, textvariable=status_var, values=["Active", "Inactive"], state="readonly", width=18)
        status_combo.grid(row=row, column=1, padx=20, pady=8, sticky="w")
        row += 1

        def submit():
            username = username_entry.get().strip()
            password = password_entry.get().strip()
            fullname = fullname_entry.get().strip()
            email = email_entry.get().strip()
            phone = phone_entry.get().strip()
            department = department_entry.get().strip()
            qualification = qualification_entry.get().strip()
            status = status_var.get().strip()

            # Required fields
            required_map = {
                "username": username,
                "password": password,
                "full name": fullname,
                "email": email,
            }
            missing = [field for field, value in required_map.items() if not value]
            if missing:
                messagebox.showerror("Error", f"Please fill: {', '.join(missing)}.", parent=form)
                return

            # Normalize optionals
            phone = phone or None
            department = department or None
            qualification = qualification or None

            # Duplicates
            try:
                existing_user = db.check_username_exists(username)
            except Exception:
                existing_user = db.execute_query("SELECT user_id FROM users WHERE username = %s", (username,))
            if existing_user:
                messagebox.showerror("Error", "Username already exists. Please choose another username.", parent=form)
                return

            if email:
                existing_email = db.execute_query("SELECT teacher_id FROM teachers WHERE email = %s", (email,))
                if existing_email:
                    messagebox.showerror("Error", "Email already exists. Please use a different email.", parent=form)
                    return

            ok = db.add_teacher(username, password, fullname, email, phone, department, qualification, status)
            if ok:
                messagebox.showinfo("Success", "Teacher added successfully.", parent=form)
                self.load_teachers()
                self.load_dashboard_data()
                form.destroy()
            else:
                messagebox.showerror("Error", "Failed to add teacher. Username or email may already exist.", parent=form)

        tk.Button(form, text="Add Teacher", font=("Arial", 12, "bold"), bg="#27ae60", fg="white", command=submit).grid(row=row, column=0, columnspan=2, pady=20)

        form.transient(self.root)
        form.grab_set()
        self.root.wait_window(form)
    
    def edit_teacher(self):
        """Edit selected teacher"""
        selection = self.teachers_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a teacher to edit")
            return
        item = self.teachers_tree.item(selection[0])
        values = item['values']
        form = tk.Toplevel(self.root)
        form.title("Edit Teacher")
        form.geometry("520x460")
        form.resizable(False, False)

        # Pull fresh row from DB in case table is stale
        teacher_id = values[0]
        current = db.execute_query(
            "SELECT fullname, email, phone, department, qualification, status FROM teachers WHERE teacher_id = %s",
            (teacher_id,)
        )
        cur = current[0] if current else {}

        fullname_value = cur.get('fullname', values[1])
        email_value = cur.get('email', values[2])
        phone_value = cur.get('phone', values[3])
        department_value = cur.get('department', values[4])
        qualification_value = cur.get('qualification', values[5])
        status_var = tk.StringVar(value=cur.get('status', values[6]))

        row = 0
        def add_row(label_text, widget):
            tk.Label(form, text=label_text, font=("Arial", 11)).grid(row=row, column=0, padx=20, pady=8, sticky="w")
            widget.grid(row=row, column=1, padx=20, pady=8, sticky="w")
            return 1

        fullname_entry = tk.Entry(form, font=("Arial", 11))
        fullname_entry.insert(0, str(fullname_value or ""))
        row += add_row("Full Name", fullname_entry)

        email_entry = tk.Entry(form, font=("Arial", 11))
        email_entry.insert(0, str(email_value or ""))
        row += add_row("Email", email_entry)

        phone_entry = tk.Entry(form, font=("Arial", 11))
        phone_entry.insert(0, str(phone_value or ""))
        row += add_row("Phone", phone_entry)

        dept_entry = tk.Entry(form, font=("Arial", 11))
        dept_entry.insert(0, str(department_value or ""))
        row += add_row("Department", dept_entry)

        qual_entry = tk.Entry(form, font=("Arial", 11))
        qual_entry.insert(0, str(qualification_value or ""))
        row += add_row("Qualification", qual_entry)

        tk.Label(form, text="Status", font=("Arial", 11)).grid(row=row, column=0, padx=20, pady=8, sticky="w")
        status_combo = ttk.Combobox(form, textvariable=status_var, values=["Active", "Inactive"], state="readonly", width=18)
        status_combo.grid(row=row, column=1, padx=20, pady=8, sticky="w")
        row += 1

        def submit():
            teacher_id = values[0]
            full_name = fullname_entry.get().strip()
            email = email_entry.get().strip()
            phone = phone_entry.get().strip()
            department = dept_entry.get().strip() or None
            qualification = qual_entry.get().strip() or None
            status = status_var.get().strip()
            if not full_name or not email or not phone:
                messagebox.showerror("Error", "Full name, email, and phone are required.", parent=form)
                return
            if db.update_teacher(teacher_id, full_name, email, phone, department, qualification, status):
                messagebox.showinfo("Success", "Teacher updated successfully.", parent=form)
                self.load_teachers()
                form.destroy()
            else:
                messagebox.showerror("Error", "Failed to update teacher.", parent=form)

        tk.Button(form, text="Update Teacher", font=("Arial", 12, "bold"), bg="#3498db", fg="white", command=submit).grid(row=row, column=0, columnspan=2, pady=20)

        form.transient(self.root)
        form.grab_set()
        self.root.wait_window(form)
    
    def delete_teacher(self):
        """Delete selected teacher"""
        selection = self.teachers_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a teacher to delete")
            return
        
        if messagebox.askyesno("Confirm", "Are you sure you want to delete this teacher?"):
            item = self.teachers_tree.item(selection[0])
            teacher_id = item['values'][0]
            
            if db.delete_teacher(teacher_id):
                messagebox.showinfo("Success", "Teacher deleted successfully")
                self.load_teachers()
                self.load_dashboard_data()
            else:
                messagebox.showerror("Error", "Failed to delete teacher")
    
    def logout(self):
        """Logout and return to login"""
        if messagebox.askyesno("Logout", "Are you sure you want to logout?"):
            # Clean up event bindings
            self.root.unbind_all("<MouseWheel>")
            self.root.unbind_all("<Key>")
            self.root.destroy()
            # Relaunch a fresh login window in a new process to avoid Tk re-init and circular imports
            try:
                login_path = os.path.join(os.path.dirname(__file__), 'login.py')
                subprocess.Popen([sys.executable, login_path])
            except Exception as e:
                messagebox.showerror("Error", f"Failed to relaunch login: {e}")
    
    def on_closing(self):
        """Handle window closing"""
        # Clean up event bindings
        self.root.unbind_all("<MouseWheel>")
        self.root.unbind_all("<Key>")
        self.root.destroy()
    
    def load_students(self):
        """Load students data"""
        # Clear existing items
        for item in self.students_tree.get_children():
            self.students_tree.delete(item)
        
        students = db.get_all_students()
        for student in students:
            self.students_tree.insert('', 'end', values=(
                student['student_id'],
                student['fullname'],
                student['email'],
                student['phone'],
                student['gender'],
                student['status'],
                student['enrollment_date']
            ))
    
    def load_teachers(self):
        """Load teachers data"""
        # Clear existing items
        for item in self.teachers_tree.get_children():
            self.teachers_tree.delete(item)
        
        teachers = db.get_all_teachers()
        for teacher in teachers:
            self.teachers_tree.insert('', 'end', values=(
                teacher['teacher_id'],
                teacher['fullname'],
                teacher['email'],
                teacher['phone'],
                teacher['department'],
                teacher['qualification'],
                teacher['status']
            ))
    
    def filter_students(self, *args):
        """Filter students based on search"""
        search_term = self.student_search_var.get().lower()
        students = db.get_all_students()
        
        # Clear existing items
        for item in self.students_tree.get_children():
            self.students_tree.delete(item)
        
        # Filter and insert
        for student in students:
            if (search_term in student['fullname'].lower() or 
                search_term in student['email'].lower()):
                self.students_tree.insert('', 'end', values=(
                    student['student_id'],
                    student['fullname'],
                    student['email'],
                    student['phone'],
                    student['gender'],
                    student['status'],
                    student['enrollment_date']
                ))
    
    def filter_teachers(self, *args):
        """Filter teachers based on search"""
        search_term = self.teacher_search_var.get().lower()
        teachers = db.get_all_teachers()
        
        # Clear existing items
        for item in self.teachers_tree.get_children():
            self.teachers_tree.delete(item)
        
        # Filter and insert
        for teacher in teachers:
            if (search_term in teacher['fullname'].lower() or 
                search_term in teacher['email'].lower() or
                search_term in teacher['department'].lower()):
                self.teachers_tree.insert('', 'end', values=(
                    teacher['teacher_id'],
                    teacher['fullname'],
                    teacher['email'],
                    teacher['phone'],
                    teacher['department'],
                    teacher['qualification'],
                    teacher['status']
                ))
    
    
