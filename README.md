# Arithmetic Drills Game (`math_game.py`)

A classroom-styled, customizable math drill application built with Python and Tkinter. Features advanced vertical fraction rendering, customizable audio feedback, duration-partitioned scoreboards, and secret teacher modifiers.

---

## 🌟 Key Features

- **8 Math Categories:**
  - Addition (`+`)
  - Subtraction (`–`)
  - Multiplication (`×`)
  - Division (`÷`)
  - Exponents & Roots (`x²`)
  - Order of Operations (`( )`)
  - Solve for x (`x = ?`)
  - Fractions (`½`) with dynamic vertical stacking and fraction bar rendering

- **Clean Directory Isolation:**
  - Automatically segregates saved high scores and settings into a `data/` directory.
  - Manages sound effect assets cleanly inside a `sounds/` directory.

- **Audio Feedback (`pygame-ce`):**
  - Instant audio cues for correct answers, incorrect answers, and game completion.
  - Safe fallback mechanism ensures the game runs smoothly even if sound hardware or files are missing.

- **Teacher Settings & Security:**
  - Password-protected settings menu (Default password: `password`).
  - Customizable number range limits (`min_val`, `max_val`) and drill durations (30 to 300 seconds).
  - Toggles for negative numbers, two-step equations, and unlike denominators.
  - **Secret Key Modifier:** Hold key `1`-`9`, `0`, `-`, `=`, or ``` ` ``` when starting a basic drill to force that number into the practice set.

- **Scoreboard Management:**
  - Category high scores and all-time boards automatically partitioned by game duration.

---

## 📁 Directory Structure

Upon first run, the game will automatically create the required subdirectories:

```text
├── math_game_3.py             # Main application script
├── data/                      # Auto-generated application data
│   ├── settings.json          # Teacher settings and configurations
│   ├── High_Scores_AllTime.json
│   └── High_Scores_*.json     # Individual category high scores
└── sounds/                    # Audio asset directory
    ├── correct.mp3            # Sound played on correct answer
    ├── wrong.mp3              # Sound played on incorrect answer
    └── finish.mp3             # Sound played when time expires
```

---

## 🚀 Installation & Requirements

### Prerequisites
- **Python 3.8+**
- **Tkinter** (included with standard Python installations on Windows/macOS)

### 1. Install Dependencies
Install `pygame-ce` (Community Edition) for audio support:

```bash
python -m pip install --upgrade pip setuptools wheel
pip install pygame-ce
```

### 2. Configure Audio Assets
Drop your preferred audio files into the `sounds/` folder:
- `correct.mp3` (or `.wav`)
- `wrong.mp3` (or `.wav`)
- `finish.mp3` (or `.wav`)

*(Note: If using `.wav` files, ensure `math_game_3.py` is configured to load `.wav` extensions.)*

### 3. Run the Game
```bash
python math_game_3.py
```

---

## ⌨️ Controls & Keyboard Shortcuts

| Key / Input | Action |
| :--- | :--- |
| **Left Arrow** or **Left Ctrl** | Select Left Answer Option |
| **Right Arrow** | Select Right Answer Option |
| **Spacebar** | Pause / Resume Game |
| **F** | Toggle Fullscreen Mode |
| **Escape** | Exit Fullscreen Mode / Close Dialogs |
| **1-9, 0, -, =** *(Hold during drill launch)* | Secret Key: Lock focus number into basic operations |

---

## 🏫 Teacher Access & Password

1. Click the **⚙ Settings** button in the upper-right corner of the main menu.
2. Enter the teacher password (Default: `password`).
3. From the settings menu, you can adjust difficulty parameters, toggle pre-algebra options, clear scoreboards, or update the teacher password.
