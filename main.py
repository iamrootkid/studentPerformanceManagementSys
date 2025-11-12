#!/usr/bin/env python3
"""
Main entry point for Student Performance Monitoring System
"""

import sys
import os
from database import db
import admin

def main():
    """Main application function"""
    print("Starting Student Performance Monitoring System...")
    
    # Check database connection
    if not db.connection or not db.connection.is_connected():
        print("[ERROR] Database connection failed. Please ensure:")
        print("   1. XAMPP is running")
        print("   2. MySQL service is started")
        print("   3. Database 'student_performance_db' exists")
        print("   4. Run database_setup.sql in phpMyAdmin")
        return
    
    print("[OK] Database connection successful")
    print("Launching Admin Dashboard...")
    
    # Start the application directly in Admin Dashboard
    try:
        # Try to fetch an existing admin user from DB; fallback to a stub
        admin_user_result = db.execute_query("SELECT user_id, username, role FROM users WHERE role = 'admin' LIMIT 1")
        if admin_user_result and len(admin_user_result) > 0:
            admin_user = admin_user_result[0]
        else:
            admin_user = {"user_id": 0, "username": "admin", "role": "admin"}

        dashboard = admin.AdminDashboard(admin_user)
        dashboard.run()
    except Exception as e:
        print(f"[ERROR] Application error: {e}")
    finally:
        # Close database connection
        db.close()

if __name__ == "__main__":
    main()
