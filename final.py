import os
import json
import uuid
import threading
import urllib.request
import asyncio

import requests
from langdetect import detect
import urllib.parse

import sounddevice as sd
import scipy.io.wavfile as wav
from vosk import Model, KaldiRecognizer

import edge_tts
from playsound import playsound
from gtts import gTTS

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageTk

import tkinter as tk
from tkinter import ttk, messagebox


# -----------------------------------
# AUTO DOWNLOAD UNICODE FONT
# -----------------------------------
def ensure_font_exists():
    font_name = "NotoSans-Regular.ttf"
    font_url = "https://gw.alipayobjects.com/os/bmw-prod/16c55b09-a65f-4d1c-a3c5-8ceb2bc67b06.ttf"

    if not os.path.exists(font_name):
        print("\n⬇️ Downloading Unicode font (NotoSans-Regular.ttf)...")
        try:
            urllib.request.urlretrieve(font_url, font_name)
            print("✔ Font downloaded successfully!\n")
        except Exception as e:
            print("❌ Font download failed:", e)
            print("⚠ Using default font (Indian languages may not render)")
            return None

    return font_name


def load_font():
    font_path = ensure_font_exists()

    if font_path is None:
        return ImageFont.load_default()

    try:
        # Bigger font for subtitles
        return ImageFont.truetype(font_path, 32)
    except Exception:
        print("⚠ Could not load font. Using default font.")
        return ImageFont.load_default()


FONT = load_font()


# -----------------------------------
# LANGUAGE SETTINGS (same as before)
# -----------------------------------
LANGUAGES = {
    "en": "English",
    "kn": "Kannada",
    "hi": "Hindi",
    "ta": "Tamil",
    "te": "Telugu",
    "ml": "Malayalam",
    "mr": "Marathi",
    "gu": "Gujarati",
    "bn": "Bengali",
    "pa": "Punjabi"
}

EDGE_VOICES = {
    "en": "en-US-AriaNeural",
    "hi": "hi-IN-MadhurNeural",
}


# -----------------------------------
# GLOBAL STATE
# -----------------------------------
camera_running = True
listening = False
subtitle_spoken = ""
subtitle_translated = ""
cap = None  # OpenCV VideoCapture
recognition_thread = None


# -----------------------------------
# TTS SYSTEM (unchanged logic)
# -----------------------------------
async def edge_tts_safe(text, voice):
    filename = f"voice_{uuid.uuid4().hex}.mp3"
    try:
        await edge_tts.Communicate(text, voice).save(filename)
        return filename
    except:
        return None


def google_tts(text, lang):
    filename = f"google_{uuid.uuid4().hex}.mp3"
    gTTS(text=text, lang=lang).save(filename)
    return filename


def speak(text, lang):
    text = text.strip()
    if not text:
        return

    # Try Edge TTS
    if lang in EDGE_VOICES:
        filename = asyncio.run(edge_tts_safe(text, EDGE_VOICES[lang]))
        if filename:
            playsound(filename)
            os.remove(filename)
            return

    # Fallback to Google TTS
    filename = google_tts(text, lang)
    playsound(filename)
    os.remove(filename)


# -----------------------------------
# TRANSLATION FUNCTION (same as before)
# -----------------------------------
def translate_text(text, target_lang):
    try:
        src = detect(text) if len(text) > 2 else "en"
        encoded = urllib.parse.quote(text)
        url = (
            f"https://api.mymemory.translated.net/get?"
            f"q={encoded}&langpair={src}|{target_lang}"
        )
        data = requests.get(url).json()
        return data["responseData"]["translatedText"]
    except:
        return "Translation error!"


# -----------------------------------
# SPEECH RECOGNITION (VOSK) (same as before)
# -----------------------------------
def record_and_recognize(duration=4):
    print("\n🎤 Listening...")
    fs = 16000

    audio = sd.rec(int(duration * fs), samplerate=fs, channels=1, dtype="int16")
    sd.wait()
    wav.write("voice_input.wav", fs, audio)

    model_path = "vosk-model-small-en-us-0.15"
    if not os.path.exists(model_path):
        print(f"❌ Vosk model folder not found at: {model_path}")
        return ""

    model = Model(model_path)
    recognizer = KaldiRecognizer(model, fs)

    with open("voice_input.wav", "rb") as f:
        recognizer.AcceptWaveform(f.read())
        result = json.loads(recognizer.Result())
        return result.get("text", "")


