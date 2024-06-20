import os
os.environ["PATH"] += os.pathsep + "ffmpeg/bin"
import requests
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
import speech_recognition as sr
from pydub import AudioSegment
from pydub.playback import play
from TTS.utils.io import load_config
from TTS.tts import TTS

# Initialize API Keys (Change this in .env)

# Initialize Voice Recognizer
r = sr.Recognizer()

# Initialize Chat List
chat_list = []

# Load TTS configuration
tts_config = load_config("path/to/your/config.json")

# Initialize Mozilla TTS engine
tts_engine = TTS(tts_config)

# Function to synthesize speech from text using Mozilla TTS
def text_to_speech(text):
    # Synthesize speech from text
    wav_data = tts_engine.tts(text)

    # Save synthesized speech to a WAV file
    with open('output.wav', 'wb') as f:
        f.write(wav_data)

    return True

# Generate text response using OpenAI API
def generate_response(user_message):
    global chat_list

    # Case 1: Chat list is empty, so we will initialize the list with a system prompt
    if len(chat_list) == 0:
        system_prompt = {"role": "system", "content": """
                - You are a virtual assistant designed to assist the user.
                - You will respond to the user's queries and commands.
                - You can provide information, perform tasks, and engage in conversation.
                - Your responses should be helpful and relevant to the user's needs.
                """}
        chat_list.append(system_prompt)

    # Case 2: Chat list is not empty and is already initialized
    user_prompt = {"role": "user", "content": user_message}
    chat_list.append(user_prompt)
    response = client.chat.completions.create(model="gpt-3.5-turbo",
    messages=chat_list,
    temperature=0.85).choices[0].message.content
    assistant_prompt = {"role": "assistant", "content": response}
    chat_list.append(assistant_prompt)
    print(f"You: {user_message}")
    print(f"Assistant: {response}")
    return response

# Function to listen for speech input from the user
def listen_for_input():
    with sr.Microphone() as source:
        r.adjust_for_ambient_noise(source)  # Adjust for ambient noise
        print("Listening...")
        try:
            audio = r.listen(source, timeout=5)  # Listen for up to 5 seconds
            print("Processing...")
            user_input = r.recognize_google(audio)
            print(f"You said: {user_input}")
            return user_input
        except sr.WaitTimeoutError:
            print("No speech detected.")
            return ""
        except sr.UnknownValueError:
            print("Sorry, I couldn't understand what you said.")
            return ""
        except sr.RequestError as e:
            print(f"Error occurred: {e}")
            return ""

if __name__ == '__main__':
    print("Welcome! I'm your personal assistant. You can start interacting with me.")

    while True:
        # Listen for speech input
        user_speech_input = listen_for_input()
        if user_speech_input:
            response = generate_response(user_speech_input)
            if text_to_speech(response):
                sound = AudioSegment.from_wav('output.wav')
                play(sound)
            continue  # Skip text input if speech input was successful

        # If no speech input detected, prompt for text input
        user_input = input("You: ")

        # Exit condition
        if user_input.lower() == 'exit':
            print("Goodbye!")
            break

        # Generate response from text input
        response = generate_response(user_input)
        if text_to_speech(response):  # Convert text to speech
            sound = AudioSegment.from_wav('output.wav')
            play(sound)
