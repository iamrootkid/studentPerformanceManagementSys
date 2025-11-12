# Interactive Student Academic Performance Monitoring & Comparative Analysis Tool

A comprehensive GUI-based application for monitoring and analyzing student academic performance.

## 🎯 Features

- **Multi-role Access**: Admin, Teacher, and Student dashboards
- **Performance Monitoring**: Track grades, attendance, and progress
- **Performance Dashboard**: Modern visual dashboard with interactive charts
  - Donut charts for student distribution by grade and gender
  - Grouped bar charts for examination results by subject
  - Horizontal bar charts for participation rates
  - Gauge charts for average subject scores
  - Interactive filters for year and grade selection
- **Comparative Analysis**: Compare student performance across subjects and time periods
- **Graphical Reports**: Visual charts and analytics using matplotlib
- **Database Management**: MySQL backend with secure authentication

## 🏗️ Project Structure

```
python_project/
├── main.py                 # Application entry point
├── database.py            # Database connection and operations
├── database_setup.sql     # Database schema and sample data
├── requirements.txt       # Python dependencies
├── performance_dashboard.py # Modern performance dashboard with charts
├── demo_dashboard.py      # Demo script for showcasing dashboards
├── login.py              # Login window
├── admin.py              # Admin interface
├── teacher.py            # Teacher interface with performance dashboard
├── student.py            # Student interface with performance dashboard
└── test_*.py            # Test files
```

## 🛠️ Setup Instructions

1. **Install Python 3.x**
2. **Install XAMPP** (for MySQL)
3. **Install dependencies**: `pip install -r requirements.txt`
4. **Run setup script**: `python setup.py`
5. **Start application**: `python main.py`
6. **Demo dashboards**: `python demo_dashboard.py`

## 🔐 Demo Credentials

- **Admin**: admin / admin123
- **Teacher**: teacher1 / teacher123  
- **Student**: student1 / student123

## 📊 Database Schema

- `users` - User authentication
- `students` - Student profiles
- `teachers` - Teacher profiles
- `subjects` - Course information
- `marks` - Academic performance data

# studentPerformanceManagementSys