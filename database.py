import sqlite3
import json
import qrcode
import os
import hashlib
from datetime import datetime
import re

# Connect to the database or create it if it doesn't exist
def connect_db():
    conn = sqlite3.connect("contacts.db")
    cursor = conn.cursor()

    # Create `users` table for login functionality
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    """)

    # Create `contacts` table with user_id
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS contacts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            phone TEXT UNIQUE NOT NULL CHECK(length(phone) = 10),
            email TEXT CHECK(email LIKE '%@gmail.com'),
            category TEXT,
            is_sos INTEGER DEFAULT 0,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)

    conn.commit()
    conn.close()

# Initialize the database
connect_db()

# Register a new user
def register_user(username: str, password: str) -> bool:
    conn = sqlite3.connect("contacts.db")
    cursor = conn.cursor()
    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    try:
        cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, hashed_password))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

# Verify user login and return user_id
def verify_login(username: str, password: str):
    conn = sqlite3.connect("contacts.db")
    cursor = conn.cursor()
    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    cursor.execute("SELECT id FROM users WHERE username = ? AND password = ?", (username, hashed_password))
    user = cursor.fetchone()
    conn.close()
    return user[0] if user else None

# ✅ Validate name: only alphabets and spaces
def validate_name(name):
    return bool(name.strip()) and all(char.isalpha() or char.isspace() for char in name)

# 📞 Validate phone: 10-digit numeric only
def validate_phone(phone):
    return phone.isdigit() and len(phone) == 10

# 📧 Validate email: simple regex pattern
def validate_email(email):
    pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return re.match(pattern, email) is not None

# Add a new contact for a user
def add_contact(user_id: int, name: str, phone: str, email: str, category: str, is_sos: bool) -> bool:
    conn = sqlite3.connect("contacts.db")
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO contacts (user_id, name, phone, email, category, is_sos)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (user_id, name, phone, email, category, int(is_sos)))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

# Fetch all contacts for a user
def fetch_contacts(user_id: int):
    conn = sqlite3.connect("contacts.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, phone, email, category, is_sos FROM contacts WHERE user_id = ?", (user_id,))
    contacts = cursor.fetchall()
    conn.close()
    return contacts

# Search contacts for a user
def search_contacts(user_id: int, query: str):
    conn = sqlite3.connect("contacts.db")
    cursor = conn.cursor()
    cursor.execute("""
        SELECT * FROM contacts
        WHERE user_id = ? AND (name LIKE ? OR phone LIKE ? OR email LIKE ? OR category LIKE ?)
    """, (user_id, '%' + query + '%', '%' + query + '%', '%' + query + '%', '%' + query + '%'))
    results = cursor.fetchall()
    conn.close()
    return results

# Delete a contact by ID for a specific user
def delete_contact(user_id: int, contact_id: int) -> bool:
    conn = sqlite3.connect("contacts.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM contacts WHERE id = ? AND user_id = ?", (contact_id, user_id))
    if not cursor.fetchone():
        conn.close()
        return False
    cursor.execute("DELETE FROM contacts WHERE id = ? AND user_id = ?", (contact_id, user_id))
    conn.commit()
    conn.close()
    return True

# Fetch a contact by ID for QR code generation
def fetch_contact_by_id(user_id: int, contact_id: int):
    conn = sqlite3.connect("contacts.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM contacts WHERE id = ? AND user_id = ?", (contact_id, user_id))
    contact = cursor.fetchone()
    conn.close()
    return contact

# Generate QR for a single contact
def generate_qr(user_id: int, contact_id: int):
    contact = fetch_contact_by_id(user_id, contact_id)
    if not contact:
        return None
    qr_data = f"Name: {contact[2]}\nPhone: {contact[3]}\nEmail: {contact[4]}\nCategory: {contact[5]}\nSOS: {'Yes' if contact[6] else 'No'}"
    qr = qrcode.make(qr_data)
    qr_dir = "qrcodes"
    os.makedirs(qr_dir, exist_ok=True)
    qr_filename = os.path.join(qr_dir, f"contact_{contact_id}.png")
    qr.save(qr_filename)
    return qr_filename

# Generate QR code for all contacts of a user
def generate_qr_for_all_contacts(user_id: int):
    contacts = fetch_contacts(user_id)
    if not contacts:
        return None
    contacts_data = [{"Name": c[1], "Phone": c[2], "Email": c[3], "Category": c[4], "SOS": "Yes" if c[5] else "No"} for c in contacts]
    contacts_json = json.dumps(contacts_data, indent=4)
    qr = qrcode.make(contacts_json)
    qr_dir = "qrcodes"
    os.makedirs(qr_dir, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    qr_filename = os.path.join(qr_dir, f"all_contacts_qr_{timestamp}.png")
    qr.save(qr_filename)
    return qr_filename
