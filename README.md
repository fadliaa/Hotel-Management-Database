# Hotel Management Relational Database & Desktop App

## What It Does

A complete relational database lifecycle project—from conceptual Entity-Relationship Diagram (ERD) and normalized 7-table schema design to a multi-tab Python/Tkinter operational client backed by MySQL. It supports guest registration with multi-valued phone records, room inventory tracking, date-overlap conflict prevention, dynamic 10% tax + 5% service charge billing, split payment tracking, and 7 aggregated SQL management reports.

## Tech Stack

- **Database:** MySQL 8.0+ (DDL/DML, `PRIMARY KEY`, `FOREIGN KEY`, `UNIQUE`, `ENUM`, `CHECK` constraints)
- **Application:** Python 3.11+, Tkinter, `mysql-connector-python`, `tkcalendar`
- **Testing:** Python `unittest`, in-memory SQLite relational integrity suite

## Project Structure

```text
├── sql/
│   ├── 01_schema.sql              # 7-table MySQL DDL (PK/FK, UNIQUE, ENUM, CHECK)
│   ├── 02_seed_data.sql           # Sample seed records for immediate testing
│   └── 03_queries_reference.sql   # 7 analytical reporting queries
├── src/
│   ├── config.py                  # Environment-driven DB configuration (.env)
│   ├── business_logic.py          # Billing, date-overlap & payment validation logic
│   └── hotel_booking_app.py       # Multi-tab Python/Tkinter GUI client
├── docs/                          # ERD, Relational Schema, Data Dictionary, Pathways & Deck
├── tests/
│   └── test_hotel_system.py       # Automated business logic & relational integrity tests
├── .env.example
└── requirements.txt
```

## Database Architecture (7 Normalized Tables)

- **`RoomType`** & **`Room`** — Room categories, capacities, pricing, and live availability states (`Available`, `Reserved`, `Occupied`, `Maintenance`).
- **`Guest`** & **`GuestPhone`** — Composite guest names with normalized multi-valued phone numbers (`ON DELETE CASCADE`).
- **`Booking`** & **`BookingRoom`** — Many-to-many reservation junction with date-order `CHECK` constraints (`check_out_date > check_in_date`) and overlap conflict prevention.
- **`Payment`** — Supports partial/split payments per booking with balance enforcement.

Design artifacts are available in [`docs/`](docs/): Entity-Relationship Diagram (ERD), Relational Schema, Data Dictionary, Transaction Pathways, and Presentation Deck.

## How to Run

```bash
# 1. Initialize MySQL schema and seed sample records
mysql -u root -p < sql/01_schema.sql
mysql -u root -p < sql/02_seed_data.sql

# 2. Configure local environment variables (never commit .env!)
cp .env.example .env
# Edit .env and set HOTEL_DB_PASSWORD

# 3. Install Python dependencies and run the desktop client
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python src/hotel_booking_app.py

# 4. Run automated logic & relational constraint tests (no MySQL server needed)
python -m unittest discover -s tests -v
```
