#!/usr/bin/env python3
"""
SmartRide Vehicle Rental Management System
Flask Application Main File

--- CORRECTED AND COMPLETED VERSION ---
"""

from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from flask_mysqldb import MySQL
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import os
from functools import wraps
import logging
from dotenv import load_dotenv
from admin_config import ADMIN_CREDENTIALS
import io
import csv

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)

# Configuration
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your-secret-key-change-in-production')
app.config['MYSQL_HOST'] = os.environ.get('MYSQL_HOST', 'localhost')
app.config['MYSQL_USER'] = os.environ.get('MYSQL_USER', 'root')
app.config['MYSQL_PASSWORD'] = os.environ.get('MYSQL_PASSWORD', 'your-mysql-password') # Make sure to set this
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
    """Execute database query safely and return lowercase dict keys"""
    conn = get_db_connection()
    if conn is None:
        logger.error("Failed to get DB connection.")
        return None
    
    try:
        cursor = conn.cursor()  # This will be DictCursor due to app.config
        cursor.execute(query, params or ())
        
        # This normalization is required by all your templates
        def normalize_keys(row):
            return {k.lower(): v for k, v in row.items()} if row else None

        if fetch_one:
            row = cursor.fetchone()
            result = normalize_keys(row)
        elif fetch_all:
            rows = cursor.fetchall()
            result = [normalize_keys(r) for r in rows]
        else:
            conn.commit()
            result = cursor.lastrowid if cursor.description is None else cursor.rowcount
        
        cursor.close()
        return result
    except Exception as e:
        logger.error(f"Query execution error: {e}")
        conn.rollback()
        return None

# Routes

# Home Routes
@app.route('/')
def index():
    """Homepage"""
    return render_template('index.html')

