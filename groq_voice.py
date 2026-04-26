import time
import threading
import keyboard
import speech_recognition as sr
import pyaudio
from openai import OpenAI
import pyttsx3
import pyautogui

# Configuration
KEY_TO_HOLD = 'insert'
MODEL_NAME = "meta-llama/llama-4-scout-17b-16e-instruct"
GROQ_API_KEY = ""

client = OpenAI(base_url="https://api.groq.com/openai/v1", api_key=GROQ_API_KEY)

# Initialize speech recognition and text-to-speech
recognizer = sr.Recognizer()
microphone = sr.Microphone()

engine = pyttsx3.init()
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[0].id)
engine.setProperty('rate', 170)

# Flag to pause speech
pause_speaking = threading.Event()

# Text-to-speech function
def speak(text):
    """Speak text with conflict protection"""
    pause_speaking.set()
    try:
        engine.say(text)
        engine.runAndWait()
    except Exception as e:
        print(f"Speech synthesis error: {e}")
    finally:
        pause_speaking.clear()

# Command processing function
def process_command(text):
    """Send to Groq, speak response and execute actions"""
    try:
        print(f"→ Sending to Groq: {text}")

        resp = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {
                    "role": "system",
                    "content": "You are a witty, sarcastic assistant. Respond naturally with humor but stay on topic. If asked to open an application, say 'On it' and execute the command."
                },
                {"role": "user", "content": text}
            ],
            temperature=0.8,
            max_tokens=300
        )

        answer = resp.choices[0].message.content.strip()
        print(f"AI response: {answer}")
        speak(answer)

        answer_lower = answer.lower()

        if "open" in answer_lower:
            opened = False

            # Browsers
            if any(word in answer_lower for word in ["browser", "chrome", "google chrome"]):
                print("Opening Google Chrome...")
                pyautogui.hotkey('win')
                time.sleep(0.7)
                pyautogui.typewrite('chrome')
                pyautogui.press('enter')
                opened = True

            elif any(word in answer_lower for word in ["firefox"]):
                print("Opening Firefox...")
                pyautogui.hotkey('win')
                time.sleep(0.7)
                pyautogui.typewrite('firefox')
                pyautogui.press('enter')
                opened = True

            elif "tor" in answer_lower or "tor browser" in answer_lower:
                print("Opening Tor Browser...")
                pyautogui.hotkey('win')
                time.sleep(0.7)
                pyautogui.typewrite('tor')
                pyautogui.press('enter')
                opened = True

            # Messengers
            elif any(word in answer_lower for word in ["telegram", "tg"]):
                print("Opening Telegram...")
                pyautogui.hotkey('win')
                time.sleep(0.7)
                pyautogui.typewrite('telegram')
                pyautogui.press('enter')
                opened = True

            elif any(word in answer_lower for word in ["discord"]):
                print("Opening Discord...")
                pyautogui.hotkey('win')
                time.sleep(0.7)
                pyautogui.typewrite('discord')
                pyautogui.press('enter')
                opened = True

            # Other applications
            elif any(word in answer_lower for word in ["steam"]):
                print("Opening Steam...")
                pyautogui.hotkey('win')
                time.sleep(0.7)
                pyautogui.typewrite('steam')
                pyautogui.press('enter')
                opened = True

            elif any(word in answer_lower for word in ["spotify"]):
                print("Opening Spotify...")
                pyautogui.hotkey('win')
                time.sleep(0.7)
                pyautogui.typewrite('spotify')
                pyautogui.press('enter')
                opened = True

            elif any(word in answer_lower for word in ["vscode", "visual studio code", "code"]):
                print("Opening VS Code...")
                pyautogui.hotkey('win')
                time.sleep(0.7)
                pyautogui.typewrite('code')
                pyautogui.press('enter')
                opened = True

            if not opened:
                speak("I didn't understand which application to open. Please be more specific or check if it's installed.")
            else:
                speak("On it, give me a second...")

    except Exception as e:
        print(f"Groq error: {e}")
        speak("Oops, something broke in my brain... Please repeat.")

# Voice listener function
def voice_listener():
    """Thread: listens for key press and records speech when held"""
    while True:
        if keyboard.is_pressed(KEY_TO_HOLD):
            if pause_speaking.is_set():
                print("Waiting for AI to finish speaking...")
                pause_speaking.wait()

            print(f"[{KEY_TO_HOLD.upper()} held] Recording... Speak now!")

            try:
                with microphone as source:
                    recognizer.adjust_for_ambient_noise(source, duration=0.4)
                    audio = recognizer.listen(
                        source,
                        timeout=15,
                        phrase_time_limit=12
                    )

                print("Processing...")
                text = recognizer.recognize_google(audio, language="en-US")
                print(f"Heard: {text}")

                if text.strip():
                    process_command(text)
                else:
                    print("Empty phrase, skipping")

            except sr.WaitTimeoutError:
                print("You were silent for too long...")
            except sr.UnknownValueError:
                print("I didn't understand what you said")
                speak("I didn't catch that, could you repeat?")
            except sr.RequestError as e:
                print(f"Google Speech error: {e}")
                speak("No internet connection or speech recognition issue")
            except Exception as e:
                print(f"Recording/recognition error: {e}")
                speak("Something went wrong with the microphone...")

            print("Ready for next command")

        time.sleep(0.06)

# Main block
if __name__ == "__main__":
    print("Program started.")
    print(f"Hold the '{KEY_TO_HOLD.upper()}' key and speak.")
    print("Press Ctrl+C to exit.\n")

    listener_thread = threading.Thread(target=voice_listener, daemon=True)
    listener_thread.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nExiting...")
