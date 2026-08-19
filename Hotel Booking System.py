import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import DateEntry
import mysql.connector
from mysql.connector import Error

# Database connection function
def create_connection():
    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="password123",
            database="hotel_booking_system"
        )
        if connection.is_connected():
            return connection
    except Error as e:
        messagebox.showerror("Database Error", f"Error connecting to MySQL: {e}")
        return None


# Create main window
root = tk.Tk()
root.title("Hotel Booking System")
root.geometry("1200x700")
root.configure(bg="white")

# Title
title = tk.Label(root, text="🏨 Hotel Booking System",
                 font=("Arial", 22, "bold"), bg="#2c3e50", fg="white")
title.pack(fill=tk.X, pady=0, ipady=15)

# Create notebook (tabs)
notebook = ttk.Notebook(root)
notebook.pack(fill='both', expand=True, padx=10, pady=10)

# ========== GUEST TAB ==========
guest_tab = tk.Frame(notebook, bg="white")
notebook.add(guest_tab, text="👥 Guests")

tk.Label(guest_tab, text="Add New Guest", font=("Arial", 16, "bold"), bg="white").pack(pady=10)

# Guest Form
guest_form = tk.Frame(guest_tab, bg="white")
guest_form.pack(pady=10)

tk.Label(guest_form, text="First Name:", bg="white", font=("Arial", 10)).grid(row=0, column=0, sticky='w', pady=6,
                                                                              padx=10)
first_name_entry = tk.Entry(guest_form, width=30, font=("Arial", 10))
first_name_entry.grid(row=0, column=1, pady=6)

tk.Label(guest_form, text="Last Name:", bg="white", font=("Arial", 10)).grid(row=1, column=0, sticky='w', pady=6,
                                                                             padx=10)
last_name_entry = tk.Entry(guest_form, width=30, font=("Arial", 10))
last_name_entry.grid(row=1, column=1, pady=6)

tk.Label(guest_form, text="Email:", bg="white", font=("Arial", 10)).grid(row=2, column=0, sticky='w', pady=6, padx=10)
email_entry = tk.Entry(guest_form, width=30, font=("Arial", 10))
email_entry.grid(row=2, column=1, pady=6)

tk.Label(guest_form, text="National ID:", bg="white", font=("Arial", 10)).grid(row=3, column=0, sticky='w', pady=6,
                                                                               padx=10)
national_id_entry = tk.Entry(guest_form, width=30, font=("Arial", 10))
national_id_entry.grid(row=3, column=1, pady=6)

tk.Label(guest_form, text="Phone:", bg="white", font=("Arial", 10)).grid(row=4, column=0, sticky='w', pady=6, padx=10)
phone_entry = tk.Entry(guest_form, width=30, font=("Arial", 10))
phone_entry.grid(row=4, column=1, pady=6)

tk.Label(guest_form, text="Address:", bg="white", font=("Arial", 10)).grid(row=5, column=0, sticky='w', pady=6, padx=10)
address_entry = tk.Entry(guest_form, width=30, font=("Arial", 10))
address_entry.grid(row=5, column=1, pady=6)


def add_guest():
    fname = first_name_entry.get()
    lname = last_name_entry.get()
    email = email_entry.get()
    national_id = national_id_entry.get()
    phone = phone_entry.get()
    address = address_entry.get()

    if not fname or not lname or not national_id:
        messagebox.showwarning("Input Error", "First Name, Last Name, and National ID are required!")
        return

    connection = create_connection()
    if connection:
        try:
            cursor = connection.cursor()
            query = "INSERT INTO Guest (first_name, last_name, email, national_id, address) VALUES (%s, %s, %s, %s, %s)"
            cursor.execute(query, (fname, lname, email, national_id, address))
            guest_id = cursor.lastrowid

            if phone:
                phone_query = "INSERT INTO GuestPhone (guest_id, phone_number) VALUES (%s, %s)"
                cursor.execute(phone_query, (guest_id, phone))

            connection.commit()
            messagebox.showinfo("Success", f"Guest added successfully! Guest ID: {guest_id}")

            first_name_entry.delete(0, tk.END)
            last_name_entry.delete(0, tk.END)
            email_entry.delete(0, tk.END)
            national_id_entry.delete(0, tk.END)
            phone_entry.delete(0, tk.END)
            address_entry.delete(0, tk.END)

            show_guests()

        except Error as e:
            messagebox.showerror("Database Error", f"Error: {e}")
        finally:
            cursor.close()
            connection.close()


add_btn = tk.Button(guest_form, text="➕ Add Guest", command=add_guest,
                    bg="#4CAF50", fg="white", font=("Arial", 11, "bold"),
                    width=25, height=2, cursor="hand2")
add_btn.grid(row=6, column=0, columnspan=2, pady=15)


def show_guests():
    guest_list.delete(0, tk.END)
    connection = create_connection()
    if connection:
        try:
            cursor = connection.cursor()
            query = """
                SELECT g.guest_id, g.first_name, g.last_name, g.email, g.national_id,
                       GROUP_CONCAT(gp.phone_number SEPARATOR ', ') AS phones
                FROM Guest g
                LEFT JOIN GuestPhone gp ON g.guest_id = gp.guest_id
                GROUP BY g.guest_id
            """
            cursor.execute(query)
            guests = cursor.fetchall()

            if guests:
                for guest in guests:
                    guest_info = f"ID: {guest[0]} | Name: {guest[1]} {guest[2]} | Email: {guest[3] or 'N/A'} | Phone: {guest[5] or 'N/A'}"
                    guest_list.insert(tk.END, guest_info)
            else:
                guest_list.insert(tk.END, "No guests found")

        except Error as e:
            messagebox.showerror("Database Error", f"Error: {e}")
        finally:
            cursor.close()
            connection.close()


