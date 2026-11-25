"""Hotel Booking Management Desktop Client (Python / Tkinter + MySQL).

Refactored to eliminate hardcoded credentials, validate user inputs safely,
and guard GUI execution under `if __name__ == "__main__":`.
"""

from __future__ import annotations

import tkinter as tk
from tkinter import messagebox, ttk
from typing import Any, Optional

from business_logic import (
    calculate_booking_charges,
    normalize_optional_field,
    parse_selected_id,
    validate_payment_amount,
)
from config import DatabaseConfig

try:
    import mysql.connector
    from mysql.connector import Error as MySQLError
except ImportError:  # pragma: no cover - allows importing/testing without mysql driver
    mysql = None  # type: ignore[assignment]
    MySQLError = Exception  # type: ignore[misc, assignment]

try:
    from tkcalendar import DateEntry
except ImportError:  # pragma: no cover
    DateEntry = None  # type: ignore[assignment]


def create_connection(cfg: Optional[DatabaseConfig] = None) -> Any:
    """Open a MySQL connection using environment-provided credentials."""
    if mysql is None:
        messagebox.showerror(
            "Missing Dependency",
            "mysql-connector-python is not installed. Run: pip install -r requirements.txt",
        )
        return None

    config = cfg or DatabaseConfig.from_env()
    try:
        conn = mysql.connector.connect(
            host=config.host,
            port=config.port,
            user=config.user,
            password=config.password,
            database=config.database,
        )
        if conn.is_connected():
            return conn
    except MySQLError as err:
        messagebox.showerror("Database Error", f"Error connecting to MySQL: {err}")
    return None


