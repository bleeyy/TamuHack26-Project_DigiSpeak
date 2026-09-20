import tkinter as tk
from PIL import Image, ImageTk
import time
import numpy as np
from collections import deque

# ================== MAIN LOGIC (UNCHANGED CORE) ==================

MAX = 1023

class hand(object):
    def __init__(self, fingers=[0,0,0,0,0], acceleration=[0,0,0], angles=[0,0,0]):
        self.fingers = fingers
        self.angles = angles
        self.accel = acceleration

    @property
    def accel(self):
        return self._accel

    @accel.setter
    def accel(self, values):
        self._accel = np.array(values, dtype=float)

    @property
    def fingers(self):
        return self._fingers

    @fingers.setter
    def fingers(self, values):
        self._fingers = np.array(values, dtype=float)
        self.thumb, self.index, self.middle, self.ring, self.pinky = self._fingers

    @property
    def angles(self):
        return self._angles

    @angles.setter
    def angles(self, values):
        self._angles = np.array([v % 360 for v in values], dtype=float)

def follow(path):
    with open(path, "r") as f:
        while True:
            line = f.readline()
            if not line:
                time.sleep(0.05)
                continue
            yield line.strip()

def main():
    hands = deque([])
    moving_avg = deque([])
    calibration = True
    waveness = 1

    for line in follow("arduinodata.csv"):
        try:
            h_temp = np.array([float(x) for x in line.split(',')])
            h_temp[-1:] = [h_temp[-1], 0, 0]

            if calibration:
                hands.append(hand(h_temp[6:], h_temp[:3], h_temp[3:6]))
                if len(hands) >= 100:
                    calibration = False
                    hands.clear()
                continue

            moving_avg.append(h_temp)
            if len(moving_avg) > 10:
                moving_avg.popleft()

            h_temp = np.mean(moving_avg, axis=0)

            hands.append(hand(h_temp[6:], h_temp[:3], h_temp[3:6]))
            if len(hands) > 50:
                hands.popleft()

            out = "..."
            last = hands[-1]

            if last.thumb > 512 and last.middle < 512:
                out = "Gig 'Em!"
            elif 300 < last.thumb < 700 and last.middle > 512:
                out = "Peace!"
            elif last.index < 600 and last.thumb > 512:
                out = "No"
            elif waveness > 1:
                out = "Wave!"
                waveness -= 1

            yield out

        except Exception:
            pass

# ================== TKINTER UI ==================

window = tk.Tk()
window.configure(background="#FFEFD5")
window.title("Sign Translator")
window.geometry("1200x900")

translated = tk.StringVar(window, value="Starting...")

IMAGE_MAP = {
    "...": "images/Question.png",
    "Gig 'Em!": "images/GigEm.png",
    "Wave!": "images/Wave.png",
    "Peace!": "images/Peace.png",
    "No": "images/No.png"
}

image_label = tk.Label(window, bg="#FFEFD5")
image_label.place(relx=0.38, rely=0.65)

def update_image(*_):
    word = translated.get()
    if word in IMAGE_MAP:
        img = Image.open(IMAGE_MAP[word]).resize((300,300))
        tk_img = ImageTk.PhotoImage(img)
        image_label.config(image=tk_img)
        image_label.image = tk_img

translated.trace_add("write", update_image)

translation_label = tk.Label(
    window,
    textvariable=translated,
    font=("Arial", 125),
    bg="#FFEFD5",
    fg="#8B0000"
)
translation_label.place(relx=0.5, rely=0.5, anchor="center")

# ================== GENERATOR POLLING (THE IMPORTANT PART) ==================

gesture_stream = main()  # generator instance

def poll_main():
    try:
        new_value = next(gesture_stream)
        if translated.get() != new_value:
            translated.set(new_value)
    except StopIteration:
        pass

    window.after(50, poll_main)  # ~20 FPS update rate

poll_main()
window.mainloop()