def edit_guest():
    selection = guest_list.curselection()
    if not selection:
        messagebox.showwarning("Selection Error", "Please select a guest to edit!")
        return

    guest_info = guest_list.get(selection[0])
    guest_id = guest_info.split("|")[0].replace("ID:", "").strip()

    edit_window = tk.Toplevel(root)
    edit_window.title("Edit Guest")
    edit_window.geometry("400x400")
    edit_window.configure(bg="white")

    connection = create_connection()
    if connection:
        try:
            cursor = connection.cursor()
            cursor.execute("SELECT first_name, last_name, email, national_id, address FROM Guest WHERE guest_id = %s",
                           (guest_id,))
            guest_data = cursor.fetchone()

            cursor.execute("SELECT phone_number FROM GuestPhone WHERE guest_id = %s LIMIT 1", (guest_id,))
            phone_data = cursor.fetchone()

            tk.Label(edit_window, text="Edit Guest Information", font=("Arial", 14, "bold"), bg="white").pack(pady=10)

            form = tk.Frame(edit_window, bg="white")
            form.pack(pady=10)

            tk.Label(form, text="First Name:", bg="white").grid(row=0, column=0, sticky='w', pady=5, padx=5)
            edit_fname = tk.Entry(form, width=25)
            edit_fname.insert(0, guest_data[0])
            edit_fname.grid(row=0, column=1, pady=5)

            tk.Label(form, text="Last Name:", bg="white").grid(row=1, column=0, sticky='w', pady=5, padx=5)
            edit_lname = tk.Entry(form, width=25)
            edit_lname.insert(0, guest_data[1])
            edit_lname.grid(row=1, column=1, pady=5)

            tk.Label(form, text="Email:", bg="white").grid(row=2, column=0, sticky='w', pady=5, padx=5)
            edit_email = tk.Entry(form, width=25)
            edit_email.insert(0, guest_data[2] or "")
            edit_email.grid(row=2, column=1, pady=5)

            tk.Label(form, text="National ID:", bg="white").grid(row=3, column=0, sticky='w', pady=5, padx=5)
            edit_nid = tk.Entry(form, width=25)
            edit_nid.insert(0, guest_data[3])
            edit_nid.grid(row=3, column=1, pady=5)

            tk.Label(form, text="Address:", bg="white").grid(row=4, column=0, sticky='w', pady=5, padx=5)
            edit_addr = tk.Entry(form, width=25)
            edit_addr.insert(0, guest_data[4] or "")
            edit_addr.grid(row=4, column=1, pady=5)

            tk.Label(form, text="Phone:", bg="white").grid(row=5, column=0, sticky='w', pady=5, padx=5)
            edit_phone = tk.Entry(form, width=25)
            if phone_data:
                edit_phone.insert(0, phone_data[0])
            edit_phone.grid(row=5, column=1, pady=5)

            def save_changes():
                conn = create_connection()
                if conn:
                    try:
                        cur = conn.cursor()
                        update_query = """UPDATE Guest SET first_name=%s, last_name=%s, email=%s, 
                                         national_id=%s, address=%s WHERE guest_id=%s"""
                        cur.execute(update_query, (edit_fname.get(), edit_lname.get(), edit_email.get(),
                                                   edit_nid.get(), edit_addr.get(), guest_id))

                        cur.execute("DELETE FROM GuestPhone WHERE guest_id = %s", (guest_id,))
                        if edit_phone.get():
                            cur.execute("INSERT INTO GuestPhone (guest_id, phone_number) VALUES (%s, %s)",
                                        (guest_id, edit_phone.get()))

                        conn.commit()
                        messagebox.showinfo("Success", "Guest updated successfully!")
                        edit_window.destroy()
                        show_guests()
                    except Error as e:
                        messagebox.showerror("Error", f"Error: {e}")
                    finally:
                        cur.close()
                        conn.close()

            tk.Button(form, text="💾 Save Changes", command=save_changes, bg="#4CAF50",
                      fg="white", font=("Arial", 10, "bold"), width=20).grid(row=6, column=0, columnspan=2, pady=15)

        except Error as e:
            messagebox.showerror("Error", f"Error: {e}")
        finally:
            cursor.close()
            connection.close()


def delete_guest():
    selection = guest_list.curselection()
    if not selection:
        messagebox.showwarning("Selection Error", "Please select a guest to delete!")
        return

    guest_info = guest_list.get(selection[0])
    guest_id = guest_info.split("|")[0].replace("ID:", "").strip()

    if messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this guest?"):
        connection = create_connection()
        if connection:
            try:
                cursor = connection.cursor()
                cursor.execute("DELETE FROM GuestPhone WHERE guest_id = %s", (guest_id,))
                cursor.execute("DELETE FROM Guest WHERE guest_id = %s", (guest_id,))
                connection.commit()
                messagebox.showinfo("Success", "Guest deleted successfully!")
                show_guests()
            except Error as e:
                messagebox.showerror("Error", f"Error: {e}")
            finally:
                cursor.close()
                connection.close()


guest_btn_frame = tk.Frame(guest_tab, bg="white")
guest_btn_frame.pack(pady=5)

show_guests_btn = tk.Button(guest_btn_frame, text="📋 Show All Guests", command=show_guests,
                            bg="#2196F3", fg="white", font=("Arial", 10, "bold"),
                            width=18, height=2, cursor="hand2")
show_guests_btn.pack(side='left', padx=5)

edit_guest_btn = tk.Button(guest_btn_frame, text="✏️ Edit Guest", command=edit_guest,
                           bg="#FF9800", fg="white", font=("Arial", 10, "bold"),
                           width=18, height=2, cursor="hand2")
edit_guest_btn.pack(side='left', padx=5)

delete_guest_btn = tk.Button(guest_btn_frame, text="🗑️ Delete Guest", command=delete_guest,
                             bg="#F44336", fg="white", font=("Arial", 10, "bold"),
                             width=18, height=2, cursor="hand2")
delete_guest_btn.pack(side='left', padx=5)

guest_list = tk.Listbox(guest_tab, width=100, height=8, font=("Courier", 9))
guest_list.pack(pady=10, padx=20)

# ========== ROOM TAB ==========
room_tab = tk.Frame(notebook, bg="white")
notebook.add(room_tab, text="🛏️ Rooms")