# =============================================
# CUSTOMER ROUTES
# =============================================
@app.route('/customer/login', methods=['GET', 'POST'])
def customer_login():
    """Customer login"""
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        customer = execute_query(
            "SELECT CustomerID, Name, Email, Password FROM Customer WHERE Email = %s",
            (email,),
            fetch_one=True
        )
        
        # Note: Your schema uses 'Password', not 'password'
        if customer and check_password_hash(customer['password'], password):
            session['customer_id'] = customer['customerid']
            session['customer_name'] = customer['name']
            flash(f'Welcome back, {customer["name"]}!', 'success')
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
        
        existing_customer = execute_query(
            "SELECT CustomerID FROM Customer WHERE Email = %s OR LicenseNo = %s",
            (email, license_no),
            fetch_one=True
        )
        
        if existing_customer:
            flash('A customer with this email or license number already exists.', 'error')
            return render_template('customer/register.html')
        
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
    stats = {}
    
    stats['active_rentals'] = execute_query(
        "SELECT COUNT(*) as count FROM Rental WHERE CustomerID = %s AND Status = 'ACTIVE'",
        (customer_id,), fetch_one=True
    )['count']
    
    stats['completed_rentals'] = execute_query(
        "SELECT COUNT(*) as count FROM Rental WHERE CustomerID = %s AND Status = 'COMPLETED'",
        (customer_id,), fetch_one=True
    )['count']
    
    stats['pending_reservations'] = execute_query(
        "SELECT COUNT(*) as count FROM Reservation WHERE CustomerID = %s AND Status = 'PENDING'",
        (customer_id,), fetch_one=True
    )['count']
    
    # Use the SQL Function
    total_spent_result = execute_query(
        "SELECT GetCustomerTotalSpending(%s) as total",
        (customer_id,), fetch_one=True
    )
    total_spent = total_spent_result['total'] or 0
    stats['total_spent'] = f"{total_spent:.2f}"
    
    current_rentals = execute_query(
        """SELECT r.RentalID, r.StartDate, r.DueDate, v.Make, v.Model, v.PlateNo
           FROM Rental r
           JOIN Vehicle v ON r.VehicleID = v.VehicleID
           WHERE r.CustomerID = %s AND r.Status = 'ACTIVE'
           ORDER BY r.StartDate DESC LIMIT 5""",
        (customer_id,), fetch_all=True
    )
    
    upcoming_reservations = execute_query(
        """SELECT res.ResID, res.StartDate, res.EndDate, res.ResDate, vt.Name as VehicleType
           FROM Reservation res
           JOIN VehicleType vt ON res.VehicleTypeID = vt.TypeID
           WHERE res.CustomerID = %s AND res.Status = 'PENDING'
           ORDER BY res.StartDate ASC LIMIT 5""",
        (customer_id,), fetch_all=True
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
    vehicle_type = request.args.get('vehicle_type', '')
    price_range = request.args.get('price_range', '')
    year = request.args.get('year', '')
    status = request.args.get('status', 'AVAILABLE')
    
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
    
    vehicles = execute_query(query, tuple(params), fetch_all=True) or []
    
    vehicle_counts = {}
    for vtype in ['Car', 'Bus', 'Bike', 'Scooter']:
        count_result = execute_query(
            "SELECT COUNT(*) as count FROM Vehicle v JOIN VehicleType vt ON v.TypeID = vt.TypeID WHERE vt.Name = %s AND v.Status = 'AVAILABLE'",
            (vtype,), fetch_one=True
        )
        vehicle_counts[f"{vtype.lower()}_count"] = count_result['count']
    
    return render_template('customer/vehicles.html',
                         vehicles=vehicles,
                         **vehicle_counts)

@app.route('/customer/booking/new', methods=['GET', 'POST'])
@login_required
def new_booking():
    """Create a new booking"""
    if request.method == 'POST':
        try:
            vehicle_id = request.form['vehicle_id']
            start_date = request.form['start_date']
            due_date = request.form['due_date']
            customer_id = session['customer_id']
            
            # Use the SafeCreateRental stored procedure
            params = (vehicle_id, customer_id, start_date, due_date, session.get('admin_id', 1)) # Default to admin 1 if not staff
            result = execute_query(
                "CALL SafeCreateRental(%s, %s, %s, %s, %s, @p_result, @p_rental_id)",
                params
            )
            result_status = execute_query("SELECT @p_result as result, @p_rental_id as rental_id", fetch_one=True)

            if result_status and result_status['result'] == 'SUCCESS':
                flash(f"Booking successful! Your Rental ID is {result_status['rental_id']}.", 'success')
                return redirect(url_for('customer_bookings'))
            else:
                flash(f"Booking failed: {result_status['result']}", 'error')
        except Exception as e:
            flash(f"An error occurred: {e}", 'error')
        
        return redirect(url_for('new_booking', vehicle_id=request.form.get('vehicle_id')))

    # GET request
    vehicle_id = request.args.get('vehicle_id')
    vehicle = None
    if vehicle_id:
        vehicle = execute_query(
            "SELECT v.*, vt.Name as TypeName FROM Vehicle v JOIN VehicleType vt ON v.TypeID = vt.TypeID WHERE v.VehicleID = %s",
            (vehicle_id,),
            fetch_one=True
        )
        
    return render_template('customer/booking_new.html', vehicle=vehicle)

@app.route('/customer/bookings')
@login_required
def customer_bookings():
    """Show customer's all bookings"""
    customer_id = session['customer_id']
    bookings = execute_query(
        """
        SELECT r.*, v.Make, v.Model, v.PlateNo, vt.Name as TypeName
        FROM Rental r
        JOIN Vehicle v ON r.VehicleID = v.VehicleID
        JOIN VehicleType vt ON v.TypeID = vt.TypeID
        WHERE r.CustomerID = %s
        ORDER BY r.StartDate DESC
        """,
        (customer_id,),
        fetch_all=True
    )
    return render_template('customer/bookings.html', bookings=bookings or [])

@app.route('/customer/reservations', methods=['GET', 'POST'])
@login_required
def customer_reservations():
    """Show and create reservations"""
    customer_id = session['customer_id']
    
    if request.method == 'POST':
        try:
            type_id = request.form['vehicle_type_id']
            start_date = request.form['start_date']
            end_date = request.form['end_date']
            
            result = execute_query(
                """
                INSERT INTO Reservation (CustomerID, VehicleTypeID, ResDate, StartDate, EndDate)
                VALUES (%s, %s, CURDATE(), %s, %s)
                """,
                (customer_id, type_id, start_date, end_date)
            )
            if result:
                flash('Reservation made successfully!', 'success')
            else:
                flash('Failed to make reservation. Check dates.', 'error')
        except Exception as e:
            flash(f'An error occurred: {e}', 'error')
        return redirect(url_for('customer_reservations'))

    # GET Request
    reservations = execute_query(
        """
        SELECT r.*, vt.Name as TypeName
        FROM Reservation r
        JOIN VehicleType vt ON r.VehicleTypeID = vt.TypeID
        WHERE r.CustomerID = %s
        ORDER BY r.StartDate DESC
        """,
        (customer_id,),
        fetch_all=True
    )
    vehicle_types = execute_query("SELECT * FROM VehicleType", fetch_all=True)
    return render_template('customer/reservations.html', 
                           reservations=reservations or [], 
                           vehicle_types=vehicle_types or [])

@app.route('/customer/profile', methods=['GET', 'POST'])
@login_required
def customer_profile():
    """View and update customer profile"""
    customer_id = session['customer_id']
    
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        phone = request.form['phone']
        license_no = request.form['licenseNo']
        
        result = execute_query(
            """
            UPDATE Customer
            SET Name = %s, Email = %s, Phone = %s, LicenseNo = %s, UpdatedAt = CURRENT_TIMESTAMP
            WHERE CustomerID = %s
            """,
            (name, email, phone, license_no, customer_id)
        )
        
        if result:
            session['customer_name'] = name # Update session
            flash('Profile updated successfully!', 'success')
        else:
            flash('Failed to update profile. Email or License No. may already exist.', 'error')
        
        return redirect(url_for('customer_profile'))

    # GET Request
    customer = execute_query(
        "SELECT * FROM Customer WHERE CustomerID = %s",
        (customer_id,),
        fetch_one=True
    )
    return render_template('customer/profile.html', customer=customer)

@app.route('/customer/logout')
def customer_logout():
    """Customer logout"""
    session.pop('customer_id', None)
    session.pop('customer_name', None)
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('index'))

