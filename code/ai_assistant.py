import pyttsx3
import datetime
import webbrowser
import os
import speech_recognition as sr
import tkinter as tk
from tkinter import scrolledtext
import openai
import winsound
import time
import threading

# Set your OpenAI API key here
openai.api_key = "your-real-api-key"  # Replace with your valid OpenAI API key

# Initialize text-to-speech engine
engine = pyttsx3.init()

# Store last spoken text to allow repeat
last_spoken_text = ""

# Speak text aloud
def speak(text):
    global last_spoken_text
    last_spoken_text = text
    engine.say(text)
    engine.runAndWait()

# Greeting based on time of day
def greet():
    hour = datetime.datetime.now().hour
    if hour < 12:
        text = "Good morning!"
    elif hour < 18:
        text = "Good afternoon!"
    else:
        text = "Good evening!"
    update_chat(f"Assistant: {text}")
    speak(text)
    intro = "I am your assistant. How can I help you?"
    update_chat(f"Assistant: {intro}")
    speak(intro)

# Listen using microphone
def listen():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        update_chat("Assistant: Listening...")
        r.adjust_for_ambient_noise(source)  # Helps in noisy environments
        try:
            audio = r.listen(source, timeout=5, phrase_time_limit=7)
            command = r.recognize_google(audio)
            update_chat(f"You said: {command}")
            return command.lower()
        except sr.WaitTimeoutError:
            speak("Listening timed out, please try again.")
        except sr.UnknownValueError:
            speak("Sorry, I didn't catch that.")
        except Exception as e:
            speak("Something went wrong.")
            print("Speech recognition error:", e)
        return ""

# Use OpenAI to respond to unrecognized commands
def fallback_response(command):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": command}]
        )
        return response.choices[0].message.content
    except Exception as e:
        print("OpenAI API error:", e)
        return "I couldn't connect to OpenAI services. Please check your API key or internet."

# Simple music using beeps
def play_simple_music():
    notes = [
        (262, 400), (262, 400), (392, 400), (392, 400),
        (440, 400), (440, 400), (392, 800),
        (349, 400), (349, 400), (330, 400), (330, 400),
        (294, 400), (294, 400), (262, 800),
    ]
    for freq, dur in notes:
        winsound.Beep(freq, dur)
        time.sleep(0.1)

# Respond to commands
def respond(command):
    if "time" in command:
        now = datetime.datetime.now()
        reply = f"Today is {now.strftime('%A, %B %d, %Y')}. The time is {now.strftime('%I:%M %p')} IST."
    elif "youtube" in command:
        reply = "Opening YouTube"
        webbrowser.open("https://www.youtube.com")
    elif "google" in command:
        speak("What should I search on Google?")
        query = listen()
        if query:
            webbrowser.open(f"https://www.google.com/search?q={query}")
            reply = f"Searching Google for {query}"
        else:
            reply = "No search query received."
    elif "joke" in command:
        reply = "Why don't scientists trust atoms? Because they make up everything!"
    elif "open notepad" in command:
        reply = "Opening Notepad"
        os.system("notepad")
    elif "play music" in command:
        reply = "Playing a simple tune"
        play_simple_music()
    elif "who are you" in command:
        reply = "I am your AI assistant, built with Python and OpenAI."
    elif "image" in command or "generate image" in command:
        reply = "Opening image generator for you."
        webbrowser.open("https://chat.openai.com/")
    elif "exit" in command or "quit" in command:
        reply = "Goodbye!"
        speak(reply)
        root.destroy()
        exit()
    else:
        reply = fallback_response(command)

    update_chat(f"Assistant: {reply}")
    speak(reply)

# Thread wrapper for responsiveness
def threaded_respond(command):
    threading.Thread(target=respond, args=(command,), daemon=True).start()

# Handle voice input
def handle_voice():
    command = listen()
    if command.strip():
        threaded_respond(command)
    else:
        speak("Please say something.")

# Handle text input
def handle_text():
    command = entry.get()
    if command.strip():
        update_chat(f"You typed: {command}")
        threaded_respond(command)
    else:
        speak("Please type something.")
    entry.delete(0, tk.END)

