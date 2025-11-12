#!/usr/bin/env python3
"""
Student Performance Dashboard - Modern UI matching the design image
"""

import tkinter as tk
from tkinter import ttk, messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.patches as patches
from matplotlib.patches import Wedge
import numpy as np
from database import db

class PerformanceDashboard:
    def __init__(self, user_type="teacher", user_profile=None):
        self.user_type = user_type
        self.user_profile = user_profile
        self.root = tk.Tk()
        self.root.title("Student Performance Dashboard")
        self.root.geometry("1400x900")
        self.root.state('zoomed')  # Maximize window
        
        # Configure style
        self.setup_styles()
        
        # Create main container
        self.main_container = ttk.Frame(self.root)
        self.main_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Create header
        self.create_header()
        
        # Create filters section
        self.create_filters()
        
        # Create metrics card
        self.create_metrics_card()
        
        # Create main content area
        self.create_main_content()
        
        # Load initial data
        self.load_dashboard_data()
    
    def setup_styles(self):
        """Setup custom styles for the dashboard"""
        style = ttk.Style()
        
        # Configure colors to match the design
        style.configure('Header.TLabel', font=('Arial', 24, 'bold'), foreground='#2c3e50')
        style.configure('Card.TFrame', relief='solid', borderwidth=1)
        style.configure('Metric.TLabel', font=('Arial', 14, 'bold'), foreground='#34495e')
        style.configure('Filter.TLabel', font=('Arial', 12), foreground='#7f8c8d')
        
    def create_header(self):
        """Create header with title and action buttons"""
        header_frame = ttk.Frame(self.main_container)
        header_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Title
        title_label = ttk.Label(header_frame, text="Student Performance Dashboard", 
                               style='Header.TLabel')
        title_label.pack(side=tk.LEFT)
        
        # Action buttons (right side)
        actions_frame = ttk.Frame(header_frame)
        actions_frame.pack(side=tk.RIGHT)
        
        # Add refresh, link, expand, and menu buttons (as placeholders)
        ttk.Button(actions_frame, text="🔄", width=3).pack(side=tk.LEFT, padx=2)
        ttk.Button(actions_frame, text="🔗", width=3).pack(side=tk.LEFT, padx=2)
        ttk.Button(actions_frame, text="⛶", width=3).pack(side=tk.LEFT, padx=2)
        ttk.Button(actions_frame, text="⋮", width=3).pack(side=tk.LEFT, padx=2)
        
        # User info and logout
        if self.user_profile:
            user_frame = ttk.Frame(header_frame)
            user_frame.pack(side=tk.RIGHT, padx=(20, 0))
            
            user_label = ttk.Label(user_frame, text=f"Welcome, {self.user_profile.get('fullname', 'User')}", 
                                  font=("Arial", 12))
            user_label.pack(side=tk.LEFT, padx=(0, 10))
            
            logout_button = ttk.Button(user_frame, text="Logout", command=self.logout)
            logout_button.pack(side=tk.RIGHT)
    
    def create_filters(self):
        """Create filter section with year and grade dropdowns"""
        filters_frame = ttk.Frame(self.main_container)
        filters_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Year filter
        year_frame = ttk.Frame(filters_frame)
        year_frame.pack(side=tk.LEFT, padx=(0, 20))
        
        ttk.Label(year_frame, text="Select Year", style='Filter.TLabel').pack(anchor=tk.W)
        self.year_var = tk.StringVar(value="All")
        year_combo = ttk.Combobox(year_frame, textvariable=self.year_var, 
                                 values=["All", "2024", "2023", "2022"], 
                                 state="readonly", width=15)
        year_combo.pack(anchor=tk.W, pady=(5, 0))
        
        # Grade filter
        grade_frame = ttk.Frame(filters_frame)
        grade_frame.pack(side=tk.LEFT)
        
        ttk.Label(grade_frame, text="Select Grade", style='Filter.TLabel').pack(anchor=tk.W)
        self.grade_var = tk.StringVar(value="All")
        grade_combo = ttk.Combobox(grade_frame, textvariable=self.grade_var,
                                  values=["All", "Grade 1", "Grade 2", "Grade 3", "Grade 4", "Grade 5"],
                                  state="readonly", width=15)
        grade_combo.pack(anchor=tk.W, pady=(5, 0))
        
        # Bind filter changes
        year_combo.bind('<<ComboboxSelected>>', self.on_filter_change)
        grade_combo.bind('<<ComboboxSelected>>', self.on_filter_change)
    
    def create_metrics_card(self):
        """Create key metrics card showing total students"""
        metrics_frame = ttk.Frame(self.main_container)
        metrics_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Create card frame
        card_frame = ttk.Frame(metrics_frame, style='Card.TFrame')
        card_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Student icon and count
        content_frame = ttk.Frame(card_frame)
        content_frame.pack(fill=tk.X, padx=20, pady=15)
        
        # Student icon (using text as placeholder)
        icon_label = ttk.Label(content_frame, text="🎓", font=("Arial", 24))
        icon_label.pack(side=tk.LEFT, padx=(0, 15))
        
        # Student count
        count_frame = ttk.Frame(content_frame)
        count_frame.pack(side=tk.LEFT)
        
        ttk.Label(count_frame, text="Students", style='Filter.TLabel').pack(anchor=tk.W)
        self.student_count_label = ttk.Label(count_frame, text="300", 
                                           style='Metric.TLabel', font=("Arial", 20, "bold"))
        self.student_count_label.pack(anchor=tk.W)
    
    def create_main_content(self):
        """Create main content area with charts"""
        content_frame = ttk.Frame(self.main_container)
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        # Left column
        left_frame = ttk.Frame(content_frame)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        # Students by Grade and Gender (Donut Chart)
        self.create_donut_chart(left_frame)
        
        # Examination Results by Branch (Grouped Bar Chart)
        self.create_exam_results_chart(left_frame)
        
        # Middle column
        middle_frame = ttk.Frame(content_frame)
        middle_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10)
        
        # Student Participation Rate by Branch (Horizontal Bar Chart)
        self.create_participation_chart(middle_frame)
        
        # Right column
        right_frame = ttk.Frame(content_frame)
        right_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(10, 0))
        
        # Average Subject Score (Gauge Charts)
        self.create_gauge_charts(right_frame)
    
    def create_donut_chart(self, parent):
        """Create donut chart for students by grade and gender"""
        chart_frame = ttk.LabelFrame(parent, text="Students by Grade and Gender", padding="10")
        chart_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Create matplotlib figure
        fig, ax = plt.subplots(figsize=(8, 6))
        fig.patch.set_facecolor('white')
        
        # Sample data matching the image
        grades = ['Grade 1', 'Grade 2', 'Grade 3', 'Grade 4', 'Grade 5']
        sizes = [22.67, 20.33, 21.33, 14.67, 21.0]
        colors = ['#FFD700', '#FF8C00', '#FF4500', '#FF6347', '#DC143C']
        
        # Create donut chart
        wedges, texts, autotexts = ax.pie(sizes, labels=grades, colors=colors, autopct='%1.1f%%',
                                         startangle=90, pctdistance=0.85)
        
        # Create donut hole
        centre_circle = plt.Circle((0,0), 0.70, fc='white')
        ax.add_artist(centre_circle)
        
        # Style the chart
        ax.set_title('Drill down to show the number of students by gender.', 
                    fontsize=10, pad=20, style='italic')
        
        # Embed in tkinter
        canvas = FigureCanvasTkAgg(fig, chart_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
    
    def create_exam_results_chart(self, parent):
        """Create grouped bar chart for examination results"""
        chart_frame = ttk.LabelFrame(parent, text="Examination Results by Branch", padding="10")
        chart_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create matplotlib figure
        fig, ax = plt.subplots(figsize=(8, 6))
        fig.patch.set_facecolor('white')
        
        # Sample data matching the image
        subjects = ['Phys. Ed', 'Arts', 'English', 'Science', 'Maths']
        pass_scores = [255, 205, 200, 195, 180]
        fail_scores = [20, 70, 75, 70, 90]
        not_attended = [15, 15, 15, 15, 15]
        
        x = np.arange(len(subjects))
        width = 0.25
        
        # Create bars
        bars1 = ax.bar(x - width, pass_scores, width, label='Pass', color='#FFD700')
        bars2 = ax.bar(x, fail_scores, width, label='Fail', color='#DC143C')
        bars3 = ax.bar(x + width, not_attended, width, label='Not attended', color='#8B4513')
        
        # Style the chart
        ax.set_xlabel('Subjects')
        ax.set_ylabel('Count')
        ax.set_title('Examination Results by Branch')
        ax.set_xticks(x)
        ax.set_xticklabels(subjects)
        ax.legend()
        ax.set_ylim(0, 280)
        
        plt.tight_layout()
        
        # Embed in tkinter
        canvas = FigureCanvasTkAgg(fig, chart_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
    
    def create_participation_chart(self, parent):
        """Create horizontal bar chart for participation rates"""
        chart_frame = ttk.LabelFrame(parent, text="Student Participation Rate by Branch", padding="10")
        chart_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create matplotlib figure
        fig, ax = plt.subplots(figsize=(6, 8))
        fig.patch.set_facecolor('white')
        
        # Sample data matching the image
        subjects = ['English', 'Arts', 'Maths', 'Phy. Ed', 'Science']
        participation = [89, 87.67, 87.33, 85.33, 82.33]
        colors = ['#FFD700'] * len(subjects)
        
        # Create horizontal bar chart
        bars = ax.barh(subjects, participation, color=colors)
        
        # Style the chart
        ax.set_xlabel('Participation Rate (%)')
        ax.set_title('Student Participation Rate by Branch')
        ax.set_xlim(0, 100)
        
        # Add value labels on bars
        for i, (bar, value) in enumerate(zip(bars, participation)):
            width = bar.get_width()
            ax.text(width + 1, bar.get_y() + bar.get_height()/2, 
                   f'{value}%', ha='left', va='center')
        
        plt.tight_layout()
        
        # Embed in tkinter
        canvas = FigureCanvasTkAgg(fig, chart_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
    
    def create_gauge_charts(self, parent):
        """Create gauge charts for average subject scores"""
        chart_frame = ttk.LabelFrame(parent, text="Avg. Subject Score", padding="10")
        chart_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create matplotlib figure with subplots
        fig, axes = plt.subplots(2, 3, figsize=(8, 6))
        fig.patch.set_facecolor('white')
        
        # Sample data matching the image
        subjects = ['Arts', 'English', 'Maths', 'Phy. Ed', 'Science']
        scores = [84.37, 84.05, 81.86, 84.76, 79.36]
        colors = ['#FFD700', '#DC143C', '#FF4500', '#8B4513', '#FF8C00']
        
        # Flatten axes for easier iteration
        axes_flat = axes.flatten()
        
        for i, (subject, score, color) in enumerate(zip(subjects, scores, colors)):
            ax = axes_flat[i]
            
            # Create gauge chart
            self.create_gauge(ax, score, subject, color)
        
        # Hide the last subplot
        axes_flat[5].set_visible(False)
        
        plt.tight_layout()
        
        # Embed in tkinter
        canvas = FigureCanvasTkAgg(fig, chart_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
    
    def create_gauge(self, ax, value, title, color):
        """Create a single gauge chart"""
        # Calculate angles
        theta = np.linspace(0, np.pi, 100)
        radius = 1
        
        # Background circle
        ax.plot(radius * np.cos(theta), radius * np.sin(theta), 'k-', linewidth=2)
        
        # Filled portion
        filled_theta = np.linspace(0, np.pi * (value / 100), 100)
        ax.fill_between(radius * np.cos(filled_theta), 0, radius * np.sin(filled_theta), 
                       color=color, alpha=0.7)
        
        # Add score text
        ax.text(0, 0, f'{value:.2f}', ha='center', va='center', fontsize=10, fontweight='bold')
        
        # Add title
        ax.text(0, -1.3, title, ha='center', va='center', fontsize=8)
        
        # Set equal aspect ratio and remove axes
        ax.set_aspect('equal')
        ax.set_xlim(-1.5, 1.5)
        ax.set_ylim(-1.5, 1.5)
        ax.axis('off')
    
    def load_dashboard_data(self):
        """Load dashboard data from database"""
        try:
            # Get system statistics
            stats = db.get_system_stats()
            
            # Update student count
            if stats and 'active_students' in stats:
                try:
                    self.student_count_label.config(text=str(int(stats['active_students'])))
                except Exception:
                    self.student_count_label.config(text=str(stats['active_students']))
            
            # In a real implementation, you would:
            # 1. Filter data based on year and grade selections
            # 2. Update all charts with real data
            # 3. Handle data refresh when filters change
            
        except Exception as e:
            print(f"Error loading dashboard data: {e}")
    
    def on_filter_change(self, event=None):
        """Handle filter changes"""
        # In a real implementation, this would refresh the dashboard data
        # based on the selected year and grade filters
        print(f"Filters changed - Year: {self.year_var.get()}, Grade: {self.grade_var.get()}")
        self.load_dashboard_data()
    
    def logout(self):
        """Logout and return to login"""
        if messagebox.askyesno("Logout", "Are you sure you want to logout?"):
            self.root.destroy()
            import login
            login.LoginWindow().run()
    
    def run(self):
        """Run the dashboard"""
        self.root.mainloop()

# Demo function to show the dashboard
def demo_dashboard():
    """Demo function to show the dashboard without login"""
    dashboard = PerformanceDashboard()
    dashboard.run()

if __name__ == "__main__":
    demo_dashboard()
