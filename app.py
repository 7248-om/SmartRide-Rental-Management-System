#!/usr/bin/env python3
"""
SmartRide Vehicle Rental Management System
Flask Application Main File

Authors: [Your Names Here]
Date: 2024
Version: 1.0
"""

from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from flask_mysqldb import MySQL
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import os
from functools import wraps
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)

# Configuration
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your-secret-key-change-in-production')
app.config['MYSQL_HOST'] = os.environ.get('MYSQL_HOST', 'localhost')
app.config['MYSQL_USER'] = os.environ.get('MYSQL_USER', 'root')
app.config['MYSQL_PASSWORD'] = os.environ.get('MYSQL_PASSWORD', '')
app.config['MYSQL_DB'] = os.environ.get('MYSQL_DB', 'smartride_rental')
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

# Initialize MySQL
mysql = MySQL(app)

# Logging configuration
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Decorators
def login_required(f):
    """Decorator to require customer login"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'customer_id' not in session:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('customer_login'))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    """Decorator to require admin login"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'admin_id' not in session:
            flash('Please log in as administrator to access this page.', 'error')
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    return decorated_function

# Utility Functions
def get_db_connection():
    """Get database connection"""
    try:
        return mysql.connection
    except Exception as e:
        logger.error(f"Database connection error: {e}")
        return None

def execute_query(query, params=None, fetch_one=False, fetch_all=False):
    """Execute database query safely"""
    try:
        conn = get_db_connection()
        if conn is None:
            return None
            
        cursor = conn.cursor()
        cursor.execute(query, params or ())
        
        if fetch_one:
            result = cursor.fetchone()
        elif fetch_all:
            result = cursor.fetchall()
        else:
            conn.commit()
            result = cursor.rowcount
            
        cursor.close()
        return result
    except Exception as e:
        logger.error(f"Query execution error: {e}")
        return None

# Routes

# Home Routes
@app.route('/')
def index():
    """Homepage"""
    return render_template('index.html')

# Customer Routes
@app.route('/customer/login', methods=['GET', 'POST'])
def customer_login():
    """Customer login"""
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        # Validate customer credentials
        customer = execute_query(
            "SELECT CustomerID, Name, Email, Password FROM Customer WHERE Email = %s",
            (email,),
            fetch_one=True
        )
        
        if customer and check_password_hash(customer['Password'], password):
            session['customer_id'] = customer['CustomerID']
            session['customer_name'] = customer['Name']
            flash(f'Welcome back, {customer["Name"]}!', 'success')
            return redirect(url_for('customer_dashboard'))
        else:
            flash('Invalid email or password.', 'error')
    
    return render_template('customer/login.html')

@app.route('/customer/register', methods=['GET', 'POST'])
def customer_register():
    """Customer registration"""
    if request.method == 'POST':
        first_name = request.form['firstName']
        last_name = request.form['lastName']
        email = request.form['email']
        phone = request.form['phone']
        license_no = request.form['licenseNo']
        password = request.form['password']
        
        # Check if customer already exists
        existing_customer = execute_query(
            "SELECT CustomerID FROM Customer WHERE Email = %s OR LicenseNo = %s",
            (email, license_no),
            fetch_one=True
        )
        
        if existing_customer:
            flash('A customer with this email or license number already exists.', 'error')
            return render_template('customer/register.html')
        
        # Hash password and create customer
        hashed_password = generate_password_hash(password)
        full_name = f"{first_name} {last_name}"
        
        result = execute_query(
            """INSERT INTO Customer (Name, Email, Phone, LicenseNo, Password) 
               VALUES (%s, %s, %s, %s, %s)""",
            (full_name, email, phone, license_no, hashed_password)
        )
        
        if result:
            flash('Registration successful! Please log in.', 'success')
            return redirect(url_for('customer_login'))
        else:
            flash('Registration failed. Please try again.', 'error')
    
    return render_template('customer/register.html')

