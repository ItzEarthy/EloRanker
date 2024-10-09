import os
from tkinter import *
from tkinter import ttk

K_singles = 32  # K-value for singles matches
K_doubles = 24  # K-value for doubles matches
DATA_FOLDER = "player_data"  # Folder to store player rating files

# Ensure the data folder exists
if not os.path.exists(DATA_FOLDER):
    os.makedirs(DATA_FOLDER)

# Function to format names as 'First Last'
def format_name(name):
    return " ".join(word.capitalize() for word in name.split())

# Function to get player's rating and stats from text file or create one if not found
def get_player_stats(player_name):
    filename = os.path.join(DATA_FOLDER, f"{player_name}.txt")
    if os.path.exists(filename):
        with open(filename, "r") as file:
            data = file.read().strip().split(',')
            rating = int(data[0])
            wins = int(data[1])
            losses = int(data[2])
    else:
        # If player is new, start with a default rating of 1200 and 0 wins/losses
        rating = 1200
        wins = 0
        losses = 0
        with open(filename, "w") as file:
            file.write(f"{rating},{wins},{losses}")
    return rating, wins, losses

# Function to update player's rating and stats and save to text file
def update_player_stats(player_name, new_rating, wins, losses):
    filename = os.path.join(DATA_FOLDER, f"{player_name}.txt")
    with open(filename, "w") as file:
        file.write(f"{new_rating},{wins},{losses}")

# Function to calculate the expected score for a player
def calculate_expected_score(rating_a, rating_b):
    return 1 / (1 + 10 ** ((rating_b - rating_a) / 400))

# Function to calculate new ratings for singles matches
def update_singles_ratings(player_a, player_b, result_a):
    rating_a, wins_a, losses_a = get_player_stats(player_a)
    rating_b, wins_b, losses_b = get_player_stats(player_b)

    expected_a = calculate_expected_score(rating_a, rating_b)
    expected_b = calculate_expected_score(rating_b, rating_a)

    # Update ratings based on match result
    if result_a == "win":
        score_a = 1
        score_b = 0
        wins_a += 1
        losses_b += 1
    else:  # loss
        score_a = 0
        score_b = 1
        losses_a += 1
        wins_b += 1

    new_rating_a = rating_a + K_singles * (score_a - expected_a)
    new_rating_b = rating_b + K_singles * (score_b - expected_b)

    update_player_stats(player_a, round(new_rating_a), wins_a, losses_a)
    update_player_stats(player_b, round(new_rating_b), wins_b, losses_b)

# Function to calculate new ratings for doubles matches
def update_doubles_ratings(winner_1, winner_2, loser_1, loser_2):
    rating_w1, wins_w1, losses_w1 = get_player_stats(winner_1)
    rating_w2, wins_w2, losses_w2 = get_player_stats(winner_2)
    rating_l1, wins_l1, losses_l1 = get_player_stats(loser_1)
    rating_l2, wins_l2, losses_l2 = get_player_stats(loser_2)

    # Team ratings are the average of both players
    team_w_rating = (rating_w1 + rating_w2) / 2
    team_l_rating = (rating_l1 + rating_l2) / 2

    expected_w = calculate_expected_score(team_w_rating, team_l_rating)
    expected_l = calculate_expected_score(team_l_rating, team_w_rating)

    # Winners score 1, losers score 0
    team_w_new_rating = team_w_rating + K_doubles * (1 - expected_w)
    team_l_new_rating = team_l_rating + K_doubles * (0 - expected_l)

    # Update both players' ratings and stats
    update_player_stats(winner_1, round(rating_w1 + (team_w_new_rating - team_w_rating)), wins_w1 + 1, losses_w1)
    update_player_stats(winner_2, round(rating_w2 + (team_w_new_rating - team_w_rating)), wins_w2 + 1, losses_w2)
    update_player_stats(loser_1, round(rating_l1 + (team_l_new_rating - team_l_rating)), wins_l1, losses_l1 + 1)
    update_player_stats(loser_2, round(rating_l2 + (team_l_new_rating - team_l_rating)), wins_l2, losses_l2 + 1)

