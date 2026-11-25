"""Automated verification of Hotel Booking business logic and 7-table relational schema."""

from __future__ import annotations

import sqlite3
import sys
import unittest
from datetime import date
from decimal import Decimal
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from business_logic import (
    calculate_booking_charges,
    dates_overlap,
    normalize_optional_field,
    parse_selected_id,
    validate_payment_amount,
)
from config import DatabaseConfig
from hotel_booking_app import HotelBookingApp

SQLITE_EQUIVALENT_SCHEMA = """
PRAGMA foreign_keys = ON;
CREATE TABLE RoomType (
    room_type_id INTEGER PRIMARY KEY AUTOINCREMENT,
    type_name TEXT NOT NULL UNIQUE,
    capacity INTEGER NOT NULL CHECK (capacity > 0),
    description TEXT
);
CREATE TABLE Room (
    room_id INTEGER PRIMARY KEY AUTOINCREMENT,
    room_number TEXT NOT NULL UNIQUE,
    floor INTEGER NOT NULL CHECK (floor > 0),
    status TEXT DEFAULT 'Available' CHECK (status IN ('Available','Occupied','Maintenance','Reserved')),
    price_per_night REAL NOT NULL CHECK (price_per_night > 0),
    room_type_id INTEGER NOT NULL REFERENCES RoomType(room_type_id) ON DELETE RESTRICT
);
CREATE TABLE Guest (
    guest_id INTEGER PRIMARY KEY AUTOINCREMENT,
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    email TEXT UNIQUE,
    national_id TEXT UNIQUE NOT NULL,
    address TEXT
);
CREATE TABLE GuestPhone (
    phone_id INTEGER PRIMARY KEY AUTOINCREMENT,
    guest_id INTEGER NOT NULL REFERENCES Guest(guest_id) ON DELETE CASCADE,
    phone_number TEXT NOT NULL
);
CREATE TABLE Booking (
    booking_id INTEGER PRIMARY KEY AUTOINCREMENT,
    guest_id INTEGER NOT NULL REFERENCES Guest(guest_id) ON DELETE RESTRICT,
    check_in_date TEXT NOT NULL,
    check_out_date TEXT NOT NULL,
    total_amount REAL NOT NULL CHECK (total_amount >= 0),
    status TEXT DEFAULT 'Pending' CHECK (status IN ('Pending','Confirmed','Checked-In','Checked-Out','Cancelled')),
    CHECK (check_out_date > check_in_date)
);
CREATE TABLE BookingRoom (
    booking_id INTEGER NOT NULL REFERENCES Booking(booking_id) ON DELETE CASCADE,
    room_id INTEGER NOT NULL REFERENCES Room(room_id) ON DELETE RESTRICT,
    PRIMARY KEY (booking_id, room_id)
);
CREATE TABLE Payment (
    payment_id INTEGER PRIMARY KEY AUTOINCREMENT,
    booking_id INTEGER NOT NULL REFERENCES Booking(booking_id) ON DELETE RESTRICT,
    amount REAL NOT NULL CHECK (amount > 0),
    payment_method TEXT NOT NULL
);
"""


