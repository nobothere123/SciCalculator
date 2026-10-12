import ast
import math
import operator
import tkinter as tk
from tkinter import ttk, messagebox

APP_TITLE = "Python Calculator"
BG = "#f3f6fb"
PANEL = "#ffffff"
TEXT = "#172033"
MUTED = "#667085"
ACCENT = "#2878f0"
ACCENT_LIGHT = "#e6f0ff"
DANGER_BG = "#ffe7e7"
DANGER = "#c62828"

# Conversion factors are relative to a base unit.
UNITS = {
    "Length": {
        "Millimeter (mm)": 0.001, "Centimeter (cm)": 0.01,
        "Meter (m)": 1.0, "Kilometer (km)": 1000.0,
        "Inch (in)": 0.0254, "Foot (ft)": 0.3048,
        "Yard (yd)": 0.9144, "Mile (mi)": 1609.344,
    },
    "Weight / Mass": {
        "Milligram (mg)": 0.001, "Gram (g)": 1.0,
        "Kilogram (kg)": 1000.0, "Metric tonne (t)": 1_000_000.0,
        "Ounce (oz)": 28.349523125, "Pound (lb)": 453.59237,
    },
    "Time": {
        "Millisecond (ms)": 0.001, "Second (s)": 1.0,
        "Minute (min)": 60.0, "Hour (h)": 3600.0,
        "Day": 86400.0, "Week": 604800.0,
    },
    "Data Storage (decimal)": {
        "Bit (bit)": 0.125, "Byte (B)": 1.0, "Kilobyte (KB)": 1000.0,
        "Megabyte (MB)": 1000.0**2, "Gigabyte (GB)": 1000.0**3,
        "Terabyte (TB)": 1000.0**4,
    },
    "Data Storage (binary)": {
        "Byte (B)": 1.0, "Kibibyte (KiB)": 1024.0,
        "Mebibyte (MiB)": 1024.0**2, "Gibibyte (GiB)": 1024.0**3,
        "Tebibyte (TiB)": 1024.0**4,
    },
    "Area": {
        "Square meter (m²)": 1.0, "Square kilometer (km²)": 1_000_000.0,
        "Square centimeter (cm²)": 0.0001, "Hectare (ha)": 10000.0,
        "Acre": 4046.8564224, "Square foot (ft²)": 0.09290304,
    },
    "Volume": {
        "Milliliter (mL)": 0.001, "Liter (L)": 1.0,
        "Cubic meter (m³)": 1000.0, "US gallon (gal)": 3.785411784,
        "US cup": 0.2365882365, "US fluid ounce (fl oz)": 0.0295735296,
    },
    "Speed": {
        "Meter/second (m/s)": 1.0, "Kilometer/hour (km/h)": 1 / 3.6,
        "Mile/hour (mph)": 0.44704, "Knot (kn)": 0.5144444444,
    },
    "Energy": {
        "Joule (J)": 1.0, "Kilojoule (kJ)": 1000.0,
        "Calorie (cal)": 4.184, "Kilocalorie (kcal)": 4184.0,
        "Watt-hour (Wh)": 3600.0, "Kilowatt-hour (kWh)": 3_600_000.0,
    },
    "Pressure": {
        "Pascal (Pa)": 1.0, "Kilopascal (kPa)": 1000.0,
        "Bar": 100000.0, "Atmosphere (atm)": 101325.0,
        "PSI": 6894.757293, "mmHg": 133.3223874,
    },
    "Power": {
        "Watt (W)": 1.0, "Kilowatt (kW)": 1000.0,
        "Megawatt (MW)": 1_000_000.0, "Mechanical horsepower (hp)": 745.699872,
    },
    "Angle": {
        "Degree (°)": math.pi / 180, "Radian (rad)": 1.0,
        "Gradian (gon)": math.pi / 200,
    },
    # "Fuel Economy": {
    #     "Kilometers/liter (km/L)": 1.0, "Miles/gallon US (mpg US)": 0.425143707,
    #     "Miles/gallon UK (mpg UK)": 0.35400619,
    # },
}

TEMPERATURE_UNITS = ["Celsius (°C)", "Fahrenheit (°F)", "Kelvin (K)"]