@app.route('/customer/dashboard')
@login_required
def customer_dashboard():
    """Customer dashboard"""
    customer_id = session['customer_id']
    
    # Get dashboard statistics
    stats = {}
    
    # Active rentals
    stats['active_rentals'] = execute_query(
        "SELECT COUNT(*) as count FROM Rental WHERE CustomerID = %s AND Status = 'ACTIVE'",
        (customer_id,),
        fetch_one=True
    )['count']
    
    # Completed rentals
    stats['completed_rentals'] = execute_query(
        "SELECT COUNT(*) as count FROM Rental WHERE CustomerID = %s AND Status = 'COMPLETED'",
        (customer_id,),
        fetch_one=True
    )['count']
    
    # Pending reservations
    stats['pending_reservations'] = execute_query(
        "SELECT COUNT(*) as count FROM Reservation WHERE CustomerID = %s AND Status = 'PENDING'",
        (customer_id,),
        fetch_one=True
    )['count']
    
    # Total spent
    total_spent = execute_query(
        "SELECT SUM(TotalAmount) as total FROM Rental WHERE CustomerID = %s AND Status = 'COMPLETED'",
        (customer_id,),
        fetch_one=True
    )['total'] or 0
    
    stats['total_spent'] = f"{total_spent:.2f}"
    
    # Get current rentals
    current_rentals = execute_query(
        """SELECT r.RentalID, r.StartDate, r.DueDate, v.Make, v.Model, v.PlateNo
           FROM Rental r
           JOIN Vehicle v ON r.VehicleID = v.VehicleID
           WHERE r.CustomerID = %s AND r.Status = 'ACTIVE'
           ORDER BY r.StartDate DESC
           LIMIT 5""",
        (customer_id,),
        fetch_all=True
    )
    
    # Get upcoming reservations
    upcoming_reservations = execute_query(
        """SELECT res.ResID, res.StartDate, res.EndDate, res.ResDate, vt.Name as VehicleType
           FROM Reservation res
           JOIN VehicleType vt ON res.VehicleTypeID = vt.TypeID
           WHERE res.CustomerID = %s AND res.Status = 'PENDING'
           ORDER BY res.StartDate ASC
           LIMIT 5""",
        (customer_id,),
        fetch_all=True
    )
    
    return render_template('customer/dashboard.html',
                         customer={'name': session['customer_name']},
                         **stats,
                         current_rentals=current_rentals,
                         upcoming_reservations=upcoming_reservations)

@app.route('/customer/vehicles')
@login_required
def customer_vehicles():
    """Browse available vehicles"""
    # Get filter parameters
    vehicle_type = request.args.get('vehicle_type', '')
    price_range = request.args.get('price_range', '')
    year = request.args.get('year', '')
    status = request.args.get('status', 'AVAILABLE')
    
    # Build query
    query = """
        SELECT v.VehicleID, v.Make, v.Model, v.Year, v.PlateNo, v.Status, v.RatePerDay,
               vt.TypeID, vt.Name as TypeName
        FROM Vehicle v
        JOIN VehicleType vt ON v.TypeID = vt.TypeID
        WHERE 1=1
    """
    params = []
    
    if vehicle_type:
        query += " AND vt.Name = %s"
        params.append(vehicle_type)
    
    if status:
        query += " AND v.Status = %s"
        params.append(status)
    
    if year:
        query += " AND v.Year = %s"
        params.append(year)
    
    if price_range:
        if price_range == '0-50':
            query += " AND v.RatePerDay <= 50"
        elif price_range == '51-100':
            query += " AND v.RatePerDay BETWEEN 51 AND 100"
        elif price_range == '101-200':
            query += " AND v.RatePerDay BETWEEN 101 AND 200"
        elif price_range == '201+':
            query += " AND v.RatePerDay > 200"
    
    query += " ORDER BY v.RatePerDay ASC"
    
    vehicles = execute_query(query, params, fetch_all=True) or []
    
    # Get vehicle counts by type
    vehicle_counts = {}
    for vtype in ['Car', 'Bus', 'Bike', 'Scooter']:
        count = execute_query(
            "SELECT COUNT(*) as count FROM Vehicle v JOIN VehicleType vt ON v.TypeID = vt.TypeID WHERE vt.Name = %s AND v.Status = 'AVAILABLE'",
            (vtype,),
            fetch_one=True
        )['count']
        vehicle_counts[f"{vtype.lower()}_count"] = count
    
    return render_template('customer/vehicles.html',
                         vehicles=vehicles,
                         **vehicle_counts)

