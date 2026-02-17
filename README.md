# Flappy Arms

Flappy Bird–style game controlled by your arms: use your webcam and raise your arms to make the bird fly. Great for moving around while you play.

![Python](https://img.shields.io/badge/Python-3.x-blue)
![Pygame](https://img.shields.io/badge/Pygame-2.5-green)
![MediaPipe](https://img.shields.io/badge/MediaPipe-Pose-orange)

## How it works

- **Camera:** The game uses your webcam to detect your pose in real time.
- **Controls:** Raise one or both arms (wrists above shoulders) to make the bird flap and rise.
- **Calibration:** Before playing, you need to calibrate (press **C**) so the game recognizes your starting pose.

## Requirements

- **Python 3.9+**
- **Working webcam**
- Good lighting for pose detection

## Installation

1. Clone the repository (or download the files):

```bash
git clone <repository-url>
cd flappy-arms
```

2. Create and activate a virtual environment (recommended):

```bash
python -m venv .venv
source .venv/bin/activate   # Linux/macOS
# or: .venv\Scripts\activate   # Windows
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Optional: Add `bird_logo.png` (menu logo) and `bird.png` (in-game bird) to the project folder. Without them, the menu and bird use the default graphics.

## How to play

1. Run the game:

```bash
python flappy_arms.py
```

2. On the menu:
   - Press **C** to **calibrate** (stand with arms relaxed).
   - When you see "CALIBRATED!", press **SPACE** to start.

3. During the game:
   - **Raise your arms** to make the bird fly up and avoid the pipes.
   - **ESC** returns to the menu.

4. On game over:
   - **SPACE** — play again  
   - **ESC** — back to menu

## Controls (keyboard)

| Key        | Action                    |
|-----------|---------------------------|
| **C**     | Calibrate (on menu)       |
| **SPACE** | Start / Play again        |
| **ESC**   | Quit / Back to menu       |

## Project structure

```
flappy-arms/
├── flappy_arms.py    # Main game (desktop, camera)
├── game_core.py      # Shared game logic (Bird, Pipe, physics)
├── streamlit_app.py  # Web version (Streamlit)
├── requirements.txt  # Python dependencies
├── bird_logo.png     # Menu logo (optional)
├── bird.png          # In-game bird image (optional)
└── README.md
```

## Dependencies

- **pygame** — graphics and game loop  
- **opencv-python** — webcam capture  
- **mediapipe** — pose detection (shoulders and wrists)

## Tips

- Use a relatively clear background and good lighting for the camera.
- Keep your body (at least shoulders and arms) in frame.
- A flap is detected when your arms **go up**; you don’t need to keep them raised.

## Web version (Streamlit)

To run the browser version (click to flap, same game logic):

```bash
pip install -r requirements.txt
streamlit run streamlit_app.py
```

## License

Free to use for learning and fun.
