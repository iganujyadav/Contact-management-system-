import tkinter as tk
from tkinter import messagebox, ttk
import database
import requests

ULTRAMSG_INSTANCE_ID = "instance143823"
ULTRAMSG_TOKEN = "pjkr1s2cpvb81vu6"

class ContactManagerApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Contact Manager")
        self.geometry("800x600")
        self.current_user_id = None
        self.frames = {}
        self.show_login_screen()

    def show_frame(self, frame_name):
        frame = self.frames[frame_name]
        frame.tkraise()

    def show_login_screen(self):
        for widget in self.winfo_children():
            widget.destroy()

        login_frame = tk.Frame(self)
        login_frame.pack(fill="both", expand=True)
        self.frames["Login"] = login_frame

        tk.Label(login_frame, text="Login / Register", font=("Arial", 20)).pack(pady=20)
        tk.Label(login_frame, text="Username").pack()
        username_entry = tk.Entry(login_frame)
        username_entry.pack()
        tk.Label(login_frame, text="Password").pack()
        password_entry = tk.Entry(login_frame, show="*")
        password_entry.pack()

        def login():
            username = username_entry.get().strip()
            password = password_entry.get().strip()
            user_id = database.verify_login(username, password)
            if user_id:
                self.current_user_id = user_id
                self.show_main_menu()
            else:
                messagebox.showerror("Login Failed", "Invalid credentials.")

        def register():
            username = username_entry.get().strip()
            password = password_entry.get().strip()
            if database.register_user(username, password):
                messagebox.showinfo("Registered", "Registration successful!")
            else:
                messagebox.showerror("Failed", "Username already taken.")

        tk.Button(login_frame, text="Login", command=login).pack(pady=10)
        tk.Button(login_frame, text="Register", command=register).pack()

    def show_main_menu(self):
        for widget in self.winfo_children():
            widget.destroy()

        main_frame = tk.Frame(self)
        main_frame.pack(fill="both", expand=True)
        self.frames["MainMenu"] = main_frame

        tk.Label(main_frame, text="Main Menu", font=("Arial", 20)).pack(pady=20)
        options = [
            ("Add Contact", self.show_add_screen),
            ("View Contacts", self.show_view_screen),
            ("Search Contacts", self.show_search_screen),
            ("Delete Contact", self.show_delete_screen),
            ("Generate QR", self.show_qr_screen),
            ("Generate All QR", self.generate_all_qr),
            ("Send WhatsApp", self.show_whatsapp_screen),
            ("Logout", self.show_login_screen),
        ]

        for label, command in options:
            tk.Button(main_frame, text=label, width=30, command=command).pack(pady=5)

    def show_add_screen(self):
        self._clear_and_setup("Add Contact")
        frame = self.frames["Add Contact"]

        tk.Label(frame, text="Name").pack()
        name_entry = tk.Entry(frame)
        name_entry.pack()
        tk.Label(frame, text="Phone").pack()
        phone_entry = tk.Entry(frame)
        phone_entry.pack()
        tk.Label(frame, text="Email").pack()
        email_entry = tk.Entry(frame)
        email_entry.pack()
        tk.Label(frame, text="Category").pack()
        category_entry = tk.Entry(frame)
        category_entry.pack()
        sos_var = tk.IntVar()
        tk.Checkbutton(frame, text="SOS", variable=sos_var).pack()

        def save():
            name = name_entry.get().strip()
            phone = phone_entry.get().strip()
            email = email_entry.get().strip()
            category = category_entry.get().strip()
            is_sos = sos_var.get()

            if not database.validate_name(name):
                messagebox.showerror("Invalid", "Name should be letters only")
                return
            if not database.validate_phone(phone):
                messagebox.showerror("Invalid", "Phone must be 10 digits")
                return
            if not database.validate_email(email):
                messagebox.showerror("Invalid", "Email is not valid")
                return

            if database.add_contact(self.current_user_id, name, phone, email, category, is_sos):
                messagebox.showinfo("Saved", "Contact added")
                self.show_main_menu()
            else:
                messagebox.showerror("Error", "Phone already exists")

        tk.Button(frame, text="Save", command=save).pack(pady=10)
        tk.Button(frame, text="Back", command=self.show_main_menu).pack()

    def show_view_screen(self):
        self._clear_and_setup("View Contacts")
        frame = self.frames["View Contacts"]
        contacts = database.fetch_contacts(self.current_user_id)

        tree = ttk.Treeview(frame, columns=("ID", "Name", "Phone", "Email", "Category", "SOS"), show="headings")
        for col in tree["columns"]:
            tree.heading(col, text=col)
            tree.column(col, width=100)
        for contact in contacts:
            tree.insert("", "end", values=contact)
        tree.pack(fill="both", expand=True)

        tk.Button(frame, text="Back", command=self.show_main_menu).pack(pady=10)

    def show_search_screen(self):
        self._clear_and_setup("Search Contacts")
        frame = self.frames["Search Contacts"]

        tk.Label(frame, text="Enter search query:").pack()
        query_entry = tk.Entry(frame)
        query_entry.pack()

        def search():
            query = query_entry.get().strip()
            results = database.search_contacts(self.current_user_id, query)
            if not results:
                messagebox.showinfo("No Results", "No contacts found")
                return

            result_frame = tk.Frame(frame)
            result_frame.pack(pady=10)
            tree = ttk.Treeview(result_frame, columns=("ID", "Name", "Phone", "Email", "Category", "SOS"), show="headings")
            for col in tree["columns"]:
                tree.heading(col, text=col)
                tree.column(col, width=100)
            for contact in results:
                tree.insert("", "end", values=contact)
            tree.pack(fill="both", expand=True)

        tk.Button(frame, text="Search", command=search).pack(pady=5)
        tk.Button(frame, text="Back", command=self.show_main_menu).pack()

    def show_delete_screen(self):
        self._clear_and_setup("Delete Contact")
        frame = self.frames["Delete Contact"]

        tk.Label(frame, text="Enter Contact ID to delete:").pack()
        id_entry = tk.Entry(frame)
        id_entry.pack()

        def delete():
            try:
                contact_id = int(id_entry.get().strip())
                if database.delete_contact(self.current_user_id, contact_id):
                    messagebox.showinfo("Deleted", "Contact deleted")
                else:
                    messagebox.showerror("Error", "Not found or unauthorized")
            except ValueError:
                messagebox.showerror("Error", "Invalid ID")

        tk.Button(frame, text="Delete", command=delete).pack(pady=5)
        tk.Button(frame, text="Back", command=self.show_main_menu).pack()

    def show_qr_screen(self):
        self._clear_and_setup("Generate QR")
        frame = self.frames["Generate QR"]

        tk.Label(frame, text="Enter Contact ID:").pack()
        id_entry = tk.Entry(frame)
        id_entry.pack()

        def generate():
            try:
                contact_id = int(id_entry.get().strip())
                qr_file = database.generate_qr(self.current_user_id, contact_id)
                if qr_file:
                    messagebox.showinfo("QR Generated", f"Saved as: {qr_file}")
                else:
                    messagebox.showerror("Error", "Contact not found")
            except ValueError:
                messagebox.showerror("Error", "Invalid ID")

        tk.Button(frame, text="Generate QR", command=generate).pack(pady=5)
        tk.Button(frame, text="Back", command=self.show_main_menu).pack()

    def generate_all_qr(self):
        file = database.generate_qr_for_all_contacts(self.current_user_id)
        if file:
            messagebox.showinfo("QR Generated", f"Saved as: {file}")
        else:
            messagebox.showwarning("Empty", "No contacts found")

    def show_whatsapp_screen(self):
        self._clear_and_setup("Send WhatsApp")
        frame = self.frames["Send WhatsApp"]

        tk.Label(frame, text="Phone with country code:").pack()
        phone_entry = tk.Entry(frame)
        phone_entry.pack()
        tk.Label(frame, text="Message:").pack()
        msg_entry = tk.Entry(frame)
        msg_entry.pack()

        def send():
            phone = phone_entry.get().strip()
            message = msg_entry.get().strip()
            url = f"https://api.ultramsg.com/{ULTRAMSG_INSTANCE_ID}/messages/chat"
            payload = {"token": ULTRAMSG_TOKEN, "to": phone, "body": message}
            headers = {"Content-Type": "application/x-www-form-urlencoded"}
            response = requests.post(url, data=payload, headers=headers)
            if response.status_code == 200:
                messagebox.showinfo("Success", "Message sent!")
            else:
                messagebox.showerror("Error", response.text)

        tk.Button(frame, text="Send", command=send).pack(pady=5)
        tk.Button(frame, text="Back", command=self.show_main_menu).pack()

    def _clear_and_setup(self, screen_name):
        for widget in self.winfo_children():
            widget.destroy()
        frame = tk.Frame(self)
        frame.pack(fill="both", expand=True)
        self.frames[screen_name] = frame
        tk.Label(frame, text=screen_name, font=("Arial", 16)).pack(pady=10)


if __name__ == "__main__":
    app = ContactManagerApp()
    app.mainloop()
