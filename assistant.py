import os
import io
import numpy as np
import speech_recognition as sr
from gtts import gTTS
import playsound
from openai import OpenAI
import threading
import time
import RPi.GPIO as GPIO
import subprocess
import sounddevice as sd
import soundfile as sf

# Initialize OpenAI client
#client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
client = OpenAI(api_key="YOUR_OPENAI_KEY")

# Servo Setup
GPIO.setmode(GPIO.BCM)
SERVO_PIN = 18
GPIO.setup(SERVO_PIN, GPIO.OUT)

pwm = GPIO.PWM(SERVO_PIN, 50)  # 50Hz for servo
pwm.start(0)

# Global flag to control servo movement
servo_running = False

def set_angle(angle):
    duty = 2 + (angle / 18)
    GPIO.output(SERVO_PIN, True)
    pwm.ChangeDutyCycle(duty)
    time.sleep(0.3)
    GPIO.output(SERVO_PIN, False)
    pwm.ChangeDutyCycle(0)

def servo_loop():
    """Continuously sweep servo while servo_running is True."""
    while servo_running:
        set_angle(0)
        time.sleep(0.3)
        set_angle(180)
        time.sleep(0.3)
    set_angle(90)  # Return to center when done

def play_prerecorded():
    # Use subprocess.Popen so the call does not block
    # Use -q quiet mode for no console messages
    try:
         # set volume to make sure it can be heard
         subprocess.run(["amixer", "-D", "hw:P10S", "sset", "PCM", "25%"], check=True)

         # Uncomment if you use Option1 or Option2 to stream audio in the speak function
         # It takes longer to run those options so these prerecorded audio files can fill in while waiting
         # A similar process can be used to play an advertisement for a free account or skip the ad for a paid account
         # I.e., free account uses Option 1 while the paid account uses Option 3.

         # Run the intro audio
         #time.sleep(5)
         #subprocess.Popen(["/usr/bin/aplay", "-q", "VonShokle.wav"])
         # Run the ad for ARM (They have the best products and hackathons!)
         #time.sleep(10)
         #subprocess.Popen(["/usr/bin/aplay", "-q", "advertisement.wav"])
    except Exception as e:
         # Avoid crashing if no file
         print(f"Failed to play pre-recorded audio: {e}")

def listen():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening for wake word...")
        audio = r.listen(source)
    try:
        text = r.recognize_google(audio).lower()
        print(f"Heard: {text}")
        return text
    except sr.UnknownValueError:
        return None

def ask_openai(prompt):
    global servo_running
    servo_running = True  

    #Start pre-recorded audio
    audio_thread = threading.Thread(target=play_prerecorded, daemon=True)
    audio_thread.start()

    #start servo movement
    servo_thread = threading.Thread(target=servo_loop)
    servo_thread.start()

    # Send question to OpenAI
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
              "role": "system",
              "content": (
                "You are a diabolical cooking assistant who answers questions with a mischievous, humorous, and scary tone."
                "You provide useful recipes and kitchen tips, as well as answer unrelated cooking questions."
                "Keep answers clear and always scary with a diabolical twist and never longer than one sentence unless a recipe is requested."
              )
            },
            {"role": "user", "content": prompt}
        ]
    )
    return response.choices[0].message.content, servo_thread


def speak(text, servo_thread):
    global servo_running

    try:
        #Option 1:  Convert the text to mp3 and then play it - not optimized playback
        #tts = gTTS(text="Now is a great time for an advertisement...Buy more ARM products...I'm almost done executing...please standby.", lang='en', tld='co.uk') 
        #tts = gTTS(text=text, lang='en', tld='co.uk')
        #tts.save("response.mp3")
        #os.system("mpg123 response.mp3")

        #Option 2: Make a new request to OpenAI and stream the file without saving it - better but still not optimized due to mp3 audio format and the file needs to fully download and then load into memory before playback
        #audio_response = client.audio.speech.create(
        #    model="gpt-4o-mini-tts",  # TTS model
        #    voice="alloy",            # Change voice here
        #    input=text
        #)
        #process = subprocess.Popen(["mpg123", "-q", "-"], stdin=subprocess.PIPE)
        #process.communicate(audio_response.content)

        #Option 3: Make a new request to OpenAI and stream buffered wav file in chunks as it is received
        #          Optimized for quick playback
        with client.audio.speech.with_streaming_response.create(
            model="gpt-4o-mini-tts",  # High-quality TTS model
            voice="fable",
            input=text,
            response_format="wav",
        ) as response:
            # Collect streamed audio into memory
            buffer = io.BytesIO()
            for chunk in response.iter_bytes():
                buffer.write(chunk)
            buffer.seek(0)

            # Decode WAV and play
            audio, samplerate = sf.read(buffer, dtype='float32')
            if audio.ndim == 1:  # Ensure stereo shape
                audio = np.expand_dims(audio, axis=1)

            print("Playing audio...")
            sd.play(audio, samplerate)
            sd.wait()
            print("Playback finished.")

        # Stop the servo
        servo_running = False
        servo_thread.join()
    except Exception as e:
        print(f"Error during speak playback: {e}")

def main():
  try:
    while True:
        heard = listen()
        if heard and heard.startswith("hey cookie"):
            command = heard.replace("hey cookie", "", 1).strip()
            if command:
                print(f"Command: {command}")
                response, servo_thread = ask_openai(command)
                print(f"AI: {response}")
                speak(response, servo_thread)
            else:
                print("Wake word detected, but no command given.")
  except KeyboardInterrupt:
    pwm.stop()
    GPIO.cleanup()

if __name__ == "__main__":
    main()