tk.Label(room_tab, text="Room Management", font=("Arial", 16, "bold"), bg="white").pack(pady=10)


def show_rooms():
    room_list.delete(0, tk.END)
    connection = create_connection()
    if connection:
        try:
            cursor = connection.cursor()
            query = """
                SELECT r.room_id, r.room_number, r.floor, rt.type_name, 
                       r.price_per_night, r.status
                FROM Room r
                JOIN RoomType rt ON r.room_type_id = rt.room_type_id
                ORDER BY r.room_number
            """
            cursor.execute(query)
            rooms = cursor.fetchall()

            if rooms:
                for room in rooms:
                    room_info = f"ID: {room[0]} | Room: {room[1]} | Floor: {room[2]} | Type: {room[3]} | Price: ${room[4]} | Status: {room[5]}"
                    room_list.insert(tk.END, room_info)
            else:
                room_list.insert(tk.END, "No rooms found")

        except Error as e:
            messagebox.showerror("Database Error", f"Error: {e}")
        finally:
            cursor.close()
            connection.close()


def edit_room():
    selection = room_list.curselection()
    if not selection:
        messagebox.showwarning("Selection Error", "Please select a room to edit!")
        return

    room_info = room_list.get(selection[0])
    room_id = room_info.split("|")[0].replace("ID:", "").strip()

    edit_window = tk.Toplevel(root)
    edit_window.title("Edit Room")
    edit_window.geometry("400x350")
    edit_window.configure(bg="white")

    connection = create_connection()
    if connection:
        try:
            cursor = connection.cursor()
            cursor.execute(
                "SELECT room_number, floor, price_per_night, room_type_id, status FROM Room WHERE room_id = %s",
                (room_id,))
            room_data = cursor.fetchone()

            tk.Label(edit_window, text="Edit Room Information", font=("Arial", 14, "bold"), bg="white").pack(pady=10)

            form = tk.Frame(edit_window, bg="white")
            form.pack(pady=10)

            tk.Label(form, text="Room Number:", bg="white").grid(row=0, column=0, sticky='w', pady=5, padx=5)
            edit_room_num = tk.Entry(form, width=25)
            edit_room_num.insert(0, room_data[0])
            edit_room_num.grid(row=0, column=1, pady=5)

            tk.Label(form, text="Floor:", bg="white").grid(row=1, column=0, sticky='w', pady=5, padx=5)
            edit_floor = tk.Entry(form, width=25)
            edit_floor.insert(0, room_data[1])
            edit_floor.grid(row=1, column=1, pady=5)

            tk.Label(form, text="Price per Night:", bg="white").grid(row=2, column=0, sticky='w', pady=5, padx=5)
            edit_price = tk.Entry(form, width=25)
            edit_price.insert(0, room_data[2])
            edit_price.grid(row=2, column=1, pady=5)

            tk.Label(form, text="Room Type ID:", bg="white").grid(row=3, column=0, sticky='w', pady=5, padx=5)
            edit_type = tk.Entry(form, width=25)
            edit_type.insert(0, room_data[3])
            edit_type.grid(row=3, column=1, pady=5)

            tk.Label(form, text="Status:", bg="white").grid(row=4, column=0, sticky='w', pady=5, padx=5)
            edit_status = ttk.Combobox(form, width=23, values=["Available", "Reserved", "Occupied", "Maintenance"])
            edit_status.set(room_data[4])
            edit_status.grid(row=4, column=1, pady=5)

            def save_changes():
                conn = create_connection()
                if conn:
                    try:
                        cur = conn.cursor()
                        update_query = """UPDATE Room SET room_number=%s, floor=%s, price_per_night=%s, 
                                         room_type_id=%s, status=%s WHERE room_id=%s"""
                        cur.execute(update_query, (edit_room_num.get(), edit_floor.get(), edit_price.get(),
                                                   edit_type.get(), edit_status.get(), room_id))
                        conn.commit()
                        messagebox.showinfo("Success", "Room updated successfully!")
                        edit_window.destroy()
                        show_rooms()
                    except Error as e:
                        messagebox.showerror("Error", f"Error: {e}")
                    finally:
                        cur.close()
                        conn.close()

            tk.Button(form, text="💾 Save Changes", command=save_changes, bg="#4CAF50",
                      fg="white", font=("Arial", 10, "bold"), width=20).grid(row=5, column=0, columnspan=2, pady=15)

        except Error as e:
            messagebox.showerror("Error", f"Error: {e}")
        finally:
            cursor.close()
            connection.close()


def delete_room():
    selection = room_list.curselection()
    if not selection:
        messagebox.showwarning("Selection Error", "Please select a room to delete!")
        return

    room_info = room_list.get(selection[0])
    room_id = room_info.split("|")[0].replace("ID:", "").strip()

    if messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this room?"):
        connection = create_connection()
        if connection:
            try:
                cursor = connection.cursor()
                cursor.execute("DELETE FROM Room WHERE room_id = %s", (room_id,))
                connection.commit()
                messagebox.showinfo("Success", "Room deleted successfully!")
                show_rooms()
            except Error as e:
                messagebox.showerror("Error", f"Error: {e}")
            finally:
                cursor.close()
                connection.close()


room_btn_frame = tk.Frame(room_tab, bg="white")
room_btn_frame.pack(pady=10)

show_rooms_btn = tk.Button(room_btn_frame, text="🛏️ Show All Rooms", command=show_rooms,
                           bg="#2196F3", fg="white", font=("Arial", 10, "bold"),
                           width=18, height=2, cursor="hand2")
show_rooms_btn.pack(side='left', padx=5)

edit_room_btn = tk.Button(room_btn_frame, text="✏️ Edit Room", command=edit_room,
                          bg="#FF9800", fg="white", font=("Arial", 10, "bold"),
                          width=18, height=2, cursor="hand2")
edit_room_btn.pack(side='left', padx=5)

delete_room_btn = tk.Button(room_btn_frame, text="🗑️ Delete Room", command=delete_room,
                            bg="#F44336", fg="white", font=("Arial", 10, "bold"),
                            width=18, height=2, cursor="hand2")
