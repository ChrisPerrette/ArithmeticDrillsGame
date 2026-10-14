import tkinter as tk
import tkinter.font as tkfont
import tkinter.messagebox as messagebox
from fractions import Fraction
import random
import json
import os

# File paths for saving data
SETTINGS_FILE = "settings.json"
ALL_TIME_FILE = "High_Scores_AllTime.json"
SCORE_FILES = {
    "+": "High_Scores_Add.json",
    "–": "High_Scores_Sub.json",
    "×": "High_Scores_Mul.json",
    "÷": "High_Scores_Div.json",
    "x²": "High_Scores_Exp.json",
    "( )": "High_Scores_Order.json",
    "x": "High_Scores_Solve.json",
    "½": "High_Scores_Frac.json",
}

DEFAULT_SETTINGS = {
    "min_val": 0,
    "max_val": 12,
    "game_time": 90,
    "password": "password",
    "allow_negatives": False,
    "two_step": True,
    "unlike_denominators": True,
}

# ---------------------------------------------------------------------------
# Theme: chalkboard green header, cool paper background, pencil-yellow accent
# ---------------------------------------------------------------------------
CHALK = "#1E3A34"       # chalkboard green (headers, primary buttons)
CHALK_LT = "#2B5047"    # lighter chalkboard (buttons on the header)
CHALK_TEXT = "#B9CEC6"  # soft chalk text for subtitles
PAPER = "#EDF1F4"       # page background
SURFACE = "#FFFFFF"     # cards
BORDER = "#D3DCE2"
INK = "#1C2B33"         # main text
MUTED = "#5E6E78"       # secondary text
PENCIL = "#F2B705"      # pencil-yellow accent stripe
SOFT = "#E3E9ED"        # neutral button fill
FIELD = "#F7F9FA"       # input fill
SUCCESS = "#2E8B57"
DANGER = "#C0392B"

# key: (name, color, tile symbol, instruction shown under each problem)
CATEGORY_INFO = {
    "+": ("Addition", "#2E7D4F", "+", "Find the sum."),
    "–": ("Subtraction", "#B5472E", "\u2212", "Find the difference."),
    "×": ("Multiplication", "#2F5D9E", "×", "Find the product."),
    "÷": ("Division", "#7A4E9C", "÷", "Find the quotient."),
    "x²": ("Exponents & roots", "#0F7C7A", "x²", "Evaluate the power or square root."),
    "( )": ("Order of operations", "#9C6A12", "( )", "Use the order of operations."),
    "x": ("Solve for x", "#4A5560", "x = ?", "Find the value of x."),
    "½": ("Fractions", "#A3365F", "½", "Answers are in lowest terms."),
}
CATEGORY_ORDER = ["+", "–", "×", "÷", "x²", "( )", "x", "½"]

MINUS = "\u2212"  # true minus sign, easier to read than a hyphen
FONT_FAMILY = "Arial"


def pick_font(root):
    global FONT_FAMILY
    available = set(tkfont.families(root))
    for name in ("Segoe UI", "Avenir Next", "Helvetica Neue", "Noto Sans",
                 "DejaVu Sans", "Helvetica", "Arial"):
        if name in available:
            FONT_FAMILY = name
            return

def F(size, weight="normal"):
    return (FONT_FAMILY, size, weight)

def shade(hex_color, factor):
    hex_color = hex_color.lstrip("#")
    r, g, b = (int(hex_color[i:i + 2], 16) for i in (0, 2, 4))
    if factor < 0:
        r, g, b = (int(c * (1 + factor)) for c in (r, g, b))
    else:
        r, g, b = (int(c + (255 - c) * factor) for c in (r, g, b))
    return f"#{r:02x}{g:02x}{b:02x}"

def load_scores(category):
    filename = SCORE_FILES[category]
    if os.path.exists(filename):
        try:
            with open(filename, "r") as f:
                return json.load(f)
        except Exception:
            pass
    return []

def load_all_time_scores():
    if os.path.exists(ALL_TIME_FILE):
        try:
            with open(ALL_TIME_FILE, "r") as f:
                return json.load(f)
        except Exception:
            pass
    return []

def seed_all_time_scores():
    if not os.path.exists(ALL_TIME_FILE):
        seed_scores = []
        for cat, file in SCORE_FILES.items():
            if os.path.exists(file):
                try:
                    with open(file, "r") as f:
                        cat_scores = json.load(f)
                        for s in cat_scores:
                            seed_scores.append({
                                "name": s["name"], 
                                "score": s["score"], 
                                "category": cat
                            })
                except Exception:
                    pass
        seed_scores.sort(key=lambda x: x["score"], reverse=True)
        with open(ALL_TIME_FILE, "w") as f:
            json.dump(seed_scores[:5], f)

# ---------------------------------------------------------------------------
# Number formatting
# ---------------------------------------------------------------------------
def fmt_num(v):
    if isinstance(v, Fraction):
        if v.denominator == 1:
            v = v.numerator
        else:
            text = f"{abs(v.numerator)}/{v.denominator}"
            return MINUS + text if v < 0 else text
    return f"{MINUS}{abs(v)}" if v < 0 else str(v)

def fmt_term(v):
    text = fmt_num(v)
    return f"({text})" if v < 0 else text

def fmt_raw_fraction(signed_num, den):
    text = f"{abs(signed_num)}/{den}"
    return MINUS + text if signed_num < 0 else text

def fmt_linear(a, k):
    if a == 1:
        text = "x"
    elif a == -1:
        text = MINUS + "x"
    else:
        text = f"{fmt_num(a)}x"
    if k > 0:
        text += f" + {k}"
    elif k < 0:
        text += f" {MINUS} {abs(k)}"
    return text