# Function to get all player names
def get_all_player_names():
    player_files = os.listdir(DATA_FOLDER)
    return [file.replace(".txt", "") for file in player_files]

# Function to display rankings in the popup
def show_rankings():
    ranking_window = Toplevel(root)
    ranking_window.title("Player Rankings")
    ranking_window.configure(bg='lightgray')

    # Create a listbox to display the player rankings
    ranking_list = Listbox(ranking_window, width=60, height=20, font=('Arial', 14))
    ranking_list.pack(padx=10, pady=10)

    player_names = get_all_player_names()
    player_stats = {player: get_player_stats(player) for player in player_names}

    # Sort players by rating
    sorted_players = sorted(player_stats.items(), key=lambda x: x[1][0], reverse=True)

    # Add players to the listbox
    for player, (rating, wins, losses) in sorted_players:
        ranking_list.insert(END, f"{player}: {rating} (Wins: {wins}, Losses: {losses})")

# Function to handle match submission
def submit_match():
    if game_type.get() == "singles":
        player_a = format_name(player_a_var.get().strip())
        player_b = format_name(player_b_var.get().strip())
        result_a = result_var.get()

        if player_a == "" or player_b == "":
            result_label.config(text="Both player names must be filled.", fg="red")
            return

        update_singles_ratings(player_a, player_b, result_a)
    else:
        winner_1 = format_name(winner_1_var.get().strip())
        winner_2 = format_name(winner_2_var.get().strip())
        loser_1 = format_name(loser_1_var.get().strip())
        loser_2 = format_name(loser_2_var.get().strip())

        if winner_1 == "" or winner_2 == "" or loser_1 == "" or loser_2 == "":
            result_label.config(text="All player names must be filled.", fg="red")
            return

        update_doubles_ratings(winner_1, winner_2, loser_1, loser_2)

    result_label.config(text="Match results updated!", fg="green")
    # Clear the inputs
    player_a_var.set("")
    player_b_var.set("")
    winner_1_var.set("")
    winner_2_var.set("")
    loser_1_var.set("")
    loser_2_var.set("")

    # Refresh the player dropdowns to include any new players
    player_a_dropdown['values'] = get_all_player_names()
    player_b_dropdown['values'] = get_all_player_names()
    winner_1_dropdown['values'] = get_all_player_names()
    winner_2_dropdown['values'] = get_all_player_names()
    loser_1_dropdown['values'] = get_all_player_names()
    loser_2_dropdown['values'] = get_all_player_names()

# Function to switch between singles and doubles inputs
def toggle_game_type():
    if game_type.get() == "singles":
        singles_frame.grid()
        doubles_frame.grid_remove()
    else:
        singles_frame.grid_remove()
        doubles_frame.grid()

# Main application window
root = Tk()
root.title("Elo Rating System")
root.configure(bg='lightgray')

# Game Type Toggle (Singles/Doubles)
game_type = StringVar(value="singles")
singles_radio = Radiobutton(root, text="Singles", variable=game_type, value="singles", command=toggle_game_type, bg='lightgray', font=('Arial', 14))
doubles_radio = Radiobutton(root, text="Doubles", variable=game_type, value="doubles", command=toggle_game_type, bg='lightgray', font=('Arial', 14))
singles_radio.grid(row=0, column=0, sticky='w', padx=10, pady=10)
doubles_radio.grid(row=0, column=1, sticky='w', padx=10, pady=10)

# Frame for Singles Inputs
singles_frame = Frame(root, bg='lightgray')
singles_frame.grid(row=1, column=0, columnspan=2)

# Player A dropdown
player_a_var = StringVar()
player_a_label = Label(singles_frame, text="Player A:", bg='lightgray', font=('Arial', 14))
player_a_label.grid(row=0, column=0, padx=5, pady=5)
player_a_dropdown = ttk.Combobox(singles_frame, textvariable=player_a_var)
player_a_dropdown['values'] = get_all_player_names()
player_a_dropdown.grid(row=0, column=1, padx=5, pady=5)