# =============================================
# ADMIN ROUTES
# =============================================
@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    """Admin login"""
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # Check against configuration file first
        if username in ADMIN_CREDENTIALS and ADMIN_CREDENTIALS[username] == password:
            admin = execute_query(
                "SELECT StaffID, Name, Role FROM Staff WHERE Name = %s",
                (username,),
                fetch_one=True
            )
            
            if not admin:
                execute_query(
                    "INSERT INTO Staff (Name, Role, Email) VALUES (%s, 'Admin', %s)",
                    (username, f"{username.lower().replace(' ', '')}@smartride.com")
                )
                admin = execute_query(
                    "SELECT StaffID, Name, Role FROM Staff WHERE Name = %s",
                    (username,),
                    fetch_one=True
                )
            
            if admin:
                session['admin_id'] = admin['staffid']
                session['admin_name'] = admin['name']
                flash(f'Welcome, {admin["name"]}!', 'success')
                return redirect(url_for('admin_dashboard'))
        
        # Fallback: check database with default password from README
        admin = execute_query(
            "SELECT StaffID, Name, Role FROM Staff WHERE Name = %s AND Role = 'Admin'",
            (username,),
            fetch_one=True
        )
        
        if admin and password == 'admin123': # Default password
            session['admin_id'] = admin['staffid']
            session['admin_name'] = admin['name']
            flash(f'Welcome, {admin["name"]}!', 'success')
            return redirect(url_for('admin_dashboard'))
        
        flash('Invalid credentials.', 'error')
    
    return render_template('admin/login.html')

