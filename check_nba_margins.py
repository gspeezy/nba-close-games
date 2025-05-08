import requests
from datetime import datetime, timedelta
import smtplib
from email.mime.text import MIMEText
import os

import logging

# Set up logging
logging.basicConfig(level=logging.INFO)

def fetch_games():
    # Convert to UTC date from NZT (12-13 hours ahead)
    today = (datetime.utcnow() - timedelta(hours=12)).strftime('%Y-%m-%d')
    url = f"https://www.balldontlie.io/api/v1/games?start_date={today}&end_date={today}&per_page=100"
    logging.info(f"Fetching games from API: {url}")
    
    try:
        response = requests.get(url)
        if response.status_code == 404:
            logging.error(f"API responded with 404 Not Found. URL: {url}")
            return []  # Return an empty list if no data is found
        response.raise_for_status()
        data = response.json()
        return data.get('data', [])
    except requests.exceptions.RequestException as e:
        logging.error(f"Error fetching data from API: {e}")
        return []  # Return an empty list if there's an error

def find_close_games(games):
    return [
        f"{game['home_team']['full_name']} v {game['visitor_team']['full_name']}"
        for game in games
        if abs(game['home_team_score'] - game['visitor_team_score']) < 10 and game['status'] == "Final"
    ]

def send_email(body):
    user = os.environ['EMAIL_USER']
    password = os.environ['EMAIL_PASS']
    to_addr = os.environ['EMAIL_TO']
    smtp_server = os.environ.get('SMTP_SERVER', 'smtp.mailersend.net')
    smtp_port = int(os.environ.get('SMTP_PORT', '587'))

    msg = MIMEText(body)
    msg['Subject'] = 'NBA Close Games Today'
    msg['From'] = user
    msg['To'] = to_addr

    with smtplib.SMTP(smtp_server, smtp_port) as server:
        server.starttls()
        print("SMTP config:")
        print(f"Server: {smtp_server}")
        print(f"Port: {smtp_port}")
        print(f"User: {user}")
        server.login(user, password)
        server.send_message(msg)

def main():
    try:
        games = fetch_games()
        close_games = find_close_games(games)
        if close_games:
            body = "\n".join(close_games)
        else:
            body = "No close NBA games today — this is a test email to confirm delivery."

        send_email(body)

    except Exception as e:
        print(f"Error: {e}")
        raise


