# Real-Time-Audio-Video-Call-Translation-System

A **Real-Time Voice Translator** built with Python that captures speech through a microphone, converts it into text using **Vosk Speech Recognition**, translates the detected speech into a selected Indian language, displays live subtitles over the webcam feed, and speaks the translated text using **Edge TTS / Google TTS**.

The application provides a simple **Tkinter desktop GUI** with real-time camera visualization and translation controls.

---

## 🚀 Features

* 🎤 Real-time microphone speech recognition
* 🧠 Offline speech recognition using **Vosk**
* 🌐 Automatic source-language detection using `langdetect`
* 🔄 Text translation using **MyMemory Translation API**
* 🗣️ Text-to-Speech using **Microsoft Edge TTS**
* 🔊 Google TTS fallback when Edge TTS is unavailable
* 📹 Live webcam video feed
* 💬 Live subtitles displayed directly on the camera
* 🇮🇳 Supports multiple Indian languages
* 🖥️ Dark-themed Tkinter desktop interface
* 🔤 Unicode font support using **Noto Sans**
* ⏯️ Start/Stop translation controls
* 🧵 Speech recognition runs in a separate thread so the GUI remains responsive

---

## 🌐 Supported Languages

| Code | Language  |
| ---- | --------- |
| `en` | English   |
| `kn` | Kannada   |
| `hi` | Hindi     |
| `ta` | Tamil     |
| `te` | Telugu    |
| `ml` | Malayalam |
| `mr` | Marathi   |
| `gu` | Gujarati  |
| `bn` | Bengali   |
| `pa` | Punjabi   |

Select the desired target language from the dropdown menu.

---

## 🏗️ Project Architecture

```text
                 🎤 Microphone
                       │
                       ▼
              ┌─────────────────┐
              │  SoundDevice    │
              │ Audio Recording │
              └────────┬────────┘
                       │
                       ▼
              ┌─────────────────┐
              │      Vosk       │
              │ Speech-to-Text  │
              └────────┬────────┘
                       │
                       ▼
              ┌─────────────────┐
              │   LangDetect    │
              │ Detect Language │
              └────────┬────────┘
                       │
                       ▼
              ┌─────────────────┐
              │    MyMemory     │
              │   Translation   │
              └────────┬────────┘
                       │
             ┌─────────┴─────────┐
             ▼                   ▼
      💬 Live Subtitle       🔊 TTS Output
             │                   │
             ▼                   ▼
       📹 Webcam Feed      Edge TTS / gTTS
```

---

## 🛠️ Technologies Used

### Programming Language

* Python 3

### Speech Recognition

* Vosk
* SoundDevice
* SciPy

### Translation

* MyMemory Translation API
* LangDetect

### Text-to-Speech

* Microsoft Edge TTS
* Google Text-to-Speech (`gTTS`)
* `playsound`

### Computer Vision

* OpenCV
* NumPy

### GUI

* Tkinter
* ttk

### Image Processing

* Pillow

---

## 📁 Project Structure

```text
Real-Time-Voice-Translator/
│
├── translator.py
├── README.md
├── requirements.txt
│
├── NotoSans-Regular.ttf
│
├── vosk-model-small-en-us-0.15/
│   ├── am/
│   ├── conf/
│   ├── graph/
│   ├── ivector/
│   └── README
│
└── .gitignore
```

> Rename your Python file to `translator.py` or replace the name above with your actual filename.

---

## ⚙️ Installation

### 1. Clone the Repository

```bash
git clone https://github.com/YOUR_USERNAME/Real-Time-Voice-Translator.git
```

Move into the project directory:

```bash
cd Real-Time-Voice-Translator
```

---

### 2. Create a Virtual Environment

Windows:

```bash
python -m venv venv
```

Activate it:

```bash
venv\Scripts\activate
```

Linux/macOS:

```bash
python3 -m venv venv
source venv/bin/activate
```

---

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

If you don't have `requirements.txt`, install the dependencies manually:

```bash
pip install requests langdetect sounddevice scipy vosk edge-tts playsound gTTS opencv-python numpy pillow
```

---

## 🧠 Vosk Model Setup

The application uses:

