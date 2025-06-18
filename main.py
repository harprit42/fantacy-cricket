import tkinter as tk
from tkinter import ttk, messagebox
from calculator import calculate_points
from scoreboard import load_scoreboard
import csv
from collections import defaultdict

players = load_scoreboard()
team_A = [name for i, name in enumerate(players) if i % 2 == 0]
team_B = [name for i, name in enumerate(players) if i % 2 != 0]

selected_players = []
captain_var = None
vice_captain_var = None
username_var = None
player_buttons = {}

root = tk.Tk()
root.title("Fantasy Points Selector")

def clear_widgets(frame):
    for widget in frame.winfo_children():
        widget.destroy()
    frame.grid_forget()

def next_stage(current_frame, next_func):
    clear_widgets(current_frame)
    next_func()

# --- Stage 1: Username and Team Selection ---
def build_stage_1():
    stage1 = tk.Frame(root)
    stage1.grid(row=0, column=0, padx=20, pady=20)

    global username_var
    username_var = tk.StringVar()

    tk.Label(stage1, text="Your Name:").grid(row=0, column=0, sticky="w")
    tk.Entry(stage1, textvariable=username_var, width=30).grid(row=0, column=1, columnspan=2, sticky="w")

    count_label = tk.Label(stage1, text="Selected 0 of 11")
    count_label.grid(row=1, column=2)

    selected_box = tk.Listbox(stage1, height=15, width=40)
    selected_box.grid(row=2, column=2, rowspan=12, sticky="n")

    def select_player(p, btn):
        if p not in selected_players and len(selected_players) < 11:
            selected_players.append(p)
            selected_box.insert(tk.END, f"{len(selected_players)}. {p}")
            btn.config(state="disabled", bg="lightcoral")
            count_label.config(text=f"Selected {len(selected_players)} of 11")
            if len(selected_players) == 11:
                next_btn.config(state="normal")

    tk.Label(stage1, text="Team A").grid(row=1, column=0)
    for i, p in enumerate(team_A):
        b = tk.Button(stage1, text=p, width=25)
        b.grid(row=i + 2, column=0, sticky="w")
        b.config(command=lambda p=p, btn=b: select_player(p, btn))
        player_buttons[p] = b

    tk.Label(stage1, text="Team B").grid(row=1, column=1)
    for i, p in enumerate(team_B):
        b = tk.Button(stage1, text=p, width=25)
        b.grid(row=i + 2, column=1, sticky="w")
        b.config(command=lambda p=p, btn=b: select_player(p, btn))
        player_buttons[p] = b

    tk.Label(stage1, text="Selected Players:").grid(row=1, column=2)

    next_btn = tk.Button(stage1, text="Next", state="disabled",
                         command=lambda: next_stage(stage1, build_stage_2))
    next_btn.grid(row=16, column=2, pady=10)

    tk.Button(stage1, text="Leaderboard", command=lambda: show_leaderboard(stage1)).grid(row=17, column=2, pady=10)

# --- Stage 2: Captain / Vice-Captain Selection ---
def build_stage_2():
    stage2 = tk.Frame(root)
    stage2.grid(row=0, column=0, padx=20, pady=20)

    tk.Label(stage2, text="Select Captain").grid(row=0, column=0)
    tk.Label(stage2, text="Select Vice-Captain").grid(row=0, column=1)

    cap_listbox = tk.Listbox(stage2, height=12, exportselection=False)
    cap_listbox.grid(row=1, column=0, padx=10)
    vcap_listbox = tk.Listbox(stage2, height=12, exportselection=False)
    vcap_listbox.grid(row=1, column=1, padx=10)

    for p in selected_players:
        cap_listbox.insert(tk.END, p)
        vcap_listbox.insert(tk.END, p)

    def update_selection(event=None):
        try:
            cap = cap_listbox.get(cap_listbox.curselection()[0])
        except IndexError:
            cap = None
        try:
            vcap = vcap_listbox.get(vcap_listbox.curselection()[0])
        except IndexError:
            vcap = None

        if cap and vcap and cap != vcap:
            next_btn.config(state="normal")
        else:
            next_btn.config(state="disabled")

    cap_listbox.bind("<<ListboxSelect>>", update_selection)
    vcap_listbox.bind("<<ListboxSelect>>", update_selection)

    def assign_and_continue():
        global captain_var, vice_captain_var
        captain_var = tk.StringVar(value=cap_listbox.get(cap_listbox.curselection()))
        vice_captain_var = tk.StringVar(value=vcap_listbox.get(vcap_listbox.curselection()))
        calculate_score()
        root.destroy()

    next_btn = tk.Button(stage2, text="Submit Team", state="disabled", command=assign_and_continue)
    next_btn.grid(row=3, column=0, columnspan=2, pady=10)

    tk.Button(stage2, text="← Back", command=lambda: next_stage(stage2, build_stage_1)).grid(row=4, column=0, columnspan=2)