@app.route('/customer/logout')
def customer_logout():
    """Customer logout"""
    session.pop('customer_id', None)
    session.pop('customer_name', None)
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('index'))

# Admin Routes
@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    """Admin login"""
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # Validate admin credentials
        admin = execute_query(
            "SELECT StaffID, Name, Role FROM Staff WHERE Name = %s AND Role = 'Admin'",
            (username,),
            fetch_one=True
        )
        
        # For demo purposes, use simple password check
        # In production, use hashed passwords
        if admin and password == 'admin123':  # Change this!
            session['admin_id'] = admin['StaffID']
            session['admin_name'] = admin['Name']
            flash(f'Welcome, {admin["Name"]}!', 'success')
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Invalid credentials.', 'error')
    
    return render_template('admin/login.html')

@app.route('/admin/dashboard')
@admin_required
def admin_dashboard():
    """Admin dashboard"""
    # Get dashboard statistics
    stats = {}
    
    # Total vehicles
    stats['total_vehicles'] = execute_query(
        "SELECT COUNT(*) as count FROM Vehicle",
        fetch_one=True
    )['count']
    
    # Vehicle status counts
    vehicle_status = execute_query(
        "SELECT Status, COUNT(*) as count FROM Vehicle GROUP BY Status",
        fetch_all=True
    ) or []
    
    for status in vehicle_status:
        if status['Status'] == 'AVAILABLE':
            stats['available_vehicles'] = status['count']
        elif status['Status'] == 'RENTED':
            stats['rented_vehicles'] = status['count']
        elif status['Status'] == 'MAINTENANCE':
            stats['maintenance_vehicles'] = status['count']
    
    # Set defaults for missing statuses
    stats.setdefault('available_vehicles', 0)
    stats.setdefault('rented_vehicles', 0)
    stats.setdefault('maintenance_vehicles', 0)
    
    # Active rentals
    stats['active_rentals'] = execute_query(
        "SELECT COUNT(*) as count FROM Rental WHERE Status = 'ACTIVE'",
        fetch_one=True
    )['count']
    
    # Overdue rentals
    stats['overdue_rentals'] = execute_query(
        "SELECT COUNT(*) as count FROM Rental WHERE Status = 'ACTIVE' AND DueDate < CURDATE()",
        fetch_one=True
    )['count']
    
    # Total customers
    stats['total_customers'] = execute_query(
        "SELECT COUNT(*) as count FROM Customer",
        fetch_one=True
    )['count']
    
    # Monthly revenue
    monthly_revenue = execute_query(
        "SELECT SUM(TotalAmount) as total FROM Rental WHERE MONTH(StartDate) = MONTH(CURDATE()) AND YEAR(StartDate) = YEAR(CURDATE())",
        fetch_one=True
    )['total'] or 0
    stats['monthly_revenue'] = f"{monthly_revenue:.2f}"
    
    # Daily revenue
    daily_revenue = execute_query(
        "SELECT SUM(TotalAmount) as total FROM Rental WHERE DATE(StartDate) = CURDATE()",
        fetch_one=True
    )['total'] or 0
    stats['daily_revenue'] = f"{daily_revenue:.2f}"
    
    # Recent rentals
    recent_rentals = execute_query(
        """SELECT r.RentalID, r.StartDate, r.DueDate, r.Status,
                  c.Name as CustomerName, v.Make, v.Model
           FROM Rental r
           JOIN Customer c ON r.CustomerID = c.CustomerID
           JOIN Vehicle v ON r.VehicleID = v.VehicleID
           ORDER BY r.StartDate DESC
           LIMIT 10""",
        fetch_all=True
    ) or []
    
    # Vehicle stats by type
    vehicle_type_stats = execute_query(
        """SELECT vt.Name, COUNT(v.VehicleID) as total,
                  SUM(CASE WHEN v.Status = 'AVAILABLE' THEN 1 ELSE 0 END) as available
           FROM VehicleType vt
           LEFT JOIN Vehicle v ON vt.TypeID = v.TypeID
           GROUP BY vt.TypeID, vt.Name""",
        fetch_all=True
    ) or []
    
    type_stats = {}
    for stat in vehicle_type_stats:
        type_name = stat['Name'].lower()
        type_stats[f"{type_name}_stats"] = {
            'total': stat['total'] or 0,
            'available': stat['available'] or 0
        }
    
    return render_template('admin/dashboard.html',
                         admin={'name': session['admin_name']},
                         current_date=datetime.now().strftime('%Y-%m-%d'),
                         current_time=datetime.now().strftime('%H:%M:%S'),
                         recent_rentals=recent_rentals,
                         **stats,
                         **type_stats)