# Player B dropdown
player_b_var = StringVar()
player_b_label = Label(singles_frame, text="Player B:", bg='lightgray', font=('Arial', 14))
player_b_label.grid(row=1, column=0, padx=5, pady=5)
player_b_dropdown = ttk.Combobox(singles_frame, textvariable=player_b_var)
player_b_dropdown['values'] = get_all_player_names()
player_b_dropdown.grid(row=1, column=1, padx=5, pady=5)

# Result Toggle (Win/Loss)
result_var = StringVar(value="win")
result_label = Label(singles_frame, text="Result for Player A:", bg='lightgray', font=('Arial', 14))
result_label.grid(row=2, column=0, padx=5, pady=5)
win_radio = Radiobutton(singles_frame, text="Win", variable=result_var, value="win", bg='lightgray', font=('Arial', 14))
loss_radio = Radiobutton(singles_frame, text="Loss", variable=result_var, value="loss", bg='lightgray', font=('Arial', 14))
win_radio.grid(row=2, column=1, sticky='w')
loss_radio.grid(row=2, column=1, sticky='e')

# Frame for Doubles Inputs (initially hidden)
doubles_frame = Frame(root, bg='lightgray')
doubles_frame.grid(row=1, column=0, columnspan=2)
doubles_frame.grid_remove()

# Doubles Winner 1 dropdown
winner_1_var = StringVar()
winner_1_label = Label(doubles_frame, text="Winner 1:", bg='lightgray', font=('Arial', 14))
winner_1_label.grid(row=0, column=0, padx=5, pady=5)
winner_1_dropdown = ttk.Combobox(doubles_frame, textvariable=winner_1_var)
winner_1_dropdown['values'] = get_all_player_names()
winner_1_dropdown.grid(row=0, column=1, padx=5, pady=5)

# Doubles Winner 2 dropdown
winner_2_var = StringVar()
winner_2_label = Label(doubles_frame, text="Winner 2:", bg='lightgray', font=('Arial', 14))
winner_2_label.grid(row=1, column=0, padx=5, pady=5)
winner_2_dropdown = ttk.Combobox(doubles_frame, textvariable=winner_2_var)
winner_2_dropdown['values'] = get_all_player_names()
winner_2_dropdown.grid(row=1, column=1, padx=5, pady=5)

# Doubles Loser 1 dropdown
loser_1_var = StringVar()
loser_1_label = Label(doubles_frame, text="Loser 1:", bg='lightgray', font=('Arial', 14))
loser_1_label.grid(row=2, column=0, padx=5, pady=5)
loser_1_dropdown = ttk.Combobox(doubles_frame, textvariable=loser_1_var)
loser_1_dropdown['values'] = get_all_player_names()
loser_1_dropdown.grid(row=2, column=1, padx=5, pady=5)

# Doubles Loser 2 dropdown
loser_2_var = StringVar()
loser_2_label = Label(doubles_frame, text="Loser 2:", bg='lightgray', font=('Arial', 14))
loser_2_label.grid(row=3, column=0, padx=5, pady=5)
loser_2_dropdown = ttk.Combobox(doubles_frame, textvariable=loser_2_var)
loser_2_dropdown['values'] = get_all_player_names()
loser_2_dropdown.grid(row=3, column=1, padx=5, pady=5)

# Submit button
submit_button = Button(root, text="Submit Match", command=submit_match, bg='#007aff', fg='white', font=('Arial', 16), relief='flat')
submit_button.grid(row=3, column=0, columnspan=2, pady=10)

# Result message label
result_label = Label(root, text="", bg='lightgray', font=('Arial', 14))
result_label.grid(row=4, column=0, columnspan=2)

# Rankings Button
rankings_button = Button(root, text="Show Rankings", command=show_rankings, bg='#007aff', fg='white', font=('Arial', 16), relief='flat')
rankings_button.grid(row=5, column=0, columnspan=2, pady=10)

# Start the GUI main loop
root.mainloop()
