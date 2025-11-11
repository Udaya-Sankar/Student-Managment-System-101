# app.py
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, filedialog
from storage import load_data, save_data
from utils import (
    generate_student_id,
    generate_temp_password,
    compute_totals_and_ranks,
    export_rank_list_csv,
)
from datetime import datetime
from typing import Optional

APP_TITLE = "Student Management System - v4 (Final)"


class SMSApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(APP_TITLE)
        self.geometry("980x620")
        self.minsize(850, 500)
        self.data = load_data()
        self.current_user: Optional[str] = None
        self.current_role: Optional[str] = None
        self._build_login()

    # ---------- Login Screen ----------
    def _build_login(self) -> None:
        for w in self.winfo_children():
            w.destroy()
        frame = ttk.Frame(self, padding=18)
        frame.pack(expand=True, fill=tk.BOTH)

        ttk.Label(frame, text="Student Management System", font=("Helvetica", 20)).pack(pady=6)

        role_frame = ttk.Frame(frame)
        role_frame.pack(pady=6)
        self.role_var = tk.StringVar(value="faculty")
        ttk.Radiobutton(role_frame, text="Faculty", variable=self.role_var, value="faculty").grid(row=0, column=0, padx=6)
        ttk.Radiobutton(role_frame, text="Student", variable=self.role_var, value="student").grid(row=0, column=1, padx=6)

        login_frame = ttk.Frame(frame)
        login_frame.pack(pady=12)
        ttk.Label(login_frame, text="Username / Student ID:").grid(row=0, column=0, sticky=tk.E, padx=6, pady=4)
        self.ent_user = ttk.Entry(login_frame, width=36)
        self.ent_user.grid(row=0, column=1, padx=6, pady=4)
        ttk.Label(login_frame, text="Password:").grid(row=1, column=0, sticky=tk.E, padx=6, pady=4)
        self.ent_pass = ttk.Entry(login_frame, width=36, show="*")
        self.ent_pass.grid(row=1, column=1, padx=6, pady=4)

        btn_frame = ttk.Frame(frame)
        btn_frame.pack(pady=10)
        ttk.Button(btn_frame, text="Login", command=self._handle_login).grid(row=0, column=0, padx=8)
        ttk.Button(btn_frame, text="Register Faculty", command=self._register_faculty).grid(row=0, column=1, padx=8)
        ttk.Button(btn_frame, text="Quit", command=self.destroy).grid(row=0, column=2, padx=8)

    def _register_faculty(self) -> None:
        uname = simpledialog.askstring("Register Faculty", "Faculty username:", parent=self)
        if not uname:
            return
        if uname in self.data["faculties"]:
            messagebox.showerror("Error", "Faculty username already exists.")
            return
        name = simpledialog.askstring("Full name:", "Full name:", parent=self)
        pwd = simpledialog.askstring("Password:", "Password:", parent=self, show="*")
        if not name or not pwd:
            return
        self.data["faculties"][uname] = {"name": name, "password": pwd}
        save_data(self.data)
        messagebox.showinfo("OK", "Faculty registered.")

    def _handle_login(self) -> None:
        uname = self.ent_user.get().strip()
        pwd = self.ent_pass.get().strip()
        role = self.role_var.get()
        if role == "faculty":
            f = self.data["faculties"].get(uname)
            if not f or f.get("password") != pwd:
                messagebox.showerror("Login failed", "Invalid faculty credentials.")
                return
            self.current_user = uname
            self.current_role = "faculty"
            self._build_faculty_dashboard()
        else:
            s = self.data["students"].get(uname)
            if not s or s.get("password") != pwd:
                messagebox.showerror("Login failed", "Invalid student credentials.")
                return
            if s.get("first_login", True):
                new_pwd = simpledialog.askstring("First Login", "Set a new password:", parent=self, show="*")
                if not new_pwd:
                    messagebox.showwarning("First login", "You must set a password.")
                    return
                s["password"] = new_pwd
                s["first_login"] = False
                save_data(self.data)
                messagebox.showinfo("Password updated", "Password changed successfully.")
            self.current_user = uname
            self.current_role = "student"
            self._build_student_view()

    # ---------- Faculty Dashboard ----------
    def _build_faculty_dashboard(self) -> None:
        for w in self.winfo_children():
            w.destroy()
        top = ttk.Frame(self, padding=8)
        top.pack(side=tk.TOP, fill=tk.X)
        ttk.Label(top, text=f"Faculty: {self.data['faculties'][self.current_user]['name']}", font=("Helvetica", 14)).pack(side=tk.LEFT)
        ttk.Button(top, text="Export Rank CSV", command=self._export_csv_dialog).pack(side=tk.RIGHT, padx=6)
        ttk.Button(top, text="Logout", command=self._logout).pack(side=tk.RIGHT, padx=6)

        main = ttk.PanedWindow(self, orient=tk.HORIZONTAL)
        main.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)

        # left: operations
        left = ttk.Frame(main, width=300, padding=8)
        main.add(left, weight=1)
        ttk.Button(left, text="Create Class", command=self._create_class).pack(fill=tk.X, pady=4)
        ttk.Button(left, text="Add Subject to Class", command=self._add_subject_to_class).pack(fill=tk.X, pady=4)
        ttk.Button(left, text="Register Student to Class", command=self._register_student_to_class).pack(fill=tk.X, pady=4)
        ttk.Button(left, text="Add / Update Marks", command=self._add_update_marks).pack(fill=tk.X, pady=4)
        ttk.Button(left, text="Refresh Rank List", command=self._refresh_rank_list).pack(fill=tk.X, pady=4)

        # right: class selector and rank list
        right = ttk.Frame(main, padding=8)
        main.add(right, weight=3)
        ttk.Label(right, text="Select Class:").pack(anchor=tk.W)
        self.class_combo = ttk.Combobox(right, state="readonly")
        self.class_combo.pack(fill=tk.X, pady=4)
        self.class_combo.bind("<<ComboboxSelected>>", lambda e: self._refresh_rank_list())
        ttk.Label(right, text="Rank List:").pack(anchor=tk.W, pady=(8, 0))
        self.rank_tree = ttk.Treeview(right, columns=("rank", "id", "name", "total"), show="headings", selectmode="browse")
        self.rank_tree.heading("rank", text="Rank")
        self.rank_tree.heading("id", text="Student ID")
        self.rank_tree.heading("name", text="Name")
        self.rank_tree.heading("total", text="Total")
        self.rank_tree.column("rank", width=60, anchor=tk.CENTER)
        self.rank_tree.column("id", width=160, anchor=tk.CENTER)
        self.rank_tree.column("name", width=220)
        self.rank_tree.column("total", width=80, anchor=tk.CENTER)
        self.rank_tree.pack(fill=tk.BOTH, expand=True)
        self.rank_tree.bind("<Double-1>", self._on_rank_double_click)
        self._populate_class_combo()

    def _logout(self) -> None:
        self.current_user = None
        self.current_role = None
        self._build_login()

    def _populate_class_combo(self) -> None:
        fac = self.current_user
        classes = [(cid, c["name"]) for cid, c in self.data["classes"].items() if c.get("faculty") == fac]
        self.fac_classes = classes
        vals = [f"{name} ({cid})" for cid, name in classes]
        self.class_combo["values"] = vals
        if vals:
            self.class_combo.current(0)
            self._refresh_rank_list()
        else:
            for i in self.rank_tree.get_children():
                self.rank_tree.delete(i)

    def _create_class(self) -> None:
        cname = simpledialog.askstring("Create Class", "Class name (e.g., 10A):", parent=self)
        if not cname:
            return
        cid = f"class_{int(datetime.now().timestamp())}"
        self.data["classes"][cid] = {"name": cname, "faculty": self.current_user, "students": [], "subjects": []}
        save_data(self.data)
        messagebox.showinfo("Created", f"Class '{cname}' created.")
        self._populate_class_combo()

    def _choose_class_for_faculty(self) -> Optional[str]:
        if not getattr(self, "fac_classes", None):
            messagebox.showerror("No classes", "Create a class first.")
            return None
        idx = self.class_combo.current()
        if idx < 0:
            messagebox.showerror("Choose class", "Select a class from dropdown.")
            return None
        return self.fac_classes[idx][0]

    def _add_subject_to_class(self) -> None:
        cid = self._choose_class_for_faculty()
        if not cid:
            return
        sub = simpledialog.askstring("Add Subject", "Subject name:", parent=self)
        if not sub:
            return
        if sub in self.data["classes"][cid]["subjects"]:
            messagebox.showwarning("Exists", "Subject already exists.")
            return
        self.data["classes"][cid]["subjects"].append(sub)
        save_data(self.data)
        messagebox.showinfo("Added", f"Subject '{sub}' added to class.")

    def _register_student_to_class(self) -> None:
        cid = self._choose_class_for_faculty()
        if not cid:
            return
        roll = simpledialog.askstring("Student Roll", "Enter roll number:", parent=self)
        name = simpledialog.askstring("Student Name", "Full name:", parent=self)
        if not roll or not name:
            return
        sid = generate_student_id(roll)
        pwd = generate_temp_password()
        self.data["students"][sid] = {
            "name": name,
            "password": pwd,
            "first_login": True,
            "class_id": cid,
            "marks": {}
        }
        self.data["classes"][cid]["students"].append(sid)
        save_data(self.data)
        messagebox.showinfo("Student Created", f"ID: {sid}\nTemp Password: {pwd}")
        self._refresh_rank_list()

    def _add_update_marks(self) -> None:
        cid = self._choose_class_for_faculty()
        if not cid:
            return
        cls = self.data["classes"][cid]
        subjects = cls.get("subjects", [])
        if not subjects:
            messagebox.showerror("No subjects", "Add subjects to class first.")
            return
        students = cls.get("students", [])
        if not students:
            messagebox.showerror("No students", "Register students first.")
            return
        choices = [f"{self.data['students'][s]['name']} ({s})" for s in students]
        idx = simpledialog.askinteger("Choose Student", "Enter number:\n" + "\n".join(f"{i+1}. {c}" for i, c in enumerate(choices)),
                                      parent=self, minvalue=1, maxvalue=len(choices))
        if not idx:
            return
        sid = students[idx - 1]
        marks_win = tk.Toplevel(self)
        marks_win.title(f"Marks for {self.data['students'][sid]['name']} ({sid})")
        entries = {}
        for r, sub in enumerate(subjects):
            ttk.Label(marks_win, text=sub).grid(row=r, column=0, padx=8, pady=6, sticky=tk.E)
            ent = ttk.Entry(marks_win, width=10)
            ent.grid(row=r, column=1, padx=8, pady=6)
            cur = str(self.data["students"][sid].get("marks", {}).get(sub, ""))
            ent.insert(0, cur)
            entries[sub] = ent

        def save_marks() -> None:
            try:
                for sub, ent in entries.items():
                    text = ent.get().strip()
                    if text == "":
                        continue
                    val = int(text)
                    if "marks" not in self.data["students"][sid]:
                        self.data["students"][sid]["marks"] = {}
                    self.data["students"][sid]["marks"][sub] = val
                save_data(self.data)
                messagebox.showinfo("Saved", "Marks saved.")
                marks_win.destroy()
                self._refresh_rank_list()
            except ValueError:
                messagebox.showerror("Invalid", "Enter integer marks only.")

        ttk.Button(marks_win, text="Save", command=save_marks).grid(row=len(subjects), column=0, columnspan=2, pady=10)

    def _refresh_rank_list(self) -> None:
        cid = self._choose_class_for_faculty()
        if not cid:
            return
        ranks = compute_totals_and_ranks(self.data, cid)
        for i in self.rank_tree.get_children():
            self.rank_tree.delete(i)
        arr = sorted([(info["rank"], sid, info["total"]) for sid, info in ranks.items()], key=lambda x: x[0])
        for rank, sid, total in arr:
            name = self.data["students"].get(sid, {}).get("name", "Unknown")
            self.rank_tree.insert("", tk.END, values=(rank, sid, name, total))

    def _on_rank_double_click(self, event) -> None:
        sel = self.rank_tree.selection()
        if not sel:
            return
        item = sel[0]
        vals = self.rank_tree.item(item, "values")
        if not vals:
            return
        sid = vals[1]
        self._open_student_popup(sid)

    def _open_student_popup(self, sid: str) -> None:
        student = self.data["students"].get(sid)
        if not student:
            return
        cid = student.get("class_id")
        subjects = []
        if cid:
            subjects = self.data["classes"][cid].get("subjects", [])
        ranks = compute_totals_and_ranks(self.data, cid) if cid else {}
        popup = tk.Toplevel(self)
        popup.title(f"{student['name']} - Details")
        popup.geometry("380x320")
        ttk.Label(popup, text=f"{student['name']} ({sid})", font=("Helvetica", 12)).pack(pady=6)
        body = ttk.Frame(popup, padding=8)
        body.pack(fill=tk.BOTH, expand=True)
        for sub in subjects:
            val = student.get("marks", {}).get(sub, 0)
            ttk.Label(body, text=f"{sub}: {val}").pack(anchor=tk.W, padx=10, pady=2)
        total = ranks.get(sid, {}).get("total", 0)
        rank = ranks.get(sid, {}).get("rank", "-")
        ttk.Label(popup, text=f"Total: {total}    Rank: {rank}", font=("Helvetica", 11)).pack(pady=8)
        ttk.Button(popup, text="Close", command=popup.destroy).pack(pady=6)

    def _export_csv_dialog(self) -> None:
        cid = self._choose_class_for_faculty()
        if not cid:
            return
        fpath = filedialog.asksaveasfilename(self, defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
        if not fpath:
            return
        try:
            export_rank_list_csv(self.data, cid, fpath)
            messagebox.showinfo("Exported", f"Rank list exported to:\n{fpath}")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    # ---------- Student View ----------
    def _build_student_view(self) -> None:
        for w in self.winfo_children():
            w.destroy()
        top = ttk.Frame(self, padding=8)
        top.pack(side=tk.TOP, fill=tk.X)
        student = self.data["students"][self.current_user]
        ttk.Label(top, text=f"Student: {student['name']}", font=("Helvetica", 14)).pack(side=tk.LEFT)
        ttk.Button(top, text="Logout", command=self._logout).pack(side=tk.RIGHT)

        main = ttk.Frame(self, padding=12)
        main.pack(fill=tk.BOTH, expand=True)
        cid = student.get("class_id")
        if not cid:
            ttk.Label(main, text="You are not assigned to any class.").pack()
            return
        cls = self.data["classes"][cid]
        ttk.Label(main, text=f"Class: {cls['name']}", font=("Helvetica", 12)).pack(anchor=tk.W)
        ttk.Label(main, text="Your Marks:", font=("Helvetica", 12)).pack(anchor=tk.W, pady=(8, 0))
        for sub in cls.get("subjects", []):
            val = student.get("marks", {}).get(sub, 0)
            ttk.Label(main, text=f"{sub}: {val}").pack(anchor=tk.W, padx=8)
        ranks = compute_totals_and_ranks(self.data, cid)
        total = ranks.get(self.current_user, {}).get("total", 0)
        rank = ranks.get(self.current_user, {}).get("rank", "-")
        ttk.Label(main, text=f"Total: {total}    Rank: {rank}", font=("Helvetica", 12)).pack(pady=12)


if __name__ == "__main__":
    app = SMSApp()
    app.mainloop()