delete_room_btn.pack(side='left', padx=5)

room_list = tk.Listbox(room_tab, width=100, height=10, font=("Courier", 9))
room_list.pack(pady=10, padx=20)

tk.Label(room_tab, text="Quick Add Room", font=("Arial", 12, "bold"), bg="white").pack(pady=10)

room_form = tk.Frame(room_tab, bg="white")
room_form.pack()

tk.Label(room_form, text="Room Number:", bg="white").grid(row=0, column=0, padx=5)
room_number_entry = tk.Entry(room_form, width=12)
room_number_entry.grid(row=0, column=1, padx=5)

tk.Label(room_form, text="Floor:", bg="white").grid(row=0, column=2, padx=5)
floor_entry = tk.Entry(room_form, width=8)
floor_entry.grid(row=0, column=3, padx=5)

tk.Label(room_form, text="Price/Night:", bg="white").grid(row=0, column=4, padx=5)
price_entry = tk.Entry(room_form, width=10)
price_entry.grid(row=0, column=5, padx=5)

tk.Label(room_form, text="Type ID:", bg="white").grid(row=0, column=6, padx=5)
type_entry = tk.Entry(room_form, width=8)
type_entry.grid(row=0, column=7, padx=5)


def add_room():
    room_num = room_number_entry.get()
    floor = floor_entry.get()
    price = price_entry.get()
    type_id = type_entry.get()

    if not room_num or not floor or not price or not type_id:
        messagebox.showwarning("Input Error", "All fields are required!")
        return

    connection = create_connection()
    if connection:
        try:
            cursor = connection.cursor()
            query = "INSERT INTO Room (room_number, floor, price_per_night, room_type_id) VALUES (%s, %s, %s, %s)"
            cursor.execute(query, (room_num, floor, price, type_id))
            connection.commit()
            messagebox.showinfo("Success", "Room added successfully!")

            room_number_entry.delete(0, tk.END)
            floor_entry.delete(0, tk.END)
            price_entry.delete(0, tk.END)
            type_entry.delete(0, tk.END)

            show_rooms()

        except Error as e:
            messagebox.showerror("Database Error", f"Error: {e}")
        finally:
            cursor.close()
            connection.close()


add_room_btn = tk.Button(room_form, text="➕ Add Room", command=add_room,
                         bg="#4CAF50", fg="white", font=("Arial", 9, "bold"),
                         width=15, cursor="hand2")
add_room_btn.grid(row=0, column=8, padx=10)

# ========== BOOKING TAB ==========
booking_tab = tk.Frame(notebook, bg="white")
notebook.add(booking_tab, text="📅 Bookings")

tk.Label(booking_tab, text="Create New Booking", font=("Arial", 16, "bold"), bg="white").pack(pady=10)

booking_form = tk.Frame(booking_tab, bg="white")
booking_form.pack(pady=15)

tk.Label(booking_form, text="Guest ID:", bg="white", font=("Arial", 10)).grid(row=0, column=0, sticky='w', pady=6,
                                                                              padx=10)
booking_guest_id = tk.Entry(booking_form, width=30, font=("Arial", 10))
booking_guest_id.grid(row=0, column=1, pady=6)

tk.Label(booking_form, text="Room ID:", bg="white", font=("Arial", 10)).grid(row=1, column=0, sticky='w', pady=6,
                                                                             padx=10)
booking_room_id = tk.Entry(booking_form, width=30, font=("Arial", 10))
booking_room_id.grid(row=1, column=1, pady=6)

tk.Label(booking_form, text="Check-in Date:", bg="white", font=("Arial", 10)).grid(row=2, column=0, sticky='w', pady=6,
                                                                                   padx=10)
checkin_entry = DateEntry(booking_form, width=28, font=("Arial", 10), date_pattern='yyyy-mm-dd')
checkin_entry.grid(row=2, column=1, pady=6)

tk.Label(booking_form, text="Check-out Date:", bg="white", font=("Arial", 10)).grid(row=3, column=0, sticky='w', pady=6,
                                                                                    padx=10)
checkout_entry = DateEntry(booking_form, width=28, font=("Arial", 10), date_pattern='yyyy-mm-dd')
checkout_entry.grid(row=3, column=1, pady=6)

tk.Label(booking_form, text="Total Amount:", bg="white", font=("Arial", 10)).grid(row=4, column=0, sticky='w', pady=6,
                                                                                  padx=10)
amount_entry = tk.Entry(booking_form, width=30, font=("Arial", 10), state='readonly')
amount_entry.grid(row=4, column=1, pady=6)


def calculate_amount():
    room_id = booking_room_id.get()
    checkin = checkin_entry.get_date()
    checkout = checkout_entry.get_date()

    if not room_id:
        messagebox.showwarning("Input Error", "Please enter Room ID!")
        return

    if checkout <= checkin:
        messagebox.showerror("Date Error", "Check-out date must be after check-in date!")
        return

    connection = create_connection()
    if connection:
        try:
            cursor = connection.cursor()

            conflict_query = """
                SELECT COUNT(*) FROM Booking b
                JOIN BookingRoom br ON b.booking_id = br.booking_id
                WHERE br.room_id = %s
                AND b.status NOT IN ('Cancelled', 'Checked-Out')
                AND (
                    (b.check_in_date <= %s AND b.check_out_date > %s) OR
                    (b.check_in_date < %s AND b.check_out_date >= %s) OR
                    (b.check_in_date >= %s AND b.check_out_date <= %s)
                )
            """
            cursor.execute(conflict_query, (room_id, checkin, checkin, checkout, checkout, checkin, checkout))
            conflicts = cursor.fetchone()[0]

            if conflicts > 0:
                messagebox.showerror("Booking Conflict", "This room is not available for the selected dates!")
                return

            cursor.execute("SELECT price_per_night FROM Room WHERE room_id = %s", (room_id,))
            result = cursor.fetchone()

            if result:
                price_per_night = float(result[0])
                nights = (checkout - checkin).days
                subtotal = price_per_night * nights
                tax = subtotal * 0.10
                service_charge = subtotal * 0.05
                total = subtotal + tax + service_charge

                amount_entry.config(state='normal')
                amount_entry.delete(0, tk.END)
                amount_entry.insert(0, f"{total:.2f}")
                amount_entry.config(state='readonly')

                messagebox.showinfo("Calculation",
                                    f"Nights: {nights}\n"
                                    f"Subtotal: ${subtotal:.2f}\n"
                                    f"Tax (10%): ${tax:.2f}\n"
                                    f"Service Charge (5%): ${service_charge:.2f}\n"
                                    f"Total: ${total:.2f}")
            else:
                messagebox.showerror("Error", "Room not found!")

        except Error as e:
            messagebox.showerror("Error", f"Error: {e}")
        finally:
            cursor.close()
            connection.close()


