import tkinter as tk
from PIL import Image, ImageTk
import threading as t
import queue as q
import main

data_queue = q.Queue()

def data_reading():
    for i  in main.main():
        data_queue.put(i)

def data_printing():
    while True:
        if not data_queue.empty():
            print(data_queue.get())

if __name__ == "__main__":
    thread1 = t.Thread(target=data_reading, args=())
    thread2 = t.Thread(target=data_printing, args=())

    thread1.start()
    thread2.start()