```text
vosk-model-small-en-us-0.15
```

Download the **Vosk small English model** and extract it into the project directory.

Your folder should look like:

```text
Real-Time-Voice-Translator/
│
├── translator.py
│
└── vosk-model-small-en-us-0.15/
    ├── am/
    ├── conf/
    ├── graph/
    └── ivector/
```

The code searches for:

```python
model_path = "vosk-model-small-en-us-0.15"
```

If the folder is missing, speech recognition will not work.

---

## 🔤 Unicode Font

The application uses:

```text
NotoSans-Regular.ttf
```

to display Indian-language subtitles.

The program automatically attempts to download the font if it is not already present.

This allows subtitles such as:

```text
ನಮಸ್ಕಾರ
नमस्ते
வணக்கம்
నమస్కారం
നമസ്കാരം
નમસ્તે
ਸਤ ਸ੍ਰੀ ਅਕਾਲ
```

to be displayed correctly.

---

## ▶️ Running the Application

Run:

```bash
python translator.py
```

The application opens a desktop window containing:

```text
┌─────────────────────────────────────────────┐
│                                             │
│              📹 CAMERA FEED                 │
│                                             │
│ You said: hello                             │
│ Translated: ನಮಸ್ಕಾರ                        │
│                                             │
├─────────────────────────────────────────────┤
│ Target Language: [ en ▼ ]                   │
│                                             │
│ [ Start Translation ] [ Stop ]              │
│                                             │
│ Status: Listening...                        │
└─────────────────────────────────────────────┘
```

---

## 🎯 How It Works

### Step 1 — Camera Initialization

OpenCV initializes the computer's default webcam:

```python
cap = cv2.VideoCapture(0)
```

The webcam feed is continuously displayed inside the Tkinter window.

---

### Step 2 — Start Translation

When the user clicks:

```text
Start Translation
```

a separate recognition thread is started.

```python
recognition_thread = threading.Thread(
    target=recognition_loop,
    daemon=True
)
```

Using a separate thread prevents the GUI from freezing while recording audio.

---

### Step 3 — Record Speech

The application records approximately 4 seconds of audio:

```python
audio = sd.rec(
    int(duration * fs),
    samplerate=fs,
    channels=1,
    dtype="int16"
)
```

The sampling rate is:

```text
16000 Hz
```

---

### Step 4 — Speech Recognition

Vosk processes the recorded audio and converts speech into text.

Example:

```text
🎤 User speaks:
"Hello, how are you?"
```

Vosk produces:

```text
Hello how are you
```

---

### Step 5 — Detect Source Language

The application uses:

```python
detect(text)
```

from `langdetect` to identify the source language.

For example:

```text
Hello → English
```

---

### Step 6 — Translate

The detected text is sent to the MyMemory Translation API.

Example:

```text
English
   ↓
"Hello"
   ↓
Kannada
   ↓
"ನಮಸ್ಕಾರ"
```

---

### Step 7 — Display Subtitles

The original and translated text are displayed over the webcam feed.

```text
You said: Hello

Translated: ನಮಸ್ಕಾರ
```

A black subtitle background is used to improve readability.

---

### Step 8 — Text-to-Speech

The translated sentence is converted into speech.

The application first tries **Edge TTS** for supported languages.

If Edge TTS is unavailable, it falls back to:

```text
Google TTS
```

The translated sentence is then played through the computer's speakers.

---

## 🔊 Text-to-Speech Flow

```text
Translated Text
       │
       ▼
  Edge TTS Available?
     /        \
   Yes         No
   │            │
   ▼            ▼
Edge TTS      Google TTS
   │            │
   └──────┬─────┘
          ▼
      🔊 Speaker
```

Currently, Edge TTS voices are configured for:

```python
"en": "en-US-AriaNeural"
"hi": "hi-IN-MadhurNeural"
```

Other supported languages use Google TTS as the fallback.

---

## 🖥️ GUI Components

The application contains:

### Camera Display

Displays the live webcam feed.

### Target Language

Allows the user to select the target language.

### Start Translation

Starts continuous speech recognition and translation.

### Stop

Stops the translation loop.

### Status

