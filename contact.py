# pip install mysql-connector-python
import tkinter as tk
from tkinter import messagebox, font, ttk
import mysql.connector
from mysql.connector import errorcode

DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',       
    'password': '12345678',  
    'database': 'shamim' 
}

class ContactManagerApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Contact Manager")
        self.geometry("800x600")
        self.config(bg="#f4f4f9")
        
        self.bold_font = font.Font(family="Helvetica", size=14, weight="bold")
        self.normal_font = font.Font(family="Helvetica", size=12)
        
        self.db_connection = self.create_connection() 
        
        if self.db_connection:
            self.create_ui()
            self.load_data()
        else:
            self.destroy()

    def create_connection(self):
        try:
            conn = mysql.connector.connect(use_pure=True, **DB_CONFIG)
            print("Database connection established successfully.")
            return conn
        except mysql.connector.Error as err:
            if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
                 msg = "Connection Failed: Invalid user credentials (username/password)."
            elif err.errno == errorcode.ER_BAD_DB_ERROR:
                msg = f"Connection Failed: Database '{DB_CONFIG['database']}' does not exist."
            else:
                msg = f"Connection Failed: {err}"     
            messagebox.showerror("Database Error", f"{msg}\n\nCheck your DB_CONFIG credentials and ensure MySQL is running.")
            return None
            
    def create_ui(self):
        entry_frame = tk.LabelFrame(self, text="Contact Entry", font=self.bold_font, bg="#f4f4f9")
        entry_frame.pack(pady=10, padx=20, fill="x")
        
        tk.Label(entry_frame, text="Name:", font=self.normal_font, bg="#f4f4f9").grid(row=0, column=0, padx=10, pady=5, sticky="w")
        self.name_entry = tk.Entry(entry_frame, width=40, font=self.normal_font)
        self.name_entry.grid(row=0, column=1, padx=10, pady=5)

        tk.Label(entry_frame, text="Mobile:", font=self.normal_font, bg="#f4f4f9").grid(row=1, column=0, padx=10, pady=5, sticky="w")
        self.mobile_entry = tk.Entry(entry_frame, width=40, font=self.normal_font)
        self.mobile_entry.grid(row=1, column=1, padx=10, pady=5)
        
        # Connect the button to the save_data function
        save_btn = tk.Button(entry_frame, text="Data Save", command=self.save_data, font=self.bold_font, bg="#4CAF50", fg="white")
        save_btn.grid(row=2, column=0, columnspan=2, pady=15)

        
        view_frame = tk.LabelFrame(self, text="Saved Data", font=self.bold_font, bg="#f4f4f9")
        view_frame.pack(pady=10, padx=20, fill="both", expand=True)
        
        columns = ("ID", "Name", "Mobile Number") # Use descriptive names
        self.tree = ttk.Treeview(view_frame, columns=columns, show='headings', selectmode='browse')
        
        self.tree.heading("ID", text="ID", anchor=tk.CENTER)
        self.tree.column("ID", width=50, anchor=tk.CENTER)
        self.tree.heading("Name", text="Name", anchor=tk.W)
        self.tree.column("Name", width=250, anchor=tk.W)
        self.tree.heading("Mobile Number", text="Mobile Number", anchor=tk.CENTER)
        self.tree.column("Mobile Number", width=150, anchor=tk.CENTER)
        
        # Add a scrollbar
        scrollbar = ttk.Scrollbar(view_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.pack(fill="both", expand=True, side=tk.LEFT)

    def load_data(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        if not self.db_connection or not self.db_connection.is_connected():
            return

        try:
            cursor = self.db_connection.cursor()
            cursor.execute("SELECT id, name, mobile FROM contact ORDER BY id ASC")
            records = cursor.fetchall()
            cursor.close()
            
            for record in records:
                self.tree.insert('', tk.END, values=record)
                
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Failed to load Data: {err}")

    def save_data(self):
        name = self.name_entry.get().strip()
        mobile = self.mobile_entry.get().strip()

        if not name or not mobile:
            messagebox.showerror("Error", "Please, Insert Name and Mobile number both.")
            return

        if not self.db_connection or not self.db_connection.is_connected():
             messagebox.showerror("Error", "Database connection lost. Cannot save data.")
             return

        try:
            cursor = self.db_connection.cursor()
            insert_query = "INSERT INTO contact (name, mobile) VALUES (%s, %s)"
            cursor.execute(insert_query, (name, mobile))
            self.db_connection.commit()
            cursor.close()
        
            messagebox.showinfo("Success", f"Contact '{name}' Successfully Saved.")
            
            self.name_entry.delete(0, tk.END)
            self.mobile_entry.delete(0, tk.END)
            
            self.load_data()
            
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Failed to save Data: {err}")

if __name__ == "__main__":
    app = ContactManagerApp()
    app.mainloop()