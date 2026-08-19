-- ============================================
-- HOTEL BOOKING SYSTEM
-- ============================================
-- Create Database
CREATE DATABASE IF NOT EXISTS hotel_booking_system;
USE hotel_booking_system;
-- ============================================
-- PART 1: CREATE TABLES (DDL)
-- ============================================

-- Table 1: RoomType
CREATE TABLE RoomType (
    room_type_id INT PRIMARY KEY AUTO_INCREMENT,
    type_name VARCHAR(50) NOT NULL UNIQUE,
    capacity INT NOT NULL CHECK (capacity > 0),
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table 2: Room
CREATE TABLE Room (
    room_id INT PRIMARY KEY AUTO_INCREMENT,
    room_number VARCHAR(10) NOT NULL UNIQUE,
    floor INT NOT NULL CHECK (floor > 0),
    status ENUM('Available', 'Occupied', 'Maintenance', 'Reserved') DEFAULT 'Available',
    price_per_night DECIMAL(10, 2) NOT NULL CHECK (price_per_night > 0),
    room_type_id INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (room_type_id) REFERENCES RoomType(room_type_id)
        ON DELETE RESTRICT
        ON UPDATE CASCADE
);

-- Table 3: Guest (Name is composite: first_name + last_name)
CREATE TABLE Guest (
    guest_id INT PRIMARY KEY AUTO_INCREMENT,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    email VARCHAR(100) UNIQUE,
    national_id VARCHAR(50) UNIQUE NOT NULL,
    address TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table 4: GuestPhone (Multivalued attribute - one guest can have multiple phones)
CREATE TABLE GuestPhone (
    phone_id INT PRIMARY KEY AUTO_INCREMENT,
    guest_id INT NOT NULL,
    phone_number VARCHAR(20) NOT NULL,
    FOREIGN KEY (guest_id) REFERENCES Guest(guest_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);

-- Table 5: Booking
CREATE TABLE Booking (
    booking_id INT PRIMARY KEY AUTO_INCREMENT,
    guest_id INT NOT NULL,
    check_in_date DATE NOT NULL,
    check_out_date DATE NOT NULL,
    total_amount DECIMAL(10, 2) NOT NULL CHECK (total_amount >= 0),
    status ENUM('Pending', 'Confirmed', 'Checked-In', 'Checked-Out', 'Cancelled') DEFAULT 'Pending',
    booking_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (guest_id) REFERENCES Guest(guest_id)
        ON DELETE RESTRICT
        ON UPDATE CASCADE,
    CHECK (check_out_date > check_in_date)
);

-- Table 6: BookingRoom (Junction Table)
CREATE TABLE BookingRoom (
    booking_id INT NOT NULL,
    room_id INT NOT NULL,
    PRIMARY KEY (booking_id, room_id),
    FOREIGN KEY (booking_id) REFERENCES Booking(booking_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    FOREIGN KEY (room_id) REFERENCES Room(room_id)
        ON DELETE RESTRICT
        ON UPDATE CASCADE
);

-- Table 7: Payment
CREATE TABLE Payment (
    payment_id INT PRIMARY KEY AUTO_INCREMENT,
    booking_id INT NOT NULL,
    amount DECIMAL(10, 2) NOT NULL CHECK (amount > 0),
    payment_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    payment_method ENUM('Cash', 'Credit Card', 'Debit Card', 'Online Transfer', 'Bank Transfer', 'Mobile Payment') NOT NULL,
    FOREIGN KEY (booking_id) REFERENCES Booking(booking_id)
        ON DELETE RESTRICT
        ON UPDATE CASCADE
);

-- ============================================
-- PART 2: INSERT SAMPLE DATA (DML)
-- ============================================

-- Insert RoomTypes (3 records)
INSERT INTO RoomType (type_name, capacity, description) VALUES
('Single Room', 1, 'Cozy room with single bed, perfect for solo travelers'),
('Double Room', 2, 'Comfortable room with double bed, ideal for couples'),
('Suite', 4, 'Luxurious suite with king bed, living area, and premium amenities');

-- Insert Rooms (6 records - 2 per type)
INSERT INTO Room (room_number, floor, status, price_per_night, room_type_id) VALUES
('101', 1, 'Available', 500.00, 1),
('102', 1, 'Available', 500.00, 1),
('201', 2, 'Available', 800.00, 2),
('202', 2, 'Occupied', 800.00, 2),
('301', 3, 'Available', 1500.00, 3),
('302', 3, 'Maintenance', 1500.00, 3);

-- Insert Guests (4 records with first_name and last_name)
INSERT INTO Guest (first_name, last_name, email, national_id, address) VALUES
('Ahmed', 'Hassan', 'ahmed.hassan@email.com', '29501011234567', '15 Tahrir St, Cairo, Egypt'),
('Sara', 'Mohamed', 'sara.mohamed@email.com', '29603152345678', '42 Corniche Rd, Alexandria, Egypt'),
('John', 'Smith', 'john.smith@email.com', 'US123456789', '123 Main St, New York, USA'),
('Fatima', 'Ali', 'fatima.ali@email.com', '29705203456789', '88 El-Horreya St, Alexandria, Egypt');

-- Insert GuestPhone (Multiple phone numbers per guest - multivalued attribute)
INSERT INTO GuestPhone (guest_id, phone_number) VALUES
(1, '+20-100-1234567'),
(1, '+20-2-12345678'),
(2, '+20-111-9876543'),
(2, '+20-3-7654321'),
(3, '+1-555-1234567'),
(4, '+20-122-5554433'),
(4, '+20-122-9998877');

-- Insert Bookings (3 records)
INSERT INTO Booking (guest_id, check_in_date, check_out_date, total_amount, status) VALUES
(1, '2024-12-10', '2024-12-15', 2500.00, 'Confirmed'),
(2, '2024-12-08', '2024-12-12', 3200.00, 'Checked-In'),
(3, '2024-12-20', '2024-12-25', 7500.00, 'Pending');

-- Insert BookingRoom (Link bookings to rooms)
INSERT INTO BookingRoom (booking_id, room_id) VALUES
(1, 1),  -- Ahmed booked room 101
(2, 4),  -- Sara booked room 202
(3, 5);  -- John booked room 301

-- Insert Payments (4 records)
INSERT INTO Payment (booking_id, amount, payment_method) VALUES
(1, 1250.00, 'Credit Card'),  -- Ahmed paid 50% deposit
(1, 1250.00, 'Credit Card'),  -- Ahmed paid remaining 50%
(2, 3200.00, 'Cash'),         -- Sara paid full amount
(3, 3750.00, 'Online Transfer'); -- John paid 50% deposit

-- ============================================
-- PART 3: DATA QUERIES (7+ Required Queries)
-- ============================================

-- Query 1: Show Available Rooms
SELECT 
    r.room_number, 
    rt.type_name, 
    r.floor, 
    r.price_per_night
FROM Room r
JOIN RoomType rt ON r.room_type_id = rt.room_type_id
WHERE r.status = 'Available';

-- Query 2: Show All Guests with Booking History
SELECT 
    CONCAT(g.first_name, ' ', g.last_name) AS guest_name,
    COUNT(b.booking_id) AS total_bookings,
    SUM(b.total_amount) AS total_spent
FROM Guest g
LEFT JOIN Booking b ON g.guest_id = b.guest_id
GROUP BY g.guest_id;

-- Query 3: Show Current Check-ins
SELECT 
    CONCAT(g.first_name, ' ', g.last_name) AS guest_name,
    GROUP_CONCAT(r.room_number) AS rooms,
    b.check_in_date, 
    b.check_out_date
FROM Booking b
JOIN Guest g ON b.guest_id = g.guest_id
JOIN BookingRoom br ON b.booking_id = br.booking_id
JOIN Room r ON br.room_id = r.room_id
WHERE b.status = 'Checked-In'
GROUP BY b.booking_id;

-- Query 4: Revenue Report
SELECT 
    SUM(p.amount) AS total_revenue,
    COUNT(DISTINCT p.booking_id) AS total_bookings,
    AVG(p.amount) AS average_payment
FROM Payment p;

-- Query 5: Room Status Summary
SELECT 
    status, 
    COUNT(*) AS count
FROM Room
GROUP BY status;

-- Query 6: Guest Contact List
SELECT 
    CONCAT(g.first_name, ' ', g.last_name) AS guest_name,
    g.email,
    GROUP_CONCAT(gp.phone_number SEPARATOR ', ') AS phones
FROM Guest g
LEFT JOIN GuestPhone gp ON g.guest_id = gp.guest_id
GROUP BY g.guest_id;

-- Query 7: Payment Summary
SELECT 
    b.booking_id, 
    CONCAT(g.first_name, ' ', g.last_name) AS guest_name,
    b.total_amount, 
    COALESCE(SUM(p.amount), 0) AS total_paid,
    (b.total_amount - COALESCE(SUM(p.amount), 0)) AS remaining
FROM Booking b
JOIN Guest g ON b.guest_id = g.guest_id
LEFT JOIN Payment p ON b.booking_id = p.booking_id
GROUP BY b.booking_id;

-- ============================================
-- ADDITIONAL QUERIES USED IN THE APPLICATION
-- ============================================

-- Query 8: Get Guest with Phone Numbers
SELECT 
    g.guest_id,
    g.first_name, 
    g.last_name, 
    g.email, 
    g.national_id,
    GROUP_CONCAT(gp.phone_number SEPARATOR ', ') AS phones
FROM Guest g
LEFT JOIN GuestPhone gp ON g.guest_id = gp.guest_id
GROUP BY g.guest_id;

-- Query 9: Get All Rooms with Room Type
SELECT 
    r.room_id, 
    r.room_number, 
    r.floor, 
    rt.type_name, 
    r.price_per_night, 
    r.status
FROM Room r
JOIN RoomType rt ON r.room_type_id = rt.room_type_id
ORDER BY r.room_number;

-- Query 10: Get All Bookings with Details
SELECT 
    b.booking_id, 
    CONCAT(g.first_name, ' ', g.last_name) AS guest_name,
    GROUP_CONCAT(r.room_number) AS rooms, 
    b.check_in_date, 
    b.check_out_date,
    b.total_amount, 
    b.status
FROM Booking b
JOIN Guest g ON b.guest_id = g.guest_id
JOIN BookingRoom br ON b.booking_id = br.booking_id
JOIN Room r ON br.room_id = r.room_id
GROUP BY b.booking_id;

-- Query 11: Check Booking Date Conflicts
SELECT COUNT(*) 
FROM Booking b
JOIN BookingRoom br ON b.booking_id = br.booking_id
WHERE br.room_id = ? -- Parameter for room_id
AND b.status NOT IN ('Cancelled', 'Checked-Out')
AND (
    (b.check_in_date <= ? AND b.check_out_date > ?) OR
    (b.check_in_date < ? AND b.check_out_date >= ?) OR
    (b.check_in_date >= ? AND b.check_out_date <= ?)
);

-- Query 12: Get Room Price for Calculation
SELECT price_per_night 
FROM Room 
WHERE room_id = ?;

-- Query 13: Get Booking Balance
SELECT 
    b.total_amount, 
    COALESCE(SUM(p.amount), 0) AS total_paid,
    (b.total_amount - COALESCE(SUM(p.amount), 0)) AS remaining
FROM Booking b
LEFT JOIN Payment p ON b.booking_id = p.booking_id
WHERE b.booking_id = ?
GROUP BY b.booking_id;

-- Query 14: Get All Payments with Details
SELECT 
    p.payment_id, 
    p.booking_id, 
    CONCAT(g.first_name, ' ', g.last_name) AS guest_name,
    p.amount, 
    p.payment_method, 
    p.payment_date
FROM Payment p
JOIN Booking b ON p.booking_id = b.booking_id
JOIN Guest g ON b.guest_id = g.guest_id
ORDER BY p.payment_date DESC;

-- Query 15: Get Guest Details by ID
SELECT 
    first_name, 
    last_name, 
    email, 
    national_id, 
    address 
FROM Guest 
WHERE guest_id = ?;

-- Query 16: Get Guest Phone by ID
SELECT phone_number 
FROM GuestPhone 
WHERE guest_id = ? 
LIMIT 1;

-- Query 17: Get Room Details by ID
SELECT 
    room_number, 
    floor, 
    price_per_night, 
    room_type_id, 
    status 
FROM Room 
WHERE room_id = ?;

-- ============================================
-- INSERT QUERIES USED IN THE APPLICATION
-- ============================================

-- Insert Guest
INSERT INTO Guest (first_name, last_name, email, national_id, address) 
VALUES (?, ?, ?, ?, ?);

-- Insert Guest Phone
INSERT INTO GuestPhone (guest_id, phone_number) 
VALUES (?, ?);

-- Insert Room
INSERT INTO Room (room_number, floor, price_per_night, room_type_id) 
VALUES (?, ?, ?, ?);

-- Insert Booking
INSERT INTO Booking (guest_id, check_in_date, check_out_date, total_amount) 
VALUES (?, ?, ?, ?);

-- Insert BookingRoom
INSERT INTO BookingRoom (booking_id, room_id) 
VALUES (?, ?);

-- Insert Payment
INSERT INTO Payment (booking_id, amount, payment_method, payment_date) 
VALUES (?, ?, ?, ?);

-- ============================================
-- UPDATE QUERIES USED IN THE APPLICATION
-- ============================================

-- Update Guest
UPDATE Guest 
SET first_name = ?, last_name = ?, email = ?, national_id = ?, address = ? 
WHERE guest_id = ?;

-- Update Room
UPDATE Room 
SET room_number = ?, floor = ?, price_per_night = ?, room_type_id = ?, status = ? 
WHERE room_id = ?;

-- Update Room Status to Reserved
UPDATE Room 
SET status = 'Reserved' 
WHERE room_id = ?;

-- Update Room Status to Occupied
UPDATE Room r
JOIN BookingRoom br ON r.room_id = br.room_id
SET r.status = 'Occupied'
WHERE br.booking_id = ?;

-- Update Room Status to Available
UPDATE Room r
JOIN BookingRoom br ON r.room_id = br.room_id
SET r.status = 'Available'
WHERE br.booking_id = ?;

-- Update Booking Status to Checked-In
UPDATE Booking 
SET status = 'Checked-In' 
WHERE booking_id = ?;

-- Update Booking Status to Checked-Out
UPDATE Booking 
SET status = 'Checked-Out' 
WHERE booking_id = ?;

-- Update Booking Status to Cancelled
UPDATE Booking 
SET status = 'Cancelled' 
WHERE booking_id = ?;

-- ============================================
-- DELETE QUERIES USED IN THE APPLICATION
-- ============================================

-- Delete Guest Phone Numbers
DELETE FROM GuestPhone 
WHERE guest_id = ?;

-- Delete Guest
DELETE FROM Guest 
WHERE guest_id = ?;

-- Delete Room
DELETE FROM Room 
WHERE room_id = ?;