Shows the current application state:

```text
Status: Idle
```

or:

```text
Status: Listening...
```

or:

```text
Status: Stopped
```

---

## 📦 requirements.txt

Create a file named:

```text
requirements.txt
```

and add:

```text
requests
langdetect
sounddevice
scipy
vosk
edge-tts
playsound
gTTS
opencv-python
numpy
Pillow
```

Install everything using:

```bash
pip install -r requirements.txt
```

---

## ⚠️ Common Problems

### 1. Camera Not Opening

If you see:

```text
Unable to access camera.
```

Check:

* Camera permissions
* Whether another application is using the camera
* Windows camera settings
* Webcam connection

You can also try:

```python
cap = cv2.VideoCapture(1)
```

instead of:

```python
cap = cv2.VideoCapture(0)
```

---

### 2. Vosk Model Not Found

If you see:

```text
Vosk model folder not found
```

make sure this folder exists:

```text
vosk-model-small-en-us-0.15
```

and that it is located in the same directory as your Python program.

---

### 3. Microphone Not Working

Check available audio devices:

```python
import sounddevice as sd

print(sd.query_devices())
```

Then select the correct microphone if necessary.

---

### 4. Indian Language Characters Not Displaying

Make sure:

```text
NotoSans-Regular.ttf
```

exists in the project directory.

The application automatically attempts to download it if it is missing.

---

### 5. Translation Error

The application requires an internet connection because MyMemory Translation API is used.

If the API cannot be reached, the program displays:

```text
Translation error!
```

---

### 6. Text-to-Speech Error

Edge TTS and Google TTS require internet connectivity.

Check your internet connection if speech output is not working.

---

## 🔒 Privacy

The application processes microphone audio locally through Vosk for speech recognition.

However, translation and some text-to-speech operations use online services.

Therefore:

* Do not use sensitive/private conversations without reviewing the third-party service policies.
* Internet connectivity is required for translation.
* Audio should not be assumed to remain entirely offline because the overall application uses online services.

---

## 🔮 Future Improvements

Possible improvements include:

* 🌍 Automatic target-language selection
* 🎤 Continuous streaming speech recognition
* ⚡ Lower translation latency
* 🗣️ More Edge TTS voices
* 📱 Android/mobile version
* 💻 Web-based version
* 📞 Audio call translation
* 📹 Video call translation
* 👥 Multi-user translation
* 🔊 Voice activity detection
* 📝 Translation history
* 💾 Save translated conversations
* 🎧 Bluetooth headset support
* 🌐 Offline translation models
* 🤖 AI-powered contextual translation
* 🔤 Improved subtitle wrapping for long sentences

---

## 💡 Use Cases

This project can be useful for:

* 🧑‍🎓 Students learning languages
* 🧳 Travelers
* 🗣️ Multilingual communication
* 🏫 Educational environments
* 🏢 Business communication
* 👨‍👩‍👧 Communication between people speaking different languages
* 🇮🇳 Communication across Indian regional languages

---

## 📸 Application Workflow

```text
Launch Application
       ↓
Open Webcam
       ↓
Select Target Language
       ↓
Click "Start Translation"
       ↓
Record Voice
       ↓
Speech → Text
       ↓
Detect Source Language
       ↓
Translate Text
       ↓
Display Subtitle
       ↓
Translated Text → Speech
       ↓
Play Audio
       ↓
Repeat
```

---

## 👨‍💻 Author

**Umesh BN**

Information Science & Engineering
Student Developer

---

## ⭐ Contributing

Contributions are welcome!

1. Fork the repository
2. Create a new branch

```bash
git checkout -b feature/new-feature
```

3. Make your changes
4. Commit your changes

```bash
git commit -m "Add new translation feature"
```

5. Push the branch

```bash
git push origin feature/new-feature
```

6. Create a Pull Request

---

## 📄 License

This project is intended for educational and development purposes.

You may modify and extend the project according to your requirements.

---

## ⭐ If You Like This Project

If you find this project useful, consider giving the repository a ⭐ on GitHub!

**Real-Time Voice Translator — Breaking Language Barriers with AI and Speech Technology.** 🎙️🌍
