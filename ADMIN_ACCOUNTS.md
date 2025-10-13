# SmartRide Admin Accounts

## Available Admin Login Credentials

### Method 1: Configured Accounts (admin_config.py)
| Username | Password | Notes |
|----------|----------|-------|
| `John Admin` | `admin123` | Original admin |
| `Admin User1` | `password123` | Added admin |
| `Admin User2` | `admin456` | Added admin |
| `admin` | `admin` | Simple login |
| `superadmin` | `super123` | Super admin |

### Method 2: Database Accounts
These are stored in the Staff table and use the default password `admin123`:
- Any admin in the Staff table with Role = 'Admin'

## How to Add More Admin Accounts

### Option 1: Edit admin_config.py (Recommended)
```python
ADMIN_CREDENTIALS = {
    "John Admin": "admin123",
    "Admin User1": "password123", 
    "Admin User2": "admin456",
    "admin": "admin",
    "superadmin": "super123",
    # Add your own here:
    "YourName": "YourPassword",
    "Student1": "student123",
    "Student2": "project123"
}
```

### Option 2: Use Admin Management Interface
1. Login as any existing admin
2. Go to Admin Dashboard
3. Click your name → "Admin Management"
4. Add new admin accounts through the web interface

### Option 3: Direct MySQL Commands
```sql
INSERT INTO Staff (Name, Role, Email, Phone) VALUES 
('New Admin', 'Admin', 'newadmin@smartride.com', '123-456-7895');
```

## Login URLs
- Admin Login: http://localhost:5000/admin/login
- Admin Dashboard: http://localhost:5000/admin/dashboard
- Admin Management: http://localhost:5000/admin/admin-management

## Notes
- The system checks admin_config.py first, then falls back to database
- You can have unlimited admin accounts
- Each admin has full system access
- Admins cannot delete their own accounts