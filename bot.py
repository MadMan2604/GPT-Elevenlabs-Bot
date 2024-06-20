import os
import requests
import openai
import speech_recognition as sr

# Initialize API Keys (Change this in .env)
openai.api_key = os.getenv("OPENAI_API_KEY")
elevenai_api_key = os.getenv("ELEVENAI_API_KEY")

# Initialize ElevenAI Voice ID (Change this in .env)
elevenai_voice_id = os.getenv("ELEVENAI_VOICE_ID")

# Set FFMPEG PATH (Change this to the directory of FFMPEG.exe if required)
ffmpeg_path = "ffmpeg/bin/ffmpeg.exe"

# Initialize Voice Recognizer
r = sr.Recognizer()

# Initialize Chat List
chat_list = []


# Generate audio response using ElevenLabs API
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

    # Case 2: Unsuccessful retrieval of MP3 file from ElevenLabs
    else:
        print("Request failed with status code:", response.status_code)


# Generate text response using OpenAI API
def generate_response(user_message):
    global chat_list
    # Case 1: Chat list is empty, so we will initialize the list with a system prompt
    if len(chat_list) == 0:
        system_prompt = {"role": "system", "content": """
                - You are a virtual assistant designed to have conversations with users.
                - It is important to respond naturally and appropriately to user queries.
                """}
        chat_list.append(system_prompt)

    # Case 2: Chat list is not empty and is already initialized
    user_prompt = {"role": "user", "content": f"User: {user_message}"}
    chat_list.append(user_prompt)
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=chat_list,
        temperature=0.85,
    ).choices[0].message.content
    assistant_prompt = {"role": "assistant", "content": f"{response}"}
    chat_list.append(assistant_prompt)
    print(f"Bot: {response}")
    return response


# Function to capture user speech input and convert it to text
def listen_for_input():
    with sr.Microphone() as source:
        print('Listening...')
        audio = r.listen(source, phrase_time_limit=10)

    try:
        user_message = r.recognize_google(audio)  # Convert speech to text
        print(f'User: {user_message}')
        return user_message
    except sr.UnknownValueError:
        print("Sorry, I didn't catch that.")
        return None
    except sr.RequestError as e:
        print(f'Sorry, there was an error processing your request: {e}')
        return None


if __name__ == '__main__':
    while True:
        user_input = listen_for_input()
        if user_input:
            response = generate_response(user_input)
            text_to_speech(response)
