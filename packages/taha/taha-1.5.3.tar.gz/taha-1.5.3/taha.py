import pygame
import webbrowser
import pyttsx3
import pyperclip
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
import builtins
import tkinter as tk
from PIL import Image
import requests
from tkinter import colorchooser
import turtle as t
import random as ra
import time
import playsound
from pydub import AudioSegment
import os
from PIL import Image, Image
from gtts import gTTS
import os
from pathlib import Path
from gtts import gTTS, lang as gtts_langs
import pygame
import time
from pathlib import Path
import os
from gtts import gTTS, lang as gtts_langs
from pathlib import Path
import ctypes
import speech_recognition as sr
import platform
import psutil
import socket
import datetime
import pytz
import random
import string
def get_system_summary():
    try:
        os_info = platform.system() + " " + platform.release()
        cpu_info = platform.processor()
        ram_info = f"{round(psutil.virtual_memory().total / (1024**3))} GB"
        python_ver = platform.python_version()
        ip = socket.gethostbyname(socket.gethostname())
        tz = datetime.datetime.now(pytz.timezone("Asia/Tehran")).tzname()
        return {
            "os": os_info,
            "cpu": cpu_info,
            "ram": ram_info,
            "python_version": python_ver,
            "ip_address": ip,
            "timezone": tz
        }
    except Exception as e:
        return {"error": str(e)}

def generate_password(length=12, strength="strong"):
    if strength == "simple":
        chars = string.ascii_lowercase
    elif strength == "medium":
        chars = string.ascii_letters + string.digits
    else:
        chars = string.ascii_letters + string.digits + string.punctuation

    return ''.join(random.choice(chars) for _ in range(length))
def speech_to_text(timeout=5, phrase_time_limit=10, language="fa-IR"):
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("🎙️ لطفاً صحبت کنید...")
        audio = recognizer.listen(source, timeout=timeout, phrase_time_limit=phrase_time_limit)
        try:
            text = recognizer.recognize_google(audio, language=language)
            return text
        except sr.UnknownValueError:
            return "❌ گفتار قابل تشخیص نبود"
        except sr.RequestError:
            return "⚠️ خطا در اتصال به سرویس گوگل"
def speak(text, lang="auto"):
    # تشخیص زبان
    if lang == "auto":
        lang = "fa" if any('\u0600' <= ch <= '\u06FF' for ch in text) else "en"

    # بررسی پشتیبانی gTTS
    supported_langs = gtts_langs.tts_langs()
    if lang not in supported_langs:
        fallback = "ar" if lang == "fa" else "en"
        print(f"[!] زبان '{lang}' توسط gTTS پشتیبانی نمی‌شود. استفاده از جایگزین: '{fallback}'")
        lang = fallback

    # ساخت فایل با نام جديد
    downloads = get_downloads_dir()
    downloads.mkdir(parents=True, exist_ok=True)
    filename = get_unique_filename(base_name="voice", ext=".mp3", folder=downloads)

    tts = gTTS(text=text, lang=lang)
    tts.save(str(filename))
    pygame.mixer.init()
    pygame.mixer.music.load(str(filename))
    pygame.mixer.music.set_volume(1.0)
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy():
        time.sleep(0.1)
def browser(url):
    webbrowser.open(url)
def run_app(path):
    try:
        os.startfile(path)
    except Exception as e:
        print(FileNotFoundError ("TahaError:", e))
def get_file_size(path: str):
    size = os.path.getsize(path)
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size < 1024:
            return f"{size:.2f} {unit}"
        size /= 1024
def count_words(text: str):
    return len(text.strip().split())
def get_day_name(date_str: str):
    date_obj = datetime.datetime.strptime(date_str, "%Y-%m-%d")
    return date_obj.strftime("%A")

def get_downloads_dir():
    return Path(os.path.expanduser("~/Downloads"))

def system(action):
    """action :
            sleep
            shut_down
            log_out
            restart
            """
    if action == "shut_down":
        os.system("shutdown /s /t 0")
    elif action == "restart":
        os.system("shutdown /r /t")
    elif action == "log_out":
        os.system("shutdown -1")
    elif action == "sleep":
        os.system("rundll32.exe powrprof.dll,SetSuspendState 0,1,0")
def copy_text(text):
    pyperclip.copy(text)
def save_var(local_or_name, value):
    with open (local_or_name, "w") as f:
        f.write(str(value))
def load_var(local_or_name, default=None):
    try:
        with open(local_or_name, "r") as f:
            data = f.read().strip()
            if data == "":
                return default
            return data
    except FileNotFoundError:
        return default