# ---------------------------------------------------------------------------
# Advanced Math Rendering 
# ---------------------------------------------------------------------------
def render_math(container, text, size, bg_color, fg_color, bind_func=None):
    """Parses a string and renders fractions vertically, aligning whole numbers to the center."""
    for w in container.winfo_children():
        w.destroy()
        
    def apply(w):
        if bind_func:
            bind_func(w)

    # Central container to keep the whole equation together
    inner = tk.Frame(container, bg=bg_color)
    inner.pack(expand=True)
    apply(inner)

    tokens = text.split(" ")
    for token in tokens:
        if "/" in token and "÷" not in token:
            prefix, suffix = "", ""
            if token.startswith("("):
                prefix = "("
                token = token[1:]
            if token.endswith(")"):
                suffix = ")"
                token = token[:-1]
            
            num_str, den_str = token.split("/")
            
            term_frame = tk.Frame(inner, bg=bg_color)
            term_frame.pack(side="left", padx=2, anchor="c")
            apply(term_frame)
            
            if prefix:
                lbl = tk.Label(term_frame, text=prefix, font=F(size, "bold"), bg=bg_color, fg=fg_color)
                lbl.pack(side="left")
                apply(lbl)
                
            frac_frame = tk.Frame(term_frame, bg=bg_color)
            frac_frame.pack(side="left", padx=1, anchor="c")
            apply(frac_frame)
            
            frac_size = max(12, int(size * 0.65)) 
            
            num_lbl = tk.Label(frac_frame, text=num_str, font=F(frac_size, "bold"), bg=bg_color, fg=fg_color)
            num_lbl.pack(side="top")
            apply(num_lbl)
            
            bar = tk.Frame(frac_frame, bg=fg_color, height=max(2, size//15))
            bar.pack(side="top", fill="x", pady=1)
            bar._is_frac_bar = True  
            apply(bar)
            
            den_lbl = tk.Label(frac_frame, text=den_str, font=F(frac_size, "bold"), bg=bg_color, fg=fg_color)
            den_lbl.pack(side="top")
            apply(den_lbl)
            
            if suffix:
                lbl = tk.Label(term_frame, text=suffix, font=F(size, "bold"), bg=bg_color, fg=fg_color)
                lbl.pack(side="left")
                apply(lbl)
        else:
            lbl = tk.Label(inner, text=token, font=F(size, "bold"), bg=bg_color, fg=fg_color)
            lbl.pack(side="left", padx=3)
            apply(lbl)


class MathButton(tk.Frame):
    """A button that supports complex math rendering (like vertical fractions)."""
    def __init__(self, parent, command=None, bg=SURFACE, fg=INK, hover_bg="#EEF3F6", **kw):
        super().__init__(parent, bg=bg, cursor="hand2", **kw)
        self._base = bg
        self._hover = hover_bg
        self._fg = fg
        self._command = command
        self._last_text = ""
        self._last_size = 40
        
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)
        self.bind("<ButtonRelease-1>", self._on_click)

    def _bind_all(self, w):
        w.bind("<Enter>", self._on_enter)
        w.bind("<Leave>", self._on_leave)
        w.bind("<ButtonRelease-1>", self._on_click)

    def _on_enter(self, e):
        self._paint(self._hover)
        
    def _on_leave(self, e):
        self._paint(self._base)

    def _on_click(self, e):
        if self._command:
            self._command()

    def _paint(self, bg_color):
        self.configure(bg=bg_color)
        for w in self.winfo_children():
            w.configure(bg=bg_color)
            for sub in w.winfo_children():
                if getattr(sub, "_is_frac_bar", False):
                    continue
                sub.configure(bg=bg_color)
                for sub2 in sub.winfo_children():
                    if getattr(sub2, "_is_frac_bar", False):
                        continue
                    sub2.configure(bg=bg_color)

    def set_content(self, text, size=40):
        self._last_text = text
        self._last_size = size
        render_math(self, text, size, self._base, self._fg, self._bind_all)

    def set_colors(self, bg, fg, hover_bg):
        self._base = bg
        self._hover = hover_bg
        self._fg = fg
        self._paint(bg)
        self.set_content(self._last_text, self._last_size)


# ---------------------------------------------------------------------------
# Reusable widgets
# ---------------------------------------------------------------------------
class FlatButton(tk.Label):
    def __init__(self, parent, text="", command=None, bg=CHALK, fg="white",
                 hover_bg=None, font=None, padx=18, pady=10, **kw):
        super().__init__(parent, text=text, bg=bg, fg=fg, font=font or F(12, "bold"),
                         padx=padx, pady=pady, cursor="hand2", **kw)
        self._base = bg
        self._hover = hover_bg or shade(bg, -0.12)
        self._command = command
        self.bind("<Enter>", lambda e: self.configure(bg=self._hover))
        self.bind("<Leave>", lambda e: self.configure(bg=self._base))
        self.bind("<ButtonRelease-1>", self._on_click)

    def _on_click(self, event):
        inside = 0 <= event.x <= self.winfo_width() and 0 <= event.y <= self.winfo_height()
        if inside and self._command:
            self._command()

    def set_colors(self, bg, fg=None, hover_bg=None):
        self._base = bg
        self._hover = hover_bg or shade(bg, -0.12)
        self.configure(bg=bg)
        if fg:
            self.configure(fg=fg)


class Toggle(FlatButton):
    def __init__(self, parent, value=False):
        super().__init__(parent, "", self.flip, font=F(11, "bold"), padx=0, pady=6, width=6)
        self.set(value)

    def flip(self):
        self.set(not self.value)

    def set(self, value):
        self.value = bool(value)
        if self.value:
            self.set_colors(SUCCESS, "white")
            self.config(text="On")
        else:
            self.set_colors(SOFT, MUTED)
            self.config(text="Off")


class OperationTile(tk.Frame):
    def __init__(self, parent, symbol, name, color, command):
        super().__init__(parent, bg=color, cursor="hand2")
        self.color = color
        self.hover = shade(color, -0.12)
        self.command = command

        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=3)
        self.rowconfigure(1, weight=1)

        self.sym = tk.Label(self, text=symbol, font=F(40, "bold"), bg=color, fg="white", cursor="hand2")
        self.sym.grid(row=0, column=0, sticky="s", pady=(8, 0))
        self.name = tk.Label(self, text=name, font=F(13, "bold"), bg=color, fg=shade(color, 0.78),
                             cursor="hand2", wraplength=150, justify="center")
        self.name.grid(row=1, column=0, sticky="n", pady=(0, 12), padx=6)

        for w in (self, self.sym, self.name):
            w.bind("<Enter>", lambda e: self._paint(self.hover))
            w.bind("<Leave>", lambda e: self._paint(self.color))
            w.bind("<Button-1>", lambda e: self.command())

    def _paint(self, color):
        for w in (self, self.sym, self.name):
            w.configure(bg=color)


class Header(tk.Frame):
    def __init__(self, parent, title, subtitle="", accent=PENCIL):
        super().__init__(parent, bg=CHALK)
        self.columnconfigure(0, weight=1)

        text_box = tk.Frame(self, bg=CHALK)
        text_box.grid(row=0, column=0, sticky="w", padx=28, pady=(16, 14))
        self.title_lbl = tk.Label(text_box, text=title, font=F(22, "bold"), bg=CHALK, fg="white")
        self.title_lbl.pack(anchor="w")
        self.subtitle_lbl = tk.Label(text_box, text=subtitle, font=F(11), bg=CHALK, fg=CHALK_TEXT)
        self.subtitle_lbl.pack(anchor="w")

        self.actions = tk.Frame(self, bg=CHALK)
        self.actions.grid(row=0, column=1, sticky="e", padx=24)

        self.stripe = tk.Frame(self, bg=accent, height=5)
        self.stripe.grid(row=1, column=0, columnspan=2, sticky="ew")

    def set(self, title=None, subtitle=None, accent=None):
        if title is not None:
            self.title_lbl.config(text=title)
        if subtitle is not None:
            self.subtitle_lbl.config(text=subtitle)
        if accent is not None:
            self.stripe.config(bg=accent)

    def add_action(self, text, command):
        btn = FlatButton(self.actions, text, command, bg=CHALK_LT, fg="white",
                         font=F(11, "bold"), padx=14, pady=8)
        btn.pack(side="left", padx=(8, 0))
        return btn


def card(parent, **kw):
    return tk.Frame(parent, bg=SURFACE, highlightthickness=1, highlightbackground=BORDER,
                    highlightcolor=BORDER, **kw)