@app.route('/admin/dashboard')
@admin_required
def admin_dashboard():
    """Admin dashboard"""
    stats = {}
    
    stats['total_vehicles'] = execute_query("SELECT COUNT(*) as count FROM Vehicle", fetch_one=True)['count']
    
    vehicle_status = execute_query("SELECT Status, COUNT(*) as count FROM Vehicle GROUP BY Status", fetch_all=True) or []
    stats.setdefault('available_vehicles', 0)
    stats.setdefault('rented_vehicles', 0)
    stats.setdefault('maintenance_vehicles', 0)
    for status in vehicle_status:
        if status['status'] == 'AVAILABLE':
            stats['available_vehicles'] = status['count']
        elif status['status'] == 'RENTED':
            stats['rented_vehicles'] = status['count']
        elif status['status'] == 'MAINTENANCE':
            stats['maintenance_vehicles'] = status['count']
    
    stats['active_rentals'] = execute_query("SELECT COUNT(*) as count FROM Rental WHERE Status = 'ACTIVE'", fetch_one=True)['count']
    
    # Use the View
    stats['overdue_rentals'] = execute_query("SELECT COUNT(*) as count FROM vw_overdue_rentals", fetch_one=True)['count']
    
    stats['total_customers'] = execute_query("SELECT COUNT(*) as count FROM Customer", fetch_one=True)['count']
    
    monthly_revenue = execute_query(
        "SELECT SUM(TotalAmount + FineAmount) as total FROM Rental WHERE Status='COMPLETED' AND MONTH(ReturnDate) = MONTH(CURDATE()) AND YEAR(ReturnDate) = YEAR(CURDATE())",
        fetch_one=True
    )['total'] or 0
    stats['monthly_revenue'] = f"{monthly_revenue:.2f}"
    
    daily_revenue = execute_query(
        "SELECT SUM(TotalAmount + FineAmount) as total FROM Rental WHERE Status='COMPLETED' AND DATE(ReturnDate) = CURDATE()",
        fetch_one=True
    )['total'] or 0
    stats['daily_revenue'] = f"{daily_revenue:.2f}"
    
    recent_rentals = execute_query(
        """SELECT r.RentalID, r.StartDate, r.DueDate, r.Status,
                  c.Name as CustomerName, v.Make, v.Model
           FROM Rental r
           JOIN Customer c ON r.CustomerID = c.CustomerID
           JOIN Vehicle v ON r.VehicleID = v.VehicleID
           ORDER BY r.StartDate DESC LIMIT 10""",
        fetch_all=True
    ) or []
    
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
        type_name = stat['name'].lower()
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
    vehicle_type = request.args.get('type', '')
    status = request.args.get('status', '')
    search = request.args.get('search', '')
    page = int(request.args.get('page', 1))
    per_page = 20

    base_query = """
        FROM Vehicle v
        JOIN VehicleType vt ON v.TypeID = vt.TypeID
        WHERE 1=1
    """
    params = []

    if vehicle_type:
        base_query += " AND vt.Name = %s"
        params.append(vehicle_type)
    if status:
        base_query += " AND v.Status = %s"
        params.append(status)
    if search:
        base_query += " AND (v.Make LIKE %s OR v.Model LIKE %s OR v.PlateNo LIKE %s)"
        search_param = f"%{search}%"
        params.extend([search_param, search_param, search_param])

    # Count query
    count_query = "SELECT COUNT(*) AS count " + base_query
    count_result = execute_query(count_query, tuple(params), fetch_one=True)
    total_vehicles = count_result['count'] if count_result else 0
    
    # Pagination
    offset = (page - 1) * per_page
    total_pages = (total_vehicles + per_page - 1) // per_page if total_vehicles > 0 else 1
    
    # Data query
    data_query = """
        SELECT 
            v.VehicleID, v.Make, v.Model, v.Year, v.PlateNo, v.Status, 
            v.RatePerDay, vt.Name as TypeName
    """ + base_query + f" ORDER BY v.VehicleID ASC LIMIT {per_page} OFFSET {offset}"
    
    vehicles = execute_query(data_query, tuple(params), fetch_all=True) or []
    
    return render_template(
        'admin/vehicles.html',
        vehicles=vehicles,
        total_vehicles=total_vehicles,
        page=page,
        total_pages=total_pages
    )

@app.route('/admin/vehicles/add', methods=['GET', 'POST'])
@admin_required
def admin_add_vehicle():
    if request.method == 'POST':
        try:
            type_id = request.form['type_id']
            make = request.form['make']
            model = request.form['model']
            plate_no = request.form['plate_no']
            year = request.form['year']
            rate = request.form['rate']
            
            result = execute_query(
                """
                INSERT INTO Vehicle (TypeID, Make, Model, PlateNo, Year, RatePerDay)
                VALUES (%s, %s, %s, %s, %s, %s)
                """,
                (type_id, make, model, plate_no, year, rate)
            )
            if result:
                flash('Vehicle added successfully!', 'success')
                return redirect(url_for('admin_vehicles'))
            else:
                flash('Failed to add vehicle. Plate No. may already exist.', 'error')
        except Exception as e:
            flash(f'An error occurred: {e}', 'error')
        
        return redirect(url_for('admin_add_vehicle'))

    # GET Request
    vehicle_types = execute_query("SELECT * FROM VehicleType ORDER BY Name", fetch_all=True)
    return render_template('admin/vehicle_add.html', vehicle_types=vehicle_types or [])

