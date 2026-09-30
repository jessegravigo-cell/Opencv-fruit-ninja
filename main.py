import cv2
import numpy as np
import random
import math
import time
import os
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision

# Screen Dimensions
WIDTH, HEIGHT = 1280, 720

# Initialize MediaPipe HandLandmarker
model_path = os.path.join(os.path.dirname(__file__), 'hand_landmarker.task')

if not os.path.exists(model_path):
    print(f"ERROR: '{model_path}' not found!")
    print("Please download 'hand_landmarker.task' and put it in the same folder as fruit.py.")
    exit()

base_options = python.BaseOptions(model_asset_path=model_path)
options = vision.HandLandmarkerOptions(
    base_options=base_options,
    num_hands=1,
    min_hand_detection_confidence=0.5,
    min_hand_presence_confidence=0.5
)
detector = vision.HandLandmarker.create_from_options(options)

class Fruit:
    def __init__(self):
        self.radius = random.randint(40, 60)  # Slightly larger fruits
        self.x = random.randint(self.radius + 100, WIDTH - self.radius - 100)
        self.y = HEIGHT + self.radius
        
        # Physics / Motion variables
        self.vx = random.uniform(-3, 3)
        self.vy = random.uniform(-20, -15)  # Upward launch force
        self.gravity = 0.4
        
        # Color & Type (BGR format for OpenCV)
        types = [
            {"color": (0, 0, 255), "name": "Apple"},      # Red
            {"color": (0, 215, 255), "name": "Orange"},  # Orange
            {"color": (0, 255, 0), "name": "Lime"},      # Green
            {"color": (0, 255, 255), "name": "Lemon"}    # Yellow
        ]
        chosen = random.choice(types)
        self.color = chosen["color"]
        
        self.sliced = False

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += self.gravity  # Apply gravity

    def draw(self, img):
        if not self.sliced:
            # Draw main fruit body
            cv2.circle(img, (int(self.x), int(self.y)), self.radius, self.color, -1)
            # Outline
            cv2.circle(img, (int(self.x), int(self.y)), self.radius, (255, 255, 255), 2)
        else:
            # Draw sliced halves separating
            cv2.circle(img, (int(self.x - 20), int(self.y)), self.radius // 2, self.color, -1)
            cv2.circle(img, (int(self.x + 20), int(self.y)), self.radius // 2, self.color, -1)

class Game:
    def __init__(self):
        self.fruits = []
        self.score = 0
        self.misses = 0
        self.max_misses = 5
        self.trail = []  # Stores finger positions for blade trail effect
        self.spawn_timer = time.time()
        self.spawn_interval = 1.2  # Seconds between spawns

    def check_slice(self, finger_x, finger_y):
        for fruit in self.fruits:
            if not fruit.sliced:
                # Calculate distance between index finger tip and fruit center
                dist = math.hypot(finger_x - fruit.x, finger_y - fruit.y)
                # Slicing threshold (Fruit radius + finger tip buffer)
                if dist < fruit.radius + 30:  
                    fruit.sliced = True
                    self.score += 10

    def update_and_draw(self, img):
        # Spawn fruits continuously
        if time.time() - self.spawn_timer > self.spawn_interval:
            self.fruits.append(Fruit())
            self.spawn_timer = time.time()

        for fruit in self.fruits[:]:
            fruit.update()
            fruit.draw(img)

            # Check if fruit fell off screen unsliced
            if fruit.y > HEIGHT + fruit.radius + 50:
                if not fruit.sliced:
                    self.misses += 1
                self.fruits.remove(fruit)

        # Render Score and Misses UI
        cv2.putText(img, f"Score: {self.score}", (30, 60), 
                    cv2.FONT_HERSHEY_SIMPLEX, 1.5, (255, 255, 255), 3)
        cv2.putText(img, f"Misses: {self.misses}/{self.max_misses}", (WIDTH - 320, 60), 
                    cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 0, 255), 3)

def main():
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, WIDTH)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, HEIGHT)

    game = Game()

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        # Get actual frame dimensions
        h, w, _ = frame.shape

        # Mirror frame horizontally for natural movement tracking
        frame = cv2.flip(frame, 1)
        
        # Convert BGR image to RGB for MediaPipe processing
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)

        # Detect hand landmarks
        detection_result = detector.detect(mp_image)

        if detection_result.hand_landmarks:
            for hand_landmarks in detection_result.hand_landmarks:
                # Landmark 8 is the Index Finger Tip
                index_tip = hand_landmarks[8]
                
                # Map relative coordinates (0.0 - 1.0) directly to actual pixel dimensions
                finger_x = int(index_tip.x * w)
                finger_y = int(index_tip.y * h)

                # Visual Debugger: Draw red circle at finger location
                cv2.circle(frame, (finger_x, finger_y), 12, (0, 0, 255), -1)

                # Store history for trail effect
                game.trail.append((finger_x, finger_y))
                if len(game.trail) > 8:
                    game.trail.pop(0)

                # Check slice collision
                game.check_slice(finger_x, finger_y)
        else:
            game.trail.clear()

        # Draw Blade Trail (cyan line)
        for i in range(1, len(game.trail)):
            thickness = int(np.sqrt(8 / float(i + 1)) * 5)
            cv2.line(frame, game.trail[i - 1], game.trail[i], (255, 255, 0), thickness)

        # Update and render game objects
        game.update_and_draw(frame)

        # Game Over Condition
        if game.misses >= game.max_misses:
            cv2.putText(frame, "GAME OVER", (w // 2 - 200, h // 2), 
                        cv2.FONT_HERSHEY_SIMPLEX, 2.5, (0, 0, 255), 5)
            cv2.putText(frame, "Press 'R' to Restart or 'Q' to Quit", (w // 2 - 280, h // 2 + 80), 
                        cv2.FONT_HERSHEY_SIMPLEX, 1.0, (255, 255, 255), 2)

        cv2.imshow("OpenCV Fruit Ninja", frame)

        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
        elif key == ord('r') and game.misses >= game.max_misses:
            game = Game()  # Reset game state

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