def styled_entry(parent, font=None, **kw):
    return tk.Entry(parent, font=font or F(14), justify="center", relief="flat",
                    bg=FIELD, fg=INK, insertbackground=INK,
                    highlightthickness=2, highlightbackground=BORDER, highlightcolor=CHALK, **kw)


def make_dialog(controller, title, heading, subtitle=None):
    win = tk.Toplevel(controller)
    win.title(title)
    win.configure(bg=SURFACE)
    win.resizable(False, False)
    win.transient(controller)

    top = tk.Frame(win, bg=CHALK)
    top.pack(fill="x")
    tk.Label(top, text=heading, font=F(15, "bold"), bg=CHALK, fg="white").pack(
        anchor="w", padx=22, pady=(14, 0 if subtitle else 14))
    if subtitle:
        tk.Label(top, text=subtitle, font=F(10), bg=CHALK, fg=CHALK_TEXT).pack(anchor="w", padx=22, pady=(0, 12))
    tk.Frame(win, bg=PENCIL, height=4).pack(fill="x")

    body = tk.Frame(win, bg=SURFACE)
    body.pack(fill="both", expand=True, padx=22, pady=18)
    win.bind("<Escape>", lambda e: win.destroy())
    return win, body


def _safe_grab(win):
    if not win.winfo_exists():
        return
    try:
        win.grab_set()
    except tk.TclError:
        win.after(50, lambda: _safe_grab(win))


def center_dialog(win, controller):
    win.update_idletasks()
    w, h = win.winfo_reqwidth(), win.winfo_reqheight()
    x = controller.winfo_rootx() + (controller.winfo_width() - w) // 2
    y = controller.winfo_rooty() + (controller.winfo_height() - h) // 3
    win.geometry(f"+{max(x, 0)}+{max(y, 0)}")
    _safe_grab(win)


# ---------------------------------------------------------------------------
# App
# ---------------------------------------------------------------------------
class MathGameApp(tk.Tk):
    def __init__(self):
        super().__init__()
        pick_font(self)
        self.title("Arithmetic Drills")
        self.geometry("1000x700")
        self.minsize(820, 620)
        self.configure(bg=PAPER)

        # Fullscreen setup
        self.is_fullscreen = False
        self.bind("<f>", self.toggle_fullscreen)
        self.bind("<F>", self.toggle_fullscreen)
        self.bind("<Escape>", self.exit_fullscreen)

        # Make the main window grid resizable
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)

        self.load_settings()
        seed_all_time_scores()

        # Container for all frames
        self.container = tk.Frame(self, bg=PAPER)
        self.container.grid(row=0, column=0, sticky="nsew")
        self.container.rowconfigure(0, weight=1)
        self.container.columnconfigure(0, weight=1)

        self.frames = {}
        for F_ in (MainMenu, GameScreen, ScoreboardScreen, SettingsScreen):
            page_name = F_.__name__
            frame = F_(parent=self.container, controller=self)
            self.frames[page_name] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame("MainMenu")

    def toggle_fullscreen(self, event=None):
        if event and event.widget.winfo_class() == "Entry":
            return
        self.is_fullscreen = not self.is_fullscreen
        self.attributes("-fullscreen", self.is_fullscreen)

    def exit_fullscreen(self, event=None):
        self.is_fullscreen = False
        self.attributes("-fullscreen", False)

    def load_settings(self):
        self.settings = dict(DEFAULT_SETTINGS)
        if os.path.exists(SETTINGS_FILE):
            try:
                with open(SETTINGS_FILE, "r") as f:
                    saved = json.load(f)
                    self.settings.update(saved)
            except Exception:
                pass

    def save_settings(self):
        with open(SETTINGS_FILE, "w") as f:
            json.dump(self.settings, f)

    def show_frame(self, page_name, *args):
        frame = self.frames[page_name]
        if hasattr(frame, "on_show"):
            frame.on_show(*args)
        frame.tkraise()


