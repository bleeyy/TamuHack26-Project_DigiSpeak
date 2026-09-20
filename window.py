import tkinter as tk
from PIL import Image, ImageTk
import threading as t
import queue as q
import main


# ------------------ WINDOW SETUP ------------------
window = tk.Tk()
window.configure(background="#FFEFD5")
window.title("Sign Translator")
window.geometry("1200x900")

# ------------------ TRANSLATED VARIABLE ------------------
translated = tk.StringVar(window, value="Gig 'Em!")  # attach to window

# ------------------ IMAGE MAP ------------------
IMAGE_MAP = {
    "...": "images/Question.png",
    "Gig 'Em!": "images/GigEm.png",
    "Wave": "images/Wave.jpg", 
    "Peace!": "images/Peace.png",
    "No" : "images/No.jpg"
    }

# ------------------ IMAGE UPDATE FUNCTION ------------------
def update_translation(*args):
    word = translated.get()

    if word in IMAGE_MAP:
        img = Image.open(IMAGE_MAP[word])
        img = img.resize((300, 300))
        tk_img = ImageTk.PhotoImage(img)

        image_label.config(image=tk_img)
        image_label.image = tk_img
    else:
        image_label.config(image="")
        image_label.image = None

# Attach trace
translated.trace_add("write", update_translation)
data_queue = q.Queue()

def data_reading():
    for i  in main.main():
        data_queue.put(i)

def poll_translation():
    
    if not data_queue.empty():
        translated.set(data_queue.get())
        print(data_queue.get())

    window.after(1, poll_translation)


# ------------------ FADE-IN FUNCTION ------------------
def fade_in_text(widget, start=0, end=1.0, step=0.05, delay=50):
    alpha = start

    def step_fade():
        nonlocal alpha
        alpha += step
        if alpha > end:
            alpha = end

        r_fg, g_fg, b_fg = (139, 0, 0)
        r_bg, g_bg, b_bg = (255, 239, 213)

        r = int(r_bg + (r_fg - r_bg) * alpha)
        g = int(g_bg + (g_fg - g_bg) * alpha)
        b = int(b_bg + (b_fg - b_bg) * alpha)

        widget.config(foreground=f"#{r:02x}{g:02x}{b:02x}")

        if alpha < end:
            widget.after(delay, step_fade)

    step_fade()


# ------------------ STARTUP SCREENS ------------------
def show_welcome():
    startup.destroy()
    global welcome
    welcome = tk.Label(
        window,
        text="Welcome!",
        font=("Segoe UI", 150),
        background="#FFEFD5",
        foreground="#FFEFD5"
    )
    welcome.place(relx=0.5, rely=0.5, anchor="center")
    fade_in_text(welcome)


def show_translate():
    welcome.destroy()
    translating = tk.Label(
        window,
        text="Translating in Progress...",
        font=("Segoe UI", 25),
        background="#FFEFD5",
        foreground="#8B0000"
    )
    translating.place(relx=0.001, rely=0.01)


# ------------------ TRANSLATION DISPLAY ------------------
def translation():
    global translation_label, image_label

    translation_label = tk.Label(
        window,
        textvariable=translated,
        font=("Arial", 125),
        background="#FFEFD5",
        foreground="#8B0000"
    )
    translation_label.place(relx=0.5, rely=0.5, anchor="center")

    title = tk.Label(
        window,
        text="Digi-Speak",
        font=("Arial", 50),
        background="#FFEFD5",
        foreground="#8B0000"
    )
    title.place(relx=0.5, rely=0.35, anchor="center")

    image_label = tk.Label(window, bg="#FFEFD5")
    image_label.place(relx=0.38, rely=0.65)

    update_translation()


