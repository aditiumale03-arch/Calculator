import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import math
import ast
import operator as op
from datetime import datetime

# ============================================================
# ADVANCE CALCULATOR
# Created by Aditi Umale
# For Next Hikes IT Solution
# Python standard library only
# ============================================================

APP_NAME = "Advance Calculator"
VERSION = "v2.0"

DARK = {
    "bg": "#0F172A", "panel": "#172554", "panel2": "#1E293B",
    "button": "#243B63", "accent": "#14B8A6", "accent2": "#0D9488",
    "equal": "#F59E0B", "text": "#FFFFFF", "muted": "#CBD5E1",
    "entry": "#0B1220", "border": "#334155",
}
LIGHT = {
    "bg": "#C8D8E9", "panel": "#FFFFFF", "panel2": "#E2E8F0",
    "button": "#FFFFFF", "accent": "#0D9488", "accent2": "#0F766E",
    "equal": "#0D9488", "text": "#0F172A", "muted": "#475569",
    "entry": "#FFFFFF", "border": "#CBD5E1",
}

BIN_OPS = {
    ast.Add: op.add, ast.Sub: op.sub, ast.Mult: op.mul,
    ast.Div: op.truediv, ast.Pow: op.pow, ast.Mod: op.mod,
    ast.FloorDiv: op.floordiv,
}
UNARY_OPS = {ast.UAdd: op.pos, ast.USub: op.neg}


def safe_eval(expr):
    """Evaluate calculator expressions safely; trigonometry uses degrees."""
    expr = (expr.replace("×", "*").replace("÷", "/")
                 .replace("−", "-").replace("^", "**").replace("π", "pi"))
    allowed = {
        "sin": lambda x: math.sin(math.radians(x)),
        "cos": lambda x: math.cos(math.radians(x)),
        "tan": lambda x: math.tan(math.radians(x)),
        "asin": lambda x: math.degrees(math.asin(x)),
        "acos": lambda x: math.degrees(math.acos(x)),
        "atan": lambda x: math.degrees(math.atan(x)),
        "sqrt": math.sqrt, "log": math.log10, "ln": math.log,
        "abs": abs, "exp": math.exp, "floor": math.floor,
        "ceil": math.ceil, "factorial": math.factorial,
        "pi": math.pi, "e": math.e,
    }
    bin_ops = {ast.Add: op.add, ast.Sub: op.sub, ast.Mult: op.mul,
               ast.Div: op.truediv, ast.Pow: op.pow, ast.Mod: op.mod,
               ast.FloorDiv: op.floordiv}
    unary_ops = {ast.UAdd: op.pos, ast.USub: op.neg}
    def walk(node):
        if isinstance(node, ast.Expression): return walk(node.body)
        if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)): return node.value
        if isinstance(node, ast.Name) and node.id in allowed: return allowed[node.id]
        if isinstance(node, ast.BinOp) and type(node.op) in bin_ops:
            return bin_ops[type(node.op)](walk(node.left), walk(node.right))
        if isinstance(node, ast.UnaryOp) and type(node.op) in unary_ops:
            return unary_ops[type(node.op)](walk(node.operand))
        if isinstance(node, ast.Call):
            fn = walk(node.func)
            return fn(*(walk(a) for a in node.args))
        raise ValueError("Unsupported expression")
    return walk(ast.parse(expr, mode="eval"))


