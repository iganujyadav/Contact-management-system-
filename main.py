import database
import requests
import gui

ULTRAMSG_INSTANCE_ID = "instance143823"
ULTRAMSG_TOKEN = "pjkr1s2cpvb81vu6"

# Global variable to track logged-in user
current_user = None

def login_or_register():
    global current_user
    while True:
        print("\n🔐 Welcome to Secure Contact Manager")
        print("1. Login")
        print("2. Register")
        print("3. Exit")

        choice = input("Choose an option: ").strip()
        if choice == '1':
            username = input("Enter username: ").strip()
            password = input("Enter password: ").strip()
            if database.verify_login(username, password):
                print("✅ Login successful!")
                current_user = username
                return True
            else:
                print("❌ Invalid username or password.")
        elif choice == '2':
            username = input("Choose a username: ").strip()
            password = input("Choose a password: ").strip()
            if database.register_user(username, password):
                print("✅ Registration successful! You can now login.")
            else:
                print("❌ Username already taken. Try again.")
        elif choice == '3':
            print("👋 Goodbye!")
            return False
        else:
            print("❗ Invalid choice.")

def validate_name(name: str):
    if not name.isalpha():
        raise ValueError("Name should contain only alphabetic characters.")

def validate_phone(phone: str):
    if not phone.isdigit() or len(phone) != 10:
        raise ValueError("Phone number must be exactly 10 digits.")

def validate_email(email: str):
    if not email.endswith("@gmail.com"):
        raise ValueError("Email must end with '@gmail.com'.")

def add_contact():
    try:
        name = input("Enter name: ").strip()
        validate_name(name)

        phone = input("Enter phone number (10 digits): ").strip()
        validate_phone(phone)

        email = input("Enter email (must end with @gmail.com): ").strip()
        validate_email(email)

        category = input("Enter category: ").strip()
        is_sos = input("Is this an SOS contact? (yes/no): ").strip().lower() == 'yes'

        if database.add_contact(current_user, name, phone, email, category, is_sos):
            print("✅ Contact added successfully.")
        else:
            print("❌ Error: Phone number already exists.")
    except ValueError as e:
        print(f"❗ {e}")

def view_contacts():
    contacts = database.fetch_contacts(current_user)
    if contacts:
        print("\n📇 All Contacts:")
        for contact in contacts:
            print(f"ID: {contact[0]}, Name: {contact[1]}, Phone: {contact[2]}, Email: {contact[3]}, "
                  f"Category: {contact[4]}, SOS: {'Yes' if contact[5] else 'No'}")
    else:
        print("⚠️ No contacts found.")

def search_contacts():
    query = input("Enter search query: ").strip()
    results = database.search_contacts(current_user, query)
    if results:
        print("\n🔍 Search Results:")
        for contact in results:
            print(f"ID: {contact[0]}, Name: {contact[2]}, Phone: {contact[3]}, Email: {contact[4]}, Category: {contact[5]}, SOS: {'Yes' if contact[6] else 'No'}")
    else:
        print("⚠️ No contacts match your query.")

def delete_contact():
    try:
        contact_id = int(input("Enter contact ID to delete: "))
        if database.delete_contact(current_user, contact_id):
            print("🗑️ Contact deleted successfully.")
        else:
            print("❌ Error: Contact ID not found or unauthorized.")
    except ValueError:
        print("❗ Invalid ID.")

def generate_qr_code():
    try:
        contact_id = int(input("Enter contact ID for QR code generation: "))
        qr_file = database.generate_qr(current_user, contact_id)
        if qr_file:
            print(f"✅ QR code generated and saved as {qr_file}.")
        else:
            print("❌ Error: Contact not found.")
    except ValueError:
        print("❗ Invalid contact ID.")

def generate_qr_for_all_contacts():
    qr_file = database.generate_qr_for_all_contacts(current_user)
    if qr_file:
        print(f"✅ QR code for all contacts generated and saved as {qr_file}.")
    else:
        print("⚠️ No contacts to generate QR code.")

def send_whatsapp_message(phone_number: str, message: str):
    url = "https://api.ultramsg.com/instance112311/"
    payload = {
        "token": ULTRAMSG_TOKEN,
        "to": f"{phone_number}",
        "body": message
    }
    headers = {
        "Content-Type": "application/x-www-form-urlencoded"
    }
    response = requests.post(url, data=payload, headers=headers)
    if response.status_code == 200:
        print(f"✅ WhatsApp message sent to {phone_number}")
    else:
        print(f"❌ Failed to send message: {response.text}")

def make_call(caller_id, receiver_number):
    print("🔔 Call functionality is currently not implemented.")

def main_menu():
    global current_user
    while True:
        print("\n========= 📱 Contact Manager =========")
        print("1. Add Contact")
        print("2. View Contacts")
        print("3. Search Contacts")
        print("4. Delete Contact")
        print("5. Generate QR Code for Contact")
        print("6. Generate QR Code for All Contacts")
        print("7. Send WhatsApp Message")
        print("8. Make a Call")
        print("9. Logout")

        choice = input("Enter your choice: ").strip()
        if choice == '1':
            add_contact()
        elif choice == '2':
            view_contacts()
        elif choice == '3':
            search_contacts()
        elif choice == '4':
            delete_contact()
        elif choice == '5':
            generate_qr_code()
        elif choice == '6':
            generate_qr_for_all_contacts()
        elif choice == '7':
            phone = input("Enter recipient's WhatsApp number (with country code): ").strip()
            message = input("Enter the message: ").strip()
            send_whatsapp_message(phone, message)
        elif choice == '8':
            caller_id = input("Enter your phone number (caller): ").strip()
            receiver_number = input("Enter recipient's phone number: ").strip()
            make_call(caller_id, receiver_number)
        elif choice == '9':
            print("🔓 Logged out successfully.")
            current_user = None
            break
        else:
            print("❗ Invalid choice. Please try again.")

if __name__ == "__main__":
    gui.ContactManagerApp().mainloop()
    while True:
        if login_or_register():
            main_menu()
        else:
            break
