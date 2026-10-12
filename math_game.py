import tkinter as tk
from tkinter import ttk
import tkinter.messagebox as messagebox
import random
import json
import os

# File paths for saving data
SETTINGS_FILE = "settings.json"
SCORE_FILES = {
    "+": "High_Scores_Add.json",
    "–": "High_Scores_Sub.json",
    "×": "High_Scores_Mul.json",
    "÷": "High_Scores_Div.json"
}

# Color Palette
BG_COLOR = "#87CEEB" # Sky Blue
TXT_COLOR = "#000080" # Navy Blue
BTN_BG = "#FFD700" # Gold
BTN_ADD = "#FF6347" # Tomato Red
BTN_SUB = "#32CD32" # Lime Green
BTN_MUL = "#1E90FF" # Dodger Blue
BTN_DIV = "#FFA500" # Orange

class MathGameApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Math Game")
        self.geometry("800x600")
        self.minsize(600, 400)
        self.configure(bg=BG_COLOR)
        
        # Make the main window grid resizable
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)
        
        self.load_settings()
        
        # Container for all frames
        self.container = tk.Frame(self, bg=BG_COLOR)
        self.container.grid(row=0, column=0, sticky="nsew")
        self.container.rowconfigure(0, weight=1)
        self.container.columnconfigure(0, weight=1)
        
        self.frames = {}
        for F in (MainMenu, GameScreen, ScoreboardScreen, SettingsScreen):
            page_name = F.__name__
            frame = F(parent=self.container, controller=self)
            self.frames[page_name] = frame
            frame.grid(row=0, column=0, sticky="nsew")
            
        self.show_frame("MainMenu")

    def load_settings(self):
        self.settings = {"min_val": 0, "max_val": 12, "game_time": 90, "password": "password"}
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
        # Call an on_show method if it exists to refresh data
        if hasattr(frame, "on_show"):
            frame.on_show(*args)
        frame.tkraise()