@app.route('/admin/vehicles/<int:vehicle_id>')
@admin_required
def admin_vehicle_detail(vehicle_id):
    """View vehicle details"""
    vehicle = execute_query(
        "SELECT v.*, vt.Name as TypeName FROM Vehicle v JOIN VehicleType vt ON v.TypeID = vt.TypeID WHERE v.VehicleID = %s",
        (vehicle_id,),
        fetch_one=True
    )
    if not vehicle:
        flash('Vehicle not found.', 'error')
        return redirect(url_for('admin_vehicles'))
    
    rentals = execute_query(
        "SELECT r.*, c.Name as CustomerName FROM Rental r JOIN Customer c ON r.CustomerID = c.CustomerID WHERE r.VehicleID = %s ORDER BY r.StartDate DESC",
        (vehicle_id,),
        fetch_all=True
    )
    return render_template('admin/vehicle_detail.html', vehicle=vehicle, rentals=rentals or [])

@app.route('/admin/vehicles/<int:vehicle_id>/edit', methods=['GET', 'POST'])
@admin_required
def admin_edit_vehicle(vehicle_id):
    """Edit vehicle details"""
    if request.method == 'POST':
        try:
            type_id = request.form['type_id']
            make = request.form['make']
            model = request.form['model']
            plate_no = request.form['plate_no']
            year = request.form['year']
            rate = request.form['rate']
            status = request.form['status']
            
            result = execute_query(
                """
                UPDATE Vehicle
                SET TypeID = %s, Make = %s, Model = %s, PlateNo = %s, 
                    Year = %s, RatePerDay = %s, Status = %s
                WHERE VehicleID = %s
                """,
                (type_id, make, model, plate_no, year, rate, status, vehicle_id)
            )
            if result:
                flash('Vehicle updated successfully!', 'success')
            else:
                flash('Failed to update vehicle. Plate No. may already exist.', 'error')
        except Exception as e:
            flash(f'An error occurred: {e}', 'error')
        
        return redirect(url_for('admin_edit_vehicle', vehicle_id=vehicle_id))

    # GET Request
    vehicle = execute_query(
        "SELECT * FROM Vehicle WHERE VehicleID = %s",
        (vehicle_id,),
        fetch_one=True
    )
    if not vehicle:
        flash('Vehicle not found.', 'error')
        return redirect(url_for('admin_vehicles'))
        
    vehicle_types = execute_query("SELECT * FROM VehicleType ORDER BY Name", fetch_all=True)
    return render_template('admin/vehicle_edit.html', vehicle=vehicle, vehicle_types=vehicle_types or [])

@app.route('/admin/vehicles/<int:vehicle_id>/delete', methods=['POST'])
@admin_required
def admin_delete_vehicle(vehicle_id):
    """Delete a vehicle"""
    try:
        result = execute_query("DELETE FROM Vehicle WHERE VehicleID = %s", (vehicle_id,))
        if result:
            flash('Vehicle deleted successfully.', 'success')
        else:
            flash('Failed to delete vehicle. It may be associated with rentals.', 'error')
    except Exception as e:
        flash(f'An error occurred: {e}', 'error')
    
    return redirect(url_for('admin_vehicles'))

@app.route('/admin/vehicles/<int:vehicle_id>/maintenance', methods=['POST'])
@admin_required
def admin_vehicle_maintenance(vehicle_id):
    """Set vehicle to maintenance"""
    try:
        # First, create a maintenance record
        result = execute_query(
            "INSERT INTO Maintenance (VehicleID, Date, Description, Cost, Status) VALUES (%s, CURDATE(), %s, 0, 'IN_PROGRESS')",
            (vehicle_id, 'Admin-initiated maintenance')
        )
        # This will trigger the tr_maintenance_update_vehicle_status trigger,
        # which sets the vehicle status to 'MAINTENANCE'.
        if result:
            return jsonify({'success': True, 'message': 'Vehicle set to maintenance.'})
        else:
            return jsonify({'success': False, 'message': 'Failed to create maintenance record.'}), 500
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/admin/vehicles/export')
@admin_required
def admin_export_vehicles():
    """Export vehicles to CSV"""
    vehicles = execute_query(
        """
        SELECT v.VehicleID, vt.Name as Type, v.Make, v.Model, v.Year, v.PlateNo, v.RatePerDay, v.Status
        FROM Vehicle v
        JOIN VehicleType vt ON v.TypeID = vt.TypeID
        ORDER BY v.VehicleID
        """,
        fetch_all=True
    )
    
    if not vehicles:
        flash('No vehicles to export.', 'info')
        return redirect(url_for('admin_vehicles'))
        
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Write header
    writer.writerow(vehicles[0].keys())
    # Write data
    for vehicle in vehicles:
        writer.writerow(vehicle.values())
        
    output.seek(0)
    return (
        output.getvalue(),
        200,
        {
            'Content-Type': 'text/csv',
            'Content-Disposition': 'attachment; filename="vehicles_export.csv"',
        },
    )

