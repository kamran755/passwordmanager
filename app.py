import tkinter as tk
from tkinter import messagebox, ttk
import sqlite3
import random
import string
import csv  # CSV export

# ===== COLORS & STYLES =====
BG_MAIN = "#1e1e2f"
FG_TEXT = "#ffffff"
ACCENT = "#4caf50"
ACCENT2 = "#2196f3"

# ===== DATABASE SETUP =====
conn = sqlite3.connect("passwords.db")
c = conn.cursor()
c.execute("""
CREATE TABLE IF NOT EXISTS passwords (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    website TEXT,
    username TEXT,
    password TEXT
)
""")
conn.commit()

# naya NOTES column add (agar pehle se ho to error ignore)
try:
    c.execute("ALTER TABLE passwords ADD COLUMN notes TEXT")
    conn.commit()
except Exception:
    pass


# ===== MAIN APP WINDOW =====
def show_main_app():
    global root, website_entry, username_entry, password_entry, notes_entry, status_label

    root = tk.Tk()
    root.title("Password Manager - Kamran Codes Lab")
    root.geometry("500x330")
    root.configure(bg=BG_MAIN)

    # Icon
    try:
        root.iconbitmap("icon.ico")
    except Exception as e:
        print("Icon load error:", e)

    # Heading
    title_label = tk.Label(
        root,
        text="🔐 Password Manager",
        font=("Segoe UI", 14, "bold"),
        bg=BG_MAIN,
        fg=FG_TEXT
    )
    title_label.grid(row=0, column=0, columnspan=2, pady=(8, 4))

    # Labels
    lbl_font = ("Segoe UI", 10)

    tk.Label(root, text="Website:", font=lbl_font, bg=BG_MAIN, fg=FG_TEXT).grid(
        row=1, column=0, padx=10, pady=4, sticky="w"
    )
    tk.Label(root, text="Username:", font=lbl_font, bg=BG_MAIN, fg=FG_TEXT).grid(
        row=2, column=0, padx=10, pady=4, sticky="w"
    )
    tk.Label(root, text="Password:", font=lbl_font, bg=BG_MAIN, fg=FG_TEXT).grid(
        row=3, column=0, padx=10, pady=4, sticky="w"
    )
    tk.Label(root, text="Notes:", font=lbl_font, bg=BG_MAIN, fg=FG_TEXT).grid(
        row=4, column=0, padx=10, pady=4, sticky="w"
    )

    # Entries
    entry_font = ("Segoe UI", 10)

    website_entry = tk.Entry(root, width=36, font=entry_font)
    website_entry.grid(row=1, column=1, padx=10, sticky="w")

    username_entry = tk.Entry(root, width=36, font=entry_font)
    username_entry.grid(row=2, column=1, padx=10, sticky="w")

    password_entry = tk.Entry(root, width=36, font=entry_font, show="*")
    password_entry.grid(row=3, column=1, padx=10, sticky="w")

    notes_entry = tk.Entry(root, width=36, font=entry_font)
    notes_entry.grid(row=4, column=1, padx=10, sticky="w")

    # Status label
    status_label = tk.Label(
        root,
        text="Ready",
        font=("Segoe UI", 9),
        bg=BG_MAIN,
        fg="#cccccc"
    )
    status_label.grid(row=5, column=0, columnspan=2, pady=(0, 4))

    # ===== FUNCTIONS =====
    def save_password():
        website = website_entry.get().strip()
        username = username_entry.get().strip()
        password = password_entry.get().strip()
        notes = notes_entry.get().strip()

        if not website or not username or not password:
            messagebox.showwarning("Warning", "Please fill website, username, password")
            status_label.config(text="Fill required fields to save")
            return

        c.execute(
            "INSERT INTO passwords (website, username, password, notes) VALUES (?, ?, ?, ?)",
            (website, username, password, notes)
        )
        conn.commit()

        status_label.config(text=f"Auto Saved: {website}")

        website_entry.delete(0, tk.END)
        username_entry.delete(0, tk.END)
        password_entry.delete(0, tk.END)
        notes_entry.delete(0, tk.END)
        website_entry.focus_set()

        root.after(3000, lambda: status_label.config(text="Ready"))

    def build_table_window(title, rows, allow_delete=False):
        win = tk.Toplevel(root)
        win.title(title)
        win.geometry("700x380")
        win.configure(bg=BG_MAIN)

        tk.Label(
            win, text=title,
            font=("Segoe UI", 12, "bold"),
            bg=BG_MAIN, fg=FG_TEXT
        ).pack(pady=(8, 4))

        frame = tk.Frame(win, bg=BG_MAIN)
        frame.pack(fill="both", expand=True, padx=10, pady=10)

        style = ttk.Style()
        style.theme_use("default")
        style.configure(
            "Treeview",
            background="#25253a",
            foreground="white",
            fieldbackground="#25253a",
            rowheight=22,
            font=("Segoe UI", 9)
        )
        style.configure(
            "Treeview.Heading",
            background="#33334d",
            foreground="white",
            font=("Segoe UI", 9, "bold")
        )
        style.map("Treeview", background=[("selected", "#546e7a")])

        columns = ("id", "website", "username", "password", "notes")
        tree = ttk.Treeview(frame, columns=columns, show="headings", selectmode="extended")

        tree.heading("id", text="ID")
        tree.heading("website", text="Website")
        tree.heading("username", text="Username")
        tree.heading("password", text="Password")
        tree.heading("notes", text="Notes")

        tree.column("id", width=40, anchor="center")
        tree.column("website", width=150, anchor="w")
        tree.column("username", width=150, anchor="w")
        tree.column("password", width=180, anchor="w")
        tree.column("notes", width=200, anchor="w")

        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
        tree.configure(yscroll=scrollbar.set)

        tree.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")

        frame.rowconfigure(0, weight=1)
        frame.columnconfigure(0, weight=1)

        for i, row in enumerate(rows):
            tag = "oddrow" if i % 2 else "evenrow"
            tree.insert("", tk.END, values=row, tags=(tag,))

        tree.tag_configure("evenrow", background="#25253a")
        tree.tag_configure("oddrow", background="#2d2d45")

        def delete_selected():
            selected_items = tree.selection()
            if not selected_items:
                messagebox.showwarning("Warning", "Select at least one row to delete")
                return

            if not messagebox.askyesno("Confirm Delete", "Delete selected record(s)?"):
                return

            ids_to_delete = []
            for item in selected_items:
                row_values = tree.item(item, "values")
                ids_to_delete.append(row_values[0])

            for rec_id in ids_to_delete:
                c.execute("DELETE FROM passwords WHERE id = ?", (rec_id,))
            conn.commit()

            for item in selected_items:
                tree.delete(item)

            status_label.config(text="Deleted selected record(s)")
            root.after(3000, lambda: status_label.config(text="Ready"))

        if allow_delete:
            btn_del = tk.Button(
                win, text="Delete Selected",
                command=delete_selected,
                bg="#e53935", fg="white",
                font=("Segoe UI", 9, "bold")
            )
            btn_del.pack(pady=6)

    def show_passwords():
        c.execute("SELECT id, website, username, password, notes FROM passwords")
        rows = c.fetchall()
        if not rows:
            messagebox.showinfo("Info", "No passwords saved yet.")
            status_label.config(text="No passwords to show")
            return
        build_table_window("All Saved Passwords", rows, allow_delete=True)

    def search_password():
        query = website_entry.get().strip()
        if not query:
            messagebox.showwarning("Warning", "Enter website to search")
            status_label.config(text="Enter website to search")
            return

        c.execute(
            "SELECT id, website, username, password, notes FROM passwords WHERE website LIKE ?",
            (f"%{query}%",)
        )
        rows = c.fetchall()
        if not rows:
            messagebox.showinfo("Info", "No matching entries found.")
            status_label.config(text="No match found")
            return
        build_table_window(f"Search Results for '{query}'", rows, allow_delete=True)
        status_label.config(text=f"Search results for: {query}")

    def generate_password():
        chars = string.ascii_letters + string.digits + string.punctuation
        pwd = "".join(random.choice(chars) for _ in range(12))
        password_entry.delete(0, tk.END)
        password_entry.insert(0, pwd)
        status_label.config(text="Generated strong password")
        root.after(3000, lambda: status_label.config(text="Ready"))

    def export_to_csv():
        c.execute("SELECT id, website, username, password, notes FROM passwords")
        rows = c.fetchall()

        if not rows:
            messagebox.showinfo("Info", "No data to export.")
            status_label.config(text="No data to export")
            return

        try:
            with open("passwords_export.csv", "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(["ID", "Website", "Username", "Password", "Notes"])
                writer.writerows(rows)
            messagebox.showinfo("Export", "Exported to passwords_export.csv")
            status_label.config(text="Exported to passwords_export.csv")
        except Exception as e:
            messagebox.showerror("Error", f"Export failed: {e}")
            status_label.config(text="Export failed")

    # ===== BUTTONS =====
    btn_font = ("Segoe UI", 9, "bold")

    btn_frame = tk.Frame(root, bg=BG_MAIN)
    btn_frame.grid(row=6, column=0, columnspan=2, pady=8)

    tk.Button(
        btn_frame, text="Save",
        command=save_password,
        bg=ACCENT, fg="white",
        font=btn_font, width=10
    ).grid(row=0, column=0, padx=4)

    tk.Button(
        btn_frame, text="Show All",
        command=show_passwords,
        bg=ACCENT2, fg="white",
        font=btn_font, width=10
    ).grid(row=0, column=1, padx=4)

    tk.Button(
        btn_frame, text="Search",
        command=search_password,
        bg="#ff9800", fg="black",
        font=btn_font, width=10
    ).grid(row=0, column=2, padx=4)

    tk.Button(
        btn_frame, text="Export CSV",
        command=export_to_csv,
        bg="#607d8b", fg="white",
        font=btn_font, width=10
    ).grid(row=0, column=3, padx=4)

    tk.Button(
        root, text="Generate Password",
        command=generate_password,
        bg="#9c27b0", fg="white",
        font=btn_font, width=34
    ).grid(row=7, column=0, columnspan=2, pady=(0, 8))

    # Enter key = auto save
    password_entry.bind("<Return>", lambda event: save_password())

    root.mainloop()


# ===== SPLASH SCREEN =====
def show_splash():
    splash = tk.Tk()
    splash.overrideredirect(True)
    splash.configure(bg="#111111")

    w, h = 320, 160
    screen_w = splash.winfo_screenwidth()
    screen_h = splash.winfo_screenheight()
    x = (screen_w // 2) - (w // 2)
    y = (screen_h // 2) - (h // 2)
    splash.geometry(f"{w}x{h}+{x}+{y}")

    label = tk.Label(
        splash,
        text="Kamran Codes Lab\nPassword Manager",
        font=("Segoe UI", 12, "bold"),
        bg="#111111",
        fg="#ffffff",
        justify="center"
    )
    label.pack(expand=True)

    splash.after(2000, lambda: (splash.destroy(), show_main_app()))
    splash.mainloop()


if __name__ == "__main__":
    show_splash()
    conn.close()
