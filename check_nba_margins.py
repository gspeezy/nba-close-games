import requests
from datetime import datetime
import pytz

def get_games_with_close_margins(date_str):
    url = f"https://site.api.espn.com/apis/site/v2/sports/basketball/nba/scoreboard?dates={date_str}"
    resp = requests.get(url)
    data = resp.json()

    close_games = []
    for event in data.get("events", []):
        competitions = event.get("competitions", [])
        if not competitions:
            continue

        competitors = competitions[0].get("competitors", [])
        if len(competitors) != 2:
            continue

        team_1 = competitors[0]["team"]["shortDisplayName"]
        team_2 = competitors[1]["team"]["shortDisplayName"]

        try:
            score_1 = int(competitors[0]["score"])
            score_2 = int(competitors[1]["score"])
        except (KeyError, ValueError):
            continue  # Skip games without valid scores

        margin = abs(score_1 - score_2)

        if margin < 10:
            matchup = f"{team_1} vs {team_2}"
            close_games.append(matchup)

    return close_games

def main():
    est_now = datetime.now(pytz.timezone("US/Eastern"))
    date_str = est_now.strftime("%Y%m%d")

    close_games = get_games_with_close_margins(date_str)
    if close_games:
        print("Close NBA games today (margin < 10 pts):")
        for game in close_games:
            print(f"- {game}")
    else:
        print("No close NBA games today.")

if __name__ == "__main__":
    main()