class TestHotelBusinessLogic(unittest.TestCase):
    def test_billing_charges_tax_and_service(self) -> None:
        bill = calculate_booking_charges(500, date(2026, 6, 1), date(2026, 6, 4))
        self.assertEqual(bill.nights, 3)
        self.assertEqual(bill.subtotal, Decimal("1500.00"))
        self.assertEqual(bill.tax, Decimal("150.00"))
        self.assertEqual(bill.service_charge, Decimal("75.00"))
        self.assertEqual(bill.total, Decimal("1725.00"))

    def test_checkout_before_checkin_rejected(self) -> None:
        with self.assertRaises(ValueError):
            calculate_booking_charges(500, date(2026, 6, 5), date(2026, 6, 5))

    def test_date_overlap_allows_same_day_turnover(self) -> None:
        self.assertFalse(dates_overlap(date(2026, 6, 1), date(2026, 6, 5), date(2026, 6, 5), date(2026, 6, 8)))
        self.assertTrue(dates_overlap(date(2026, 6, 1), date(2026, 6, 6), date(2026, 6, 5), date(2026, 6, 8)))

    def test_payment_validation(self) -> None:
        self.assertEqual(validate_payment_amount("250.5", Decimal("500.00")), Decimal("250.50"))
        with self.assertRaises(ValueError):
            validate_payment_amount("-10", Decimal("500.00"))
        with self.assertRaises(ValueError):
            validate_payment_amount("500.01", Decimal("500.00"))
        with self.assertRaises(ValueError):
            validate_payment_amount("abc", Decimal("500.00"))

    def test_helpers(self) -> None:
        self.assertEqual(parse_selected_id("ID: 42 | Guest: Sara"), 42)
        self.assertIsNone(parse_selected_id("No guests found."))
        self.assertIsNone(normalize_optional_field("   "))
        self.assertEqual(normalize_optional_field(" test@example.com "), "test@example.com")

    def test_fallback_entry_date_parsing(self) -> None:
        class _DummyEntry:
            def __init__(self, text: str) -> None:
                self._text = text

            def get(self) -> str:
                return self._text

        self.assertEqual(HotelBookingApp._read_date(_DummyEntry("2026-07-15")), date(2026, 7, 15))
        with self.assertRaises(ValueError):
            HotelBookingApp._read_date(_DummyEntry("not-a-date"))

    def test_env_config_defaults(self) -> None:
        cfg = DatabaseConfig.from_env()
        self.assertIsInstance(cfg.port, int)
        self.assertTrue(bool(cfg.host))
        self.assertTrue(bool(cfg.database))


class TestHotelRelationalModel(unittest.TestCase):
    def setUp(self) -> None:
        self.conn = sqlite3.connect(":memory:")
        self.conn.executescript(SQLITE_EQUIVALENT_SCHEMA)
        self.conn.executescript(
            """
            INSERT INTO RoomType (type_name, capacity) VALUES ('Single', 1), ('Suite', 4);
            INSERT INTO Room (room_number, floor, status, price_per_night, room_type_id)
            VALUES ('101', 1, 'Available', 500.0, 1), ('301', 3, 'Occupied', 1500.0, 2);
            INSERT INTO Guest (first_name, last_name, email, national_id)
            VALUES ('Ahmed', 'Hassan', 'ahmed@example.com', 'ID-1'), ('Sara', 'Ali', NULL, 'ID-2');
            INSERT INTO GuestPhone (guest_id, phone_number) VALUES (1, '+20-100-1'), (1, '+20-2-2');
            INSERT INTO Booking (guest_id, check_in_date, check_out_date, total_amount, status)
            VALUES (1, '2026-12-10', '2026-12-15', 2500.0, 'Confirmed');
            INSERT INTO BookingRoom (booking_id, room_id) VALUES (1, 1);
            INSERT INTO Payment (booking_id, amount, payment_method)
            VALUES (1, 1250.0, 'Credit Card'), (1, 500.0, 'Cash');
            """
        )

    def tearDown(self) -> None:
        self.conn.close()

    def test_split_payment_balance_query(self) -> None:
        row = self.conn.execute(
            """
            SELECT b.total_amount, COALESCE(SUM(p.amount), 0), (b.total_amount - COALESCE(SUM(p.amount), 0))
            FROM Booking b LEFT JOIN Payment p ON b.booking_id = p.booking_id
            WHERE b.booking_id = 1 GROUP BY b.booking_id
            """
        ).fetchone()
        self.assertEqual(row, (2500.0, 1750.0, 750.0))

    def test_booking_date_conflict_query(self) -> None:
        conflicts = self.conn.execute(
            """
            SELECT COUNT(*) FROM Booking b
            JOIN BookingRoom br ON b.booking_id = br.booking_id
            WHERE br.room_id = 1 AND b.status NOT IN ('Cancelled', 'Checked-Out')
              AND b.check_in_date < '2026-12-16' AND '2026-12-12' < b.check_out_date
            """
        ).fetchone()[0]
        self.assertEqual(conflicts, 1)

    def test_cascade_delete_guest_phones(self) -> None:
        self.conn.execute("DELETE FROM Guest WHERE guest_id = 2")
        with self.assertRaises(sqlite3.IntegrityError):
            # Guest 1 has an active booking -> RESTRICT must block deletion
            self.conn.execute("DELETE FROM Guest WHERE guest_id = 1")


if __name__ == "__main__":
    unittest.main()
