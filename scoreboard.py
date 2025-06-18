# scoreboard.py

import csv

def load_scoreboard(file_path='scoreboard.csv'):
    players = {}
    with open(file_path, 'r', newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            name = row['player']
            stats = {}
            for key, value in row.items():
                if key != 'player':
                    try:
                        stats[key] = int(value)
                    except:
                        stats[key] = 0
            players[name] = stats
    return players