@app.route('/admin/customers')
@admin_required
def admin_customers():
    """Show all customers"""
    search = request.args.get('search', '')
    query = "SELECT * FROM Customer"
    params = []
    
    if search:
        query += " WHERE Name LIKE %s OR Email LIKE %s OR LicenseNo LIKE %s"
        search_param = f"%{search}%"
        params.extend([search_param, search_param, search_param])
        
    query += " ORDER BY Name"
    customers = execute_query(query, tuple(params), fetch_all=True)
    return render_template('admin/customers.html', customers=customers or [])

@app.route('/admin/customers/add', methods=['GET', 'POST'])
@admin_required
def admin_add_customer():
    """Admin adds new customer"""
    if request.method == 'POST':
        first_name = request.form['firstName']
        last_name = request.form['lastName']
        email = request.form['email']
        phone = request.form['phone']
        license_no = request.form['licenseNo']
        password = request.form['password']
        
        existing_customer = execute_query(
            "SELECT CustomerID FROM Customer WHERE Email = %s OR LicenseNo = %s",
            (email, license_no),
            fetch_one=True
        )
        
        if existing_customer:
            flash('A customer with this email or license number already exists.', 'error')
        else:
            hashed_password = generate_password_hash(password)
            full_name = f"{first_name} {last_name}"
            
            result = execute_query(
                """INSERT INTO Customer (Name, Email, Phone, LicenseNo, Password) 
                   VALUES (%s, %s, %s, %s, %s)""",
                (full_name, email, phone, license_no, hashed_password)
            )
            
            if result:
                flash('Customer added successfully!', 'success')
                return redirect(url_for('admin_customers'))
            else:
                flash('Failed to add customer.', 'error')
    
    return render_template('admin/customer_add.html')

@app.route('/admin/rentals')
@admin_required
def admin_rentals():
    """Show all rentals"""
    rentals = execute_query("SELECT * FROM vw_rental_history ORDER BY StartDate DESC", fetch_all=True)
    return render_template('admin/rentals.html', rentals=rentals or [], title="All Rentals")

@app.route('/admin/rentals/active')
@admin_required
def admin_active_rentals():
    rentals = execute_query("SELECT * FROM vw_rental_history WHERE Status = 'ACTIVE' ORDER BY StartDate DESC", fetch_all=True)
    return render_template('admin/rentals.html', rentals=rentals or [], title="Active Rentals")

@app.route('/admin/rentals/overdue')
@admin_required
def admin_overdue_rentals():
    rentals = execute_query("SELECT * FROM vw_overdue_rentals ORDER BY DaysOverdue DESC", fetch_all=True)
    return render_template('admin/rentals.html', rentals=rentals or [], title="Overdue Rentals")

@app.route('/admin/reservations')
@admin_required
def admin_reservations():
    reservations = execute_query(
        """
        SELECT r.*, vt.Name as TypeName, c.Name as CustomerName
        FROM Reservation r
        JOIN VehicleType vt ON r.VehicleTypeID = vt.TypeID
        JOIN Customer c ON r.CustomerID = c.CustomerID
        ORDER BY r.StartDate DESC
        """,
        fetch_all=True
    )
    return render_template('admin/reservations.html', reservations=reservations or [])

@app.route('/admin/reports')
@admin_required
def admin_reports():
    """Generate reports"""
    # Example: Use the cursor procedure
    month = request.args.get('month', datetime.now().month)
    year = request.args.get('year', datetime.now().year)
    
    execute_query(f"CALL GenerateMonthlyRevenueReport({month}, {year})")
    report_data = execute_query("SELECT * FROM temp_monthly_report", fetch_all=True)
    
    return render_template('admin/reports.html', report_data=report_data or [], month=month, year=year)