calc_btn = tk.Button(booking_form, text="🧮 Calculate Amount", command=calculate_amount,
                     bg="#2196F3", fg="white", font=("Arial", 10, "bold"),
                     width=25, height=1, cursor="hand2")
calc_btn.grid(row=5, column=0, columnspan=2, pady=5)


def create_booking():
    guest_id = booking_guest_id.get()
    room_id = booking_room_id.get()
    checkin = checkin_entry.get()
    checkout = checkout_entry.get()
    amount = amount_entry.get()

    if not guest_id or not room_id or not checkin or not checkout or not amount:
        messagebox.showwarning("Input Error", "All fields are required! Please calculate amount first.")
        return

    connection = create_connection()
    if connection:
        try:
            cursor = connection.cursor()
            query = "INSERT INTO Booking (guest_id, check_in_date, check_out_date, total_amount) VALUES (%s, %s, %s, %s)"
            cursor.execute(query, (guest_id, checkin, checkout, amount))
            booking_id = cursor.lastrowid

            booking_room_query = "INSERT INTO BookingRoom (booking_id, room_id) VALUES (%s, %s)"
            cursor.execute(booking_room_query, (booking_id, room_id))

            update_room_query = "UPDATE Room SET status = 'Reserved' WHERE room_id = %s"
            cursor.execute(update_room_query, (room_id,))

            connection.commit()
            messagebox.showinfo("Success", f"Booking created successfully! Booking ID: {booking_id}")

            booking_guest_id.delete(0, tk.END)
            booking_room_id.delete(0, tk.END)
            amount_entry.config(state='normal')
            amount_entry.delete(0, tk.END)
            amount_entry.config(state='readonly')

            show_bookings()

        except Error as e:
            messagebox.showerror("Database Error", f"Error: {e}")
        finally:
            cursor.close()
            connection.close()


create_booking_btn = tk.Button(booking_form, text="✅ Create Booking", command=create_booking,
                               bg="#4CAF50", fg="white", font=("Arial", 11, "bold"),
                               width=25, height=2, cursor="hand2")
create_booking_btn.grid(row=6, column=0, columnspan=2, pady=15)


def show_bookings():
    booking_list.delete(0, tk.END)
    connection = create_connection()
    if connection:
        try:
            cursor = connection.cursor()
            query = """
                SELECT b.booking_id, CONCAT(g.first_name, ' ', g.last_name) AS guest_name,
                       GROUP_CONCAT(r.room_number) AS rooms, b.check_in_date, b.check_out_date,
                       b.total_amount, b.status
                FROM Booking b
                JOIN Guest g ON b.guest_id = g.guest_id
                JOIN BookingRoom br ON b.booking_id = br.booking_id
                JOIN Room r ON br.room_id = r.room_id
                GROUP BY b.booking_id
            """
            cursor.execute(query)
            bookings = cursor.fetchall()

            if bookings:
                for booking in bookings:
                    booking_info = f"ID: {booking[0]} | Guest: {booking[1]} | Rooms: {booking[2]} | In: {booking[3]} | Out: {booking[4]} | Amount: ${booking[5]} | Status: {booking[6]}"
                    booking_list.insert(tk.END, booking_info)
            else:
                booking_list.insert(tk.END, "No bookings found")

        except Error as e:
            messagebox.showerror("Database Error", f"Error: {e}")
        finally:
            cursor.close()
            connection.close()


def checkin_booking():
    selection = booking_list.curselection()
    if not selection:
        messagebox.showwarning("Selection Error", "Please select a booking to check-in!")
        return

    booking_info = booking_list.get(selection[0])
    booking_id = booking_info.split("|")[0].replace("ID:", "").strip()

    if messagebox.askyesno("Confirm Check-In", "Confirm guest check-in?"):
        connection = create_connection()
        if connection:
            try:
                cursor = connection.cursor()
                cursor.execute("UPDATE Booking SET status = 'Checked-In' WHERE booking_id = %s", (booking_id,))
                cursor.execute("""UPDATE Room r
                               JOIN BookingRoom br ON r.room_id = br.room_id
                               SET r.status = 'Occupied'
                               WHERE br.booking_id = %s""", (booking_id,))
                connection.commit()
                messagebox.showinfo("Success", "Guest checked in successfully!")
                show_bookings()
            except Error as e:
                messagebox.showerror("Error", f"Error: {e}")
            finally:
                cursor.close()
                connection.close()


def checkout_booking():
    selection = booking_list.curselection()
    if not selection:
        messagebox.showwarning("Selection Error", "Please select a booking to check-out!")
        return

    booking_info = booking_list.get(selection[0])
    booking_id = booking_info.split("|")[0].replace("ID:", "").strip()

    if messagebox.askyesno("Confirm Check-Out", "Confirm guest check-out?"):
        connection = create_connection()
        if connection:
            try:
                cursor = connection.cursor()
                cursor.execute("UPDATE Booking SET status = 'Checked-Out' WHERE booking_id = %s", (booking_id,))
                cursor.execute("""UPDATE Room r
                               JOIN BookingRoom br ON r.room_id = br.room_id
                               SET r.status = 'Available'
                               WHERE br.booking_id = %s""", (booking_id,))
                connection.commit()
                messagebox.showinfo("Success", "Guest checked out successfully!")
                show_bookings()
            except Error as e:
                messagebox.showerror("Error", f"Error: {e}")
            finally:
                cursor.close()
                connection.close()