# -----------------------------------
# CAMERA + SUBTITLE RENDERING
# -----------------------------------
def update_camera_frame():
    global cap, subtitle_spoken, subtitle_translated, camera_running

    if cap is None or not cap.isOpened():
        root.after(30, update_camera_frame)
        return

    ret, frame = cap.read()
    if not ret:
        root.after(30, update_camera_frame)
        return

    # Convert frame to PIL image
    pil_img = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
    draw = ImageDraw.Draw(pil_img)

    width, height = pil_img.size

    # Black bar at top for subtitles
    bar_height = 100
    draw.rectangle([(0, 0), (width, bar_height)], fill=(0, 0, 0))

    y = 10

    def draw_bold_text(pos, text, color):
        x, yy = pos
        draw.text((x, yy), text, font=FONT, fill=color)
        draw.text((x + 1, yy), text, font=FONT, fill=color)

    if subtitle_spoken:
        draw_bold_text(
            (10, y),
            f"You said: {subtitle_spoken}",
            (0, 255, 0)
        )
        y += 40

    if subtitle_translated:
        draw_bold_text(
            (10, y),
            f"Translated: {subtitle_translated}",
            (255, 255, 0)
        )

    # Convert back to OpenCV image, then to ImageTk
    frame = cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)
    img = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
    imgtk = ImageTk.PhotoImage(image=img)

    video_label.imgtk = imgtk
    video_label.configure(image=imgtk)

    if camera_running:
        root.after(30, update_camera_frame)


# -----------------------------------
# RECOGNITION LOOP (runs in separate thread)
# -----------------------------------
def recognition_loop():
    global listening, subtitle_spoken, subtitle_translated

    while listening:
        text = record_and_recognize()
        if not text.strip():
            continue

        subtitle_spoken = text
        target_lang = lang_var.get() or "en"
        translated = translate_text(text, target_lang)
        subtitle_translated = translated

        speak(translated, target_lang)


# -----------------------------------
# GUI CONTROL CALLBACKS
# -----------------------------------
def start_translation():
    global listening, recognition_thread

    if listening:
        return

    listening = True
    recognition_thread = threading.Thread(target=recognition_loop, daemon=True)
    recognition_thread.start()
    status_var.set("Status: Listening...")


def stop_translation():
    global listening
    listening = False
    status_var.set("Status: Stopped")


def on_close():
    global camera_running, listening, cap
    listening = False
    camera_running = False
    if cap is not None and cap.isOpened():
        cap.release()
    root.destroy()


# -----------------------------------
# TKINTER GUI SETUP (Dark Theme)
# -----------------------------------
root = tk.Tk()
root.title("Real-Time Voice Translator")
root.configure(bg="#111111")

# Window size
root.geometry("900x700")

# Top frame for video
video_frame = tk.Frame(root, bg="#111111")
video_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

video_label = tk.Label(video_frame, bg="#000000")
video_label.pack(fill=tk.BOTH, expand=True)

# Bottom control panel
control_frame = tk.Frame(root, bg="#111111")
control_frame.pack(fill=tk.X, padx=10, pady=10)

# Language selector
lang_label = tk.Label(
    control_frame,
    text="Target Language:",
    bg="#111111",
    fg="#ffffff",
    font=("Segoe UI", 11)
)
lang_label.grid(row=0, column=0, padx=5, pady=5, sticky="w")

lang_var = tk.StringVar(value="en")
lang_menu = ttk.Combobox(
    control_frame,
    textvariable=lang_var,
    values=list(LANGUAGES.keys()),
    state="readonly"
)
lang_menu.grid(row=0, column=1, padx=5, pady=5, sticky="w")
lang_menu.current(0)

# Start / Stop buttons
style = ttk.Style()
style.theme_use("clam")
style.configure(
    "TButton",
    font=("Segoe UI", 11, "bold"),
    foreground="#ffffff",
    background="#333333",
    padding=6
)
style.map(
    "TButton",
    background=[("active", "#555555")]
)

start_button = ttk.Button(control_frame, text="Start Translation", command=start_translation)
start_button.grid(row=0, column=2, padx=10, pady=5)

stop_button = ttk.Button(control_frame, text="Stop", command=stop_translation)
stop_button.grid(row=0, column=3, padx=10, pady=5)

# Status label
status_var = tk.StringVar(value="Status: Idle")
status_label = tk.Label(
    control_frame,
    textvariable=status_var,
    bg="#111111",
    fg="#aaaaaa",
    font=("Segoe UI", 10)
)
status_label.grid(row=1, column=0, columnspan=4, sticky="w", padx=5, pady=5)

# Camera init
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    messagebox.showerror("Camera Error", "Unable to access camera.")
else:
    update_camera_frame()

root.protocol("WM_DELETE_WINDOW", on_close)

root.mainloop()