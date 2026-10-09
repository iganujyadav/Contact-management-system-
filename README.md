# Contact Management System

A simple, lightweight Python application designed to manage, store, and organize contacts efficiently. The system provides an easy-to-use desktop interface alongside a command-line fallback to perform everyday contact operations seamlessly.

## Key Features
- **Contact Management:** Easily add, view, search, and delete contact details (Name, Phone Number, Email, and Category).
- **Dual Interface:** Choose between an intuitive desktop GUI (Tkinter) or an interactive terminal menu (CLI).
- **Safe & Persistent Storage:** Uses SQLite database to keep all contact data structured, persistent, and secure.
- **Input Validation:** Verifies phone numbers, names, and email formats to prevent invalid or duplicate entries.
- **Quick Share & Tools:** Built-in QR code generation for quick contact sharing and WhatsApp integration for direct messaging.

## Tech Stack
- **Language:** Python
- **GUI Framework:** Tkinter
- **Database:** SQLite
- **Libraries:** Requests, QRCode, Pillow

## Getting Started
1. Run with Desktop Interface:
   python gui.py
2. Run in Terminal:
   python main.py