@app.route('/admin/vehicles')
@admin_required
def admin_vehicles():
    """Admin vehicle management"""
    # Get filter parameters
    vehicle_type = request.args.get('type', '')
    status = request.args.get('status', '')
    search = request.args.get('search', '')
    page = int(request.args.get('page', 1))
    per_page = 20
    
    # Build query
    query = """
        SELECT v.VehicleID, v.Make, v.Model, v.Year, v.PlateNo, v.Status, v.RatePerDay,
               vt.Name as TypeName
        FROM Vehicle v
        JOIN VehicleType vt ON v.TypeID = vt.TypeID
        WHERE 1=1
    """
    params = []
    
    if vehicle_type:
        query += " AND vt.Name = %s"
        params.append(vehicle_type)
    
    if status:
        query += " AND v.Status = %s"
        params.append(status)
    
    if search:
        query += " AND (v.Make LIKE %s OR v.Model LIKE %s OR v.PlateNo LIKE %s)"
        search_param = f"%{search}%"
        params.extend([search_param, search_param, search_param])
    
    # Get total count for pagination
    count_query = query.replace("SELECT v.VehicleID, v.Make, v.Model, v.Year, v.PlateNo, v.Status, v.RatePerDay, vt.Name as TypeName", "SELECT COUNT(*)")
    total_vehicles = execute_query(count_query, params, fetch_one=True)['COUNT(*)']
    
    # Add pagination
    offset = (page - 1) * per_page
    query += f" ORDER BY v.VehicleID ASC LIMIT {per_page} OFFSET {offset}"
    
    vehicles = execute_query(query, params, fetch_all=True) or []
    
    total_pages = (total_vehicles + per_page - 1) // per_page
    
    return render_template('admin/vehicles.html',
                         vehicles=vehicles,
                         total_vehicles=total_vehicles,
                         page=page,
                         total_pages=total_pages)

@app.route('/admin/logout')
def admin_logout():
    """Admin logout"""
    session.pop('admin_id', None)
    session.pop('admin_name', None)
    flash('Admin logged out successfully.', 'info')
    return redirect(url_for('index'))

# Error Handlers
@app.errorhandler(404)
def page_not_found(e):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('errors/500.html'), 500

# API Routes (for AJAX calls)
@app.route('/api/dashboard/stats')
def api_dashboard_stats():
    """API endpoint for dashboard statistics"""
    if 'admin_id' not in session and 'customer_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    # Return basic stats - implement as needed
    return jsonify({
        'timestamp': datetime.now().isoformat(),
        'status': 'success'
    })

# Database initialization
def init_db():
    """Initialize database tables"""
    try:
        with app.app_context():
            # Test database connection
            conn = get_db_connection()
            if conn:
                logger.info("Database connection successful")
                return True
            else:
                logger.error("Database connection failed")
                return False
    except Exception as e:
        logger.error(f"Database initialization error: {e}")
        return False

if __name__ == '__main__':
    # Initialize database
    if init_db():
        logger.info("Starting SmartRide Vehicle Rental Management System")
        app.run(debug=True, host='0.0.0.0', port=5001)
    else:
        logger.error("Failed to initialize database. Please check your database configuration.")