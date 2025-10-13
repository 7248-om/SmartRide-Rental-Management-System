#!/usr/bin/env python3
"""
SmartRide - Simple Test Version (No Database)
"""

from flask import Flask, render_template

app = Flask(__name__)
app.config['SECRET_KEY'] = 'test-key'

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/customer/login')
def customer_login():
    return render_template('customer/login.html')

@app.route('/customer/register')
def customer_register():
    return render_template('customer/register.html')

@app.route('/admin/login')
def admin_login():
    return render_template('admin/login.html')

@app.route('/customer/dashboard')
def customer_dashboard():
    # Sample data for display
    return render_template('customer/dashboard.html',
                         customer={'name': 'Test Customer'},
                         active_rentals=2,
                         completed_rentals=5,
                         pending_reservations=1,
                         total_spent="450.00",
                         current_rentals=[],
                         upcoming_reservations=[])

@app.route('/admin/dashboard')
def admin_dashboard():
    # Sample data for display
    return render_template('admin/dashboard.html',
                         admin={'name': 'Test Admin'},
                         current_date='2024-10-13',
                         current_time='10:20:00',
                         total_vehicles=15,
                         available_vehicles=12,
                         rented_vehicles=2,
                         maintenance_vehicles=1,
                         active_rentals=2,
                         overdue_rentals=0,
                         total_customers=25,
                         monthly_revenue="2500.00",
                         daily_revenue="150.00",
                         recent_rentals=[])

@app.route('/customer/vehicles')
def customer_vehicles():
    # Sample vehicles data
    sample_vehicles = [
        {
            'vehicle_id': 1,
            'make': 'Toyota',
            'model': 'Camry',
            'year': 2023,
            'plate_no': 'ABC123',
            'rate_per_day': 45.00,
            'status': 'AVAILABLE',
            'type_name': 'Car',
            'type_id': 1
        },
        {
            'vehicle_id': 2,
            'make': 'Honda',
            'model': 'Civic',
            'year': 2022,
            'plate_no': 'XYZ789',
            'rate_per_day': 40.00,
            'status': 'AVAILABLE',
            'type_name': 'Car',
            'type_id': 1
        }
    ]
    
    return render_template('customer/vehicles.html',
                         vehicles=sample_vehicles,
                         car_count=10,
                         bus_count=3,
                         bike_count=8,
                         scooter_count=4)

@app.route('/admin/vehicles')
def admin_vehicles():
    # Sample vehicles data
    sample_vehicles = [
        {
            'vehicle_id': 1,
            'make': 'Toyota',
            'model': 'Camry',
            'year': 2023,
            'plate_no': 'ABC123',
            'rate_per_day': 45.00,
            'status': 'AVAILABLE',
            'type_name': 'Car'
        },
        {
            'vehicle_id': 2,
            'make': 'Honda',
            'model': 'Civic',
            'year': 2022,
            'plate_no': 'XYZ789',
            'rate_per_day': 40.00,
            'status': 'RENTED',
            'type_name': 'Car'
        }
    ]
    
    return render_template('admin/vehicles.html',
                         vehicles=sample_vehicles,
                         total_vehicles=15,
                         page=1,
                         total_pages=1)

if __name__ == '__main__':
    print("🚀 Starting SmartRide Test Server...")
    print("📱 Open your browser and go to: http://localhost:5001")
    print("🎯 This is a demo version with sample data (no database required)")
    app.run(debug=True, host='0.0.0.0', port=5001)
