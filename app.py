import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from storage import load_data, save_data
import random, string
from datetime import datetime

# -------- utility helpers ----------
def gen_pwd(n=8):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=n))

def gen_id(roll):
    return f"STU_{roll}_{''.join(random.choices(string.ascii_uppercase + string.digits, k=4))}"

# -------- GUI application ----------
class SMSApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Student Management System - Version 2 (Classes)")
        self.geometry("550x350")
        self.data = load_data()
        self.role = tk.StringVar(value="faculty")
        self.build_login()

    # ---------- login screen ----------
    def build_login(self):
        for w in self.winfo_children():
            w.destroy()
        ttk.Label(self, text="Login", font=("Helvetica", 16)).pack(pady=10)
        frm_role = ttk.Frame(self); frm_role.pack()
        ttk.Radiobutton(frm_role, text="Faculty", variable=self.role, value="faculty").grid(row=0, column=0)
        ttk.Radiobutton(frm_role, text="Student", variable=self.role, value="student").grid(row=0, column=1)

        self.u = tk.StringVar(); self.p = tk.StringVar()
        ttk.Label(self, text="Username:").pack(pady=(10,0))
        ttk.Entry(self, textvariable=self.u).pack()
        ttk.Label(self, text="Password:").pack()
        ttk.Entry(self, textvariable=self.p, show="*").pack()
        ttk.Button(self, text="Login", command=self.handle_login).pack(pady=5)
        ttk.Button(self, text="Register Faculty", command=self.register_faculty).pack()

    # ---------- faculty registration ----------
    def register_faculty(self):
        uname = simpledialog.askstring("Register Faculty", "Enter username:", parent=self)
        if not uname: return
        if uname in self.data["faculties"]:
            return messagebox.showerror("Error", "Username already exists.")
        name = simpledialog.askstring("Register Faculty", "Full name:", parent=self)
        pwd = simpledialog.askstring("Register Faculty", "Password:", parent=self, show="*")
        self.data["faculties"][uname] = {"name": name, "password": pwd}
        save_data(self.data)
        messagebox.showinfo("Success", "Faculty registered successfully.")

    # ---------- login logic ----------
    def handle_login(self):
        role = self.role.get()
        uname, pwd = self.u.get().strip(), self.p.get().strip()
        if role == "faculty":
            user = self.data["faculties"].get(uname)
            if not user or user["password"] != pwd:
                return messagebox.showerror("Login Failed", "Invalid faculty credentials.")
            self.faculty_home(uname)
        else:
            stu = self.data["students"].get(uname)
            if not stu or stu["password"] != pwd:
                return messagebox.showerror("Login Failed", "Invalid student credentials.")
            if stu.get("first_login", True):
                new_pwd = simpledialog.askstring("First Login", "Set new password:", parent=self, show="*")
                if not new_pwd: return
                stu["password"] = new_pwd
                stu["first_login"] = False
                save_data(self.data)
                messagebox.showinfo("Updated", "Password changed successfully.")
            self.student_home(uname)

    # ---------- faculty dashboard ----------
    def faculty_home(self, uname):
        for w in self.winfo_children():
            w.destroy()
        ttk.Label(self, text=f"Welcome {self.data['faculties'][uname]['name']}", font=("Helvetica", 14)).pack(pady=10)
        ttk.Button(self, text="Create Class", command=lambda:self.create_class(uname)).pack(pady=3)
        ttk.Button(self, text="Register Student to Class", command=lambda:self.register_student_to_class(uname)).pack(pady=3)
        ttk.Button(self, text="Logout", command=self.build_login).pack(pady=10)

    # ---------- create a new class ----------
    def create_class(self, faculty_uname):
        cname = simpledialog.askstring("Create Class", "Enter class name (e.g., 10A):", parent=self)
        if not cname: return
        cid = f"class_{int(datetime.now().timestamp())}"
        self.data["classes"][cid] = {"name": cname, "faculty": faculty_uname, "students": [], "subjects": []}
        save_data(self.data)
        messagebox.showinfo("Success", f"Class '{cname}' created.")

    # ---------- register a student to class ----------
    def register_student_to_class(self, faculty_uname):
        # list faculty classes
        owned = [(cid, c) for cid, c in self.data["classes"].items() if c["faculty"] == faculty_uname]
        if not owned:
            return messagebox.showerror("Error", "No classes found. Create one first.")
        # choose class
        classes_str = "\n".join([f"{i+1}. {c['name']}" for i,(cid,c) in enumerate(owned)])
        idx = simpledialog.askinteger("Select Class", f"Choose class:\n{classes_str}", parent=self, minvalue=1, maxvalue=len(owned))
        if not idx: return
        cid = owned[idx-1][0]
        roll = simpledialog.askstring("Register Student", "Enter Roll No:", parent=self)
        name = simpledialog.askstring("Register Student", "Full Name:", parent=self)
        if not roll or not name: return
        sid = gen_id(roll)
        pwd = gen_pwd()
        self.data["students"][sid] = {
            "name": name,
            "password": pwd,
            "first_login": True,
            "class_id": cid
        }
        self.data["classes"][cid]["students"].append(sid)
        save_data(self.data)
        messagebox.showinfo("Student Added", f"Student '{name}' registered.\nID: {sid}\nTemp Password: {pwd}")

    # ---------- student dashboard ----------
    def student_home(self, sid):
        for w in self.winfo_children():
            w.destroy()
        s = self.data["students"][sid]
        class_name = "Not assigned"
        if s.get("class_id"):
            class_name = self.data["classes"][s["class_id"]]["name"]
        ttk.Label(self, text=f"Welcome {s['name']}", font=("Helvetica", 14)).pack(pady=5)
        ttk.Label(self, text=f"Class: {class_name}", font=("Helvetica", 12)).pack(pady=5)
        ttk.Button(self, text="Logout", command=self.build_login).pack(pady=10)

if __name__ == "__main__":
    app = SMSApp()
    app.mainloop()