class MainMenu(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=PAPER)
        self.controller = controller

        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

        header = Header(self, "Arithmetic Drills",
                        "Timed math practice, from basic facts through pre-algebra. Pick a drill to start.")
        header.grid(row=0, column=0, sticky="ew")
        
        # Add the Fullscreen action (uses unicode Square Four Corners symbol)
        header.add_action("\u26F6", self.controller.toggle_fullscreen)
        header.add_action("?", self.show_help)
        header.add_action("\u2699  Settings", self.prompt_password)

        body = tk.Frame(self, bg=PAPER)
        body.grid(row=1, column=0, sticky="nsew", padx=40, pady=(24, 10))
        for c in range(4):
            body.columnconfigure(c, weight=1, uniform="tile")
        for r in range(2):
            body.rowconfigure(r, weight=1, uniform="row")

        for idx, key in enumerate(CATEGORY_ORDER):
            name, color, symbol, _ = CATEGORY_INFO[key]
            tile = OperationTile(body, symbol, name, color,
                                 lambda k=key: controller.show_frame("GameScreen", k))
            tile.grid(row=idx // 4, column=idx % 4, sticky="nsew", padx=7, pady=7)

        footer = tk.Frame(self, bg=PAPER)
        footer.grid(row=2, column=0, sticky="ew", padx=47, pady=(4, 26))
        footer.columnconfigure(0, weight=3)
        footer.columnconfigure(1, weight=1)

        FlatButton(footer, "View scoreboards", lambda: controller.show_frame("ScoreboardScreen"),
                   bg=CHALK, fg="white", font=F(14, "bold"), pady=14).grid(
            row=0, column=0, sticky="ew", padx=(0, 8))
        FlatButton(footer, "Quit", controller.quit, bg=SURFACE, fg=DANGER, hover_bg="#FBEAEA",
                   font=F(14, "bold"), pady=14, highlightthickness=1, highlightbackground=BORDER,
                   highlightcolor=BORDER).grid(row=0, column=1, sticky="ew", padx=(8, 0))

    def show_help(self):
        win, body = make_dialog(self.controller, "How to Play", "How to Play")
        
        instructions = (
            "1. Pick a math drill from the main menu.\n\n"
            "2. Read the problem and choose the correct answer.\n\n"
            "3. Click the answer with your mouse, or press the Left or Right arrow keys (you can also use the Control key instead of the Left arrow). \n\n"
            "4. Answer as many as you can before the timer runs out!\n\n"
            "5. Press 'Spacebar' at any time to pause the game.\n\n"
            "6. Press 'F' to play in fullscreen mode, and 'Escape' to exit fullscreen.\n\n"
            "Note: Wrong answers lower your score, so think carefully before you guess."
        )
        
        lbl = tk.Label(body, text=instructions, font=F(12), bg=SURFACE, fg=INK, justify="left", wraplength=350)
        lbl.pack(padx=10, pady=(0, 20))
        
        FlatButton(body, "OK", win.destroy, bg=CHALK, fg="white").pack()
        center_dialog(win, self.controller)

    def prompt_password(self):
        win, body = make_dialog(self.controller, "Teacher access", "Teacher access",
                                "Enter the password to open settings")

        entry = styled_entry(body, show="\u2022", width=24)
        entry.pack(fill="x", ipady=6)
        error = tk.Label(body, text="", font=F(10), bg=SURFACE, fg=DANGER)
        error.pack(anchor="w", pady=(6, 0))

        def check_pwd(event=None):
            if entry.get() == self.controller.settings.get("password", "password"):
                win.destroy()
                self.controller.show_frame("SettingsScreen")
            else:
                error.config(text="That password doesn't match. Try again.")
                entry.delete(0, tk.END)

        btns = tk.Frame(body, bg=SURFACE)
        btns.pack(fill="x", pady=(10, 0))
        FlatButton(btns, "Unlock", check_pwd, bg=CHALK, fg="white").pack(side="right")
        FlatButton(btns, "Cancel", win.destroy, bg=SOFT, fg=INK).pack(side="right", padx=(0, 8))

        entry.bind("<Return>", check_pwd)
        center_dialog(win, self.controller)
        entry.focus_set()


class GameScreen(tk.Frame):
    ANSWER_HOVER = "#EEF3F6"

    def __init__(self, parent, controller):
        super().__init__(parent, bg=PAPER)
        self.controller = controller
        self.category = "+"
        self.timer_id = None
        self.countdown_id = None
        self.pause_delay_id = None
        self.calculated_score = 0
        self.is_flashing = False
        self.is_paused = False
        self.is_countdown = False
        self.time_remaining = 0
        self.total_time = 1
        self._is_root = False
        self._measure_font = tkfont.Font(family=FONT_FAMILY, size=60, weight="bold")

        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

        self.header = Header(self, "Addition", "")
        self.header.grid(row=0, column=0, sticky="ew")
        self.header.add_action("Main menu", self.exit_game)

        # ---------------- Active game view ----------------
        self.play_frame = tk.Frame(self, bg=PAPER)
        self.play_frame.columnconfigure(0, weight=1)
        self.play_frame.rowconfigure(1, weight=3)
        self.play_frame.rowconfigure(2, weight=2)

        timer_row = tk.Frame(self.play_frame, bg=PAPER)
        timer_row.grid(row=0, column=0, sticky="ew", pady=(0, 14))
        timer_row.columnconfigure(1, weight=1)
        tk.Label(timer_row, text="Time left", font=F(11, "bold"), bg=PAPER, fg=MUTED).grid(
            row=0, column=0, sticky="w", padx=(0, 12))
        self.progress = tk.Canvas(timer_row, height=10, bg=SOFT, highlightthickness=0, bd=0)
        self.progress.grid(row=0, column=1, sticky="ew")
        self.progress.bind("<Configure>", lambda e: self.draw_progress())
        self.time_label = tk.Label(timer_row, text="", font=F(20, "bold"), bg=PAPER, fg=CHALK,
                                   width=5, anchor="e")
        self.time_label.grid(row=0, column=2, sticky="e", padx=(12, 0))

        # Problem card
        self.problem_card = card(self.play_frame)
        self.problem_card.grid(row=1, column=0, sticky="nsew")
        self.problem_accent = tk.Frame(self.problem_card, bg=PENCIL, height=6)
        self.problem_accent.pack(fill="x")
        problem_inner = tk.Frame(self.problem_card, bg=SURFACE)
        problem_inner.pack(expand=True)
        
        self.problem_container = tk.Frame(problem_inner, bg=SURFACE)
        self.problem_container.pack()
        
        self.instruction_label = tk.Label(problem_inner, text="", font=F(12), bg=SURFACE, fg=MUTED)
        self.instruction_label.pack(pady=(6, 6))

        # Answer buttons
        self.buttons_frame = tk.Frame(self.play_frame, bg=PAPER)
        self.buttons_frame.grid(row=2, column=0, sticky="nsew", pady=(16, 0))
        self.buttons_frame.rowconfigure(0, weight=1)
        self.buttons_frame.columnconfigure(0, weight=1, uniform="ans")
        self.buttons_frame.columnconfigure(1, weight=1, uniform="ans")

        answer_style = dict(bg=SURFACE, fg=INK, hover_bg=self.ANSWER_HOVER,
                            highlightthickness=2, highlightbackground=BORDER, highlightcolor=BORDER)
        self.left_btn = MathButton(self.buttons_frame, command=lambda: self.check_answer("left"), **answer_style)
        self.left_btn.grid(row=0, column=0, sticky="nsew", padx=(0, 8))
        self.right_btn = MathButton(self.buttons_frame, command=lambda: self.check_answer("right"), **answer_style)
        self.right_btn.grid(row=0, column=1, sticky="nsew", padx=(8, 0))

        tk.Label(self.play_frame, text="Keyboard shortcuts:  \u2190 or Ctrl picks the left answer,  \u2192 picks the right",
                 font=F(10), bg=PAPER, fg=MUTED).grid(row=3, column=0, pady=(12, 0))

        # Countdown label (Fix: Removed expand=True which breaks the grid layout)
        self.countdown_label = tk.Label(self.play_frame, text="", font=F(120, "bold"), bg=PAPER, fg=CHALK)

        # Pause overlay
        self.pause_overlay = tk.Frame(self.play_frame, bg=CHALK)
        tk.Label(self.pause_overlay, text="Game paused\n\nPress the Spacebar to resume", 
                 font=F(28, "bold"), bg=CHALK, fg="white", justify="center").pack(expand=True)

        # ---------------- Results view (hidden initially) ----------------
        self.results_frame = tk.Frame(self, bg=PAPER)
        self.results_frame.columnconfigure(0, weight=1)
        self.results_frame.rowconfigure(0, weight=1)

        results_card = card(self.results_frame)
        results_card.grid(row=0, column=0)
        self.results_accent = tk.Frame(results_card, bg=PENCIL, height=6)
        self.results_accent.pack(fill="x")

        inner = tk.Frame(results_card, bg=SURFACE)
        inner.pack(padx=56, pady=(20, 28))
        tk.Label(inner, text="Time's up! Your final score", font=F(16, "bold"), bg=SURFACE, fg=INK).pack()
        self.score_label = tk.Label(inner, text="", font=F(56, "bold"), bg=SURFACE, fg=SUCCESS)
        self.score_label.pack()

        stats = tk.Frame(inner, bg=SURFACE)
        stats.pack(pady=(0, 16))
        self.correct_stat = self._stat(stats, "Correct", SUCCESS, 0)
        self.wrong_stat = self._stat(stats, "Incorrect", DANGER, 1)
        self.answered_label = self._stat(stats, "Problems answered", CHALK, 2)

        tk.Frame(inner, bg=BORDER, height=1).pack(fill="x", pady=(0, 14))
        tk.Label(inner, text="Type your name for the scoreboard", font=F(12, "bold"),
                 bg=SURFACE, fg=INK).pack()
        self.name_entry = styled_entry(inner, font=F(16), width=24)
        self.name_entry.pack(pady=(8, 14), ipady=6)
        self.name_entry.bind("<Return>", self.save_score)
        FlatButton(inner, "Save score", self.save_score, bg=CHALK, fg="white",
                   font=F(13, "bold"), pady=12).pack(fill="x")

    def _stat(self, parent, label, color, col):
        box = tk.Frame(parent, bg=SURFACE)
        box.grid(row=0, column=col, padx=18)
        value = tk.Label(box, text="0", font=F(20, "bold"), bg=SURFACE, fg=color)
        value.pack()
        tk.Label(box, text=label, font=F(10), bg=SURFACE, fg=MUTED).pack()
        return value

    def _reset_answer_colors(self, btn):
        btn.set_colors(SURFACE, INK, self.ANSWER_HOVER)

    @property
    def neg(self):
        return bool(self.controller.settings.get("allow_negatives", False))

    def on_show(self, category="+"):
        self.category = category
        name, color, _, instruction = CATEGORY_INFO[category]
        self.header.set(title=name, subtitle="Pick the correct answer as fast as you can.", accent=color)
        self.problem_accent.config(bg=color)
        self.results_accent.config(bg=color)
        self.instruction_label.config(text=instruction)

        self.success_count = 0
        self.failure_count = 0
        self.time_remaining = self.controller.settings["game_time"]
        self.total_time = max(1, self.time_remaining)
        self.is_flashing = False
        self.is_paused = False
        self.is_countdown = True

        if self.timer_id:
            self.after_cancel(self.timer_id)
            self.timer_id = None
        if self.countdown_id:
            self.after_cancel(self.countdown_id)
            self.countdown_id = None
        if self.pause_delay_id:
            self.after_cancel(self.pause_delay_id)
            self.pause_delay_id = None

        self.pause_overlay.place_forget()
        self.results_frame.grid_forget()
        self.play_frame.grid(row=1, column=0, sticky="nsew", padx=48, pady=24)
        self.update_idletasks()

        self._reset_answer_colors(self.left_btn)
        self._reset_answer_colors(self.right_btn)

        self.controller.bind("<Left>", lambda e: self.check_answer("left"))
        self.controller.bind("<Control_L>", lambda e: self.check_answer("left"))
        self.controller.bind("<Control_R>", lambda e: self.check_answer("left"))
        self.controller.bind("<Right>", lambda e: self.check_answer("right"))
        self.controller.bind("<space>", self.toggle_pause)

        # Clear the timer text initially during the countdown
        mins, secs = divmod(self.time_remaining, 60)
        self.time_label.config(text=f"{mins}:{secs:02d}", fg=CHALK)
        self.draw_progress()

        # Hide problem and buttons, show countdown
        self.problem_card.grid_remove()
        self.buttons_frame.grid_remove()
        self.countdown_label.grid(row=1, column=0, rowspan=2)
        self.run_countdown(3)

    def run_countdown(self, count):
        if count > 0:
            self.countdown_label.config(text=str(count))
            self.countdown_id = self.after(1000, lambda: self.run_countdown(count - 1))
        else:
            self.countdown_label.grid_remove()
            self.problem_card.grid()
            self.buttons_frame.grid()
            self.is_countdown = False
            self.generate_problem()
            self.update_timer()

    def toggle_pause(self, event=None):
        if self.is_countdown or self.time_remaining <= 0:
            return

        # Ignore extra spacebar presses if we are currently in the 0.5s resume delay
        if self.pause_delay_id:
            return

        if not self.is_paused:
            self.is_paused = True
            if self.timer_id:
                self.after_cancel(self.timer_id)
                self.timer_id = None
            self.pause_overlay.place(relx=0, rely=0, relwidth=1, relheight=1)
            self.pause_overlay.lift()
        else:
            self.pause_overlay.place_forget()
            # 0.5 second delay before timer resumes and inputs are allowed
            self.pause_delay_id = self.after(500, self.resume_from_pause)

    def resume_from_pause(self):
        self.pause_delay_id = None
        self.is_paused = False
        if self.time_remaining > 0:
            self.update_timer()

    def exit_game(self):
        if self.timer_id:
            self.after_cancel(self.timer_id)
            self.timer_id = None
        if self.countdown_id:
            self.after_cancel(self.countdown_id)
            self.countdown_id = None
        if self.pause_delay_id:
            self.after_cancel(self.pause_delay_id)
            self.pause_delay_id = None
            
        self.controller.unbind("<Left>")
        self.controller.unbind("<Control_L>")
        self.controller.unbind("<Control_R>")
        self.controller.unbind("<Right>")
        self.controller.unbind("<space>")
        self.controller.show_frame("MainMenu")

    # ------------------------------------------------------------------
    # Problem generation
    # ------------------------------------------------------------------
    def rand(self, lo, hi, signed=True):
        v = random.randint(lo, hi)
        if signed and self.neg and v != 0 and random.random() < 0.5:
            v = -v
        return v

    def number_range(self):
        s = self.controller.settings
        lo, hi = s["min_val"], s["max_val"]
        return min(lo, hi), max(lo, hi)

    def gen_addition(self, lo, hi):
        a, b = self.rand(lo, hi), self.rand(lo, hi)
        mistakes = [a - b] if self.neg else []
        return f"{fmt_num(a)} + {fmt_term(b)} =", a + b, mistakes

    def gen_subtraction(self, lo, hi):
        a, b = self.rand(lo, hi), self.rand(lo, hi)
        if not self.neg and a < b:
            a, b = b, a
        mistakes = [a + b] if self.neg else []
        return f"{fmt_num(a)} {MINUS} {fmt_term(b)} =", a - b, mistakes

    def gen_multiplication(self, lo, hi):
        a, b = self.rand(lo, hi), self.rand(lo, hi)
        return f"{fmt_num(a)} × {fmt_term(b)} =", a * b, [a + b]

    def gen_division(self, lo, hi):
        ans = self.rand(lo, hi)
        b = self.rand(max(1, lo), max(1, hi))
        a = ans * b
        return f"{fmt_num(a)} ÷ {fmt_term(b)} =", ans, []

    def gen_exponents(self, lo, hi):
        sq_hi = max(1, min(hi, 15))
        sq_lo = min(lo, sq_hi)
        kind = random.choice(["square", "square", "cube", "root", "root"])
        if kind == "square":
            n = self.rand(sq_lo, sq_hi)
            return f"{fmt_term(n)}² =", n * n, [2 * n, n + 2]
        if kind == "cube":
            cu_hi = max(1, min(hi, 6))
            n = self.rand(min(lo, cu_hi), cu_hi)
            return f"{fmt_term(n)}³ =", n ** 3, [3 * n, n * n]
        n = random.randint(sq_lo, sq_hi)
        sq = n * n
        self._is_root = True
        mistakes = [sq // 2] if sq % 2 == 0 else []
        return f"\u221A{sq} =", n, mistakes

    def gen_order_of_ops(self, lo, hi):
        f_hi = max(1, min(hi, 12))
        f_lo = min(lo, f_hi)
        form = random.randint(1, 5)
        if form == 1:
            a, b, c = self.rand(lo, hi), self.rand(f_lo, f_hi), self.rand(f_lo, f_hi)
            return (f"{fmt_num(a)} + {fmt_term(b)} × {fmt_term(c)} =", a + b * c, [(a + b) * c])
        if form == 2:
            b, c = self.rand(f_lo, f_hi), self.rand(f_lo, f_hi)
            a = self.rand(lo, hi) if self.neg else b * c + random.randint(lo, hi)
            return (f"{fmt_num(a)} {MINUS} {fmt_term(b)} × {fmt_term(c)} =", a - b * c, [(a - b) * c])
        if form == 3:
            a, b, c = self.rand(f_lo, f_hi), self.rand(f_lo, f_hi), self.rand(lo, hi)
            return (f"{fmt_num(a)} × {fmt_term(b)} + {fmt_term(c)} =", a * b + c, [a * (b + c)])
        if form == 4:
            a, b, c = self.rand(f_lo, f_hi), self.rand(f_lo, f_hi), self.rand(f_lo, f_hi)
            return (f"({fmt_num(a)} + {fmt_term(b)}) × {fmt_term(c)} =", (a + b) * c, [a + b * c])
        a, b, c = self.rand(lo, hi), self.rand(lo, hi), self.rand(lo, hi)
        if not self.neg and a < b:
            a, b = b, a
        return (f"{fmt_num(a)} {MINUS} {fmt_term(b)} + {fmt_term(c)} =", a - b + c, [a - (b + c)])

    def gen_solve_for_x(self, lo, hi):
        coef_hi = max(2, min(hi, 12))

        def coef():
            v = random.randint(2, coef_hi)
            return -v if self.neg and random.random() < 0.5 else v

        def constant(limit):
            k = random.randint(max(1, lo), max(1, hi))
            if (self.neg or k <= limit) and random.random() < 0.5:
                k = -k
            return k

        forms = ["add", "mul", "div"]
        if self.controller.settings.get("two_step", True):
            forms += ["two", "two"]
        form = random.choice(forms)
        x = self.rand(lo, hi)

        if form == "add":
            k = constant(x)
            c = x + k
            return f"{fmt_linear(1, k)} = {fmt_num(c)}", x, [c + k]
        if form == "mul":
            a = coef()
            c = a * x
            return f"{fmt_linear(a, 0)} = {fmt_num(c)}", x, [c - a, c * a]
        if form == "div":
            a = coef()
            q = x
            x = a * q
            return f"x ÷ {fmt_term(a)} = {fmt_num(q)}", x, [q, q + a]
        
        a = coef()
        k = constant(a * x)
        c = a * x + k
        mistakes = [c - k]
        if (c + k) % a == 0:
            mistakes.append((c + k) // a)
        if c % a == 0:
            mistakes.append(c // a - k)
        return f"{fmt_linear(a, k)} = {fmt_num(c)}", x, mistakes

    def gen_fractions(self, lo, hi):
        d1 = random.randint(2, 12)
        unlike = self.controller.settings.get("unlike_denominators", True)
        d2 = random.randint(2, 12) if unlike and random.random() < 0.7 else d1
        n1, n2 = random.randint(1, d1 - 1), random.randint(1, d2 - 1)
        if self.neg and random.random() < 0.5:
            if random.random() < 0.5:
                n1 = -n1
            else:
                n2 = -n2
        op = random.choice(["+", MINUS, "×"])
        f1, f2 = Fraction(n1, d1), Fraction(n2, d2)
        if op == MINUS and not self.neg and f1 < f2:
            f1, f2, n1, n2, d1, d2 = f2, f1, n2, n1, d2, d1

        if op == "+":
            correct = f1 + f2
            mistakes = [Fraction(n1 + n2, d1 + d2)]
        elif op == MINUS:
            correct = f1 - f2
            mistakes = [Fraction(n1 - n2, d1 + d2)]
        else:
            correct = f1 * f2
            mistakes = [Fraction(n1 * d2, d1 * n2)] if n2 != 0 else []

        left = fmt_raw_fraction(n1, d1)
        right = fmt_raw_fraction(n2, d2)
        if n2 < 0:
            right = f"({right})"
        return f"{left} {op} {right} =", correct, mistakes

    GENERATORS = {
        "+": "gen_addition", "–": "gen_subtraction", "×": "gen_multiplication",
        "÷": "gen_division", "x²": "gen_exponents", "( )": "gen_order_of_ops",
        "x": "gen_solve_for_x", "½": "gen_fractions",
    }

    def pick_wrong(self, correct, mistakes):
        candidates = []
        for m in mistakes:
            if m is None or m == correct or m in candidates:
                continue
            if not self.neg and m < 0:
                continue
            candidates.append(m)

        if self.neg and correct != 0 and not self._is_root and random.random() < 0.35:
            return -correct
        if candidates and random.random() < 0.7:
            return random.choice(candidates)

        if isinstance(correct, Fraction):
            den = correct.denominator if correct.denominator > 1 else random.randint(2, 6)
            for _ in range(20):
                w = correct + Fraction(random.choice([-3, -2, -1, 1, 2, 3]), den)
                if self.neg or w >= 0:
                    return w
            return correct + Fraction(1, den)

        deltas = [-12, -10, -8, -5, -3, -2, -1, 1, 2, 3, 5, 8, 10, 12]
        for _ in range(20):
            w = correct + random.choice(deltas)
            if self.neg or w >= 0:
                return w
        return correct + 1

    def fmt_answer(self, value):
        return f"x = {fmt_num(value)}" if self.category == "x" else fmt_num(value)

    def show_problem_text(self, text):
        available = max(300, self.problem_card.winfo_width() - 60)
        size = 60
        self._measure_font.configure(family=FONT_FAMILY, size=size)
        while size > 28 and self._measure_font.measure(text) > available:
            size -= 4
            self._measure_font.configure(size=size)
        
        render_math(self.problem_container, text, size, SURFACE, INK)

    def generate_problem(self):
        lo, hi = self.number_range()
        self._is_root = False
        generator = getattr(self, self.GENERATORS[self.category])
        prob_text, self.correct_ans, mistakes = generator(lo, hi)
        self.show_problem_text(prob_text)

        wrong_ans = self.pick_wrong(self.correct_ans, mistakes)

        if random.choice([True, False]):
            self.left_val = self.correct_ans
            self.right_val = wrong_ans
            self.correct_side = "left"
        else:
            self.left_val = wrong_ans
            self.right_val = self.correct_ans
            self.correct_side = "right"

        self.left_btn.set_content(self.fmt_answer(self.left_val))
        self.right_btn.set_content(self.fmt_answer(self.right_val))

    # ------------------------------------------------------------------
    # Answering and timing
    # ------------------------------------------------------------------
    def check_answer(self, side):
        # Ignore input if timer is stopped, game is paused, or currently in countdown/flash
        if self.time_remaining <= 0 or self.is_flashing or self.is_paused or self.is_countdown:
            return

        self.is_flashing = True

        if side == self.correct_side:
            self.success_count += 1
            flash_color = SUCCESS
        else:
            self.failure_count += 1
            flash_color = DANGER

        target_btn = self.left_btn if side == "left" else self.right_btn
        target_btn.set_colors(flash_color, "white", flash_color)

        self.after(150, lambda: self.reset_flash_and_continue(target_btn))

    def reset_flash_and_continue(self, target_btn):
        self._reset_answer_colors(target_btn)
        self.is_flashing = False

        if self.time_remaining > 0:
            self.generate_problem()

    def draw_progress(self):
        c = self.progress
        c.delete("all")
        w, h = c.winfo_width(), c.winfo_height()
        frac = max(0.0, min(1.0, self.time_remaining / self.total_time))
        color = DANGER if self.time_remaining <= 10 else CATEGORY_INFO[self.category][1]
        if frac > 0:
            c.create_rectangle(0, 0, w * frac, h, fill=color, outline="")

    def update_timer(self):
        if self.time_remaining > 0:
            mins, secs = divmod(self.time_remaining, 60)
            low = self.time_remaining <= 10
            self.time_label.config(text=f"{mins}:{secs:02d}", fg=DANGER if low else CHALK)
            self.draw_progress()
            self.time_remaining -= 1
            self.timer_id = self.after(1000, self.update_timer)
        else:
            self.timer_id = None
            self.end_game()

    def end_game(self):
        self.controller.unbind("<Left>")
        self.controller.unbind("<Control_L>")
        self.controller.unbind("<Control_R>")
        self.controller.unbind("<Right>")
        self.controller.unbind("<space>")

        self.calculated_score = self.success_count - self.failure_count
        total_answered = self.success_count + self.failure_count

        self.score_label.config(text=fmt_num(self.calculated_score),
                                fg=SUCCESS if self.calculated_score >= 0 else DANGER)
        self.correct_stat.config(text=str(self.success_count))
        self.wrong_stat.config(text=str(self.failure_count))
        self.answered_label.config(text=str(total_answered))

        self.header.set(subtitle="Nice work. Save your score or head back to the menu.")
        self.play_frame.grid_forget()
        self.results_frame.grid(row=1, column=0, sticky="nsew", padx=48, pady=24)

        self.name_entry.delete(0, tk.END)
        self.name_entry.focus_set()

    def save_score(self, event=None):
        name = self.name_entry.get().strip()
        if not name:
            name = "Anonymous"

        filename = SCORE_FILES[self.category]
        scores = load_scores(self.category)

        scores.append({"name": name, "score": self.calculated_score})
        scores.sort(key=lambda x: x["score"], reverse=True)

        with open(filename, "w") as f:
            json.dump(scores, f)
            
        all_time = load_all_time_scores()
        all_time.append({"name": name, "score": self.calculated_score, "category": self.category})
        all_time.sort(key=lambda x: x["score"], reverse=True)
        
        with open(ALL_TIME_FILE, "w") as f:
            json.dump(all_time[:5], f)

        self.exit_game()


class ScoreboardScreen(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=PAPER)
        self.controller = controller

        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

        header = Header(self, "Scoreboards", "Top five scores for each drill")
        header.grid(row=0, column=0, sticky="ew")
        header.add_action("Main menu", lambda: controller.show_frame("MainMenu"))

        self.scores_frame = tk.Frame(self, bg=PAPER)
        self.scores_frame.grid(row=1, column=0, sticky="nsew", padx=26, pady=20)
        
        for i in range(3):
            self.scores_frame.columnconfigure(i, weight=1, uniform="board")

    def on_show(self):
        for widget in self.scores_frame.winfo_children():
            widget.destroy()

        display_categories = CATEGORY_ORDER + ["ALL"]

        for idx, key in enumerate(display_categories):
            if key == "ALL":
                name = "All-Time Highs"
                color = "#1C2B33" 
                scores = load_all_time_scores()
            else:
                name, color, symbol, _ = CATEGORY_INFO[key]
                scores = load_scores(key)

            board = card(self.scores_frame)
            board.grid(row=idx // 3, column=idx % 3, sticky="new", padx=6, pady=4)

            top = tk.Frame(board, bg=color)
            top.pack(fill="x")
            tk.Label(top, text=name, font=F(10, "bold"), bg=color, fg="white").pack(side="left", padx=10, pady=8)

            rows = tk.Frame(board, bg=SURFACE)
            rows.pack(fill="both", expand=True, padx=8, pady=8)

            for i in range(5):
                row_bg = FIELD if i % 2 == 0 else SURFACE
                row = tk.Frame(rows, bg=row_bg)
                row.pack(fill="x", pady=1)

                rank_color = PENCIL if i == 0 and i < len(scores) else MUTED
                tk.Label(row, text=str(i + 1), font=F(11, "bold"), bg=row_bg, fg=rank_color,
                         width=2).pack(side="left", padx=(4, 2), pady=4)

                if i < len(scores):
                    player = str(scores[i]["name"])
                    
                    if key == "ALL":
                        cat_sym = scores[i].get("category", "")
                        if len(player) > 8:
                            player = player[:7] + "\u2026"
                        player += f" ({cat_sym})"
                    else:
                        if len(player) > 12:
                            player = player[:11] + "\u2026"
                            
                    score_text = fmt_num(scores[i]["score"])
                    name_color = INK
                else:
                    player, score_text, name_color = "No score yet", "", MUTED

                tk.Label(row, text=score_text, font=F(11, "bold"), bg=row_bg, fg=INK).pack(side="right", padx=(4, 8))
                tk.Label(row, text=player, font=F(11), bg=row_bg, fg=name_color, anchor="w").pack(
                    side="left", fill="x", expand=True)


class SettingsScreen(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=PAPER)
        self.controller = controller
        self._status_job = None

        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

        header = Header(self, "Teacher settings", "Adjust difficulty, timing and pre-algebra options for every drill")
        header.grid(row=0, column=0, sticky="ew")

        body = tk.Frame(self, bg=PAPER)
        body.grid(row=1, column=0, sticky="nsew", padx=40, pady=16)
        body.columnconfigure(0, weight=1, uniform="settings")
        body.columnconfigure(1, weight=1, uniform="settings")

        range_card = card(body)
        range_card.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        ri = tk.Frame(range_card, bg=SURFACE)
        ri.pack(fill="both", expand=True, padx=24, pady=18)
        ri.columnconfigure(0, weight=1)
        tk.Label(ri, text="Numbers and time", font=F(15, "bold"), bg=SURFACE, fg=INK).grid(
            row=0, column=0, columnspan=2, sticky="w")
        tk.Label(ri, text="With negative numbers on, these set how big each number is, ignoring its sign.",
                 font=F(10), bg=SURFACE, fg=MUTED, wraplength=290, justify="left").grid(
            row=1, column=0, columnspan=2, sticky="w", pady=(0, 6))
        self.min_spin = self._spin_field(ri, 2, "Smallest number", "Lowest value used in problems", 0, 100)
        self.max_spin = self._spin_field(ri, 3, "Largest number", "Highest value used in problems", 0, 100)
        self.time_spin = self._spin_field(ri, 4, "Game time (seconds)", "How long each drill lasts", 0, 180)

        opt_card = card(body)
        opt_card.grid(row=0, column=1, sticky="nsew", padx=(10, 0))
        oi = tk.Frame(opt_card, bg=SURFACE)
        oi.pack(fill="both", expand=True, padx=24, pady=18)
        oi.columnconfigure(0, weight=1)
        tk.Label(oi, text="Pre-algebra options", font=F(15, "bold"), bg=SURFACE, fg=INK).grid(
            row=0, column=0, columnspan=2, sticky="w")
        tk.Label(oi, text="Turn these on as students are ready for them.",
                 font=F(10), bg=SURFACE, fg=MUTED, wraplength=290, justify="left").grid(row=1, column=0, columnspan=2, sticky="w", pady=(0, 6))
        self.neg_toggle = self._toggle_field(oi, 2, "Negative numbers",
                                             f"Integers like {MINUS}7\u00a0+\u00a03 appear in every drill")
        self.two_step_toggle = self._toggle_field(oi, 3, "Two-step equations",
                                                  "Adds problems like 3x\u00a0+\u00a04\u00a0=\u00a019 to Solve for x")
        self.unlike_toggle = self._toggle_field(oi, 4, "Unlike denominators",
                                                "Adds problems like 1/3\u00a0+\u00a01/4 to Fractions")

        tools = card(body)
        tools.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(14, 0))
        ti = tk.Frame(tools, bg=SURFACE)
        ti.pack(fill="x", padx=20, pady=10)
        FlatButton(ti, "Restore defaults", self.reset_to_default, bg=SOFT, fg=INK).pack(side="left", padx=(0, 6))
        FlatButton(ti, "Change password", self.change_password, bg=SOFT, fg=INK).pack(side="left", padx=4)
        FlatButton(ti, "Clear scoreboards", self.reset_scoreboard, bg="#FBEAEA", fg=DANGER,
                   hover_bg="#F5D5D5").pack(side="left", padx=4)

        actions = tk.Frame(body, bg=PAPER)
        actions.grid(row=2, column=0, columnspan=2, sticky="ew", pady=(12, 0))
        self.status = tk.Label(actions, text="", font=F(11), bg=PAPER, fg=SUCCESS)
        self.status.pack(side="left")
        FlatButton(actions, "Save changes", self.save_and_return, bg=SUCCESS, fg="white").pack(side="right")
        FlatButton(actions, "Cancel", lambda: controller.show_frame("MainMenu"), bg=SOFT, fg=INK).pack(
            side="right", padx=(0, 8))

    def _field_label(self, parent, row, title, help_text):
        tk.Frame(parent, bg=BORDER, height=1).grid(row=row, column=0, columnspan=2, sticky="new")
        label_box = tk.Frame(parent, bg=SURFACE)
        label_box.grid(row=row, column=0, sticky="w", pady=7)
        tk.Label(label_box, text=title, font=F(12, "bold"), bg=SURFACE, fg=INK).pack(anchor="w")
        tk.Label(label_box, text=help_text, font=F(10), bg=SURFACE, fg=MUTED,
                 wraplength=200, justify="left").pack(anchor="w")

    def _spin_field(self, parent, row, title, help_text, lo, hi):
        self._field_label(parent, row, title, help_text)
        spin = tk.Spinbox(parent, from_=lo, to=hi, font=F(14), width=5, justify="center",
                          relief="flat", bg=FIELD, fg=INK, buttonbackground=SOFT,
                          highlightthickness=2, highlightbackground=BORDER, highlightcolor=CHALK,
                          insertbackground=INK)
        spin.grid(row=row, column=1, sticky="e", pady=7, ipady=3)
        return spin

    def _toggle_field(self, parent, row, title, help_text):
        self._field_label(parent, row, title, help_text)
        toggle = Toggle(parent)
        toggle.grid(row=row, column=1, sticky="e", pady=7)
        return toggle

    def show_status(self, message, color=SUCCESS):
        if self._status_job:
            self.after_cancel(self._status_job)
        self.status.config(text=message, fg=color)
        self._status_job = self.after(4000, lambda: self.status.config(text=""))

    def _set_spin(self, spin, value):
        spin.delete(0, tk.END)
        spin.insert(0, value)

    def on_show(self):
        s = self.controller.settings
        self.status.config(text="")
        self._set_spin(self.min_spin, s["min_val"])
        self._set_spin(self.max_spin, s["max_val"])
        self._set_spin(self.time_spin, s["game_time"])
        self.neg_toggle.set(s.get("allow_negatives", False))
        self.two_step_toggle.set(s.get("two_step", True))
        self.unlike_toggle.set(s.get("unlike_denominators", True))

    def reset_to_default(self):
        d = DEFAULT_SETTINGS
        self._set_spin(self.min_spin, d["min_val"])
        self._set_spin(self.max_spin, d["max_val"])
        self._set_spin(self.time_spin, d["game_time"])
        self.neg_toggle.set(d["allow_negatives"])
        self.two_step_toggle.set(d["two_step"])
        self.unlike_toggle.set(d["unlike_denominators"])
        self.show_status("Defaults restored. Select Save changes to keep them.", CHALK)

    def reset_scoreboard(self):
        confirm = messagebox.askyesno("Clear all scoreboards",
                                      "This permanently deletes every saved score in all drills. \n\nNote: The All-Time High Scores list will NOT be erased. Continue?")
        if confirm:
            for filename in SCORE_FILES.values():
                try:
                    with open(filename, "w") as f:
                        json.dump([], f)
                except Exception:
                    pass
            self.show_status("All category scoreboards cleared.")

    def change_password(self):
        win, body = make_dialog(self.controller, "Change password", "Change password",
                                "Type the new password in both boxes")

        tk.Label(body, text="New password", font=F(11, "bold"), bg=SURFACE, fg=INK).pack(anchor="w")
        box1 = styled_entry(body, show="\u2022", width=26)
        box1.pack(fill="x", ipady=5, pady=(4, 10))
        tk.Label(body, text="Confirm new password", font=F(11, "bold"), bg=SURFACE, fg=INK).pack(anchor="w")
        box2 = styled_entry(body, show="\u2022", width=26)
        box2.pack(fill="x", ipady=5, pady=(4, 0))

        error = tk.Label(body, text="", font=F(10), bg=SURFACE, fg=DANGER)
        error.pack(anchor="w", pady=(6, 0))

        def confirm(event=None):
            val1 = box1.get()
            val2 = box2.get()
            if val1 == "":
                error.config(text="Enter a new password.")
            elif val1 != val2:
                error.config(text="The two passwords don't match.")
            else:
                self.controller.settings["password"] = val1
                self.controller.save_settings()
                win.destroy()
                self.show_status("Password changed.")

        btn_frame = tk.Frame(body, bg=SURFACE)
        btn_frame.pack(fill="x", pady=(10, 0))
        FlatButton(btn_frame, "Change password", confirm, bg=CHALK, fg="white").pack(side="right")
        FlatButton(btn_frame, "Cancel", win.destroy, bg=SOFT, fg=INK).pack(side="right", padx=(0, 8))

        box2.bind("<Return>", confirm)
        center_dialog(win, self.controller)
        box1.focus_set()

    def save_and_return(self):
        s = self.controller.settings
        try:
            s["min_val"] = int(self.min_spin.get())
            s["max_val"] = int(self.max_spin.get())
            s["game_time"] = int(self.time_spin.get())
            if s["min_val"] > s["max_val"]:
                s["min_val"] = s["max_val"]
        except ValueError:
            pass

        s["allow_negatives"] = self.neg_toggle.value
        s["two_step"] = self.two_step_toggle.value
        s["unlike_denominators"] = self.unlike_toggle.value
        self.controller.save_settings()

        self.controller.show_frame("MainMenu")


if __name__ == "__main__":
    app = MathGameApp()
    app.mainloop()