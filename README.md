# SmartRide Vehicle Rental Management System

A comprehensive web-based vehicle rental management system built with Flask (Python), MySQL, HTML, CSS, and Bootstrap. This system provides both customer and administrative interfaces for managing vehicle rentals, reservations, and maintenance.

## 🚗 Features

### Customer Portal
- **User Authentication**: Secure registration and login system
- **Vehicle Browsing**: Search and filter available vehicles by type, price, year
- **Rental Booking**: Book vehicles with automatic pricing calculation
- **Reservation System**: Reserve vehicles for future dates
- **Dashboard**: View active rentals, booking history, and spending summary
- **Profile Management**: Update personal information and license details

### Admin Portal
- **Comprehensive Dashboard**: Real-time statistics and system overview
- **Vehicle Management**: Add, edit, delete, and track vehicle status
- **Customer Management**: View and manage customer information
- **Rental Processing**: Process new rentals and vehicle returns
- **Maintenance Tracking**: Schedule and track vehicle maintenance
- **Reporting**: Generate revenue and usage reports
- **Staff Management**: Manage system users and roles

### Database Features
- **7 Entities**: VehicleType, Vehicle, Customer, Staff, Rental, Reservation, Maintenance
- **Multiple Relationships**: 1:N and M:N relationships with proper normalization (BCNF)
- **4 Triggers**: Automatic status updates and data validation
- **3 Stored Procedures**: Rental processing, return handling, and amount calculations
- **3 Functions**: Customer spending, vehicle availability, and age calculations
- **Cursor Implementation**: Monthly revenue reporting
- **Exception Handling**: Safe rental creation with error handling
- **Views**: Pre-defined queries for common operations

## 🛠 Technology Stack

- **Backend**: Python 3.8+ with Flask framework
- **Database**: MySQL 8.0+
- **Frontend**: HTML5, CSS3, Bootstrap 5.3, JavaScript
- **Authentication**: Werkzeug password hashing
- **Database ORM**: Flask-MySQLdb

## 📋 Requirements

### Software Requirements
- Python 3.8 or higher
- MySQL 8.0 or higher
- Web browser (Chrome, Firefox, Safari, Edge)

### Python Dependencies
All dependencies are listed in `requirements.txt`:
- Flask==2.3.3
- Flask-MySQLdb==1.0.1
- Werkzeug==2.3.7
- mysqlclient==2.2.0
- python-dotenv==1.0.0

## 🚀 Installation & Setup

### 1. Clone the Repository
```bash
git clone <repository-url>
cd SmartRide-Rental-Management-System
```

### 2. Set Up Python Environment
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Database Setup

#### Install MySQL (if not already installed)
- **Windows**: Download MySQL Installer from https://dev.mysql.com/downloads/installer/
- **macOS**: Use Homebrew: `brew install mysql`
- **Linux**: `sudo apt-get install mysql-server` (Ubuntu/Debian)

#### Create Database
```bash
# Login to MySQL
mysql -u root -p

# Run the database schema
source database/smartride_schema.sql
```

Or import the schema file through MySQL Workbench or phpMyAdmin.

### 4. Environment Configuration
Create a `.env` file in the project root (optional):
```env
SECRET_KEY=your-super-secret-key-change-in-production
MYSQL_HOST=localhost
MYSQL_USER=root
MYSQL_PASSWORD=your-mysql-password
MYSQL_DB=smartride_rental
```

### 5. Run the Application
```bash
python app.py
```

The application will be available at: http://localhost:5000

## 👥 Default Login Credentials

### Admin Access
- **Username**: John Admin
- **Password**: admin123

### Test Customer Accounts
All test customers use password: `password123`
- **Email**: alice@email.com
- **Email**: bob@email.com  
- **Email**: carol@email.com
- **Email**: david@email.com

## 📁 Project Structure

```
SmartRide-Rental-Management-System/
├── app.py                      # Main Flask application
├── requirements.txt            # Python dependencies
├── README.md                  # Project documentation
├── database/
│   └── smartride_schema.sql   # Complete database schema
├── templates/
│   ├── base.html             # Base template
│   ├── index.html            # Homepage
│   ├── customer/             # Customer templates
│   │   ├── login.html
│   │   ├── register.html
│   │   ├── dashboard.html
│   │   └── vehicles.html
│   └── admin/                # Admin templates
│       ├── login.html
│       ├── dashboard.html
│       └── vehicles.html
└── static/
    ├── css/
    │   └── style.css         # Custom styles
    └── js/
        └── script.js         # Custom JavaScript
```

## 🗄 Database Schema

