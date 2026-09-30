# OpenCV Fruit Ninja with Hand Tracking

A computer vision-based Fruit Ninja clone built using Python, OpenCV, and MediaPipe's HandLandmarker API. Play hands-free using your webcam and slice falling fruits with your index finger.

---

## 📋 Features

* **Real-Time Hand Tracking:** Uses MediaPipe's HandLandmarker API to track your index finger tip in real time.
* **Physics Engine:** Simulates parabolic motion, velocity, and gravity for launched fruits.
* **Interactive Gameplay:** Features custom blade trail visual effects, distance-based collision detection, live score tracking, and game-over states.

---

## 🛠 Prerequisites & Dependencies

### 1. Requirements
* Python 3.9 – 3.13
* A working webcam
* install https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task
### 2. Install Dependencies
Open your terminal or PowerShell and run:

pip install opencv-python mediapipe numpy



### 3. directory
put the hand_landmarker.task in a same folder with the app.py

### how to play and troubleshoot
🎮 How to Play
1. Stand in front of your webcam in a well-lit area.
2. Hold up your hand—a red dot will track your index finger tip on screen.
3. Swipe across falling fruits to slice them.
4. Scoring: Slicing a fruit awards +10 points.
5. Game Over: Missing 5 fruits ends the game.
6. Controls:
 Press R to restart after Game Over.
 Press Q to quit the game.
🔧 Troubleshooting
 Missing Model File: If you see ⁠ERROR: '...hand_landmarker.task' not found!⁠, confirm ⁠hand_landmarker.task⁠ is located in the same directory as ⁠fruit.py⁠.
 Tracking Latency or Unresponsive Cutting: Ensure proper room lighting so MediaPipe can reliably detect hand landmarks.