def show_leaderboard(_):
    leaderboard_win = tk.Toplevel(root)
    leaderboard_win.title("Leaderboard")
    leaderboard_win.geometry("420x420")

    try:
        with open("points.csv", "r") as f:
            entries = f.read().strip().split("\n" + "-" * 40 + "\n")
    except FileNotFoundError:
        messagebox.showinfo("No Data", "No scores submitted yet.")
        return

    tk.Label(leaderboard_win, text="Select a player to view their score breakdown").pack(pady=5)

    user_listbox = tk.Listbox(leaderboard_win, width=45, height=15)
    user_listbox.pack(padx=10, pady=5)

    details_map = {}
    for entry in entries:
        lines = entry.strip().splitlines()
        if not lines:
            continue
        uname = lines[0].replace("Player: ", "").strip()
        total_line = next((l for l in lines if l.startswith("Total: ")), "Total: 0")
        total = total_line.replace("Total: ", "").strip()
        display = f"{uname} - {total} points"
        details_map[uname] = "\n".join(lines)
        user_listbox.insert(tk.END, display)

    breakdown_btn = tk.Button(leaderboard_win, text="Show Points Breakdown", state="disabled")
    breakdown_btn.pack(pady=5)

    def enable_button(event):
        if user_listbox.curselection():
            breakdown_btn.config(state="normal")
        else:
            breakdown_btn.config(state="disabled")

    user_listbox.bind("<<ListboxSelect>>", enable_button)

    def show_details():
        try:
            selected = user_listbox.get(user_listbox.curselection())
            uname = selected.split(" - ")[0]
        except:
            return

        detail_win = tk.Toplevel(leaderboard_win)
        detail_win.title(f"{uname}'s Breakdown")
        detail_win.geometry("420x500")

        tk.Label(detail_win, text=f"{uname}'s Team & Scorecard").pack(pady=5)

        # ⬇️ SET THESE as needed
        captain = "Bose Ruban"
        vice_captain = "Ankush Singh"

        data_lines = details_map[uname].splitlines()
        teams = {'Team A': [], 'Team B': []}
        current_team = None

        for line in data_lines[1:]:
            stripped = line.strip()
            if not stripped or stripped == "-" * 40:
                continue

            if stripped.lower().startswith("team a:"):
                current_team = "Team A"
            elif stripped.lower().startswith("team b:"):
                current_team = "Team B"
            elif stripped.lower().startswith("total:"):
                total = stripped
            elif stripped.startswith("-") and current_team:
                entry = stripped.lstrip("-").strip()
                if "(" in entry and ")" in entry:
                    name = entry.rsplit("(", 1)[0].strip()
                    points = entry.rsplit("(", 1)[1].replace(")", "").strip()
                    role_tag = ""
                    if name == captain:
                        role_tag = " (c)"
                    elif name == vice_captain:
                        role_tag = " (vc)"
                    display = f"{name}{role_tag} - {points} points"
                    teams[current_team].append(display)

        for team, players in teams.items():
            tk.Label(detail_win, text=team + ":").pack(anchor="w", padx=10, pady=(6, 0))
            for idx, player in enumerate(players, start=1):
                tk.Label(detail_win, text=f"{idx}. {player}").pack(anchor="w", padx=20)

        tk.Label(detail_win, text="").pack()
        tk.Label(detail_win, text=total, font=("Arial", 10, "bold")).pack()

        tk.Button(detail_win, text="← Back to Leaderboard", command=detail_win.destroy).pack(pady=10)

    breakdown_btn.config(command=show_details)
    tk.Button(leaderboard_win, text="← Back to Home", command=leaderboard_win.destroy).pack(pady=10)

# Your leaderboard function here...
def calculate_score():
    # ⬅️ Paste the full function block I gave you here
    uname = username_var.get().strip()
    if not uname:
        return
    cap = captain_var.get()
    vcap = vice_captain_var.get()

    results = []
    total = 0

    for p in selected_players:
        score = calculate_points(players.get(p, {}))
        if p == cap:
            score *= 2
        elif p == vcap:
            score *= 1.5
        score = round(score, 2)
        results.append((p, score))
        total += score

    team_a_lines = [f"  - {p} ({pts})" for p, pts in results if p in team_A]
    team_b_lines = [f"  - {p} ({pts})" for p, pts in results if p in team_B]

    with open("points.csv", "a", newline="") as f:
        f.write(f"Player: {uname}\n\n")
        f.write("Team A:\n" + "\n".join(team_a_lines) + "\n\n")
        f.write("Team B:\n" + "\n".join(team_b_lines) + "\n\n")
        f.write(f"Total: {round(total, 2)}\n")
        f.write("-" * 40 + "\n")

    # Now launch the GUI

build_stage_1()
root.mainloop()

