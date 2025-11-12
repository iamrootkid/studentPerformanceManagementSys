#!/usr/bin/env python3
"""
Setup script for Student Performance Monitoring System
"""

import subprocess
import sys
import os
import mysql.connector
from mysql.connector import Error

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 7):
        print("❌ Python 3.7 or higher is required")
        return False
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor} detected")
    return True

def install_dependencies():
    """Install required Python packages"""
    print("📦 Installing Python dependencies...")
    
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False

def check_mysql_connection():
    """Check MySQL connection"""
    print("🔍 Checking MySQL connection...")
    
    try:
        connection = mysql.connector.connect(
            host='localhost',
            user='root',
            password='',
            charset='utf8mb4',
            collation='utf8mb4_unicode_ci'
        )
        
        if connection.is_connected():
            print("✅ MySQL connection successful")
            connection.close()
            return True
    except Error as e:
        print(f"❌ MySQL connection failed: {e}")
        print("   Please ensure XAMPP is running and MySQL service is started")
        return False

def create_database():
    """Create database and tables"""
    print("🗄️ Setting up database...")
    
    try:
        # Connect to MySQL
        connection = mysql.connector.connect(
            host='localhost',
            user='root',
            password='',
            charset='utf8mb4',
            collation='utf8mb4_unicode_ci'
        )
        
        cursor = connection.cursor()
        
        # Read and execute database setup script
        with open('database_setup.sql', 'r', encoding='utf-8') as file:
            sql_commands = file.read()
        
        # Split commands and execute
        commands = sql_commands.split(';')
        for command in commands:
            command = command.strip()
            if command and not command.startswith('--'):
                try:
                    cursor.execute(command)
                    connection.commit()
                except Error as e:
                    if "already exists" not in str(e).lower():
                        print(f"⚠️ Warning: {e}")
        
        cursor.close()
        connection.close()
        print("✅ Database setup completed")
        return True
        
    except Error as e:
        print(f"❌ Database setup failed: {e}")
        return False
    except FileNotFoundError:
        print("❌ database_setup.sql file not found")
        return False

def main():
    """Main setup function"""
    print("🚀 Student Performance Monitoring System Setup")
    print("=" * 50)
    
    # Check Python version
    if not check_python_version():
        return
    
    # Install dependencies
    if not install_dependencies():
        return
    
    # Check MySQL connection
    if not check_mysql_connection():
        return
    
    # Create database
    if not create_database():
        return
    
    print("\n🎉 Setup completed successfully!")
    print("\n📋 Next steps:")
    print("   1. Run: python main.py")
    print("   2. Use demo credentials:")
    print("      - Admin: admin / admin123")
    print("      - Teacher: teacher1 / teacher123")
    print("      - Student: student1 / student123")

if __name__ == "__main__":
    main()
