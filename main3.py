import os
os.environ["PATH"] += os.pathsep + "ffmpeg/bin"
import requests
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
import speech_recognition as sr
from pydub import AudioSegment
from pydub.playback import play
import pygame
from pygame.locals import *
from threading import Thread
from buttons import Button

# Initialize API Keys (Change this in .env)
elevenai_api_key = os.getenv("ELEVENAI_API_KEY")

# Initialize ElevenAI Voice ID (Change this in .env)
elevenai_voice_id = os.getenv("ELEVENAI_VOICE_ID")

# Initialize Voice Recognizer
r = sr.Recognizer()

# Initialize Chat List
chat_list = []

# Function to generate audio response using ElevenLabs API
def text_to_speech(text):
    url = "https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
    voice_id = elevenai_voice_id
    api_key = elevenai_api_key
    data = {
        "text": text
    }
    headers = {
        "Content-Type": "application/json",
        "xi-api-key": api_key
    }
    response = requests.post(url.format(voice_id=voice_id), headers=headers, json=data)

    # Case 1: Successful retrieval of MP3 file from ElevenLabs
    if response.status_code == 200:
        with open('tts.mp3', 'wb') as f:
            f.write(response.content)
        return True

    # Case 2: Unsuccessful retrieval of MP3 file from ElevenLabs
    else:
        print("Request failed with status code:", response.status_code)
        return False

# Function to generate text response using OpenAI API
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

# Function to listen for voice input
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

# Function to run Pygame GUI
## Define Pygame Window Variables
WIDTH = 900 
HEIGHT = 700
### Now write the Function to run Pygame GUI
def run_gui():
    pygame.init()
    pygame.font.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
    pygame.display.set_caption("AI Voice Assistant")

    font = pygame.font.Font('Aquire-BW0ox.ttf', 100)
    clock = pygame.time.Clock()

    speaking = False

    # Load button images
    #talk_img = pygame.image.load('talk_button.png')
    # Create the button/s for the ai input
    #talk_button_img = Button(talk_img, (200, 80))


    # Define button sizes
    button_width = 100
    button_height = 40

    while True:
        screen.fill((255, 255, 255))
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                exit()
            if event.type == MOUSEBUTTONDOWN:
                if not speaking:
                    speaking = True
                    user_speech_input = listen_for_input()
                    if user_speech_input:
                        response = generate_response(user_speech_input)
                        if text_to_speech(response):
                            sound = AudioSegment.from_mp3('tts.mp3')
                            play(sound)
                        speaking = False
                elif 400 <= pygame.mouse.get_pos()[0] <= 400 + button_width and 280 <= pygame.mouse.get_pos()[1] <= 280 + button_height:
                    speaking = False

        

        # Draw Background & Screen Text (Title) 
        background = pygame.image.load('background.png')
        background = pygame.transform.scale(background, (WIDTH, HEIGHT))
        screen.blit(background, (0, 0))
        title_text = font.render("AI ASSISTANT", True, (255, 255, 255))
        screen.blit(title_text, (WIDTH // 2 - title_text.get_width() // 2, 100))
        # Draw button
        #talk_button_img.draw(screen)

        pygame.display.flip()
        clock.tick(60)

if __name__ == '__main__':
    gui_thread = Thread(target=run_gui)
    gui_thread.start()
