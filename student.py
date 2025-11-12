#!/usr/bin/env python3
"""
Student Dashboard for Student Performance Monitoring System
"""

import tkinter as tk
from tkinter import ttk, messagebox
from database import db

# Try to import matplotlib, but make it optional
try:
    import matplotlib.pyplot as plt
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    import matplotlib
    matplotlib.use('TkAgg')
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False
    print("⚠️ Matplotlib not available. Charts will be disabled.")

class StudentDashboard:
    def __init__(self, user, student_profile):
        self.user = user
        self.student_profile = student_profile
        self.root = tk.Tk()
        self.root.title("Student Performance Dashboard")
        self.root.geometry("1400x900")
        self.root.state('zoomed')  # Maximize window
        
        # Set modern background color
        self.root.configure(bg='#f5f5f5')
        
        # Configure grid weights for root window
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_rowconfigure(0, weight=1)
        
        # Configure style
        self.setup_styles()
        
        # Create scrollable area (prevents content clipping and enables scrolling)
        self._canvas = tk.Canvas(self.root, bg='#f5f5f5', highlightthickness=0)
        self._vsb = ttk.Scrollbar(self.root, orient='vertical', command=self._canvas.yview)
        self._canvas.configure(yscrollcommand=self._vsb.set)
        self._canvas.grid(row=0, column=0, sticky="nsew")
        self._vsb.grid(row=0, column=1, sticky="ns")

        # Inner scrollable frame
        self._scroll_frame = ttk.Frame(self._canvas, style='Main.TFrame')
        self._canvas.create_window((0, 0), window=self._scroll_frame, anchor='nw')
        self._scroll_frame.bind(
            '<Configure>',
            lambda e: self._canvas.configure(scrollregion=self._canvas.bbox('all'))
        )
        # Smooth mouse wheel scrolling (Windows)
        self._canvas.bind_all('<MouseWheel>', lambda e: self._canvas.yview_scroll(int(-1 * (e.delta / 120)), 'units'))

        # Create main container with modern styling inside scrollable frame
        self.main_container = ttk.Frame(self._scroll_frame, style='Main.TFrame')
        self.main_container.grid(row=0, column=0, sticky="nsew", padx=15, pady=15)
        
        # Configure grid weights for main container
        self.main_container.grid_columnconfigure(0, weight=1)
        self.main_container.grid_rowconfigure(0, weight=0)  # Header row
        self.main_container.grid_rowconfigure(1, weight=0)  # Filters row
        self.main_container.grid_rowconfigure(2, weight=1)  # Main content row
        
        # Create header
        self.create_header()
        
        # Create filters section
        self.create_filters()
        
        # Create main content area
        self.create_main_content()
        
        # Load initial data
        self.load_dashboard_data()
    
    def setup_styles(self):
        """Setup modern styles for the dashboard"""
        style = ttk.Style()
        
        # Configure modern color scheme
        style.configure('Main.TFrame', background='#f5f5f5')
        style.configure('Header.TFrame', background='#ffffff', relief='solid', borderwidth=1)
        style.configure('Card.TFrame', background='#ffffff', relief='solid', borderwidth=1)
        style.configure('Header.TLabel', font=('Arial', 24, 'bold'), foreground='#2c3e50', background='#ffffff')
        style.configure('Metric.TLabel', font=('Arial', 14, 'bold'), foreground='#34495e', background='#ffffff')
        style.configure('Filter.TLabel', font=('Arial', 12), foreground='#7f8c8d', background='#ffffff')
        style.configure('Stats.TLabel', font=('Arial', 10), foreground='#34495e', background='#ffffff')
        style.configure('StatsValue.TLabel', font=('Arial', 16, 'bold'), foreground='#2c3e50', background='#ffffff')
    
    def create_header(self):
        """Create modern header with title and user info using grid layout"""
        header_frame = ttk.Frame(self.main_container, style='Header.TFrame')
        header_frame.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        header_frame.grid_columnconfigure(0, weight=1)
        header_frame.grid_columnconfigure(1, weight=0)
        
        # Title (left side)
        title_label = ttk.Label(header_frame, text="Student Performance Dashboard", 
                               style='Header.TLabel')
        title_label.grid(row=0, column=0, sticky="w", padx=20, pady=15)
        
        # User info and logout (right side)
        user_frame = ttk.Frame(header_frame, style='Header.TFrame')
        user_frame.grid(row=0, column=1, sticky="e", padx=20, pady=15)
        user_frame.grid_columnconfigure(0, weight=0)
        user_frame.grid_columnconfigure(1, weight=0)
        user_frame.grid_columnconfigure(2, weight=0)
        
        user_label = ttk.Label(user_frame, text=f"Welcome, {self.student_profile['fullname']}", 
                              font=("Arial", 12), background='#ffffff')
        user_label.grid(row=0, column=0, padx=(0, 15))

        # CGPA display in header
        self.cgpa_header_label = ttk.Label(user_frame, text="CGPA: --", font=("Arial", 12, 'bold'), background='#ffffff')
        self.cgpa_header_label.grid(row=0, column=1, padx=(0, 15))
        
        logout_button = ttk.Button(user_frame, text="Logout", command=self.logout)
        logout_button.grid(row=0, column=2)
    
    def create_filters(self):
        """Create modern filter section with year and grade dropdowns using grid layout"""
        filters_frame = ttk.Frame(self.main_container, style='Card.TFrame')
        filters_frame.grid(row=1, column=0, sticky="ew", pady=(0, 10))
        filters_frame.grid_columnconfigure(0, weight=0)
        filters_frame.grid_columnconfigure(1, weight=0)
        filters_frame.grid_columnconfigure(2, weight=1)
        
        # Year filter
        year_frame = ttk.Frame(filters_frame, style='Card.TFrame')
        year_frame.grid(row=0, column=0, sticky="w", padx=20, pady=15)
        
        ttk.Label(year_frame, text="Select Year", style='Filter.TLabel').grid(row=0, column=0, sticky="w")
        self.year_var = tk.StringVar(value="All")
        year_combo = ttk.Combobox(year_frame, textvariable=self.year_var, 
                                 values=["All", "2024", "2023", "2022"], 
                                 state="readonly", width=15)
        year_combo.grid(row=1, column=0, sticky="w", pady=(5, 0))
        
        # Grade filter
        grade_frame = ttk.Frame(filters_frame, style='Card.TFrame')
        grade_frame.grid(row=0, column=1, sticky="w", padx=(0, 20), pady=15)
        
        ttk.Label(grade_frame, text="Select Grade", style='Filter.TLabel').grid(row=0, column=0, sticky="w")
        self.grade_var = tk.StringVar(value="All")
        grade_combo = ttk.Combobox(grade_frame, textvariable=self.grade_var,
                                  values=["All", "Grade 1", "Grade 2", "Grade 3", "Grade 4", "Grade 5"],
                                  state="readonly", width=15)
        grade_combo.grid(row=1, column=0, sticky="w", pady=(5, 0))
        
        # Bind filter changes
        year_combo.bind('<<ComboboxSelected>>', self.on_filter_change)
        grade_combo.bind('<<ComboboxSelected>>', self.on_filter_change)
    
    
    def create_main_content(self):
        """Create modern main content area with 2 columns and full-width sections using grid layout"""
        # Configure grid weights for main content
        self.main_container.grid_rowconfigure(2, weight=1)
        
        # Main content container
        content_frame = ttk.Frame(self.main_container, style='Main.TFrame')
        content_frame.grid(row=2, column=0, sticky="nsew")
        content_frame.grid_columnconfigure(0, weight=1)
        content_frame.grid_columnconfigure(1, weight=1)
        content_frame.grid_rowconfigure(0, weight=1)  # Charts row
        content_frame.grid_rowconfigure(1, weight=1)  # Charts row 2
        content_frame.grid_rowconfigure(2, weight=0)  # Recent grades row
        content_frame.grid_rowconfigure(3, weight=0)  # Statistics row
        
        # Top row - 2 charts side by side (balanced columns)
        charts_row = ttk.Frame(content_frame, style='Main.TFrame')
        charts_row.grid(row=0, column=0, columnspan=2, sticky="nsew", pady=(0, 10))
        charts_row.grid_columnconfigure(0, weight=1)
        charts_row.grid_columnconfigure(1, weight=1)
        charts_row.grid_rowconfigure(0, weight=1)
        
        # Left chart - Performance Over Time
        left_chart_frame = ttk.Frame(charts_row, style='Card.TFrame')
        left_chart_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 5))
        self.create_performance_chart(left_chart_frame)
        
        # Right chart - Subject Performance
        right_chart_frame = ttk.Frame(charts_row, style='Card.TFrame')
        right_chart_frame.grid(row=0, column=1, sticky="nsew", padx=(5, 0))
        self.create_subject_chart(right_chart_frame)
        
        # Second row - additional charts (pie and boxplot)
        charts_row2 = ttk.Frame(content_frame, style='Main.TFrame')
        charts_row2.grid(row=1, column=0, columnspan=2, sticky="nsew", pady=(0, 10))
        charts_row2.grid_columnconfigure(0, weight=1)
        charts_row2.grid_columnconfigure(1, weight=1)
        charts_row2.grid_rowconfigure(0, weight=1)

        # Left chart - Grade Distribution Pie
        pie_frame = ttk.Frame(charts_row2, style='Card.TFrame')
        pie_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 5))
        self.create_grade_distribution_pie(pie_frame)

        # Right chart - Subject Score Boxplot
        box_frame = ttk.Frame(charts_row2, style='Card.TFrame')
        box_frame.grid(row=0, column=1, sticky="nsew", padx=(5, 0))
        self.create_subject_boxplot(box_frame)

        # Recent Grades section (full width)
        grades_frame = ttk.Frame(content_frame, style='Card.TFrame')
        grades_frame.grid(row=2, column=0, columnspan=2, sticky="ew", pady=(0, 10))
        grades_frame.grid_columnconfigure(0, weight=1)
        grades_frame.grid_rowconfigure(0, weight=1)
        self.create_grades_summary(grades_frame)
        
        # Performance Statistics section (full width)
        stats_frame = ttk.Frame(content_frame, style='Card.TFrame')
        stats_frame.grid(row=3, column=0, columnspan=2, sticky="ew")
        stats_frame.grid_columnconfigure(0, weight=1)
        stats_frame.grid_rowconfigure(0, weight=1)
        self.create_performance_stats(stats_frame)

    def create_grade_distribution_pie(self, parent):
        """Create grade distribution pie chart using real marks"""
        try:
            import matplotlib.pyplot as plt
            from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
            import numpy as np

            parent.grid_columnconfigure(0, weight=1)
            parent.grid_rowconfigure(0, weight=1)

            chart_frame = ttk.LabelFrame(parent, text="My Grade Distribution", padding="10")
            chart_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
            chart_frame.grid_columnconfigure(0, weight=1)
            chart_frame.grid_rowconfigure(0, weight=1)

            fig, ax = plt.subplots(figsize=(6.5, 3.8))
            fig.patch.set_facecolor('white')

            marks = db.get_student_marks(self.student_profile['student_id'])

            if marks:
                percentages = [
                    (float(m['marks_obtained']) / float(m['total_marks'])) * 100 if m['total_marks'] else 0.0
                    for m in marks
                ]
                grades = [self.calculate_grade(p) for p in percentages]
                order = ['A+', 'A', 'B', 'C', 'D', 'F']
                counts = [grades.count(g) for g in order]
                labels = [f"{g} ({c})" for g, c in zip(order, counts)]
                colors = ['#2ecc71', '#27ae60', '#3498db', '#f1c40f', '#e67e22', '#e74c3c']

                # Avoid all-zero data
                if sum(counts) > 0:
                    wedges, texts, autotexts = ax.pie(counts, labels=labels, autopct='%1.0f%%',
                                                      startangle=90, colors=colors, pctdistance=0.8)
                    centre_circle = plt.Circle((0,0), 0.55, fc='white')
                    ax.add_artist(centre_circle)
                    ax.set_title('Grade Distribution', fontsize=12, pad=10)
                else:
                    ax.text(0.5, 0.5, 'No data', ha='center', va='center', transform=ax.transAxes)
            else:
                ax.text(0.5, 0.5, 'No data available', ha='center', va='center', transform=ax.transAxes)

            canvas = FigureCanvasTkAgg(fig, chart_frame)
            canvas.draw()
            canvas.get_tk_widget().grid(row=0, column=0, sticky="nsew")

        except ImportError:
            ttk.Label(parent, text="Matplotlib not available for charts", 
                     font=("Arial", 12)).grid(row=0, column=0, sticky="nsew")

    def create_subject_boxplot(self, parent):
        """Create subject-wise bar chart (attempts per subject)"""
        try:
            import matplotlib.pyplot as plt
            from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
            import numpy as np

            parent.grid_columnconfigure(0, weight=1)
            parent.grid_rowconfigure(0, weight=1)

            chart_frame = ttk.LabelFrame(parent, text="Attempts per Subject (Bar)", padding="10")
            chart_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
            chart_frame.grid_columnconfigure(0, weight=1)
            chart_frame.grid_rowconfigure(0, weight=1)

            fig, ax = plt.subplots(figsize=(6.5, 3.8))
            fig.patch.set_facecolor('white')

            marks = db.get_student_marks(self.student_profile['student_id'])

            if marks:
                # Count attempts per subject
                counts = {}
                for m in marks:
                    subj = str(m['subject_name'])
                    counts[subj] = counts.get(subj, 0) + 1

                items = sorted(counts.items(), key=lambda kv: kv[0])[:10]
                labels = [k for k, _ in items]
                values = [v for _, v in items]

                if values:
                    colors = ['#2E86AB', '#27ae60', '#f39c12', '#e74c3c', '#9b59b6']
                    xs = np.arange(len(labels))
                    bars = ax.bar(xs, values, color=[colors[i % len(colors)] for i in range(len(labels))])
                    ax.set_ylabel('Attempts')
                    ax.set_title('Attempts per Subject', fontsize=12)
                    ax.set_xticks(xs)
                    ax.set_xticklabels(labels, rotation=20, ha='right')
                    for b, v in zip(bars, values):
                        ax.text(b.get_x() + b.get_width()/2, b.get_height()+0.05, f"{int(v)}", ha='center', va='bottom', fontsize=9)
                    fig.subplots_adjust(bottom=0.25, left=0.07, right=0.98, top=0.90)
                else:
                    ax.text(0.5, 0.5, 'No data', ha='center', va='center', transform=ax.transAxes)
            else:
                ax.text(0.5, 0.5, 'No data available', ha='center', va='center', transform=ax.transAxes)

            canvas = FigureCanvasTkAgg(fig, chart_frame)
            canvas.draw()
            canvas.get_tk_widget().grid(row=0, column=0, sticky="nsew")

        except ImportError:
            ttk.Label(parent, text="Matplotlib not available for charts", 
                     font=("Arial", 12)).grid(row=0, column=0, sticky="nsew")
    
    def create_performance_chart(self, parent):
        """Create performance over time chart with modern styling"""
        try:
            import matplotlib.pyplot as plt
            from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
            import numpy as np
            
            # Configure parent frame
            parent.grid_columnconfigure(0, weight=1)
            parent.grid_rowconfigure(0, weight=1)
            
            chart_frame = ttk.LabelFrame(parent, text="My Performance Over Time", padding="10")
            chart_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
            chart_frame.grid_columnconfigure(0, weight=1)
            chart_frame.grid_rowconfigure(0, weight=1)
            
            fig, ax = plt.subplots(figsize=(7.0, 3.8))
            fig.patch.set_facecolor('white')
            
            # Get student's marks
            marks = db.get_student_marks(self.student_profile['student_id'])
            
            if marks:
                # Prepare data
                # Normalize dates to short strings
                def _fmt_date(d):
                    return d.strftime('%Y-%m-%d') if hasattr(d, 'strftime') else str(d)
                dates = [_fmt_date(mark['exam_date']) for mark in marks]
                percentages = [
                    (float(mark['marks_obtained']) / float(mark['total_marks'])) * 100 if mark['total_marks'] else 0.0
                    for mark in marks
                ]
                subjects = [mark['subject_name'] for mark in marks]
                
                # Create line plot
                ax.plot(range(len(dates)), percentages, marker='o', linewidth=3, markersize=8, color='#2E86AB')
                ax.set_title('My Performance Over Time', fontsize=14, fontweight='bold')
                ax.set_ylabel('Percentage (%)', fontsize=12)
                ax.set_xlabel('Exams', fontsize=12)
                ax.grid(True, alpha=0.3)
                
                # Set x-axis labels
                ax.set_xticks(range(len(dates)))
                # Limit labels to avoid overlap and use tighter rotation
                labels = [f"{s}\n{d}" for s, d in zip(subjects, dates)]
                ax.set_xticklabels(labels, rotation=25, ha='right', fontsize=9)
                ax.set_ylim(0, 100)
                ax.margins(x=0.02, y=0.1)
                fig.subplots_adjust(bottom=0.32, left=0.08, right=0.98, top=0.90)
                
                # Add average line
                avg_percentage = sum(percentages) / len(percentages)
                ax.axhline(y=avg_percentage, color='red', linestyle='--', alpha=0.7, label=f'Average: {avg_percentage:.1f}%')
                ax.legend()
                
                plt.tight_layout()
            else:
                ax.text(0.5, 0.5, 'No performance data available', 
                       ha='center', va='center', transform=ax.transAxes, fontsize=12)
                ax.set_title('My Performance Over Time', fontsize=14, fontweight='bold')
            
            canvas = FigureCanvasTkAgg(fig, chart_frame)
            canvas.draw()
            canvas.get_tk_widget().grid(row=0, column=0, sticky="nsew")
            
        except ImportError:
            ttk.Label(parent, text="Matplotlib not available for charts", 
                     font=("Arial", 12)).grid(row=0, column=0, sticky="nsew")
    
    def create_subject_chart(self, parent):
        """Create subject performance chart with modern styling"""
        try:
            import matplotlib.pyplot as plt
            from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
            import numpy as np
            
            # Configure parent frame
            parent.grid_columnconfigure(0, weight=1)
            parent.grid_rowconfigure(0, weight=1)
            
            chart_frame = ttk.LabelFrame(parent, text="My Average Performance by Subject", padding="10")
            chart_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
            chart_frame.grid_columnconfigure(0, weight=1)
            chart_frame.grid_rowconfigure(0, weight=1)
            
            fig, ax = plt.subplots(figsize=(7.0, 4.1))
            fig.patch.set_facecolor('white')
            
            # Get student's marks
            marks = db.get_student_marks(self.student_profile['student_id'])
            
            if marks:
                # Group by subject and compute averages
                subject_marks = {}
                for mark in marks:
                    subject = str(mark['subject_name'])
                    percentage = (
                        (float(mark['marks_obtained']) / float(mark['total_marks'])) * 100
                        if mark['total_marks'] else 0.0
                    )
                    subject_marks.setdefault(subject, []).append(percentage)

                items = [
                    (subj, sum(vals) / len(vals)) for subj, vals in subject_marks.items()
                ]
                # Sort by average desc and limit to top 10 to reduce clutter
                items.sort(key=lambda x: x[1], reverse=True)
                items = items[:10]
                # Unpack reversed so highest appears at top in barh
                subjects = [s for s, _ in items][::-1]
                avg_percentages = [v for _, v in items][::-1]

                # Create horizontal bar chart
                colors = ['#2E86AB', '#27ae60', '#f39c12', '#e74c3c', '#9b59b6']
                bars = ax.barh(subjects, avg_percentages, color=colors * ((len(subjects)//len(colors))+1))
                ax.set_title('My Average Performance by Subject', fontsize=14, fontweight='bold')
                ax.set_xlabel('Average Percentage (%)', fontsize=12)
                ax.set_xlim(0, 100)
                ax.margins(y=0.05)
                fig.subplots_adjust(left=0.32, right=0.95, top=0.92, bottom=0.12)
                
                # Add value labels on bars
                for i, (bar, value) in enumerate(zip(bars, avg_percentages)):
                    width = bar.get_width()
                    ax.text(min(width + 1, 98), bar.get_y() + bar.get_height()/2, 
                           f'{value:.1f}%', ha='left', va='center', fontweight='bold', fontsize=9)
                
                plt.tight_layout()
            else:
                ax.text(0.5, 0.5, 'No performance data available', 
                       ha='center', va='center', transform=ax.transAxes, fontsize=12)
                ax.set_title('My Average Performance by Subject', fontsize=14, fontweight='bold')
            
            canvas = FigureCanvasTkAgg(fig, chart_frame)
            canvas.draw()
            canvas.get_tk_widget().grid(row=0, column=0, sticky="nsew")
            
        except ImportError:
            ttk.Label(parent, text="Matplotlib not available for charts", 
                     font=("Arial", 12)).grid(row=0, column=0, sticky="nsew")
    
    def create_performance_stats(self, parent):
        """Create modern performance statistics with horizontal cards layout"""
        # Configure parent frame
        parent.grid_columnconfigure(0, weight=1)
        parent.grid_rowconfigure(0, weight=1)
        
        stats_frame = ttk.LabelFrame(parent, text="My Performance Statistics", padding="10")
        stats_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        stats_frame.grid_columnconfigure(0, weight=1)
        stats_frame.grid_rowconfigure(0, weight=1)
        
        # Get student's marks
        marks = db.get_student_marks(self.student_profile['student_id'])
        
        if marks:
            # Calculate comprehensive statistics
            total_marks = len(marks)
            percentages = [
                (float(m['marks_obtained']) / float(m['total_marks'])) * 100 if m['total_marks'] else 0.0
                for m in marks
            ]
            avg_percentage = sum(percentages) / total_marks
            highest_mark = max(percentages)
            gpa = self.calculate_gpa(marks)
            
            # Create horizontal cards layout
            cards_frame = ttk.Frame(stats_frame, style='Card.TFrame')
            cards_frame.grid(row=0, column=0, sticky="ew")
            cards_frame.grid_columnconfigure(0, weight=1)
            cards_frame.grid_columnconfigure(1, weight=1)
            cards_frame.grid_columnconfigure(2, weight=1)
            cards_frame.grid_columnconfigure(3, weight=1)
            
            # Create metric cards
            metrics = [
                ("Average", f"{avg_percentage:.1f}%", "#2E86AB"),
                ("CGPA", f"{gpa:.2f}", "#27ae60"),
                ("Best Score", f"{highest_mark:.1f}%", "#f39c12"),
                ("Total Exams", str(total_marks), "#e74c3c")
            ]
            
            for i, (label, value, color) in enumerate(metrics):
                card = ttk.Frame(cards_frame, style='Card.TFrame')
                card.grid(row=0, column=i, sticky="ew", padx=5)
                card.grid_columnconfigure(0, weight=1)
                card.grid_rowconfigure(0, weight=1)
                
                # Card content
                content_frame = ttk.Frame(card, style='Card.TFrame')
                content_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
                content_frame.grid_columnconfigure(0, weight=1)
                
                # Label
                ttk.Label(content_frame, text=label, style='Stats.TLabel').grid(row=0, column=0, pady=(0, 5))
                
                # Value
                ttk.Label(content_frame, text=value, style='StatsValue.TLabel', foreground=color).grid(row=1, column=0)
            
        else:
            # No data message
            no_data_label = ttk.Label(stats_frame, text="No performance data available", 
                                     font=("Arial", 14), background='#ffffff')
            no_data_label.grid(row=0, column=0, sticky="nsew")
    
    def create_gauge(self, ax, value, title, color, max_val=100):
        """Create a single gauge chart"""
        import numpy as np
        
        # Calculate angles
        theta = np.linspace(0, np.pi, 100)
        radius = 1
        
        # Background circle
        ax.plot(radius * np.cos(theta), radius * np.sin(theta), 'k-', linewidth=2)
        
        # Filled portion
        filled_theta = np.linspace(0, np.pi * (value / max_val), 100)
        ax.fill_between(radius * np.cos(filled_theta), 0, radius * np.sin(filled_theta), 
                       color=color, alpha=0.7)
        
        # Add value text
        ax.text(0, 0, f'{value:.1f}', ha='center', va='center', fontsize=10, fontweight='bold')
        
        # Add title
        ax.text(0, -1.3, title, ha='center', va='center', fontsize=8)
        
        # Set equal aspect ratio and remove axes
        ax.set_aspect('equal')
        ax.set_xlim(-1.5, 1.5)
        ax.set_ylim(-1.5, 1.5)
        ax.axis('off')
    
    def create_grades_summary(self, parent):
        """Create modern grades summary panel with recent grades table"""
        # Configure parent frame
        parent.grid_columnconfigure(0, weight=1)
        parent.grid_rowconfigure(0, weight=1)
        
        summary_frame = ttk.LabelFrame(parent, text="Recent Grades Performance", padding="10")
        summary_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        summary_frame.grid_columnconfigure(0, weight=1)
        summary_frame.grid_rowconfigure(0, weight=1)
        
        # Get student's marks
        marks = db.get_student_marks(self.student_profile['student_id'])
        
        if marks:
            # Create modern table for recent grades
            table_frame = ttk.Frame(summary_frame, style='Card.TFrame')
            table_frame.grid(row=0, column=0, sticky="nsew")
            table_frame.grid_columnconfigure(0, weight=1)
            table_frame.grid_rowconfigure(0, weight=1)
            
            columns = ('Subject', 'Grade', 'Score', 'Date', 'Status')
            self.grades_tree = ttk.Treeview(table_frame, columns=columns, show='headings', height=6)
            
            # Configure columns
            self.grades_tree.heading('Subject', text='Subject')
            self.grades_tree.heading('Grade', text='Grade')
            self.grades_tree.heading('Score', text='Score')
            self.grades_tree.heading('Date', text='Date')
            self.grades_tree.heading('Status', text='Status')
            
            self.grades_tree.column('Subject', width=150, anchor='w')
            self.grades_tree.column('Grade', width=80, anchor='center')
            self.grades_tree.column('Score', width=100, anchor='center')
            self.grades_tree.column('Date', width=120, anchor='center')
            self.grades_tree.column('Status', width=100, anchor='center')
            
            # Add scrollbar
            scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.grades_tree.yview)
            self.grades_tree.configure(yscrollcommand=scrollbar.set)
            
            self.grades_tree.grid(row=0, column=0, sticky="nsew")
            scrollbar.grid(row=0, column=1, sticky="ns")
            
            # Populate with recent marks
            recent_marks = marks[:10]  # Show last 10 grades
            for mark in recent_marks:
                percentage = (
                    (float(mark['marks_obtained']) / float(mark['total_marks'])) * 100
                    if mark['total_marks'] else 0.0
                )
                grade = self.calculate_grade(percentage)
                
                # Determine status based on grade
                if grade in ['A+', 'A']:
                    status = "Excellent"
                elif grade == 'B':
                    status = "Good"
                elif grade == 'C':
                    status = "Average"
                elif grade == 'D':
                    status = "Below Average"
                else:
                    status = "Needs Improvement"
                
                self.grades_tree.insert('', 'end', values=(
                    mark['subject_name'],
                    grade,
                    f"{percentage:.1f}%",
                    mark['exam_date'],
                    status
                ))
        else:
            # No data message
            no_data_label = ttk.Label(summary_frame, text="No grades data available", 
                                     font=("Arial", 14), background='#ffffff')
            no_data_label.grid(row=0, column=0, sticky="nsew")
    
    def on_filter_change(self, event=None):
        """Handle filter changes"""
        print(f"Filters changed - Year: {self.year_var.get()}, Grade: {self.grade_var.get()}")
        # In a real implementation, this would refresh the dashboard data
        # based on the selected year and grade filters
        self.load_dashboard_data()
    
    def load_dashboard_data(self):
        """Load dashboard data from database"""
        try:
            # Get student's marks
            marks = db.get_student_marks(self.student_profile['student_id'])
            
            # Update CGPA in header
            try:
                cgpa = self.calculate_gpa(marks)
                self.cgpa_header_label.config(text=f"CGPA: {cgpa:.2f}")
            except Exception:
                self.cgpa_header_label.config(text="CGPA: --")
            
            # Update any dynamic content based on filters (placeholder)
            
        except Exception as e:
            print(f"Error loading dashboard data: {e}")
    
    
    def calculate_grade(self, percentage):
        """Calculate letter grade based on percentage"""
        if percentage >= 90:
            return 'A+'
        elif percentage >= 80:
            return 'A'
        elif percentage >= 70:
            return 'B'
        elif percentage >= 60:
            return 'C'
        elif percentage >= 50:
            return 'D'
        else:
            return 'F'
    
    def calculate_gpa(self, marks):
        """Calculate CGPA as credits-weighted average of subject grade points.
        CGPA = Σ(grade_points(subject_avg) × subject_credits) ÷ Σ(subject_credits)
        Subject average is computed from all attempts/assessments in that subject.
        """
        if not marks:
            return 0.0

        # Group by subject and calculate subject-level average percentage
        by_subject = {}
        for m in marks:
            subject_id = m.get('subject_id')
            subject_name = str(m.get('subject_name'))
            key = (subject_id, subject_name)
            pct = (
                (float(m.get('marks_obtained', 0)) / float(m.get('total_marks', 1))) * 100
                if m.get('total_marks') else 0.0
            )
            credits = int(m.get('credits') or 3)
            entry = by_subject.setdefault(key, { 'percentages': [], 'credits': credits })
            entry['percentages'].append(pct)
            if credits:
                entry['credits'] = credits

        total_points = 0.0
        total_credits = 0
        for (_, _), info in by_subject.items():
            if not info['percentages']:
                continue
            avg_pct = sum(info['percentages']) / len(info['percentages'])
            gp = self.get_grade_points(avg_pct)
            cr = max(int(info.get('credits') or 0), 0)
            total_points += gp * cr
            total_credits += cr

        return (total_points / total_credits) if total_credits > 0 else 0.0
    
    def get_grade_points(self, percentage):
        """Get grade points based on percentage"""
        if percentage >= 90:
            return 4.0
        elif percentage >= 80:
            return 3.7
        elif percentage >= 70:
            return 3.0
        elif percentage >= 60:
            return 2.0
        elif percentage >= 50:
            return 1.0
        else:
            return 0.0
    
    
    def logout(self):
        """Logout and return to login"""
        if messagebox.askyesno("Logout", "Are you sure you want to logout?"):
            # Clean up bindings
            self.root.unbind_all("<MouseWheel>")
            self.root.unbind_all("<Key>")
            self.root.destroy()
            import login
            login.LoginWindow().run()
    
    def run(self):
        """Run the dashboard"""
        # Bind cleanup when window is closed
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.root.mainloop()
    
    def on_closing(self):
        """Handle window closing"""
        # Clean up bindings
        self.root.unbind_all("<MouseWheel>")
        self.root.unbind_all("<Key>")
        self.root.destroy()
