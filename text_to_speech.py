import pyttsx3
import speech_recognition as sr


def speak(text):
    engine = pyttsx3.init()
    engine.setProperty('rate', 150)
    engine.setProperty('volume', 0.9)
    # Set the engine to use Microsoft Zira's voice
    for voice in engine.getProperty('voices'):
        if voice.id == "HKEY_LOCAL_MACHINE\\SOFTWARE\\Microsoft\\Speech\\Voices\\Tokens\\TTS_MS_EN-US_ZIRA_11.0":
            engine.setProperty('voice', voice.id)
            break

    engine.say(text)
    engine.runAndWait()


def listen_for_speech(prompt):
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        speak(prompt)
        recognizer.adjust_for_ambient_noise(source)
        try:
            audio = recognizer.listen(source, timeout=10, phrase_time_limit=5)
            return recognizer.recognize_google(audio)
        except sr.WaitTimeoutError:
            speak("I did not hear anything. Let's try again.")
        except sr.UnknownValueError:
            speak("I could not understand that. Let's try again.")
        except sr.RequestError as e:
            speak(f"Request failed; {e}")
        return None


def greeting(name):
    speak(f"Nice to meet you, {name}. Have a great day!")


def ask_person_name():
    name = None
    while name is None:
        name = listen_for_speech("What is your name?")

    # Repeat the name back to the user and wait for confirmation
    confirmation = None
    while confirmation is None or confirmation.lower() not in ["yes", "yeah", "yup", "yes please"]:
        confirmation = listen_for_speech(f"Did you say {name}? Please say 'yes' to confirm.")
        if confirmation and confirmation.lower() in ["yes", "yeah", "yup", "yes please"]:
            speak(f"Nice to meet you, {name}. Have a great day!")
            break
        else:
            name = None  # Reset name to None to re-initiate the name asking process
            speak("Let's try this again. What's your name?")