# ------------------ PIXEL ART ------------------
def pixel_art():
    pixel_size = 15
    rows = 22
    cols = 22

    canvas_width = cols * pixel_size
    canvas_height = rows * pixel_size

    tomato_canvas = tk.Canvas(
        window,
        width=canvas_width,
        height=canvas_height,
        highlightthickness=0
    )
    tomato_canvas.place(relx=1, rely=0.035, anchor='ne', x=-10, y=10)

    art = [
        ["W","W","W","B","B","B","B","W","F","F","W","W","W","G","G","B","B","B","B","W","W","W"],
        ["W","W","B","B","R","R","R","B","W","F","F","F","D","G","B","R","R","R","B","B","W","W"],
        ["W","B","B","R","R","M","R","F","F","F","F","D","D","G","G","R","M","R","R","B","B","W"],
        ["B","B","R","R","M","M","R","R","F","F","D","D","G","G","R","R","M","M","R","R","B","B"],
        ["B","R","R","M","M","M","R","R","F","D","D","D","G","R","R","R","M","M","M","R","R","B"],
        ["B","R","R","M","M","M","R","F","R","D","D","G","G","G","G","R","M","M","M","R","R","B"],
        ["B","R","R","R","R","R","R","F","R","R","R","R","R","R","G","R","R","R","R","R","R","B"],
        ["B","R","R","R","R","R","R","R","R","R","R","R","R","R","R","R","R","R","R","R","R","B"],
        ["B","R","B","B","R","R","R","R","R","R","R","R","R","R","R","R","R","R","B","B","R","B"],
        ["B","R","R","B","B","R","R","B","R","R","R","R","R","R","B","R","R","B","B","R","R","B"],
        ["B","R","R","R","R","B","R","R","R","R","R","R","R","R","R","R","B","R","R","R","R","B"],
        ["B","R","R","B","R","R","R","B","R","R","B","B","R","R","B","R","R","R","B","R","R","B"],
        ["B","R","R","B","B","R","R","R","B","B","R","R","B","B","R","R","R","B","B","R","R","B"],
        ["B","R","R","R","B","B","R","R","R","R","R","R","R","R","R","R","B","B","R","R","R","B"],
        ["B","R","R","R","R","R","R","R","R","R","R","R","R","R","R","R","R","R","R","R","R","B"],
        ["B","R","R","R","R","R","R","R","R","R","R","R","R","R","R","R","R","R","R","R","R","B"],
        ["B","R","R","R","R","R","R","R","R","R","R","R","R","R","R","R","R","R","R","R","R","B"],
        ["B","B","R","R","R","R","R","R","R","R","R","R","R","R","R","R","R","R","R","R","B","B"],
        ["W","B","B","R","R","R","R","R","R","R","R","R","R","R","R","R","R","R","R","B","B","W"],
        ["W","W","B","B","M","M","R","R","M","M","R","R","M","M","R","R","M","M","B","B","W","W"],
        ["W","W","W","B","B","B","M","M","B","B","B","B","B","B","M","M","B","B","B","W","W","W"],
        ["W","W","W","W","W","W","B","B","W","W","W","W","W","W","B","B","W","W","W","W","W","W"],
    ]

    color_map = {
        "R": "#ff0000",
        "W": "#FFEFD5",
        "B": "#000000",
        "G": "#32CD32",
        "D": "#228B22",
        "F": "#006400",
        "M": "#8B0000",
    }

    for y, row in enumerate(art):
        for x, color_key in enumerate(row):
            x1 = x * pixel_size
            y1 = y * pixel_size
            x2 = x1 + pixel_size
            y2 = y1 + pixel_size
            tomato_canvas.create_rectangle(
                x1, y1, x2, y2,
                fill=color_map[color_key],
                outline=""
            )



if __name__ == "__main__":
    # ------------------ STARTUP LABEL ------------------
    startup = tk.Label(
        window,
        text="Starting...",
        font=("Arial", 150),
        background="#FFEFD5",
        foreground="#FFEFD5"
    )
    startup.place(relx=0.5, rely=0.5, anchor="center")
    fade_in_text(startup)

    # ------------------ TIMING FLOW ------------------
    window.after(1500, show_welcome)
    window.after(3000, show_translate)
    window.after(3000, pixel_art)
    window.after(3000, translation)

    thread1 = t.Thread(target=data_reading, args=())
    thread2 = t.Thread(target=poll_translation, args=())

    thread1.start()
    thread2.start()

    window.mainloop()
