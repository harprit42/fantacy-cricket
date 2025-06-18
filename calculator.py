# calculator.py

def calculate_points(stats):
    runs = stats.get('runs', 0)
    fours = stats.get('fours', 0)
    sixes = stats.get('sixes', 0)
    wickets = stats.get('wickets', 0)
    dot_balls = stats.get('dot_balls', 0)
    overs = stats.get('overs', 0)
    runs_conceded = stats.get('runs_conceded', 0)
    catches = stats.get('catches', 0)
    stumpings = stats.get('stumpings', 0)
    run_outs = stats.get('run_outs', 0)
    balls_faced = stats.get('balls_faced', 0)

    # Batting
    batting = runs + fours * 4 + sixes * 6
    sr = (runs / balls_faced) * 100 if balls_faced else 0
    if 130 <= sr <= 150: batting += 2
    elif 150.01 <= sr <= 170: batting += 4
    elif sr > 170: batting += 6

    # Bowling
    bowling = wickets * 25 + dot_balls
    economy = (runs_conceded / overs) if overs else 0
    if economy < 5: bowling += 6
    elif 5 <= economy < 6: bowling += 4
    elif 6 <= economy <= 7: bowling += 2

    # Fielding
    fielding = (catches + stumpings + run_outs) * 10

    return batting + bowling + fielding