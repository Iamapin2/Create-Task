import random
import os
from PIL import Image, ImageTk
from io import BytesIO
import tkinter as tk
from tkinter import simpledialog, messagebox
import requests

dates = ['2025-03-01', '2025-03-02', '2025-03-01', '2025-03-04', '2025-03-05', '2025-02-27', '2025-02-26', '2025-02-11', '2024-11-24']
date = random.choice(dates)
api_key = os.environ['nasa_api_key']

#used the ground work of a previous group project to help create the gui rock paper scissors (group partner was Jaden Joseph) - used ai to help the conversion to tkinter
ROCK = "rock"
PAPER = "paper"
SCISSORS = "scissors"
CHOICES = [ROCK, PAPER, SCISSORS]

USER_WIN_MESSAGE = "User has won!"
COMPUTER_WIN_MESSAGE = "Computer has won!"
TIE_MESSAGE = "It's a tie!"

user_score = 0
computer_score = 0
rounds_played = 0

def get_user_name():
    username = None
    while not username:
        username = simpledialog.askstring("Username", "Please enter a username", initialvalue="User")
    return username

def get_savefile_name(username):
    return f"save_{username.lower()}.txt"

def has_save(username):
    return os.path.exists(get_savefile_name(username))

def write_save(username, rounds_played, user_score, computer_score):
    with open(get_savefile_name(username), "w") as f:
        f.write(f"{str(rounds_played)},{str(user_score)},{str(computer_score)}")

def read_save(username):
    filename = get_savefile_name(username)
    if not os.path.exists(filename):
        return
    with open(filename, "r") as f:
        data = f.read().split(",")
        rounds_played = int(data[0])
        user_score = int(data[1])
        computer_score = int(data[2])
        return rounds_played, user_score, computer_score

def get_computer_choice():
    return random.choice(CHOICES)

def determine_winner(user_choice, computer_choice):
    if user_choice == computer_choice:
        return TIE_MESSAGE
    if ((user_choice == ROCK and computer_choice == SCISSORS)
            or (user_choice == PAPER and computer_choice == ROCK)
            or (user_choice == SCISSORS and computer_choice == PAPER)):
        return USER_WIN_MESSAGE
    return COMPUTER_WIN_MESSAGE

def get_random_star_image(api_key, date):
    space_api_url = "https://api.nasa.gov/planetary/apod"
    params = {"api_key": api_key, "date": date}
    try:
        response = requests.get(space_api_url, params=params)
        response.raise_for_status()
        data = response.json()
        if data["media_type"] == "image":
            image_url = data.get("hdurl") or data.get("url")
            if image_url:
                image_response = requests.get(image_url)
                image_response.raise_for_status()
                return Image.open(BytesIO(image_response.content))
        return None
    except Exception as e:
        print(f"Error: {e}")
        return None

def create_gui():
    root = tk.Tk()
    root.title("Rock, Paper, Scissors!")
    root.geometry("400x400")

    
    bg_label = tk.Label(root)
    bg_label.place(x=0, y=0, relwidth=1, relheight=1)

    # Used ai to help fix my background code to work
    image = get_random_star_image(api_key, date)
    if image:
        image.thumbnail((400, 400), Image.Resampling.LANCZOS)
        photo = ImageTk.PhotoImage(image)
        bg_label.configure(image=photo)
        bg_label.image = photo

    
    game_frame = tk.Frame(root, bg='#f0f0f0')
    game_frame.place(relx=0.5, rely=0.5, anchor='center', width=300, height=300)

    title = tk.Label(game_frame, text="Rock Paper Scissors", font=("Arial", 20), bg='#f0f0f0')
    title.pack(pady=20)

    buttons_frame = tk.Frame(game_frame, bg='#f0f0f0')
    buttons_frame.pack(pady=20)

    result_label = tk.Label(game_frame, text="Make your choice!", font=("Arial", 12), bg='#f0f0f0')
    result_label.pack(pady=20)

    score_label = tk.Label(
        game_frame,
        text=f"Score - You: {user_score} Computer: {computer_score}",
        font=("Arial", 12),
        bg='#f0f0f0'
    )
    score_label.pack(pady=10)

    def make_choice(choice):
        global user_score, computer_score, rounds_played
        computer = get_computer_choice()
        result = determine_winner(choice, computer)

        if result == USER_WIN_MESSAGE:
            user_score += 1
        elif result == COMPUTER_WIN_MESSAGE:
            computer_score += 1

        rounds_played += 1
        result_label.config(text=f"Computer chose: {computer}\n{result}")
        score_label.config(text=f"Score - You: {user_score} Computer: {computer_score}")
        write_save(username, rounds_played, user_score, computer_score)

    tk.Button(buttons_frame, text="Rock", command=lambda: make_choice(ROCK)).pack(side=tk.LEFT, padx=10)
    tk.Button(buttons_frame, text="Paper", command=lambda: make_choice(PAPER)).pack(side=tk.LEFT, padx=10)
    tk.Button(buttons_frame, text="Scissors", command=lambda: make_choice(SCISSORS)).pack(side=tk.LEFT, padx=10)

    return root

if __name__ == "__main__":
    username = get_user_name()

    root = create_gui()

    if has_save(username) and messagebox.askyesno("Save File", "Do you want to load your last save?"):
        save = read_save(username)
        rounds_played = save[0]
        user_score = save[1]
        computer_score = save[2]

    root.mainloop()