def cancel_booking():
    selection = booking_list.curselection()
    if not selection:
        messagebox.showwarning("Selection Error", "Please select a booking to cancel!")
        return

    booking_info = booking_list.get(selection[0])
    booking_id = booking_info.split("|")[0].replace("ID:", "").strip()

    if messagebox.askyesno("Confirm Cancellation", "Are you sure you want to cancel this booking?"):
        connection = create_connection()
        if connection:
            try:
                cursor = connection.cursor()
                cursor.execute("UPDATE Booking SET status = 'Cancelled' WHERE booking_id = %s", (booking_id,))
                cursor.execute("""UPDATE Room r
                               JOIN BookingRoom br ON r.room_id = br.room_id
                               SET r.status = 'Available'
                               WHERE br.booking_id = %s""", (booking_id,))
                connection.commit()
                messagebox.showinfo("Success", "Booking cancelled successfully!")
                show_bookings()
            except Error as e:
                messagebox.showerror("Error", f"Error: {e}")
            finally:
                cursor.close()
                connection.close()


booking_btn_frame = tk.Frame(booking_tab, bg="white")
booking_btn_frame.pack(pady=5)

show_bookings_btn = tk.Button(booking_btn_frame, text="📋 Show All Bookings", command=show_bookings,
                              bg="#2196F3", fg="white", font=("Arial", 10, "bold"),
                              width=18, height=2, cursor="hand2")
show_bookings_btn.pack(side='left', padx=5)

checkin_btn = tk.Button(booking_btn_frame, text="✅ Check-In", command=checkin_booking,
                        bg="#4CAF50", fg="white", font=("Arial", 10, "bold"),
                        width=18, height=2, cursor="hand2")
checkin_btn.pack(side='left', padx=5)

checkout_btn = tk.Button(booking_btn_frame, text="🚪 Check-Out", command=checkout_booking,
                         bg="#FF9800", fg="white", font=("Arial", 10, "bold"),
                         width=18, height=2, cursor="hand2")
checkout_btn.pack(side='left', padx=5)

cancel_btn = tk.Button(booking_btn_frame, text="❌ Cancel Booking", command=cancel_booking,
                       bg="#F44336", fg="white", font=("Arial", 10, "bold"),
                       width=18, height=2, cursor="hand2")
cancel_btn.pack(side='left', padx=5)

booking_list = tk.Listbox(booking_tab, width=100, height=8, font=("Courier", 9))
booking_list.pack(pady=10, padx=20)

# ========== PAYMENT TAB ==========
payment_tab = tk.Frame(notebook, bg="white")
notebook.add(payment_tab, text="💳 Payments")

tk.Label(payment_tab, text="Payment Management", font=("Arial", 16, "bold"), bg="white").pack(pady=10)

payment_form = tk.Frame(payment_tab, bg="white")
payment_form.pack(pady=15)

tk.Label(payment_form, text="Booking ID:", bg="white", font=("Arial", 10)).grid(row=0, column=0, sticky='w', pady=6,
                                                                                padx=10)
payment_booking_id = tk.Entry(payment_form, width=30, font=("Arial", 10))
payment_booking_id.grid(row=0, column=1, pady=6)

tk.Label(payment_form, text="Payment Amount:", bg="white", font=("Arial", 10)).grid(row=1, column=0, sticky='w', pady=6,
                                                                                    padx=10)
payment_amount = tk.Entry(payment_form, width=30, font=("Arial", 10))
payment_amount.grid(row=1, column=1, pady=6)

tk.Label(payment_form, text="Payment Method:", bg="white", font=("Arial", 10)).grid(row=2, column=0, sticky='w', pady=6,
                                                                                    padx=10)
payment_method = ttk.Combobox(payment_form, width=28, font=("Arial", 10),
                              values=["Cash", "Credit Card", "Debit Card", "Bank Transfer", "Mobile Payment"])
payment_method.set("Cash")
payment_method.grid(row=2, column=1, pady=6)

tk.Label(payment_form, text="Payment Date:", bg="white", font=("Arial", 10)).grid(row=3, column=0, sticky='w', pady=6,
                                                                                  padx=10)
payment_date = DateEntry(payment_form, width=28, font=("Arial", 10), date_pattern='yyyy-mm-dd')
payment_date.grid(row=3, column=1, pady=6)


def get_booking_balance():
    booking_id = payment_booking_id.get()
    if not booking_id:
        messagebox.showwarning("Input Error", "Please enter Booking ID!")
        return

    connection = create_connection()
    if connection:
        try:
            cursor = connection.cursor()
            query = """
                SELECT b.total_amount, COALESCE(SUM(p.amount), 0) AS total_paid,
                       (b.total_amount - COALESCE(SUM(p.amount), 0)) AS remaining
                FROM Booking b
                LEFT JOIN Payment p ON b.booking_id = p.booking_id
                WHERE b.booking_id = %s
                GROUP BY b.booking_id
            """
            cursor.execute(query, (booking_id,))
            result = cursor.fetchone()

            if result:
                messagebox.showinfo("Booking Balance",
                                    f"Total Amount: ${result[0]:.2f}\n"
                                    f"Total Paid: ${result[1]:.2f}\n"
                                    f"Remaining Balance: ${result[2]:.2f}")
            else:
                messagebox.showerror("Error", "Booking not found!")

        except Error as e:
            messagebox.showerror("Error", f"Error: {e}")
        finally:
            cursor.close()
            connection.close()


