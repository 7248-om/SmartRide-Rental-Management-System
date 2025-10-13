-- =============================================
-- SmartRide Vehicle Rental Management System
-- MySQL Database Schema (Fixed Version)
-- =============================================

-- Create database
CREATE DATABASE IF NOT EXISTS smartride_rental;
USE smartride_rental;

-- Drop existing tables (for clean setup)
DROP TABLE IF EXISTS Maintenance;
DROP TABLE IF EXISTS Rental;
DROP TABLE IF EXISTS Reservation;
DROP TABLE IF EXISTS Vehicle;
DROP TABLE IF EXISTS VehicleType;
DROP TABLE IF EXISTS Customer;
DROP TABLE IF EXISTS Staff;

-- =============================================
-- ENTITY TABLES
-- =============================================

-- 1. VehicleType Entity
CREATE TABLE VehicleType (
    TypeID INT PRIMARY KEY AUTO_INCREMENT,
    Name VARCHAR(50) NOT NULL UNIQUE,
    Description TEXT,
    CreatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. Vehicle Entity  
CREATE TABLE Vehicle (
    VehicleID INT PRIMARY KEY AUTO_INCREMENT,
    TypeID INT NOT NULL,
    Make VARCHAR(50) NOT NULL,
    Model VARCHAR(50) NOT NULL,
    PlateNo VARCHAR(20) NOT NULL UNIQUE,
    Year YEAR NOT NULL,
    Status ENUM('AVAILABLE', 'RENTED', 'MAINTENANCE') DEFAULT 'AVAILABLE',
    RatePerDay DECIMAL(10,2) NOT NULL,
    CreatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UpdatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (TypeID) REFERENCES VehicleType(TypeID) ON DELETE RESTRICT
);

-- 3. Customer Entity
CREATE TABLE Customer (
    CustomerID INT PRIMARY KEY AUTO_INCREMENT,
    Name VARCHAR(100) NOT NULL,
    Email VARCHAR(100) NOT NULL UNIQUE,
    Phone VARCHAR(15) NOT NULL,
    LicenseNo VARCHAR(20) NOT NULL UNIQUE,
    Password VARCHAR(255) NOT NULL,
    CreatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UpdatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- 4. Staff Entity
CREATE TABLE Staff (
    StaffID INT PRIMARY KEY AUTO_INCREMENT,
    Name VARCHAR(100) NOT NULL,
    Role ENUM('Admin', 'Manager', 'Staff') NOT NULL,
    Email VARCHAR(100) UNIQUE,
    Phone VARCHAR(15),
    CreatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 5. Rental Entity
CREATE TABLE Rental (
    RentalID INT PRIMARY KEY AUTO_INCREMENT,
    VehicleID INT NOT NULL,
    CustomerID INT NOT NULL,
    StartDate DATE NOT NULL,
    DueDate DATE NOT NULL,
    ReturnDate DATE NULL,
    DailyRate DECIMAL(10,2) NOT NULL,
    TotalAmount DECIMAL(10,2) NOT NULL,
    FineAmount DECIMAL(10,2) DEFAULT 0.00,
    Status ENUM('ACTIVE', 'COMPLETED', 'OVERDUE', 'CANCELLED') DEFAULT 'ACTIVE',
    ProcessedBy INT,
    CreatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UpdatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (VehicleID) REFERENCES Vehicle(VehicleID) ON DELETE RESTRICT,
    FOREIGN KEY (CustomerID) REFERENCES Customer(CustomerID) ON DELETE RESTRICT,
    FOREIGN KEY (ProcessedBy) REFERENCES Staff(StaffID) ON DELETE SET NULL
);

-- 6. Reservation Entity
CREATE TABLE Reservation (
    ResID INT PRIMARY KEY AUTO_INCREMENT,
    CustomerID INT NOT NULL,
    VehicleTypeID INT NOT NULL,
    ResDate DATE NOT NULL,
    StartDate DATE NOT NULL,
    EndDate DATE NOT NULL,
    Status ENUM('PENDING', 'CONFIRMED', 'CANCELLED', 'COMPLETED') DEFAULT 'PENDING',
    CreatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UpdatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (CustomerID) REFERENCES Customer(CustomerID) ON DELETE CASCADE,
    FOREIGN KEY (VehicleTypeID) REFERENCES VehicleType(TypeID) ON DELETE RESTRICT
);

-- 7. Maintenance Entity
CREATE TABLE Maintenance (
    MaintID INT PRIMARY KEY AUTO_INCREMENT,
    VehicleID INT NOT NULL,
    Date DATE NOT NULL,
    Description TEXT NOT NULL,
    Cost DECIMAL(10,2) NOT NULL,
    Status ENUM('SCHEDULED', 'IN_PROGRESS', 'COMPLETED') DEFAULT 'SCHEDULED',
    CreatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UpdatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (VehicleID) REFERENCES Vehicle(VehicleID) ON DELETE CASCADE
);

-- =============================================
-- INDEXES FOR PERFORMANCE
-- =============================================

-- Vehicle indexes
CREATE INDEX idx_vehicle_type ON Vehicle(TypeID);
CREATE INDEX idx_vehicle_status ON Vehicle(Status);
CREATE INDEX idx_vehicle_plate ON Vehicle(PlateNo);

-- Customer indexes  
CREATE INDEX idx_customer_email ON Customer(Email);
CREATE INDEX idx_customer_license ON Customer(LicenseNo);

-- Rental indexes
CREATE INDEX idx_rental_customer ON Rental(CustomerID);
CREATE INDEX idx_rental_vehicle ON Rental(VehicleID);
CREATE INDEX idx_rental_dates ON Rental(StartDate, DueDate);
CREATE INDEX idx_rental_status ON Rental(Status);

-- Reservation indexes
CREATE INDEX idx_reservation_customer ON Reservation(CustomerID);
CREATE INDEX idx_reservation_dates ON Reservation(StartDate, EndDate);

-- =============================================
-- SAMPLE DATA (Insert before creating triggers)
-- =============================================

-- Insert Vehicle Types
INSERT INTO VehicleType (Name, Description) VALUES
('Car', 'Standard passenger cars for personal transportation'),
('Bus', 'Large vehicles for group transportation'),
('Bike', 'Motorcycles for quick urban transportation'),
('Scooter', 'Small two-wheelers for short distance travel');

-- Insert Staff
INSERT INTO Staff (Name, Role, Email, Phone) VALUES
('John Admin', 'Admin', 'admin@smartride.com', '123-456-7890'),
('Sarah Manager', 'Manager', 'sarah@smartride.com', '123-456-7891'),
('Mike Staff', 'Staff', 'mike@smartride.com', '123-456-7892');

-- Insert Vehicles
INSERT INTO Vehicle (TypeID, Make, Model, PlateNo, Year, RatePerDay) VALUES
-- Cars
(1, 'Toyota', 'Camry', 'ABC123', 2023, 45.00),
(1, 'Honda', 'Civic', 'XYZ789', 2022, 40.00),
(1, 'BMW', '320i', 'BMW001', 2024, 85.00),
(1, 'Mercedes', 'C-Class', 'MER001', 2023, 90.00),
(1, 'Audi', 'A4', 'AUD001', 2022, 80.00),

-- Buses
(2, 'Mercedes', 'Sprinter', 'BUS001', 2023, 120.00),
(2, 'Ford', 'Transit', 'BUS002', 2022, 100.00),
(2, 'Iveco', 'Daily', 'BUS003', 2023, 110.00),

-- Bikes
(3, 'Yamaha', 'R15', 'BIKE01', 2023, 25.00),
(3, 'Honda', 'CBR150R', 'BIKE02', 2022, 30.00),
(3, 'Kawasaki', 'Ninja 250', 'BIKE03', 2024, 35.00),
(3, 'Suzuki', 'GSX-R150', 'BIKE04', 2023, 28.00),

-- Scooters
(4, 'Honda', 'PCX 150', 'SCTR01', 2023, 20.00),
(4, 'Yamaha', 'NMAX', 'SCTR02', 2022, 18.00),
(4, 'Vespa', 'Primavera', 'SCTR03', 2024, 25.00);

-- Insert Sample Customers (with hashed passwords - 'password123' for all)
INSERT INTO Customer (Name, Email, Phone, LicenseNo, Password) VALUES
('Alice Johnson', 'alice@email.com', '555-0101', 'DL001234', '$2b$12$LqGkqOqvKiHvW3bFKr8j.uT8Q9n8n9M8Y6P7N5L9K1D3F2G4H5I6J7'),
('Bob Smith', 'bob@email.com', '555-0102', 'DL005678', '$2b$12$LqGkqOqvKiHvW3bFKr8j.uT8Q9n8n9M8Y6P7N5L9K1D3F2G4H5I6J7'),
('Carol Davis', 'carol@email.com', '555-0103', 'DL009012', '$2b$12$LqGkqOqvKiHvW3bFKr8j.uT8Q9n8n9M8Y6P7N5L9K1D3F2G4H5I6J7'),
('David Wilson', 'david@email.com', '555-0104', 'DL003456', '$2b$12$LqGkqOqvKiHvW3bFKr8j.uT8Q9n8n9M8Y6P7N5L9K1D3F2G4H5I6J7');

-- Insert Sample Rentals (using current dates)
INSERT INTO Rental (VehicleID, CustomerID, StartDate, DueDate, ReturnDate, DailyRate, TotalAmount, Status, ProcessedBy) VALUES
(1, 1, CURDATE() - INTERVAL 5 DAY, CURDATE() - INTERVAL 2 DAY, CURDATE() - INTERVAL 2 DAY, 45.00, 180.00, 'COMPLETED', 1),
(2, 2, CURDATE(), CURDATE() + INTERVAL 5 DAY, NULL, 40.00, 240.00, 'ACTIVE', 1),
(3, 3, CURDATE() - INTERVAL 10 DAY, CURDATE() - INTERVAL 8 DAY, CURDATE() - INTERVAL 6 DAY, 85.00, 170.00, 'COMPLETED', 2);

-- Update vehicle status for rented vehicles
UPDATE Vehicle SET Status = 'RENTED' WHERE VehicleID IN (2);

-- Insert Sample Reservations
INSERT INTO Reservation (CustomerID, VehicleTypeID, ResDate, StartDate, EndDate) VALUES
(4, 1, CURDATE(), CURDATE() + INTERVAL 20 DAY, CURDATE() + INTERVAL 25 DAY),
(1, 2, CURDATE(), CURDATE() + INTERVAL 30 DAY, CURDATE() + INTERVAL 32 DAY);

-- Insert Sample Maintenance Records
INSERT INTO Maintenance (VehicleID, Date, Description, Cost, Status) VALUES
(5, CURDATE() - INTERVAL 12 DAY, 'Regular oil change and tire rotation', 150.00, 'COMPLETED'),
(6, CURDATE() - INTERVAL 3 DAY, 'Engine diagnostic and minor repairs', 350.00, 'IN_PROGRESS');

-- =============================================
-- STORED PROCEDURES
-- =============================================

-- 1. Procedure to calculate rental amount
DELIMITER $$
CREATE PROCEDURE CalculateRentalAmount(
    IN p_vehicle_id INT,
    IN p_start_date DATE,
    IN p_due_date DATE,
    OUT p_daily_rate DECIMAL(10,2),
    OUT p_total_amount DECIMAL(10,2)
)
BEGIN
    DECLARE v_days INT;
    
    -- Get daily rate for the vehicle
    SELECT RatePerDay INTO p_daily_rate
    FROM Vehicle 
    WHERE VehicleID = p_vehicle_id;
    
    -- Calculate number of days
    SET v_days = DATEDIFF(p_due_date, p_start_date) + 1;
    
    -- Calculate total amount
    SET p_total_amount = p_daily_rate * v_days;
END$$

-- 2. Procedure to process vehicle return
DELIMITER $$
CREATE PROCEDURE ProcessVehicleReturn(
    IN p_rental_id INT,
    IN p_return_date DATE,
    IN p_processed_by INT
)
BEGIN
    DECLARE v_vehicle_id INT;
    DECLARE v_due_date DATE;
    DECLARE v_daily_rate DECIMAL(10,2);
    DECLARE v_fine_amount DECIMAL(10,2) DEFAULT 0.00;
    DECLARE v_overdue_days INT DEFAULT 0;
    
    -- Get rental details
    SELECT VehicleID, DueDate, DailyRate 
    INTO v_vehicle_id, v_due_date, v_daily_rate
    FROM Rental 
    WHERE RentalID = p_rental_id;
    
    -- Calculate fine if overdue (10% of daily rate per day)
    IF p_return_date > v_due_date THEN
        SET v_overdue_days = DATEDIFF(p_return_date, v_due_date);
        SET v_fine_amount = v_overdue_days * (v_daily_rate * 0.10);
    END IF;
    
    -- Update rental record
    UPDATE Rental 
    SET ReturnDate = p_return_date,
        FineAmount = v_fine_amount,
        Status = 'COMPLETED',
        ProcessedBy = p_processed_by,
        UpdatedAt = CURRENT_TIMESTAMP
    WHERE RentalID = p_rental_id;
    
    -- Update vehicle status to available
    UPDATE Vehicle 
    SET Status = 'AVAILABLE',
        UpdatedAt = CURRENT_TIMESTAMP
    WHERE VehicleID = v_vehicle_id;
    
END$$

-- 3. Procedure to create new rental
DELIMITER $$
CREATE PROCEDURE CreateNewRental(
    IN p_vehicle_id INT,
    IN p_customer_id INT,
    IN p_start_date DATE,
    IN p_due_date DATE,
    IN p_processed_by INT,
    OUT p_rental_id INT,
    OUT p_total_amount DECIMAL(10,2)
)
BEGIN
    DECLARE v_daily_rate DECIMAL(10,2);
    DECLARE v_vehicle_available INT DEFAULT 0;
    
    -- Check if vehicle is available
    SELECT COUNT(*) INTO v_vehicle_available
    FROM Vehicle 
    WHERE VehicleID = p_vehicle_id AND Status = 'AVAILABLE';
    
    IF v_vehicle_available = 0 THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Vehicle is not available for rental';
    END IF;
    
    -- Calculate rental amount
    CALL CalculateRentalAmount(p_vehicle_id, p_start_date, p_due_date, v_daily_rate, p_total_amount);
    
    -- Create rental record
    INSERT INTO Rental (VehicleID, CustomerID, StartDate, DueDate, DailyRate, TotalAmount, ProcessedBy)
    VALUES (p_vehicle_id, p_customer_id, p_start_date, p_due_date, v_daily_rate, p_total_amount, p_processed_by);
    
    SET p_rental_id = LAST_INSERT_ID();
    
    -- Update vehicle status
    UPDATE Vehicle 
    SET Status = 'RENTED',
        UpdatedAt = CURRENT_TIMESTAMP
    WHERE VehicleID = p_vehicle_id;
    
END$$

-- 4. Procedure with exception handling for rental processing
DELIMITER $$
CREATE PROCEDURE SafeCreateRental(
    IN p_vehicle_id INT,
    IN p_customer_id INT,
    IN p_start_date DATE,
    IN p_due_date DATE,
    IN p_processed_by INT,
    OUT p_result VARCHAR(255),
    OUT p_rental_id INT
)
BEGIN
    DECLARE v_total_amount DECIMAL(10,2);
    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        ROLLBACK;
        GET DIAGNOSTICS CONDITION 1
            p_result = MESSAGE_TEXT;
        SET p_rental_id = -1;
    END;
    
    START TRANSACTION;
    
    -- Validate customer exists
    IF NOT EXISTS (SELECT 1 FROM Customer WHERE CustomerID = p_customer_id) THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Customer does not exist';
    END IF;
    
    -- Validate vehicle exists and is available
    IF NOT EXISTS (SELECT 1 FROM Vehicle WHERE VehicleID = p_vehicle_id AND Status = 'AVAILABLE') THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Vehicle is not available';
    END IF;
    
    -- Create rental
    CALL CreateNewRental(p_vehicle_id, p_customer_id, p_start_date, p_due_date, p_processed_by, p_rental_id, v_total_amount);
    
    COMMIT;
    SET p_result = 'SUCCESS';
    
END$$

-- 5. Procedure to generate monthly revenue report using cursor
DELIMITER $$
CREATE PROCEDURE GenerateMonthlyRevenueReport(IN report_month INT, IN report_year INT)
BEGIN
    DECLARE done INT DEFAULT FALSE;
    DECLARE v_vehicle_type VARCHAR(50);
    DECLARE v_total_revenue DECIMAL(10,2);
    DECLARE v_rental_count INT;
    
    -- Declare cursor for vehicle types and their monthly revenue
    DECLARE revenue_cursor CURSOR FOR
        SELECT vt.Name, 
               IFNULL(SUM(r.TotalAmount + r.FineAmount), 0) as revenue,
               COUNT(r.RentalID) as rental_count
        FROM VehicleType vt
        LEFT JOIN Vehicle v ON vt.TypeID = v.TypeID
        LEFT JOIN Rental r ON v.VehicleID = r.VehicleID 
                            AND MONTH(r.StartDate) = report_month 
                            AND YEAR(r.StartDate) = report_year
                            AND r.Status = 'COMPLETED'
        GROUP BY vt.TypeID, vt.Name
        ORDER BY revenue DESC;
    
    DECLARE CONTINUE HANDLER FOR NOT FOUND SET done = TRUE;
    
    -- Create temporary table for report
    CREATE TEMPORARY TABLE IF NOT EXISTS temp_monthly_report (
        vehicle_type VARCHAR(50),
        total_revenue DECIMAL(10,2),
        rental_count INT
    );
    
    -- Clear any existing data
    DELETE FROM temp_monthly_report;
    
    -- Open cursor and fetch data
    OPEN revenue_cursor;
    
    revenue_loop: LOOP
        FETCH revenue_cursor INTO v_vehicle_type, v_total_revenue, v_rental_count;
        
        IF done THEN
            LEAVE revenue_loop;
        END IF;
        
        -- Insert data into temporary table
        INSERT INTO temp_monthly_report (vehicle_type, total_revenue, rental_count)
        VALUES (v_vehicle_type, v_total_revenue, v_rental_count);
        
    END LOOP revenue_loop;
    
    CLOSE revenue_cursor;
    
    -- Return the report
    SELECT * FROM temp_monthly_report;
    
END$$

DELIMITER ;

-- =============================================
-- FUNCTIONS
-- =============================================

-- 1. Function to get customer's total spending
DELIMITER $$
CREATE FUNCTION GetCustomerTotalSpending(p_customer_id INT) 
RETURNS DECIMAL(10,2)
READS SQL DATA
DETERMINISTIC
BEGIN
    DECLARE v_total DECIMAL(10,2) DEFAULT 0.00;
    
    SELECT IFNULL(SUM(TotalAmount + FineAmount), 0.00) 
    INTO v_total
    FROM Rental 
    WHERE CustomerID = p_customer_id AND Status = 'COMPLETED';
    
    RETURN v_total;
END$$

-- 2. Function to check vehicle availability for date range
DELIMITER $$
CREATE FUNCTION IsVehicleAvailable(p_vehicle_id INT, p_start_date DATE, p_end_date DATE) 
RETURNS BOOLEAN
READS SQL DATA
DETERMINISTIC
BEGIN
    DECLARE v_conflict_count INT DEFAULT 0;
    
    -- Check for conflicting rentals
    SELECT COUNT(*) INTO v_conflict_count
    FROM Rental 
    WHERE VehicleID = p_vehicle_id 
    AND Status IN ('ACTIVE', 'OVERDUE')
    AND (
        (StartDate <= p_end_date AND DueDate >= p_start_date)
    );
    
    -- Check vehicle status
    IF (SELECT Status FROM Vehicle WHERE VehicleID = p_vehicle_id) != 'AVAILABLE' THEN
        SET v_conflict_count = v_conflict_count + 1;
    END IF;
    
    RETURN (v_conflict_count = 0);
END$$

-- 3. Function to calculate age of vehicle
DELIMITER $$
CREATE FUNCTION GetVehicleAge(p_vehicle_id INT) 
RETURNS INT
READS SQL DATA
DETERMINISTIC
BEGIN
    DECLARE v_age INT;
    
    SELECT YEAR(CURDATE()) - Year INTO v_age
    FROM Vehicle 
    WHERE VehicleID = p_vehicle_id;
    
    RETURN IFNULL(v_age, 0);
END$$

DELIMITER ;

-- =============================================
-- TRIGGERS (Created after data insertion)
-- =============================================

-- 1. Trigger to validate rental dates (for future rentals only)
DELIMITER $$
CREATE TRIGGER tr_rental_validate_dates
BEFORE INSERT ON Rental
FOR EACH ROW
BEGIN
    -- Only validate future rentals, allow historical data
    IF NEW.StartDate >= CURDATE() THEN
        IF NEW.StartDate < CURDATE() THEN
            SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Rental start date cannot be in the past';
        END IF;
    END IF;
    
    -- Check if due date is after start date
    IF NEW.DueDate <= NEW.StartDate THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Due date must be after start date';
    END IF;
    
    -- Automatically set status to OVERDUE if due date has passed and no return date
    IF NEW.DueDate < CURDATE() AND NEW.ReturnDate IS NULL AND NEW.Status = 'ACTIVE' THEN
        SET NEW.Status = 'OVERDUE';
    END IF;
END$$

-- 2. Trigger to update reservation status
DELIMITER $$
CREATE TRIGGER tr_reservation_validate_dates
BEFORE INSERT ON Reservation
FOR EACH ROW
BEGIN
    -- Only validate future reservations
    IF NEW.StartDate >= CURDATE() THEN
        IF NEW.StartDate < CURDATE() THEN
            SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Reservation start date cannot be in the past';
        END IF;
    END IF;
    
    -- Check if end date is after start date
    IF NEW.EndDate <= NEW.StartDate THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Reservation end date must be after start date';
    END IF;
    
    -- Set reservation date to current date if not provided
    IF NEW.ResDate IS NULL THEN
        SET NEW.ResDate = CURDATE();
    END IF;
END$$

-- 3. Trigger to log maintenance activities
DELIMITER $$
CREATE TRIGGER tr_maintenance_update_vehicle_status
AFTER INSERT ON Maintenance
FOR EACH ROW
BEGIN
    -- Set vehicle to maintenance status when maintenance is scheduled
    UPDATE Vehicle 
    SET Status = 'MAINTENANCE', UpdatedAt = CURRENT_TIMESTAMP
    WHERE VehicleID = NEW.VehicleID;
END$$

-- 4. Trigger to update vehicle status when rental is created (for future rentals)
DELIMITER $$
CREATE TRIGGER tr_rental_insert_update_vehicle
AFTER INSERT ON Rental
FOR EACH ROW
BEGIN
    -- Only update status for active rentals
    IF NEW.Status = 'ACTIVE' THEN
        UPDATE Vehicle 
        SET Status = 'RENTED', UpdatedAt = CURRENT_TIMESTAMP
        WHERE VehicleID = NEW.VehicleID;
    END IF;
END$$

DELIMITER ;

-- =============================================
-- VIEWS FOR COMMON QUERIES
-- =============================================

-- View for available vehicles with type information
CREATE VIEW vw_available_vehicles AS
SELECT 
    v.VehicleID,
    v.Make,
    v.Model,
    v.PlateNo,
    v.Year,
    v.RatePerDay,
    vt.Name as VehicleType,
    v.Status
FROM Vehicle v
JOIN VehicleType vt ON v.TypeID = vt.TypeID
WHERE v.Status = 'AVAILABLE';

-- View for rental history with customer and vehicle details
CREATE VIEW vw_rental_history AS
SELECT 
    r.RentalID,
    c.Name as CustomerName,
    c.Email as CustomerEmail,
    v.Make,
    v.Model,
    v.PlateNo,
    vt.Name as VehicleType,
    r.StartDate,
    r.DueDate,
    r.ReturnDate,
    r.TotalAmount,
    r.FineAmount,
    r.Status,
    s.Name as ProcessedBy
FROM Rental r
JOIN Customer c ON r.CustomerID = c.CustomerID
JOIN Vehicle v ON r.VehicleID = v.VehicleID
JOIN VehicleType vt ON v.TypeID = vt.TypeID
LEFT JOIN Staff s ON r.ProcessedBy = s.StaffID;

-- View for overdue rentals
CREATE VIEW vw_overdue_rentals AS
SELECT 
    r.RentalID,
    c.Name as CustomerName,
    c.Phone as CustomerPhone,
    v.Make,
    v.Model,
    v.PlateNo,
    r.DueDate,
    DATEDIFF(CURDATE(), r.DueDate) as DaysOverdue,
    r.DailyRate * 0.10 * DATEDIFF(CURDATE(), r.DueDate) as EstimatedFine
FROM Rental r
JOIN Customer c ON r.CustomerID = c.CustomerID
JOIN Vehicle v ON r.VehicleID = v.VehicleID
WHERE r.Status = 'ACTIVE' AND r.DueDate < CURDATE();

-- =============================================
-- DATABASE SETUP COMPLETE
-- =============================================

-- Display summary
SELECT 'Database Setup Complete!' as Status;
SELECT COUNT(*) as VehicleTypes FROM VehicleType;
SELECT COUNT(*) as Vehicles FROM Vehicle;
SELECT COUNT(*) as Customers FROM Customer;
SELECT COUNT(*) as Staff FROM Staff;
SELECT COUNT(*) as Rentals FROM Rental;
SELECT COUNT(*) as Reservations FROM Reservation;
SELECT COUNT(*) as MaintenanceRecords FROM Maintenance;