import speech_recognition as sr
import requests
import piper
import sounddevice as sd
import numpy as np
import time
import librosa
from datetime import datetime

# ---------------------------------------------------------
#  PIPER TTS (Python API)
# ---------------------------------------------------------
VOICE_PATH = r"C:\Users\corin\OneDrive\Desktop\voices\piper\voices\en_GB-southern_english_female-low.onnx"

print("Loading Piper voice...")
model = piper.PiperVoice.load(VOICE_PATH)
print("Piper voice loaded.")

# ---------------------------------------------------------
#  SPEAK FUNCTION (clean, no edits)
# ---------------------------------------------------------
def stretch_audio(audio, factor):
    """Slow down audio without changing pitch."""
    return librosa.effects.time_stretch(y=audio, rate=factor)

def speak(text):
    """Speak text using Piper TTS with natural pacing."""

    # Add a tiny pause if the line is short (fixes fast numbers)
    if len(text) < 40:
        text = "... " + text

    # Add natural sentence pacing
    text = text.replace(". ", ".  ")

    chunks = []
    for chunk in model.synthesize(text):
        chunks.extend(chunk.audio_float_array)

    audio = np.array(chunks, dtype=np.float32)

    sd.play(audio, model.config.sample_rate)
    sd.wait()
    time.sleep(0.1)


# ---------------------------------------------------------
#  WAKE WORD LISTENER
# ---------------------------------------------------------
def listen_for_wake_word():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        # Short calibration, but not too short
        r.adjust_for_ambient_noise(source, duration=0.5)

        # These values are SAFE and won't trigger AssertionError
        r.energy_threshold = 80
        r.pause_threshold = 0.5
        r.non_speaking_duration = 0.3
        r.dynamic_energy_threshold = True

        print("Waiting for wake word: 'aria'...")
        audio = r.listen(source, phrase_time_limit=4)

    try:
        text = r.recognize_google(audio).lower()
        print("Heard:", text)
        return "aria" in text
    except:
        return False

# ---------------------------------------------------------
#  COMMAND LISTENER
# ---------------------------------------------------------
def listen_for_command():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        r.adjust_for_ambient_noise(source, duration=1.0)
        r.energy_threshold = 60
        r.pause_threshold = 1.2
        r.dynamic_energy_threshold = True

        print("Listening for command...")
        audio = r.listen(source, phrase_time_limit=15)

    try:
        text = r.recognize_google(audio).lower()
        print("Command:", text)
        return text
    except:
        return ""

# ---------------------------------------------------------
#  ARIA BRAIN (LLAMA3)
# ---------------------------------------------------------
def aria_brain(prompt):
    try:
        system_instructions = (
            "You are ARIA, a calm, confident, and direct personal assistant. "
            "You do not lecture, moralize, or correct the user. "
            "You respond in a cooperative, helpful, and non-judgmental way. "
            "You keep answers concise unless the user asks for detail. "
            "You follow the user's tone while staying respectful. "
            "Your purpose is to assist, not to judge.\n\n"
        )

        full_prompt = system_instructions + "User: " + prompt + "\nARIA:"

        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": "dolphin-llama3:8b",
                "prompt": full_prompt,
                "stream": False
            }
        )

        data = response.json()
        reply = data.get("response", "").strip()

        return reply

    except Exception as e:
        print("ERROR:", e)
        return "I am having trouble connecting to my AI systems."


# ---------------------------------------------------------
#  INTERNET SEARCH
# ---------------------------------------------------------
def web_search(query):
    try:
        url = "https://api.duckduckgo.com/"
        params = {
            "q": query,
            "format": "json",
            "no_html": 1,
            "skip_disambig": 1
        }
        r = requests.get(url, params=params)
        data = r.json()

        if data.get("AbstractText"):
            return data["AbstractText"]

        if data.get("RelatedTopics"):
            for item in data["RelatedTopics"]:
                if isinstance(item, dict) and "Text" in item:
                    return item["Text"]

        return "I couldn't find anything useful online."
    except:
        return "I couldn't access the internet."


# ---------------------------------------------------------
#  INTENT HELPERS
# ---------------------------------------------------------
def is_time_question(cmd):
    return any(p in cmd for p in [
        "what time is it",
        "tell me the time",
        "current time",
        "time right now"
    ])

def is_date_question(cmd):
    return any(p in cmd for p in [
        "what's the date",
        "what is the date",
        "today's date",
        "what day is it"
    ])

def is_search_intent(cmd):
    return any(t in cmd for t in [
        "search for",
        "look up",
        "who is",
        "what is",
        "tell me about"
    ])

def extract_search_query(cmd):
    for prefix in ["search for", "look up", "who is", "what is", "tell me about"]:
        if prefix in cmd:
            return cmd.replace(prefix, "").strip()
    return cmd.strip()


# ---------------------------------------------------------
#  MAIN LOOP
# ---------------------------------------------------------
speak("ARIA is online.")

while True:
    if not listen_for_wake_word():
        continue

    speak("Yes?")

    command = listen_for_command()
    if command == "":
        continue

    if "stop" in command or "shut down" in command:
        speak("Shutting down. Goodbye.")
        break

    if is_time_question(command):
        now = datetime.now().strftime("%I:%M %p")
        speak(f"The time is {now}.")
        continue

    if is_date_question(command):
        today = datetime.now().strftime("%A, %B %d, %Y")
        speak(f"Today is {today}.")
        continue

    if is_search_intent(command):
        query = extract_search_query(command)
        result = web_search(query)
        speak(result)
        continue

    response = aria_brain(command)
    speak(response)