def record_payment():
    booking_id = payment_booking_id.get()
    amount = payment_amount.get()
    method = payment_method.get()
    date = payment_date.get()

    if not booking_id or not amount or not method:
        messagebox.showwarning("Input Error", "All fields are required!")
        return

    connection = create_connection()
    if connection:
        try:
            cursor = connection.cursor()

            cursor.execute("""
                SELECT (b.total_amount - COALESCE(SUM(p.amount), 0)) AS remaining
                FROM Booking b
                LEFT JOIN Payment p ON b.booking_id = p.booking_id
                WHERE b.booking_id = %s
                GROUP BY b.booking_id
            """, (booking_id,))

            result = cursor.fetchone()
            if not result:
                messagebox.showerror("Error", "Booking not found!")
                return

            remaining = float(result[0])
            payment_amt = float(amount)

            if payment_amt > remaining:
                messagebox.showerror("Error", f"Payment amount exceeds remaining balance of ${remaining:.2f}!")
                return

            query = "INSERT INTO Payment (booking_id, amount, payment_method, payment_date) VALUES (%s, %s, %s, %s)"
            cursor.execute(query, (booking_id, amount, method, date))
            connection.commit()

            messagebox.showinfo("Success", f"Payment of ${amount} recorded successfully!")

            payment_booking_id.delete(0, tk.END)
            payment_amount.delete(0, tk.END)

            show_payments()

        except Error as e:
            messagebox.showerror("Error", f"Error: {e}")
        finally:
            cursor.close()
            connection.close()


payment_btn_frame = tk.Frame(payment_form, bg="white")
payment_btn_frame.grid(row=4, column=0, columnspan=2, pady=15)

check_balance_btn = tk.Button(payment_btn_frame, text="💰 Check Balance", command=get_booking_balance,
                              bg="#2196F3", fg="white", font=("Arial", 10, "bold"),
                              width=20, height=2, cursor="hand2")
check_balance_btn.pack(side='left', padx=5)

record_payment_btn = tk.Button(payment_btn_frame, text="💳 Record Payment", command=record_payment,
                               bg="#4CAF50", fg="white", font=("Arial", 10, "bold"),
                               width=20, height=2, cursor="hand2")
record_payment_btn.pack(side='left', padx=5)


def show_payments():
    payment_list.delete(0, tk.END)
    connection = create_connection()
    if connection:
        try:
            cursor = connection.cursor()
            query = """
                SELECT p.payment_id, p.booking_id, CONCAT(g.first_name, ' ', g.last_name) AS guest_name,
                       p.amount, p.payment_method, p.payment_date
                FROM Payment p
                JOIN Booking b ON p.booking_id = b.booking_id
                JOIN Guest g ON b.guest_id = g.guest_id
                ORDER BY p.payment_date DESC
            """
            cursor.execute(query)
            payments = cursor.fetchall()

            if payments:
                for payment in payments:
                    payment_info = f"Payment ID: {payment[0]} | Booking: {payment[1]} | Guest: {payment[2]} | Amount: ${payment[3]} | Method: {payment[4]} | Date: {payment[5]}"
                    payment_list.insert(tk.END, payment_info)
            else:
                payment_list.insert(tk.END, "No payments found")

        except Error as e:
            messagebox.showerror("Error", f"Error: {e}")
        finally:
            cursor.close()
            connection.close()


show_payments_btn = tk.Button(payment_tab, text="📋 Show All Payments", command=show_payments,
                              bg="#2196F3", fg="white", font=("Arial", 10, "bold"),
                              width=20, height=2, cursor="hand2")
show_payments_btn.pack(pady=10)

payment_list = tk.Listbox(payment_tab, width=100, height=12, font=("Courier", 9))
payment_list.pack(pady=10, padx=20)

# ========== REPORTS TAB ==========
report_tab = tk.Frame(notebook, bg="white")
notebook.add(report_tab, text="📊 Reports")

tk.Label(report_tab, text="Database Queries & Reports", font=("Arial", 16, "bold"), bg="white").pack(pady=10)

main_container = tk.Frame(report_tab, bg="white")
main_container.pack(fill='both', expand=True, padx=10, pady=10)

left_frame = tk.Frame(main_container, bg="white")
left_frame.pack(side='left', fill='y', padx=(0, 10))

tk.Label(left_frame, text="Select Query:", font=("Arial", 12, "bold"), bg="white").pack(pady=10)

right_frame = tk.Frame(main_container, bg="white")
right_frame.pack(side='left', fill='both', expand=True)

tk.Label(right_frame, text="Query Results:", font=("Arial", 12, "bold"), bg="white").pack(pady=5)
result_text = tk.Text(right_frame, width=80, height=25, font=("Courier", 9))
result_text.pack(fill='both', expand=True, pady=5)


def query_1():
    result_text.delete('1.0', tk.END)
    connection = create_connection()
    if connection:
        try:
            cursor = connection.cursor()
            query = """
                SELECT r.room_number, rt.type_name, r.floor, r.price_per_night
                FROM Room r
                JOIN RoomType rt ON r.room_type_id = rt.room_type_id
                WHERE r.status = 'Available'
            """
            cursor.execute(query)
            rooms = cursor.fetchall()

            result_text.insert(tk.END, "=== AVAILABLE ROOMS ===\n\n")
            if rooms:
                for room in rooms:
                    result_text.insert(tk.END,
                                       f"Room: {room[0]} | Type: {room[1]} | Floor: {room[2]} | Price: ${room[3]}\n")
            else:
                result_text.insert(tk.END, "No available rooms found\n")

        except Error as e:
            result_text.insert(tk.END, f"Error: {e}\n")
        finally:
            cursor.close()
            connection.close()


def query_2():
    result_text.delete('1.0', tk.END)
    connection = create_connection()
    if connection:
        try:
            cursor = connection.cursor()
            query = """
                SELECT CONCAT(g.first_name, ' ', g.last_name) AS guest_name,
                       COUNT(b.booking_id) AS total_bookings,
                       SUM(b.total_amount) AS total_spent
                FROM Guest g
                LEFT JOIN Booking b ON g.guest_id = b.guest_id
                GROUP BY g.guest_id
            """
            cursor.execute(query)
            guests = cursor.fetchall()

            result_text.insert(tk.END, "=== GUESTS WITH BOOKING HISTORY ===\n\n")
            if guests:
                for guest in guests:
                    result_text.insert(tk.END,
                                       f"Guest: {guest[0]} | Bookings: {guest[1]} | Total Spent: ${guest[2] or 0}\n")
            else:
                result_text.insert(tk.END, "No guests found\n")

        except Error as e:
            result_text.insert(tk.END, f"Error: {e}\n")
        finally:
            cursor.close()
            connection.close()