@app.route('/admin/admin-management')
@admin_required
def admin_management():
    """Admin account management"""
    admins = execute_query(
        "SELECT StaffID, Name, Role, Email FROM Staff WHERE Role = 'Admin' ORDER BY Name",
        fetch_all=True
    ) or []
    
    return render_template('admin/admin_management.html', admins=admins)

@app.route('/admin/admin-management/add', methods=['POST'])
@admin_required
def add_admin():
    """Add new admin"""
    name = request.form['name']
    email = request.form.get('email', '')
    phone = request.form.get('phone', '')
    
    existing = execute_query(
        "SELECT StaffID FROM Staff WHERE Name = %s",
        (name,),
        fetch_one=True
    )
    
    if existing:
        flash('Admin with this name already exists.', 'error')
    else:
        result = execute_query(
            "INSERT INTO Staff (Name, Role, Email, Phone) VALUES (%s, 'Admin', %s, %s)",
            (name, email or None, phone or None)
        )
        
        if result:
            flash(f'Admin "{name}" added successfully!', 'success')
        else:
            flash('Failed to add admin.', 'error')
    
    return redirect(url_for('admin_management'))

@app.route('/admin/admin-management/edit', methods=['POST'])
@admin_required
def edit_admin():
    """Edit admin"""
    admin_id = request.form['admin_id']
    name = request.form['name']
    email = request.form.get('email', '')
    
    result = execute_query(
        "UPDATE Staff SET Name = %s, Email = %s WHERE StaffID = %s",
        (name, email or None, admin_id)
    )
    
    if result:
        flash('Admin updated successfully!', 'success')
    else:
        flash('Failed to update admin.', 'error')
    
    return redirect(url_for('admin_management'))

@app.route('/admin/admin-management/delete', methods=['POST'])
@admin_required
def delete_admin():
    """Delete admin"""
    admin_id = request.form['admin_id']
    
    if int(admin_id) == session.get('admin_id'):
        flash('You cannot delete your own account.', 'error')
        return redirect(url_for('admin_management'))
    
    result = execute_query(
        "DELETE FROM Staff WHERE StaffID = %s AND Role = 'Admin'",
        (admin_id,)
    )
    
    if result:
        flash('Admin deleted successfully!', 'success')
    else:
        flash('Failed to delete admin.', 'error')
    
    return redirect(url_for('admin_management'))

@app.route('/admin/logout')
def admin_logout():
    """Admin logout"""
    session.pop('admin_id', None)
    session.pop('admin_name', None)
    flash('Admin logged out successfully.', 'info')
    return redirect(url_for('index'))

# -------------------------------
# Admin Quick Action & Other Routes
# -------------------------------

@app.route('/admin/maintenance')
@admin_required
def admin_maintenance():
    maintenance = execute_query(
        """
        SELECT m.*, v.Make, v.Model, v.PlateNo
        FROM Maintenance m
        JOIN Vehicle v ON m.VehicleID = v.VehicleID
        ORDER BY m.Date DESC
        """,
        fetch_all=True
    )
    return render_template('admin/maintenance.html', maintenance_records=maintenance or [])

@app.route('/admin/rentals/return')
@admin_required
def admin_process_return():
    # This should be a real page to search for a rental ID
    flash("This is a placeholder. A real page would let you search for a rental to return.", "info")
    return render_template('admin/rentals.html', rentals=[], title="Process Return")

@app.route('/admin/profile')
@admin_required
def admin_profile():
    return render_template('admin/profile.html')
    
@app.route('/admin/settings')
@admin_required
def admin_settings():
    return render_template('admin/settings.html')


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
    
    return jsonify({
        'timestamp': datetime.now().isoformat(),
        'status': 'success'
    })

# Database initialization
def init_db():
    """Initialize database tables"""
    try:
        with app.app_context():
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
    if not app.config.get('MYSQL_PASSWORD'):
        logger.error("MYSQL_PASSWORD is not set. Please set it in your .env file or environment variables.")
    elif init_db():
        logger.info("Starting SmartRide Vehicle Rental Management System")
        app.run(debug=True, host='0.0.0.0', port=5000)
    else:
        logger.error("Failed to initialize database. Please check your database configuration and credentials.")