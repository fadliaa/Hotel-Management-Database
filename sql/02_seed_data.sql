-- ============================================
-- HOTEL BOOKING SYSTEM — SAMPLE SEED DATA (DML)
-- Run after sql/01_schema.sql
-- ============================================

USE hotel_booking_system;

INSERT INTO RoomType (type_name, capacity, description) VALUES
('Single Room', 1, 'Cozy room with single bed, ideal for solo travelers'),
('Double Room', 2, 'Comfortable room with double bed, ideal for couples'),
('Suite', 4, 'Spacious suite with king bed, living area, and premium amenities');

INSERT INTO Room (room_number, floor, status, price_per_night, room_type_id) VALUES
('101', 1, 'Available', 500.00, 1),
('102', 1, 'Available', 500.00, 1),
('201', 2, 'Available', 800.00, 2),
('202', 2, 'Occupied', 800.00, 2),
('301', 3, 'Available', 1500.00, 3),
('302', 3, 'Maintenance', 1500.00, 3);

INSERT INTO Guest (first_name, last_name, email, national_id, address) VALUES
('Ahmed', 'Hassan', 'ahmed.hassan@email.com', '29501011234567', '15 Tahrir St, Cairo, Egypt'),
('Sara', 'Mohamed', 'sara.mohamed@email.com', '29603152345678', '42 Corniche Rd, Alexandria, Egypt'),
('John', 'Smith', 'john.smith@email.com', 'US123456789', '123 Main St, New York, USA'),
('Fatima', 'Ali', 'fatima.ali@email.com', '29705203456789', '88 El-Horreya St, Alexandria, Egypt');

INSERT INTO GuestPhone (guest_id, phone_number) VALUES
(1, '+20-100-1234567'),
(1, '+20-2-12345678'),
(2, '+20-111-9876543'),
(2, '+20-3-7654321'),
(3, '+1-555-1234567'),
(4, '+20-122-5554433'),
(4, '+20-122-9998877');

INSERT INTO Booking (guest_id, check_in_date, check_out_date, total_amount, status) VALUES
(1, '2024-12-10', '2024-12-15', 2500.00, 'Confirmed'),
(2, '2024-12-08', '2024-12-12', 3200.00, 'Checked-In'),
(3, '2024-12-20', '2024-12-25', 7500.00, 'Pending');

INSERT INTO BookingRoom (booking_id, room_id) VALUES
(1, 1),
(2, 4),
(3, 5);

INSERT INTO Payment (booking_id, amount, payment_method) VALUES
(1, 1250.00, 'Credit Card'),
(1, 1250.00, 'Credit Card'),
(2, 3200.00, 'Cash'),
(3, 3750.00, 'Online Transfer');
