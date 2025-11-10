import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from storage import load_data, save_data
import random, string

def gen_pwd(n=8): return ''.join(random.choices(string.ascii_letters+string.digits, k=n))
def gen_id(roll): return f"STU_{roll}_{''.join(random.choices(string.ascii_uppercase+string.digits,k=4))}"

class SMSApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Student Management System v1")
        self.geometry("450x300")
        self.data = load_data()
        self.current_user=None; self.role=None
        self.login_screen()

    def login_screen(self):
        for w in self.winfo_children(): w.destroy()
        ttk.Label(self,text="Login",font=("Helvetica",16)).pack(pady=10)
        self.role=tk.StringVar(value="faculty")
        frm=ttk.Frame(self); frm.pack(pady=5)
        ttk.Radiobutton(frm,text="Faculty",variable=self.role,value="faculty").grid(row=0,column=0)
        ttk.Radiobutton(frm,text="Student",variable=self.role,value="student").grid(row=0,column=1)
        self.u=tk.StringVar(); self.p=tk.StringVar()
        ttk.Label(self,text="Username:").pack(); ttk.Entry(self,textvariable=self.u).pack()
        ttk.Label(self,text="Password:").pack(); ttk.Entry(self,textvariable=self.p,show="*").pack()
        ttk.Button(self,text="Login",command=self.handle_login).pack(pady=5)
        ttk.Button(self,text="Register Faculty",command=self.register_faculty).pack()

    def register_faculty(self):
        u=simpledialog.askstring("Faculty Register","Username:",parent=self)
        if not u: return
        if u in self.data["faculties"]: return messagebox.showerror("Err","Exists")
        n=simpledialog.askstring("Name","Full name:",parent=self)
        p=simpledialog.askstring("Pwd","Password:",parent=self,show="*")
        self.data["faculties"][u]={"name":n,"password":p}
        save_data(self.data); messagebox.showinfo("OK","Faculty added")

    def handle_login(self):
        role=self.role.get(); u=self.u.get().strip(); p=self.p.get().strip()
        if role=="faculty":
            f=self.data["faculties"].get(u)
            if not f or f["password"]!=p: return messagebox.showerror("Fail","Invalid creds")
            self.faculty_home(u)
        else:
            s=self.data["students"].get(u)
            if not s or s["password"]!=p: return messagebox.showerror("Fail","Invalid creds")
            if s.get("first_login",True):
                np=simpledialog.askstring("First login","Set new password:",parent=self,show="*")
                s["password"]=np; s["first_login"]=False; save_data(self.data)
                messagebox.showinfo("OK","Password changed")
            self.student_home(u)

    def faculty_home(self,u):
        for w in self.winfo_children(): w.destroy()
        ttk.Label(self,text=f"Welcome {self.data['faculties'][u]['name']}").pack(pady=10)
        ttk.Button(self,text="Register Student",command=self.register_student).pack(pady=5)
        ttk.Button(self,text="Logout",command=self.login_screen).pack()

    def register_student(self):
        roll=simpledialog.askstring("Roll","Roll number:",parent=self)
        name=simpledialog.askstring("Name","Student name:",parent=self)
        sid=gen_id(roll); pwd=gen_pwd()
        self.data["students"][sid]={"name":name,"password":pwd,"first_login":True}
        save_data(self.data)
        messagebox.showinfo("Student","Created:\nID:"+sid+"\nPwd:"+pwd)

    def student_home(self,u):
        for w in self.winfo_children(): w.destroy()
        ttk.Label(self,text=f"Welcome {self.data['students'][u]['name']}").pack(pady=10)
        ttk.Button(self,text="Logout",command=self.login_screen).pack()

if __name__=="__main__": SMSApp().mainloop()
