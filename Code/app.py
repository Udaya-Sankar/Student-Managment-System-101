# app.py
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from storage import load_data, save_data
from utils import (
    generate_student_id,
    generate_temp_password,
    compute_totals_and_ranks,
)
from datetime import datetime
import random
import re
from typing import Optional

APP_TITLE = "Student Management System - Final Version"

CLASS_NAME_REGEX = re.compile(r'^\d+[A-Za-z]$')  # starts with digits, ends with 1 letter


class SMSApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(APP_TITLE)
        self.geometry("980x620")
        self.minsize(850, 500)

        # ---------- UI Styling ----------
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure("TFrame", background="#f7faff")
        style.configure("TLabel", background="#f7faff", font=("Segoe UI", 11))
        style.configure("Header.TLabel", background="#d7e3fc", font=("Segoe UI", 18, "bold"))
        style.configure("Accent.TButton", background="#2b6edc", foreground="white")
        style.map("Accent.TButton",
                  background=[("active", "#2356b3")],
                  foreground=[("active", "white")])
        style.configure("TButton", padding=6)

        self.data = load_data()
        self.current_user: Optional[str] = None
        self.current_role: Optional[str] = None
        self._build_login()

    # ---------- LOGIN SCREEN ----------
    def _build_login(self):
        for w in self.winfo_children():
            w.destroy()
        frame = ttk.Frame(self, padding=18)
        frame.pack(expand=True, fill=tk.BOTH)

        ttk.Label(frame, text="Student Management System", style="Header.TLabel", anchor="center").pack(fill=tk.X, pady=(0, 10))

        self.role_var = tk.StringVar(value="faculty")
        role_frame = ttk.Frame(frame)
        role_frame.pack(pady=6)
        ttk.Radiobutton(role_frame, text="Faculty", variable=self.role_var, value="faculty").grid(row=0, column=0, padx=8)
        ttk.Radiobutton(role_frame, text="Student", variable=self.role_var, value="student").grid(row=0, column=1, padx=8)

        login_frame = ttk.Frame(frame)
        login_frame.pack(pady=12)
        ttk.Label(login_frame, text="Username:").grid(row=0, column=0, sticky=tk.E, padx=6, pady=4)
        self.ent_user = ttk.Entry(login_frame, width=36)
        self.ent_user.grid(row=0, column=1, padx=6, pady=4)
        ttk.Label(login_frame, text="Password:").grid(row=1, column=0, sticky=tk.E, padx=6, pady=4)
        self.ent_pass = ttk.Entry(login_frame, width=36, show="*")
        self.ent_pass.grid(row=1, column=1, padx=6, pady=4)

        btn_frame = ttk.Frame(frame)
        btn_frame.pack(pady=10)
        self.login_btn = ttk.Button(btn_frame, text="Login", command=self._handle_login, style="Accent.TButton")
        self.login_btn.grid(row=0, column=0, padx=8)
        self.reg_btn = ttk.Button(btn_frame, text="Register Faculty", command=self._register_faculty)
        self.reg_btn.grid(row=0, column=1, padx=8)
        self.quit_btn = ttk.Button(btn_frame, text="Quit", command=self.destroy)
        self.quit_btn.grid(row=0, column=2, padx=8)

        # hide register button when student role is selected
        def on_role_change(*_):
            if self.role_var.get() == "student":
                self.reg_btn.grid_remove()
            else:
                self.reg_btn.grid()
        on_role_change()
        self.role_var.trace_add("write", on_role_change)

    # ---------- FACULTY REGISTRATION ----------
    def _register_faculty(self):
        while True:
            uname = simpledialog.askstring("Register Faculty", "Faculty username (unique):", parent=self)
            if uname is None:
                return
            uname = uname.strip()
            if not uname:
                messagebox.showwarning("Invalid", "Username cannot be empty.")
                continue
            if uname in self.data.get("faculties", {}):
                messagebox.showerror("Exists", "Username already taken.")
                continue
            break
        name = simpledialog.askstring("Full Name", "Enter full name:", parent=self)
        if not name:
            messagebox.showwarning("Invalid", "Full name required.")
            return
        pwd = simpledialog.askstring("Password", "Enter password:", parent=self, show="*")
        if not pwd:
            messagebox.showwarning("Invalid", "Password required.")
            return

        self.data["faculties"][uname] = {"name": name.strip(), "password": pwd}
        save_data(self.data)
        messagebox.showinfo("Success", "Faculty registered successfully!")

    # ---------- LOGIN HANDLER ----------
    def _handle_login(self):
        uname = self.ent_user.get().strip()
        pwd = self.ent_pass.get().strip()
        role = self.role_var.get()
        if not uname or not pwd:
            messagebox.showerror("Login Failed", "Enter username and password.")
            return

        if role == "faculty":
            fac = self.data.get("faculties", {}).get(uname)
            if not fac or fac.get("password") != pwd:
                messagebox.showerror("Login Failed", "Invalid faculty credentials.")
                return
            self.current_user = uname
            self.current_role = "faculty"
            self._build_faculty_dashboard()
        else:
            stu = self.data.get("students", {}).get(uname)
            if not stu or stu.get("password") != pwd:
                messagebox.showerror("Login Failed", "Invalid student credentials.")
                return
            if stu.get("first_login", True):
                while True:
                    new_pwd = simpledialog.askstring("First Login", "Set a new password:", parent=self, show="*")
                    if not new_pwd:
                        messagebox.showwarning("Invalid", "Password cannot be empty.")
                        continue
                    stu["password"] = new_pwd
                    stu["first_login"] = False
                    save_data(self.data)
                    messagebox.showinfo("Updated", "Password changed successfully.")
                    break
            self.current_user = uname
            self.current_role = "student"
            self._build_student_view()

    # ---------- FACULTY DASHBOARD ----------
    def _build_faculty_dashboard(self):
        for w in self.winfo_children():
            w.destroy()
        top = ttk.Frame(self, padding=8)
        top.pack(side=tk.TOP, fill=tk.X)
        ttk.Label(top, text=f"Faculty: {self.data['faculties'][self.current_user]['name']}", font=("Segoe UI", 13)).pack(side=tk.LEFT)
        ttk.Button(top, text="Logout", command=self._logout).pack(side=tk.RIGHT, padx=6)

        main = ttk.PanedWindow(self, orient=tk.HORIZONTAL)
        main.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)

        left = ttk.Frame(main, width=300, padding=8)
        main.add(left, weight=1)
        ttk.Button(left, text="Create Class", command=self._create_class).pack(fill=tk.X, pady=4)
        ttk.Button(left, text="Add Subject", command=self._add_subject_to_class).pack(fill=tk.X, pady=4)
        ttk.Button(left, text="Register Student", command=self._register_student_to_class).pack(fill=tk.X, pady=4)
        ttk.Button(left, text="Add / Update Marks", command=self._add_update_marks).pack(fill=tk.X, pady=4)
        ttk.Button(left, text="Refresh Rank List", command=self._refresh_rank_list).pack(fill=tk.X, pady=4)

        right = ttk.Frame(main, padding=8)
        main.add(right, weight=3)
        ttk.Label(right, text="Select Class:").pack(anchor=tk.W)
        self.class_combo = ttk.Combobox(right, state="readonly")
        self.class_combo.pack(fill=tk.X, pady=4)
        self.class_combo.bind("<<ComboboxSelected>>", lambda e: self._refresh_rank_list())

        self.rank_tree = ttk.Treeview(right, columns=("rank", "id", "name", "roll", "total"),
                                      show="headings", selectmode="browse")
        for col, width, text in [
            ("rank", 60, "Rank"),
            ("id", 160, "Student ID"),
            ("name", 200, "Name"),
            ("roll", 80, "Roll"),
            ("total", 80, "Total"),
        ]:
            self.rank_tree.heading(col, text=text)
            self.rank_tree.column(col, width=width, anchor=tk.CENTER)
        self.rank_tree.pack(fill=tk.BOTH, expand=True)
        self.rank_tree.bind("<Double-1>", self._on_rank_double_click)

        self._populate_class_combo()

    def _logout(self):
        self.current_user = None
        self.current_role = None
        self._build_login()

    # ---------- CLASS CREATION ----------
    def _create_class(self):
        while True:
            cname = simpledialog.askstring("Create Class", "Enter class name (e.g. 10A):", parent=self)
            if cname is None:
                return
            cname = cname.strip()
            if not cname:
                messagebox.showwarning("Invalid", "Class name cannot be empty.")
                continue
            if not CLASS_NAME_REGEX.match(cname):
                messagebox.showerror("Invalid", "Class must start with digits and end with one letter (e.g. 10A).")
                continue
            for c in self.data["classes"].values():
                if c["name"].lower() == cname.lower():
                    messagebox.showerror("Duplicate", f"Class '{cname}' already exists.")
                    break
            else:
                break

        cid = f"class_{int(datetime.now().timestamp())}_{random.choice('ABCDEFGHIJKLMNOPQRSTUVWXYZ')}"
        self.data["classes"][cid] = {"name": cname, "faculty": self.current_user, "students": [], "subjects": []}
        save_data(self.data)
        messagebox.showinfo("Created", f"Class '{cname}' created successfully!")
        self._populate_class_combo()

    # ---------- ADD SUBJECT ----------
    def _add_subject_to_class(self):
        cid = self._choose_class_for_faculty()
        if not cid:
            return
        sub = simpledialog.askstring("Add Subject", "Subject name:", parent=self)
        if not sub:
            return
        sub = sub.strip()
        if sub in self.data["classes"][cid].get("subjects", []):
            messagebox.showwarning("Exists", "Subject already exists.")
            return
        self.data["classes"][cid]["subjects"].append(sub)
        save_data(self.data)
        messagebox.showinfo("Added", f"Subject '{sub}' added.")

    # ---------- REGISTER STUDENT ----------
    def _register_student_to_class(self):
        cid = self._choose_class_for_faculty()
        if not cid:
            return
        roll = simpledialog.askstring("Roll Number", "Enter numeric roll number:", parent=self)
        if not roll:
            return
        roll = roll.strip()
        if not roll.isdigit():
            messagebox.showerror("Invalid", "Roll number must be numeric.")
            return
        for sid in self.data["classes"][cid]["students"]:
            if self.data["students"][sid]["roll_no"] == roll:
                messagebox.showerror("Duplicate", f"Roll number '{roll}' already exists in this class.")
                return
        name = simpledialog.askstring("Student Name", "Enter full name:", parent=self)
        if not name:
            return
        sid = generate_student_id(roll)
        pwd = generate_temp_password()
        self.data["students"][sid] = {"name": name, "password": pwd, "first_login": True,
                                      "class_id": cid, "roll_no": roll, "marks": {}}
        self.data["classes"][cid]["students"].append(sid)
        save_data(self.data)
        messagebox.showinfo("Registered", f"Student ID: {sid}\nTemp Password: {pwd}")
        self._refresh_rank_list()

    # ---------- ADD / UPDATE MARKS ----------
    def _add_update_marks(self):
        cid = self._choose_class_for_faculty()
        if not cid:
            return
        cls = self.data["classes"][cid]
        subjects = cls.get("subjects", [])
        if not subjects:
            messagebox.showerror("Error", "Add subjects first.")
            return
        students = cls.get("students", [])
        if not students:
            messagebox.showerror("Error", "No students in class.")
            return

        choices = [f"{self.data['students'][s]['name']} ({s})" for s in students]
        idx = simpledialog.askinteger("Select Student",
                                      "Enter number:\n" + "\n".join(f"{i+1}. {c}" for i, c in enumerate(choices)),
                                      parent=self, minvalue=1, maxvalue=len(choices))
        if not idx:
            return
        sid = students[idx - 1]

        win = tk.Toplevel(self)
        win.title(f"Marks - {self.data['students'][sid]['name']}")
        entries = {}
        for r, sub in enumerate(subjects):
            ttk.Label(win, text=sub).grid(row=r, column=0, padx=8, pady=6, sticky=tk.E)
            ent = ttk.Entry(win, width=12)
            ent.grid(row=r, column=1, padx=8, pady=6)
            ent.insert(0, str(self.data["students"][sid]["marks"].get(sub, "")))
            entries[sub] = ent

        def save_marks():
            try:
                for sub, ent in entries.items():
                    txt = ent.get().strip()
                    if txt == "":
                        continue
                    val = int(txt)
                    if val < 0:
                        raise ValueError
                    self.data["students"][sid]["marks"][sub] = val
                save_data(self.data)
                messagebox.showinfo("Saved", "Marks saved successfully.")
                win.destroy()
                self._refresh_rank_list()
            except ValueError:
                messagebox.showerror("Invalid", "Enter non-negative integer marks only.")

        ttk.Button(win, text="Save", command=save_marks).grid(row=len(subjects), column=0, columnspan=2, pady=10)

    # ---------- RANK LIST ----------
    def _refresh_rank_list(self):
        cid = self._choose_class_for_faculty()
        if not cid:
            return
        ranks = compute_totals_and_ranks(self.data, cid)
        for i in self.rank_tree.get_children():
            self.rank_tree.delete(i)
        arr = sorted([(info["rank"], sid, info["total"]) for sid, info in ranks.items()], key=lambda x: x[0])
        for rank, sid, total in arr:
            s = self.data["students"][sid]
            self.rank_tree.insert("", tk.END, values=(rank, sid, s["name"], s["roll_no"], total))

    def _choose_class_for_faculty(self):
        idx = self.class_combo.current()
        if idx < 0:
            messagebox.showwarning("Select", "Select a class first.")
            return None
        val = self.class_combo.get()
        for cid, c in self.data["classes"].items():
            if f"{c['name']} ({cid})" == val:
                return cid
        return None

    def _populate_class_combo(self):
        fac = self.current_user
        vals = [f"{c['name']} ({cid})" for cid, c in self.data["classes"].items() if c["faculty"] == fac]
        self.class_combo["values"] = vals
        if vals:
            self.class_combo.current(0)
            self._refresh_rank_list()

    # ---------- POPUP ----------
    def _on_rank_double_click(self, event):
        sel = self.rank_tree.selection()
        if not sel:
            return
        sid = self.rank_tree.item(sel[0], "values")[1]
        self._open_student_popup(sid)

    def _open_student_popup(self, sid: str):
        s = self.data["students"][sid]
        cid = s["class_id"]
        cls = self.data["classes"][cid]
        subjects = cls.get("subjects", [])
        ranks = compute_totals_and_ranks(self.data, cid)
        total = ranks.get(sid, {}).get("total", 0)
        rank = ranks.get(sid, {}).get("rank", "-")

        popup = tk.Toplevel(self)
        popup.title(f"{s['name']} ({s['roll_no']})")
        ttk.Label(popup, text=f"Student: {s['name']}", font=("Segoe UI", 13, "bold")).pack(pady=6)
        for sub in subjects:
            val = s["marks"].get(sub, 0)
            ttk.Label(popup, text=f"{sub}: {val}").pack(anchor=tk.W, padx=10)
        ttk.Label(popup, text=f"Total: {total}    Rank: {rank}", font=("Segoe UI", 12)).pack(pady=10)
        ttk.Button(popup, text="Close", command=popup.destroy).pack(pady=6)

    # ---------- STUDENT DASHBOARD ----------
    def _build_student_view(self):
        for w in self.winfo_children():
            w.destroy()
        top = ttk.Frame(self, padding=8)
        top.pack(side=tk.TOP, fill=tk.X)
        s = self.data["students"][self.current_user]
        ttk.Label(top, text=f"Student: {s['name']}", font=("Segoe UI", 14)).pack(side=tk.LEFT)
        ttk.Button(top, text="Logout", command=self._logout).pack(side=tk.RIGHT)

        main = ttk.Frame(self, padding=12)
        main.pack(fill=tk.BOTH, expand=True)
        cid = s["class_id"]
        cls = self.data["classes"][cid]
        ttk.Label(main, text=f"Class: {cls['name']}", font=("Segoe UI", 12)).pack(anchor=tk.W)
        ttk.Label(main, text="Your Marks:", font=("Segoe UI", 12, "bold")).pack(anchor=tk.W, pady=(8, 0))
        for sub in cls.get("subjects", []):
            val = s["marks"].get(sub, 0)
            ttk.Label(main, text=f"{sub}: {val}").pack(anchor=tk.W, padx=8)
        ranks = compute_totals_and_ranks(self.data, cid)
        total = ranks.get(self.current_user, {}).get("total", 0)
        rank = ranks.get(self.current_user, {}).get("rank", "-")
        ttk.Label(main, text=f"Total: {total}    Rank: {rank}", font=("Segoe UI", 12)).pack(pady=12)


if __name__ == "__main__":
    app = SMSApp()
    app.mainloop()