class HotelBookingApp:
    """Multi-tab hotel operations GUI (Guests, Rooms, Bookings, Payments, Reports)."""

    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("Hotel Booking System")
        self.root.geometry("1200x700")
        self.root.configure(bg="white")

        title = tk.Label(
            root,
            text="Hotel Booking Management System",
            font=("Segoe UI", 20, "bold"),
            bg="#1e3a5f",
            fg="white",
        )
        title.pack(fill=tk.X, ipady=14)

        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=10)

        self._build_guest_tab()
        self._build_room_tab()
        self._build_booking_tab()
        self._build_payment_tab()
        self._build_reports_tab()

    # ---------- GUESTS ----------
    def _build_guest_tab(self) -> None:
        tab = tk.Frame(self.notebook, bg="white")
        self.notebook.add(tab, text="Guests")
        tk.Label(tab, text="Guest Directory & Registration", font=("Segoe UI", 14, "bold"), bg="white").pack(pady=8)

        form = tk.Frame(tab, bg="white")
        form.pack(pady=6)

        labels = ["First Name*:", "Last Name*:", "Email:", "National ID*:", "Phone:", "Address:"]
        self.guest_entries: dict[str, tk.Entry] = {}
        keys = ["first_name", "last_name", "email", "national_id", "phone", "address"]
        for row, (label, key) in enumerate(zip(labels, keys)):
            tk.Label(form, text=label, bg="white", font=("Segoe UI", 10)).grid(row=row, column=0, sticky="w", pady=4, padx=8)
            entry = tk.Entry(form, width=32, font=("Segoe UI", 10))
            entry.grid(row=row, column=1, pady=4)
            self.guest_entries[key] = entry

        tk.Button(
            form, text="Add Guest", command=self.add_guest, bg="#16a34a", fg="white",
            font=("Segoe UI", 10, "bold"), width=24, pady=5, cursor="hand2"
        ).grid(row=len(labels), column=0, columnspan=2, pady=10)

        btns = tk.Frame(tab, bg="white")
        btns.pack(pady=4)
        tk.Button(btns, text="Refresh Guests", command=self.show_guests, bg="#2563eb", fg="white", width=18, pady=4).pack(side="left", padx=4)
        tk.Button(btns, text="Delete Selected", command=self.delete_guest, bg="#dc2626", fg="white", width=18, pady=4).pack(side="left", padx=4)

        self.guest_list = tk.Listbox(tab, width=110, height=9, font=("Consolas", 9))
        self.guest_list.pack(pady=8, padx=16, fill="x")

    def add_guest(self) -> None:
        fname = self.guest_entries["first_name"].get().strip()
        lname = self.guest_entries["last_name"].get().strip()
        email = normalize_optional_field(self.guest_entries["email"].get())
        nid = self.guest_entries["national_id"].get().strip()
        phone = normalize_optional_field(self.guest_entries["phone"].get())
        address = normalize_optional_field(self.guest_entries["address"].get())

        if not fname or not lname or not nid:
            messagebox.showwarning("Input Error", "First Name, Last Name, and National ID are required.")
            return

        conn = create_connection()
        if not conn:
            return
        cursor = conn.cursor()
        try:
            cursor.execute(
                "INSERT INTO Guest (first_name, last_name, email, national_id, address) VALUES (%s, %s, %s, %s, %s)",
                (fname, lname, email, nid, address),
            )
            guest_id = cursor.lastrowid
            if phone:
                cursor.execute("INSERT INTO GuestPhone (guest_id, phone_number) VALUES (%s, %s)", (guest_id, phone))
            conn.commit()
            messagebox.showinfo("Success", f"Guest added successfully (ID: {guest_id}).")
            for entry in self.guest_entries.values():
                entry.delete(0, tk.END)
            self.show_guests()
        except MySQLError as err:
            conn.rollback()
            messagebox.showerror("Database Error", str(err))
        finally:
            cursor.close()
            conn.close()

    def show_guests(self) -> None:
        self.guest_list.delete(0, tk.END)
        conn = create_connection()
        if not conn:
            return
        cursor = conn.cursor()
        try:
            cursor.execute(
                """
                SELECT g.guest_id, g.first_name, g.last_name, g.email,
                       GROUP_CONCAT(gp.phone_number SEPARATOR ', ') AS phones
                FROM Guest g
                LEFT JOIN GuestPhone gp ON g.guest_id = gp.guest_id
                GROUP BY g.guest_id, g.first_name, g.last_name, g.email
                ORDER BY g.guest_id
                """
            )
            rows = cursor.fetchall()
            if not rows:
                self.guest_list.insert(tk.END, "No guests found.")
                return
            for g in rows:
                self.guest_list.insert(
                    tk.END, f"ID: {g[0]} | Name: {g[1]} {g[2]} | Email: {g[3] or 'N/A'} | Phone: {g[4] or 'N/A'}"
                )
        except MySQLError as err:
            messagebox.showerror("Database Error", str(err))
        finally:
            cursor.close()
            conn.close()

    def delete_guest(self) -> None:
        sel = self.guest_list.curselection()
        if not sel:
            messagebox.showwarning("Selection Error", "Select a guest to delete.")
            return
        guest_id = parse_selected_id(self.guest_list.get(sel[0]))
        if guest_id is None:
            messagebox.showwarning("Selection Error", "Selected row is not a valid guest.")
            return
        if not messagebox.askyesno("Confirm Delete", f"Delete Guest #{guest_id}?"):
            return
        conn = create_connection()
        if not conn:
            return
        cursor = conn.cursor()
        try:
            cursor.execute("DELETE FROM Guest WHERE guest_id = %s", (guest_id,))
            conn.commit()
            self.show_guests()
        except MySQLError as err:
            conn.rollback()
            messagebox.showerror("Database Error", str(err))
        finally:
            cursor.close()
            conn.close()

    # ---------- ROOMS ----------
    def _build_room_tab(self) -> None:
        tab = tk.Frame(self.notebook, bg="white")
        self.notebook.add(tab, text="Rooms")
        tk.Label(tab, text="Room Inventory", font=("Segoe UI", 14, "bold"), bg="white").pack(pady=8)

        tk.Button(tab, text="Refresh Rooms", command=self.show_rooms, bg="#2563eb", fg="white", width=18, pady=4).pack(pady=4)
        self.room_list = tk.Listbox(tab, width=110, height=12, font=("Consolas", 9))
        self.room_list.pack(pady=8, padx=16, fill="x")

        form = tk.Frame(tab, bg="white")
        form.pack(pady=8)
        self.room_entries: dict[str, tk.Entry] = {}
        for col, (lbl, key, width) in enumerate(
            [("Room #:", "room_number", 10), ("Floor:", "floor", 8), ("Price/Night:", "price", 10), ("Type ID:", "type_id", 8)]
        ):
            tk.Label(form, text=lbl, bg="white").grid(row=0, column=col * 2, padx=4)
            ent = tk.Entry(form, width=width)
            ent.grid(row=0, column=col * 2 + 1, padx=4)
            self.room_entries[key] = ent

        tk.Button(form, text="Add Room", command=self.add_room, bg="#16a34a", fg="white", width=14).grid(row=0, column=8, padx=8)

    def show_rooms(self) -> None:
        self.room_list.delete(0, tk.END)
        conn = create_connection()
        if not conn:
            return
        cursor = conn.cursor()
        try:
            cursor.execute(
                """
                SELECT r.room_id, r.room_number, r.floor, rt.type_name, r.price_per_night, r.status
                FROM Room r
                JOIN RoomType rt ON r.room_type_id = rt.room_type_id
                ORDER BY r.room_number
                """
            )
            rows = cursor.fetchall()
            if not rows:
                self.room_list.insert(tk.END, "No rooms found.")
                return
            for r in rows:
                self.room_list.insert(
                    tk.END, f"ID: {r[0]} | Room: {r[1]} | Floor: {r[2]} | Type: {r[3]} | Price: ${r[4]} | Status: {r[5]}"
                )
        except MySQLError as err:
            messagebox.showerror("Database Error", str(err))
        finally:
            cursor.close()
            conn.close()

    def add_room(self) -> None:
        vals = {k: e.get().strip() for k, e in self.room_entries.items()}
        if not all(vals.values()):
            messagebox.showwarning("Input Error", "All room fields are required.")
            return
        conn = create_connection()
        if not conn:
            return
        cursor = conn.cursor()
        try:
            cursor.execute(
                "INSERT INTO Room (room_number, floor, price_per_night, room_type_id) VALUES (%s, %s, %s, %s)",
                (vals["room_number"], int(vals["floor"]), float(vals["price"]), int(vals["type_id"])),
            )
            conn.commit()
            for ent in self.room_entries.values():
                ent.delete(0, tk.END)
            self.show_rooms()
        except (ValueError, MySQLError) as err:
            conn.rollback()
            messagebox.showerror("Error", str(err))
        finally:
            cursor.close()
            conn.close()

    # ---------- BOOKINGS ----------
    def _build_booking_tab(self) -> None:
        tab = tk.Frame(self.notebook, bg="white")
        self.notebook.add(tab, text="Bookings")
        tk.Label(tab, text="Reservation Management", font=("Segoe UI", 14, "bold"), bg="white").pack(pady=8)

        form = tk.Frame(tab, bg="white")
        form.pack(pady=6)
        tk.Label(form, text="Guest ID:", bg="white").grid(row=0, column=0, sticky="w", padx=8, pady=4)
        self.b_guest = tk.Entry(form, width=28)
        self.b_guest.grid(row=0, column=1, pady=4)

        tk.Label(form, text="Room ID:", bg="white").grid(row=1, column=0, sticky="w", padx=8, pady=4)
        self.b_room = tk.Entry(form, width=28)
        self.b_room.grid(row=1, column=1, pady=4)

        tk.Label(form, text="Check-in:", bg="white").grid(row=2, column=0, sticky="w", padx=8, pady=4)
        self.b_in = DateEntry(form, width=26, date_pattern="yyyy-mm-dd") if DateEntry else tk.Entry(form, width=28)
        self.b_in.grid(row=2, column=1, pady=4)

        tk.Label(form, text="Check-out:", bg="white").grid(row=3, column=0, sticky="w", padx=8, pady=4)
        self.b_out = DateEntry(form, width=26, date_pattern="yyyy-mm-dd") if DateEntry else tk.Entry(form, width=28)
        self.b_out.grid(row=3, column=1, pady=4)

        tk.Label(form, text="Total ($):", bg="white").grid(row=4, column=0, sticky="w", padx=8, pady=4)
        self.b_amount = tk.Entry(form, width=28, state="readonly")
        self.b_amount.grid(row=4, column=1, pady=4)

        tk.Button(form, text="Check Availability & Calculate", command=self.calculate_amount, bg="#2563eb", fg="white", width=26).grid(row=5, column=0, columnspan=2, pady=4)
        tk.Button(form, text="Create Booking", command=self.create_booking, bg="#16a34a", fg="white", width=26, pady=4).grid(row=6, column=0, columnspan=2, pady=6)

        btns = tk.Frame(tab, bg="white")
        btns.pack(pady=4)
        tk.Button(btns, text="Refresh Bookings", command=self.show_bookings, bg="#2563eb", fg="white", width=16).pack(side="left", padx=4)
        tk.Button(btns, text="Check-In", command=lambda: self._transition_booking("Checked-In", "Occupied"), bg="#16a34a", fg="white", width=14).pack(side="left", padx=4)
        tk.Button(btns, text="Check-Out", command=lambda: self._transition_booking("Checked-Out", "Available"), bg="#d97706", fg="white", width=14).pack(side="left", padx=4)
        tk.Button(btns, text="Cancel", command=lambda: self._transition_booking("Cancelled", "Available"), bg="#dc2626", fg="white", width=14).pack(side="left", padx=4)

        self.booking_list = tk.Listbox(tab, width=110, height=8, font=("Consolas", 9))
        self.booking_list.pack(pady=8, padx=16, fill="x")

    def calculate_amount(self) -> None:
        room_id = self.b_room.get().strip()
        if not room_id.isdigit():
            messagebox.showwarning("Input Error", "Enter a valid numeric Room ID.")
            return
        checkin = self.b_in.get_date()
        checkout = self.b_out.get_date()
        if checkout <= checkin:
            messagebox.showerror("Date Error", "Check-out date must be after check-in date.")
            return

        conn = create_connection()
        if not conn:
            return
        cursor = conn.cursor()
        try:
            cursor.execute(
                """
                SELECT COUNT(*) FROM Booking b
                JOIN BookingRoom br ON b.booking_id = br.booking_id
                WHERE br.room_id = %s
                  AND b.status NOT IN ('Cancelled', 'Checked-Out')
                  AND b.check_in_date < %s AND %s < b.check_out_date
                """,
                (int(room_id), checkout, checkin),
            )
            if cursor.fetchone()[0] > 0:
                messagebox.showerror("Booking Conflict", "Room is unavailable for the selected date range.")
                return

            cursor.execute("SELECT price_per_night FROM Room WHERE room_id = %s", (int(room_id),))
            row = cursor.fetchone()
            if not row:
                messagebox.showerror("Not Found", f"Room #{room_id} not found.")
                return

            bill = calculate_booking_charges(row[0], checkin, checkout)
            self.b_amount.config(state="normal")
            self.b_amount.delete(0, tk.END)
            self.b_amount.insert(0, f"{bill.total:.2f}")
            self.b_amount.config(state="readonly")
            messagebox.showinfo(
                "Price Breakdown",
                f"Nights: {bill.nights}\nSubtotal: ${bill.subtotal:.2f}\n"
                f"Tax (10%): ${bill.tax:.2f}\nService (5%): ${bill.service_charge:.2f}\nTotal: ${bill.total:.2f}",
            )
        except (ValueError, MySQLError) as err:
            messagebox.showerror("Error", str(err))
        finally:
            cursor.close()
            conn.close()

    def create_booking(self) -> None:
        guest_id, room_id, amount = self.b_guest.get().strip(), self.b_room.get().strip(), self.b_amount.get().strip()
        if not (guest_id.isdigit() and room_id.isdigit() and amount):
            messagebox.showwarning("Input Error", "Enter numeric Guest ID & Room ID, then calculate amount first.")
            return
        conn = create_connection()
        if not conn:
            return
        cursor = conn.cursor()
        try:
            cursor.execute(
                "INSERT INTO Booking (guest_id, check_in_date, check_out_date, total_amount) VALUES (%s, %s, %s, %s)",
                (int(guest_id), self.b_in.get(), self.b_out.get(), amount),
            )
            booking_id = cursor.lastrowid
            cursor.execute("INSERT INTO BookingRoom (booking_id, room_id) VALUES (%s, %s)", (booking_id, int(room_id)))
            cursor.execute("UPDATE Room SET status = 'Reserved' WHERE room_id = %s", (int(room_id),))
            conn.commit()
            messagebox.showinfo("Success", f"Booking #{booking_id} created.")
            self.show_bookings()
        except MySQLError as err:
            conn.rollback()
            messagebox.showerror("Database Error", str(err))
        finally:
            cursor.close()
            conn.close()

    def show_bookings(self) -> None:
        self.booking_list.delete(0, tk.END)
        conn = create_connection()
        if not conn:
            return
        cursor = conn.cursor()
        try:
            cursor.execute(
                """
                SELECT b.booking_id, CONCAT(g.first_name, ' ', g.last_name),
                       GROUP_CONCAT(r.room_number), b.check_in_date, b.check_out_date, b.total_amount, b.status
                FROM Booking b
                JOIN Guest g ON b.guest_id = g.guest_id
                JOIN BookingRoom br ON b.booking_id = br.booking_id
                JOIN Room r ON br.room_id = r.room_id
                GROUP BY b.booking_id, g.first_name, g.last_name, b.check_in_date, b.check_out_date, b.total_amount, b.status
                ORDER BY b.booking_id DESC
                """
            )
            rows = cursor.fetchall()
            if not rows:
                self.booking_list.insert(tk.END, "No bookings found.")
                return
            for b in rows:
                self.booking_list.insert(
                    tk.END, f"ID: {b[0]} | Guest: {b[1]} | Rooms: {b[2]} | {b[3]} -> {b[4]} | ${b[5]} | {b[6]}"
                )
        except MySQLError as err:
            messagebox.showerror("Database Error", str(err))
        finally:
            cursor.close()
            conn.close()

    def _transition_booking(self, booking_status: str, room_status: str) -> None:
        sel = self.booking_list.curselection()
        if not sel:
            messagebox.showwarning("Selection Error", "Select a booking first.")
            return
        booking_id = parse_selected_id(self.booking_list.get(sel[0]))
        if booking_id is None:
            return
        conn = create_connection()
        if not conn:
            return
        cursor = conn.cursor()
        try:
            cursor.execute("UPDATE Booking SET status = %s WHERE booking_id = %s", (booking_status, booking_id))
            cursor.execute(
                """
                UPDATE Room r JOIN BookingRoom br ON r.room_id = br.room_id
                SET r.status = %s WHERE br.booking_id = %s
                """,
                (room_status, booking_id),
            )
            conn.commit()
            self.show_bookings()
        except MySQLError as err:
            conn.rollback()
            messagebox.showerror("Error", str(err))
        finally:
            cursor.close()
            conn.close()

    # ---------- PAYMENTS ----------
    def _build_payment_tab(self) -> None:
        tab = tk.Frame(self.notebook, bg="white")
        self.notebook.add(tab, text="Payments")
        tk.Label(tab, text="Payment Tracking", font=("Segoe UI", 14, "bold"), bg="white").pack(pady=8)

        form = tk.Frame(tab, bg="white")
        form.pack(pady=6)
        tk.Label(form, text="Booking ID:", bg="white").grid(row=0, column=0, sticky="w", padx=8, pady=4)
        self.p_booking = tk.Entry(form, width=28)
        self.p_booking.grid(row=0, column=1, pady=4)

        tk.Label(form, text="Amount ($):", bg="white").grid(row=1, column=0, sticky="w", padx=8, pady=4)
        self.p_amount = tk.Entry(form, width=28)
        self.p_amount.grid(row=1, column=1, pady=4)

        tk.Label(form, text="Method:", bg="white").grid(row=2, column=0, sticky="w", padx=8, pady=4)
        self.p_method = ttk.Combobox(
            form, width=26, values=["Cash", "Credit Card", "Debit Card", "Bank Transfer", "Mobile Payment"]
        )
        self.p_method.set("Credit Card")
        self.p_method.grid(row=2, column=1, pady=4)

        tk.Button(form, text="Record Payment", command=self.record_payment, bg="#16a34a", fg="white", width=22, pady=4).grid(row=3, column=0, columnspan=2, pady=8)
        self.payment_list = tk.Listbox(tab, width=110, height=11, font=("Consolas", 9))
        self.payment_list.pack(pady=8, padx=16, fill="x")

    def record_payment(self) -> None:
        bid = self.p_booking.get().strip()
        if not bid.isdigit():
            messagebox.showwarning("Input Error", "Booking ID must be numeric.")
            return
        conn = create_connection()
        if not conn:
            return
        cursor = conn.cursor()
        try:
            cursor.execute(
                """
                SELECT (b.total_amount - COALESCE(SUM(p.amount), 0))
                FROM Booking b LEFT JOIN Payment p ON b.booking_id = p.booking_id
                WHERE b.booking_id = %s GROUP BY b.booking_id, b.total_amount
                """,
                (int(bid),),
            )
            row = cursor.fetchone()
            if not row:
                messagebox.showerror("Error", "Booking not found.")
                return
            validated = validate_payment_amount(self.p_amount.get(), row[0])
            cursor.execute(
                "INSERT INTO Payment (booking_id, amount, payment_method) VALUES (%s, %s, %s)",
                (int(bid), str(validated), self.p_method.get()),
            )
            conn.commit()
            messagebox.showinfo("Success", f"Recorded payment of ${validated:.2f}.")
            self.p_amount.delete(0, tk.END)
        except (ValueError, MySQLError) as err:
            conn.rollback()
            messagebox.showerror("Payment Error", str(err))
        finally:
            cursor.close()
            conn.close()

    # ---------- REPORTS ----------
    def _build_reports_tab(self) -> None:
        tab = tk.Frame(self.notebook, bg="white")
        self.notebook.add(tab, text="Reports")
        tk.Label(tab, text="Analytical SQL Reports", font=("Segoe UI", 14, "bold"), bg="white").pack(pady=8)

        container = tk.Frame(tab, bg="white")
        container.pack(fill="both", expand=True, padx=12, pady=6)
        left = tk.Frame(container, bg="white")
        left.pack(side="left", fill="y", padx=(0, 12))

        self.result_text = tk.Text(container, font=("Consolas", 9))
        self.result_text.pack(side="left", fill="both", expand=True)

        reports = [
            ("Available Rooms", "SELECT r.room_number, rt.type_name, r.floor, r.price_per_night FROM Room r JOIN RoomType rt ON r.room_type_id = rt.room_type_id WHERE r.status = 'Available'"),
            ("Guest Booking History", "SELECT CONCAT(g.first_name,' ',g.last_name), COUNT(b.booking_id), COALESCE(SUM(b.total_amount),0) FROM Guest g LEFT JOIN Booking b ON g.guest_id = b.guest_id GROUP BY g.guest_id, g.first_name, g.last_name"),
            ("Revenue Summary", "SELECT COALESCE(SUM(amount),0), COUNT(DISTINCT booking_id), COALESCE(AVG(amount),0) FROM Payment"),
            ("Room Status Summary", "SELECT status, COUNT(*) FROM Room GROUP BY status"),
        ]
        for label, sql in reports:
            tk.Button(left, text=label, width=26, pady=6, bg="#d97706", fg="white", command=lambda q=sql, t=label: self._run_report(t, q)).pack(pady=4)

    def _run_report(self, title: str, query: str) -> None:
        self.result_text.delete("1.0", tk.END)
        conn = create_connection()
        if not conn:
            return
        cursor = conn.cursor()
        try:
            cursor.execute(query)
            self.result_text.insert(tk.END, f"=== {title.upper()} ===\n\n")
            for row in cursor.fetchall():
                self.result_text.insert(tk.END, " | ".join(str(v) for v in row) + "\n")
        except MySQLError as err:
            self.result_text.insert(tk.END, f"Error: {err}\n")
        finally:
            cursor.close()
            conn.close()


def main() -> None:
    root = tk.Tk()
    HotelBookingApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