### Entities & Relationships
1. **VehicleType** (1:N) **Vehicle** - Vehicle categorization
2. **Vehicle** (1:N) **Rental** - Vehicle rental tracking
3. **Customer** (1:N) **Rental** - Customer rental history
4. **Customer** (1:N) **Reservation** - Customer reservations
5. **Staff** (1:N) **Rental** - Staff processing rentals
6. **Vehicle** (1:N) **Maintenance** - Vehicle maintenance records

### Key Business Rules (Implemented via Triggers/Procedures)
- Vehicles must be AVAILABLE to be rented
- Rental dates cannot be in the past
- Due date must be after start date
- Vehicle status automatically updates when rented/returned
- Fine calculation for overdue returns (10% of daily rate per day)
- Automatic status updates for overdue rentals

## 🎨 Features Demonstration

### Customer Features
1. **Registration & Login**: Secure account creation with password hashing
2. **Vehicle Search**: Filter by type, price range, year, availability
3. **Booking Process**: Select dates, view pricing, confirm booking
4. **Dashboard Analytics**: View rental statistics and history
5. **Profile Management**: Update contact and license information

### Admin Features
1. **System Dashboard**: Real-time metrics and alerts
2. **Vehicle Fleet Management**: CRUD operations with status tracking
3. **Customer Management**: View customer details and rental history
4. **Rental Processing**: Create rentals, process returns, calculate fines
5. **Maintenance Scheduling**: Track vehicle maintenance and costs
6. **Reporting**: Generate revenue and usage reports

## 🔧 Database Advanced Features

### Stored Procedures
- `CalculateRentalAmount()` - Calculates total rental cost
- `ProcessVehicleReturn()` - Handles vehicle returns with fine calculation
- `CreateNewRental()` - Creates new rental with validation
- `SafeCreateRental()` - Rental creation with exception handling
- `GenerateMonthlyRevenueReport()` - Revenue reporting using cursors

### Functions
- `GetCustomerTotalSpending()` - Customer's total expenditure
- `IsVehicleAvailable()` - Check vehicle availability for dates
- `GetVehicleAge()` - Calculate vehicle age

### Triggers
- `tr_rental_insert_update_vehicle` - Update vehicle status on rental
- `tr_rental_validate_dates` - Validate rental dates
- `tr_maintenance_update_vehicle_status` - Set maintenance status
- `tr_reservation_validate_dates` - Validate reservation dates

### Views
- `vw_available_vehicles` - Available vehicles with details
- `vw_rental_history` - Complete rental history
- `vw_overdue_rentals` - Overdue rentals with fine calculations

## 🧪 Testing the System

1. **Admin Login**: Use admin credentials to access management features
2. **Add Vehicles**: Create different types of vehicles with various rates
3. **Customer Registration**: Create customer accounts with valid license numbers
4. **Make Bookings**: Test the booking process with different scenarios
5. **Process Returns**: Test return processing with on-time and overdue scenarios
6. **Generate Reports**: Use the reporting features to analyze data
7. **Test Triggers**: Create rentals and observe automatic status updates

## 📊 Sample Data Included

The database schema includes sample data:
- 4 Vehicle types (Car, Bus, Bike, Scooter)
- 15 Sample vehicles across all types
- 4 Test customers with hashed passwords
- 3 Staff members with different roles
- Sample rental and reservation records
- Maintenance history examples

## 🎯 Academic Project Requirements Met

✅ **Application Definition**: Vehicle Rental Management System
✅ **Group Project**: Designed for 2-student teams
✅ **4 Entities**: VehicleType, Vehicle, Customer, Staff (+3 more: Rental, Reservation, Maintenance)
✅ **4-5 Relationships**: Multiple relationship types with different cardinalities
✅ **BCNF Normalization**: All tables properly normalized
✅ **CRUD Operations**: Complete Create, Read, Update, Delete functionality
✅ **3+ Triggers**: 4 triggers for business rule enforcement
✅ **3+ Procedures**: Multiple stored procedures with complex logic
✅ **Cursors**: Revenue report generation using cursors
✅ **Functions**: 3 custom functions for calculations and validations
✅ **Exception Handling**: Safe procedures with error handling
✅ **Web Integration**: Complete web interface with database connectivity

## 🚀 Future Enhancements

- Payment gateway integration
- Email notifications for reservations and overdue rentals
- Mobile application
- Advanced reporting with charts and graphs
- GPS tracking integration
- Multi-location support
- Inventory management
- Customer feedback system

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is developed for academic purposes. Feel free to use it for educational projects.

## 👨‍💻 Authors

- [Student Name 1] - Development & Database Design
- [Student Name 2] - Frontend & System Integration

## 📞 Support

For any questions or issues, please create an issue in the repository or contact the development team.

---

**Note**: This system is designed for educational purposes and demonstrates various database concepts and web development practices. For production use, additional security measures and testing would be required.