# Update chat window
def update_chat(message):
    chat_box.configure(state='normal')
    chat_box.insert(tk.END, message + "\n\n")
    chat_box.configure(state='disabled')
    chat_box.see(tk.END)

# Repeat last response
def repeat_audio():
    if last_spoken_text:
        speak(last_spoken_text)
    else:
        speak("There is nothing to repeat yet.")

# --- GUI SETUP ---
root = tk.Tk()
root.title("Personal AI Voice Assistant")
root.geometry("750x550")
root.configure(bg="#2c3e50")

label = tk.Label(root, text="Personal AI Voice Assistant", font=("Segoe UI", 26, "bold"),
                 fg="#ecf0f1", bg="#2c3e50")
label.pack(pady=15)

chat_box = scrolledtext.ScrolledText(root, wrap=tk.WORD, font=("Consolas", 15),
                                     state='disabled', height=16, bg="#34495e", fg="#ecf0f1")
chat_box.pack(padx=15, pady=10, fill=tk.BOTH, expand=True)

entry = tk.Entry(root, font=("Segoe UI", 16), bg="#ecf0f1", fg="#2c3e50")
entry.pack(padx=15, pady=8, fill=tk.X)

btn_frame = tk.Frame(root, bg="#2c3e50")
btn_frame.pack(pady=5)

def style_button(btn):
    btn.config(font=("Segoe UI", 14, "bold"), bg="#2980b9", fg="white",
               activebackground="#3498db", relief=tk.FLAT, padx=18, pady=10, cursor="hand2")
    btn.bind("<Enter>", lambda e: btn.config(bg="#3498db"))
    btn.bind("<Leave>", lambda e: btn.config(bg="#2980b9"))

btn_text = tk.Button(btn_frame, text="Send Text", command=handle_text)
btn_voice = tk.Button(btn_frame, text="🎤 Speak", command=handle_voice)
btn_repeat = tk.Button(btn_frame, text="🔁 Repeat Audio", command=repeat_audio)

for i, b in enumerate([btn_text, btn_voice, btn_repeat]):
    style_button(b)
    b.grid(row=0, column=i, padx=10)

# Suggested commands
suggestion_label = tk.Label(root, text="Try these commands:", font=("Segoe UI", 16, "italic"),
                            fg="#bdc3c7", bg="#2c3e50")
suggestion_label.pack(pady=(15, 5))

suggestion_frame = tk.Frame(root, bg="#2c3e50")
suggestion_frame.pack(pady=5, fill=tk.X)

canvas = tk.Canvas(suggestion_frame, height=55, bg="#2c3e50", highlightthickness=0)
h_scroll = tk.Scrollbar(suggestion_frame, orient=tk.HORIZONTAL, command=canvas.xview)
canvas.configure(xscrollcommand=h_scroll.set)
h_scroll.pack(side=tk.BOTTOM, fill=tk.X)
canvas.pack(side=tk.LEFT, fill=tk.X, expand=True)

btn_container = tk.Frame(canvas, bg="#2c3e50")
canvas.create_window((0, 0), window=btn_container, anchor='nw')

def on_configure(event):
    canvas.configure(scrollregion=canvas.bbox('all'))
btn_container.bind('<Configure>', on_configure)

example_commands = [
    "What's the time?",
    "Tell me a joke",
    "Open YouTube",
    "Play music",
    "Who are you?",
    "Generate image",
    "Open notepad",
]

for cmd in example_commands:
    b = tk.Button(btn_container, text=cmd, width=20,
                  command=lambda c=cmd: threaded_respond(c))
    style_button(b)
    b.pack(side=tk.LEFT, padx=8, pady=5)

# Start assistant
greet()
root.mainloop()

#pip install pandas   
#pip install numpy
#pip install scikit-learn
# pip install matplotlib
#  pip install seaborn    
# pip install pyttsx3    
# pip install datetime 
# pip install openai==0.28    
# pip install openai  
# pip install pyttsx3 speechrecognition openai
# 
# python ai_assistant.py                                                                                                                                                                   