class MainMenu(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.configure(bg=BG_COLOR)
        
        # Configure scaling
        self.rowconfigure(0, weight=1)
        self.rowconfigure(1, weight=3)
        self.rowconfigure(2, weight=1)
        self.rowconfigure(3, weight=1)
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        self.columnconfigure(2, weight=1)
        
        # Main Title
        title_lbl = tk.Label(self, text="ARITHMETIC DRILLS", font=("Arial", 36, "bold"), 
                             bg=BG_COLOR, fg="#FF0000")
        title_lbl.grid(row=0, column=0, columnspan=2, sticky="w", padx=30, pady=10)
        
        # Gear Button (Settings) in Top Right
        gear_btn = tk.Button(self, text="\u2699", font=("Arial", 24, "bold"), relief="raised",
                             bg=BTN_BG, fg=TXT_COLOR, activebackground="white",
                             command=self.prompt_password)
        gear_btn.grid(row=0, column=2, sticky="ne", padx=10, pady=10)
        
        # 2x2 Grid for Game Categories
        grid_frame = tk.Frame(self, bg=BG_COLOR)
        grid_frame.grid(row=1, column=0, columnspan=3, sticky="nsew", padx=50, pady=20)
        for i in range(2):
            grid_frame.rowconfigure(i, weight=1)
            grid_frame.columnconfigure(i, weight=1)
            
        btn_font = ("Arial", 48, "bold")
        tk.Button(grid_frame, text="+", font=btn_font, bg=BTN_ADD, fg="white", activebackground="#FF8C00",
                  command=lambda: controller.show_frame("GameScreen", "+")).grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        tk.Button(grid_frame, text="–", font=btn_font, bg=BTN_SUB, fg="white", activebackground="#00FA9A",
                  command=lambda: controller.show_frame("GameScreen", "–")).grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        tk.Button(grid_frame, text="×", font=btn_font, bg=BTN_MUL, fg="white", activebackground="#00BFFF",
                  command=lambda: controller.show_frame("GameScreen", "×")).grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
        tk.Button(grid_frame, text="÷", font=btn_font, bg=BTN_DIV, fg="white", activebackground="#FFD700",
                  command=lambda: controller.show_frame("GameScreen", "÷")).grid(row=1, column=1, sticky="nsew", padx=10, pady=10)
        
        # Scoreboards & Quit Buttons Frame
        bottom_btn_frame = tk.Frame(self, bg=BG_COLOR)
        bottom_btn_frame.grid(row=2, column=0, columnspan=3, sticky="nsew", padx=50, pady=10)
        bottom_btn_frame.rowconfigure(0, weight=1)
        bottom_btn_frame.columnconfigure(0, weight=1)
        bottom_btn_frame.columnconfigure(1, weight=1)
        
        tk.Button(bottom_btn_frame, text="Scoreboards", font=("Arial", 18, "bold"), bg=BTN_BG, fg=TXT_COLOR,
                  command=lambda: controller.show_frame("ScoreboardScreen")).grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        tk.Button(bottom_btn_frame, text="Quit Game", font=("Arial", 18, "bold"), bg="#FF0000", fg="white",
                  command=controller.quit).grid(row=0, column=1, sticky="nsew", padx=10, pady=10)

    def prompt_password(self):
        pwd_win = tk.Toplevel(self)
        pwd_win.title("Enter Password")
        pwd_win.geometry("350x150")
        pwd_win.configure(bg=BG_COLOR)
        pwd_win.transient(self.controller)
        pwd_win.grab_set()
        
        tk.Label(pwd_win, text="Enter Password:", font=("Arial", 16, "bold"), bg=BG_COLOR, fg=TXT_COLOR).pack(pady=10)
        pwd_entry = tk.Entry(pwd_win, show="*", font=("Arial", 16), justify="center")
        pwd_entry.pack(pady=5)
        pwd_entry.focus()
        
        def check_pwd(event=None):
            entered = pwd_entry.get()
            if entered == self.controller.settings.get("password", "password"):
                pwd_win.destroy()
                self.controller.show_frame("SettingsScreen")
            else:
                pwd_win.destroy()
                
        pwd_entry.bind("<Return>", check_pwd)


class GameScreen(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.configure(bg=BG_COLOR)
        self.category = "+"
        self.timer_id = None
        self.calculated_score = 0
        self.is_flashing = False
        
        # Configure scaling
        self.rowconfigure(0, weight=1)
        self.rowconfigure(1, weight=2)
        self.rowconfigure(2, weight=2)
        self.rowconfigure(3, weight=1)
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        self.columnconfigure(2, weight=1)
        
        # Return Button (Top Right)
        return_btn = tk.Button(self, text="\u21B5", font=("Arial", 36, "bold"), relief="raised",
                               bg=BTN_BG, fg=TXT_COLOR, command=self.exit_game)
        return_btn.grid(row=0, column=2, sticky="ne", padx=20, pady=20)
        
        # Active Game Widgets
        self.problem_label = tk.Label(self, text="", font=("Arial", 64, "bold"), bg=BG_COLOR, fg=TXT_COLOR)
        self.problem_label.grid(row=1, column=0, columnspan=3)
        
        self.buttons_frame = tk.Frame(self, bg=BG_COLOR)
        self.buttons_frame.grid(row=2, column=0, columnspan=3, sticky="nsew", padx=20)
        self.buttons_frame.rowconfigure(0, weight=1)
        self.buttons_frame.columnconfigure(0, weight=1)
        self.buttons_frame.columnconfigure(1, weight=1)
        
        self.left_btn = tk.Button(self.buttons_frame, text="", font=("Arial", 48, "bold"), bg="white", fg=TXT_COLOR, command=lambda: self.check_answer("left"))
        self.left_btn.grid(row=0, column=0, sticky="nsew", padx=10)
        self.right_btn = tk.Button(self.buttons_frame, text="", font=("Arial", 48, "bold"), bg="white", fg=TXT_COLOR, command=lambda: self.check_answer("right"))
        self.right_btn.grid(row=0, column=1, sticky="nsew", padx=10)
        
        self.time_label = tk.Label(self, text="", font=("Arial", 32, "bold"), bg=BG_COLOR, fg="#FF0000")
        self.time_label.grid(row=3, column=0, columnspan=3)
        
        # Post-Game Widgets (Hidden initially)
        self.score_title = tk.Label(self, text="Score", font=("Arial", 36, "bold"), bg=BG_COLOR, fg=TXT_COLOR)
        self.score_label = tk.Label(self, text="", font=("Arial", 64, "bold"), bg=BG_COLOR, fg="#006400") # Dark Green
        self.answered_label = tk.Label(self, text="", font=("Arial", 28, "bold"), bg=BG_COLOR, fg=TXT_COLOR)
        self.name_prompt = tk.Label(self, text="Enter name:", font=("Arial", 24, "bold"), bg=BG_COLOR, fg=TXT_COLOR)
        self.name_entry = tk.Entry(self, font=("Arial", 24, "bold"), justify="center")
        self.name_entry.bind("<Return>", self.save_score)

    def on_show(self, category="+"):
        self.category = category
        self.success_count = 0
        self.failure_count = 0
        self.time_remaining = self.controller.settings["game_time"]
        self.is_flashing = False
        
        # Hide end-game widgets
        self.score_title.grid_forget()
        self.score_label.grid_forget()
        self.answered_label.grid_forget()
        self.name_prompt.grid_forget()
        self.name_entry.grid_forget()
        
        # Show active game widgets
        self.problem_label.grid(row=1, column=0, columnspan=3)
        self.buttons_frame.grid(row=2, column=0, columnspan=3, sticky="nsew", padx=20)
        self.time_label.grid(row=3, column=0, columnspan=3)
        
        # Reset colors just in case
        self.left_btn.config(bg="white")
        self.right_btn.config(bg="white")
        
        # Bind keys
        self.controller.bind("<Left>", lambda e: self.check_answer("left"))
        self.controller.bind("<Control_L>", lambda e: self.check_answer("left"))
        self.controller.bind("<Control_R>", lambda e: self.check_answer("left"))
        self.controller.bind("<Right>", lambda e: self.check_answer("right"))
        
        self.generate_problem()
        self.update_timer()
        
    def exit_game(self):
        if self.timer_id:
            self.after_cancel(self.timer_id)
            self.timer_id = None
        self.controller.unbind("<Left>")
        self.controller.unbind("<Control_L>")
        self.controller.unbind("<Control_R>")
        self.controller.unbind("<Right>")
        self.controller.show_frame("MainMenu")

    def generate_problem(self):
        min_v = self.controller.settings["min_val"]
        max_v = self.controller.settings["max_val"]
        
        if self.category == "+":
            a, b = random.randint(min_v, max_v), random.randint(min_v, max_v)
            self.correct_ans = a + b
            prob_text = f"{a} + {b} ="
        elif self.category == "–":
            a, b = random.randint(min_v, max_v), random.randint(min_v, max_v)
            if a < b:
                a, b = b, a
            self.correct_ans = a - b
            prob_text = f"{a} – {b} ="
        elif self.category == "×":
            a, b = random.randint(min_v, max_v), random.randint(min_v, max_v)
            self.correct_ans = a * b
            prob_text = f"{a} × {b} ="
        elif self.category == "÷":
            divisor_min = max(1, min_v)
            divisor_max = max(1, max_v) if max_v >= 1 else 1
            
            ans = random.randint(min_v, max_v)
            b = random.randint(divisor_min, divisor_max)
            a = ans * b
            self.correct_ans = ans
            prob_text = f"{a} ÷ {b} ="
            
        self.problem_label.config(text=prob_text)
        
        delta = random.choice([-12, -10, -8, -5, -3, -2, -1, 1, 2, 3, 5, 8, 10, 12])
        wrong_ans = self.correct_ans + delta
        if wrong_ans < 0:
            wrong_ans = self.correct_ans + abs(delta)
            
        if random.choice([True, False]):
            self.left_val = self.correct_ans
            self.right_val = wrong_ans
            self.correct_side = "left"
        else:
            self.left_val = wrong_ans
            self.right_val = self.correct_ans
            self.correct_side = "right"
            
        self.left_btn.config(text=str(self.left_val))
        self.right_btn.config(text=str(self.right_val))

    def check_answer(self, side):
        # Prevent input if time is up or if currently flashing
        if self.time_remaining <= 0 or self.is_flashing:
            return
            
        self.is_flashing = True
            
        if side == self.correct_side:
            self.success_count += 1
            flash_color = "#32CD32" # Lime Green
        else:
            self.failure_count += 1
            flash_color = "#FF0000" # Red
            
        # Flash the background of the selected button
        target_btn = self.left_btn if side == "left" else self.right_btn
        target_btn.config(bg=flash_color)
        
        # Wait 150ms, revert the color, and move to the next problem
        self.after(150, lambda: self.reset_flash_and_continue(target_btn))

    def reset_flash_and_continue(self, target_btn):
        target_btn.config(bg="white")
        self.is_flashing = False
        
        # Only generate the next problem if the game hasn't ended during the flash
        if self.time_remaining > 0:
            self.generate_problem()

    def update_timer(self):
        if self.time_remaining > 0:
            self.time_label.config(text=str(self.time_remaining))
            self.time_remaining -= 1
            self.timer_id = self.after(1000, self.update_timer)
        else:
            self.end_game()

    def end_game(self):
        self.controller.unbind("<Left>")
        self.controller.unbind("<Control_L>")
        self.controller.unbind("<Control_R>")
        self.controller.unbind("<Right>")
        
        self.problem_label.grid_forget()
        self.buttons_frame.grid_forget()
        self.time_label.grid_forget()
        
        self.calculated_score = self.success_count - self.failure_count
        total_answered = self.success_count + self.failure_count
        
        self.score_title.grid(row=0, column=0, columnspan=3, pady=(20, 0))
        
        self.score_label.config(text=str(self.calculated_score))
        self.score_label.grid(row=1, column=0, columnspan=3)
        
        self.answered_label.config(text=f"Problems Answered: {total_answered}")
        self.answered_label.grid(row=2, column=0, columnspan=3, pady=10)
        
        self.name_prompt.grid(row=3, column=0, columnspan=3)
        self.name_entry.grid(row=4, column=0, columnspan=3, pady=(0, 40))
        self.name_entry.delete(0, tk.END)
        self.name_entry.focus()

    def save_score(self, event=None):
        name = self.name_entry.get().strip()
        if not name:
            name = "Anonymous"
            
        filename = SCORE_FILES[self.category]
        scores = []
        if os.path.exists(filename):
            try:
                with open(filename, "r") as f:
                    scores = json.load(f)
            except Exception:
                pass
                
        scores.append({"name": name, "score": self.calculated_score})
        scores.sort(key=lambda x: x["score"], reverse=True)
        
        with open(filename, "w") as f:
            json.dump(scores, f)
            
        self.exit_game()


class ScoreboardScreen(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.configure(bg=BG_COLOR)
        
        self.rowconfigure(0, weight=1)
        self.rowconfigure(1, weight=5)
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        
        # Return Button (Top Right)
        return_btn = tk.Button(self, text="\u21B5", font=("Arial", 36, "bold"), relief="raised",
                               bg=BTN_BG, fg=TXT_COLOR, command=lambda: controller.show_frame("MainMenu"))
        return_btn.grid(row=0, column=1, sticky="ne", padx=20, pady=20)
        
        tk.Label(self, text="Top 5 Scores", font=("Arial", 36, "bold"), bg=BG_COLOR, fg=TXT_COLOR).grid(row=0, column=0, columnspan=2, pady=20)
        
        self.scores_frame = tk.Frame(self, bg=BG_COLOR)
        self.scores_frame.grid(row=1, column=0, columnspan=2, sticky="nsew", padx=40, pady=10)
        
        for i in range(4):
            self.scores_frame.columnconfigure(i, weight=1)

    def on_show(self):
        # Clear existing score lists
        for widget in self.scores_frame.winfo_children():
            widget.destroy()
            
        categories = [("+", "Addition"), ("–", "Subtraction"), 
                      ("×", "Multiplication"), ("÷", "Division")]
                      
        for col, (cat_sym, cat_name) in enumerate(categories):
            tk.Label(self.scores_frame, text=cat_name, font=("Arial", 18, "bold"), bg=BG_COLOR, fg="#FF0000").grid(row=0, column=col, pady=10)
            
            filename = SCORE_FILES[cat_sym]
            scores = []
            if os.path.exists(filename):
                try:
                    with open(filename, "r") as f:
                        scores = json.load(f)
                except Exception:
                    pass
            
            for i in range(5):
                if i < len(scores):
                    text = f"{scores[i]['name']}: {scores[i]['score']}"
                else:
                    text = "---"
                tk.Label(self.scores_frame, text=text, font=("Arial", 16, "bold"), bg=BG_COLOR, fg=TXT_COLOR).grid(row=i+1, column=col, pady=5)


class SettingsScreen(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.configure(bg=BG_COLOR)
        
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        for i in range(6):
            self.rowconfigure(i, weight=1)
            
        # Left-Side Action Buttons
        reset_btn = tk.Button(self, text="Reset to Default Values", font=("Arial", 14, "bold"), 
                              bg=BTN_BG, fg=TXT_COLOR, command=self.reset_to_default)
        reset_btn.place(x=15, y=15)
        
        reset_score_btn = tk.Button(self, text="Reset Scoreboard", font=("Arial", 14, "bold"), 
                                    bg=BTN_ADD, fg="white", command=self.reset_scoreboard)
        reset_score_btn.place(x=15, y=65)
        
        change_pwd_btn = tk.Button(self, text="Change Password", font=("Arial", 14, "bold"), 
                                   bg=BTN_MUL, fg="white", command=self.change_password)
        change_pwd_btn.place(x=15, y=115)
        
        tk.Label(self, text="Settings", font=("Arial", 36, "bold"), bg=BG_COLOR, fg=TXT_COLOR).grid(row=0, column=0, columnspan=2, pady=20)
        
        font_setup = ("Arial", 18, "bold")
        
        tk.Label(self, text="Minimum Problem Component Value:", font=font_setup, bg=BG_COLOR, fg=TXT_COLOR).grid(row=1, column=0, sticky="e", padx=10)
        self.min_spin = tk.Spinbox(self, from_=0, to=100, font=font_setup, width=5)
        self.min_spin.grid(row=1, column=1, sticky="w", padx=10)
        
        tk.Label(self, text="Maximum Problem Component Value:", font=font_setup, bg=BG_COLOR, fg=TXT_COLOR).grid(row=2, column=0, sticky="e", padx=10)
        self.max_spin = tk.Spinbox(self, from_=0, to=100, font=font_setup, width=5)
        self.max_spin.grid(row=2, column=1, sticky="w", padx=10)
        
        tk.Label(self, text="Game Time:", font=font_setup, bg=BG_COLOR, fg=TXT_COLOR).grid(row=3, column=0, sticky="e", padx=10)
        self.time_spin = tk.Spinbox(self, from_=0, to=180, font=font_setup, width=5)
        self.time_spin.grid(row=3, column=1, sticky="w", padx=10)
        
        btn_frame = tk.Frame(self, bg=BG_COLOR)
        btn_frame.grid(row=4, column=0, columnspan=2, pady=30)
        tk.Button(btn_frame, text="Save", font=font_setup, bg="#32CD32", fg="white", 
                  command=self.save_and_return).pack(side=tk.LEFT, padx=20)
        tk.Button(btn_frame, text="Return to Main Menu without Saving", font=font_setup, bg="#FF6347", fg="white",
                  command=lambda: controller.show_frame("MainMenu")).pack(side=tk.LEFT, padx=20)

    def on_show(self):
        settings = self.controller.settings
        
        self.min_spin.delete(0, tk.END)
        self.min_spin.insert(0, settings["min_val"])
        
        self.max_spin.delete(0, tk.END)
        self.max_spin.insert(0, settings["max_val"])
        
        self.time_spin.delete(0, tk.END)
        self.time_spin.insert(0, settings["game_time"])
        
    def reset_to_default(self):
        self.min_spin.delete(0, tk.END)
        self.min_spin.insert(0, 0)
        
        self.max_spin.delete(0, tk.END)
        self.max_spin.insert(0, 12)
        
        self.time_spin.delete(0, tk.END)
        self.time_spin.insert(0, 90)

    def reset_scoreboard(self):
        confirm = messagebox.askyesno("Confirm Scoreboard Reset", "Are you sure you want to completely clear the scoreboard? This cannot be undone.")
        if confirm:
            for filename in SCORE_FILES.values():
                try:
                    with open(filename, "w") as f:
                        json.dump([], f)
                except Exception:
                    pass

    def change_password(self):
        pwd_win = tk.Toplevel(self)
        pwd_win.title("Change Password")
        pwd_win.geometry("400x250")
        pwd_win.configure(bg=BG_COLOR)
        pwd_win.transient(self.controller)
        pwd_win.grab_set()
        
        tk.Label(pwd_win, text="Enter New Password in Both Boxes", font=("Arial", 14, "bold"), bg=BG_COLOR, fg=TXT_COLOR).pack(pady=15)
        
        box1 = tk.Entry(pwd_win, show="*", font=("Arial", 16), justify="center")
        box1.pack(pady=5)
        box2 = tk.Entry(pwd_win, show="*", font=("Arial", 16), justify="center")
        box2.pack(pady=5)
        
        def confirm():
            val1 = box1.get()
            val2 = box2.get()
            if val1 == val2 and val1 != "":
                self.controller.settings["password"] = val1
                self.controller.save_settings()
                pwd_win.destroy()
            else:
                pass
                
        def cancel():
            pwd_win.destroy()
            
        btn_frame = tk.Frame(pwd_win, bg=BG_COLOR)
        btn_frame.pack(pady=15)
        tk.Button(btn_frame, text="Confirm", font=("Arial", 12, "bold"), bg=BTN_SUB, fg="white", command=confirm).pack(side=tk.LEFT, padx=10)
        tk.Button(btn_frame, text="Cancel", font=("Arial", 12, "bold"), bg=BTN_ADD, fg="white", command=cancel).pack(side=tk.LEFT, padx=10)

    def save_and_return(self):
        try:
            self.controller.settings["min_val"] = int(self.min_spin.get())
            self.controller.settings["max_val"] = int(self.max_spin.get())
            self.controller.settings["game_time"] = int(self.time_spin.get())
            
            if self.controller.settings["min_val"] > self.controller.settings["max_val"]:
                self.controller.settings["min_val"] = self.controller.settings["max_val"]
                
            self.controller.save_settings()
        except ValueError:
            pass
        
        self.controller.show_frame("MainMenu")

if __name__ == "__main__":
    app = MathGameApp()
    app.mainloop()