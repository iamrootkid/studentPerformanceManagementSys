-- ==============================
-- Create database
-- ==============================
CREATE DATABASE IF NOT EXISTS student_performance_db;
USE student_performance_db;

-- ==============================
-- 1. Users table
-- ==============================
CREATE TABLE IF NOT EXISTS users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    role ENUM('admin', 'teacher', 'student') NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ==============================
-- 2. Students table
-- ==============================
CREATE TABLE IF NOT EXISTS students (
    student_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    fullname VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE,
    phone VARCHAR(20),
    date_of_birth DATE,
    gender ENUM('Male', 'Female', 'Other'),
    address TEXT,
    enrollment_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status ENUM('Active', 'Inactive', 'Graduated') DEFAULT 'Active',
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);

-- ==============================
-- 3. Teachers table
-- ==============================
CREATE TABLE IF NOT EXISTS teachers (
    teacher_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    fullname VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE,
    phone VARCHAR(20),
    department VARCHAR(50),
    qualification VARCHAR(100),
    hire_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status ENUM('Active', 'Inactive') DEFAULT 'Active',
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);

-- ==============================
-- 4. Subjects table
-- ==============================
CREATE TABLE IF NOT EXISTS subjects (
    subject_id INT AUTO_INCREMENT PRIMARY KEY,
    subject_name VARCHAR(100) NOT NULL,
    subject_code VARCHAR(20) UNIQUE NOT NULL,
    credits INT DEFAULT 3,
    description TEXT,
    teacher_id INT NULL,
    FOREIGN KEY (teacher_id) REFERENCES teachers(teacher_id) ON DELETE SET NULL
);

-- ==============================
-- 5. Marks table
-- ==============================
CREATE TABLE IF NOT EXISTS marks (
    mark_id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT,
    subject_id INT,
    teacher_id INT,
    exam_type ENUM('Quiz', 'Midterm', 'Final', 'Assignment', 'Project') NOT NULL,
    marks_obtained DECIMAL(5,2) NOT NULL,
    total_marks DECIMAL(5,2) DEFAULT 100.00,
    exam_date DATE,
    semester VARCHAR(20),
    academic_year VARCHAR(10),
    remarks TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES students(student_id) ON DELETE CASCADE,
    FOREIGN KEY (subject_id) REFERENCES subjects(subject_id) ON DELETE CASCADE,
    FOREIGN KEY (teacher_id) REFERENCES teachers(teacher_id) ON DELETE CASCADE,
    CONSTRAINT chk_marks CHECK (marks_obtained <= total_marks)
);

-- ==============================
-- Insert sample data
-- ==============================

-- Sample users (passwords are SHA-256 hashed for demo)
INSERT INTO users (username, password, role) VALUES 
('admin', '240be518fabd2724ddb6f04eeb1da5967448d7e831c08c8fa822809f74c720a9', 'admin'),
('teacher1', 'cde383eee8ee7a4400adf7a15f716f179a2eb97646b37e089eb8d6d04e663416', 'teacher'),
('teacher2', 'cde383eee8ee7a4400adf7a15f716f179a2eb97646b37e089eb8d6d04e663416', 'teacher'),
('student1', '703b0a3d6ad75b649a28adde7d83c6251da457549263bc7ff45ec709b0a8448b', 'student'),
('student2', '703b0a3d6ad75b649a28adde7d83c6251da457549263bc7ff45ec709b0a8448b', 'student'),
('student3', '703b0a3d6ad75b649a28adde7d83c6251da457549263bc7ff45ec709b0a8448b', 'student');

-- Sample teachers
INSERT INTO teachers (user_id, fullname, email, phone, department, qualification) VALUES
(2, 'John Smith', 'john.smith@school.com', '123-456-7890', 'Mathematics', 'M.Sc. Mathematics'),
(3, 'Sarah Johnson', 'sarah.johnson@school.com', '123-456-7891', 'Science', 'Ph.D. Physics');

-- Sample students
INSERT INTO students (user_id, fullname, email, phone, date_of_birth, gender, address) VALUES
(4, 'Alice Brown', 'alice.brown@student.com', '123-456-7892', '2005-03-15', 'Female', '123 Student St'),
(5, 'Bob Wilson', 'bob.wilson@student.com', '123-456-7893', '2005-07-22', 'Male', '456 Student Ave'),
(6, 'Carol Davis', 'carol.davis@student.com', '123-456-7894', '2005-11-08', 'Female', '789 Student Blvd');

-- Sample subjects
INSERT INTO subjects (subject_name, subject_code, credits, description, teacher_id) VALUES
('Mathematics', 'MATH101', 4, 'Advanced Mathematics', 1),
('Physics', 'PHY101', 4, 'Introduction to Physics', 2),
('English', 'ENG101', 3, 'English Literature', 1),
('Computer Science', 'CS101', 4, 'Programming Fundamentals', 2);

-- Sample marks
INSERT INTO marks (student_id, subject_id, teacher_id, exam_type, marks_obtained, total_marks, exam_date, semester, academic_year) VALUES
(1, 1, 1, 'Midterm', 85.5, 100.0, '2024-03-15', 'Spring 2024', '2024'),
(1, 1, 1, 'Final', 92.0, 100.0, '2024-05-20', 'Spring 2024', '2024'),
(1, 2, 2, 'Midterm', 78.0, 100.0, '2024-03-20', 'Spring 2024', '2024'),
(1, 2, 2, 'Final', 88.5, 100.0, '2024-05-25', 'Spring 2024', '2024'),
(2, 1, 1, 'Midterm', 90.0, 100.0, '2024-03-15', 'Spring 2024', '2024'),
(2, 1, 1, 'Final', 95.5, 100.0, '2024-05-20', 'Spring 2024', '2024'),
(2, 3, 1, 'Midterm', 82.0, 100.0, '2024-03-18', 'Spring 2024', '2024'),
(3, 1, 1, 'Midterm', 75.5, 100.0, '2024-03-15', 'Spring 2024', '2024'),
(3, 4, 2, 'Midterm', 88.0, 100.0, '2024-03-22', 'Spring 2024', '2024'),
(3, 4, 2, 'Final', 91.0, 100.0, '2024-05-28', 'Spring 2024', '2024');