def query_3():
    result_text.delete('1.0', tk.END)
    connection = create_connection()
    if connection:
        try:
            cursor = connection.cursor()
            query = """
                SELECT CONCAT(g.first_name, ' ', g.last_name) AS guest_name,
                       GROUP_CONCAT(r.room_number) AS rooms,
                       b.check_in_date, b.check_out_date
                FROM Booking b
                JOIN Guest g ON b.guest_id = g.guest_id
                JOIN BookingRoom br ON b.booking_id = br.booking_id
                JOIN Room r ON br.room_id = r.room_id
                WHERE b.status = 'Checked-In'
                GROUP BY b.booking_id
            """
            cursor.execute(query)
            bookings = cursor.fetchall()

            result_text.insert(tk.END, "=== CURRENT CHECK-INS ===\n\n")
            if bookings:
                for booking in bookings:
                    result_text.insert(tk.END,
                                       f"Guest: {booking[0]} | Rooms: {booking[1]} | In: {booking[2]} | Out: {booking[3]}\n")
            else:
                result_text.insert(tk.END, "No current check-ins\n")

        except Error as e:
            result_text.insert(tk.END, f"Error: {e}\n")
        finally:
            cursor.close()
            connection.close()


def query_4():
    result_text.delete('1.0', tk.END)
    connection = create_connection()
    if connection:
        try:
            cursor = connection.cursor()
            query = """
                SELECT SUM(p.amount) AS total_revenue,
                       COUNT(DISTINCT p.booking_id) AS total_bookings,
                       AVG(p.amount) AS average_payment
                FROM Payment p
            """
            cursor.execute(query)
            revenue = cursor.fetchone()

            result_text.insert(tk.END, "=== REVENUE REPORT ===\n\n")
            if revenue:
                result_text.insert(tk.END, f"Total Revenue: ${revenue[0] or 0}\n")
                result_text.insert(tk.END, f"Total Bookings: {revenue[1] or 0}\n")
                result_text.insert(tk.END, f"Average Payment: ${revenue[2] or 0:.2f}\n")
            else:
                result_text.insert(tk.END, "No revenue data found\n")

        except Error as e:
            result_text.insert(tk.END, f"Error: {e}\n")
        finally:
            cursor.close()
            connection.close()


def query_5():
    result_text.delete('1.0', tk.END)
    connection = create_connection()
    if connection:
        try:
            cursor = connection.cursor()
            query = """
                SELECT status, COUNT(*) AS count
                FROM Room
                GROUP BY status
            """
            cursor.execute(query)
            statuses = cursor.fetchall()

            result_text.insert(tk.END, "=== ROOM STATUS SUMMARY ===\n\n")
            if statuses:
                for status in statuses:
                    result_text.insert(tk.END, f"{status[0]}: {status[1]} rooms\n")
            else:
                result_text.insert(tk.END, "No rooms found\n")

        except Error as e:
            result_text.insert(tk.END, f"Error: {e}\n")
        finally:
            cursor.close()
            connection.close()


def query_6():
    result_text.delete('1.0', tk.END)
    connection = create_connection()
    if connection:
        try:
            cursor = connection.cursor()
            query = """
                SELECT CONCAT(g.first_name, ' ', g.last_name) AS guest_name,
                       g.email,
                       GROUP_CONCAT(gp.phone_number SEPARATOR ', ') AS phones
                FROM Guest g
                LEFT JOIN GuestPhone gp ON g.guest_id = gp.guest_id
                GROUP BY g.guest_id
            """
            cursor.execute(query)
            guests = cursor.fetchall()

            result_text.insert(tk.END, "=== GUEST CONTACT LIST ===\n\n")
            if guests:
                for guest in guests:
                    result_text.insert(tk.END,
                                       f"Name: {guest[0]} | Email: {guest[1] or 'N/A'} | Phone: {guest[2] or 'N/A'}\n")
            else:
                result_text.insert(tk.END, "No guests found\n")

        except Error as e:
            result_text.insert(tk.END, f"Error: {e}\n")
        finally:
            cursor.close()
            connection.close()


def query_7():
    result_text.delete('1.0', tk.END)
    connection = create_connection()
    if connection:
        try:
            cursor = connection.cursor()
            query = """
                SELECT b.booking_id, CONCAT(g.first_name, ' ', g.last_name) AS guest_name,
                       b.total_amount, COALESCE(SUM(p.amount), 0) AS total_paid,
                       (b.total_amount - COALESCE(SUM(p.amount), 0)) AS remaining
                FROM Booking b
                JOIN Guest g ON b.guest_id = g.guest_id
                LEFT JOIN Payment p ON b.booking_id = p.booking_id
                GROUP BY b.booking_id
            """
            cursor.execute(query)
            payments = cursor.fetchall()

            result_text.insert(tk.END, "=== PAYMENT SUMMARY ===\n\n")
            if payments:
                for payment in payments:
                    result_text.insert(tk.END,
                                       f"Booking #{payment[0]} | Guest: {payment[1]} | Total: ${payment[2]} | Paid: ${payment[3]} | Remaining: ${payment[4]}\n")
            else:
                result_text.insert(tk.END, "No payment data found\n")

        except Error as e:
            result_text.insert(tk.END, f"Error: {e}\n")
        finally:
            cursor.close()
            connection.close()


queries = [
    ("🛏️ Show Available Rooms", query_1),
    ("👥 Show All Guests with Bookings", query_2),
    ("✅ Show Current Check-ins", query_3),
    ("💰 Revenue Report", query_4),
    ("📊 Room Status Summary", query_5),
    ("📞 Guest Contact List", query_6),
    ("💳 Payment Summary", query_7)
]

for query_text, command in queries:
    btn = tk.Button(left_frame, text=query_text, width=35, height=2,
                    bg="#FF9800", fg="white", font=("Arial", 10, "bold"),
                    cursor="hand2", command=command)
    btn.pack(pady=5)

root.mainloop()