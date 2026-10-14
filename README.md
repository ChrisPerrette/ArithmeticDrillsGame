# Arithmetic Drills

A timed math practice game for the classroom, covering everything from basic facts through pre-algebra. Students see a problem and two possible answers, and pick the right one as fast as they can before time runs out. Teachers control difficulty, timing and which pre-algebra skills are included from a password-protected settings screen.

Built with Python and Tkinter. No other installs are needed.

![Main menu](screenshots/main-menu.png)

## Features

- **Eight drills:** addition, subtraction, multiplication, division, exponents and roots, order of operations, solve for x, and fractions.
- **Two-choice format:** each problem shows one correct answer and one wrong answer. The wrong answer is usually a mistake students really make, so the drill checks understanding as well as speed.
- **Advanced math rendering:** A custom rendering engine parses and dynamically draws fractions with vertical fraction bars, accurately aligning whole numbers and operator symbols to the center.
- **Classroom mechanics:** Features a 3-second visual countdown before each drill, a spacebar-triggered pause menu that obstructs the screen with a 0.5-second input delay upon resuming, and a fullscreen toggle (`F` key or `⛶` button).
- **Keyboard or mouse:** students can click an answer or use the arrow keys.
- **Scoreboards:** the top five scores for each drill are saved between sessions. A persistent 9th master scoreboard also tracks **All-Time Highs** across all game modes, which survives individual category resets.
- **Teacher settings:** set the number range and game length, and turn negative numbers, two-step equations and unlike denominators on or off.
- **Resizable window:** the layout adjusts to the window size, and long problems shrink to fit.

| Order of operations | Solve for x |
| --- | --- |
| ![Order of operations drill](screenshots/order-of-operations.png) | ![Solve for x drill](screenshots/solve-for-x.png) |

## The drills

| Drill | Example problems |
| --- | --- |
| Addition | `7 + 5`, `−9 + (−7)` |
| Subtraction | `12 − 4`, `10 − (−4)` |
| Multiplication | `6 × 8`, `−3 × (−6)` |
| Division | `54 ÷ 9`, `−16 ÷ 4` |
| Exponents & roots | `(−5)²`, `4³`, `√81` |
| Order of operations | `12 − 3 × 4`, `(6 + 2) × 5`, `9 − 4 + 2` |
| Solve for x | `x + 7 = 15`, `4x = 28`, `x ÷ 3 = 6`, `3x − 5 = 16` |
| Fractions | `1/4 + 2/4`, `2/3 − 1/6`, `3/4 × 2/5` |

Problems with negative numbers only appear when **Negative numbers** is turned on in settings. Fraction answers are always given in lowest terms.

### How wrong answers are chosen

Instead of a random number, the wrong answer is usually a common error:

- **Order of operations:** the answer you get by working left to right. For `3 + 4 × 2`, the choices are 11 and 14.
- **Fractions:** the answer you get by adding the tops and the bottoms. For `1/2 + 1/3`, the choices are 5/6 and 2/5.
- **Exponents:** multiplying instead of using the power. For `5²`, the choices are 25 and 10.
- **Solve for x:** using the wrong inverse operation, or forgetting a step.
- **Negative numbers:** the correct answer with the wrong sign.

## Getting started

### Requirements

- Python 3.8 or newer
- Tkinter, which comes with Python on Windows and macOS

On Linux, Tkinter may need to be installed separately:

```bash
# Debian / Ubuntu
sudo apt install python3-tk

# Fedora
sudo dnf install python3-tkinter