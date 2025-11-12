#!/usr/bin/env python3
"""
Teacher Dashboard for Student Performance Monitoring System
"""

import tkinter as tk
from tkinter import ttk, messagebox
from database import db
import datetime
from performance_dashboard import PerformanceDashboard

class TeacherDashboard:
    def __init__(self, user, teacher_profile):
        self.user = user
        self.teacher_profile = teacher_profile
        self.root = tk.Tk()
        self.root.title("Teacher Dashboard - Student Performance Monitoring System")
        self.root.geometry("1400x900")
        self.root.state('zoomed')  # Maximize window
        
        # Configure grid weights for root window
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_rowconfigure(0, weight=1)
        
        # Create scrollable area for the whole dashboard
        self._canvas = tk.Canvas(self.root, bg=self.root.cget('bg'), highlightthickness=0)
        self._vsb = ttk.Scrollbar(self.root, orient='vertical', command=self._canvas.yview)
        self._canvas.configure(yscrollcommand=self._vsb.set)
        self._canvas.grid(row=0, column=0, sticky="nsew")
        self._vsb.grid(row=0, column=1, sticky="ns")

        # Inner scrollable frame
        self._scroll_frame = ttk.Frame(self._canvas)
        self._canvas.create_window((0, 0), window=self._scroll_frame, anchor='nw')
        self._scroll_frame.bind(
            '<Configure>',
            lambda e: self._canvas.configure(scrollregion=self._canvas.bbox('all'))
        )
        # Smooth mouse wheel scrolling (Windows)
        self._canvas.bind_all('<MouseWheel>', lambda e: self._canvas.yview_scroll(int(-1 * (e.delta / 120)), 'units'))

        # Main container inside the scrollable frame
        self.main_container = ttk.Frame(self._scroll_frame)
        self.main_container.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        
        # Configure grid weights for main container
        self.main_container.grid_columnconfigure(0, weight=1)
        self.main_container.grid_rowconfigure(0, weight=0)  # Header row
        self.main_container.grid_rowconfigure(1, weight=1)  # Notebook row
        
        # Create header
        self.create_header()
        
        # Create notebook for tabs
        self.notebook = ttk.Notebook(self.main_container)
        self.notebook.grid(row=1, column=0, sticky="nsew", pady=(10, 0))
        
        # Create tabs
        self.create_performance_tab()
        self.create_students_tab()
        self.create_marks_tab()
        
        # Load initial data
        self.load_dashboard_data()
    
    def create_header(self):
        """Create header with title and logout button using grid layout"""
        header_frame = ttk.Frame(self.main_container)
        header_frame.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        header_frame.grid_columnconfigure(0, weight=1)
        header_frame.grid_columnconfigure(1, weight=0)
        
        # Title
        title_label = ttk.Label(header_frame, text="Teacher Dashboard", 
                               font=("Arial", 20, "bold"))
        title_label.grid(row=0, column=0, sticky="w")
        
        # User info and logout
        user_frame = ttk.Frame(header_frame)
        user_frame.grid(row=0, column=1, sticky="e")
        
        user_label = ttk.Label(user_frame, text=f"Welcome, {self.teacher_profile['fullname']}", 
                              font=("Arial", 12))
        user_label.grid(row=0, column=0, padx=(0, 10))
        
        logout_button = ttk.Button(user_frame, text="Logout", command=self.logout)
        logout_button.grid(row=0, column=1)
    
    def create_performance_tab(self):
        """Create performance dashboard tab"""
        self.performance_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.performance_frame, text="Performance Dashboard")
        
        # Create embedded performance dashboard
        self.performance_dashboard = PerformanceDashboard("teacher", self.teacher_profile)
        
        # Move the performance dashboard content to this tab
        # We'll create a simplified version that fits in the tab
        self.create_embedded_performance_dashboard()
    
    def create_embedded_performance_dashboard(self):
        """Create embedded performance dashboard for the tab using grid layout"""
        # Configure grid weights for performance frame
        self.performance_frame.grid_columnconfigure(0, weight=1)
        self.performance_frame.grid_rowconfigure(0, weight=0)  # Header row
        self.performance_frame.grid_rowconfigure(1, weight=0)  # Filters row
        self.performance_frame.grid_rowconfigure(2, weight=0)  # Metrics row
        self.performance_frame.grid_rowconfigure(3, weight=1)  # Charts row
        
        # Header
        header_frame = ttk.Frame(self.performance_frame)
        header_frame.grid(row=0, column=0, sticky="ew", pady=(0, 20))
        header_frame.grid_columnconfigure(0, weight=1)
        
        title_label = ttk.Label(header_frame, text="Student Performance Dashboard", 
                               font=("Arial", 20, "bold"))
        title_label.grid(row=0, column=0, sticky="w")
        
        # Filters
        filters_frame = ttk.Frame(self.performance_frame)
        filters_frame.grid(row=1, column=0, sticky="ew", pady=(0, 20))
        filters_frame.grid_columnconfigure(0, weight=0)
        filters_frame.grid_columnconfigure(1, weight=0)
        filters_frame.grid_columnconfigure(2, weight=1)
        
        # Year filter
        year_frame = ttk.Frame(filters_frame)
        year_frame.grid(row=0, column=0, sticky="w", padx=(0, 20))
        
        ttk.Label(year_frame, text="Select Year", font=("Arial", 12)).grid(row=0, column=0, sticky="w")
        self.year_var = tk.StringVar(value="All")
        year_combo = ttk.Combobox(year_frame, textvariable=self.year_var, 
                                 values=["All", "2024", "2023", "2022"], 
                                 state="readonly", width=15)
        year_combo.grid(row=1, column=0, sticky="w", pady=(5, 0))
        
        # Grade filter
        grade_frame = ttk.Frame(filters_frame)
        grade_frame.grid(row=0, column=1, sticky="w")
        
        ttk.Label(grade_frame, text="Select Grade", font=("Arial", 12)).grid(row=0, column=0, sticky="w")
        self.grade_var = tk.StringVar(value="All")
        grade_combo = ttk.Combobox(grade_frame, textvariable=self.grade_var,
                                  values=["All", "Grade 1", "Grade 2", "Grade 3", "Grade 4", "Grade 5"],
                                  state="readonly", width=15)
        grade_combo.grid(row=1, column=0, sticky="w", pady=(5, 0))
        
        # Metrics card
        metrics_frame = ttk.Frame(self.performance_frame)
        metrics_frame.grid(row=2, column=0, sticky="ew", pady=(0, 20))
        metrics_frame.grid_columnconfigure(0, weight=1)
        
        card_frame = ttk.Frame(metrics_frame, relief='solid', borderwidth=1)
        card_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=10)
        card_frame.grid_columnconfigure(0, weight=1)
        
        content_frame = ttk.Frame(card_frame)
        content_frame.grid(row=0, column=0, sticky="ew", padx=20, pady=15)
        content_frame.grid_columnconfigure(1, weight=1)
        
        icon_label = ttk.Label(content_frame, text="🎓", font=("Arial", 24))
        icon_label.grid(row=0, column=0, sticky="w", padx=(0, 15))
        
        count_frame = ttk.Frame(content_frame)
        count_frame.grid(row=0, column=1, sticky="w")
        
        ttk.Label(count_frame, text="Students", font=("Arial", 12)).grid(row=0, column=0, sticky="w")
        self.student_count_label = ttk.Label(count_frame, text="300", 
                                           font=("Arial", 20, "bold"))
        self.student_count_label.grid(row=1, column=0, sticky="w")
        
        # Charts area
        charts_frame = ttk.Frame(self.performance_frame)
        charts_frame.grid(row=3, column=0, sticky="nsew")
        charts_frame.grid_columnconfigure(0, weight=1)
        charts_frame.grid_columnconfigure(1, weight=1)
        charts_frame.grid_rowconfigure(0, weight=1)
        
        # Left column - Donut chart
        left_frame = ttk.Frame(charts_frame)
        left_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        
        self.create_donut_chart(left_frame)
        
        # Right column - Bar chart
        right_frame = ttk.Frame(charts_frame)
        right_frame.grid(row=0, column=1, sticky="nsew", padx=(10, 0))
        
        self.create_bar_chart(right_frame)
    
    def create_donut_chart(self, parent):
        """Create donut chart for students (gender distribution) using DB"""
        try:
            import matplotlib.pyplot as plt
            from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
            import numpy as np
            
            chart_frame = ttk.LabelFrame(parent, text="Students by Gender", padding="10")
            chart_frame.grid(row=0, column=0, sticky="nsew")
            chart_frame.grid_columnconfigure(0, weight=1)
            chart_frame.grid_rowconfigure(0, weight=1)
            
            fig, ax = plt.subplots(figsize=(6, 5))
            fig.patch.set_facecolor('white')
            
            # Real data (gender distribution of teacher's students)
            gd = db.get_teacher_students_gender_counts(self.teacher_profile['teacher_id'])
            labels = ['Male', 'Female', 'Other']
            sizes = [gd.get('Male', 0), gd.get('Female', 0), gd.get('Other', 0)]
            colors = ['#3498db', '#e74c3c', '#95a5a6']

            wedges, texts, autotexts = ax.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%',
                                             startangle=90, pctdistance=0.85)
            
            centre_circle = plt.Circle((0,0), 0.70, fc='white')
            ax.add_artist(centre_circle)
            
            ax.set_title('Gender split of your students', 
                        fontsize=10, pad=20, style='italic')
            
            canvas = FigureCanvasTkAgg(fig, chart_frame)
            canvas.draw()
            canvas.get_tk_widget().grid(row=0, column=0, sticky="nsew")
            
        except ImportError:
            ttk.Label(parent, text="Matplotlib not available for charts", 
                     font=("Arial", 12)).grid(row=0, column=0, sticky="nsew")
    
    def create_bar_chart(self, parent):
        """Create bar chart of average percentage by subject using DB"""
        try:
            import matplotlib.pyplot as plt
            from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
            import numpy as np
            
            chart_frame = ttk.LabelFrame(parent, text="Average Percentage by Subject", padding="10")
            chart_frame.grid(row=0, column=0, sticky="nsew")
            chart_frame.grid_columnconfigure(0, weight=1)
            chart_frame.grid_rowconfigure(0, weight=1)
            
            fig, ax = plt.subplots(figsize=(6, 5))
            fig.patch.set_facecolor('white')
            
            # Real data
            rows = db.get_teacher_subject_average_percentages(self.teacher_profile['teacher_id'])
            subjects = [r['subject_name'] for r in rows] or ['No Data']
            averages = [round(float(r.get('avg_pct') or 0), 1) for r in rows] or [0.0]
            x = np.arange(len(subjects))
            bars = ax.bar(x, averages, color='#3498db')
            ax.set_xlabel('Subjects')
            ax.set_ylabel('Average %')
            ax.set_title('Your subjects - average percentage')
            ax.set_xticks(x)
            ax.set_xticklabels(subjects, rotation=0)
            ax.set_ylim(0, 100)
            
            plt.tight_layout()
            
            canvas = FigureCanvasTkAgg(fig, chart_frame)
            canvas.draw()
            canvas.get_tk_widget().grid(row=0, column=0, sticky="nsew")
            
        except ImportError:
            ttk.Label(parent, text="Matplotlib not available for charts", 
                     font=("Arial", 12)).grid(row=0, column=0, sticky="nsew")
    
    def create_students_tab(self):
        """Create students tab using grid layout"""
        self.students_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.students_frame, text="My Students")
        
        # Configure grid weights for students frame
        self.students_frame.grid_columnconfigure(0, weight=1)
        self.students_frame.grid_rowconfigure(0, weight=1)
        
        # Students table
        table_frame = ttk.Frame(self.students_frame)
        table_frame.grid(row=0, column=0, sticky="nsew", pady=10)
        table_frame.grid_columnconfigure(0, weight=1)
        table_frame.grid_rowconfigure(0, weight=1)
        
        # Create Treeview
        columns = ('ID', 'Name', 'Email', 'Phone', 'Gender', 'Status')
        self.students_tree = ttk.Treeview(table_frame, columns=columns, show='headings', height=15)
        
        # Define headings
        for col in columns:
            self.students_tree.heading(col, text=col)
            self.students_tree.column(col, width=120)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.students_tree.yview)
        self.students_tree.configure(yscrollcommand=scrollbar.set)
        
        self.students_tree.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")
        
        # Load sample data
        self.load_students()
    
    def create_marks_tab(self):
        """Create marks management tab using grid layout"""
        self.marks_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.marks_frame, text="Manage Marks")
        
        # Configure grid weights for marks frame
        self.marks_frame.grid_columnconfigure(0, weight=1)
        self.marks_frame.grid_rowconfigure(0, weight=0)  # Actions row
        self.marks_frame.grid_rowconfigure(1, weight=1)  # Table row
        
        # Action buttons
        actions_frame = ttk.Frame(self.marks_frame)
        actions_frame.grid(row=0, column=0, sticky="ew", pady=10)
        actions_frame.grid_columnconfigure(0, weight=1)
        actions_frame.grid_columnconfigure(1, weight=0)
        actions_frame.grid_columnconfigure(2, weight=0)
        actions_frame.grid_columnconfigure(3, weight=0)
        
        ttk.Button(actions_frame, text="Add Mark", 
                  command=self.add_mark).grid(row=0, column=1, padx=5)
        ttk.Button(actions_frame, text="Edit Mark", 
                  command=self.edit_mark).grid(row=0, column=2, padx=5)
        ttk.Button(actions_frame, text="Delete Mark", 
                  command=self.delete_mark).grid(row=0, column=3, padx=5)
        
        # Marks table
        table_frame = ttk.Frame(self.marks_frame)
        table_frame.grid(row=1, column=0, sticky="nsew", pady=10)
        table_frame.grid_columnconfigure(0, weight=1)
        table_frame.grid_rowconfigure(0, weight=1)
        
        # Create Treeview
        columns = ('Student', 'Subject', 'Exam Type', 'Marks', 'Total', 'Percentage', 'Date')
        self.marks_tree = ttk.Treeview(table_frame, columns=columns, show='headings', height=15)
        
        # Define headings
        for col in columns:
            self.marks_tree.heading(col, text=col)
            self.marks_tree.column(col, width=100)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.marks_tree.yview)
        self.marks_tree.configure(yscrollcommand=scrollbar.set)
        
        self.marks_tree.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")
        
        # Load sample data
        self.load_marks()
    
    def load_dashboard_data(self):
        """Load dashboard data with real DB values for this teacher"""
        # Update Students count metric
        try:
            students = db.get_teacher_students(self.teacher_profile['teacher_id'])
            self.student_count_label.config(text=str(len(students)))
        except Exception:
            self.student_count_label.config(text="0")
    
    def load_students(self):
        """Load students data"""
        # Clear existing items
        for item in self.students_tree.get_children():
            self.students_tree.delete(item)
        
        # Load students taught by this teacher (distinct based on marks)
        students = db.get_teacher_students(self.teacher_profile['teacher_id'])
        for student in students:
            self.students_tree.insert('', 'end', values=(
                student['student_id'],
                student['fullname'],
                student['email'],
                student['phone'],
                student['gender'],
                student['status']
            ))
    
    def load_marks(self):
        """Load marks for this teacher from DB"""
        for item in self.marks_tree.get_children():
            self.marks_tree.delete(item)
        rows = db.get_marks_for_teacher(self.teacher_profile['teacher_id'])
        for r in rows:
            percent = 0
            try:
                if r['total_marks']:
                    percent = round((float(r['marks_obtained']) / float(r['total_marks'])) * 100)
            except Exception:
                percent = 0
            date_str = r['exam_date'].strftime('%Y-%m-%d') if hasattr(r['exam_date'], 'strftime') else (r['exam_date'] or '')
            self.marks_tree.insert('', 'end', iid=str(r['mark_id']), values=(
                r['student_name'],
                r['subject_name'],
                '',  # exam type not modeled
                r['marks_obtained'],
                r['total_marks'],
                f"{percent}%",
                date_str,
            ))
    
    def add_mark(self):
        """Add new mark"""
        form = tk.Toplevel(self.root)
        form.title("Add Mark")
        form.geometry("460x380")
        form.resizable(False, False)

        row = 0
        def add_row(label_text, widget):
            ttk.Label(form, text=label_text).grid(row=row, column=0, padx=16, pady=8, sticky="w")
            widget.grid(row=row, column=1, padx=16, pady=8, sticky="w")
            return 1

        # Student selection
        students = db.get_all_students() or []
        student_map = { f"{s['student_id']} - {s['fullname']}": s['student_id'] for s in students }
        student_var = tk.StringVar()
        student_combo = ttk.Combobox(form, textvariable=student_var, values=list(student_map.keys()), width=28, state='readonly')
        row += add_row("Student", student_combo)

        # Subject selection (for this teacher) - names only, allow typing
        subjects = db.get_teacher_subjects(self.teacher_profile['teacher_id'])
        # Map subject name -> id for resolution on submit
        subject_map = { str(sub['subject_name']): sub['subject_id'] for sub in subjects }
        subject_var = tk.StringVar()
        subject_combo = ttk.Combobox(form, textvariable=subject_var, values=list(subject_map.keys()), width=28, state='normal')
        row += add_row("Subject", subject_combo)

        marks_var = tk.StringVar()
        total_var = tk.StringVar()
        today_str = datetime.date.today().strftime('%Y-%m-%d')
        date_var = tk.StringVar(value=today_str)
        marks_entry = ttk.Entry(form, textvariable=marks_var, width=30)
        total_entry = ttk.Entry(form, textvariable=total_var, width=30)
        row += add_row("Marks Obtained", marks_entry)
        # Default total to 100; will auto-adjust if marks exceed total
        total_var.set("100")
        row += add_row("Total Marks", total_entry)
        # Live percentage display
        percent_var = tk.StringVar(value="")
        percent_label = ttk.Label(form, textvariable=percent_var)
        row += add_row("Percentage", percent_label)
        # Date row with calendar icon button
        date_entry = ttk.Entry(form, textvariable=date_var, width=30)
        # Ensure the entry visibly shows today's date if empty
        if not (date_entry.get() or "").strip():
            date_entry.insert(0, today_str)
        # Place date label, entry, and calendar icon in the same row
        tk.Label(form, text="Exam Date (YYYY-MM-DD)").grid(row=row, column=0, padx=16, pady=8, sticky="w")
        date_entry.grid(row=row, column=1, padx=16, pady=8, sticky="w")
        def set_today():
            date_var.set(datetime.date.today().strftime('%Y-%m-%d'))
            try:
                date_entry.icursor('end')
            except Exception:
                pass
        calendar_btn = ttk.Button(form, text="📅", width=3, command=set_today)
        calendar_btn.grid(row=row, column=2, padx=(0, 0), pady=8, sticky="w")
        row += 1

        # Helpers to keep total reasonable and update percentage
        def _update_percent_and_total(*_):
            m_txt = (marks_var.get() or "").strip()
            t_txt = (total_var.get() or "").strip()
            try:
                m_val = float(m_txt.replace(',', '.')) if m_txt else None
            except Exception:
                m_val = None
            # Default total to 100 if empty
            if not t_txt:
                total_var.set("100")
                t_txt = "100"
            # If marks exceed total, auto-raise total to marks
            try:
                t_val = float(t_txt.replace(',', '.')) if t_txt else None
            except Exception:
                t_val = None
            if m_val is not None and t_val is not None and m_val > t_val:
                total_var.set(str(m_val))
                t_val = m_val
            # Update percentage
            if m_val is not None and t_val not in (None, 0):
                pct = round((m_val / t_val) * 100, 1)
                percent_var.set(f"{pct}%")
            else:
                percent_var.set("")
        # Trace variable changes
        try:
            marks_var.trace_add('write', _update_percent_and_total)
            total_var.trace_add('write', _update_percent_and_total)
        except Exception:
            # Fallback for older Tk versions
            marks_var.trace('w', _update_percent_and_total)
            total_var.trace('w', _update_percent_and_total)
        # Initial compute
        _update_percent_and_total()

        # Preselect first options if available to avoid empty selection
        try:
            if student_combo['values']:
                student_combo.current(0)
            if subject_combo['values']:
                subject_combo.current(0)
        except Exception:
            pass

        def submit():
            # Resolve student selection robustly
            student_key = (student_var.get() or student_combo.get() or "").strip()
            if not student_key and getattr(student_combo, '__getitem__', None):
                try:
                    vals = student_combo['values']
                    if vals:
                        student_key = vals[0]
                except Exception:
                    pass
            try:
                student_id = None
                if ' - ' in student_key:
                    student_id = int(student_key.split(' - ', 1)[0])
                else:
                    # Try mapping fallback or direct int
                    student_id = student_map.get(student_key) or int(student_key)
            except Exception:
                student_id = None
            if not student_id:
                messagebox.showerror("Error", "Please select a student.", parent=form)
                return

            # Resolve subject selection: expect subject name from combo or typed
            subject_key = (subject_var.get() or subject_combo.get() or "").strip()
            if not subject_key and getattr(subject_combo, '__getitem__', None):
                try:
                    vals = subject_combo['values']
                    if vals:
                        subject_key = vals[0]
                except Exception:
                    pass
            # Map typed/selected subject name to id
            subject_id = subject_map.get(subject_key)
            if not subject_id:
                messagebox.showerror("Error", "Please select a subject.", parent=form)
                return
            # Parse numeric inputs (support comma decimals) and read directly from Entry if needed
            raw_marks = (marks_var.get() or marks_entry.get() or "").strip()
            raw_total = (total_var.get() or total_entry.get() or "").strip()
            try:
                marks = float(raw_marks.replace(',', '.'))
                total = float(raw_total.replace(',', '.'))
            except Exception:
                messagebox.showerror("Error", "Marks and Total must be numeric.", parent=form)
                return
            if total <= 0:
                messagebox.showerror("Error", "Total must be greater than 0.", parent=form)
                return
            if marks < 0 or marks > total:
                messagebox.showerror("Error", "Marks must be between 0 and Total.", parent=form)
                return
            # Normalize date: support YYYY-MM-DD, DD-MM-YYYY, DD/MM/YYYY, YYYY/MM/DD
            exam_date = (date_var.get() or date_entry.get() or today_str).strip()
            if not exam_date:
                exam_date = today_str
            if len(exam_date) == 10:
                if exam_date[2] in ('-', '/') and exam_date[5] in ('-', '/'):
                    # Possibly DD-MM-YYYY or DD/MM/YYYY
                    try:
                        d, m, y = exam_date.replace('/', '-').split('-')
                        int(d); int(m); int(y)
                        exam_date = f"{y}-{m.zfill(2)}-{d.zfill(2)}"
                    except Exception:
                        pass
                elif exam_date[4] in ('-', '/') and exam_date[7] in ('-', '/'):
                    # YYYY-MM-DD or YYYY/MM/DD -> normalize hyphens
                    exam_date = exam_date.replace('/', '-')
            ok = db.add_mark(
                student_id,
                subject_id,
                self.teacher_profile['teacher_id'],
                marks,
                total,
                exam_date,
            )
            if ok:
                messagebox.showinfo("Success", "Mark added successfully.", parent=form)
                self.load_marks()
                self.load_dashboard_data()
                form.destroy()
            else:
                messagebox.showerror("Error", "Failed to add mark.", parent=form)

        ttk.Button(form, text="Add", command=submit).grid(row=row, column=0, columnspan=2, pady=16)
        form.transient(self.root)
        form.grab_set()
        self.root.wait_window(form)
    
    def edit_mark(self):
        """Edit selected mark"""
        selection = self.marks_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a mark to edit")
            return
        iid = selection[0]
        values = self.marks_tree.item(iid)['values']
        # We need mark_id; store it in iid when loading. If iid is not numeric, editing can't proceed.
        try:
            mark_id = int(iid)
        except Exception:
            messagebox.showerror("Error", "Cannot edit this mark (missing identifier).")
            return

        form = tk.Toplevel(self.root)
        form.title("Edit Mark")
        form.geometry("420x300")
        form.resizable(False, False)

        marks_var = tk.StringVar(value=str(values[3]))
        total_var = tk.StringVar(value=str(values[4]))
        date_var = tk.StringVar(value=str(values[6]))

        row = 0
        def add_row(label_text, widget):
            ttk.Label(form, text=label_text).grid(row=row, column=0, padx=16, pady=8, sticky="w")
            widget.grid(row=row, column=1, padx=16, pady=8, sticky="w")
            return 1

        row += add_row("Marks Obtained", ttk.Entry(form, textvariable=marks_var, width=28))
        row += add_row("Total Marks", ttk.Entry(form, textvariable=total_var, width=28))
        # Date row with calendar icon button in edit dialog
        date_entry = ttk.Entry(form, textvariable=date_var, width=28)
        # Ensure default today if empty (var) and entry visibly shows a value
        if not (date_var.get() or "").strip():
            date_var.set(datetime.date.today().strftime('%Y-%m-%d'))
        if not (date_entry.get() or "").strip():
            date_entry.insert(0, date_var.get())
        # Place label, entry, and icon
        ttk.Label(form, text="Exam Date (YYYY-MM-DD)").grid(row=row, column=0, padx=16, pady=8, sticky="w")
        date_entry.grid(row=row, column=1, padx=16, pady=8, sticky="w")
        def set_today_edit():
            date_var.set(datetime.date.today().strftime('%Y-%m-%d'))
            try:
                date_entry.icursor('end')
            except Exception:
                pass
        calendar_btn = ttk.Button(form, text="📅", width=3, command=set_today_edit)
        calendar_btn.grid(row=row, column=2, padx=(0, 0), pady=8, sticky="w")
        row += 1

        def submit():
            # Parse numeric inputs (support comma decimals)
            raw_marks = (marks_var.get() or "").strip()
            raw_total = (total_var.get() or "").strip()
            try:
                marks = float(raw_marks.replace(',', '.'))
                total = float(raw_total.replace(',', '.'))
            except Exception:
                messagebox.showerror("Error", "Marks and Total must be numbers.", parent=form)
                return
            # Normalize date similar to add flow
            exam_date = (date_var.get() or "").strip()
            if not exam_date:
                exam_date = datetime.date.today().strftime('%Y-%m-%d')
            if len(exam_date) == 10:
                if exam_date[2] in ('-', '/') and exam_date[5] in ('-', '/'):
                    # DD-MM-YYYY or DD/MM/YYYY -> YYYY-MM-DD
                    try:
                        d, m, y = exam_date.replace('/', '-').split('-')
                        int(d); int(m); int(y)
                        exam_date = f"{y}-{m.zfill(2)}-{d.zfill(2)}"
                    except Exception:
                        pass
                elif exam_date[4] in ('-', '/') and exam_date[7] in ('-', '/'):
                    # YYYY-MM-DD or YYYY/MM/DD -> normalize separators
                    exam_date = exam_date.replace('/', '-')
            if db.update_mark(mark_id, marks, total, exam_date):
                messagebox.showinfo("Success", "Mark updated successfully.", parent=form)
                self.load_marks()
                # Reselect updated row for user feedback
                try:
                    self.marks_tree.selection_set(str(mark_id))
                    self.marks_tree.see(str(mark_id))
                except Exception:
                    pass
                self.load_dashboard_data()
                form.destroy()
            else:
                messagebox.showerror("Error", "Failed to update mark.", parent=form)

        ttk.Button(form, text="Update", command=submit).grid(row=row, column=0, columnspan=2, pady=16)
        form.transient(self.root)
        form.grab_set()
        self.root.wait_window(form)
    
    def delete_mark(self):
        """Delete selected mark"""
        selection = self.marks_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a mark to delete")
            return
        iid = selection[0]
        try:
            mark_id = int(iid)
        except Exception:
            messagebox.showerror("Error", "Cannot delete this mark (missing identifier).")
            return
        if messagebox.askyesno("Confirm", "Are you sure you want to delete this mark?"):
            if db.delete_mark(mark_id):
                messagebox.showinfo("Success", "Mark deleted successfully")
                self.load_marks()
                self.load_dashboard_data()
            else:
                messagebox.showerror("Error", "Failed to delete mark")
    
    def logout(self):
        """Logout and return to login"""
        if messagebox.askyesno("Logout", "Are you sure you want to logout?"):
            self.root.destroy()
            import login
            login.LoginWindow().run()