class AdvanceCalculator(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(f"{APP_NAME} {VERSION}")
        self.geometry("460x780")
        self.minsize(400, 680)
        self.current_theme = "dark"
        self.colors = DARK
        self.history = []
        self.current_page = "Standard"
        self.sidebar_open = False

        self.content = tk.Frame(self)
        self.content.pack(fill="both", expand=True)

        self.sidebar = tk.Frame(self, bd=1, relief="solid")
        self.apply_theme()
        self.show_standard()

    # ---------- Theme / layout ----------
    def apply_theme(self):
        self.colors = DARK if self.current_theme == "dark" else LIGHT
        c = self.colors
        self.configure(bg=c["bg"])
        self.content.configure(bg=c["bg"])
        self.sidebar.configure(bg=c["panel"])

    def toggle_theme(self):
        self.current_theme = "light" if self.current_theme == "dark" else "dark"
        self.close_sidebar()
        self.apply_theme()
        self.show_page(self.current_page)

    def clear_content(self):
        for w in self.content.winfo_children():
            w.destroy()

    def label(self, parent, text, size=12, bold=False, color=None, **kwargs):
        c = self.colors
        return tk.Label(
            parent, text=text,
            font=("Segoe UI", size, "bold" if bold else "normal"),
            bg=kwargs.pop("bg", c["bg"]), fg=color or c["text"], **kwargs
        )

    def entry(self, parent, **kwargs):
        c = self.colors
        return tk.Entry(
            parent, font=("Segoe UI", 12), bg=c["entry"], fg=c["text"],
            insertbackground=c["text"], relief="flat", highlightthickness=1,
            highlightbackground=c["border"], **kwargs
        )

    def button(self, parent, text, command, kind="normal", width=10, height=2):
        c = self.colors
        bg = c["equal"] if kind == "equal" else c["accent"] if kind == "accent" else c["button"]
        fg = "#FFFFFF" if kind in ("equal", "accent") else c["text"]
        return tk.Button(
            parent, text=text, command=command,
            font=("Segoe UI", 15, "bold" if kind in ("equal", "accent") else "normal"),
            bg=bg, fg=fg, activebackground=c["accent2"],
            activeforeground="#FFFFFF", relief="flat", bd=0,
            width=width, height=height, cursor="hand2"
        )

    def title_bar(self, title, subtitle=""):
        c = self.colors
        frame = tk.Frame(self.content, bg=c["bg"])
        frame.pack(fill="x", padx=14, pady=(10, 8))
        tk.Button(
            frame, text="☰", command=self.toggle_sidebar,
            font=("Segoe UI Symbol", 18, "bold"), bg=c["bg"], fg=c["text"],
            activebackground=c["panel2"], activeforeground=c["text"],
            relief="flat", bd=0, cursor="hand2", padx=5
        ).grid(row=0, column=0, rowspan=2, padx=(0, 8))
        self.label(frame, title, 19, True).grid(row=0, column=1, sticky="w")
        if subtitle:
            self.label(frame, subtitle, 9, color=c["muted"]).grid(
                row=1, column=1, sticky="w", pady=(2, 0)
            )

    # ---------- Three-line menu ----------
    def toggle_sidebar(self):
        if self.sidebar_open:
            self.close_sidebar()
        else:
            self.refresh_sidebar()
            self.sidebar_open = True
            self.sidebar.lift()
            self.sidebar.place(x=0, y=0, relheight=1, width=235)

    def close_sidebar(self):
        self.sidebar_open = False
        self.sidebar.place_forget()
        self.content.lift()

    def nav(self, command):
        """Run a menu option and automatically hide the menu."""
        self.close_sidebar()
        command()

    def refresh_sidebar(self):
        for w in self.sidebar.winfo_children():
            w.destroy()
        c = self.colors
        self.sidebar.configure(bg=c["panel"])

        top = tk.Frame(self.sidebar, bg=c["panel"])
        top.pack(fill="x", padx=12, pady=(12, 10))
        tk.Button(
            top, text="☰", command=self.close_sidebar,
            font=("Segoe UI Symbol", 20, "bold"), bg=c["panel"], fg=c["text"],
            activebackground=c["panel2"], activeforeground=c["text"],
            relief="flat", bd=0, cursor="hand2"
        ).pack(side="left")
        self.label(top, "Advance Calculator", 13, True, bg=c["panel"]).pack(side="left", padx=7)

        groups = [
            ("CALCULATOR", [
                ("▣", "Standard", self.show_standard),
                ("⚗", "Scientific", self.show_scientific),
                ("◷", "History", self.show_history),
            ]),
            ("MATHEMATICS", [
                ("∑", "Algebra", self.show_algebra),
                ("↔", "Linear equations", self.show_linear),
                ("△", "Trigonometry", self.show_trigonometry),
            ]),
            ("FINANCE & HEALTH", [
                ("₹", "Financial analysis", self.show_finance),
                ("♥", "BMI", self.show_bmi),
                ("↔", "Converters", self.show_converter),
            ]),
            ("OTHER", [
                ("?", "Help", self.show_help),
                ("ⓘ", "About", self.show_about),
            ]),
        ]
        for heading, items in groups:
            self.label(self.sidebar, heading, 9, True, color=c["muted"], bg=c["panel"]).pack(
                anchor="w", padx=22, pady=(8, 3)
            )
            for icon, name, command in items:
                self.add_nav(icon, name, command)

        self.label(self.sidebar, f"{VERSION}", 9, color=c["muted"], bg=c["panel"]).pack(
            anchor="w", padx=22, pady=(8, 12)
        )

    def add_nav(self, icon, text, command):
        c = self.colors
        tk.Button(
            self.sidebar, text=f"{icon}   {text}",
            command=lambda cmd=command: self.nav(cmd),
            font=("Segoe UI", 10), bg=c["panel"], fg=c["text"],
            activebackground=c["panel2"], activeforeground=c["text"],
            relief="flat", bd=0, anchor="w", padx=14, pady=7, cursor="hand2"
        ).pack(fill="x", padx=7, pady=1)

    def show_page(self, page):
        pages = {
            "Standard": self.show_standard,
            "Scientific": self.show_scientific,
            "Algebra": self.show_algebra,
            "Linear equations": self.show_linear,
            "Trigonometry": self.show_trigonometry,
            "Financial analysis": self.show_finance,
            "BMI": self.show_bmi,
            "Converters": self.show_converter,
            "Help": self.show_help,
            "About": self.show_about,
        }
        pages.get(page, self.show_standard)()

    # ---------- Standard calculator ----------
    def show_standard(self):
        self.close_sidebar()
        self.current_page = "Standard"
        self.clear_content()
        c = self.colors
        self.title_bar("Calculator", "Everyday arithmetic")

        top = tk.Frame(self.content, bg=c["panel"], padx=14, pady=14)
        top.pack(fill="x", padx=14, pady=(4, 10))
        self.std_expr = tk.StringVar()
        display = tk.Entry(
            top, textvariable=self.std_expr, justify="right",
            font=("Segoe UI", 28), bg=c["entry"], fg=c["text"],
            insertbackground=c["text"], relief="flat", bd=0
        )
        display.pack(fill="x", ipady=17)
        display.focus_set()

        grid = tk.Frame(self.content, bg=c["bg"])
        grid.pack(fill="both", expand=True, padx=14, pady=(0, 12))
        rows = [
            ["C", "⌫", "%", "÷"],
            ["7", "8", "9", "×"],
            ["4", "5", "6", "−"],
            ["1", "2", "3", "+"],
            ["±", "0", ".", "="],
        ]
        for r, row in enumerate(rows):
            for col, key in enumerate(row):
                kind = "equal" if key == "=" else "accent" if key in ("÷", "×", "−", "+", "%") else "normal"
                self.button(grid, key, lambda x=key: self.std_press(x), kind, 1, 2).grid(
                    row=r, column=col, padx=5, pady=5, sticky="nsew"
                )
        for i in range(4):
            grid.grid_columnconfigure(i, weight=1, uniform="calc")
        for i in range(5):
            grid.grid_rowconfigure(i, weight=1, uniform="calc")
        self.bind_all("<Key>", self.keyboard)

    def keyboard(self, event):
        if self.current_page != "Standard":
            return
        if event.char in "0123456789.+-*/%()":
            self.std_press(event.char)
        elif event.keysym in ("Return", "KP_Enter"):
            self.std_press("=")
        elif event.keysym == "BackSpace":
            self.std_press("⌫")
        elif event.keysym == "Escape":
            self.std_press("C")

    def std_press(self, x):
        s = self.std_expr.get()
        if x == "C":
            self.std_expr.set("")
        elif x == "⌫":
            self.std_expr.set(s[:-1])
        elif x == "=":
            self.calculate_standard()
        elif x == "±" and s:
            self.std_expr.set(f"-({s})")
        elif x == "÷":
            self.std_expr.set(s + "/")
        elif x == "×":
            self.std_expr.set(s + "*")
        elif x == "−":
            self.std_expr.set(s + "-")
        else:
            self.std_expr.set(s + x)

    def calculate_standard(self):
        expr = self.std_expr.get()
        if not expr:
            return
        try:
            result = safe_eval(expr)
            result_text = self.format_result(result)
            self.std_expr.set(result_text)
            self.history.append((datetime.now().strftime("%d-%m-%Y %I:%M %p"), expr, result_text))
            if self.current_page == "History": self.refresh_history_list()
        except Exception:
            messagebox.showerror("Error", "Invalid calculation.")

    @staticmethod
    def format_result(x):
        if isinstance(x, float) and x.is_integer():
            return str(int(x))
        return f"{x:.12g}"

    # ---------- Scientific ----------
    def show_scientific(self):
        self.current_page = "Scientific"
        self.close_sidebar()
        self.clear_content()
        c = self.colors
        self.title_bar("Scientific Calculator", "Trigonometry uses degrees by default")

        top = tk.Frame(self.content, bg=c["panel"], padx=12, pady=10)
        top.pack(fill="x", padx=14, pady=(4, 8))
        self.sci_expr = tk.StringVar()
        display = tk.Entry(top, textvariable=self.sci_expr, justify="right",
                           font=("Segoe UI", 24), bg=c["entry"], fg=c["text"],
                           insertbackground=c["text"], relief="flat", bd=0)
        display.pack(fill="x", ipady=13)
        display.focus_set()

        grid = tk.Frame(self.content, bg=c["bg"])
        grid.pack(fill="both", expand=True, padx=14, pady=5)
        rows = [
            ["C","⌫","(",")"],
            ["sin","cos","tan","√"],
            ["asin","acos","atan","x²"],
            ["log","ln","π","e"],
            ["7","8","9","÷"],
            ["4","5","6","×"],
            ["1","2","3","−"],
            ["0",".","±","+"],
            ["^","%","!","="],
        ]
        for r, row in enumerate(rows):
            for col, key in enumerate(row):
                kind = "equal" if key == "=" else (
                    "accent" if key in {"sin","cos","tan","asin","acos","atan",
                                        "√","x²","log","ln","π","e","^","%","!"}
                    else "normal")
                self.button(grid, key, lambda k=key: self.sci_press(k),
                            kind, 1).grid(row=r, column=col, padx=4, pady=4, sticky="nsew")
        for col in range(4):
            grid.grid_columnconfigure(col, weight=1, uniform="sci")
        for row in range(len(rows)):
            grid.grid_rowconfigure(row, weight=1, uniform="sci")

    def sci_press(self, key):
        s = self.sci_expr.get().strip()

        if key == "C":
            self.sci_expr.set("")
            return

        if key == "⌫":
            self.sci_expr.set(self.sci_expr.get()[:-1])
            return

        # Scientific function buttons calculate the current expression
        # immediately. This prevents unfinished expressions such as sin(55.
        function_keys = {
            "sin", "cos", "tan", "asin", "acos", "atan",
            "log", "ln", "√", "x²", "!"
        }

        if key in function_keys:
            if not s:
                openings = {
                    "√": "sqrt(",
                    "sin": "sin(",
                    "cos": "cos(",
                    "tan": "tan(",
                    "asin": "asin(",
                    "acos": "acos(",
                    "atan": "atan(",
                    "log": "log(",
                    "ln": "ln("
                }
                self.sci_expr.set(openings.get(key, ""))
                return

            try:
                if key == "√":
                    expression = f"sqrt({s})"
                elif key == "x²":
                    expression = f"({s})**2"
                elif key == "!":
                    expression = f"factorial({s})"
                else:
                    expression = f"{key}({s})"

                result = safe_eval(expression)
                text = self.format_result(result)
                self.sci_expr.set(text)
                self.history.append((
                    datetime.now().strftime("%d-%m-%Y %I:%M %p"),
                    expression, text
                ))
                if self.current_page == "History":
                    self.refresh_history_list()
            except Exception:
                messagebox.showerror(
                    "Scientific Calculator",
                    f"Cannot calculate {key}({s})."
                )
            return

        if key == "=":
            try:
                if not s:
                    return
                result = safe_eval(s)
                text = self.format_result(result)
                self.sci_expr.set(text)
                self.history.append((
                    datetime.now().strftime("%d-%m-%Y %I:%M %p"),
                    s, text
                ))
                if self.current_page == "History":
                    self.refresh_history_list()
            except Exception:
                messagebox.showerror(
                    "Scientific Calculator",
                    "Invalid calculation."
                )
            return

        if key == "π":
            self.sci_expr.set(self.sci_expr.get() + "pi")
        elif key == "e":
            self.sci_expr.set(self.sci_expr.get() + "e")
        elif key == "±":
            if s:
                self.sci_expr.set(f"-({s})")
        elif key == "÷":
            self.sci_expr.set(self.sci_expr.get() + "/")
        elif key == "×":
            self.sci_expr.set(self.sci_expr.get() + "*")
        elif key == "−":
            self.sci_expr.set(self.sci_expr.get() + "-")
        else:
            self.sci_expr.set(self.sci_expr.get() + key)

    # ---------- History ----------
    def show_history(self):
        self.close_sidebar()
        self.current_page = "History"
        self.clear_content()
        c = self.colors
        self.title_bar("History", "Your previous calculations")

        outer = tk.Frame(self.content, bg=c["bg"])
        outer.pack(fill="both", expand=True, padx=14, pady=(2, 12))

        list_frame = tk.Frame(outer, bg=c["panel"], padx=8, pady=8)
        list_frame.pack(fill="both", expand=True)

        scrollbar = tk.Scrollbar(list_frame)
        scrollbar.pack(side="right", fill="y")

        self.history_list = tk.Listbox(
            list_frame, font=("Consolas", 11),
            bg=c["entry"], fg=c["text"],
            selectbackground=c["accent"], selectforeground="#FFFFFF",
            activestyle="none", relief="flat", bd=0,
            yscrollcommand=scrollbar.set
        )
        self.history_list.pack(fill="both", expand=True)
        scrollbar.config(command=self.history_list.yview)

        self.refresh_history_list()

        buttons = tk.Frame(outer, bg=c["bg"])
        buttons.pack(fill="x", pady=(8, 0))
        self.button(
            buttons, "Clear History", self.clear_history, "accent", 14, 1
        ).pack(side="left", fill="x", expand=True, padx=(0, 4))
        self.button(
            buttons, "Export History", self.export_history, "normal", 14, 1
        ).pack(side="left", fill="x", expand=True, padx=(4, 0))

    def refresh_history_list(self):
        if not hasattr(self, "history_list"):
            return
        self.history_list.delete(0, tk.END)
        if not self.history:
            self.history_list.insert(tk.END, "No calculations yet.")
            return
        for stamp, expression, result in reversed(self.history):
            self.history_list.insert(
                tk.END, f"{expression} = {result}    [{stamp}]"
            )

    def clear_history(self):
        if self.history and messagebox.askyesno(
            "Clear History", "Delete all calculation history?"
        ):
            self.history.clear()
            self.refresh_history_list()

    def export_history(self):
        if not self.history:
            messagebox.showinfo("Export History", "There is no history to export.")
            return
        path = filedialog.asksaveasfilename(
            title="Export Calculation History",
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        if not path:
            return
        try:
            with open(path, "w", encoding="utf-8") as f:
                f.write("Advance Calculator - Calculation History\n")
                f.write("=" * 60 + "\n\n")
                for stamp, expression, result in reversed(self.history):
                    f.write(f"{expression} = {result}\nTime: {stamp}\n\n")
            messagebox.showinfo("Export History", "History exported successfully.")
        except Exception as exc:
            messagebox.showerror("Export History", f"Could not export history:\n{exc}")

    # ---------- Algebra ----------
    def show_algebra(self):
        self.current_page = "Algebra"
        self.close_sidebar()
        self.clear_content()
        c = self.colors
        self.title_bar("Algebra", "Solve linear and quadratic equations")

        box = tk.Frame(self.content, bg=c["panel"], padx=18, pady=14)
        box.pack(fill="x", padx=20, pady=8)
        self.label(box, "Linear equation: ax + b = c", 14, True, bg=c["panel"]).pack(anchor="w")
        row = tk.Frame(box, bg=c["panel"]); row.pack(fill="x", pady=8)
        lin = {}
        for name in ("a","b","c"):
            self.label(row, name, 11, True, bg=c["panel"]).pack(side="left", padx=(2,2))
            e = self.entry(row, width=9); e.pack(side="left", padx=(2,8)); lin[name] = e
        lr = self.label(box, "", 12, True, color=c["accent"], bg=c["panel"])
        lr.pack(anchor="w", pady=5)
        self.button(box, "Solve Linear", lambda: self.solve_linear_one(lin, lr), "accent", 16).pack(anchor="w")

        box2 = tk.Frame(self.content, bg=c["panel"], padx=18, pady=14)
        box2.pack(fill="x", padx=20, pady=8)
        self.label(box2, "Quadratic equation: ax² + bx + c = 0", 14, True, bg=c["panel"]).pack(anchor="w")
        row2 = tk.Frame(box2, bg=c["panel"]); row2.pack(fill="x", pady=8)
        quad = {}
        for name in ("a","b","c"):
            self.label(row2, name, 11, True, bg=c["panel"]).pack(side="left", padx=(2,2))
            e = self.entry(row2, width=9); e.pack(side="left", padx=(2,8)); quad[name] = e
        qr = self.label(box2, "", 12, True, color=c["accent"], bg=c["panel"])
        qr.pack(anchor="w", pady=5)
        self.button(box2, "Solve Quadratic", lambda: self.solve_quadratic(quad, qr), "accent", 16).pack(anchor="w")

    def _number(self, e):
        value = e.get().strip()
        if not value:
            raise ValueError("Please enter all coefficients.")
        return float(value)

    def solve_linear_one(self, es, out):
        try:
            a, b, c = self._number(es["a"]), self._number(es["b"]), self._number(es["c"])
            if math.isclose(a, 0.0):
                out.config(text="a cannot be 0 for a unique solution.")
                return
            out.config(text=f"x = {self.format_result((c - b) / a)}")
        except Exception as exc:
            out.config(text=f"Error: {exc}")

    def solve_quadratic(self, es, out):
        try:
            a, b, c = self._number(es["a"]), self._number(es["b"]), self._number(es["c"])
            if math.isclose(a, 0.0):
                out.config(text="a cannot be 0. Use the Linear solver.")
                return
            d = b*b - 4*a*c
            if d > 1e-12:
                root = math.sqrt(d)
                x1 = (-b + root) / (2*a)
                x2 = (-b - root) / (2*a)
                out.config(text=f"x₁ = {self.format_result(x1)}    x₂ = {self.format_result(x2)}")
            elif math.isclose(d, 0.0, abs_tol=1e-12):
                out.config(text=f"x = {self.format_result(-b / (2*a))}")
            else:
                real = -b / (2*a)
                imag = math.sqrt(-d) / abs(2*a)
                out.config(text=f"x₁ = {real:.8g} + {imag:.8g}i    x₂ = {real:.8g} - {imag:.8g}i")
        except Exception as exc:
            out.config(text=f"Error: {exc}")

    # ---------- Linear equations ----------
    def show_linear(self):
        self.close_sidebar()
        self.current_page = "Linear equations"
        self.clear_content()
        c = self.colors
        self.title_bar("Linear equations", "Solve two equations in x and y")
        rows, sets = [], []
        for idx in (1, 2):
            self.label(self.content, f"Equation {idx}: a{idx}x + b{idx}y = c{idx}", 12, True).pack(anchor="w", padx=28, pady=(8,0))
            row = tk.Frame(self.content, bg=c["bg"]); row.pack(padx=28, pady=5)
            es = []
            for name in (f"a{idx}", f"b{idx}", f"c{idx}"):
                self.label(row, name, 10, True).pack(side="left", padx=(4,2))
                e=self.entry(row,width=8); e.pack(side="left",padx=4); es.append(e)
            sets.append(es)
        out=self.label(self.content,"",14,True,color=c["accent"]); out.pack(anchor="w",padx=28,pady=12)
        self.button(self.content,"Solve",lambda:self.solve_two_linear(sets[0],sets[1],out),"accent",16).pack(anchor="w",padx=28)

    def solve_two_linear(self,e1,e2,out):
        try:
            a1,b1,c1=map(lambda e:float(e.get()),e1); a2,b2,c2=map(lambda e:float(e.get()),e2)
            d=a1*b2-a2*b1
            if d == 0:
                out.config(text="No unique solution (parallel or identical equations)."); return
            x=(c1*b2-c2*b1)/d; y=(a1*c2-a2*c1)/d
            out.config(text=f"x = {x:g}    y = {y:g}")
        except Exception as e: out.config(text=f"Error: {e}")

    # ---------- Trigonometry: degrees only, no DEG/RAD control ----------
    def show_trigonometry(self):
        self.close_sidebar()
        self.current_page = "Trigonometry"
        self.clear_content()
        c=self.colors
        self.title_bar("Trigonometry","Angle is interpreted in degrees")
        row=tk.Frame(self.content,bg=c["bg"]); row.pack(padx=28,pady=20)
        self.label(row,"Angle (degrees)",12,True).pack(side="left",padx=5)
        angle=self.entry(row,width=16); angle.pack(side="left",padx=8)
        out=self.label(self.content,"",14,True,color=c["accent"],wraplength=420,justify="left")
        out.pack(anchor="w",padx=28,pady=15)
        def calc():
            try:
                x=math.radians(float(angle.get()))
                vals={"sin":math.sin(x),"cos":math.cos(x),"tan":math.tan(x)}
                vals["cot"]=1/vals["tan"] if abs(vals["tan"]) > 1e-14 else float("inf")
                vals["sec"]=1/vals["cos"] if abs(vals["cos"]) > 1e-14 else float("inf")
                vals["cosec"]=1/vals["sin"] if abs(vals["sin"]) > 1e-14 else float("inf")
                out.config(text="   ".join(f"{k} = {v:.8g}" for k,v in vals.items()))
            except Exception as e: out.config(text=f"Error: {e}")
        self.button(self.content,"Calculate",calc,"accent",16).pack(anchor="w",padx=28)

    # ---------- Financial analysis ----------
    def show_finance(self):
        self.close_sidebar()
        self.current_page="Financial analysis"
        self.clear_content()
        c=self.colors
        self.title_bar("Financial analysis","Interest, EMI, SIP, GST and profit/loss")
        notebook=ttk.Notebook(self.content); notebook.pack(fill="both",expand=True,padx=20,pady=10)
        for name, builder in [
            ("Simple Interest",self.finance_simple_interest),
            ("Compound Interest",self.finance_compound),
            ("EMI",self.finance_emi),
            ("SIP",self.finance_sip),
            ("GST",self.finance_gst),
            ("Profit / Loss",self.finance_pl),
        ]:
            f=tk.Frame(notebook,bg=c["bg"]); notebook.add(f,text=name); builder(f)

    def finance_form(self,parent,fields,calc):
        c=self.colors; es={}
        for i,(key,label_text) in enumerate(fields):
            self.label(parent,label_text,11,True,bg=c["bg"]).grid(row=i,column=0,padx=15,pady=7,sticky="w")
            e=self.entry(parent,width=19); e.grid(row=i,column=1,padx=8,pady=7); es[key]=e
        out=self.label(parent,"",12,True,color=c["accent"],bg=c["bg"],wraplength=390,justify="left")
        out.grid(row=len(fields),column=0,columnspan=2,padx=15,pady=10,sticky="w")
        self.button(parent,"Calculate",lambda:calc(es,out),"accent",14,1).grid(row=len(fields)+1,column=0,columnspan=2,pady=8)
        return es,out

    def finance_simple_interest(self,p):
        def calc(e,o):
            P=float(e["p"].get()); r=float(e["r"].get()); t=float(e["t"].get())
            interest=P*r*t/100; o.config(text=f"Simple Interest = {interest:.2f}\nAmount = {P+interest:.2f}")
        self.finance_form(p,[("p","Principal"),("r","Rate % per year"),("t","Time (years)")],calc)

    def finance_compound(self,p):
        def calc(e,o):
            P=float(e["p"].get()); r=float(e["r"].get())/100; t=float(e["t"].get()); n=float(e["n"].get())
            if n <= 0: raise ValueError("Compounds/year must be positive")
            A=P*(1+r/n)**(n*t); o.config(text=f"Amount = {A:.2f}\nInterest = {A-P:.2f}")
        self.finance_form(p,[("p","Principal"),("r","Rate %"),("t","Years"),("n","Compounds/year")],self.wrap_finance(calc))

    def wrap_finance(self, fn):
        def wrapped(e,o):
            try: fn(e,o)
            except Exception: o.config(text="Enter valid values.")
        return wrapped

    def finance_emi(self,p):
        def calc(e,o):
            P=float(e["p"].get()); annual=float(e["r"].get()); months=float(e["m"].get())
            r=annual/12/100
            if months <= 0: raise ValueError
            emi=P/months if r==0 else P*r*(1+r)**months/((1+r)**months-1)
            o.config(text=f"Monthly EMI = {emi:.2f}\nTotal Payment = {emi*months:.2f}")
        self.finance_form(p,[("p","Loan Amount"),("r","Annual Rate %"),("m","Months")],self.wrap_finance(calc))

    def finance_sip(self,p):
        def calc(e,o):
            P=float(e["p"].get()); annual=float(e["r"].get())/100; years=float(e["y"].get())
            n=years*12; rm=annual/12
            if n <= 0: raise ValueError
            fv=P*n if rm==0 else P*((1+rm)**n-1)/rm*(1+rm)
            invested=P*n; o.config(text=f"Invested = {invested:.2f}\nFuture Value = {fv:.2f}\nGain = {fv-invested:.2f}")
        self.finance_form(p,[("p","Monthly SIP"),("r","Annual Return %"),("y","Years")],self.wrap_finance(calc))

    def finance_gst(self,p):
        def calc(e,o):
            amount=float(e["a"].get()); rate=float(e["r"].get()); gst=amount*rate/100
            o.config(text=f"GST = {gst:.2f}\nTotal = {amount+gst:.2f}")
        self.finance_form(p,[("a","Amount"),("r","GST %")],self.wrap_finance(calc))

    def finance_pl(self,p):
        def calc(e,o):
            cost=float(e["c"].get()); sell=float(e["s"].get())
            if cost == 0: raise ValueError
            diff=sell-cost
            if diff>=0: o.config(text=f"Profit = {diff:.2f}\nProfit % = {diff/cost*100:.2f}%")
            else: o.config(text=f"Loss = {-diff:.2f}\nLoss % = {-diff/cost*100:.2f}%")
        self.finance_form(p,[("c","Cost Price"),("s","Selling Price")],self.wrap_finance(calc))

    # ---------- BMI ----------
    def show_bmi(self):
        self.close_sidebar()
        self.current_page="BMI"
        self.clear_content()
        c=self.colors
        self.title_bar("BMI Calculator","Calculate Body Mass Index")
        row=tk.Frame(self.content,bg=c["bg"]); row.pack(padx=28,pady=20)
        self.label(row,"Weight (kg)",12,True).grid(row=0,column=0,padx=5,pady=8)
        w=self.entry(row,width=15); w.grid(row=0,column=1,padx=10)
        self.label(row,"Height (cm)",12,True).grid(row=1,column=0,padx=5,pady=8)
        h=self.entry(row,width=15); h.grid(row=1,column=1,padx=10)
        out=self.label(self.content,"",15,True,color=c["accent"]); out.pack(padx=28,pady=20)
        def calc():
            try:
                kg=float(w.get()); m=float(h.get())/100
                if kg <= 0 or m <= 0: raise ValueError
                bmi=kg/(m*m)
                cat="Underweight" if bmi<18.5 else "Normal weight" if bmi<25 else "Overweight" if bmi<30 else "Obesity"
                out.config(text=f"BMI = {bmi:.2f}\nCategory: {cat}")
            except Exception: out.config(text="Enter valid height and weight.")
        self.button(self.content,"Calculate BMI",calc,"accent",18).pack(anchor="w",padx=28)

    # ---------- Converters ----------
    def show_converter(self):
        self.close_sidebar()
        self.current_page="Converters"; self.clear_content(); c=self.colors
        self.title_bar("Converters","Length, temperature, weight, area, speed and volume")
        kind=tk.StringVar(value="Length")
        ttk.Combobox(self.content,textvariable=kind,values=["Length","Temperature","Weight","Speed","Area","Volume"],state="readonly",width=20).pack(anchor="w",padx=28,pady=10)
        row=tk.Frame(self.content,bg=c["bg"]); row.pack(padx=28,pady=10)
        self.label(row,"Value",11,True).grid(row=0,column=0,padx=5); frm=self.entry(row,width=14); frm.grid(row=0,column=1,padx=5)
        self.label(row,"From",11,True).grid(row=1,column=0,padx=5,pady=10)
        fu=tk.StringVar(); fcb=ttk.Combobox(row,textvariable=fu,width=12,state="readonly"); fcb.grid(row=1,column=1,padx=5)
        self.label(row,"To",11,True).grid(row=2,column=0,padx=5,pady=10)
        tu=tk.StringVar(); tcb=ttk.Combobox(row,textvariable=tu,width=12,state="readonly"); tcb.grid(row=2,column=1,padx=5)
        out=self.label(self.content,"",13,True,color=c["accent"]); out.pack(anchor="w",padx=28,pady=10)
        units={
            "Length":["m","km","cm","mm","ft","in","mile"], "Temperature":["C","F","K"],
            "Weight":["kg","g","lb","oz"], "Speed":["m/s","km/h","mph"],
            "Area":["m²","km²","ft²","acre"], "Volume":["L","mL","m³","ft³"],
        }
        def update_units(*_):
            vals=units[kind.get()]; fcb["values"]=vals; tcb["values"]=vals
            fu.set(vals[0]); tu.set(vals[1] if len(vals)>1 else vals[0])
        kind.trace_add("write",update_units); update_units()

        def convert():
            try:
                x=float(frm.get()); cat=kind.get(); a=fu.get(); b=tu.get()
                if cat=="Temperature":
                    base=x if a=="C" else (x-32)*5/9 if a=="F" else x-273.15
                    y=base if b=="C" else base*9/5+32 if b=="F" else base+273.15
                else:
                    factors={
                        "Length":{"m":1,"km":1000,"cm":.01,"mm":.001,"ft":.3048,"in":.0254,"mile":1609.344},
                        "Weight":{"kg":1,"g":.001,"lb":.45359237,"oz":.0283495231},
                        "Speed":{"m/s":1,"km/h":1/3.6,"mph":0.44704},
                        "Area":{"m²":1,"km²":1e6,"ft²":.092903,"acre":4046.8564224},
                        "Volume":{"L":1,"mL":.001,"m³":1000,"ft³":28.3168466},
                    }[cat]
                    y=x*factors[a]/factors[b]
                out.config(text=f"{x:g} {a} = {y:.10g} {b}")
            except Exception as e: out.config(text=f"Error: {e}")
        self.button(self.content,"Convert",convert,"accent",16).pack(anchor="w",padx=28)

    # ---------- Help / About ----------
    def show_help(self):
        self.close_sidebar()
        self.current_page="Help"; self.clear_content(); c=self.colors
        self.title_bar("Help","How to use Professional Calculator")
        text = """STANDARD
• Use the large number/operator buttons or your keyboard.
• Enter = calculate, Backspace = delete, Esc = clear.
• There are no memory buttons.

SCIENTIFIC
• Use sin, cos, tan, logarithms, powers, roots and constants.
• Trigonometry uses degrees; there is no DEG/RAD control.

ALGEBRA
• Linear: ax + b = c.
• Quadratic: ax² + bx + c = 0.

LINEAR EQUATIONS
• Enter coefficients for a₁x+b₁y=c₁ and a₂x+b₂y=c₂.

TRIGONOMETRY
• Enter an angle in degrees and calculate sin, cos, tan, cot, sec and cosec.

FINANCIAL ANALYSIS
• Simple/compound interest, EMI, SIP, GST and profit/loss.

BMI
• Enter weight in kg and height in cm.

CONVERTERS
• Select a category, units, enter a value and press Convert.

MENU
• Click ☰ to open the menu.
• The menu automatically disappears after you select an option.

APPEARANCE
• Use the Light / Dark option in the three-line menu."""
        box=tk.Text(self.content,font=("Segoe UI",11),bg=c["entry"],fg=c["text"],relief="flat",wrap="word")
        box.pack(fill="both",expand=True,padx=28,pady=10); box.insert("1.0",text); box.config(state="disabled")

    def show_about(self):
        self.close_sidebar()
        self.current_page="About"; self.clear_content(); c=self.colors
        self.title_bar("About","Application information")
        box=tk.Frame(self.content,bg=c["panel"],padx=30,pady=30); box.pack(padx=28,pady=20,fill="x")
        self.label(box,"ADVANCE CALCULATOR",21,True,bg=c["panel"]).pack(pady=5)
        self.label(box,VERSION,11,color=c["accent"],bg=c["panel"]).pack(pady=5)
        self.label(box,"Created by Aditi Umale",15,True,bg=c["panel"]).pack(pady=(22,5))
        self.label(box,"For Next Hikes IT Solution",13,color=c["muted"],bg=c["panel"]).pack(pady=5)
        self.label(box,"\nStandard • Scientific • Algebra • Linear equations\n"
                       "Trigonometry • Financial analysis • BMI • Converters\n"
                       "Light / Dark mode • Professional appearance",11,
                   color=c["muted"],bg=c["panel"],wraplength=390,justify="center").pack(pady=18)

    # ---------- Light / Dark is available inside the three-line menu ----------
    # The requested menu stays compact; the theme action is the last item.
    def refresh_sidebar(self):
        for w in self.sidebar.winfo_children():
            w.destroy()
        c = self.colors
        self.sidebar.configure(bg=c["panel"])
        top = tk.Frame(self.sidebar, bg=c["panel"]); top.pack(fill="x", padx=12, pady=(12,10))
        tk.Button(top, text="☰", command=self.close_sidebar,
                  font=("Segoe UI Symbol",20,"bold"), bg=c["panel"], fg=c["text"],
                  activebackground=c["panel2"], activeforeground=c["text"],
                  relief="flat", bd=0, cursor="hand2").pack(side="left")
        self.label(top,"Advance Calculator",13,True,bg=c["panel"]).pack(side="left",padx=7)

        groups = [
            ("CALCULATOR",[("▣","Standard",self.show_standard),("⚗","Scientific",self.show_scientific),("◷","History",self.show_history)]),
            ("MATHEMATICS",[("∑","Algebra",self.show_algebra),("↔","Linear equations",self.show_linear),("△","Trigonometry",self.show_trigonometry)]),
            ("FINANCE & HEALTH",[("₹","Financial analysis",self.show_finance),("♥","BMI",self.show_bmi),("↔","Converters",self.show_converter)]),
            ("OTHER",[("?", "Help", self.show_help),("ⓘ","About",self.show_about)]),
        ]
        for heading,items in groups:
            self.label(self.sidebar,heading,9,True,color=c["muted"],bg=c["panel"]).pack(anchor="w",padx=22,pady=(7,3))
            for icon,name,cmd in items: self.add_nav(icon,name,cmd)
        theme_text = "☀  Light mode" if self.current_theme=="dark" else "☾  Dark mode"
        self.add_nav("◐",theme_text,self.toggle_theme)
        self.label(self.sidebar,VERSION,9,color=c["muted"],bg=c["panel"]).pack(anchor="w",padx=22,pady=(7,10))


if __name__ == "__main__":
    app = AdvanceCalculator()
    app.mainloop()