FUNCTIONS = {
    "sin": math.sin, "cos": math.cos, "tan": math.tan,
    "asin": math.asin, "acos": math.acos, "atan": math.atan,
    "sqrt": math.sqrt, "log": math.log10, "ln": math.log,
    "abs": abs, "floor": math.floor, "ceil": math.ceil,
    "factorial": math.factorial, "exp": math.exp,
}
CONSTANTS = {"pi": math.pi, "e": math.e, "tau": math.tau}
BIN_OPS = {
    ast.Add: operator.add, ast.Sub: operator.sub, ast.Mult: operator.mul,
    ast.Div: operator.truediv, ast.Pow: operator.pow, ast.Mod: operator.mod,
}
UNARY_OPS = {ast.UAdd: operator.pos, ast.USub: operator.neg}


def safe_calculate(expression, degrees=True):
    """Evaluate arithmetic and a small allowlist of scientific functions safely."""
    expression = expression.replace("×", "*").replace("÷", "/").replace("−", "-")
    expression = expression.replace("^", "**").replace("π", "pi")
    tree = ast.parse(expression, mode="eval")

    def visit(node):
        if isinstance(node, ast.Expression):
            return visit(node.body)
        if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
            return node.value
        if isinstance(node, ast.Name):
            if node.id in CONSTANTS:
                return CONSTANTS[node.id]
            raise ValueError(f"Unknown name: {node.id}")
        if isinstance(node, ast.BinOp) and type(node.op) in BIN_OPS:
            left, right = visit(node.left), visit(node.right)
            if isinstance(node.op, ast.Div) and right == 0:
                raise ZeroDivisionError("Cannot divide by zero")
            result = BIN_OPS[type(node.op)](left, right)
            if isinstance(result, complex):
                raise ValueError("Complex results are not supported")
            if not math.isfinite(float(result)):
                raise ValueError("Result is too large or undefined")
            return result
        if isinstance(node, ast.UnaryOp) and type(node.op) in UNARY_OPS:
            return UNARY_OPS[type(node.op)](visit(node.operand))
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id in FUNCTIONS:
            if len(node.args) != 1 or node.keywords:
                raise ValueError("Use one argument per function")
            name = node.func.id
            value = visit(node.args[0])
            if name in ("sin", "cos", "tan") and degrees:
                value = math.radians(value)
            elif name in ("asin", "acos", "atan") and degrees:
                result = FUNCTIONS[name](value)
                return math.degrees(result)
            if name == "factorial" and (value < 0 or int(value) != value or value > 170):
                raise ValueError("Factorial requires an integer from 0 to 170")
            return FUNCTIONS[name](value)
        raise ValueError("Unsupported expression")

    result = visit(tree)
    if isinstance(result, float) and not math.isfinite(result):
        raise ValueError("Result is undefined")
    return result


def format_number(value):
    if isinstance(value, float):
        if abs(value) < 1e-12:
            value = 0.0
        if value.is_integer() and abs(value) < 1e16:
            return f"{int(value):,}"
        return f"{value:,.12g}"
    return f"{value:,}"


