import pyttsx3

def list_voices():
    engine = pyttsx3.init()
    voices = engine.getProperty('voices')
    for i, voice in enumerate(voices):
        print(f"Voice {i}: ID: {voice.id} | Name: {voice.name} | Languages: {voice.languages} | Gender: {voice.gender}")

def set_voice(voice_number=0):
    engine = pyttsx3.init()
    voices = engine.getProperty('voices')
    # Select a voice by its index. You can choose a number based on the output of list_voices()
    engine.setProperty('voice', voices[voice_number].id)
    return engine

# Example usage
list_voices()
# Now, choose a voice number based on the list. For example, to choose the second voice, use voice_number=1.
engine = set_voice(voice_number=1)
engine.say("Hello, how are you doing today?")
engine.runAndWait()
