-- ============================================
-- HOTEL BOOKING SYSTEM — ANALYTICAL QUERIES
-- ============================================

USE hotel_booking_system;

-- 1. Available Rooms with Type Details
SELECT r.room_number, rt.type_name, r.floor, r.price_per_night
FROM Room r
JOIN RoomType rt ON r.room_type_id = rt.room_type_id
WHERE r.status = 'Available'
ORDER BY r.room_number;

-- 2. Guests with Booking History & Total Spend
SELECT
    CONCAT(g.first_name, ' ', g.last_name) AS guest_name,
    COUNT(b.booking_id) AS total_bookings,
    COALESCE(SUM(b.total_amount), 0) AS total_spent
FROM Guest g
LEFT JOIN Booking b ON g.guest_id = b.guest_id
GROUP BY g.guest_id, g.first_name, g.last_name;

-- 3. Active Check-Ins
SELECT
    CONCAT(g.first_name, ' ', g.last_name) AS guest_name,
    GROUP_CONCAT(r.room_number ORDER BY r.room_number) AS rooms,
    b.check_in_date,
    b.check_out_date
FROM Booking b
JOIN Guest g ON b.guest_id = g.guest_id
JOIN BookingRoom br ON b.booking_id = br.booking_id
JOIN Room r ON br.room_id = r.room_id
WHERE b.status = 'Checked-In'
GROUP BY b.booking_id, g.first_name, g.last_name, b.check_in_date, b.check_out_date;

-- 4. Revenue Summary
SELECT
    COALESCE(SUM(p.amount), 0) AS total_revenue,
    COUNT(DISTINCT p.booking_id) AS paid_bookings,
    COALESCE(AVG(p.amount), 0) AS average_payment
FROM Payment p;

-- 5. Room Inventory by Status
SELECT status, COUNT(*) AS room_count
FROM Room
GROUP BY status;

-- 6. Guest Contact Directory (Aggregated Multi-Valued Phones)
SELECT
    CONCAT(g.first_name, ' ', g.last_name) AS guest_name,
    g.email,
    GROUP_CONCAT(gp.phone_number SEPARATOR ', ') AS phones
FROM Guest g
LEFT JOIN GuestPhone gp ON g.guest_id = gp.guest_id
GROUP BY g.guest_id, g.first_name, g.last_name, g.email;

-- 7. Booking Payment & Outstanding Balance Report
SELECT
    b.booking_id,
    CONCAT(g.first_name, ' ', g.last_name) AS guest_name,
    b.total_amount,
    COALESCE(SUM(p.amount), 0) AS total_paid,
    (b.total_amount - COALESCE(SUM(p.amount), 0)) AS remaining_balance
FROM Booking b
JOIN Guest g ON b.guest_id = g.guest_id
LEFT JOIN Payment p ON b.booking_id = p.booking_id
GROUP BY b.booking_id, g.first_name, g.last_name, b.total_amount;
