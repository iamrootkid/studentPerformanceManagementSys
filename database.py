#!/usr/bin/env python3
"""
Database operations for Student Performance Monitoring System
"""

import mysql.connector
from mysql.connector import Error
import os
import hashlib
from tkinter import messagebox

class Database:
    def __init__(self):
        self.connection = None
        self.connect()
    
    def connect(self):
        """Establish connection to MySQL database"""
        try:
            # First connect to the server (without specifying database) to ensure DB exists
            self.connection = mysql.connector.connect(
                host='localhost',
                user='root',
                password='',
                autocommit=True,
                charset='utf8mb4'
            )
            if not self.connection or not self.connection.is_connected():
                raise Error("Unable to establish initial MySQL connection")

            cursor = self.connection.cursor()
            # Ensure database exists (utf8mb4)
            cursor.execute("CREATE DATABASE IF NOT EXISTS student_performance_db DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
            cursor.execute("USE student_performance_db")
            # Session settings
            try:
                cursor.execute("SET NAMES utf8mb4")
                cursor.execute("SET SESSION sql_mode = ''")
            except Exception:
                pass
            cursor.close()

            # Attempt to apply schema if not present
            try:
                self._ensure_schema()
            except Exception:
                # Non-fatal if schema file missing
                pass

            # Seed default subjects if missing
            try:
                self._seed_default_subjects()
            except Exception:
                pass

            print("[OK] Connected to MySQL database")
            return True
        except Error as e:
            print(f"[ERROR] Error connecting to MySQL: {e}")
            messagebox.showerror("Database Error", 
                              f"Failed to connect to database:\n{e}\n\nPlease ensure:\n"
                              "1. XAMPP is running\n"
                              "2. MySQL service is started\n"
                              "3. Database 'student_performance_db' exists")
            return False
        return False

    def _ensure_schema(self):
        """Apply schema from database_setup.sql if available (idempotent)."""
        try:
            base_dir = os.path.dirname(os.path.abspath(__file__))
            schema_path = os.path.join(base_dir, 'database_setup.sql')
            if not os.path.exists(schema_path):
                return
            with open(schema_path, 'r', encoding='utf-8') as f:
                sql = f.read()
            # Execute script splitting on semicolons (simple best-effort)
            cursor = self.connection.cursor()
            statements = [s.strip() for s in sql.split(';') if s.strip()]
            for stmt in statements:
                try:
                    cursor.execute(stmt)
                except Exception as e:
                    # Continue on benign errors (e.g., table exists)
                    print(f"[WARN] Schema statement failed: {e}")
            cursor.close()
        except Exception as e:
            print(f"[WARN] Failed to apply schema: {e}")

    def _seed_default_subjects(self):
        """Insert a set of common subjects if not present (idempotent)."""
        subjects = [
            ("Physics", "PHY102", 4, "General Physics"),
            ("Chemistry", "CHEM101", 4, "General Chemistry"),
            ("Informatics", "CS102", 4, "Computer Science Basics"),
            ("Biology", "BIO101", 4, "Introduction to Biology"),
            ("History", "HIS101", 3, "World History"),
            ("Geography", "GEO101", 3, "Geographical Studies"),
            ("Philosophy", "PHI101", 3, "Philosophical Thought"),
            ("Arabic", "ARB101", 3, "Arabic Language"),
            ("French", "FR101", 3, "French Language"),
            ("English", "ENG102", 3, "Advanced English"),
            ("Mathematics", "MATH102", 4, "Advanced Mathematics"),
        ]
        cursor = self.connection.cursor()
        # Use INSERT IGNORE to avoid duplicate subject_code errors
        cursor.execute("USE student_performance_db")
        for name, code, credits, desc in subjects:
            try:
                cursor.execute(
                    "INSERT IGNORE INTO subjects (subject_name, subject_code, credits, description, teacher_id) VALUES (%s, %s, %s, %s, NULL)",
                    (name, code, credits, desc)
                )
            except Exception as e:
                print(f"[WARN] Subject seed failed for {code}: {e}")
        cursor.close()
    
    def execute_query(self, query, params=None):
        """Execute SELECT query and return results"""
        try:
            if not self.connection or not self.connection.is_connected():
                self.connect()
            cursor = self.connection.cursor(dictionary=True)
            cursor.execute(query, params or ())
            result = cursor.fetchall()
            cursor.close()
            return result
        except Error as e:
            print(f"[ERROR] Query error: {e} — attempting reconnect")
            try:
                self.connect()
                cursor = self.connection.cursor(dictionary=True)
                cursor.execute(query, params or ())
                result = cursor.fetchall()
                cursor.close()
                return result
            except Error as e2:
                print(f"[ERROR] Query retry failed: {e2}")
                return None
    
    def execute_update(self, query, params=None):
        """Execute INSERT, UPDATE, DELETE query"""
        try:
            if not self.connection or not self.connection.is_connected():
                self.connect()
            cursor = self.connection.cursor()
            cursor.execute(query, params or ())
            self.connection.commit()
            cursor.close()
            return True
        except Error as e:
            print(f"[ERROR] Update error: {e} — attempting reconnect")
            try:
                self.connect()
                cursor = self.connection.cursor()
                cursor.execute(query, params or ())
                self.connection.commit()
                cursor.close()
                return True
            except Error as e2:
                print(f"[ERROR] Update retry failed: {e2}")
                return False
    
    def hash_password(self, password):
        """Hash password using SHA-256"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def verify_login(self, username, password):
        """Verify user login credentials"""
        hashed_password = self.hash_password(password)
        query = "SELECT * FROM users WHERE username = %s AND password = %s"
        result = self.execute_query(query, (username, hashed_password))
        return result[0] if result else None
    
    def get_user_by_id(self, user_id):
        """Get user by ID"""
        query = "SELECT * FROM users WHERE user_id = %s"
        result = self.execute_query(query, (user_id,))
        return result[0] if result else None
    
    def get_student_by_user_id(self, user_id):
        """Get student profile by user ID"""
        query = """
        SELECT s.*, u.username, u.role 
        FROM students s 
        JOIN users u ON s.user_id = u.user_id 
        WHERE s.user_id = %s
        """
        result = self.execute_query(query, (user_id,))
        return result[0] if result else None
    
    def get_teacher_by_user_id(self, user_id):
        """Get teacher profile by user ID"""
        query = """
        SELECT t.*, u.username, u.role 
        FROM teachers t 
        JOIN users u ON t.user_id = u.user_id 
        WHERE t.user_id = %s
        """
        result = self.execute_query(query, (user_id,))
        return result[0] if result else None
    
    def get_student_marks(self, student_id):
        """Get all marks for a student"""
        query = """
        SELECT m.*, s.subject_name, s.subject_code, s.credits, t.fullname as teacher_name
        FROM marks m
        JOIN subjects s ON m.subject_id = s.subject_id
        JOIN teachers t ON m.teacher_id = t.teacher_id
        WHERE m.student_id = %s
        ORDER BY m.exam_date DESC
        """
        return self.execute_query(query, (student_id,))

    def get_teacher_subjects(self, teacher_id):
        """Get subjects taught by a teacher"""
        query = "SELECT subject_id, subject_name FROM subjects WHERE teacher_id = %s ORDER BY subject_name"
        return self.execute_query(query, (teacher_id,)) or []

    def get_marks_for_teacher(self, teacher_id):
        """Get all marks entered by a teacher with student and subject names"""
        query = """
        SELECT 
            m.mark_id,
            m.student_id,
            m.subject_id,
            st.fullname as student_name,
            sb.subject_name,
            m.marks_obtained,
            m.total_marks,
            m.exam_date
        FROM marks m
        JOIN students st ON m.student_id = st.student_id
        JOIN subjects sb ON m.subject_id = sb.subject_id
        WHERE m.teacher_id = %s
        ORDER BY m.exam_date DESC, m.mark_id DESC
        """
        return self.execute_query(query, (teacher_id,)) or []

    def get_teacher_students(self, teacher_id):
        """Get distinct students who have marks with this teacher"""
        query = """
        SELECT DISTINCT st.student_id, st.fullname, st.email, st.phone, st.gender, st.status
        FROM marks m
        JOIN students st ON m.student_id = st.student_id
        WHERE m.teacher_id = %s
        ORDER BY st.fullname
        """
        return self.execute_query(query, (teacher_id,)) or []

    def get_teacher_students_gender_counts(self, teacher_id):
        """Return gender counts for students taught by teacher (distinct students)"""
        query = """
        SELECT st.gender, COUNT(DISTINCT st.student_id) as count
        FROM marks m
        JOIN students st ON m.student_id = st.student_id
        WHERE m.teacher_id = %s
        GROUP BY st.gender
        """
        rows = self.execute_query(query, (teacher_id,)) or []
        data = { (r['gender'] or 'Other'): r['count'] for r in rows }
        return {
            'Male': data.get('Male', 0),
            'Female': data.get('Female', 0),
            'Other': data.get('Other', 0),
        }

    def get_teacher_subject_average_percentages(self, teacher_id, limit=10):
        """Average percentage per subject for a teacher"""
        query = """
        SELECT s.subject_name, AVG((m.marks_obtained / NULLIF(m.total_marks,0)) * 100) as avg_pct
        FROM marks m
        JOIN subjects s ON m.subject_id = s.subject_id
        WHERE m.teacher_id = %s
        GROUP BY s.subject_id, s.subject_name
        ORDER BY s.subject_name ASC
        LIMIT %s
        """
        return self.execute_query(query, (teacher_id, limit)) or []

    def get_teacher_monthly_trends_average(self, teacher_id, months=6):
        """Monthly average percentage for a teacher"""
        query = """
        SELECT DATE_FORMAT(m.exam_date, '%Y-%m') as ym,
               AVG((m.marks_obtained / NULLIF(m.total_marks,0)) * 100) as avg_pct
        FROM marks m
        WHERE m.teacher_id = %s AND m.exam_date IS NOT NULL
        GROUP BY ym
        ORDER BY ym DESC
        LIMIT %s
        """
        rows = self.execute_query(query, (teacher_id, months)) or []
        return list(reversed(rows))

    def add_mark(self, student_id, subject_id, teacher_id, marks_obtained, total_marks, exam_date):
        """Insert a new mark record"""
        query = (
            "INSERT INTO marks (student_id, subject_id, teacher_id, marks_obtained, total_marks, exam_date) "
            "VALUES (%s, %s, %s, %s, %s, %s)"
        )
        return self.execute_update(query, (student_id, subject_id, teacher_id, marks_obtained, total_marks, exam_date))

    def update_mark(self, mark_id, marks_obtained, total_marks, exam_date):
        """Update an existing mark record"""
        query = (
            "UPDATE marks SET marks_obtained = %s, total_marks = %s, exam_date = %s WHERE mark_id = %s"
        )
        return self.execute_update(query, (marks_obtained, total_marks, exam_date, mark_id))

    def delete_mark(self, mark_id):
        """Delete a mark record"""
        query = "DELETE FROM marks WHERE mark_id = %s"
        return self.execute_update(query, (mark_id,))
    
    def get_all_students(self):
        """Get all students"""
        query = """
        SELECT s.*, u.username, u.role 
        FROM students s 
        JOIN users u ON s.user_id = u.user_id
        ORDER BY s.fullname
        """
        return self.execute_query(query)
    
    def get_all_teachers(self):
        """Get all teachers"""
        query = """
        SELECT t.*, u.username, u.role 
        FROM teachers t 
        JOIN users u ON t.user_id = u.user_id
        ORDER BY t.fullname
        """
        return self.execute_query(query)
    
    def get_all_subjects(self):
        """Get all subjects"""
        query = """
        SELECT s.*, t.fullname as teacher_name
        FROM subjects s
        LEFT JOIN teachers t ON s.teacher_id = t.teacher_id
        ORDER BY s.subject_name
        """
        return self.execute_query(query)
    
    def add_student(self, username, password, fullname, email, phone, date_of_birth, gender, address, status):
        """Add new student transactionally and return True on success."""
        try:
            if not self.connection or not self.connection.is_connected():
                self.connect()

            # Begin transaction (temporarily disable autocommit)
            prev_autocommit = self.connection.autocommit
            self.connection.autocommit = False
            cursor = self.connection.cursor()

            # Insert user
            hashed_password = self.hash_password(password)
            cursor.execute("INSERT INTO users (username, password, role) VALUES (%s, %s, 'student')", (username, hashed_password))
            user_id = cursor.lastrowid

            # Fallback if lastrowid isn't available for some reason
            if not user_id:
                cursor2 = self.connection.cursor()
                cursor2.execute("SELECT user_id FROM users WHERE username = %s ORDER BY user_id DESC LIMIT 1", (username,))
                row = cursor2.fetchone()
                cursor2.close()
                user_id = row[0] if row else None

            if not user_id:
                raise Error("Failed to obtain user_id for new student user")

            # Insert student profile
            cursor.execute(
                """
                INSERT INTO students (user_id, fullname, email, phone, date_of_birth, gender, address, status)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """,
                (user_id, fullname, email, phone, date_of_birth, gender, address, status)
            )

            # Commit both inserts
            self.connection.commit()
            cursor.close()
            return True
        except Error as e:
            try:
                if self.connection and self.connection.is_connected():
                    self.connection.rollback()
            except Exception:
                pass
            print(f"[ERROR] Error adding student: {e}")
            return False
        finally:
            try:
                # Restore autocommit
                if self.connection and self.connection.is_connected():
                    self.connection.autocommit = True
            except Exception:
                pass
    
    def add_teacher(self, username, password, fullname, email, phone, department, qualification, status):
        """Add new teacher transactionally and return True on success."""
        try:
            if not self.connection or not self.connection.is_connected():
                self.connect()

            # Begin transaction (temporarily disable autocommit)
            prev_autocommit = self.connection.autocommit
            self.connection.autocommit = False
            cursor = self.connection.cursor()

            # Insert user
            hashed_password = self.hash_password(password)
            cursor.execute("INSERT INTO users (username, password, role) VALUES (%s, %s, 'teacher')", (username, hashed_password))
            user_id = cursor.lastrowid

            # Fallback if lastrowid isn't available
            if not user_id:
                cursor2 = self.connection.cursor()
                cursor2.execute("SELECT user_id FROM users WHERE username = %s ORDER BY user_id DESC LIMIT 1", (username,))
                row = cursor2.fetchone()
                cursor2.close()
                user_id = row[0] if row else None

            if not user_id:
                raise Error("Failed to obtain user_id for new teacher user")

            # Insert teacher profile
            cursor.execute(
                """
                INSERT INTO teachers (user_id, fullname, email, phone, department, qualification, status)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                """,
                (user_id, fullname, email, phone, department, qualification, status)
            )

            # Commit both inserts
            self.connection.commit()
            cursor.close()
            return True
        except Error as e:
            try:
                if self.connection and self.connection.is_connected():
                    self.connection.rollback()
            except Exception:
                pass
            print(f"[ERROR] Error adding teacher: {e}")
            return False
        finally:
            try:
                # Restore autocommit
                if self.connection and self.connection.is_connected():
                    self.connection.autocommit = True
            except Exception:
                pass
    
    def update_student(self, student_id, fullname, email, phone, date_of_birth, gender, address, status):
        """Update student information"""
        query = """
        UPDATE students 
        SET fullname = %s, email = %s, phone = %s, date_of_birth = %s, gender = %s, address = %s, status = %s
        WHERE student_id = %s
        """
        return self.execute_update(query, (fullname, email, phone, date_of_birth, gender, address, status, student_id))
    
    def update_teacher(self, teacher_id, fullname, email, phone, department, qualification, status):
        """Update teacher information"""
        query = """
        UPDATE teachers 
        SET fullname = %s, email = %s, phone = %s, department = %s, qualification = %s, status = %s
        WHERE teacher_id = %s
        """
        return self.execute_update(query, (fullname, email, phone, department, qualification, status, teacher_id))
    
    def delete_student(self, student_id):
        """Delete student (cascades to user and marks)"""
        query = "DELETE FROM students WHERE student_id = %s"
        return self.execute_update(query, (student_id,))
    
    def delete_teacher(self, teacher_id):
        """Delete teacher (cascades to user)"""
        query = "DELETE FROM teachers WHERE teacher_id = %s"
        return self.execute_update(query, (teacher_id,))
    
    def get_system_stats(self):
        """Get system statistics for admin dashboard"""
        stats = {}
        
        # Count students
        result = self.execute_query("SELECT COUNT(*) as count FROM students WHERE status = 'Active'")
        stats['active_students'] = result[0]['count'] if result else 0
        
        # Count teachers
        result = self.execute_query("SELECT COUNT(*) as count FROM teachers WHERE status = 'Active'")
        stats['active_teachers'] = result[0]['count'] if result else 0
        
        # Count subjects
        result = self.execute_query("SELECT COUNT(*) as count FROM subjects")
        stats['total_subjects'] = result[0]['count'] if result else 0
        
        # Average percentage across all marks (marks_obtained / total_marks * 100)
        result = self.execute_query("SELECT AVG((marks_obtained / NULLIF(total_marks,0)) * 100) as avg_pct FROM marks")
        stats['average_marks'] = round(result[0]['avg_pct'], 2) if result and result[0]['avg_pct'] else 0
        
        return stats

    def get_gender_distribution(self):
        """Return counts by gender for students"""
        query = "SELECT gender, COUNT(*) as count FROM students GROUP BY gender"
        rows = self.execute_query(query) or []
        data = { (row['gender'] or 'Other'): row['count'] for row in rows }
        return {
            'Male': data.get('Male', 0),
            'Female': data.get('Female', 0),
            'Other': data.get('Other', 0),
        }

    def get_subject_average_percentages(self, limit=8):
        """Average percentage per subject, top N subjects by name"""
        query = (
            """
            SELECT s.subject_name, AVG((m.marks_obtained / NULLIF(m.total_marks,0)) * 100) as avg_pct
            FROM marks m
            JOIN subjects s ON m.subject_id = s.subject_id
            GROUP BY s.subject_id, s.subject_name
            ORDER BY s.subject_name ASC
            LIMIT %s
            """
        )
        return self.execute_query(query, (limit,)) or []

    def get_monthly_trends_average(self, months=6):
        """Average percentage per recent month (YYYY-MM)"""
        query = (
            """
            SELECT DATE_FORMAT(exam_date, '%Y-%m') as ym,
                   AVG((marks_obtained / NULLIF(total_marks,0)) * 100) as avg_pct
            FROM marks
            WHERE exam_date IS NOT NULL
            GROUP BY ym
            ORDER BY ym DESC
            LIMIT %s
            """
        )
        rows = self.execute_query(query, (months,)) or []
        return list(reversed(rows))
    
    def get_top_students(self, limit=3):
        """Get top performing students with their CGPA"""
        query = """
        SELECT 
            s.student_id,
            s.fullname,
            s.email,
            s.gender,
            COUNT(m.mark_id) as total_exams,
            AVG((m.marks_obtained / m.total_marks) * 100) as avg_percentage,
            CASE 
                WHEN AVG((m.marks_obtained / m.total_marks) * 100) >= 90 THEN 4.0
                WHEN AVG((m.marks_obtained / m.total_marks) * 100) >= 80 THEN 3.5
                WHEN AVG((m.marks_obtained / m.total_marks) * 100) >= 70 THEN 3.0
                WHEN AVG((m.marks_obtained / m.total_marks) * 100) >= 60 THEN 2.5
                WHEN AVG((m.marks_obtained / m.total_marks) * 100) >= 50 THEN 2.0
                ELSE 1.0
            END as cgpa
        FROM students s
        JOIN marks m ON s.student_id = m.student_id
        WHERE s.status = 'Active'
        GROUP BY s.student_id, s.fullname, s.email, s.gender
        HAVING COUNT(m.mark_id) > 0
        ORDER BY avg_percentage DESC
        LIMIT %s
        """
        return self.execute_query(query, (limit,))
    
    # Password reset functionality
    def check_username_exists(self, username):
        """Check if username exists in the database"""
        query = "SELECT user_id, username, role FROM users WHERE username = %s"
        result = self.execute_query(query, (username,))
        return result[0] if result else None
    
    def update_password(self, username, new_password):
        """Update user password"""
        hashed_password = self.hash_password(new_password)
        query = "UPDATE users SET password = %s WHERE username = %s"
        return self.execute_update(query, (hashed_password, username))
    
    def get_user_email(self, username):
        """Get user email for password reset"""
        query = """
        SELECT u.username, u.role, 
               COALESCE(s.email, t.email) as email
        FROM users u
        LEFT JOIN students s ON u.user_id = s.user_id
        LEFT JOIN teachers t ON u.user_id = t.user_id
        WHERE u.username = %s
        """
        result = self.execute_query(query, (username,))
        return result[0] if result else None
    
    def close(self):
        """Close database connection"""
        if self.connection and self.connection.is_connected():
            self.connection.close()
            print("[OK] Database connection closed")

# Global database instance
db = Database()