def ri (a, b):
    return ra.randint(a, b)
def key (a, b):
    t.listen()
    t.onkeypress(a, b)
def click(a):
    t.onscreenclick(a)
def getcolor(tit):
    return colorchooser.askcolor(title = tit)
def rc (a):
    return ra.choice(a)

def leftclick (a):
    t.onscreenclick(a, btn = 1)
def middleclick (a):
    t.onscreenclick(a, btn = 2)
def rightclick (a):
    t.onscreenclick(a, btn = 3)
def move (x, y):
    t.goto(x, y)
def randcolor():
    t.colormode(255)
    r = ra.randint(1, 255)
    g = ra.randint(1, 255)
    b = ra.randint(1, 255)
    t.color ((r, g, b))
def rgbcolor(r, g, b):
    t.colormode(255)
    t.color ((r, g, b))
def getping(url):
    start = time.time()
    requests.get(url)
    end = time.time()
    return round((end - start)* 1000)
def mouseX ():
    screen = t.Screen()
    return screen.cv.winfo_pointerx() - screen.cv.winfo_rootx() - screen.window_width() // 2
def mouseY():
    screen = t.Screen()
    return screen.window_height() // 2 - (screen.cv.winfo_pointery() - screen.cv.winfo_rooty())
def hidecursor():
    ctypes.windll.user32.ShowCursor(False)
def showcursor():
    ctypes.windll.user32.ShowCursor(True)
def shapecursor(a):
    root = tk.Tk()
    root.config (cursor = a)
    root.mainloop()
def convert_jpg(your_format, your_picture_name, your_image_path_or_name):
    img = Image.open(your_image_path_or_name)
    img.save(f"{your_picture_name}.{your_format}")
def upload_gif(NameOrPath, sizeWidth, sizeHight):
    screen = t.Screen()
    screen.register_shape(NameOrPath)
    img = Image.open(NameOrPath)
    img = img.resize((sizeWidth, sizeHight))
    img_turtle = t.Turtle()
    img_turtle.shape(NameOrPath)
    img_turtle.penup()
    img_turtle.goto(0, 0)
    return img_turtle
def show_picture():
    img_turtle.showturtle()
def hide_picture():
    img_turtle.hideturtle()

def play_mp3(path):
    pygame.mixer.init()
    pygame.mixer.music.load(path)
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy():
        time.sleep(0.1)

def text_to_speech(text):
    engine = pyttsx3.init()
    voices = engine.getProperty('voices')
    engine.setProperty('voice', voices[0].id)
    engine.setProperty('rate', 150)
    engine.say(text)
    engine.runAndWait()
import os

def search_real_usage(keyword, path):
    ignore_patterns = [
        f'def search_keyword_in_project',
        f'search_keyword_in_project("{keyword}"',
        f'search_real_usage("{keyword}"'
    ]

    for root, dirs, files in os.walk(path):
        for file in files:
            if file.endswith(".py"):
                full_path = os.path.join(root, file)
                with open(full_path, encoding="utf-8", errors="ignore") as f:
                    for i, line in enumerate(f, start=1):
                        line_stripped = line.strip()
                        if keyword in line_stripped and not any(p in line_stripped for p in ignore_patterns):
                            print(f"📍 Found in {full_path}, line {i}:\n  {line_stripped}")

def get_downloads_dir():
    return Path(os.path.expanduser("~/Downloads"))

def get_downloads_dir():
    return Path(os.path.expanduser("~/Downloads"))

def get_unique_filename(base_name="voice", ext=".mp3", folder=None):
    folder = folder or get_downloads_dir()
    i = 0
    while True:
        filename = folder / f"{base_name}_{i}{ext}"
        if not filename.exists():
            return filename
        i += 1

def clock(unit):
    """hour or minute or second or microseconde"""
    from datetime import datetime
    now = datetime.now()
    if unit == "hour":
        return now.hour
    elif unit == "minute":
        return now.minute
    elif unit == "second":
        return now.second
    elif unit == "microsecond":
        return now.microsecond
    else:
        return "Invalid unit"
__all__ = [
    "text_to_speech", "randcolor", "rgbcolor", "upload_gif", "search_real_usage", "showcursor","count_words", "get_day_name", "get_system_summary",
    "save_var", "load_var", "getping", "clock", "mouseX", "mouseY","hidecursor", "speak","shapecursor","run_app", "get_file_size", "generate_password",
    "key", "click", "getcolor", "rc", "ri", "leftclick", "middleclick", "rightclick", "play_mp3", "system", "copy_text", "browser", "speech_to_text", "speak"
]