class CalculatorApp:
    def __init__(self, root):
        self.root = root
        self.root.title(APP_TITLE)
        self.root.geometry("1120x760")
        self.root.minsize(820, 620)
        self.root.configure(bg=BG)
        self.expression = tk.StringVar(value="")
        self.result_text = tk.StringVar(value="0")
        self.status_text = tk.StringVar(value="Ready")
        self.degrees = tk.BooleanVar(value=True)
        self.history = []
        self.dark = False
        self.memory = 0.0
        self._build_style()
        self._build_ui()
        self._bind_keys()

    def _build_style(self):
        style = ttk.Style()
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass
        style.configure("TCombobox", padding=8, font=("Segoe UI", 10))
        style.configure("TNotebook", background=BG, borderwidth=0)
        style.configure("TNotebook.Tab", padding=(16, 9), font=("Segoe UI", 10, "bold"))

    def _build_ui(self):
        header = tk.Frame(self.root, bg="#17243a", height=64)
        header.pack(fill="x")
        header.pack_propagate(False)
        tk.Label(header, text="▦  Python Calculator", bg="#17243a", fg="white",
                 font=("Segoe UI", 17, "bold")).pack(side="left", padx=22)
        tk.Button(header, text="☼  Theme", command=self.toggle_theme, bg="#2b3a52",
                  fg="white", activebackground="#3c4c65", activeforeground="white",
                  relief="flat", padx=14, pady=7, cursor="hand2").pack(side="right", padx=18, pady=12)

        body = tk.Frame(self.root, bg=BG)
        body.pack(fill="both", expand=True, padx=18, pady=16)
        self.notebook = ttk.Notebook(body)
        self.notebook.pack(fill="both", expand=True)
        self.calc_tab = tk.Frame(self.notebook, bg=BG)
        self.converter_tab = tk.Frame(self.notebook, bg=BG)
        self.history_tab = tk.Frame(self.notebook, bg=BG)
        self.notebook.add(self.calc_tab, text="  Calculator  ")
        self.notebook.add(self.converter_tab, text="  Unit Conversion  ")
        self.notebook.add(self.history_tab, text="  History  ")
        self._build_calculator_tab()
        self._build_converter_tab()
        self._build_history_tab()

        footer = tk.Frame(self.root, bg=BG)
        footer.pack(fill="x", padx=22, pady=(0, 9))
        tk.Label(footer, textvariable=self.status_text, bg=BG, fg=MUTED,
                 font=("Segoe UI", 9)).pack(side="left")
        tk.Label(footer, text="Enter = calculate   •   Esc = clear   •   ^ = power",
                 bg=BG, fg=MUTED, font=("Segoe UI", 9)).pack(side="right")

    def _build_calculator_tab(self):
        outer = tk.Frame(self.calc_tab, bg=BG)
        outer.pack(fill="both", expand=True, padx=12, pady=12)
        outer.columnconfigure(0, weight=3)
        outer.columnconfigure(1, weight=2)
        outer.rowconfigure(0, weight=1)

        left = tk.Frame(outer, bg=PANEL, highlightbackground="#dce4f0", highlightthickness=1)
        left.grid(row=0, column=0, sticky="nsew", padx=(0, 12))
        right = tk.Frame(outer, bg=PANEL, highlightbackground="#dce4f0", highlightthickness=1)
        right.grid(row=0, column=1, sticky="nsew")

        top = tk.Frame(left, bg=PANEL)
        top.pack(fill="x", padx=18, pady=(15, 4))
        tk.Label(top, text="SCIENTIFIC CALCULATOR", bg=PANEL, fg=MUTED,
                 font=("Segoe UI", 9, "bold")).pack(side="left")
        tk.Checkbutton(top, text="Degrees", variable=self.degrees, bg=PANEL, fg=TEXT,
                       selectcolor=ACCENT_LIGHT, activebackground=PANEL,
                       font=("Segoe UI", 9)).pack(side="right")

        display = tk.Frame(left, bg="#edf3fc", highlightbackground="#dce6f5", highlightthickness=1)
        display.pack(fill="x", padx=18, pady=(8, 12))
        tk.Entry(display, textvariable=self.expression, justify="right", bd=0,
                 bg="#edf3fc", fg=MUTED, insertbackground=TEXT,
                 font=("Consolas", 16), relief="flat").pack(fill="x", padx=14, pady=(14, 2), ipady=4)
        tk.Label(display, textvariable=self.result_text, anchor="e", bg="#edf3fc", fg=TEXT,
                 font=("Segoe UI", 30, "bold")).pack(fill="x", padx=14, pady=(0, 12))

        keys = [
            [("sin", "sin("), ("cos", "cos("), ("tan", "tan("), ("√", "sqrt("), ("x²", "**2")],
            [("asin", "asin("), ("acos", "acos("), ("atan", "atan("), ("log", "log("), ("ln", "ln(")],
            [("(", "("), (")", ")"), ("π", "pi"), ("e", "e"), ("n!", "factorial(")],
            [("7", "7"), ("8", "8"), ("9", "9"), ("÷", "/"), ("⌫", "BACK")],
            [("4", "4"), ("5", "5"), ("6", "6"), ("×", "*"), ("C", "CLEAR")],
            [("1", "1"), ("2", "2"), ("3", "3"), ("−", "-"), ("=", "EQUAL")],
            [("0", "0"), (".", "."), ("%", "%"), ("+", "+"), ("Ans", "ANS")],
        ]
        keypad = tk.Frame(left, bg=PANEL)
        keypad.pack(fill="both", expand=True, padx=18, pady=(0, 15))
        for c in range(5):
            keypad.columnconfigure(c, weight=1, uniform="key")
        for r in range(len(keys)):
            keypad.rowconfigure(r, weight=1, uniform="key")
            for c, (label, value) in enumerate(keys[r]):
                is_action = value in ("CLEAR", "EQUAL", "BACK")
                is_operator = value in ("/", "*", "-", "+", "%", "**2")
                bg = ACCENT if value == "EQUAL" else (DANGER_BG if value == "CLEAR" else
                     (ACCENT_LIGHT if is_operator else "#f3f6fb"))
                fg = "white" if value == "EQUAL" else (DANGER if value == "CLEAR" else
                     (ACCENT if is_operator else TEXT))
                btn = tk.Button(keypad, text=label, command=lambda v=value: self.key_press(v),
                                bg=bg, fg=fg, activebackground=bg, activeforeground=fg,
                                relief="flat", bd=0, font=("Segoe UI", 12, "bold"),
                                cursor="hand2", highlightthickness=0)
                btn.grid(row=r, column=c, sticky="nsew", padx=4, pady=4, ipadx=2, ipady=7)

        tk.Label(right, text="Scientific tools", bg=PANEL, fg=TEXT,
                 font=("Segoe UI", 15, "bold")).pack(anchor="w", padx=18, pady=(18, 4))
        tk.Label(right, text="Use functions from the keypad or type an expression.",
                 bg=PANEL, fg=MUTED, font=("Segoe UI", 10), wraplength=260,
                 justify="left").pack(anchor="w", padx=18, pady=(0, 14))
        examples = [
            ("Trigonometry", "sin(30)   cos(60)   tan(45)"),
            ("Logarithms", "log(100)   ln(e)"),
            ("Powers & roots", "2^8   sqrt(144)   exp(1)"),
            ("Constants", "pi   e   tau"),
            ("Other functions", "abs(-9)   factorial(5)   ceil(2.1)"),
        ]
        for title, sample in examples:
            card = tk.Frame(right, bg="#f7f9fd", highlightbackground="#e5ebf4", highlightthickness=1)
            card.pack(fill="x", padx=16, pady=5)
            tk.Label(card, text=title, bg="#f7f9fd", fg=ACCENT,
                     font=("Segoe UI", 10, "bold")).pack(anchor="w", padx=12, pady=(8, 1))
            tk.Label(card, text=sample, bg="#f7f9fd", fg=TEXT,
                     font=("Consolas", 9), wraplength=270, justify="left").pack(anchor="w", padx=12, pady=(0, 8))
        tk.Button(right, text="Copy result to expression", command=self.use_answer,
                  bg=ACCENT_LIGHT, fg=ACCENT, activebackground=ACCENT_LIGHT,
                  relief="flat", font=("Segoe UI", 10, "bold"), cursor="hand2",
                  pady=10).pack(fill="x", padx=16, pady=(14, 8))
        tk.Button(right, text="Memory: M+   M−   MR   MC", command=self.memory_menu,
                  bg="#f3f6fb", fg=TEXT, activebackground="#f3f6fb", relief="flat",
                  font=("Segoe UI", 10), cursor="hand2", pady=10).pack(fill="x", padx=16)

    def _build_converter_tab(self):
        outer = tk.Frame(self.converter_tab, bg=BG)
        outer.pack(fill="both", expand=True, padx=20, pady=20)
        card = tk.Frame(outer, bg=PANEL, highlightbackground="#dce4f0", highlightthickness=1)
        card.pack(fill="both", expand=True, padx=5, pady=5)
        tk.Label(card, text="Unit Conversion", bg=PANEL, fg=TEXT,
                 font=("Segoe UI", 20, "bold")).pack(anchor="w", padx=24, pady=(22, 4))
        tk.Label(card, text="Convert measurements instantly across common units.",
                 bg=PANEL, fg=MUTED, font=("Segoe UI", 10)).pack(anchor="w", padx=24, pady=(0, 20))

        form = tk.Frame(card, bg=PANEL)
        form.pack(fill="x", padx=24)
        form.columnconfigure(1, weight=1)
        form.columnconfigure(3, weight=1)
        tk.Label(form, text="Category", bg=PANEL, fg=TEXT, font=("Segoe UI", 10, "bold")).grid(row=0, column=0, sticky="w", pady=7)
        self.category = tk.StringVar(value="Length")
        self.category_box = ttk.Combobox(form, textvariable=self.category,
                                         values=list(UNITS) + ["Temperature"], state="readonly", width=24)
        self.category_box.grid(row=0, column=1, columnspan=3, sticky="ew", padx=(12, 0), pady=7)
        self.category_box.bind("<<ComboboxSelected>>", self.update_units)

        tk.Label(form, text="Value", bg=PANEL, fg=TEXT, font=("Segoe UI", 10, "bold")).grid(row=1, column=0, sticky="w", pady=7)
        self.from_value = tk.StringVar(value="10")
        tk.Entry(form, textvariable=self.from_value, font=("Segoe UI", 12), relief="solid",
                 bd=1, highlightthickness=0).grid(row=1, column=1, sticky="ew", padx=(12, 8), pady=7, ipady=8)
        self.from_unit = tk.StringVar()
        self.from_box = ttk.Combobox(form, textvariable=self.from_unit, state="readonly")
        self.from_box.grid(row=1, column=2, columnspan=2, sticky="ew", pady=7)
        tk.Label(form, text="Convert to", bg=PANEL, fg=TEXT, font=("Segoe UI", 10, "bold")).grid(row=2, column=0, sticky="w", pady=7)
        self.to_unit = tk.StringVar()
        self.to_box = ttk.Combobox(form, textvariable=self.to_unit, state="readonly")
        self.to_box.grid(row=2, column=1, columnspan=3, sticky="ew", padx=(12, 0), pady=7)
        self.from_value.trace_add("write", lambda *_: self.convert())
        self.from_unit.trace_add("write", lambda *_: self.convert())
        self.to_unit.trace_add("write", lambda *_: self.convert())

        buttons = tk.Frame(card, bg=PANEL)
        buttons.pack(fill="x", padx=24, pady=(16, 10))
        tk.Button(buttons, text="⇅  Swap units", command=self.swap_units, bg="#eef3fb",
                  fg=TEXT, relief="flat", font=("Segoe UI", 10, "bold"), padx=16, pady=9,
                  cursor="hand2").pack(side="left")
        tk.Button(buttons, text="Convert", command=self.convert, bg=ACCENT, fg="white",
                  activebackground=ACCENT, relief="flat", font=("Segoe UI", 10, "bold"),
                  padx=24, pady=9, cursor="hand2").pack(side="left", padx=10)
        self.conversion_result = tk.StringVar(value="10 km = 10,000 m")
        result_box = tk.Frame(card, bg=ACCENT_LIGHT)
        result_box.pack(fill="x", padx=24, pady=(10, 18))
        tk.Label(result_box, text="RESULT", bg=ACCENT_LIGHT, fg=ACCENT,
                 font=("Segoe UI", 9, "bold")).pack(anchor="w", padx=16, pady=(12, 2))
        tk.Label(result_box, textvariable=self.conversion_result, bg=ACCENT_LIGHT, fg="#1458b8",
                 font=("Segoe UI", 21, "bold"), wraplength=700, justify="left").pack(anchor="w", padx=16, pady=(0, 14))
        tk.Label(card, text="Tip: Data storage includes decimal (KB = 1,000 bytes) and binary (KiB = 1,024 bytes) units.",
                 bg=PANEL, fg=MUTED, font=("Segoe UI", 9), wraplength=760,
                 justify="left").pack(anchor="w", padx=24, pady=(0, 20))
        self.update_units()

    def _build_history_tab(self):
        wrap = tk.Frame(self.history_tab, bg=BG)
        wrap.pack(fill="both", expand=True, padx=18, pady=18)
        top = tk.Frame(wrap, bg=BG)
        top.pack(fill="x", pady=(0, 10))
        tk.Label(top, text="Calculation History", bg=BG, fg=TEXT,
                 font=("Segoe UI", 18, "bold")).pack(side="left")
        tk.Button(top, text="Clear history", command=self.clear_history, bg=DANGER_BG,
                  fg=DANGER, activebackground=DANGER_BG, relief="flat",
                  font=("Segoe UI", 10, "bold"), padx=14, pady=7).pack(side="right")
        frame = tk.Frame(wrap, bg=PANEL, highlightbackground="#dce4f0", highlightthickness=1)
        frame.pack(fill="both", expand=True)
        self.history_list = tk.Listbox(frame, font=("Consolas", 11), bg=PANEL, fg=TEXT,
                                       selectbackground=ACCENT_LIGHT, selectforeground=TEXT,
                                       relief="flat", activestyle="none")
        self.history_list.pack(fill="both", expand=True, padx=10, pady=10)
        self.history_list.bind("<Double-Button-1>", self.reuse_history)

    def _bind_keys(self):
        self.root.bind("<Return>", lambda _e: self.calculate())
        self.root.bind("<KP_Enter>", lambda _e: self.calculate())
        self.root.bind("<Escape>", lambda _e: self.clear())
        self.root.bind("<BackSpace>", lambda _e: self.backspace())
        for key in "0123456789.+-*/()%":
            self.root.bind(key, lambda e: self.append(e.char))

    def key_press(self, value):
        if value == "CLEAR":
            self.clear()
        elif value == "EQUAL":
            self.calculate()
        elif value == "BACK":
            self.backspace()
        elif value == "ANS":
            if self.history:
                self.append(str(self.history[-1][1]))
        elif value == "**2":
            self.append("**2")
        else:
            self.append(value)

    def append(self, value):
        self.expression.set(self.expression.get() + value)
        self.status_text.set("Expression ready")

    def clear(self):
        self.expression.set("")
        self.result_text.set("0")
        self.status_text.set("Cleared")

    def backspace(self):
        self.expression.set(self.expression.get()[:-1])

    def calculate(self):
        expr = self.expression.get().strip()
        if not expr:
            return
        try:
            result = safe_calculate(expr, self.degrees.get())
            formatted = format_number(result)
            self.result_text.set(formatted)
            self.status_text.set("Calculation complete")
            self.history.append((expr, result))
            self.history_list.insert(tk.END, f"{expr}  =  {formatted}")
            self.history_list.yview_moveto(1)
        except ZeroDivisionError:
            messagebox.showerror("Math error", "Cannot divide by zero.")
            self.status_text.set("Calculation error")
        except (ValueError, SyntaxError, TypeError, OverflowError) as exc:
            messagebox.showerror("Invalid expression", str(exc) or "Please check your expression.")
            self.status_text.set("Calculation error")

    def use_answer(self):
        value = self.result_text.get().replace(",", "")
        if value and value != "0":
            self.expression.set(value)

    def memory_menu(self):
        choice = messagebox.askyesnocancel("Calculator memory",
            "Yes: M+ (add current result)\nNo: MR (recall memory)\nCancel: clear memory")
        try:
            current = float(self.result_text.get().replace(",", ""))
        except ValueError:
            current = 0.0
        if choice is True:
            self.memory += current
            self.status_text.set(f"Memory = {format_number(self.memory)}")
        elif choice is False:
            self.expression.set(str(self.memory))
        else:
            self.memory = 0.0
            self.status_text.set("Memory cleared")

    def update_units(self, *_):
        category = self.category.get()
        units = TEMPERATURE_UNITS if category == "Temperature" else list(UNITS.get(category, {}))
        self.from_box.configure(values=units)
        self.to_box.configure(values=units)
        if units:
            if self.from_unit.get() not in units:
                self.from_unit.set(units[0])
            if self.to_unit.get() not in units or self.to_unit.get() == self.from_unit.get():
                self.to_unit.set(units[1] if len(units) > 1 else units[0])
        self.convert()

    def convert(self):
        try:
            value = float(self.from_value.get())
            source = self.from_unit.get()
            target = self.to_unit.get()
            category = self.category.get()
            if not source or not target:
                return
            if category == "Temperature":
                c = value if source.startswith("Celsius") else (
                    (value - 32) * 5 / 9 if source.startswith("Fahrenheit") else value - 273.15
                )
                result = c if target.startswith("Celsius") else (
                    c * 9 / 5 + 32 if target.startswith("Fahrenheit") else c + 273.15
                )
            else:
                units = UNITS[category]
                result = value * units[source] / units[target]
            self.conversion_result.set(f"{format_number(value)} {source}  =  {format_number(result)} {target}")
            self.status_text.set("Conversion complete")
        except (ValueError, KeyError, ZeroDivisionError):
            self.conversion_result.set("Enter a valid number to convert.")

    def swap_units(self):
        a, b = self.from_unit.get(), self.to_unit.get()
        self.from_unit.set(b)
        self.to_unit.set(a)
        self.convert()

    def clear_history(self):
        self.history.clear()
        self.history_list.delete(0, tk.END)
        self.status_text.set("History cleared")

    def reuse_history(self, _event=None):
        selection = self.history_list.curselection()
        if selection:
            expr = self.history[selection[0]][0]
            self.expression.set(expr)
            self.notebook.select(self.calc_tab)

    def toggle_theme(self):
        # A simple high-contrast dark mode for the calculator window.
        self.dark = not self.dark
        bg = "#111827" if self.dark else BG
        fg = "#f9fafb" if self.dark else TEXT
        self.root.configure(bg=bg)
        for tab in (self.calc_tab, self.converter_tab, self.history_tab):
            tab.configure(bg=bg)
        # Recolor main containers and labels without changing input/display semantics.
        for widget in self.root.winfo_children():
            if isinstance(widget, tk.Frame) and widget.cget("bg") not in ("#17243a",):
                try:
                    widget.configure(bg=bg)
                except tk.TclError:
                    pass
        self.status_text.set("Dark appearance selected" if self.dark else "Light appearance selected")


def main():
    root = tk.Tk()
    CalculatorApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
